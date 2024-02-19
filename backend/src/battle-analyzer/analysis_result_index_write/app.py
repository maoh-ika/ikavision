import os
import json
import boto3
from boto3.dynamodb.types import TypeDeserializer, Binary
from battle_analyzer.error import AnalyzerError, INVALID_OPERATION_ERROR, INVALID_PARAMETER_ERROR, InternalError
from battle_analyzer.response import make_response, make_error_response
from battle_analyzer.utils import replace_decimals
from opensearchpy import OpenSearch, RequestsHttpConnection, helpers
from requests_aws4auth import AWS4Auth
from battle_analyzer.analysis_result import get_results_by_battle_date 

dynamodb_client = boto3.client('dynamodb')
aos_index_name = os.environ.get('AOS_INDEX_NAME')
end_point = os.environ.get('AOS_END_POINT')
region = os.environ.get('AWS_REGION_ID')

session = boto3.Session()
creds = session.get_credentials()
awsauth = AWS4Auth(
    creds.access_key,
    creds.secret_key,
    region,
    'es', 
    session_token=creds.token
)

os_client = OpenSearch(
    hosts=[end_point],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection,
    timeout=300
)

def _conv_death_event(evt: dict, battle_start_frame: int, frame_rate: int, enemies: list[str]) -> dict:
    death_frame = evt['start_frame']
    death_time = (death_frame - battle_start_frame) / frame_rate
    kill_idx = evt['kill_player_index']
    killer_name = enemies[kill_idx]['name'] if kill_idx is not None else None

    return {
        'death_reason': evt['death_reason'],
        'reason_type': evt['reason_type'],
        'death_time': death_time,
        'killer_name': killer_name
    }

def _conv_kill_event(evt: dict, battle_start_frame: int, frame_rate: int, enemies: list[str]) -> dict:
    kill_frame = evt['start_frame']
    kill_time = (kill_frame - battle_start_frame) / frame_rate
    death_idx = evt['death_player_index']
    death_name = enemies[death_idx]['name'] if death_idx is not None else None

    return {
        'kill_time': kill_time,
        'dead_name': death_name
    }

def _conv_player(enemy: dict) -> dict:
    return {
        'name': enemy['name']
    }

def make_doc(result: dict):
    battle_start = result['battle_open_event']['end_frame']
    battle_end = result['battle_end_event']['start_frame']
    frame_rate = result['frame_rate']
    battle_duration = (battle_end - battle_start) / frame_rate
    main_player_index = result['main_player_index']
    main_player_name = result['team'][main_player_index]['name']

    data = {
        'user_id': result['user_id'],
        'result_id': result['result_id'],
        'job_id': result['job_id'],
        'movie_frames': result['movie_frames'],
        'frame_rate': result['frame_rate'],
        'battle_open_frame': result['battle_open_event']['start_frame'],
        'battle_end_frame': result['battle_end_event']['end_frame'],
        'result_start_frame': result['battle_result_event']['start_frame'],
        'result_end_frame': result['battle_result_event']['end_frame'],
        'battle_date': result['battle_date'],
        'battle_duration': battle_duration,
        'battle_result': result['battle_result'],
        'battle_rule': result['battle_rule'],
        'battle_stage': result['battle_stage'],
        'death_count': result['death_count'],
        'death_events': [_conv_death_event(evt, battle_start, frame_rate, result['enemy']) for evt in result['death_events'] if evt['death_player_side'] == 'team' and evt['death_player_index'] == main_player_index],
        'enemy': [_conv_player(p) for p in result['enemy']],
        'enemy_bukis': result['enemy_bukis'],
        'enemy_result_count': result['enemy_result_count'],
        'kill_count': result['kill_count'],
        'kill_events': [_conv_kill_event(evt, battle_start, frame_rate, result['enemy']) for evt in result['kill_events'] if evt['kill_player_side'] == 'team' and evt['kill_player_index'] == main_player_index],
        'match_rate': result['match_rate'],
        'match_type': result['match_type'],
        'sp_count': result['sp_count'],
        'team': [_conv_player(p) for p in result['team']],
        'team_bukis': result['team_bukis'],
        'main_player_buki': result['team_bukis'][main_player_index],
        'team_result_count': result['team_result_count'],
        'main_player_name': main_player_name
    }

    return data

def create_index(result: dict):
    data = make_doc(result)
    document = json.dumps(data, ensure_ascii=False)
    os_client.index(aos_index_name, body=document, id=data['result_id'])

def delete_index(result: dict):
    os_client.delete(aos_index_name, id=result['result_id'])

def make_indices(payload: dict):
    if 'user_id' not in payload or 'start_date' not in payload or 'end_date' not in payload:
        raise INVALID_PARAMETER_ERROR
    
    user_id = payload['user_id']
    start_date = payload['start_date']
    end_date = payload['end_date']
    exclusive_start_key = None
    limit = 50
    order = 'asc'
    
    index_projection_expression = '''
        user_id,
        result_id,
        job_id,
        movie_frames,
        frame_rate,
        battle_open_event,
        battle_end_event,
        battle_result_event,
        battle_date,
        battle_result,
        battle_rule,
        battle_stage,
        death_count,
        enemy,
        death_events,
        enemy_bukis,
        enemy_result_count,
        kill_count,
        kill_events,
        match_rate,
        match_type,
        sp_count,
        team,
        team_bukis,
        team_result_count,
        main_player_index
    '''

    is_first = True
    while is_first or exclusive_start_key:
        is_first = False
        res = get_results_by_battle_date(
            dynamodb_client,
            user_id,
            start_date,
            end_date,
            index_projection_expression,
            limit,
            order,
            exclusive_start_key
        )
        docs = []
        for sammary in res['sammaries']:
            doc = make_doc(sammary)
            doc['_index'] = aos_index_name
            doc['_id'] = doc['result_id']
            docs.append(doc)
        
        helpers.bulk(os_client, docs, max_retries=3)
        exclusive_start_key = res['page_token']

def lambda_handler(event, context):
    if 'Records' in event:
        for record in event['Records']:
            if record['eventName'] == 'INSERT':
                try:
                    new_image = record['dynamodb']['NewImage']
                    deserializer = TypeDeserializer()
                    #new_result = new_image
                    new_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in new_image.items() })
                    print(f'create result index {new_result["result_id"]}')
                    create_index(new_result)
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
                    print(f'delete result index {new_result["result_id"]}')
                    delete_index(deleted_result)
                    return make_response(True)
                except AnalyzerError as e:
                    print(e.msg)
                    return make_error_response(e)
                except Exception as e:
                    print(str(e))
                    return make_error_response(InternalError(str(e)))
            elif record['eventName'] == 'MODIFY':
                try:
                    new_image = record['dynamodb']['NewImage']
                    deserializer = TypeDeserializer()
                    #new_result = new_image
                    new_result = replace_decimals({ k: deserializer.deserialize(v) for k, v in new_image.items() })
                    print(f'update result index {new_result["result_id"]}')
                    create_index(new_result) # create_index updates existing index by using same id 
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
#            if method == 'make_indices':
#                print(f'bulk appd result index {payload}')
#                make_indices(payload)
#                return make_response(True)
            pass
        except AnalyzerError as e:
            print(e.msg)
            return make_error_response(e)
        except Exception as e:
            print(str(e))
            return make_error_response(InternalError(str(e)))
    
    return make_error_response(INVALID_OPERATION_ERROR)
    