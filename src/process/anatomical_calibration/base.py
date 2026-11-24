from src.utils import CfgParse

from ..base import Kinematics


class AnatomicalCalibration(Kinematics):
    def __init__(self, hands_cfg_path: str | None = None):
        super().__init__(hands_cfg_path=hands_cfg_path)
        self.hands_cfg = CfgParse(path=self.hands_cfg_path).process()

    def process(self):
        pass
