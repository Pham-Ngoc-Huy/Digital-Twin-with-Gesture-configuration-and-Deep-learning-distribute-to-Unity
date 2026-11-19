from typing import Dict

import numpy as np

from src.utils import CfgParse, CrossProduct, Normalize

from .base import Kinematics


class VirtualLocalFrame(Kinematics):
    """
    with `virtual-local-frame`:
    Landmark IDs:
        5, 6, 7, 8: Index MCP, PIP, DIP, TIP
        9, 10, 11, 12: Ring MCP, PIP, DIP, TIP
        13, 14, 15, 16: Middle MCP, PIP, DIP, TIP
        17, 18, 19, 20: Pinky MCP, PIP, DIP, TIP

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
        self.idx_index_tip = self.hands_cfg["handmotion"]["index_finger"]["tip"][
            "index"
        ]

        self.idx_ring_mcp = self.hands_cfg["handmotion"]["ring_finger"]["mcp"]["index"]
        self.idx_ring_dip = self.hands_cfg["handmotion"]["ring_finger"]["dip"]["index"]
        self.idx_ring_pip = self.hands_cfg["handmotion"]["ring_finger"]["pip"]["index"]
        self.idx_ring_tip = self.hands_cfg["handmotion"]["ring_finger"]["tip"]["index"]

        self.idx_middle_mcp = self.hands_cfg["handmotion"]["middle_finger"]["mcp"][
            "index"
        ]
        self.idx_middle_dip = self.hands_cfg["handmotion"]["middle_finger"]["dip"][
            "index"
        ]
        self.idx_middle_pip = self.hands_cfg["handmotion"]["middle_finger"]["pip"][
            "index"
        ]
        self.idx_middle_tip = self.hands_cfg["handmotion"]["middle_finger"]["tip"][
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
        self.idx_pinky_tip = self.hands_cfg["handmotion"]["pinky_finger"]["tip"][
            "index"
        ]

        self.finger_indices = {
            "index": {
                "mcp": self.idx_index_mcp,
                "pip": self.idx_index_pip,
                "dip": self.idx_index_dip,
                "tip": self.idx_index_tip,
            },
            "middle": {
                "mcp": self.idx_middle_mcp,
                "pip": self.idx_middle_pip,
                "dip": self.idx_middle_dip,
                "tip": self.idx_middle_tip,
            },
            "ring": {
                "mcp": self.idx_ring_mcp,
                "pip": self.idx_ring_pip,
                "dip": self.idx_ring_dip,
                "tip": self.idx_ring_tip,
            },
            "pinky": {
                "mcp": self.idx_pinky_mcp,
                "pip": self.idx_pinky_pip,
                "dip": self.idx_pinky_dip,
                "tip": self.idx_pinky_tip,
            },
        }

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

        if "origin" not in root_state or "rotation_matrix" not in root_state:
            raise ValueError("Invalid root state.")

        root_rotation_matrix = root_state["rotation_matrix"]
        root_origin = root_state["origin"]

        # this helps change from vector to new coordinates frame
        root_points = (world_points - root_origin) @ root_rotation_matrix

        return root_points

    def _compute_finger_geomertry(
        self, finger_points: Dict[str, np.ndarray]
    ) -> Dict[str, np.ndarray]:
        proximal_vector = finger_points["pip"] - finger_points["mcp"]
        intermediate_vector = finger_points["dip"] - finger_points["pip"]
        distal_vector = finger_points["tip"] - finger_points["dip"]

        is_valid_proximal = np.linalg.norm(proximal_vector) > 1e-8
        is_valid_intermediate = np.linalg.norm(intermediate_vector) > 1e-8
        is_valid_distal = np.linalg.norm(distal_vector) > 1e-8

        return {
            "proximal_vector": {
                "vector": proximal_vector,
                "is_valid": is_valid_proximal,
            },
            "intermediate_vector": {
                "vector": intermediate_vector,
                "is_valid": is_valid_intermediate,
            },
            "distal_vector": {
                "vector": distal_vector,
                "is_valid": is_valid_distal,
            },
        }

    def _compute_proximal_frame(
        self, segment_vectors: Dict[str, Dict[str, np.ndarray]]
    ):
        vector_a = segment_vectors["proximal_vector"]["vector"]
        vector_b = segment_vectors["intermediate_vector"]["vector"]

        normal_vector = CrossProduct(v1=vector_a, v2=vector_b).process()

        normal_magnitude = np.linalg.norm(normal_vector)

        if normal_magnitude < 1e-8:
            return {"vector": None, "is_valid": False}

        return {"vector": Normalize(v=normal_vector).process(), "is_valid": True}

    def _compute_distal_frame(self):
        return 0

    def process(self):
        return 0
