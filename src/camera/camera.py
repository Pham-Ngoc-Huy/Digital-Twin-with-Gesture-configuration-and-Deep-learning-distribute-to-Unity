from .base import Stream
import cv2

class Camera(Stream):
    def __init__(
        self,
        device_id:int = 0
    ):
        super().__init__()
        self.device_id = device_id
        self.cap = cv2.VideoCapture(self.device_id)

    def _get_frame(self):
        if not self.cap.isOpened():
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None

        corrected_frame = cv2.flip(
            src=frame,
            flipCode=1
        )
        return True, corrected_frame
    
    def stream(self):
        if not self.cap.isOpened():
            print("Could not open the WebCam")
            return
        
        try: 
            while self.cap.isOpened():
                ret, frame = self._get_frame()
                if not ret:
                    break
                yield ret, frame

        finally:
            self.close()

    def run(self):
        window_name = "Camera Feed Test"
        cv2.namedWindow(
            winname=window_name,
            flags=cv2.WINDOW_NORMAL
        )
        try:
            for ret, frame in self.stream():
                if not ret or frame is None:
                    break

                cv2.imshow(window_name, frame)

                key = cv2.waitKey(1) & 0xFF
                if key == ord("q") or key == 27:
                    break
        finally:
            cv2.destroyWindow(
                winname=window_name
            )

    def close(self):
        if hasattr(self, "cap") and self.cap.isOpened():
            self.cap.release()
            print("Camera device released.")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()