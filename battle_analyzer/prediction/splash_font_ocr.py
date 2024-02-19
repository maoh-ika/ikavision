import torch
import numpy as np
from ultralytics import YOLO
from prediction.prediction_process import preprocess, postprocess
from prediction.cls_to_char import hiragana_map, katakana_map, number_map, alphabet_map, symbol_map, greek_map, rusian_map, diacritical_map
from models.text import Char, CharType
from models.detected_item import DetectedItem

class SplashFontOCR:
    def __init__(self,
        char_type_model_path: str,
        hiragana_model_path: str,
        katakana_model_path: str,
        number_model_path: str,
        alphabet_model_path: str,
        symbol_model_path: str,
        char_model_path: str,
        device: str
        ) -> None:
        dev = torch.device(device)
        self.char_type_model = YOLO(char_type_model_path)
        self.char_type_model.to(dev)
        self.hiragana_model = YOLO(hiragana_model_path)
        self.hiragana_model.to(dev)
        self.katakana_model = YOLO(katakana_model_path)
        self.katakana_model.to(dev)
        self.number_model = YOLO(number_model_path)
        self.number_model.to(dev)
        self.alphabet_model = YOLO(alphabet_model_path)
        self.alphabet_model.to(dev)
        self.symbol_model = YOLO(symbol_model_path)
        self.symbol_model.to(dev)
        self.char_model = YOLO(char_model_path)
        self.char_model.to(dev)

    def get_text(self, img: np.ndarray, line_break: bool=False) -> list[Char]:
        char_items = self._detect_chars(img)
        chars = self._classify(img, char_items)
        return self._line_break(chars) if line_break else chars
    
    def get_hiragara_text(self, img: np.ndarray, line_break: bool=False) -> list[Char]:
        char_items = self._detect_chars(img)
        chars = self._classify_char(img, char_items, CharType.HIRAGANA, self.hiragana_model, hiragana_map)
        return self._line_break(chars) if line_break else chars
    
    def get_katakana_text(self, img: np.ndarray, line_break: bool=False) -> list[Char]:
        char_items = self._detect_chars(img)
        chars = self._classify_char(img, char_items, CharType.KATAKANA, self.katakana_model, katakana_map)
        return self._line_break(chars) if line_break else chars
    
    def get_number_text(self, img: np.ndarray, line_break: bool=False) -> list[Char]:
        char_items = self._detect_chars(img)
        chars = self._classify_char(img, char_items, CharType.NUMBER, self.number_model, number_map)
        return self._line_break(chars) if line_break else chars
    
    def get_alphabet_text(self, img: np.ndarray, line_break: bool=False) -> list[Char]:
        char_items = self._detect_chars(img)
        chars = self._classify_char(img, char_items, CharType.ALPHABET, self.alphabet_model, alphabet_map)
        return self._line_break(chars) if line_break else chars

    def get_symbol_text(self, img: np.ndarray, line_break: bool=False) -> list[Char]:
        char_items = self._detect_chars(img)
        chars = self._classify_char(img, char_items, CharType.SYMBOL, self.symbol_model, symbol_map)
        return self._line_break(chars) if line_break else chars
    
    def _detect_chars(self, img) -> list[DetectedItem]:
        input = preprocess(img, self.char_type_model.overrides['imgsz'], self.char_type_model.device)
        preds = self.char_type_model.model(input)
        preds = postprocess(preds, input.shape[2:], img.shape, 0.25, 0.1, 1000)
        chars = []
        for *xyxy, conf, cls in preds[0]:
            x1 = int(xyxy[0].cpu().numpy().astype('uint'))
            y1 = int(xyxy[1].cpu().numpy().astype('uint'))
            x2 = int(xyxy[2].cpu().numpy().astype('uint'))
            y2 = int(xyxy[3].cpu().numpy().astype('uint'))
            conf = float(conf.cpu().numpy().astype('float'))
            cls = int(cls.cpu().numpy().astype('uint'))
            chars.append(DetectedItem(
                [x1, y1, x2, y2],
                conf,
                cls
            ))
        chars = sorted(chars, key=lambda c: c.xyxy[0])
        return chars
    
    def _classify_char(self, img: np.ndarray, char_items: list[DetectedItem], char_type: CharType, model: YOLO, cls_to_char: dict) -> list[Char]:
        if model is None:
            raise Exception('char model not loaded')

        char_items = list(filter(lambda i: i.xyxy[0] < i.xyxy[2] and i.xyxy[1] < i.xyxy[3], char_items))
        char_imgs =[img[item.xyxy[1]:item.xyxy[3],item.xyxy[0]:item.xyxy[2]] for item in char_items]
        if len(char_imgs) == 0:
            return []
        
        preds = model.predict(char_imgs, verbose=False)
        chars = []
        for idx, pred in enumerate(preds):
            char_cls = pred.names[pred.probs.top1]
            char_val = cls_to_char[char_cls]
            char = Char(value=char_val, type=char_type, xyxy=char_items[idx].xyxy, conf=pred.probs.top1conf, cls=char_items[idx].cls)
            chars.append(char)
        return chars
    
    def _classify(self, img: np.ndarray, char_items: list[DetectedItem]) -> list[Char]:
        char_items = list(filter(lambda i: i.xyxy[0] < i.xyxy[2] and i.xyxy[1] < i.xyxy[3], char_items))
        char_imgs =[img[item.xyxy[1]:item.xyxy[3],item.xyxy[0]:item.xyxy[2]] for item in char_items]
        if len(char_imgs) == 0:
            return []
        
        preds = self.char_model.predict(char_imgs, verbose=False)
        chars = []
        for idx, pred in enumerate(preds):
            char_cls = pred.names[pred.probs.top1]
            if char_cls in hiragana_map:
                ct = CharType.HIRAGANA
                val = hiragana_map[char_cls]
            elif char_cls in katakana_map:
                ct = CharType.KATAKANA
                val = katakana_map[char_cls]
            elif char_cls in alphabet_map:
                ct = CharType.ALPHABET
                val = alphabet_map[char_cls]
            elif char_cls in number_map:
                ct = CharType.NUMBER
                val = number_map[char_cls]
            elif char_cls in symbol_map:
                ct = CharType.SYMBOL
                val = symbol_map[char_cls]
            elif char_cls in greek_map:
                ct = CharType.GREEK
                val = greek_map[char_cls]
            elif char_cls in rusian_map:
                ct = CharType.RUSIAN
                val = rusian_map[char_cls]
            elif char_cls in diacritical_map:
                ct = CharType.DIACRITICAL
                val = diacritical_map[char_cls]
            else:
                return None
            
            char = Char(value=val, type=ct, xyxy=char_items[idx].xyxy, conf=pred.probs.top1conf, cls=char_items[idx].cls)
            chars.append(char)

        return chars
    
    def _line_break(self, chars: list[Char]) -> list[list[Char]]:
        if len(chars) == 0:
            return []
        first_char = chars[0]
        lines = [{
            'top': first_char.xyxy[1],
            'bottom': first_char.xyxy[3],
            'chars': [first_char]
        }]
        for char in chars[1:]:
            center_y = (char.xyxy[1] + char.xyxy[3]) / 2
            new_line = True
            for line in lines:
                if line['top'] <= center_y and center_y <= line['bottom']:
                    line['chars'].append(char)
                    new_line = False
                    break
            if new_line:
                lines.append({
                    'top': char.xyxy[1],
                    'bottom': char.xyxy[3],
                    'chars': [char]
                })

        lines.sort(key=lambda l: l['top'])
        return [line['chars'] for line in lines]

