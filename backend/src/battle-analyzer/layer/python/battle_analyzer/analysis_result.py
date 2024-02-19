import os
from boto3.dynamodb.types import TypeDeserializer
from battle_analyzer.error import ITEM_NOT_FOUND_ERROR
from battle_analyzer.utils import replace_decimals

table_name = os.environ.get('BATTLE_ANALYSIS_RESULT_TABLE')
    
sammary_projection_expression = '''
    result_id,
    job_id,
    user_id,
    frame_rate,
    movie_frames,
    splatoon_title,
    battle_result,
    team_result_count,
    enemy_result_count,
    battle_rule,
    battle_stage,
    battle_date,
    battle_open_event,
    battle_end_event,
    battle_result_event,
    match_type,
    match_rate,
    team,
    enemy,
    main_player_index,
    team_color,
    enemy_color,
    team_bukis,
    enemy_bukis,
    kill_count,
    death_count,
    sp_count
'''

def get_result_by_result_id(dynamodb_client, user_id: str, result_id: str) -> dict:
    key_condition_expression = 'user_id = :uid AND result_id = :result_id'
    expression_attribute_values = {
        ':uid': { 'S': user_id },
        ':result_id': { 'S': result_id }
    }
    
    response = dynamodb_client.query(
        TableName=table_name,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )
    
    items = response.get('Items', [])
    if len(items) == 0:
        raise ITEM_NOT_FOUND_ERROR

    deserializer = TypeDeserializer()
    return { k: deserializer.deserialize(v) for k, v in items[0].items() }

def get_results_by_job_id(
    dynamodb_client,
    user_id: str,
    job_id: str,
    projection_expression: str = None
) -> list[dict]:
    key_condition_expression = 'user_id = :uid AND job_id = :jid'
    expression_attribute_values = {
        ':uid': { 'S': user_id },
        ':jid': { 'S': job_id }
    }
    
    return get_results(
        dynamodb_client=dynamodb_client,
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
        index_name='JobIdIndex',
        projection_expression=projection_expression)

def get_results_by_battle_date(
    dynamodb_client,
    user_id: str,
    start_date: int,
    end_date: int,
    projection_expression: str = None,
    limit: int = 100,
    order: str = 'desc',
    exclusive_start_key: dict = None,
) -> list[dict]:
    key_condition_expression = 'user_id = :uid AND battle_date BETWEEN :start_date AND :end_date'
    expression_attribute_values = {
        ':uid': { 'S': user_id },
        ':start_date': { 'N': str(start_date) },
        ':end_date': { 'N': str(end_date) },
    }
        
    index_name = 'BattleDateIndex'

    return get_pagiation(
        dynamodb_client=dynamodb_client,
        key_condition_expression=key_condition_expression,
        expression_attribute_values=expression_attribute_values,
        index_name=index_name,
        limit=limit,
        order=order,
        exclusive_start_key=exclusive_start_key,
        projection_expression=projection_expression)

def get_results(
    dynamodb_client,
    key_condition_expression: str,
    expression_attribute_values: dict,
    index_name: str,
    projection_expression: str = None,
) -> list[dict]:
    if projection_expression:
        response = dynamodb_client.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ProjectionExpression=projection_expression
        )
    else:
        response = dynamodb_client.query(
            TableName=table_name,
            IndexName=index_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

    items = response.get('Items', [])
    deserializer = TypeDeserializer()
    return [{ k: deserializer.deserialize(v) for k, v in item.items() } for item in items]

def get_pagiation(
    dynamodb_client,
    key_condition_expression: str,
    expression_attribute_values: dict,
    index_name: str,
    limit: int,
    order: str,
    exclusive_start_key: dict,
    projection_expression: str
):
    scan_index_forward = False if order == 'desc' else True
    if exclusive_start_key:
        if projection_expression:
            response = dynamodb_client.query(
                TableName=table_name,
                IndexName=index_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ProjectionExpression=projection_expression,
                ScanIndexForward=scan_index_forward,
                Limit=limit,
                ExclusiveStartKey=exclusive_start_key
            )
        else:
            response = dynamodb_client.query(
                TableName=table_name,
                IndexName=index_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ScanIndexForward=scan_index_forward,
                Limit=limit,
                ExclusiveStartKey=exclusive_start_key
            )
    else:
        if projection_expression:
            response = dynamodb_client.query(
                TableName=table_name,
                IndexName=index_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ScanIndexForward=scan_index_forward,
                ProjectionExpression=projection_expression,
                Limit=limit
            )
        else:
            response = dynamodb_client.query(
                TableName=table_name,
                IndexName=index_name,
                KeyConditionExpression=key_condition_expression,
                ExpressionAttributeValues=expression_attribute_values,
                ScanIndexForward=scan_index_forward,
                Limit=limit
            )
    
    items = response.get('Items', [])
    deserializer = TypeDeserializer()
    return {
        'sammaries': [replace_decimals({ k: deserializer.deserialize(v) for k, v in item.items() }) for item in items],
        'page_token': response.get('LastEvaluatedKey', None)
    }