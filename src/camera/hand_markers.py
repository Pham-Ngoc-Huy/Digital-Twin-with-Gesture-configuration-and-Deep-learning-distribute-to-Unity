import time
import cv2
import mediapipe as mp

from .base import Stream
from camera import Camera
from utils import CfgParse


class HandMarker(Stream):

    BaseOptions = mp.tasks.BaseOptions
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    def __init__(self, model: str = "handtasks"):
        super().__init__()
        self.camera = Camera()
        cfg = CfgParse(path="src/kinematics/config/cfg.yaml").process()
        if hasattr(cfg, "assets"):
            self.model_path = cfg.assets[model]["file_path"]
        else:
            self.model_path = cfg[model]["file_path"]

        # Initialize the landmarker once for the live stream session
        options = self._get_options()
        self.landmarker = self.HandLandmarker.create_from_options(options)

    @staticmethod
    def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
        if result.hand_landmarks:
            print(f"[{timestamp_ms} ms] Detected {len(result.hand_landmarks)} hand(s): {result}")

    def _get_options(self):
        return self.HandLandmarkerOptions(
            base_options=self.BaseOptions(model_asset_path=self.model_path),
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=self.print_result,
        )

    def turn_cam(self):
        return self.camera.turn_cam()

    def process_frame(self):
        ret, frame = self.camera.turn_cam()
        if not ret or frame is None:
            return None

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(time.time() * 1000)

        self.landmarker.detect_async(mp_image, timestamp_ms)
        return frame

    def plot_marker(self):
        return self.process_frame()

    def close(self):
        """Release MediaPipe resources."""
        if hasattr(self, "landmarker"):
            self.landmarker.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()