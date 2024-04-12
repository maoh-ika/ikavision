import time
import os
import json
import hashlib
import argparse
import shutil
from multiprocessing import Process, Value
from typing import Any
from dataclasses import dataclass
from dotenv import load_dotenv
import requests
import tqdm
import boto3
from boto3.dynamodb.types import TypeDeserializer
from battle_analyzer import init, BattleAnalyzer, BattleAnalysisParams, BattlePreprocessParams, ModelPaths, BattleAnalysisResult
from models.ika_player import IkaPlayer 
from models.buki import Buki
from models.battle import BattleSide
from events.death_event import DeathEvent
from events.kill_event import KillEvent
from events.player_number_balance_event import PlayerNumberBalanceEvent
from events.battle_countdown_event import BattleCountEvent
from events.special_weapon_event import SpecialWeaponEvent, SpecialWeaponEventType
from prediction.match_frame_analyzer import MatchAnalysisResult
from tools.download_ytb import download 
from error import *
from log import create_prod_logger

load_dotenv()

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--device', type=str)
    parser.add_argument('--process', type=int, default=0)
    parser.add_argument('--date_after', type=int, default=None)
    parser.add_argument('--date_before', type=int, default=None)
    return parser.parse_args()

@dataclass
class AnalysisCommand:
    type: str
    timestamp: int
    sqs_url: str

@dataclass
class AnalysisRequest(AnalysisCommand):
    user_id: str
    job_id: str
    battle_date: int
    movie_source: str
    s3_bucket: str = None
    s3_key: str = None
    file_name: str = None
    channel_id: str = None
    video_id: str = None

def receive_message(sqs_client: Any, request_url: str, command_url: str, req_visibility_timeout: int) -> (AnalysisCommand, str):
    while True:
        # first, check command queue.
        response = sqs_client.receive_message(
            QueueUrl=command_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=1,
            WaitTimeSeconds=1
        )

        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            message_body = json.loads(message['Body'])
            timestamp = int(message['Attributes']['SentTimestamp']) // 1000
            cmd = AnalysisCommand(type=message_body['command'], timestamp=timestamp, sqs_url=command_url)
            return cmd, receipt_handle

        # if no command found, check analysis requests.
        response = sqs_client.receive_message(
            QueueUrl=request_url,
            AttributeNames=['All'],
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All'],
            VisibilityTimeout=req_visibility_timeout,
            WaitTimeSeconds=20
        )
        if 'Messages' in response:
            message = response['Messages'][0]
            receipt_handle = message['ReceiptHandle']
            message_body = json.loads(message['Body'])
            movie_source = message_body['movie_source']
            timestamp = int(message['Attributes']['SentTimestamp']) // 1000

            if movie_source == 'user':
                req = AnalysisRequest(
                    type=message_body['type'],
                    user_id=message_body['user_id'],
                    job_id=message_body['job_id'],
                    battle_date=message_body['battle_date'],
                    movie_source=movie_source,
                    s3_bucket=message_body['s3_bucket'],
                    s3_key=message_body['s3_key'],
                    file_name=message_body['file_name'],
                    timestamp=timestamp,
                    sqs_url=request_url
                )
            elif movie_source == 'youtube':
                req = AnalysisRequest(
                    type=message_body['type'],
                    user_id=message_body['user_id'],
                    job_id=message_body['job_id'],
                    battle_date=message_body['battle_date'],
                    movie_source=movie_source,
                    channel_id=message_body['channel_id'],
                    video_id=message_body['video_id'],
                    timestamp=timestamp,
                    sqs_url=request_url
                )
            else:
                req = None

            return req, receipt_handle

        else:
            print('No messages available. Waiting...')
            time.sleep(5)

def download_user_movie_file(s3_client: Any, s3_bucket: str, s3_key: str, out_dir: str, local_dir: str=None) -> str:
    ext = os.path.splitext(os.path.basename(s3_key))[1]
    key_hash = hashlib.sha256(s3_key.encode('utf-8')).hexdigest()
    file_path = f'{out_dir}/{key_hash}{ext}'
    local_file_path = f'{local_dir}/{key_hash}{ext}' if local_dir else None
    if os.path.exists(file_path):
        print(f'use cached: {file_path}')
        if local_file_path:
            print(f'move to local: {local_file_path}')
            shutil.copy(file_path, local_file_path)
            file_path = local_file_path
    else:
        if local_file_path:
            print(f'donwload to local: {local_file_path}')
            file_path = local_file_path

        s3_client.download_file(
            s3_bucket,
            s3_key,
            file_path,
            Callback=tqdm.wrapattr(open(file_path, 'wb'), 'write', total=os.path.getsize(file_path), desc='Downloading from S3')
        )
    return file_path

def download_youtube_movie_file(video_id: str, out_dir: str, local_dir: str=None) -> str:
    file_name = f'{video_id}.mp4'
    file_path = f'{out_dir}/{file_name}'
    local_file_path = f'{local_dir}/{file_name}' if local_dir else None
    if os.path.exists(file_path):
        print(f'use cached: {file_path}')
        if local_file_path:
            print(f'move to local: {local_file_path}')
            shutil.copy(file_path, local_file_path)
            file_path = local_file_path
    else:
        try:
            if local_file_path:
                print(f'donwload to local: {local_file_path}')
                file_path = local_file_path
                download(video_id, local_dir, file_name)
            else:
                download(video_id, out_dir, file_name)
        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            raise e
    return file_path
    
def download_models(s3_client: Any, s3_bucket: str, s3_key: str, out_dir: str) -> ModelPaths:
    pass

def get_model_paths() -> ModelPaths:
    return ModelPaths(
        ikalamp_model_path=os.environ.get('IKALAMP_MODEL_PATH'),
        ika_player_model_path=os.environ.get('IKA_PLAYER_MODEL_PATH'),
        notification_model_path=os.environ.get('NOTIFICATION_MODEL_PATH'),
        plate_model_path=os.environ.get('PLATE_MODEL_PATH'),
        battle_indicator_model_path=os.environ.get('BATTLE_INDICATOR_MODEL_PATH'),
        match_model_path=os.environ.get('MATCH_MODEL_PATH'),
        char_type_model_path=os.environ.get('CHAR_TYPE_MODEL_PATH'),
        hiragana_model_path=os.environ.get('HIRAGANA_MODEL_PATH'),
        katakana_model_path=os.environ.get('KATAKANA_MODEL_PATH'),
        number_model_path=os.environ.get('NUMBER_MODEL_PATH'),
        alphabet_model_path=os.environ.get('ALPHABET_MODEL_PATH'),
        symbol_model_path=os.environ.get('SYMBOL_MODEL_PATH'),
        char_model_path=os.environ.get('CHAR_MODEL_PATH'),
        stage_model_path=os.environ.get('STAGE_MODEL_PATH'),
        buki_model_path=os.environ.get('BUKI_MODEL_PATH'),
        sub_weapon_model_path=os.environ.get('SUB_WEAPON_MODEL_PATH'),
        sp_weapon_model_path=os.environ.get('SPECIAL_WEAPON_MODEL_PATH'),
        weapon_gauge_model_path=os.environ.get('WEAPON_GAUGE_MODEL_PATH'),
        ink_tank_model_path=os.environ.get('INK_TANK_MODEL_PATH')
    )

def get_job_item(dynamodb_client: Any, job_id: str, user_id: str) -> dict:
    try:
        response = dynamodb_client.query(
            TableName=os.environ.get('AWS_DYNAMODB_ANALYSIS_JOB_TABLE'),
            KeyConditionExpression='user_id = :uid AND job_id = :jid',
            ExpressionAttributeValues={
                ':uid': {'S': user_id},
                ':jid': {'S': job_id}
            }
        )
    except Exception as e:
        print(str(e))
        return None
    
    items = response.get('Items', [])
    if len(items) != 1:
        return None
    
    deserializer = TypeDeserializer()
    return { k: deserializer.deserialize(v) for k, v in items[0].items() }

def update_job_item(
    dynamodb_client: Any,
    user_id: str,
    job_id: str,
    update_expression: dict,
    expression_attribute_values: dict
):
    item_key = {
        'job_id': {'S': job_id},
        'user_id': {'S': user_id}
    }
    analzye_job_table = os.environ.get('AWS_DYNAMODB_ANALYSIS_JOB_TABLE')
    dynamodb_client.update_item(
        TableName=analzye_job_table,
        Key=item_key,
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_attribute_values
    )

def set_processing_state(dynamodb_client: Any, job_id: str, user_id: str):
    update_expression = 'SET job_state = :val'
    expression_attribute_values = {
        ':val': { 'S': 'processing' }
    }
    update_job_item(dynamodb_client, user_id, job_id, update_expression, expression_attribute_values)


def set_complete_state(dynamodb_client: Any, job_id: str, user_id: str):
    update_expression = 'SET job_state = :val'
    expression_attribute_values = {
        ':val': { 'S': 'completed' }
    }
    update_job_item(dynamodb_client, user_id, job_id, update_expression, expression_attribute_values)


def set_fail_state(dynamodb_client: Any, job_id: str, user_id: str, msg: str, code: int):
    update_expression = 'SET job_state = :val1, fail_reason = :val2'
    expression_attribute_values = {
        ':val1': { 'S': 'failed' },
        ':val2': { 'M': {
                'msg': { 'S': msg },
                'code': { 'N': str(code) }
            }
        }
    }
    update_job_item(dynamodb_client, user_id, job_id, update_expression, expression_attribute_values)

def create_analzye_result(
    job_id: str,
    user_id: str,
    file_name: str,
    result: BattleAnalysisResult,
    pre_result: BattlePreprocessParams):
    def _to_player_dict(player: IkaPlayer) -> dict:
        return {
            'id': player.id,
            'name': player.name,
            'nickname': player.nickname,
            'lamp_ord': player.lamp_ord
        }
    
    def _to_buki_dict(buki: Buki) -> dict:
        return {
            'main_weapon': Buki.get_buki_id(buki.main_weapon),
            'sub_weapon': Buki.get_buki_id(buki.sub_weapon),
            'sp_weapon': Buki.get_buki_id(buki.sp_weapon),
            'sub_ink_consumption_percent': buki.sub_ink_consumption_percent
        }
    
    def _to_death_dict(evt: DeathEvent) -> dict:
        return {
            'death_player_index': evt.death_player.lamp_ord if evt.death_player is not None else None,
            'death_player_side': evt.death_player.side.name.lower() if evt.death_player is not None else None,
            'kill_player_index': evt.kill_player.lamp_ord if evt.kill_player is not None else None,
            'kill_player_side': evt.kill_player.side.name.lower() if evt.kill_player is not None else None,
            'death_reason': evt.death_reason,
            'reason_type': evt.reason_type.name.lower(),
            'start_frame': evt.start_frame,
            'end_frame': evt.end_frame
        }
    
    def _to_kill_dict(evt: KillEvent) -> dict:
        return {
            'kill_player_index': evt.kill_player.lamp_ord if evt.kill_player is not None else None,
            'kill_player_side': evt.kill_player.side.name.lower() if evt.kill_player is not None else None,
            'death_player_index': evt.death_player.lamp_ord if evt.death_player is not None else None,
            'death_player_side': evt.death_player.side.name.lower() if evt.death_player is not None else None,
            'start_frame': evt.start_frame,
            'end_frame': evt.end_frame
        }
    
    def _to_player_number_balance_dict(evt: PlayerNumberBalanceEvent) -> dict:
        return {
            'team_number': evt.team_number,
            'enemy_number': evt.enemy_number,
            'balance_state': evt.balance_state.name.lower(),
            'start_frame': evt.start_frame,
            'end_frame': evt.end_frame,
        }
    
    def _to_battle_count_dict(evt: BattleCountEvent) -> dict:
        return {
            'count': evt.count,
            'start_frame': evt.start_frame,
            'end_frame': evt.end_frame
        }
    
    def _to_sp_weapon_dict(evt: SpecialWeaponEvent) -> dict:
        return {
            'type': evt.type.name.lower(),
            'player_index': evt.player.lamp_ord,
            'player_side': evt.player.side.name.lower(),
            'start_frame': evt.start_frame,
            'end_frame': evt.end_frame
        }
    
    def _to_rgb_color(bgr: list[int]) -> list[int]:
        return [bgr[2], bgr[1], bgr[0]]
    
    def _kill_count(events: list[KillEvent], main_player_index: int) -> int:
        return len(list(filter(lambda evt: evt.kill_player.side == BattleSide.TEAM and evt.kill_player.lamp_ord == main_player_index, events)))
    
    def _death_count(events: list[DeathEvent], main_player_index: int) -> int:
        return len(list(filter(lambda evt: evt.death_player.side == BattleSide.TEAM and evt.death_player.lamp_ord == main_player_index, events)))
    
    def _sp_count(events: list[SpecialWeaponEvent], main_player_index: int) -> int:
        return len(list(filter(lambda evt: evt.player.side == BattleSide.TEAM and evt.player.lamp_ord == main_player_index and evt.type == SpecialWeaponEventType.TRIGGERED, events)))

    result_item = {
        'job_id': job_id,
        'user_id': user_id,
        'created_at': int(time.time()),
        'movie_name': file_name,
        'movie_width': pre_result.movie_width,
        'movie_height': pre_result.movie_height,
        'movie_frames': pre_result.movie_frames,
        'frame_rate': pre_result.frame_rate,
        'splatoon_title': 'splatoon3',
        'analyzer_version': result.version,
        'battle_frames': result.battle_frames,
        'battle_rule': result.battle_info.rule.name.lower(),
        'battle_stage': result.battle_info.stage.name.lower(),
        'battle_result': result.result_event.win_lose.name.lower(),
        'team_result_count': result.result_event.team_count,
        'enemy_result_count': result.result_event.enemy_count,
        'battle_date': result.battle_info.battle_date,
        'match_type': result.match_info.match_type.name.lower(),
        'match_rate': result.match_info.match_rate,
        'team': [_to_player_dict(p) for p in result.battle_info.team_players],
        'enemy': [_to_player_dict(p) for p in result.battle_info.enemy_players],
        'team_bukis': [_to_buki_dict(b) for b in result.battle_info.team_bukis],
        'enemy_bukis': [_to_buki_dict(b) for b in result.battle_info.enemy_bukis],
        'main_player_index': result.battle_info.main_player.lamp_ord,
        'team_color': _to_rgb_color(result.battle_info.team_color.color) if result.battle_info.team_color else None,
        'enemy_color': _to_rgb_color(result.battle_info.enemy_color.color) if result.battle_info.enemy_color else None,
        'kill_count': _kill_count(result.kill_events, result.battle_info.main_player.lamp_ord),
        'death_count': _death_count(result.death_events, result.battle_info.main_player.lamp_ord),
        'sp_count': _sp_count(result.special_weapon_events, result.battle_info.main_player.lamp_ord),
        'battle_open_event': { 'start_frame': result.battle_info.open_event.start_frame, 'end_frame': result.battle_info.open_event.end_frame } if result.battle_info.open_event else None,
        'battle_end_event': { 'start_frame': result.battle_info.end_event.start_frame, 'end_frame': result.battle_info.end_event.end_frame } if result.battle_info.end_event else None,
        'battle_result_event': { 'start_frame': result.result_event.start_frame, 'end_frame': result.result_event.end_frame } if result.result_event else None,
        'death_events': [_to_death_dict(e) for e in result.death_events],
        'kill_events': [_to_kill_dict(e) for e in result.kill_events],
        'player_number_balance_events': [_to_player_number_balance_dict(e) for e in result.player_number_balance_events],
        'special_weapon_events': [_to_sp_weapon_dict(e) for e in result.special_weapon_events],
        'team_count_events': [_to_battle_count_dict(evt) for evt in result.team_count_events],
        'enemy_count_events': [_to_battle_count_dict(evt) for evt in result.enemy_count_events],
        'ink_tank_states': [{ 'ink_level': f.main_player_ink.ink_level, 'frame': f.frame } for f in result.ink_tank_result.frames ]
    }

    api_gateway_url = f'{os.environ.get("AWS_BATTLE_ANALYZER_ENDPOINT")}/analysis_result'
    payload = {
        'method': 'create_result',
        'job_id': job_id,
        'user_id': user_id,
        'result': result_item
    }
    headers={
        'Content-Type': 'application/json',
        'X-Api-Key': os.environ.get('AWS_BATTLE_ANALYZER_API_KEY')
    }
    res = requests.post(api_gateway_url, json=payload, headers=headers)
    res_data = json.loads(res.text)
    if 'error' in res_data:
        raise Exception(res_data['error']['msg'])
    
def analyze(
    movie_path,
    process_id: int, 
    device: str,
    batch_size: int,
    user_id: str,
    job_id: str,
    file_name: str,
    battle_date: int,
    analysis_per_secode: int,
    err_code: Value):
    try:
        module_name = 'battle_analyzer'
        create_prod_logger(module_name)
        model_paths = get_model_paths()
        analyzer = BattleAnalyzer(model_paths=model_paths, device=device, log_name=module_name)
        preprocess_result = analyzer.preprocess(BattlePreprocessParams(
            battle_movie_path=movie_path,
            movie_date=battle_date,
            analysis_per_second=analysis_per_secode,
            process_id=process_id,
            batch_size=batch_size
        ))
        analysis_result, e_code = analyzer.analyze(BattleAnalysisParams())
        if analysis_result is None:
            err_code.value = e_code.value
            return
    except AnalyzerError as e:
        print(e.msg)
        err_code.value = e.code.value
        return
    except Exception as e:
        err_msg = f'failed to analyze: {str(e)}'
        print(err_msg)
        err_code.value = ErrorCode.INTERNAL_ERROR.value
        return
    
    while analysis_result:
        try:
            create_analzye_result(
                user_id=user_id,
                job_id=job_id,
                file_name=file_name,
                result=analysis_result,
                pre_result=preprocess_result)
        except Exception as e:
            err_msg = f'failed to save analyze result: {str(e)}'
            print(err_msg)
            err_code.value = ErrorCode.INTERNAL_ERROR.value
            return
        
        try:
            analysis_result, _ = analyzer.analyze(BattleAnalysisParams(
                start_frame=analysis_result.battle_info.battle_end_frame
            ))
        except AnalyzerError as e:
            err_msg = e.msg
            print(err_msg)
            err_code.value = e.code.value
            return
        except Exception as e:
            err_msg = f'failed to analyze: {str(e)}'
            print(err_msg)
            err_code.value = ErrorCode.INTERNAL_ERROR.value
            return

if __name__ == '__main__':
    sqs_client = boto3.client('sqs')
    s3_client = boto3.client('s3')
    dynamodb_client = boto3.client('dynamodb')
    
    logger = create_prod_logger('battle_analyzer')
    args = get_args()
    sqs_req_url = sqs_client.get_queue_url(QueueName=os.environ.get('AWS_SQS_QUEUE_URL_REQUEST'))['QueueUrl']
    sqs_cmd_url = sqs_client.get_queue_url(QueueName=os.environ.get('AWS_SQS_QUEUE_URL_COMMAND'))['QueueUrl']
    sqs_visibility_timeout = int(os.environ.get('AWS_SQS_VISIBILITY_TIMEOUT'))
    work_dir = os.environ.get('WORK_DIR')
    local_work_dir = os.environ.get('LOCAL_WORK_DIR')
    device = os.environ.get('MODEL_DEVICE')
    if args.device is not None:
        device = args.device
    logger.info(f'use device: {device}')
    logger.info(f'process id: {args.process}')

    if not os.path.exists(work_dir):
        logger.error('work dir not found')
        exit()

    init()

    shutdown_requested = False
    while not shutdown_requested:
        req, msg_handle = receive_message(
            sqs_client,
            sqs_req_url,
            sqs_cmd_url,
            sqs_visibility_timeout
        )

        # process commands with priority
        if req.type == 'shutdown':
            logger.info('shutdown requested')
            shutdown_requested = True
            break
        
        # ignore periods other than the period in charge
        if args.date_before and args.date_before < req.battle_date:
            logger.info(f'battle_date exceed date_before: {req.job_id}')
            continue
        if args.date_after and args.date_after > req.battle_date:
            logger.info(f'battle_date less than date_after: {req.job_id}')
            continue

        if req.type == 'analyze':
            logger.info(f'anlyze started. job id: {req.job_id}, user_id: {req.user_id}')
            
            sqs_client.delete_message(
                QueueUrl=req.sqs_url,
                ReceiptHandle=msg_handle
            )

            # validate job state
            job_item = get_job_item(dynamodb_client, req.job_id, req.user_id)
            if job_item is None:
                logger.info(f'job not exist: {req.job_id}')
                continue
            if job_item['job_state'] != 'movie_uploaded':
                logger.info(f'job state to ignore: {job_item["job_state"]}')
                continue

            # download battle movie file
            try:
                out_dir = f'{work_dir}/movies/{req.user_id}'
                local_out_dir = f'{local_work_dir}/movies/{req.user_id}' if local_work_dir else None
                if req.movie_source == 'user':
                    mov_path = download_user_movie_file(
                        s3_client=s3_client,
                        s3_bucket=req.s3_bucket,
                        s3_key=req.s3_key,
                        out_dir=out_dir,
                        local_dir=local_out_dir)
                elif req.movie_source == 'youtube':
                    mov_path = download_youtube_movie_file(video_id=req.video_id, out_dir=out_dir, local_dir=local_out_dir)
                else:
                    raise Exception('invalid source type')
            except Exception as e:
                msg = f'failed to download movie file: {str(e)}'
                logger.info(msg)
                set_fail_state(dynamodb_client, req.job_id, req.user_id, msg, 201)
                continue
            
            # set job state processing
            try:
                set_processing_state(dynamodb_client, req.job_id, req.user_id)
            except Exception as e:
                msg = f'failed to set processing state: {str(e)}'
                logger.info(msg)
                set_fail_state(dynamodb_client, req.job_id, req.user_id, msg, 201)
                continue

            # run analysis on dedicated process
            battle_date = int(job_item['battle_date'])
            batch_size = int(os.environ.get('ANALYSIS_PREPROCESS_BATCH_SIZE'))
            err_code = Value('i', -1)
            if req.movie_source == 'user':
                process = Process(
                    target=analyze,
                    args=[mov_path, args.process, device, batch_size, req.user_id, req.job_id, req.file_name, battle_date, 5, err_code]
                )
            elif req.movie_source == 'youtube':
                process = Process(
                    target=analyze,
                    args=[mov_path, args.process, device, batch_size, req.user_id, req.job_id, req.video_id, battle_date, 5, err_code]
                )
            else:
                continue
            
            process.start()
            process.join()

            if err_code.value != -1:
                set_fail_state(dynamodb_client, req.job_id, req.user_id, 'analysis failed', err_code.value)
                continue
            
            # set job state completed
            try:
                set_complete_state(dynamodb_client, req.job_id, req.user_id)
            except Exception as e:
                msg = f'failed to completed state: {str(e)}'
                logger.info(msg)
                set_fail_state(dynamodb_client, req.job_id, req.user_id, msg, 201)
                continue
            
            logger.info(f'anlyze completed. job id: {req.job_id}')
        else:
            logger.info(f'invalid request type: {req.type }')
            continue

    logger.info('battle analyzer exited.') 