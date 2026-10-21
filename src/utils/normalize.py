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

        if v.ndim != 1 or v.size != 3:
            raise ValueError("Expect a 3D vector.")

        if not np.all(np.isfinite(v)):
            raise ValueError("Vector must contain finite value.")

        v_norm = np.linalg.norm(v)

        if np.isclose(v_norm, 0,0, atol=1e-9):
            raise ValueError("Cannot normalize a zero vector.")
        return v / v_norm

