import cv2
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from stream.state import State

class PlayerBalanceWindow:
    def __init__(self, width: int, height: int, opacity: float, show_frames: int=None) -> None:
        self.width = width
        self.height = height
        self.opacity = opacity
        self.show_frames = show_frames
        self.last_frame = 0
        self.window = np.zeros((height, width, 3), dtype=np.uint8)

    def draw(self, state: State):
        dif = 0
        if state.number_balance_event: 
            dif = state.number_balance_event.team_number - state.number_balance_event.enemy_number
        cv2.imshow('Alive players', self.make_content(dif))

    def make_rect_color(self, dif: int):
        if dif == 0:
            return (139, 125, 96)
        elif dif == 1:
            return (255, 177, 130)
        elif dif == 2:
            return (255, 98, 41)
        elif dif == 3:
            return (83, 200, 0) 
        elif dif == 4:
            return (32, 94, 27)
        elif dif == -1:
            return (0, 171, 255)
        elif dif == -2:
            return (0, 81, 230)
        elif dif == -3:
            return (98, 17, 197) 
        elif dif == -4:
            return (0, 0, 213)
        
    def make_text(self, dif: int) -> str:
        if dif > 0:
            text = f'+{dif}'
        elif dif < 0:
            text = str(dif)
        else:
            text = f'±{dif}'

        if dif == 1:
            desc = 'いいよ！'
        elif dif == 2:
            desc = '強気で！'
        elif dif == 3:
            desc = '詰めて!!'
        elif dif == 4:
            desc = 'GOGOGOGO!!!'
        elif dif == -1:
            desc = '油断しないで!'
        elif dif == -2:
            desc = '危ないよ!'
        elif dif == -3:
            desc = '今すぐ下がって!!'
        elif dif == -4:
            desc = 'どんまい'
        else:
            desc = ''

        return f'{text} {desc}'
    
    def make_content(self, dif: int) -> np.ndarray:
        bg_color = self.make_rect_color(dif)
        text = self.make_text(dif)
        font_size = 28
        font_color = (255, 255, 255)
        font_path = 'C:\\Windows\\Fonts\\YuGothB.ttc'
        image = Image.new('RGB', (self.width, self.height), bg_color)
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype(font_path, font_size)
        text_width, text_height = draw.textsize(text, font=font)
        text_position = ((self.width - text_width) // 2, (self.height - text_height) // 2)
        draw.text(text_position, text, font=font, fill=font_color)
        return np.array(image)
