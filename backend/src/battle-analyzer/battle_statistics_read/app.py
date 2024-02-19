import json
import boto3
from battle_analyzer.error import AnalyzerError, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, InternalError
from battle_analyzer.response import make_response, make_error_response
from battle_analyzer.battle_statistics import get_by_time_range, get_by_id
    
dynamodb_client = boto3.client('dynamodb')

def get(payload: dict):
    if 'user_id' not in payload or 'statistics_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    return get_by_id(dynamodb_client, payload['user_id'], payload['statistics_id'])

def get_master(payload: dict):
    if 'user_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    return get_by_id(dynamodb_client, payload['user_id'], payload['user_id'])

def get_dailies(payload: dict):
    if 'user_id' not in payload or 'start_date' not in payload or 'end_date' not in payload:
        raise INVALID_PARAMETER_ERROR

    day_seconds = 24 * 3600 - 1 # to get stats containing start/end date
    st = payload['start_date'] - day_seconds
    et = payload['end_date'] + day_seconds

    daily = get_by_time_range(dynamodb_client, payload['user_id'], st, et)
    return list(filter(lambda d: d['type'] == 'daily', daily))
    
def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)
    
    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'get':
            return make_response(get(payload))
        elif method == 'get_master':
            return make_response(get_master(payload))
        elif method == 'get_daily':
            return make_response(get_dailies(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))
    
    return make_error_response(INVALID_OPERATION_ERROR)