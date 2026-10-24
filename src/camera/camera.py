from .base import Stream
import cv2

class Camera(Stream):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)

    def turn_cam(self):
        if not self.cap.isOpened():
            print("Could not open the WebCam")
            exit()

        print("Camera is opened. Wanna stop - press `q`")
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Error: Failed to got frame.")
                break

            # 1: mean horizontal-flip
            # 0: mean vertical-flip
            # -1: both axis-flip
            corrected_frame = cv2.flip(frame, 1)

            cv2.imshow("Webcam feed: ", corrected_frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            return ret, corrected_frame

        # Release the camera and close all OpenCV windows
        self.cap.release()
        cv2.destroyAllWindows()

    def plot_marker(self):
        pass