import time
from multiprocessing import shared_memory, Event, Process, Value
import cv2
import numpy as np
from shared_image import SharedImage, ImageShape

#def get_args():
#    parser = argparse.ArgumentParser()
#    parser.add_argument('-v', '--video', nargs='?', type=str, action='store', default=None)

#    parser.add_argument('-u', '--user_id', nargs='?', type=str, action='store', default=None)
#    parser.add_argument('-b', '--bot_id', nargs='?', action='store', type=str, default=None)
#    parser.add_argument('-l', '--buy_amount_limit', type=float, action='store', default=100000)
#    parser.add_argument('--currency_pair', action='store', type=str, default='')
#    parser.add_argument('--exchange_id', action='store', type=str, default='')
#    parser.add_argument('--demo', action='store_true')
#    parser.add_argument('--debug', action='store_true')
#    parser.add_argument('-s', '--demo_settle_amount', nargs='?', type=float, action='store')
#    parser.add_argument('-t', '--demo_trade_amount', nargs='?', type=float, action='store')
#    parser.add_argument('-f', '--setting_file', type=str, action='store', default=None)
#    parser.add_argument('-j', '--trading_rule_json', nargs='?', type=str, action='store', default=None)
#    parser.add_argument('-p', '--trading_rule_file', nargs='?', type=str, action='store', default=None)
#    return parser.parse_args()

class SharedPlayCaptureImage(SharedImage):
    SHM_NAME = 'play_capture'

    def __init__(self, shape: ImageShape) -> None:
        super().__init__(SharedPlayCaptureImage.SHM_NAME, shape)
    
    @classmethod
    def clear(cls, shape: ImageShape): 
        SharedImage.create(SharedPlayCaptureImage.SHM_NAME, shape)
    
    @classmethod
    def clear(cls): 
        SharedImage.clear(SharedPlayCaptureImage.SHM_NAME)
    
    @classmethod
    def reset(cls, shape: ImageShape): 
        SharedImage.reset(SharedPlayCaptureImage.SHM_NAME, shape)

def run_play_capture(
    play_image_updated: Event,
    shutdown_requested: Value,
    src: str=None,
    width: int=1280,
    height: int=720,
    channels: int=3):
    
    cap = cv2.VideoCapture(0 if src is None else src)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    image_writer = SharedPlayCaptureImage(ImageShape(height, width, channels))

    while shutdown_requested:
        play_image_updated.clear()
        success, img = image_writer.write(cap)
        if not success:
            time.sleep(0.2)
            continue
        play_image_updated.set()
        print('[PLAY] image send')
        time.sleep(0.033)
    print('################# END #############')
