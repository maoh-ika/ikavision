import os
import json
import uuid
import time
import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from battle_analyzer.models.analysis_job import AnalysisJobState
from battle_analyzer.error import INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, ITEM_NOT_FOUND_ERROR, AnalyzerError, InternalError
from battle_analyzer.response import make_response, make_error_response 
from battle_analyzer.analysis_job import query, get_job_by_id, make_user_job_response, make_youtube_job_response
    
dynamodb_client = boto3.client('dynamodb')

def get_job(payload: dict) -> dict:
    if 'user_id' not in payload or 'job_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    job_id = payload['job_id']
    
    job = get_job_by_id(dynamodb_client, user_id, job_id)
    if job['movie_source'] == 'user':
        return make_user_job_response(job)
    elif job['movie_source'] == 'youtube':
        return make_youtube_job_response(job)
    else:
        raise InternalError('invalid movie source')

def query_by_user_id(payload: dict) -> list[dict]:
    if 'user_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    key_condition_expression='user_id = :id'
    expression_attribute_values={ ':id': {'S': user_id} }
    job_items = query(dynamodb_client, key_condition_expression, expression_attribute_values)

    state_filter = payload['state'] if 'state' in payload else None 
    
    jobs = []
    for job in job_items:
        if state_filter is not None and job['job_state'] != state_filter:
            continue
        if job['movie_source'] == 'user':
            jobs.append(make_user_job_response(job))
        elif job['movie_source'] == 'youtube':
            jobs.append(make_youtube_job_response(job))
        else:
            raise InternalError('invalid movie source')
    return jobs

def query_job_ids(payload: dict) -> list[dict]:
    if 'user_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    key_condition_expression='user_id = :id'
    expression_attribute_values={ ':id': {'S': user_id} }
    projection_expression = 'job_id,job_state'

    jobs = query(
        dynamodb_client,
        key_condition_expression,
        expression_attribute_values,
        projection_expression
    )

    if 'state' in payload:
        jobs = list(filter(lambda j: j['job_state'] == payload['state'], jobs))

    return list(map(lambda j: { 'job_id': j['job_id'] }, jobs))

def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)

    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'query':
            return make_response(query_by_user_id(payload))
        elif method == 'query_job_ids':
            return make_response(query_job_ids(payload))
        elif method == 'get':
            return make_response(get_job(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))

    print(payload)
    return make_error_response(INVALID_OPERATION_ERROR)