import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from stream.state import State

# 人数有利・不利状況をウィンドウに表示する
class PlayerBalanceWindow:
    def __init__(self,
        width: int, # ウィンドウ幅
        height: int, # ウィンドウ高さ
        opacity: int, # ウィンドウ透過率
        font_size: int=28, # テキスト表示用フォントサイズ
        font_path: str=None, # テキスト表示用フォントへのパス, TrueTypeフォントのみ
        show_frames: int=None # ウィンドウを表示するフレーム数
    ) -> None:
        self.width = width
        self.height = height
        self.opacity = opacity
        self.font_paht = font_path
        self.show_frames = show_frames
        self.last_frame = 0
        self.window = np.zeros((height, width, 3), dtype=np.uint8)

    def draw(self, state: State):
        diff = 0 # 敵チームとの人数差
        if state.number_balance_event:
            diff = state.number_balance_event.team_number - state.number_balance_event.enemy_number
        content = self.make_content(diff)
        cv2.imshow('PlayerBalanece', content)

    def make_content(self, diff: int) -> np.ndarray:
        # 人数状況に応じた背景色を生成
        bg_color = self.make_color(diff)
        # 人数状況に応じたテキストを生成
        text = self.make_text(diff)
        font_size = 28
        font_color = (255, 255, 255)
        image = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(self.font_paht, font_size)
        # テキストをセンターに描画
        text_width, text_height = draw.textsize(text, font=font)
        text_pos = ((self.width - text_width) // 2, (self.height - text_height) // 2)
        draw.text(text_pos, text, font=font, fill=font_color)
        return np.array(image)
    
    def make_color(self, diff: int):
        if diff == 0:
            return (139, 125, 96)
        elif diff == 1:
            return (255, 177, 130)
        elif diff == 2:
            return (255, 98, 41)
        elif diff == 3:
            return (83, 200, 0)
        elif diff == 4:
            return (32, 94, 27)
        elif diff == -1:
            return (0, 171, 255)
        elif diff == -2:
            return (0, 81, 230)
        elif diff == -3:
            return (98, 17, 197)
        elif diff == -4:
            return (0, 0, 213)

    def make_text(self, diff: int):
        if diff > 0:
            num = f'+{diff}'
        elif diff < 0:
            num = str(diff)
        elif diff == 0:
            num = f'±{diff}'
        else:
            num = ''

        if diff == 1:
            desc = 'いいよ！'
        elif diff == 2:
            desc = '強気で！'
        elif diff == 3:
            desc = '詰めて！'
        elif diff == 4:
            desc = 'GOGOGOGO!!'
        elif diff == -1:
            desc = '油断しないで！'
        elif diff == -2:
            desc = '危ないよ！'
        elif diff == -3:
            desc = '今すぐ下がって！！'
        elif diff == -4:
            desc = 'どんまい'
        else:
            desc = ''

        return f'{num} {desc}'