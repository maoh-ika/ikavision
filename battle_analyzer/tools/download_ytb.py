import os
import json
import requests
from datetime import datetime, timezone
from dateutil import tz
from pytube import YouTube
from pytube.cli import on_progress
from dotenv import load_dotenv
from googleapiclient.discovery import build
load_dotenv()

def to_jst_timestamp(iso8601: str) -> int:
    utc_datetime = datetime.strptime(iso8601, '%Y-%m-%dT%H:%M:%SZ')
    jst_timezone = tz.gettz('Asia/Tokyo')
    jst_datetime = utc_datetime.replace(tzinfo=timezone.utc).astimezone(jst_timezone)
    return int(jst_datetime.timestamp())

def to_timestamp(iso8601: str) -> int:
    utc_datetime = datetime.strptime(iso8601, '%Y-%m-%dT%H:%M:%SZ')
    return int(utc_datetime.timestamp())

def to_utc(ts: int) -> int:
    return ts - 60 * 60 * 9

def download(video_id: str, dst_dir: str, file_name: str=None, live_only: bool=False):
    video_url = f'https://www.youtube.com/watch?v={video_id}'
    yt = YouTube(video_url)
    if live_only and not yt.vid_info['videoDetails']['isLiveContent']:
        print(f'not live stream: {yt.title}_{video_id}')
        raise Exception('not live stream')

    yt.register_on_progress_callback(on_progress)
    stream = yt.streams.filter(res='720p').first()
    #stream = yt.streams.get_highest_resolution()
    if stream is None:
        raise Exception('available stream not found')

    if file_name is None: 
        file_name = f'{yt.title}_{video_id}.mp4'
    file_path = f'{dst_dir}/{file_name}'
    
    if os.path.exists(file_path):
        print(f'already exists: {file_name}')
    else:
        print(f'Downloading...: {file_name}')
        stream.download(output_path=dst_dir, filename=file_name, max_retries=3)

def _to_video_info(item):
    return {
        'id': item['id']['videoId'],
        'title': item['snippet']['title'],
        'channel_id': item['snippet']['channelId'],
        'channel_name': item['snippet']['channelTitle'],
        'published_at': to_jst_timestamp(item['snippet']['publishedAt']),
        'thumbnail_url': item['snippet']['thumbnails']['medium']['url']
    } 

def get_live_video_list(get_all: bool=False, max_results: int=50, published_after: int=None, published_before: int=None):
    api_key = os.environ.get('YOUTUBE_DATA_API_KEY')
    youtube = build('youtube', 'v3', developerKey=api_key)

    published_after_param = None
    if published_after is not None:
        published_after_utc = to_utc(published_after)
        published_after_param = datetime.fromtimestamp(published_after_utc).isoformat() + 'Z'
    
    published_before_param = None
    if published_before is not None:
        published_before_utc = to_utc(published_before)
        published_before_param = datetime.fromtimestamp(published_before_utc).isoformat() + 'Z'

    search_query = 'スプラトゥーン3 スプラトゥーン３ splatoon3 Splatoon3 SPLATOON3'
    next_token = None
    video_list = []
    while True:
        result = youtube.search().list(
            part='snippet',
            q=search_query,
            type='video',
            eventType='completed',
            order='date',
            regionCode='JP',
            publishedAfter=published_after_param,
            publishedBefore=published_before_param,
            maxResults=max_results,
            pageToken=next_token
        ).execute()
        
        videos = [_to_video_info(item) for item in result['items']]
        video_list += videos

        if not get_all or 'nextPageToken' not in result or result['nextPageToken'] == '':
            return video_list
        next_token = result['nextPageToken']

def get_list(channel_id: str, max_count: int=9999, cache_dir: str=None) -> list[dict]:
    if cache_dir is not None:
        cache_path = f'{cache_dir}/{channel_id}.json'
        if os.path.exists(cache_path):
            with open(cache_path) as f:
                return json.load(f)[:max_count]

    api_url = os.environ.get('YOUTUBE_API_END_POINT')
    api_key = os.environ.get('YOUTUBE_DATA_API_KEY')

    video_list = []
    next_token = None
    params = {
        'part': 'snippet',
        'channelId': channel_id,
        'maxResults': 1,
        'order': 'date',
        'key': api_key,
    }
    response = requests.get(api_url, params=params)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])
        videos = [_to_video_info(item) for item in items if item['id']['kind'] == 'youtube#video']
        video_list += videos
        if cache_dir is not None:
            with open(cache_path, 'w') as f:
                json.dump(video_list, f, indent=2)
        return video_list[:max_count]
    else:
        return None
        

if __name__ == '__main__':
    channel_id = 'EntD9axqHBA'
    out_dir = f'./temp/{channel_id}'
    
    video_id = '2sG1j_wkLds'
    download(video_id, out_dir)
    exit()
    
    #videos = get_list(channel_id, cache_dir=out_dir)[58:68]
    videos = get_list(channel_id, cache_dir=out_dir)
    for video in videos:
        video_id = video['id']
        download(video_id, out_dir, live_only=True)