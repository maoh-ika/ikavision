import time
import argparse
import json
import os
import re
import concurrent.futures
from time import sleep
from log import create_file_logger
from tools.download_ytb import get_live_video_list
from timestamp import timestamp, from_days, from_hours, to_string, to_timestamp
from run_youtube import put_analysis_request, is_job_exists
from run_worker import download_youtube_movie_file

logger = create_file_logger('run_youtube_monitor.log')

def filter_video(videos: list[dict]) -> list[dict]:
    ng_words = ['サーモンラン', 'さーもんらん', 'サモラン', 'さもらん', 'シャケ', '鮭', 'バイト', 'プラベ', 'プライベート', 'ナワバトラ', 'ヒーローモード']
    pattern = re.compile('|'.join(re.escape(keyword) for keyword in ng_words))
    return list(filter(lambda v: len(pattern.findall(v['title'])) == 0, videos))

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--user_id', type=str)
    parser.add_argument('--once', action='store_true')
    parser.add_argument('--reverse', action='store_true')
    parser.add_argument('--retry', action='store_true')
    parser.add_argument('--retry_all', action='store_true')
    parser.add_argument('--after', type=str)
    parser.add_argument('--before', type=str)
    parser.add_argument('--max_workers', type=int, default=1)
    parser.add_argument('--max_videos', type=int, default=5)
    return parser.parse_args()

def download(video_id: str, out_dir: str):
    try:
        download_youtube_movie_file(video_id, out_dir)
    except Exception as e:
        raise Exception(f'{video_id}: {str(e)}')
    return video_id

def download_pallarel(user_id: str, videos: list[dict], workers: int, max_videos: int=None):
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futures = []
        for video in videos:
            if is_job_exists(user_id, video['id']):
                logger.info(f'job alread exists. skip: {video["title"]} ({video["id"]})')
                continue
            futures.append(executor.submit(download, video['id'], save_dir))
            if max_videos is not None and len(futures) >= max_videos:
                break

        for future in concurrent.futures.as_completed(futures):
            try:
                video_id = future.result()
                video = list(filter(lambda v: v['id'] == video_id, videos))[0]
                logger.info(f'send analysis request. id: {video_id}, title: {video["title"]}, publisehd: {to_string(video["published_at"] * 1000)}')
                put_analysis_request(user_id, video)
            except Exception as e:
                logger.error(str(e))

def retry(user_id: str, save_dir: str, workers: int, after: int=None, before: int=None, max_videos: int=False):
    logger.info(f'user_id: {user_id}')
    logger.info(f'save_dir: {save_dir}')
    cache_path = f'{save_dir}/last_live_videos.json'
    if not os.path.exists(cache_path):
        logger.info('save_dir not found')
        return
    
    if after is None:
        after = 0
    if before is None:
        before = timestamp() // 1000
    
    logger.info(f'after: {to_string(after * 1000)}')
    logger.info(f'before: {to_string(before * 1000)}')
    
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            prev_videos_list = json.load(f)
            for videos in prev_videos_list:
                videos = list(filter(lambda v: after <= v['published_at'] and v['published_at'] <= before, videos))
                download_pallarel(user_id, videos, workers, max_videos)

def run_job(user_id: str, save_dir: str, workers: int, after: int=None, before: int=None, reverse: bool=None, retry: bool=False, max_videos: int=False):
    logger.info('fetch new live videos')
    logger.info(f'user_id: {user_id}')
    logger.info(f'save_dir: {save_dir}')
    os.makedirs(save_dir, exist_ok=True)
    cache_path = f'{save_dir}/last_live_videos.json'
    if not os.path.exists(cache_path):
        with open(cache_path, 'w') as f:
            json.dump([], f)
        
    published_after = after
    published_before = before
    prev_videos = []
    if os.path.exists(cache_path):
        with open(cache_path) as f:
            prev_videos_list = json.load(f)
            if len(prev_videos_list) > 0:
                if reverse:
                    prev_videos = prev_videos_list[0]
                else:
                    prev_videos = prev_videos_list[-1]
                prev_videos.sort(key=lambda v: v['published_at'])
                if reverse and published_before is None:
                    published_before = prev_videos[0]['published_at'] - 1
                elif not reverse and published_after is None:
                    published_after = prev_videos[-1]['published_at'] + 1
                prev_videos = list(filter(lambda v: v['id'] != '__dummy__', prev_videos))

    if retry and len(prev_videos) > 0:
        logger.info('retry if there are aborted videos')
        logger.info(f'max {max_videos} processed')
        download_pallarel(user_id, prev_videos, workers, max_videos)

    now = timestamp() // 1000
    if reverse:
        if published_before is None:
            published_before = now
        if published_after is None:
            published_after = published_before - from_hours(4) // 1000
    else:
        if published_after is None:
            published_after = (timestamp() - from_days(1)) // 1000
        if published_before is None:
            published_before = published_after + from_hours(4) // 1000
            if published_before > now:
                published_before = now
    
    logger.info(f'publish_after: {to_string(published_after * 1000)}')
    logger.info(f'publish_brfore: {to_string(published_before * 1000)}')

    try:
        new_videos = get_live_video_list(get_all=True, max_results=50, published_after=published_after, published_before=published_before)
        new_videos = filter_video(new_videos)
        if len(new_videos) == 0:
            logger.info('no video found. exit.')
            with open(cache_path, 'r') as f:
                videos_list = json.load(f)
                if reverse:
                    videos_list.append([{'published_at': published_after, 'id': '__dummy__'}])
                else:
                    videos_list.append([{'published_at': published_before, 'id': '__dummy__'}])
                videos_list.sort(key=lambda v: v[0]['published_at'])
            with open(cache_path, 'w') as f:
                json.dump(videos_list, f, indent=2)
            return True
        
        with open(cache_path, 'r') as f:
            videos_list = json.load(f)
            new_videos.sort(key=lambda v: v['published_at'])
            videos_list.append(new_videos)
            videos_list.sort(key=lambda v: v[0]['published_at'])
        with open(cache_path, 'w') as f:
            json.dump(videos_list, f, indent=2)
    except Exception as e:
        logger.error(str(e))
        return False
    
    logger.info(f'found {len(new_videos)} new videos')
    logger.info(f'max {max_videos} processed')

    download_pallarel(user_id, new_videos, workers, max_videos)
    
    logger.info('send analisis requests completed. sleep until next run')
    return True

if __name__ == '__main__':
    args = get_args()
    save_dir = f'{os.environ.get("WORK_DIR")}/movies/{args.user_id}'
    after = to_timestamp(args.after) // 1000 if args.after else None
    before = to_timestamp(args.before) // 1000 if args.before else None
    if args.once:
        print('run once')
        run_job(args.user_id, save_dir, args.max_workers, after, before, args.reverse, args.retry, args.max_videos)
    elif args.retry_all:
        print('retry all')
        retry(args.user_id, save_dir, args.max_workers, after, before, args.max_videos)
    else:
        interval = 60 * 60 * 4
        while True:
            before = time.time()
            api_success = run_job(args.user_id, save_dir, args.max_workers, None, None, args.reverse, args.retry, args.max_videos)
            if not api_success:
                print('wait for refiling api quota')
                time.sleep(interval)
            else:
                sleep_seconds = interval - (time.time() - before)
                if sleep_seconds < 0:
                    sleep_seconds = 0
                print(f'sleep {sleep_seconds} seconds')
                time.sleep(sleep_seconds)
                