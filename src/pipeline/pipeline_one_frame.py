from os import PathLike

import numpy as np

from src.kinematics import VirtualLocalFrame, VirtualRootFrame


class PipeLineOneFrame:
    def __init__(self, hands_cfg_path: str):
        self.root_frame = VirtualRootFrame(hands_cfg_path=hands_cfg_path)

        self.local_frame = VirtualLocalFrame(hands_cfg_path=hands_cfg_path)

    def run(self, landmark_path: str | PathLike[str] | np.ndarray):
        """Run on a landmark .npy path or on an already-loaded (21, 3) array."""
        if isinstance(landmark_path, (str, PathLike)):
            world_landmarks = np.load(landmark_path, allow_pickle=True)
        else:
            world_landmarks = np.asarray(landmark_path)

        root_state = self.root_frame.process(world_landmarks)

        local_state = self.local_frame.process(
            world_points=world_landmarks, root_state=root_state
        )

        return {"root": root_state, "local": local_state}
