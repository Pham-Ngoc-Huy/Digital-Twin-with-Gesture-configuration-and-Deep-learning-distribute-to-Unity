import time
import cv2
import mediapipe as mp

from .base import Stream
from camera import Camera
from utils import CfgParse
from .viz import MarkerDisplay 

class HandMarker(Stream):

    BaseOptions = mp.tasks.BaseOptions
    HandLandmarker = mp.tasks.vision.HandLandmarker
    HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
    HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
    VisionRunningMode = mp.tasks.vision.RunningMode

    def __init__(
        self, 
        model: str = "handtasks",
        num_hands: int = None
    ):
        super().__init__()
        self.camera = Camera()
        cfg = CfgParse(path="src/kinematics/config/cfg.yaml").process()
        if hasattr(cfg, "assets"):
            self.model_path = cfg.assets[model]["file_path"]
        else:
            self.model_path = cfg[model]["file_path"]

        self.latest_result = None
        self.latest_timestamp_ms = None
        self.latest_output_image = None
        self.num_hands = num_hands
        # Initialize the landmarker once for the live stream session
        options = self._get_options()
        self.landmarker = self.HandLandmarker.create_from_options(options)

    def _result_callback(
        self,
        result: HandLandmarkerResult,
        output_image: mp.Image,
        timestamp_ms: int
    ):
        self.latest_result = result
        self.latest_output_image = output_image
        self.latest_timestamp_ms = timestamp_ms
        if result.hand_landmarks:
            print(f"[{timestamp_ms} ms] Detected {len(result.hand_landmarks)} hand(s): {result}")

    def _get_options(self):
        return self.HandLandmarkerOptions(
            base_options=self.BaseOptions(
                model_asset_path=self.model_path,
            ),
            num_hands = self.num_hands,
            running_mode=self.VisionRunningMode.LIVE_STREAM,
            result_callback=self._result_callback,
        )

    def _process_frame_and_draw(self, bgr_frame):
        if bgr_frame is None:
            return None

        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        timestamp_ms = int(time.time() * 1000)

        self.landmarker.detect_async(mp_image, timestamp_ms)

        result = self.latest_result

        if result and getattr(result, "hand_landmarks", None):
            try:
                annotated_rgb = MarkerDisplay.draw_landmarks_on_image(
                    image=rgb_frame, 
                    detection_result=result
                )
                return cv2.cvtColor(annotated_rgb, cv2.COLOR_RGB2BGR)
            
            except Exception:
                pass
        return bgr_frame

    def run(self):
        window_name = "Hand Tracking with Markers"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        try:
            for ret, frame in self.camera.stream():
                if not ret or frame is None:
                    break

                annotated_frame = self._process_frame_and_draw(frame)
                cv2.imshow(
                    winname=window_name,
                    mat=annotated_frame
                )

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break
        finally:
            cv2.destroyWindow(window_name)
            self.close()

    def close(self):
        """Release MediaPipe resources."""
        if hasattr(self, "landmarker"):
            self.landmarker.close()
        if hasattr(self, "camera"):
            self.camera.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()