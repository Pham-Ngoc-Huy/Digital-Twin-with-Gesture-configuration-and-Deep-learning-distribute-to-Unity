from .utils_base import Utils
import numpy as np
class CrossProduct(Utils):
    def __init__(
        self,
        v1: list,
        v2: list
    ):
        self.v1 = v1
        self.v2 = v2

    def process(self):        
        
        if len(self.v1) != 3 or len(self.v2) != 3:
            raise ValueError("Cross product requires two 3D vectors")
                
        v1 = np.array(self.v1, dtype=float)
        v2 = np.array(self.v2, dtype=float)

        x = v1[1]*v2[2] - v1[2]*v2[1]
        y = v1[2]*v2[0] - v1[0]*v2[2]
        z = v1[0]*v2[1] - v1[1]*v2[0]
        return [x, y, z] 