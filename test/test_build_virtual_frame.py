from .base import TestCases
from src.kinematics import VirtualRootFrame
import numpy as np

class TestVirtualRootFrame(TestCases):
    def setup_method(self):
        self.landmarks = np.zeros((21, 3), dtype=float)
        self.landmarks[0] = [0.0, 0.0, 0.0]
        self.landmarks[5] = [1.0, 1.0, 0.0]
        self.landmarks[9] = [0.0, 2.0, 0.0]
        self.landmarks[17] = [-1.0, 1.0, 0.0]
        self.result = VirtualRootFrame(
            hands_cfg_path="src/kinematics/config/cfg.yaml"
        ).process(
            world_landmarks=self.landmarks
        )

    def _rotation_matrix_check(self):
        assert np.allclose(
          self.result["rotation_matrix"].T @ self.result["rotation_matrix"],
          np.eye(3),
          atol=1e-6
        ), "Result is not an orthonormal matrix"

        assert np.isclose(
            np.linalg.det(self.result['rotation_matrix']),
            1.0,
            atol=1e-6
        ), "Result is not a proper rotation matrix."
        
    def run(self):
        self._rotation_matrix_check()
        print("[PASSED] TestVirtualRootFrame")

    def test_run(self):
        self.run()