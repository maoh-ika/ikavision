from dataclasses import dataclass
import numpy as np

@dataclass
class Frame:
    frame: int
    image: np.ndarray
