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

        self.idx_pinky_mcp = self.hands_cfg["handmotion"]["pinky"]["mcp"]["index"]
        self.idx_pinky_dip = self.hands_cfg["handmotion"]["pinky"]["dip"]["index"]
        self.idx_pinky_pip = self.hands_cfg["handmotion"]["pinky"]["pip"]["index"]
        self.idx_pinky_tip = self.hands_cfg["handmotion"]["pinky"]["tip"]["index"]

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
        self, points: np.ndarray, indices: Dict[str, int]
    ) -> Dict[str, np.ndarray]:
        return {
            "mcp": points[indices["mcp"]],
            "pip": points[indices["pip"]],
            "dip": points[indices["dip"]],
            "tip": points[indices["tip"]],
        }

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

    def _compute_finger_geometry(self, finger_points: Dict[str, np.ndarray]) -> Dict:
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

    def _compute_proximal_frame(self, segment_vector: Dict[str, Dict[str, np.ndarray]]):
        vector_a = segment_vector["proximal_vector"]["vector"]
        vector_b = segment_vector["intermediate_vector"]["vector"]

        if not (
            segment_vector["proximal_vector"]["is_valid"]
            and segment_vector["intermediate_vector"]["is_valid"]
        ):
            return {"rotation_matrix": None, "is_valid": False}

        normal_vector = CrossProduct(v1=vector_a, v2=vector_b).process()

        normal_magnitude = np.linalg.norm(normal_vector)

        if normal_magnitude < 1e-8:
            return {"rotation_matrix": None, "is_valid": False}

        x_axis = Normalize(v=normal_vector).process()
        z_axis = Normalize(v=vector_a).process()
        y_axis = Normalize(v=CrossProduct(v1=z_axis, v2=x_axis).process()).process()

        rotation_matrix = np.column_stack([x_axis, y_axis, z_axis])
        return {
            "rotation_matrix": rotation_matrix,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "z_axis": z_axis,
            "is_valid": True,
        }

    def _compute_distal_frame(
        self,
        proximal_frame: Dict,
        segment_vector: Dict[str, Dict[str, np.ndarray]],
        segment_name: str,
    ) -> Dict:
        if not proximal_frame["is_valid"]:
            return {"rotation_matrix": None, "is_valid": False}

        segment = segment_vector[segment_name]

        if not segment["is_valid"]:
            return {"rotation_matrix": None, "is_valid": False}

        inherited_x = proximal_frame["x_axis"]
        segment_direction = segment["vector"]

        z_axis = Normalize(v=segment_direction).process()

        x_projected = inherited_x - np.dot(inherited_x, z_axis) * z_axis

        x_magnitude = np.linalg.norm(x_projected)

        if x_magnitude < 1e-8:
            return {"rotation_matrix": None, "is_valid": False}

        x_axis = x_projected / x_magnitude

        y_axis = Normalize(v=CrossProduct(v1=z_axis, v2=x_axis).process()).process()

        rotation_matrix = np.column_stack([x_axis, y_axis, z_axis])

        return {
            "rotation_matrix": rotation_matrix,
            "x_axis": x_axis,
            "y_axis": y_axis,
            "z_axis": z_axis,
            "is_valid": True,
        }

    def _compute_distal_frames(
        self, proximal_frame: Dict, segment_vector: Dict
    ) -> Dict:
        intermediate_frame = self._compute_distal_frame(
            proximal_frame=proximal_frame,
            segment_vector=segment_vector,
            segment_name="intermediate_vector",
        )

        distal_frame = self._compute_distal_frame(
            proximal_frame=proximal_frame,
            segment_vector=segment_vector,
            segment_name="distal_vector",
        )

        return {"intermediate": intermediate_frame, "distal": distal_frame}

    def process(self, world_points: np.ndarray, root_state: Dict) -> Dict:
        world_points = self._get_points(root_points=world_points)

        root_points = self._root_transformation(
            world_points=world_points, root_state=root_state
        )

        result = {}

        for finger_name, indices in self.finger_indices.items():
            print(f"action: {finger_name}...")

            finger_points = self._get_finger_points(points=root_points, indices=indices)

            segment_vector = self._compute_finger_geometry(finger_points=finger_points)

            proximal_frame = self._compute_proximal_frame(segment_vector=segment_vector)

            distal_frames = self._compute_distal_frames(
                proximal_frame=proximal_frame, segment_vector=segment_vector
            )

            result[finger_name] = {
                "points": finger_points,
                "geometry": segment_vector,
                "local_frames": {
                    "proximal": proximal_frame,
                    "intermediate": distal_frames["intermediate"],
                    "distal": distal_frames["distal"],
                },
            }
        return result
