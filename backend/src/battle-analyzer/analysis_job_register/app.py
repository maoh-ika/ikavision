import os
import json
import time
import boto3
from battle_analyzer.models.analysis_job import AnalysisJob, AnalysisJobState
from battle_analyzer.error import INVALID_KEY_ERROR, UNKNONW_FILE_FORMAT_ERROR, ErrorCode, AnalyzerError
from battle_analyzer.response import make_response 

sqs = boto3.client('sqs')
request_queue_url = sqs.get_queue_url(QueueName=os.environ.get('BATTLE_ANALYSIS_REQUEST_QUEUE'))['QueueUrl']

dynamodb = boto3.client('dynamodb')
analzye_job_table = os.environ.get('BATTLE_ANALYSIS_JOB_TABLE')

def fail_job(job_id: str, user_id, error: AnalyzerError):
    item_key = {
        'job_id': {'S': job_id},
        'user_id': {'S': user_id}
    }
    update_expression = 'SET job_state = :val1, fail_reason = :val2'
    expression_attribute_values = {
        ':val1': { 'S': AnalysisJobState.FAILED.name.lower() },
        ':val2': { 'M': {
                'msg': { 'S': error.msg },
                'code': { 'N': str(error.code.value) }
            }
        }
    }
    dynamodb.update_item(
        TableName=analzye_job_table,
        Key=item_key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

def update_job_state(job_id: str, user_id: str):
    item_key = {
        'job_id': {'S': job_id},
        'user_id': {'S': user_id}
    }
    update_expression = 'SET job_state = :val'
    expression_attribute_values = {
        ':val': { 'S': AnalysisJobState.MOVIE_UPLOADED.name.lower() },
    }
    dynamodb.update_item(
        TableName=analzye_job_table,
        Key=item_key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

def send_analysis_request(
    job_id: str,
    user_id: str,
    bucket: str,
    object_key: str,
    file_name: str
):
    message_body = {
        'job_id': job_id,
        'user_id': user_id,
        'type': 'analyze',
        'movie_source': 'user',
        's3_bucket': bucket,
        's3_key': object_key,
        'file_name': file_name 
    }
    sqs.send_message(
        QueueUrl=request_queue_url,
        MessageBody=json.dumps(message_body)
    )

def register(s3_record: dict):
    bucket = s3_record['bucket']['name']
    key = s3_record['object']['key']
    tokens = key.split('/')
    if len(tokens) != 2:
        raise INVALID_KEY_ERROR
    
    user_id, file_name = tokens[0], tokens[1]
    
    file_name_tokens = os.path.splitext(file_name)
    if len(file_name_tokens) != 2:
        raise UNKNONW_FILE_FORMAT_ERROR
    
    job_id = file_name_tokens[0]

    try:
        update_job_state(job_id, user_id)
        send_analysis_request(
            job_id=job_id,
            user_id=user_id,
            bucket=bucket,
            object_key=key,
            file_name=file_name
        )
    except Exception as e:
        fail_job(job_id, user_id, AnalyzerError(msg=str(e), code=ErrorCode.INTERNAL_ERROR))
        raise e
    
    return job_id

def lambda_handler(event, context):
    records = event['Records']
    job_ids = []
    for record in records:
        if 's3' in record:
            try:
                job_id = register(record['s3'])
            except Exception as e:
                print(str(e))
                continue

            job_ids.append(job_id)

    return make_response({
        'job_ids': job_ids
    })