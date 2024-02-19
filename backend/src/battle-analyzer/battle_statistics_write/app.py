import os
import json
import uuid
import boto3
import zlib
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from battle_analyzer.error import AnalyzerError, ErrorCode, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, InternalError
from battle_analyzer.response import make_response, make_error_response
from battle_analyzer.utils import replace_decimals, calc_containing_day_range
from battle_analyzer.seasons import find_season_info_by_date
from battle_analyzer.battle_statistics import get_by_period, get_master_by_id, get_by_id
    
dynamodb_client = boto3.client('dynamodb')

def _put(item: dict):
    item_copy = item.copy()
    item_copy['buki_performance'] = zlib.compress(json.dumps(item_copy['buki_performance']).encode())
    serializer = TypeSerializer()
    item_dynamodb_json = { k: serializer.serialize(v) for k, v in item_copy.items() }
    dynamodb_client.put_item(
        TableName=os.environ.get('BATTLE_STATISTICS_TABLE'),
        Item=item_dynamodb_json
    )

def _prepare_buki_faceoff(faceoff: dict, enemy_buki: str, rule: str, stage: str) -> dict:
    if enemy_buki not in faceoff:
        faceoff[enemy_buki] = {}

    buki_faceoff = faceoff[enemy_buki]
    if rule not in buki_faceoff:
        buki_faceoff[rule] = {}

    rule_faceoff = buki_faceoff[rule]
    if stage not in rule_faceoff:
        rule_faceoff[stage] = {
            "kill_main": 0,
            "kill_sub": 0,
            "kill_sp": 0,
            "death_main": 0,
            "death_sub": 0,
            "death_sp": 0,
            "battle_count": 0
        }

    return faceoff

def _update_statistics(item: dict, result: dict):
    rule = result['battle_rule']
    stage = result['battle_stage']
    battle_result = result['battle_result']
    buki = result['team_bukis'][result["main_player_index"]]
    main_weapon = buki['main_weapon']
    
    if battle_result == 'draw':
        raise INVALID_PARAMETER_ERROR

    buki_performance = item['buki_performance']
    if main_weapon not in buki_performance:
        buki_performance[main_weapon] = {
            'result': {},
            'faceoff': {},
            'events': {}
        }

    # result
    main_performance = buki_performance[main_weapon]
    if rule not in main_performance['result']:
        main_performance['result'][rule] = {}

    rule_result = main_performance['result'][rule]
    if stage not in rule_result:
        rule_result[stage] = {
            'win': 0,
            'lose': 0
        }

    stage_result = rule_result[stage]
    
    if battle_result == 'win':
        stage_result['win'] += 1
    if battle_result == 'lose':
        stage_result['lose'] += 1

    # faceoff
    main_faceoff = main_performance['faceoff']
    
    # update battle count
    for enemy_buki in result['enemy_bukis']:
        enemy_main = enemy_buki['main_weapon']
        main_faceoff = _prepare_buki_faceoff(main_faceoff, enemy_main, rule, stage)
        stage_faceoff = main_faceoff[enemy_main][rule][stage]
        stage_faceoff['battle_count'] += 1

    # update kill count
    for kill_evt in result['kill_events']:
        if kill_evt['kill_player_side'] == 'enemy' or kill_evt['kill_player_index'] != result['main_player_index']:
            continue
        if kill_evt['death_player_index'] is None:
            enemy_buki = 'unknown'
        else:
            enemy_buki = result['enemy_bukis'][kill_evt['death_player_index']]['main_weapon']

        main_faceoff = _prepare_buki_faceoff(main_faceoff, enemy_buki, rule, stage)
        stage_faceoff = main_faceoff[enemy_buki][rule][stage]

        # do not identify kill method
        stage_faceoff['kill_main'] += 1

    # update death count
    for death_evt in result['death_events']:
        if death_evt['death_player_side'] == 'enemy' or death_evt['death_player_index'] != result['main_player_index']:
            continue
        
        reason_type = death_evt['reason_type']
        if reason_type == 'hoko_shooot':
            enemy_buki = death_evt['death_reason']
        elif reason_type in ['other', 'unknown']:
            enemy_buki = 'unknown'
        elif death_evt['kill_player_index'] is None:
            enemy_buki = 'unknown'
        else:
            enemy_buki = result['enemy_bukis'][death_evt['kill_player_index']]['main_weapon']

        main_faceoff = _prepare_buki_faceoff(main_faceoff, enemy_buki, rule, stage)
        stage_faceoff = main_faceoff[enemy_buki][rule][stage]

        if reason_type in ['main_weapon', 'hoko_shooot', 'other', 'unknown']:
            stage_faceoff['death_main'] += 1
        elif reason_type == 'sub_weapon':
            stage_faceoff['death_sub'] += 1
        elif reason_type == 'sp_weapon':
            stage_faceoff['death_sp'] += 1
    
    # events
    if rule not in main_performance['events']:
        main_performance['events'][rule] = {}

    rule_events = main_performance['events'][rule]
    if stage not in rule_events:
        rule_events[stage] = {
            'sp_trigger': 0,
            'sp_spoil': 0,
            'ink_insufficient': 0
        }

    stage_events = main_performance['events'][rule][stage]

    for sp_evt in result['special_weapon_events']:
        sp_type = sp_evt['type']
        if sp_type == 'fully_charged' or sp_evt['player_side'] == 'enemy' or sp_evt['player_index'] != result['main_player_index']:
            continue
        
        if sp_type == 'triggered':
            stage_events['sp_trigger'] += 1
        elif sp_type == 'spoiled':
            stage_events['sp_spoil'] += 1

    item['result_count'] += 1

def add_result(payload: dict) -> bool:
    if 'user_id' not in payload or 'statistics_id' not in payload or 'result' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    statistics_id = payload['statistics_id']
    result = payload['result']
    
    item = get_by_id(dynamodb_client, user_id, statistics_id)
    _update_statistics(item, result)
    _put(item)

    return True

def add_result_to_master_statistics(result: dict) -> dict:
    user_id = result['user_id']
    title = result['splatoon_title']
    battle_date = result['battle_date']
    season = find_season_info_by_date(title, battle_date)

    try:
        item = get_master_by_id(dynamodb_client, user_id)
    except AnalyzerError as e:
        if e.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            item = {
                'user_id': user_id,
                'statistics_id': user_id, # id of master statistics is the same as user_id
                'type': 'master',
                'splatoon_title': title,
                'season_name': season['name'],
                'start_timestamp': battle_date,
                'end_timestamp': battle_date,
                'result_count': 0,
                'buki_performance': {}
            }
            _put(item)

    _update_statistics(item, result)
    item['end_timestamp'] = battle_date
    _put(item)
    
    return True

def add_result_to_daily_statistics(result: dict) -> dict:
    user_id = result['user_id']
    title = result['splatoon_title']
    battle_date = result['battle_date']
    season = find_season_info_by_date(title, battle_date)
    if season is None:
        raise INVALID_PARAMETER_ERROR
    
    start_timestamp, end_timestamp = calc_containing_day_range(battle_date, 11)

    try:
        item = get_by_period(dynamodb_client, user_id, start_timestamp, end_timestamp)
    except AnalyzerError as e:
        if e.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
            item = {
                'user_id': user_id,
                'statistics_id': str(uuid.uuid4()),
                'type': 'daily',
                'splatoon_title': title,
                'season_name': season['name'],
                'start_timestamp': start_timestamp,
                'end_timestamp': end_timestamp,
                'result_count': 0,
                'buki_performance': {}
            }
            _put(item)

    _update_statistics(item, result)
    _put(item)

    return True

def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                new_image = record['dynamodb']['NewImage']
                deserializer = TypeDeserializer()
                #new_result = new_image
                new_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in new_image.items() })
                add_result_to_master_statistics(new_result)
                add_result_to_daily_statistics(new_result)
                return make_response(True)
    elif 'body' in event:
        payload = json.loads(event['body'])
        method = payload['method']

        try:
            if method == 'add_result':
                return make_response(add_result(payload))
        except AnalyzerError as e:
            print(e.msg)
            return make_error_response(e)
        except Exception as e:
            print(str(e))
            return make_error_response(InternalError(str(e)))
    
    return make_error_response(INVALID_OPERATION_ERROR)