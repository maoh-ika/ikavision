import requests
import os
import json
from typing import Any
from dotenv import load_dotenv
import boto3
from boto3.dynamodb.types import TypeDeserializer
from run_worker import get_model_paths
from tools.download_ytb import get_list
from tools.ytb_filter import filters

load_dotenv()

def get_job_item(dynamodb_client: Any, video_id: str, user_id: str) -> dict:
    try:
        response = dynamodb_client.query(
            TableName=os.environ.get('AWS_DYNAMODB_ANALYSIS_JOB_TABLE'),
            IndexName='YoutubeIdIndex',
            KeyConditionExpression='user_id = :uid AND video_id = :vid',
            ExpressionAttributeValues={
                ':uid': {'S': user_id},
                ':vid': {'S': video_id}
            }
        )
    except Exception as e:
        print(str(e))
        return None
    
    items = response.get('Items', [])
    if len(items) == 0:
        return None
    
    deserializer = TypeDeserializer()
    return { k: deserializer.deserialize(v) for k, v in items[0].items() }

def create_job(user_id: str, job_name: str, channel_id: str, video_id: str, battle_date: int, thumbnail_url: str):
    api_gateway_url = f'{os.environ.get("AWS_BATTLE_ANALYZER_ENDPOINT")}/analysis_job'
    
    payload = {
        'method': 'create_job',
        'user_id': user_id,
        'job_name': job_name,
        'movie_source': 'youtube',
        'channel_id': channel_id,
        'video_id': video_id,
        'battle_date': battle_date,
        'thumbnail_url': thumbnail_url
    }
    headers={
        'Content-Type': 'application/json',
        'X-Api-Key': os.environ.get('AWS_BATTLE_ANALYZER_API_KEY')
    }
    res = requests.post(api_gateway_url, json=payload, headers=headers)
    res_data = json.loads(res.text)
    if 'error' in res_data:
        raise Exception(res_data['error']['msg'])
    elif 'message' in res_data:
        raise Exception(res_data['message'])
    
def is_job_exists(user_id: str, video_id: str):
    dynamodb_client = boto3.client('dynamodb')
    job_item = get_job_item(dynamodb_client, video_id=video_id, user_id=user_id)
    return job_item is not None
    
def put_analysis_request(user_id: str, video: dict):
    video_title = video['title']
    video_id = video['id']
    channel_id = video['channel_id']
        
    create_job(
        user_id=user_id,
        job_name=video_title,
        channel_id=channel_id,
        video_id=video_id,
        battle_date=video['published_at'],
        thumbnail_url=video['thumbnail_url']
    )

if __name__ == '__main__':
    temp_dir = './temp'

    channel_id = 'UCoA0JdwZGY6iDMdx6US4BMQ'
    #channel_id = 'UC3dMKGxwpf_SDPkq0HWFhPQ'
    channel_dir = f'{temp_dir}/{channel_id}'
    os.makedirs(channel_dir, exist_ok=True)

    videos = get_list(channel_id=channel_id, max_count=1, cache_dir=channel_dir)
    video_count = len(videos)
    if video_count == 0:
        exit()
    
    channel_name = videos[0]['channel_name']

    print(f'Channel id: {channel_id}')
    print(f'Channel name: {channel_name}')
    print(f'Video count: {video_count}')

    for idx, video in enumerate(videos):
        if is_job_exists(channel_id, video['id']):
            msg = f'job alread exists. skip: {video["title"]} ({video["id"]})'
            print(msg)
            continue

        print(f'send analysis request. id: {video["id"]}, title: {video["title"]}')
        put_analysis_request(channel_id, video)