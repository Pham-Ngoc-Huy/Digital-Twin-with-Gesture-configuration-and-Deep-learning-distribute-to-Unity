from omegaconf import OmegaConf
from .utils_base import Utils

class CfgParse(Utils):
    def __init__(
        self,
        path:str,
        **override
    ):
        self.path = path
        self.override = override
    def process(self):
        baseconfig= OmegaConf.load(self.path)
        overridecfg=OmegaConf.create(self.override)
        final_cfg=OmegaConf.merge(baseconfig, overridecfg)
        return final_cfg