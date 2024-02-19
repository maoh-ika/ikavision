import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer
from battle_analyzer.error import AnalyzerError, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, ITEM_NOT_FOUND_ERROR, InternalError, ErrorCode
from battle_analyzer.response import make_response, make_error_response
from battle_analyzer.analysis_result import sammary_projection_expression, get_result_by_result_id, get_results_by_job_id, get_results_by_battle_date, get_pagiation 
    
dynamodb_client = boto3.client('dynamodb')

def query_sammaries_by_job_ids(payload: dict) -> list[list[dict]]:
    if 'user_id' not in payload or 'job_ids' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    job_ids = payload['job_ids']

    results = []
    for job_id in job_ids:
        try:
            res = get_results_by_job_id(dynamodb_client, user_id, job_id, sammary_projection_expression)
            results.append(res)
        except AnalyzerError as err:
            if err.code == ErrorCode.ITEM_NOT_FOUND_ERROR_CODE:
                results.append([])
            else:
                raise err

    return results

def query_sammaries_by_battle_date(payload: dict) -> list[dict]:
    if 'user_id' not in payload or 'start_battle_date' not in payload or 'end_battle_date' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    start_date = payload['start_battle_date']
    end_date = payload['end_battle_date']
    exclusive_start_key = payload['page_token'] if 'page_token' in payload else None
    limit = payload['page_size'] if 'page_size' in payload else 10
    order = payload['order'] if 'order' in payload else 'desc'
    return get_results_by_battle_date(dynamodb_client, user_id, start_date, end_date, sammary_projection_expression, limit, order, exclusive_start_key)

def query_sammaries_pagination(payload: dict) -> list[dict]:
    if 'user_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    exclusive_start_key = payload['page_token'] if 'page_token' in payload else None
    limit = payload['page_size'] if 'page_size' in payload else 10
    order = payload['order'] if 'order' in payload else 'desc'

    key_condition_expression = 'user_id = :uid'
    expression_attribute_values = {
        ':uid': { 'S': user_id }
    }
    
    index_name = 'BattleDateIndex'
    return get_pagiation(dynamodb_client, key_condition_expression, expression_attribute_values, index_name, limit, order, exclusive_start_key, sammary_projection_expression)


def get_result_by_id(payload: dict) -> list[dict]:
    if 'user_id' not in payload or 'result_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    result_id = payload['result_id']
    return get_result_by_result_id(dynamodb_client, user_id, result_id)

def get_results_by_job_id(payload: dict) -> list[dict]:
    if 'user_id' not in payload or 'job_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    job_id = payload['job_id']
    return get_results_by_job_id(dynamodb_client, user_id, job_id)

def get_results_by_battle_date(payload: dict) -> list[dict]:
    if 'user_id' not in payload or 'start_battle_date' not in payload or 'end_battle_date' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    start_date = payload['start_battle_date']
    end_date = payload['end_battle_date']
    exclusive_start_key = payload['page_token'] if 'page_token' in payload else None
    limit = payload['page_size'] if 'page_size' in payload else 100
    order = payload['order'] if 'order' in payload else 'desc'
    return get_results_by_battle_date(dynamodb_client, user_id, start_date, end_date, limit=limit, order=order, exclusive_start_key=exclusive_start_key)

def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)

    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'query_sammaries':
            if 'job_ids' in payload:
                return make_response(query_sammaries_by_job_ids(payload))
            elif 'start_battle_date' in payload:
                return make_response(query_sammaries_by_battle_date(payload))
        elif method == 'query_sammaries_pagination':
            return make_response(query_sammaries_pagination(payload))
        elif method == 'get_result':
            return make_response(get_result_by_id(payload))
        elif method == 'get_results':
            if 'job_id' in payload:
                return make_response(get_results_by_job_id(payload))
            elif 'start_battle_date' in payload:
                return make_response(get_results_by_battle_date(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))

    return make_error_response(INVALID_OPERATION_ERROR)