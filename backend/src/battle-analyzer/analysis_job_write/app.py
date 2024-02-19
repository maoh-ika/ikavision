import os
import json
import uuid
import time
import boto3
from boto3.dynamodb.types import TypeSerializer
from battle_analyzer.models.analysis_job import AnalysisJobState
from battle_analyzer.error import INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, AnalyzerError, InternalError
from battle_analyzer.response import make_response, make_error_response 
from battle_analyzer.analysis_job import get_job_by_id, make_user_job_response, make_youtube_job_response
    
s3_client = boto3.client('s3')
dynamodb_client = boto3.client('dynamodb')
analzye_job_table = os.environ.get('BATTLE_ANALYSIS_JOB_TABLE')
movie_bucket_name = os.environ.get('BATTLE_MOVIE_BUCKET')
upload_url_expiration = int(os.environ.get('UPLOAD_URL_EXPIRATION'))
download_url_expiration = int(os.environ.get('DOWNLOAD_URL_EXPIRATION'))

sqs = boto3.client('sqs')
request_queue_url = sqs.get_queue_url(QueueName=os.environ.get('BATTLE_ANALYSIS_REQUEST_QUEUE'))['QueueUrl']

supported_formats = {
    'mp4': 'video/mp4',
    'mov': 'video/quicktime'
}

def _put(job_item: dict):
    serializer = TypeSerializer()
    item_dynamodb_json = { k: serializer.serialize(v) for k, v in job_item.items() }
    dynamodb_client.put_item(
        TableName=analzye_job_table,
        Item=item_dynamodb_json
    )

def _send_analysis_request(
    job_id: str,
    user_id: str,
    channel_id: str,
    video_id: str,
    battle_date: int
):
    message_body = {
        'job_id': job_id,
        'user_id': user_id,
        'type': 'analyze',
        'movie_source': 'youtube',
        'channel_id': channel_id,
        'video_id': video_id,
        'battle_date': battle_date
    }
    sqs.send_message(
        QueueUrl=request_queue_url,
        MessageBody=json.dumps(message_body)
    )

def create_job(payload: dict):
    if 'user_id' not in payload or 'job_name' not in payload or 'movie_source' not in payload or 'battle_date' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    movie_source = payload['movie_source']
    if movie_source not in ['user', 'youtube']:
        raise INVALID_PARAMETER_ERROR

    user_id = payload['user_id']
    job_name = payload['job_name']
    battle_date = payload['battle_date']
    job_id = str(uuid.uuid4())
    thumbnail_url = payload['thumbnail_url'] if 'thumbnail_url' in payload else ''

    if movie_source == 'user':
        if 'format' not in payload:
            raise INVALID_PARAMETER_ERROR
        fmt = payload['format']
        if fmt not in supported_formats.keys():
            raise INVALID_PARAMETER_ERROR
        
        file_name = f'{job_id}.{fmt}'
        object_key = f'{user_id}/{file_name}'

        job_item = {
            'job_id': job_id,
            'user_id': user_id,
            'job_name': job_name,
            'job_state': AnalysisJobState.CREATED.name.lower(),
            'movie_source': movie_source,
            'movie_bucket_name': movie_bucket_name,
            'movie_key': object_key,
            'movie_file_name': file_name,
            'battle_date': battle_date,
            'thumbnail_url': thumbnail_url,
            'created_at': int(time.time()),
            'fail_reason': None
        }
        _put(job_item)
        
        upload_url = generate_upload_url(movie_bucket_name, object_key, supported_formats[fmt])
        return {
            **make_user_job_response(job_item),
            **upload_url
        }
    elif movie_source == 'youtube':
        if 'channel_id' not in payload or 'video_id' not in payload:
            raise INVALID_PARAMETER_ERROR
        
        channel_id = payload['channel_id']
        video_id = payload['video_id']
        job_item = {
            'job_id': job_id,
            'user_id': user_id,
            'job_name': job_name,
            'job_state': AnalysisJobState.MOVIE_UPLOADED.name.lower(),
            'movie_source': movie_source,
            'channel_id': channel_id,
            'video_id': video_id,
            'battle_date': battle_date,
            'thumbnail_url': thumbnail_url,
            'created_at': int(time.time()),
            'fail_reason': None
        }
        _put(job_item)
        _send_analysis_request(job_id, user_id, channel_id, video_id, battle_date)
        
        return { **make_youtube_job_response(job_item) }

def generate_upload_url(bucket_name: str, object_key: str, mime_type: str):
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key,
            'ContentType': mime_type
        },
        ExpiresIn=upload_url_expiration
    )
    exp_time = int(time.time() + upload_url_expiration)

    return {
       'upload_url': presigned_url,
       'expiration_time': exp_time
    }

def generate_download_url(payload: dict):
    if 'user_id' not in payload or 'job_id' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    job_id = payload['job_id']

    job_item = get_job_by_id(user_id, job_id)
    
    bucket_name = job_item['movie_bucket_name']
    object_key = job_item['movie_key']

    presigned_url = s3_client.generate_presigned_url(
        'get_object',
        Params={
            'Bucket': bucket_name,
            'Key': object_key
        },
        ExpiresIn=download_url_expiration
    )
    
    exp_time = int(time.time() + download_url_expiration)

    return {
       'download_url': presigned_url,
       'expiration_time': exp_time
    }

def lambda_handler(event, context):
    if 'body' not in event:
        return make_error_response(INVALID_PARAMETER_ERROR)

    payload = json.loads(event['body'])
    method = payload['method']

    try:
        if method == 'create_job':
            return make_response(create_job(payload))
        elif method == 'download_url':
            return make_response(generate_download_url(payload))
    except AnalyzerError as e:
        print(e.msg)
        return make_error_response(e)
    except Exception as e:
        print(str(e))
        return make_error_response(InternalError(str(e)))

    print(payload)
    return make_error_response(INVALID_OPERATION_ERROR)