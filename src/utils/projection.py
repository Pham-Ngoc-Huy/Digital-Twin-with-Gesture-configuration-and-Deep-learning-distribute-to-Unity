from .utils_base import Utils
import numpy as np

class Projection(Utils):
    """
    `Projection` means "Ma trận chiếu" in Vietnamese.
    definition:
        - it was a "square matrix" - and it has "idempotent" property (tính chất luỹ đẳng) [P^2 = P]
        - it transform a vector into a subspace (chuyển một vector thành 1 hình chiếu vuông góc vào một không gian con)
    """
    def __init__(
        self,
        base_vec: list,
        ref_vec: list
    ):
        self.base_vec = np.array(base_vec, dtype=float)
        self.ref_vec = np.array(ref_vec, dtype=float)

    def _base_vec_check(
        self
    ) -> bool:
        """
        Check the base-vector that is [0,0,0] or not -- else it will return None
        """
        if np.allclose(self.base_vec, [0,0,0], atol=1e-9):
            raise ValueError("Base Vector must not be [0,0,0].")

        return True

    def _size_check(
        self
    ) -> bool:
        """
        Check the size of the vectors
        """
        if len(self.base_vec) != len(self.ref_vec):
            raise ValueError("Vectors must have the same length.")

        return True

    def _orthogonal_check(
        self,
        vec: list,
    ) -> bool:
        """
        Check the orthogonal or not
        """
        result = np.dot(self.base_vec, vec)
        if not np.isclose(result, 0.0, atol=1e-9):
            raise ValueError("Vectors are not orthogonal.")
        print("Vectors are orthogonal.")
        return True

    def _projection_calculation(
        self
    ):
        """
        Calculate the projection of ref_vec onto base_vec
        """
        projection = (np.dot(self.ref_vec, self.base_vec) / np.dot(self.base_vec, self.base_vec)) * self.base_vec
        print("Projection of ref_vec onto base_vec: ", projection)
        return projection

    def _Gram_Schmidt_calculation(
        self
    ):
        """
        Calculate the projection of ref_vec onto base_vec
        base on Gram-Schmidt process, the projection of a vector v onto a vector u is given by:
            ```
            result =  v - proj_u(v)
            orthogonal-unit-vector = result / ||result||
            ```
        """
        projection = self._projection_calculation()
        projection_result = self.ref_vec - projection

        # handle case projection_result = [0,0,0] --> `suy bien` cases 
        # in matrix -- `singular`
        # in robotics -- `degenerated`

        if np.allclose(projection_result, [0,0,0], atol=1e-9):
            raise ValueError ("The projection result is DEGENERATED!")
         
        orthogonal_unit_vector = projection_result / np.linalg.norm(projection_result)
        print("Result of ref_vec - projection: ", projection_result)
        print("orthogonal-unit-vector: ", orthogonal_unit_vector)
        return orthogonal_unit_vector

    def process(self) -> np.ndarray:
        """
        Calculation of the projection of vectors and orthogonal check.
        """
        if self._base_vec_check():
            if self._size_check():
                orthogonal_unit_vector = self._Gram_Schmidt_calculation()
                print(orthogonal_unit_vector)
                if self._orthogonal_check(vec=orthogonal_unit_vector):
                    return orthogonal_unit_vector