from typing import Dict

import numpy as np

from .base import AnatomicalCalibration


class CalibrationCenterOfRotation(AnatomicalCalibration):
    """
    this function is using for calibrated all the inputs landmarks
    following right center-of-rotation
    """

    def __init__(
        self,
        hands_cfg_path: str | None = None,
    ):
        super().__init__(hands_cfg_path=hands_cfg_path)

        self.calibration_config = self.hands_cfg_path["calibration"]
        self.epsilon = self.calibration_config["epsilon"]
        self.joint_thickness = self.calibration_config["joint_thickness"]

    def _get_landmark_and_thickness(
        self, finger_data: Dict, finger: str, frame_name: str
    ):
        frame_mapping = {"proximal": "mcp", "intermediate": "pip", "distal": "dip"}

        if frame_name not in frame_mapping:
            raise ValueError(f"Unknown frame: {frame_name}")

        joint_name = frame_mapping[frame_name]

        landmark = finger_data["points"][joint_name]

        thickness = self.joint_thickness[finger][joint_name]

        return landmark, thickness

    def _compute_anatomical_offset(
        self,
        landmark: np.ndarray,
        local_rotation: np.ndarray,
        joint_thickness: float,
        d_ref: np.ndarray,
    ):
        z_axis_local = local_rotation[:, 2]

        s = np.dot(a=z_axis_local, b=d_ref)

        if s > self.epsilon:
            sign = 1.0
        elif s < -self.epsilon:
            sign = -1.0
        else:
            return {
                "origin": None,
                "offset_vector": None,
                "sign": None,
                "is_valid": False,
            }

        offset_vector = sign * (joint_thickness / 2.0) * z_axis_local

        anatomical_origin = landmark + offset_vector

        return {
            "origin": anatomical_origin,
            "offset_vector": offset_vector,
            "sign": sign,
            "is_valid": True,
        }

    def process(
        self,
        finger: str,
        finger_data: Dict,
        d_ref: np.ndarray,
    ):
        frames = ["proximal", "intermediate", "distal"]

        finger_result = {}

        for frame_name in frames:
            landmark, thickness = self._get_landmark_and_thickness(
                finger_data=finger_data,
                finger=finger,
                frame_name=frame_name,
            )

            local_frame = finger_data["local_frames"][frame_name]

            if not local_frame["is_valid"]:
                finger_result[frame_name] = {
                    "origin": None,
                    "offset_vector": None,
                    "sign": None,
                    "is_valid": False,
                }
                continue

            local_rotation = local_frame["rotation_matrix"]

            finger_result[frame_name] = self._compute_anatomical_offset(
                landmark=landmark,
                local_rotation=local_rotation,
                joint_thickness=thickness,
                d_ref=d_ref,
            )

        return finger_result
