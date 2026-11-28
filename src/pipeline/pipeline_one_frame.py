from os import PathLike

import numpy as np

from .pipeline import HandProcessor


class PipeLineOneFrame:
    def __init__(self, hands_cfg_path: str):
        self.processor = HandProcessor(hands_cfg_path=hands_cfg_path)

    def run(self, landmark_path: str | PathLike[str] | np.ndarray):
        """Run on a landmark .npy path or on an already-loaded (21, 3) array."""
        if isinstance(landmark_path, (str, PathLike)):
            world_landmarks = np.load(landmark_path, allow_pickle=True)
        else:
            world_landmarks = np.asarray(landmark_path)

        return self.processor.process(world_landmarks)
