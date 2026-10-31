from .base import Kinematics
from src.utils import (
    CfgParse,
    Normalize,
    CrossProduct,
    Projection
)
import numpy as np
from typing import List, Optional, Dict, Any
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
        hands_cfg_path:str = "src/kinematics/config/cfg.yaml"
    ):
        self.hands_cfg_path = hands_cfg_path
        self.hands_cfg = CfgParse(
            path=self.hands_cfg_path
        ).process()

        self.last_valid_state: Optional[Dict[str, Any]] = None

        self.idx_wrist = self.hands_cfg['handmotion']['wrist']['wrist']['index']
        self.idx_index_mcp = self.hands_cfg['handmotion']['index_finger']['mcp']['index']
        self.idx_middle_mcp = self.hands_cfg['handmotion']['middle_finger']['mcp']['index']
        self.idx_pinky_mcp = self.hands_cfg['handmotion']['pinky']['mcp']['index']

        self.required_indices = [
            self.idx_wrist,
            self.idx_index_mcp,
            self.idx_middle_mcp,
            self.idx_pinky_mcp
        ]

    def _get_points(
        self,
        world_landmarks: List[Landmark],
        landmark_id:int
    ) -> np.ndarray:
        
        landmark = world_landmarks[landmark_id]
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

    def _is_valid_input(
        self,
        world_landmarks: Optional[List[Landmark]]
    ) -> bool:

        if world_landmarks is None or len(world_landmarks) == 0:
            return False

        max_idx = max(self.required_indices)

        if len(world_landmarks) <= max_idx:
            return False

        return True
    
    def process(
        self,
        world_landmarks: Optional[List[Landmark]]
    ):
        if not self._is_valid_input(world_landmarks=world_landmarks):
            return self.last_valid_state

        try:
            wrist = self._get_points(
                world_landmarks = world_landmarks,
                landmark_id = self.idx_wrist
            )

            index_mcp = self._get_points(
                world_landmarks = world_landmarks,
                landmark_id = self.idx_index_mcp
            )

            middle_mcp = self._get_points(
                world_landmarks = world_landmarks,
                landmark_id = self.idx_middle_mcp
            )

            pinky_mcp = self._get_points(
                world_landmarks = world_landmarks,
                landmark_id = self.idx_pinky_mcp
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

            state = {
                "origin": origin,
                "rotation_matrix": R,
                "x_axis": x_hat,
                "y_axis": y_hat,
                "z_axis": z_hat,
            }
            self.last_valid_state = state
            return state
        except (ValueError, IndexError, TypeError):
            return self.last_valid_state

