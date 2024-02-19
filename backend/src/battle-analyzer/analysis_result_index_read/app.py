import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from battle_analyzer.error import AnalyzerError, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, ITEM_NOT_FOUND_ERROR, InternalError, ErrorCode
from battle_analyzer.response import make_response, make_error_response
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
    
dynamodb_client = boto3.client('dynamodb')
index_name = os.environ.get('AOS_INDEX_NAME')
end_point = os.environ.get('AOS_END_POINT')
region = os.environ.get('AWS_REGION_ID')
    
session = boto3.Session()
creds = session.get_credentials()
awsauth = AWS4Auth(
    creds.access_key,
    creds.secret_key,
    region,
    'es', 
    session_token=creds.token
)

os_client = OpenSearch(
    hosts=[end_point],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=300
)

def make_range(params: dict, gte_param_name: str, lte_param_name: str) -> dict:
    range = {}
    if gte_param_name in params:
        range['gte'] = params[gte_param_name]
    if lte_param_name in params:
        range['lte'] = params[lte_param_name]
    return range

def make_match_condition(key: str, value: str) -> dict:
    return { 'match': { key: value }}

def make_fuzzy_condition(key: str, value: str) -> dict:
    return { 'fuzzy': { key: { 'value': value, 'fuzziness': 'AUTO', 'transpositions': False }}}

def make_range_condition(key: str, value: str) -> dict:
    return { 'range': { key: value }}

def make_nested_condition(path: str, key: str, value: str, cond_func) -> dict:
    return {
        'nested': {
            'path': path,
            'query': {
                'bool': {
                    'must': [cond_func(f'{path}.{key}', value)]
                }
            }
        }
    }

def make_nested_match_condition(path: str, key: str, value: str) -> dict:
    return make_nested_condition(path, key, value, make_match_condition)

def make_nested_fuzzy_condition(path: str, key: str, value: str) -> dict:
    return make_nested_condition(path, key, value, make_fuzzy_condition)

def make_nested_range_condition(path: str, key: str, value: str) -> dict:
    return make_nested_condition(path, key, value, make_range_condition)

def make_query(payload: dict) -> dict:
    conditions = []

    battle_date_range = make_range(payload, 'battle_date_gte', 'battle_date_lte')
    if len(battle_date_range) > 0:
        conditions.append(make_range_condition('battle_date', battle_date_range))
    
    battle_duration_range = make_range(payload, 'battle_duration_gte', 'battle_duration_lte')
    if len(battle_duration_range) > 0:
        conditions.append(make_range_condition('battle_duration', battle_duration_range))
    
    if 'battle_result' in payload:
        conditions.append(make_match_condition('battle_result', payload['battle_result']))
    
    if 'battle_rule' in payload:
        conditions.append(make_match_condition('battle_rule', payload['battle_rule']))
    
    if 'battle_stage' in payload:
        conditions.append(make_match_condition('battle_stage', payload['battle_stage']))

    death_count_range = make_range(payload, 'death_count_gte', 'death_count_lte')
    if len(death_count_range) > 0:
        conditions.append(make_range_condition('death_count', death_count_range))

    if 'death_reason' in payload:
        conditions.append(make_nested_match_condition('death_events', 'death_reason', payload['death_reason']))
    
    if 'death_reason_type' in payload:
        conditions.append(make_nested_match_condition('death_events', 'reason_type', payload['death_reason_type']))
    
    if 'death_killer_name' in payload:
        conditions.append(make_nested_fuzzy_condition('death_events', 'killer_name', payload['death_killer_name']))
    
    death_time_range = make_range(payload, 'death_time_gte', 'death_time_lte')
    if len(death_time_range) > 0:
        conditions.append(make_nested_range_condition('death_events', 'death_time', death_time_range))

    if 'enemy' in payload:
        for e in payload['enemy']:
            conditions.append(make_nested_fuzzy_condition('enemy', 'name', e))
    
    if 'enemy_buki_main' in payload:
        for e in payload['enemy_buki_main']:
            conditions.append(make_nested_match_condition('enemy_bukis', 'main_weapon', e))
    
    if 'enemy_buki_sub' in payload:
        for e in payload['enemy_buki_sub']:
            conditions.append(make_nested_match_condition('enemy_bukis', 'sub_weapon', e))
    
    if 'enemy_buki_sp' in payload:
        for e in payload['enemy_buki_sp']:
            conditions.append(make_nested_match_condition('enemy_bukis', 'sp_weapon', e))
    
    enemy_result_count_range = make_range(payload, 'enemy_result_count_gte', 'enemy_result_count_lte')
    if len(enemy_result_count_range) > 0:
        conditions.append(make_range_condition('enemy_result_count', enemy_result_count_range))
    
    kill_count_range = make_range(payload, 'kill_count_gte', 'kill_count_lte')
    if len(kill_count_range) > 0:
        conditions.append(make_range_condition('kill_count', kill_count_range))

    if 'kill_dead_name' in payload:
        conditions.append(make_nested_fuzzy_condition('kill_events', 'dead_name', payload['kill_dead_name']))
    
    kill_time_range = make_range(payload, 'kill_time_gte', 'kill_time_lte')
    if len(kill_time_range) > 0:
        conditions.append(make_nested_range_condition('kill_events', 'kill_time', kill_time_range))

    match_rate_range = make_range(payload, 'match_rate_gte', 'match_rate_lte')
    if len(match_rate_range) > 0:
        conditions.append(make_range_condition('match_rate', match_rate_range))

    if 'match_type' in payload:
        conditions.append(make_match_condition('match_type', payload['match_type']))
    
    sp_count_range = make_range(payload, 'sp_count_gte', 'sp_count_lte')
    if len(sp_count_range) > 0:
        conditions.append(make_range_condition('sp_count', sp_count_range))
    
    if 'team' in payload:
        for t in payload['team']:
            conditions.append(make_nested_fuzzy_condition('team', 'name', t))
    
    if 'team_buki_main' in payload:
        for t in payload['team_buki_main']:
            conditions.append(make_nested_match_condition('team_bukis', 'main_weapon', t))
    
    if 'team_buki_sub' in payload:
        for t in payload['team_buki_sub']:
            conditions.append(make_nested_match_condition('team_bukis', 'sub_weapon', t))
    
    if 'team_buki_sp' in payload:
        for t in payload['team_buki_sp']:
            conditions.append(make_nested_match_condition('team_bukis', 'sp_weapon', t))
    
    if 'main_player_buki_main' in payload:
        conditions.append(make_nested_match_condition('main_player_buki', 'main_weapon', payload['main_player_buki_main']))
    
    if 'main_player_buki_sub' in payload:
        conditions.append(make_nested_match_condition('main_player_buki', 'sub_weapon', payload['main_player_buki_sub']))
    
    if 'main_player_buki_sp' in payload:
        conditions.append(make_nested_match_condition('main_player_buki', 'sp_weapon', payload['main_player_buki_sp']))

    return conditions

def search(payload: dict) -> list[dict]:
    conditions = make_query(payload)
    page_size = payload['page_size'] if 'page_size' in payload else 20
    page_index = payload['page_index'] if 'page_index' in payload else 0
    frm = page_size * page_index
    query = {
        'query': {
            'bool': {
                'must': conditions
            }
        },
        'sort': {'battle_date': {'order': 'desc'}},
        'size': page_size,
        'from': frm
    }
    query_str = json.dumps(query, ensure_ascii=False)
    res = os_client.search(index=index_name, body=query_str)
    return {
        'total_count': res['hits']['total']['value'],
        'indices': [item['_source'] for item in res['hits']['hits']],
        'page_size': page_size,
        'page_index': page_index
    }

def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)

    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'search':
            return make_response(search(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))

    return make_error_response(INVALID_OPERATION_ERROR)