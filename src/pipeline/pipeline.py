import cv2
import numpy as np

from src.camera import HandMarker
from src.process import (
    CalibrationCenterOfRotation,
    VirtualLocalFrame,
    VirtualRootFrame,
)

from .fmt import print_calibrate_cor_tabulate, print_hand_kinematics

# Local frames are expressed in root-frame coordinates, where +Z is the
# longitudinal direction of the hand (wrist -> middle MCP).
ROOT_Z_AXIS = np.array([0.0, 0.0, 1.0], dtype=np.float64)


def landmarks_to_array(world_landmarks) -> np.ndarray:
    """Convert MediaPipe landmarks (or a (21, 3) array) into a float array."""
    points = np.asarray(
        [
            [landmark.x, landmark.y, landmark.z] if hasattr(landmark, "x") else landmark
            for landmark in world_landmarks
        ],
        dtype=np.float64,
    )

    if points.shape != (21, 3):
        raise ValueError(f"Expected 21 landmarks of shape (21, 3), got {points.shape}")

    if not np.isfinite(points).all():
        raise ValueError("Landmarks contain NaN or Inf values")

    return points


class HandProcessor:
    """Root frame -> virtual local frames -> center-of-rotation calibration."""

    def __init__(self, hands_cfg_path: str):
        self.root_frame = VirtualRootFrame(hands_cfg_path=hands_cfg_path)
        self.local_frame = VirtualLocalFrame(hands_cfg_path=hands_cfg_path)
        self.calibration = CalibrationCenterOfRotation(hands_cfg_path=hands_cfg_path)

    def process(self, world_landmarks):
        if world_landmarks is None or len(world_landmarks) == 0:
            return None

        root_state = self.root_frame.process(world_landmarks=world_landmarks)
        if root_state is None:
            return None

        local_state = self.local_frame.process(
            world_points=landmarks_to_array(world_landmarks),
            root_state=root_state,
        )

        calibration_state = None
        if self.calibration.is_configured:
            calibration_state = {
                finger: self.calibration.process(
                    finger=finger,
                    finger_data=finger_data,
                    d_ref=ROOT_Z_AXIS,
                )
                for finger, finger_data in local_state.items()
            }

        return {
            "root": root_state,
            "local": local_state,
            "calibration": calibration_state,
        }


class PipeLine:
    def __init__(self, num_hands: int, hands_cfg_path: str):
        self.num_hands = num_hands
        self.window_name = "Hand Tracking"
        self._last_ts = None

        self.hand_marker = HandMarker(
            model="handtasks",
            num_hands=num_hands,
            hands_cfg_path=hands_cfg_path,
        )

        self.hand_processors = [
            HandProcessor(hands_cfg_path=hands_cfg_path) for _ in range(num_hands)
        ]
        self.root_frames = [processor.root_frame for processor in self.hand_processors]
        self.local_frames = [
            processor.local_frame for processor in self.hand_processors
        ]
        self.calibrations = [
            processor.calibration for processor in self.hand_processors
        ]

    def _extract_world_landmarks(self, result):
        if result is None:
            return []
        return result.hand_world_landmarks or []

    def process_frame(self, result):
        hands = self._extract_world_landmarks(result)
        return [
            processor.process(hands[i] if i < len(hands) else None)
            for i, processor in enumerate(self.hand_processors)
        ]

    def _is_new_result(self) -> bool:
        ts = self.hand_marker.latest_timestamp_ms
        if ts is None or ts == self._last_ts:
            return False
        self._last_ts = ts
        return True

    def run(self):
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        try:
            frame_number = 0
            for frame, result in self.hand_marker.stream():
                if frame is None:
                    continue

                if self._is_new_result():
                    print("=" * 80)
                    print(f"Frame-number: {frame_number}")

                    states = self.process_frame(result)
                    print("-" * 80)
                    self._log(result, states)

                cv2.imshow(self.window_name, frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
                frame_number += 1
        finally:
            cv2.destroyAllWindows()

    def _log(self, result, states):
        hands = self._extract_world_landmarks(result)
        if hands:
            wrist = hands[0][0]
            print(f"world wrist: {wrist}")

        if not states or states[0] is None:
            return

        state = states[0]
        origin = state["root"]["origin"]

        print(f"root origin: {origin}")
        print(f"local frames: {len(state['local'])} fingers")

        print_hand_kinematics(hand_dict=state["local"], precision=4)
        calibration = state["calibration"]
        if calibration is None:
            print("calibration skipped: > fill in [cfg.yaml] calibration values")
        else:
            valid = sum(
                frame["is_valid"]
                for finger in calibration.values()
                for frame in finger.values()
            )
            total = sum(len(finger) for finger in calibration.values())

            print("-" * 80)

            print(f"[calibrated origins] {valid}/{total} joints valid")

            print_calibrate_cor_tabulate(cor_dict=calibration, precision=4)

    def close(self):
        self.hand_marker.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()
