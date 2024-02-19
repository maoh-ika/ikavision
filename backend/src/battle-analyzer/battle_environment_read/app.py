import os
import json
import copy
import boto3
import zlib
from battle_analyzer.error import AnalyzerError, INVALID_PARAMETER_ERROR, INVALID_OPERATION_ERROR, InternalError
from battle_analyzer.response import make_response, make_error_response
from battle_analyzer.battle_environment import query, get_by_time_range, make_season_env_tag, make_daily_env_tag, make_season_match_env_tag, make_daily_match_env_tag, x_match_rate_layers
    
dynamodb_client = boto3.client('dynamodb')
lambda_client = boto3.client('lambda')

def _get_query_time_range(start_date, end_date) -> (int, int):
    day_seconds = 24 * 3600 - 1 # to get stats containing start/end date
    st = start_date - day_seconds
    et = end_date + day_seconds
    return st, et

def query_season_environments_by_title(payload: dict):
    if 'splatoon_title' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    env_tag = make_season_env_tag(payload['splatoon_title'])
    return query(dynamodb_client, env_tag)

def query_season_match_environments_by_title(payload: dict):
    if 'splatoon_title' not in payload or 'match_type' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    match_type = payload['match_type']
    match_rate = None
    if match_type == 'x_match':
        if 'match_rate' not in payload:
            raise INVALID_PARAMETER_ERROR
        match_rate = payload['match_rate']
    
    env_tag = make_season_match_env_tag(payload['splatoon_title'], match_type, rate_label=match_rate)
    return query(dynamodb_client, env_tag)

def query_season_x_match_environments_by_title(payload: dict):
    if 'splatoon_title' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    ignore_rates = payload['ignore_rates'] if 'ignore_rates' in payload else []
    request_rates = []
    for layer in x_match_rate_layers:
        rate_label = layer['label']
        if len(list(filter(lambda r: r == rate_label, ignore_rates))) == 0:
            request_rates.append(rate_label)

    envs = []
    for rate in request_rates: 
        env_tag = make_season_match_env_tag(payload['splatoon_title'], 'x_match', rate_label=rate)
        envs += query(dynamodb_client, env_tag)

    return envs

def query_daily_environments_by_date(payload: dict):
    if 'splatoon_title' not in payload or 'start_date' not in payload or 'end_date' not in payload:
        raise INVALID_PARAMETER_ERROR

    title = payload['splatoon_title']
    start_date = payload['start_date']
    end_date = payload['end_date']
    st, et = _get_query_time_range(start_date, end_date)

    return get_by_time_range(dynamodb_client, make_daily_env_tag(title), st, et)

def query_daily_match_environments_by_date(payload: dict):
    if 'splatoon_title' not in payload or 'start_date' not in payload or 'end_date' not in payload or 'match_type' not in payload:
        raise INVALID_PARAMETER_ERROR

    title = payload['splatoon_title']
    start_date = payload['start_date']
    end_date = payload['end_date']
    st, et = _get_query_time_range(start_date, end_date)
    
    match_type = payload['match_type']
    match_rate = None
    if match_type == 'x_match':
        if 'match_rate' not in payload:
            raise INVALID_PARAMETER_ERROR
        match_rate = payload['match_rate']

    return get_by_time_range(dynamodb_client, make_daily_match_env_tag(title, match_type, rate_label=match_rate), st, et)

def query_daily_x_match_environments_by_date(payload: dict):
    if 'splatoon_title' not in payload or 'start_date' not in payload or 'end_date' not in payload:
        raise INVALID_PARAMETER_ERROR

    title = payload['splatoon_title']
    start_date = payload['start_date']
    end_date = payload['end_date']
    st, et = _get_query_time_range(start_date, end_date)
    
    ignore_rates = payload['ignore_rates'] if 'ignore_rates' in payload else []
    request_rates = []
    for layer in x_match_rate_layers:
        rate_label = layer['label']
        if len(list(filter(lambda r: r == rate_label, ignore_rates))) == 0:
            request_rates.append(rate_label)

    envs = []
    for rate in request_rates: 
        env_tag = make_daily_match_env_tag(title, 'x_match', rate_label=rate)
        envs += get_by_time_range(dynamodb_client, env_tag, st, et)

    return envs

def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)
    
    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'query_seasons':
            return make_response(query_season_environments_by_title(payload))
        elif method == 'query_daily':
            return make_response(query_daily_environments_by_date(payload))
        elif method == 'query_seasons_match':
            return make_response(query_season_match_environments_by_title(payload))
        elif method == 'query_seasons_x_match':
            return make_response(query_season_x_match_environments_by_title(payload))
        elif method == 'query_daily_match':
            return make_response(query_daily_match_environments_by_date(payload))
        elif method == 'query_daily_x_match':
            return make_response(query_daily_x_match_environments_by_date(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))
    
    return make_error_response(INVALID_OPERATION_ERROR)