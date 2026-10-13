from abc import ABC, abstractmethod
from utils import (
    CrossProduct, 
    Normalize,
    Projection,
)
from typing import List

# receive `base_vec` and `ref_vec`
# create `x_hat`
# using Gram-Schmidt process to create `y_hat`
# create `z_hat`
# create `R` matrix
# return the result


class LocalFrameBuilder(ABC):
    def __init__(
        self,
        base_vec: list,
        ref_vec: list
    ):
        self.base_vec = base_vec
        self.ref_vec = ref_vec

    def process(
        self
    ) -> List[List[float]]:
        """
        Build the local frame based on the base_vec and ref_vec
        """
        # Create x_hat
        x_hat = Normalize(self.base_vec).process()
        # Create y_hat using Gram-Schmidt process
        y_hat = Projection(self.base_vec, self.ref_vec).process()
        # Create z_hat as the cross product of x_hat and y_hat
        z_hat = CrossProduct(x_hat, y_hat).process()
        # Create R matrix
        R = [x_hat, y_hat, z_hat]
        return R


