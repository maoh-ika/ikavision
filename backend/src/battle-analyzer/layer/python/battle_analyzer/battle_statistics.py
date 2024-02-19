import os
import json
import zlib
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer, Binary
from battle_analyzer.error import AnalyzerError, ErrorCode, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, ITEM_NOT_FOUND_ERROR, InternalError
from battle_analyzer.utils import replace_decimals, calc_containing_day_range

def deserialize(item: dict) -> dict:
    deserializer = TypeDeserializer()
    item_data = replace_decimals({ k: deserializer.deserialize(v) for k, v in item.items() })
    b = bytes(item_data['buki_performance'])
    item_data['buki_performance'] = json.loads(zlib.decompress(b))
    return item_data

def get_by_id(
    dynamodb_client,
    user_id: str,
    statistics_id: str
) -> dict:
    table_name = os.environ.get('BATTLE_STATISTICS_TABLE')
    key_condition_expression = 'user_id = :uid AND statistics_id = :sid'
    expression_attribute_values = {
        ':uid': { 'S': user_id },
        ':sid': {'S': statistics_id }
    }

    response = dynamodb_client.query(
        TableName=table_name,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])
    if len(items) == 0:
        raise ITEM_NOT_FOUND_ERROR
    
    return deserialize(items[0])

def get_master_by_id(dynamodb_client, user_id: str) -> dict:
    return get_by_id(dynamodb_client, user_id, user_id)

def get_by_period(
    dynamodb_client,
    user_id: str,
    start_timestamp: str,
    end_timestamp
) -> dict:
    table_name = os.environ.get('BATTLE_STATISTICS_TABLE')
    key_condition_expression = 'user_id = :uid AND start_timestamp = :st'
    expression_attribute_values = {
        ':uid': { 'S': user_id },
        ':st': {'N': str(start_timestamp) }
    }

    response = dynamodb_client.query(
        TableName=table_name,
        IndexName='StartTimestampIndex',
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])
    if len(items) == 0:
        raise ITEM_NOT_FOUND_ERROR

    envs = [deserialize(item) for item in items]
    envs = list(filter(lambda e: e['end_timestamp'] == end_timestamp, envs))
    if len(envs) == 0:
        raise ITEM_NOT_FOUND_ERROR
    
    return envs[0]

def get_by_time_range(
    dynamodb_client,
    user_id: str,
    start_timestamp: str,
    end_timestamp
) -> dict:
    table_name = os.environ.get('BATTLE_STATISTICS_TABLE')
    key_condition_expression = 'user_id = :uid AND start_timestamp BETWEEN :start_timestamp AND :end_timestamp'
    expression_attribute_values = {
        ':uid': { 'S': user_id },
        ':start_timestamp': { 'N': str(start_timestamp) },
        ':end_timestamp': { 'N': str(end_timestamp) },
    }

    response = dynamodb_client.query(
        TableName=table_name,
        IndexName='StartTimestampIndex',
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])
    envs = [deserialize(item) for item in items]
    envs = list(filter(lambda e: e['end_timestamp'] < end_timestamp, envs))
    return envs