from src.utils import CfgParse, CrossProduct, Normalize  # noqa: F401

from .base import AnatomicalCalibration


class CalibrationCenterOfRotation(AnatomicalCalibration):
    def __init__(self, hands_cfg_path: str | None = None):
        super().__init__(hands_cfg_path=hands_cfg_path)
