from abc import ABC, abstractmethod

DEFAULT_HANDS_CFG_PATH = "src/kinematics/config/cfg.yaml"


class Kinematics(ABC):
    def __init__(self, hands_cfg_path: str | None = None):
        self.hands_cfg_path = hands_cfg_path or DEFAULT_HANDS_CFG_PATH

    @abstractmethod
    def process(self):
        pass
