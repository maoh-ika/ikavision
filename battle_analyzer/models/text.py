from dataclasses import dataclass
from enum import Enum
from models.detected_item import DetectedItem

class CharType(Enum):
    HIRAGANA = 0
    KATAKANA = 1
    NUMBER = 2
    ALPHABET = 3
    SYMBOL = 4
    GREEK = 5
    RUSIAN = 6
    DIACRITICAL = 7

@dataclass
class Char(DetectedItem):
    value: str
    type: CharType

    @classmethod
    def from_json(cls, j):
        return cls(
            value=j['value'],
            type=CharType(j['type']),
            xyxy=j['xyxy'],
            conf=j['conf'],
            cls=j['cls']
         )

@dataclass
class Text(DetectedItem):
    value: [Char]

    @property
    def text(self):
        return to_str(self.value)
    
    @property
    def rect(self):
        if len(self.value) == 0:
            return [0, 0, 0, 0]
        return [
            self.value[0].xyxy[0],
            self.value[0].xyxy[1],
            self.value[-1].xyxy[2],
            self.value[-1].xyxy[3]]
    
    @classmethod
    def from_json(cls, j):
        return cls(
            value=[Char.from_json(b) for b in j['value']],
            xyxy=j['xyxy'],
            conf=j['conf'],
            cls=j['cls']
        )
    
    def concat(self, text):
        self.value += text.value
        if self.xyxy[0] > text.xyxy[0]:
            self.xyxy[0] = text.xyxy[0]
        if self.xyxy[1] > text.xyxy[1]:
            self.xyxy[1] = text.xyxy[1]
        if self.xyxy[2] < text.xyxy[2]:
            self.xyxy[2] = text.xyxy[2]
        if self.xyxy[3] < text.xyxy[3]:
            self.xyxy[3] = text.xyxy[3]
        self.conf = (self.conf + text.conf) / 2
    
def to_str(chars: list[Char]) -> str:
    return ''.join(list(map(lambda v: v.value, chars)))

def likely_text(str_list: list[str]) -> str:
    if len(str_list) == 0:
        return ''
    len_count = {}
    for s in str_list:
        l = len(s)
        if l not in len_count:
            len_count[l] = 1
        else:
            len_count[l] += 1
    len_count = list(sorted(len_count.items(), key=lambda x: x[1], reverse=True))
    likely_count = len_count[0][0]
    str_list = list(filter(lambda s: len(s) == likely_count, str_list))
    likely_text = ''
    for i in range(likely_count):
        cahrs = map(lambda s: s[i], str_list)
        char_count = {}
        for c in cahrs:
            if c not in char_count:
                char_count[c] = 1
            else:
                char_count[c] += 1
        char_count = list(sorted(char_count.items(), key=lambda x: x[1], reverse=True))
        likely_text += char_count[0][0] 
    
    return likely_text
