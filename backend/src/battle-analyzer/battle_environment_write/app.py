import os
import json
import copy
import boto3
import zlib
import time
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer, Binary
from battle_analyzer.error import AnalyzerError, ErrorCode, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, InternalError
from battle_analyzer.response import make_response, make_error_response
from battle_analyzer.utils import replace_decimals, calc_containing_day_range
from battle_analyzer.seasons import find_season_info_by_date
from battle_analyzer.battle_environment import get_season, get_season_match, get_daily, get_daily_match, make_season_env_tag, make_season_match_env_tag, make_daily_env_tag, make_daily_match_env_tag
    
dynamodb_client = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')

DAILY_START_HOUR = 11

def _is_invalid_match_type(match_type: str, match_rate: float) -> bool:
    if match_type in ['unknown']:
        return True
    if match_type == 'x_match':
        if match_rate is None or match_rate == '':
            return True
    
    return False

def _query_result_sammaries_by_date(user_id: str, start_date: int, end_date: int, last_evaluated_key: dict=None) -> list[dict]:
    params = {
        'method': 'query_sammaries',
        'user_id': user_id,
        'start_battle_date': start_date,
        'end_battle_date': end_date,
        'page_token': last_evaluated_key,
        'page_size': 20
    }
    req = {
        'body': json.dumps(params)
    }

    response = lambda_client.invoke(
        FunctionName=os.environ.get('ANALYSIS_RESULT_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps(req)
    )
    result_data = response.get('Payload').read().decode('utf-8')
    results = json.loads(result_data)

    if 'error' in results:
        raise InternalError(results['error']['msg'])

    return results

def _make_new_item(tag: str, title: str, season: str, start_timestamp, end_timestamp) -> dict:
    return {
        'environment_tag': tag,
        'splatoon_title': title,
        'season_name': season,
        'start_timestamp': start_timestamp,
        'end_timestamp': end_timestamp,
        'result_count': 0,
        'battles': {},
        'buki_environment': {}
    }


def _put(item: dict):
    item_copy = item.copy()
    item_copy['buki_environment'] = zlib.compress(json.dumps(item_copy['buki_environment']).encode())
    serializer = TypeSerializer()
    item_dynamodb_json = { k: serializer.serialize(v) for k, v in item_copy.items() }
    dynamodb_client.put_item(
        TableName=os.environ.get('BATTLE_ENVIRONMENT_TABLE'),
        Item=item_dynamodb_json
    )

def _prepare_buki_result(buki_env: dict, rule: str, stage: str):
    if rule not in buki_env['result']:
        buki_env['result'][rule] = {}

    rule_result = buki_env['result'][rule]
    if stage not in rule_result:
        rule_result[stage] = {
            'win': 0,
            'lose': 0
        }

def _prepare_buki_usage(buki_env: dict, rule: str, stage: str):
    if rule not in buki_env['usage']:
        buki_env['usage'][rule] = {}

    rule_usage = buki_env['usage'][rule]
    if stage not in rule_usage:
        rule_usage[stage] = 0

def _prepare_buki_battles(buki_env: dict, rule: str, stage: str):
    if rule not in buki_env['battles']:
        buki_env['battles'][rule] = {}

    rule_usage = buki_env['battles'][rule]
    if stage not in rule_usage:
        rule_usage[stage] = 0

def _prepare_battles(item: dict, rule: str, stage: str):
    if rule not in item['battles']:
        item['battles'][rule] = {}
    rule_battles = item['battles'][rule]
    if stage not in rule_battles:
        rule_battles[stage] = 0
    
def _update_environment(item: dict, result: dict):
    rule = result['battle_rule']
    stage = result['battle_stage']
    battle_result = result['battle_result']
    battle_date = result['battle_date']
    team_bukis = copy.deepcopy(result['team_bukis'])
    enemy_bukis = copy.deepcopy(result['enemy_bukis'])

    buki_environment = item['buki_environment']

    team_bukis.pop(result['main_player_index']) # eliminating bias due to the weapons used by players (e.g. streamers)
    team_mains = list(map(lambda i: i['main_weapon'], team_bukis))
    enemy_mains = list(map(lambda i: i['main_weapon'], enemy_bukis))
    
    if battle_result == 'draw':
        return

    for main in (team_mains + enemy_mains):
        if main not in buki_environment:
            buki_environment[main] = {
                'battles': {},
                'usage': {},
                'result': {},
            }

        buki_env = buki_environment[main]
        _prepare_buki_usage(buki_env, rule, stage)
        buki_env['usage'][rule][stage] += 1

    unique_team_mains = list(set(team_mains))

    for main in unique_team_mains:
        # result
        buki_env = buki_environment[main]
        _prepare_buki_result(buki_env, rule, stage)

        stage_result = buki_env['result'][rule][stage]
        if battle_result == 'win':
            stage_result['win'] += 1
        if battle_result == 'lose':
            stage_result['lose'] += 1
    
    unique_enemy_mains = list(set(enemy_mains))
    
    for main in unique_enemy_mains:
        # result
        buki_env = buki_environment[main]
        _prepare_buki_result(buki_env, rule, stage)

        stage_result = buki_env['result'][rule][stage]
        if battle_result == 'win':
            stage_result['lose'] += 1
        if battle_result == 'lose':
            stage_result['win'] += 1

    unique_total_mains = list(set(unique_team_mains + unique_enemy_mains))
    
    _prepare_battles(item, rule, stage)
    item['battles'][rule][stage] += 1

    for main in unique_total_mains:
        buki_env = buki_environment[main]
        _prepare_buki_battles(buki_env, rule, stage)
        buki_env['battles'][rule][stage] += 1

    item['result_count'] += 1
    item['updated_at'] = int(time.time())
    if 'latest_battle_date' not in item or item['latest_battle_date'] < battle_date:
        item['latest_battle_date'] = battle_date

def _remove_result(item: dict, result: dict):
    rule = result['battle_rule']
    stage = result['battle_stage']
    battle_result = result['battle_result']
    team_bukis = copy.deepcopy(result['team_bukis'])
    enemy_bukis = copy.deepcopy(result['enemy_bukis'])

    buki_environment = item['buki_environment']

    team_bukis.pop(result['main_player_index']) # eliminating bias due to the weapons used by players (e.g. streamers)
    team_mains = list(map(lambda i: i['main_weapon'], team_bukis))
    enemy_mains = list(map(lambda i: i['main_weapon'], enemy_bukis))
    
    if battle_result == 'draw':
        return

    for main in (team_mains + enemy_mains):
        if main not in buki_environment:
            continue

        buki_env = buki_environment[main]
        if rule in buki_env['usage']:
            if stage in buki_env['usage'][rule]:
                if buki_env['usage'][rule][stage] > 0:
                    buki_env['usage'][rule][stage] -= 1


    unique_team_mains = list(set(team_mains))
    for main in unique_team_mains:
        # result
        buki_env = buki_environment[main]
        if rule in buki_env['result']:
            if stage in buki_env['result'][rule]:
                if battle_result == 'win' and buki_env['result'][rule][stage]['win'] > 0:
                    buki_env['result'][rule][stage]['win'] -= 1
                if battle_result == 'lose' and buki_env['result'][rule][stage]['lose'] > 0:
                    buki_env['result'][rule][stage]['lose'] -= 1

    unique_enemy_mains = list(set(enemy_mains))
    for main in unique_enemy_mains:
        # result
        buki_env = buki_environment[main]
        if rule in buki_env['result']:
            if stage in buki_env['result'][rule]:
                if battle_result == 'win' and buki_env['result'][rule][stage]['lose'] > 0:
                    buki_env['result'][rule][stage]['lose'] -= 1
                if battle_result == 'lose' and buki_env['result'][rule][stage]['win'] > 0:
                    buki_env['result'][rule][stage]['win'] -= 1

    unique_total_mains = list(set(unique_team_mains + unique_enemy_mains))

    _remove_battle(item, rule, stage)

    for main in unique_total_mains:
        buki_env = buki_environment[main]
        _remove_battle(buki_env, rule, stage)

    if item['result_count'] > 0: 
        item['result_count'] -= 1
    
    item['updated_at'] = int(time.time())
    
def _remove_battle(item, rule, stage):
    if rule in item['battles']:
        if stage in item['battles'][rule]:
            if item['battles'][rule][stage] > 0:
                item['battles'][rule][stage] -= 1

def add_result_to_season_environment(result: dict) -> dict:
    title = result['splatoon_title']
    season = find_season_info_by_date(title, result['battle_date'])
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    season_name = season['name']
    try:
        item = get_season(dynamodb_client, title, season_name)
    except AnalyzerError as e:
        if e.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            env_tag = make_season_env_tag(title)
            item = _make_new_item(env_tag, title, season_name, season['start_timestamp'], season['end_timestamp'])
            _put(item)

    _update_environment(item, result)
    return _put(item)

def remove_result_from_season_environment(result: dict) -> bool:
    title = result['splatoon_title']
    season = find_season_info_by_date(title, result['battle_date'])
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    season_name = season['name']
    item = get_season(dynamodb_client, title, season_name)
    _remove_result(item, result)
    return _put(item)

def update_season_environment(old_result: dict, new_result: dict) -> bool:
    title = old_result['splatoon_title']
    season = find_season_info_by_date(title, old_result['battle_date'])
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    season_name = season['name']
    item = get_season(dynamodb_client, title, season_name)
    _remove_result(item, old_result)
    _update_environment(item, new_result)
    return _put(item)

def add_result_to_daily_environment(result: dict) -> dict:
    title = result['splatoon_title']
    battle_date = result['battle_date']
    season = find_season_info_by_date(title, battle_date)
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    start_timestamp, end_timestamp = calc_containing_day_range(battle_date, DAILY_START_HOUR)

    try:
        item = get_daily(dynamodb_client, title, season['name'], start_timestamp, end_timestamp)
    except AnalyzerError as e:
        if e.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            env_tag = make_daily_env_tag(title)
            item = _make_new_item(env_tag, title, season['name'], start_timestamp, end_timestamp)
            _put(item)

    _update_environment(item, result)
    return _put(item)

def remove_result_from_daily_environment(result: dict) -> bool:
    title = result['splatoon_title']
    battle_date = result['battle_date']
    season = find_season_info_by_date(title, battle_date)
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    start_timestamp, end_timestamp = calc_containing_day_range(battle_date, DAILY_START_HOUR)
    item = get_daily(dynamodb_client, title, season['name'], start_timestamp, end_timestamp)
    _remove_result(item, result)
    return _put(item)

def update_daily_environment(old_result: dict, new_result: dict) -> bool:
    title = old_result['splatoon_title']
    battle_date = old_result['battle_date']
    season = find_season_info_by_date(title, battle_date)
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    start_timestamp, end_timestamp = calc_containing_day_range(battle_date, DAILY_START_HOUR)
    item = get_daily(dynamodb_client, title, season['name'], start_timestamp, end_timestamp)
    _remove_result(item, old_result)
    _update_environment(item, new_result)
    return _put(item)
    
def add_result_to_season_match_environment(result: dict) -> dict:
    title = result['splatoon_title']
    season = find_season_info_by_date(title, result['battle_date'])
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    season_name = season['name']
    match_type = result['match_type']
    match_rate = result['match_rate']
    if _is_invalid_match_type(match_type, match_rate):
        return
    
    try:
        item = get_season_match(dynamodb_client, title, season_name, match_type, match_rate)
    except AnalyzerError as e:
        if e.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            env_tag = make_season_match_env_tag(title, match_type, match_rate)
            item = _make_new_item(env_tag, title, season_name, season['start_timestamp'], season['end_timestamp'])
            _put(item)

    _update_environment(item, result)
    return _put(item)

def remove_result_from_season_match_environment(result: dict) -> bool:
    title = result['splatoon_title']
    season = find_season_info_by_date(title, result['battle_date'])
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    season_name = season['name']
    match_type = result['match_type']
    match_rate = result['match_rate']
    if _is_invalid_match_type(match_type, match_rate):
        return
    
    item = get_season_match(dynamodb_client, title, season_name, match_type, match_rate)
    _remove_result(item, result)
    return _put(item)

def update_season_match_environment(old_result: dict, new_result: dict) -> bool:
    try:
        remove_result_from_season_match_environment(old_result)
    except AnalyzerError as e:
        # to support old data structure, allow absense of env for old match type
        if e.code != ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            raise e
    return add_result_to_season_match_environment(new_result)

def add_result_to_daily_match_environment(result: dict) -> dict:
    title = result['splatoon_title']
    battle_date = result['battle_date']
    season = find_season_info_by_date(title, battle_date)
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    start_timestamp, end_timestamp = calc_containing_day_range(battle_date, DAILY_START_HOUR)
    match_type = result['match_type']
    match_rate = result['match_rate']
    if _is_invalid_match_type(match_type, match_rate):
        return

    try:
        item = get_daily_match(dynamodb_client, title, season['name'], match_type, match_rate, start_timestamp, end_timestamp)
    except AnalyzerError as e:
        if e.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            env_tag = make_daily_match_env_tag(title, match_type, match_rate)
            item = _make_new_item(env_tag, title, season['name'], start_timestamp, end_timestamp)
            _put(item)

    _update_environment(item, result)
    return _put(item)

def remove_result_from_daily_match_environment(result: dict) -> bool:
    title = result['splatoon_title']
    battle_date = result['battle_date']
    season = find_season_info_by_date(title, battle_date)
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    match_type = result['match_type']
    match_rate = result['match_rate']
    if _is_invalid_match_type(match_type, match_rate):
        return
    
    start_timestamp, end_timestamp = calc_containing_day_range(battle_date, DAILY_START_HOUR)
    item = get_daily_match(dynamodb_client, title, season['name'], match_type, match_rate, start_timestamp, end_timestamp)
    _remove_result(item, result)
    return _put(item)

def update_daily_match_environment(old_result: dict, new_result: dict) -> bool:
    try:
        remove_result_from_daily_match_environment(old_result)
    except AnalyzerError as e:
        # to support old data structure, allow absense of env for old match type
        if e.code != ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            raise e
    return add_result_to_daily_match_environment(new_result)

def add_results(payload: dict):
    if 'start_date' not in payload or 'end_date' not in payload or 'splatoon_title' not in payload:
        raise INVALID_PARAMETER_ERROR

    title = payload['splatoon_title']
    start_date = payload['start_date']
    end_date = payload['end_date']
    user_id= f'{title}_environment'

    last_evaluated_key = None
    while True:
        res = _query_result_sammaries_by_date(user_id, start_date, end_date, last_evaluated_key)
        for sammary in res['sammaries']:
            add_result_to_season_environment(sammary)
            add_result_to_daily_environment(sammary)
        last_evaluated_key = res['page_token']
        if not last_evaluated_key:
            break

    return True

def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                try:
                    new_image = record['dynamodb']['NewImage']
                    deserializer = TypeDeserializer()
                    #new_result = new_image
                    new_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in new_image.items() })
                    add_result_to_season_environment(new_result)
                    add_result_to_daily_environment(new_result)
                    add_result_to_season_match_environment(new_result)
                    add_result_to_daily_match_environment(new_result)
                    return make_response(True)
                except AnalyzerError as e:
                    print(e.msg)
                    return make_error_response(e)
                except Exception as e:
                    print(str(e))
                    return make_error_response(InternalError(str(e)))
            elif record['eventName'] == 'REMOVE':
                try:
                    deleted_image = record['dynamodb']['OldImage']
                    deserializer = TypeDeserializer()
                    #deleted_result = deleted_image
                    deleted_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in deleted_image.items() })
                    remove_result_from_season_environment(deleted_result)
                    remove_result_from_daily_environment(deleted_result)
                    remove_result_from_season_match_environment(deleted_result)
                    remove_result_from_daily_match_environment(deleted_result)
                    return make_response(True)
                except AnalyzerError as e:
                    print(e.msg)
                    return make_error_response(e)
                except Exception as e:
                    print(str(e))
                    return make_error_response(InternalError(str(e)))
            elif record['eventName'] == 'MODIFY':
                try:
                    old_image = record['dynamodb']['OldImage']
                    new_image = record['dynamodb']['NewImage']
                    deserializer = TypeDeserializer()
                    #old_result = old_image
                    #new_result = new_image
                    old_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in old_image.items() })
                    new_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in new_image.items() })
                    update_season_environment(old_result, new_result)
                    update_daily_environment(old_result, new_result)
                    update_season_match_environment(old_result, new_result)
                    update_daily_match_environment(old_result, new_result)
                    return make_response(True)
                except AnalyzerError as e:
                    print(e.msg)
                    return make_error_response(e)
                except Exception as e:
                    print(str(e))
                    return make_error_response(InternalError(str(e)))
    elif 'body' in event:
        payload = json.loads(event['body'])
        method = payload['method']

        try:
            if method == 'add_results':
                return make_response(add_results(payload))
        except AnalyzerError as e:
            print(e.msg)
            return make_error_response(e)
        except Exception as e:
            print(str(e))
            return make_error_response(InternalError(str(e)))
    
    return make_error_response(INVALID_OPERATION_ERROR)
    