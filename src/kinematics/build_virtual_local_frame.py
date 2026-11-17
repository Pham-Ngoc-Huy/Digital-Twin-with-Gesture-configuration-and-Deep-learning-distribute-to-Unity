from typing import Dict

import numpy as np

from src.utils import CfgParse

from .base import Kinematics


class VirtualLocalFrame(Kinematics):
    """
    with `virtual-local-frame`:
    Landmark IDs:
        5, 6, 7: Index MCP, DIP, PIP
        9, 10, 11: Ring MCP, DIP, PIP
        13, 14, 15: Middle MCP, DIP, PIP
        17, 18, 19: Pinky MCP, DIP, PIP

    """

    def __init__(self, hands_cfg_path: str = "src/kinametics/config/cfg.yaml"):
        self.hands_cfg_path = hands_cfg_path
        self.hands_cfg = CfgParse(path=self.hands_cfg_path).process()

        self.idx_index_mcp = self.hands_cfg["handmotion"]["index_finger"]["mcp"][
            "index"
        ]
        self.idx_index_dip = self.hands_cfg["handmotion"]["index_finger"]["dip"][
            "index"
        ]
        self.idx_index_pip = self.hands_cfg["handmotion"]["index_finger"]["pip"][
            "index"
        ]

        self.idx_ring_mcp = self.hands_cfg["handmotion"]["ring_finger"]["mcp"]["index"]
        self.idx_ring_dip = self.hands_cfg["handmotion"]["ring_finger"]["dip"]["index"]
        self.idx_ring_pip = self.hands_cfg["handmotion"]["ring_finger"]["pip"]["index"]

        self.idx_middle_mcp = self.hands_cfg["handmotion"]["middle_finger"]["mcp"][
            "index"
        ]
        self.idx_middle_dip = self.hands_cfg["handmotion"]["middle_finger"]["dip"][
            "index"
        ]
        self.idx_middle_pip = self.hands_cfg["handmotion"]["middle_finger"]["pip"][
            "index"
        ]

        self.idx_pinky_mcp = self.hands_cfg["handmotion"]["pinky_finger"]["mcp"][
            "index"
        ]
        self.idx_pinky_dip = self.hands_cfg["handmotion"]["pinky_finger"]["dip"][
            "index"
        ]
        self.idx_pinky_pip = self.hands_cfg["handmotion"]["pinky_finger"]["pip"][
            "index"
        ]

        self.mcp_required_indices = [
            self.idx_index_mcp,
            self.idx_middle_mcp,
            self.idx_ring_mcp,
            self.idx_pinky_mcp,
        ]

        self.dip_required_indices = [
            self.idx_index_dip,
            self.idx_middle_dip,
            self.idx_ring_dip,
            self.idx_pinky_dip,
        ]

        self.pip_required_indices = [
            self.idx_index_pip,
            self.idx_middle_pip,
            self.idx_ring_pip,
            self.idx_pinky_pip,
        ]

    def _get_points(self, root_points: np.ndarray) -> np.ndarray:
        points = np.asarray(root_points, dtype=np.float64)

        if points.shape != (21, 3):
            raise ValueError(f"Expected landmarks shape (21, 3), got {points.shape}")

        if not np.isfinite(points).all():
            raise ValueError("Landmarks contain NaN or Inf values")

        return points

    def _get_finger_points(
        self, points: np.ndarray, mcp_idx: int, dip_idx: int, pip_idx: int
    ) -> Dict[str, np.ndarray]:
        return {"mcp": points[mcp_idx], "dip": points[dip_idx], "pip": points[pip_idx]}

    def _root_transformation(
        self, world_points: np.ndarray, root_state: Dict[str, np.ndarray]
    ) -> np.ndarray:
        if root_state is None:
            raise ValueError("Root state is missing.")

        if "origin" not in root_state and "rotation_matrix" not in root_state:
            raise ValueError("Invalid root state.")

        root_rotation_matrix = root_state["rotation_matrix"]
        root_origin = root_state["origin"]

        # this helps change from vector to new coordinates frame
        root_points = (world_points - root_origin) @ root_rotation_matrix

        return root_points
