from src.utils import CfgParse

from .base import Kinematics


class AnatomicalCalibration(Kinematics):
    """Collect the anatomical constants required by the kinematics pipeline.

    Segment lengths, joint centres and joint axes are estimated from static
    calibration frames. This class is currently a scaffold: the hand
    configuration is loaded through the ``Kinematics`` base construction and
    the calibration routine itself is still to be implemented.
    """

    def __init__(self, hands_cfg_path: str | None = None):
        super().__init__(hands_cfg_path=hands_cfg_path)
        self.hands_cfg = CfgParse(path=self.hands_cfg_path).process()

    def process(self, *args, **kwargs):
        raise NotImplementedError(
            "AnatomicalCalibration.process() has not been implemented yet."
        )
