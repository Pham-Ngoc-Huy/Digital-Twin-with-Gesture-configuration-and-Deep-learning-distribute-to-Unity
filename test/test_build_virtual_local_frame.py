import numpy as np
import pytest

from src.process import VirtualLocalFrame

from .base import TestCases


class TestVirtualLocalFrame(TestCases):
    def setup_method(self):
        super().setup_method()

        self.local_frame = VirtualLocalFrame(hands_cfg_path=self.hands_cfg_path)

    def valid_landmarks(self):
        """
        Synthetic hand landmarks.
        Shape: (21, 3)

        Each finger has non-collinear segments
        to avoid degenerate local coordinate frames.
        """
        points = np.zeros((21, 3), dtype=float)

        # Wrist
        points[0] = [0.0, 0.0, 0.0]

        # Thumb
        points[1] = [-0.2, 0.1, 0.0]
        points[2] = [-0.4, 0.2, 0.0]
        points[3] = [-0.5, 0.4, 0.1]
        points[4] = [-0.6, 0.5, 0.2]

        # Index
        points[5] = [0.1, 0.2, 0.0]
        points[6] = [0.1, 0.4, 0.0]
        points[7] = [0.2, 0.6, 0.1]
        points[8] = [0.3, 0.8, 0.2]

        # Middle
        points[9] = [0.0, 0.2, 0.0]
        points[10] = [0.0, 0.5, 0.0]
        points[11] = [0.1, 0.7, 0.1]
        points[12] = [0.2, 0.9, 0.2]

        # Ring
        points[13] = [-0.1, 0.2, 0.0]
        points[14] = [-0.1, 0.4, 0.0]
        points[15] = [-0.2, 0.6, 0.1]
        points[16] = [-0.3, 0.8, 0.2]

        # Pinky
        points[17] = [-0.2, 0.15, 0.0]
        points[18] = [-0.3, 0.35, 0.0]
        points[19] = [-0.4, 0.5, 0.1]
        points[20] = [-0.5, 0.65, 0.2]

        return points

    def test_valid_input_shape(self, valid_landmarks):
        points = self.local_frame._get_points(valid_landmarks)

        assert points.shape == (21, 3)
        assert np.isfinite(points).all()

    def test_invalid_input_shape(self):
        points = np.zeros((20, 3))

        with pytest.raises(ValueError):
            self.local_frame._get_points(points)

    def test_nan_input(self):
        points = np.random.rand(21, 3)
        points[5, 0] = np.nan

        with pytest.raises(ValueError):
            self.local_frame._get_points(points)

    def test_infinite_input(self):
        points = np.random.rand(21, 3)
        points[5, 0] = np.inf

        with pytest.raises(ValueError):
            self.local_frame._get_points(points)

    def test_finger_geometry(self, valid_landmarks):
        points = self.local_frame._get_points(valid_landmarks)

        finger_points = self.local_frame._get_finger_points(
            points,
            self.local_frame.finger_indices["index"],
        )

        geometry = self.local_frame._compute_finger_geometry(finger_points)

        assert geometry["proximal_vector"]["is_valid"]
        assert geometry["intermediate_vector"]["is_valid"]
        assert geometry["distal_vector"]["is_valid"]

    def test_local_frames_are_valid_rotations(self, valid_landmarks):
        points = self.local_frame._get_points(valid_landmarks)

        finger_points = self.local_frame._get_finger_points(
            points,
            self.local_frame.finger_indices["index"],
        )

        geometry = self.local_frame._compute_finger_geometry(finger_points)

        proximal = self.local_frame._compute_proximal_frame(geometry)

        assert proximal["is_valid"]

        R = proximal["rotation_matrix"]

        assert np.allclose(
            R.T @ R,
            np.eye(3),
            atol=1e-6,
        )

        assert np.isclose(
            np.linalg.det(R),
            1.0,
            atol=1e-6,
        )

    def test_degenerate_geometry(self):
        points = np.zeros((21, 3))

        finger_points = self.local_frame._get_finger_points(
            points,
            self.local_frame.finger_indices["index"],
        )

        geometry = self.local_frame._compute_finger_geometry(finger_points)

        proximal = self.local_frame._compute_proximal_frame(geometry)

        assert proximal["is_valid"] is False
        assert proximal["rotation_matrix"] is None
