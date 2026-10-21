from .base import Kinematics
from utils import (
    CfgParse,
    Normalize,
    CrossProduct,
    Projection
)
import numpy as np
from typing import List
from mediapipe.tasks.python.components.containers.category import Category
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
            landmark_id = self.hands_cfg['wrist']['0']
        )

        index_mcp = self._get_points(
            landmark_id = self.hands_cfg['index_finger']['5']
        )

        middle_mcp = self._get_points(
            landmark_id = self.hands_cfg['middle_finger']['9']
        )

        pinky_mcp = self._get_points(
            landmark_id = self.hands_cfg['pinky']['17']
        )

        # virtual origin
        origin = np.mean([
            wrist, 
            index_mcp,
            middle_mcp, 
            pinky_mcp
            ],
            axis=0
        )


