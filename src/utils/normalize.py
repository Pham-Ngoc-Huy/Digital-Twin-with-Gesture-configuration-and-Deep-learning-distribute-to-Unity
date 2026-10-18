from .utils_base import Utils 
import numpy as np

class Normalize(Utils):
    def __init__(
        self,
        v: list
    ):
        self.v = v

    def process(self) -> tuple:
        v = np.array(self.v, dtype=float)
        v_norm = np.linalg.norm(v)
        return v / v_norm

