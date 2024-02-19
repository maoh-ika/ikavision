import json
import zlib
import os
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer, Binary
from battle_analyzer.utils import replace_decimals, calc_containing_day_range
from battle_analyzer.error import AnalyzerError, ErrorCode, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, ITEM_NOT_FOUND_ERROR, InternalError

table_name = os.environ.get('BATTLE_ENVIRONMENT_TABLE')

x_match_rate_layers = [
    { 'lower_rate': None, 'upper_rate': 1500, 'label': 'under_1500' },
    { 'lower_rate': 1500, 'upper_rate': 2000, 'label': '1500_2000' },
    { 'lower_rate': 2000, 'upper_rate': 2500, 'label': '2000_2500' },
    { 'lower_rate': 2500, 'upper_rate': 3000, 'label': '2500_3000' },
    { 'lower_rate': 3000, 'upper_rate': 3500, 'label': '3000_3500' },
    { 'lower_rate': 3500, 'upper_rate': 4000, 'label': '3500_4000' },
    { 'lower_rate': 4000, 'upper_rate': None, 'label': 'upper_4000' }
]

def deserialize(item: dict) -> dict:
    deserializer = TypeDeserializer()
    item_data = replace_decimals({ k: deserializer.deserialize(v) for k, v in item.items() })
    b = bytes(item_data['buki_environment'])
    item_data['buki_environment'] = json.loads(zlib.decompress(b))
    return item_data

def get_x_rate_label(rate: float) -> str:
    rate_label = ''
    for layer in x_match_rate_layers:
        if layer['lower_rate'] is not None and rate < layer['lower_rate']:
            continue
        if layer['upper_rate'] is not None and rate >= layer['upper_rate']:
            continue
        rate_label = layer['label']
        break
    return rate_label

def make_season_env_tag(title: str) -> str:
    return f'{title}_season'

def make_season_match_env_tag(title: str, match_type: str, rate: float=None, rate_label: str=None) -> str:
    if match_type == 'x_match':
        rate_label = get_x_rate_label(rate) if rate is not None else rate_label
        return f'{make_season_env_tag(title)}_{match_type}_{rate_label}'
    else:
        return f'{make_season_env_tag(title)}_{match_type}'

def make_daily_env_tag(title: str) -> str:
    return f'{title}_daily'

def make_daily_match_env_tag(title: str, match_type: str, rate: float=None, rate_label: str=None) -> str:
    if match_type == 'x_match':
        rate_label = get_x_rate_label(rate) if rate is not None else rate_label
        return f'{make_daily_env_tag(title)}_{match_type}_{rate_label}'
    else:
        return f'{make_daily_env_tag(title)}_{match_type}'

def query(
    dynamodb_client,
    environment_tag: str,
) -> dict:
    key_condition_expression = 'environment_tag = :tag'
    expression_attribute_values = {
        ':tag': {'S': environment_tag },
    }

    response = dynamodb_client.query(
        TableName=table_name,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])

    return [deserialize(item) for item in items]

def query_by_season(
    dynamodb_client,
    environment_tag: str,
    season: str
) -> dict:
    key_condition_expression = 'environment_tag = :tag and season_name = :s'
    expression_attribute_values = {
        ':tag': {'S': environment_tag },
        ':s': {'S': season }
    }

    response = dynamodb_client.query(
        TableName=table_name,
        IndexName='SeasonIndex',
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])
    return [deserialize(item) for item in items]

def get_by_period(
    dynamodb_client,
    environment_tag: str,
    season: str,
    start_timestamp: str,
    end_timestamp
) -> dict:
    key_condition_expression = 'environment_tag = :tag AND start_timestamp = :st'
    expression_attribute_values = {
        ':tag': { 'S': environment_tag },
        ':st': {'N': str(start_timestamp) }
    }

    response = dynamodb_client.query(
        TableName=table_name,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])
    if len(items) == 0:
        raise ITEM_NOT_FOUND_ERROR

    envs = [deserialize(item) for item in items]
    envs = list(filter(lambda e: e['end_timestamp'] == end_timestamp and e['season_name'] == season, envs))
    if len(envs) == 0:
        raise ITEM_NOT_FOUND_ERROR
    
    return envs[0]

def get_by_time_range(
    dynamodb_client,
    environment_tag: str,
    start_timestamp: str,
    end_timestamp
) -> dict:
    key_condition_expression = 'environment_tag = :tag AND start_timestamp BETWEEN :start_timestamp AND :end_timestamp'
    expression_attribute_values = {
        ':tag': { 'S': environment_tag },
        ':start_timestamp': { 'N': str(start_timestamp) },
        ':end_timestamp': { 'N': str(end_timestamp) },
    }

    response = dynamodb_client.query(
        TableName=table_name,
        KeyConditionExpression=key_condition_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

    items = response.get('Items', [])
    envs = [deserialize(item) for item in items]
    envs = list(filter(lambda e: e['end_timestamp'] < end_timestamp, envs))
    return envs

def get_daily(
    dynamodb_client,
    title: str,
    season: str,
    start_timestamp: int,
    end_timestamp: int
):
    env_tag = make_daily_env_tag(title)
    return get_by_period(dynamodb_client, env_tag, season, start_timestamp, end_timestamp)

def get_daily_match(
    dynamodb_client,
    title: str,
    season: str,
    match_type: str,
    match_rate: float,
    start_timestamp: int,
    end_timestamp: int
):
    env_tag = make_daily_match_env_tag(title, match_type, match_rate)
    return get_by_period(dynamodb_client, env_tag, season, start_timestamp, end_timestamp)

def get_season(
    dynamodb_client,
    title: str,
    season: str
) -> dict:
    env_tag = make_season_env_tag(title)
    seasons = query_by_season(dynamodb_client, env_tag, season)
    if len(seasons) == 0:
        raise ITEM_NOT_FOUND_ERROR
    return seasons[0]

def get_season_match(
    dynamodb_client,
    title: str,
    season: str,
    match_type: str,
    match_rate: float,
) -> dict:
    env_tag = make_season_match_env_tag(title, match_type, match_rate)
    seasons = query_by_season(dynamodb_client, env_tag, season)
    if len(seasons) == 0:
        raise ITEM_NOT_FOUND_ERROR
    return seasons[0]
