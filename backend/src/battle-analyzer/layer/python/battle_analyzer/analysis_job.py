import os
from boto3.dynamodb.types import TypeDeserializer
from battle_analyzer.error import ITEM_NOT_FOUND_ERROR

table_name = os.environ.get('BATTLE_ANALYSIS_JOB_TABLE')

def make_user_job_response(job_item: dict) -> dict:
    return {
        'job_id': job_item['job_id'],
        'user_id': job_item['user_id'],
        'job_name': job_item['job_name'],
        'job_state': job_item['job_state'],
        'created_at': job_item['created_at'],
        'battle_date': job_item['battle_date'],
        'thumbnail_url': job_item['thumbnail_url']
    }

def make_youtube_job_response(job_item: dict) -> dict:
    return {
        'job_id': job_item['job_id'],
        'user_id': job_item['user_id'],
        'job_name': job_item['job_name'],
        'job_state': job_item['job_state'],
        'movie_source': job_item['movie_source'],
        'channel_id': job_item['channel_id'],
        'video_id': job_item['video_id'],
        'created_at': job_item['created_at'],
        'battle_date': job_item['battle_date'],
        'thumbnail_url': job_item['thumbnail_url']
    }

def query(
    dynamodb_client,
    key_condition_expression: str,
    expression_attribute_values: str,
    projection_expression: str = None
) -> list[dict]: 
    
    if projection_expression:
        response = dynamodb_client.query(
            TableName=table_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ProjectionExpression=projection_expression
        )
    else:
        response = dynamodb_client.query(
            TableName=table_name,
            KeyConditionExpression=key_condition_expression,
            ExpressionAttributeValues=expression_attribute_values
        )

    deserializer = TypeDeserializer()
    items = response.get('Items', [])
    return [{ k: deserializer.deserialize(v) for k, v in item.items() } for item in items]

def get_job_by_id(
    dynamodb_client,
    user_id: str,
    job_id: str
) -> dict:
    key_condition_expression='user_id = :uid AND job_id = :jid'
    expression_attribute_values={
        ':uid': {'S': user_id},
        ':jid': {'S': job_id}
    }
    
    jobs = query(dynamodb_client, key_condition_expression, expression_attribute_values)
    
    if len(jobs) != 1:
        raise ITEM_NOT_FOUND_ERROR

    return jobs[0]