import os
import json
import uuid
from decimal import Decimal
import boto3
from boto3.dynamodb.types import TypeSerializer
from battle_analyzer.error import AnalyzerError, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, InternalError
from battle_analyzer.response import make_response, make_error_response
    
dynamodb_client = boto3.client('dynamodb')
table_name = os.environ.get('BATTLE_ANALYSIS_RESULT_TABLE')

def _update(
    user_id: str,
    result_id: str,
    update_expression: str,
    expression_attribute_values: str
):
    key = {
        'user_id': { 'S': user_id },
        'result_id': { 'S': result_id }
    }

    dynamodb_client.update_item(
        TableName=table_name,
        Key=key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )
    
def create_result(payload: dict) -> dict:
    if 'user_id' not in payload or 'job_id' not in payload or 'result' not in payload:
        raise INVALID_PARAMETER_ERROR

    result = payload['result']
    result_id = str(uuid.uuid4())
    result['result_id'] = result_id

    table_name = os.environ.get('BATTLE_ANALYSIS_RESULT_TABLE')

    if result['team_result_count'] is not None:
        result['team_result_count'] = Decimal(str(result['team_result_count']))
    if result['enemy_result_count'] is not None:
        result['enemy_result_count'] = Decimal(str(result['enemy_result_count']))
    if result['match_rate'] is not None:
        result['match_rate'] = Decimal(str(result['match_rate']))

    for ink in result['ink_tank_states']:
        ink['ink_level'] = Decimal(str(ink['ink_level']))
    
    serializer = TypeSerializer()
    item_dynamodb_json = { k: serializer.serialize(v) for k, v in result.items() }
    dynamodb_client.put_item(
        TableName=table_name,
        Item=item_dynamodb_json
    )

    return { 'result': True }

def update(payload: dict):
    if 'user_id' not in payload or 'result_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    result_id = payload['result_id']

    updates = []
    expression_attribute_values = {}

    if 'rule' in payload and payload['rule'] is not None:
        updates.append('battle_rule = :rule')
        expression_attribute_values.update({':rule': {'S': payload['rule']}})
    if 'stage' in payload and payload['stage'] is not None:
        updates.append('battle_stage = :stage')
        expression_attribute_values.update({':stage': {'S': payload['stage']}})
    if 'match_type' in payload and payload['match_type'] is not None:
        match_type = payload['match_type']
        updates.append('match_type = :match_type')
        expression_attribute_values.update({':match_type': {'S': match_type}})
        if match_type == 'x_match':
            if 'match_rate' not in payload:
                raise INVALID_PARAMETER_ERROR
            match_rate = payload['match_rate']
            updates.append('match_rate = :match_rate')
            if match_rate is None:
                expression_attribute_values.update({':match_rate': {'NULL': True }})
            else:
                expression_attribute_values.update({':match_rate': {'N': str(match_rate)}})

    if len(updates) == 0:
        return
    update_expression = f'SET {",".join(updates)}'

    _update(user_id, result_id, update_expression, expression_attribute_values)
    return True

def delete(payload: dict):
    if 'user_id' not in payload or 'result_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    result_id = payload['result_id']
    key = {
        'user_id': { 'S': user_id },
        'result_id': { 'S': result_id }
    }

    dynamodb_client.delete_item(
        TableName=table_name,
        Key=key
    )

    return True

def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)

    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'create_result':
            return make_response(create_result(payload))
        elif method == 'update':
            return make_response(update(payload))
        elif method == 'delete':
            return make_response(delete(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))

    return make_error_response(INVALID_OPERATION_ERROR)