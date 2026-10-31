from .base import Kinematics
from src.utils import (
    CrossProduct, 
    Normalize,
    Projection,
)
import numpy as np

class LocalFrameBuilder(Kinematics):
    
    @staticmethod
    def _rotation_matrix_test(
        vec: np.ndarray
    ) -> bool:
        identity_matrix = np.eye(vec.shape[0])
        R = np.asarray(vec, dtype=float)

        if R.shape != (3, 3):
            raise ValueError("Rotation matrix must have shape (3, 3).")

        if not np.all(np.isfinite(R)):
            raise ValueError("Rotation matrix must contain finite values.")
    
        if not np.allclose(vec.T @ vec, identity_matrix, atol=1e-9):
            raise ValueError("R is not an orthogonal matrix.")

        if not np.isclose(np.linalg.det(vec), 1.0, atol=1e-9):
            raise ValueError("R is not a proper rotation matrix")
    
        return True
    
    def process(
        self
    ) -> np.ndarray:
        """
        Build the local frame based on the base_vec and ref_vec
        where each axis is each columns in final matrix R return

        for example:
            R = [x_axis, y_axis, z_axis]
        """
        # Create x_hat
        x_hat = Normalize(self.base_vec).process()
        # Create y_hat using Gram-Schmidt process
        y_hat = Projection(x_hat, self.ref_vec).process()
        # Create z_hat as the cross product of x_hat and y_hat
        z_hat = CrossProduct(x_hat, y_hat).process()
        # Create R matrix
        R = np.array([x_hat, y_hat, z_hat]).T

        self._rotation_matrix_test(vec=R)
        return R


