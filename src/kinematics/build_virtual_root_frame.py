from .base import Kinematics
from utils import (
    CfgParse,
    Normalize,
    CrossProduct,
    Projection
)
import numpy as np
from typing import List
from mediapipe.tasks.python.components.containers.landmark import Landmark, NormalizedLandmark

class VirtualRootFrame(Kinematics):
    """
    with `virtual-root-frame`:
    Landmark IDs:
        0  : Wrist
        5  : Index MCP
        9  : Middle MCP
        17 : Pinky MCP

    Convention:
        Origin = centroid of landmarks 0, 5, 9, 17
        Z-axis = Wrist -> Middle MCP
        X-axis = Pinky MCP -> Index MCP,
                 orthogonalized against Z
        Y-axis = Z cross X

    Rotation matrix columns are [X, Y, Z].
    This is a project-specific approximation, not an
    exact reproduction of the physical marker setup.
    """
    def __init__(
        self,
        world_landmarks: List[List[Landmark]],
        hands_cfg_path:str
    ):
        self.world_landmarks = world_landmarks
        self.hands_cfg_path = hands_cfg_path
        self.hands_cfg = CfgParse(
            path=self.hands_cfg_path
        ).process()
    
    def _get_points(
        self,
        landmark_id:int
    ):
        landmark = self.world_landmarks[landmark_id]
        if hasattr(landmark,"x"):
            point = np.array(
                [landmark.x, landmark.y, landmark.z],
                dtype=float
            )
        else:
            point = np.asarray(landmark, dtype=float)

        if point.shape != (3,):
            raise ValueError("Each landmark must be a 3D point.")

        if not np.all(np.isfinite(point)):
            raise ValueError("Landmark contains invalid values.")

        return point

    def process(self):
        wrist = self._get_points(
            landmark_id = self.hands_cfg['handmotion']['wrist']['wrist']['index']
        )

        index_mcp = self._get_points(
            landmark_id = self.hands_cfg['handmotion']['index_finger']['mcp']['index']
        )

        middle_mcp = self._get_points(
            landmark_id = self.hands_cfg['handmotion']['middle_finger']['mcp']['index']
        )

        pinky_mcp = self._get_points(
            landmark_id = self.hands_cfg['handmotion']['pinky']['mcp']['index']
        )

        # 1. Virtual origin
        origin = np.mean([
            wrist, 
            index_mcp,
            middle_mcp, 
            pinky_mcp
            ],
            axis=0
        )

        # 2. Z-axis: longitudinal direction of the hand
        z_hat = Normalize(
            middle_mcp - wrist
        ).process()

        # 3. X-axis: across the palm, orthogonal to Z
        x_raw = index_mcp - pinky_mcp

        x_hat = Projection(
            z_hat, x_raw
        ).process()

        # 4. Y-axis: right-handed normal direction
        y_hat = CrossProduct(
            z_hat, x_hat
        ).process()

        # Re-orthogonalize X to reduce numerical error
        x_hat = CrossProduct(
            y_hat, z_hat
        ).process()

        # Rotation matrix: axes are columns
        R = np.column_stack((x_hat, y_hat, z_hat))

        # 5. Validate the rotation matrix
        if not np.allclose(
            R.T @ R, np.eye(3), atol=1e-6
        ):
            raise ValueError("Root frame is not orthonormal.")

        if not np.isclose(
            np.linalg.det(R), 1.0, atol=1e-6
        ):
            raise ValueError("Root frame is not right-handed.")

        return {
            "origin": origin,
            "rotation_matrix": R,
            "x_axis": x_hat,
            "y_axis": y_hat,
            "z_axis": z_hat,
        }


