from unittest.mock import MagicMock, patch
import numpy as np
from src.camera import Camera
from src.camera import camera as camera_module
from .base import TestCases


class TestCamera(TestCases):
    
    def setup_method(self):
        self.device_id = 0
        self.fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.flipped_frame = np.ones((480, 640, 3), dtype=np.uint8)

    @staticmethod
    def _make_camera_capture(read_results=None, is_opened=True):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = is_opened
        if read_results is not None:
            mock_cap.read.side_effect = read_results
        return mock_cap

    @patch("src.camera.camera.cv2.VideoCapture")
    def test_camera_init(self, mock_videocapture):
        cam = Camera(device_id=self.device_id)

        mock_videocapture.assert_called_once_with(self.device_id)
        assert cam.device_id == self.device_id
        assert cam.cap is mock_videocapture.return_value

    @patch("src.camera.camera.cv2.flip")
    @patch("src.camera.camera.cv2.VideoCapture")
    def test_get_frame_success(self, mock_videocapture, mock_flip):
        mock_cap = self._make_camera_capture([(True, self.fake_frame)])
        mock_videocapture.return_value = mock_cap
        mock_flip.return_value = self.flipped_frame

        cam = Camera(device_id=self.device_id)
        ret, frame = cam._get_frame()

        assert ret is True
        assert frame is self.flipped_frame
        mock_cap.read.assert_called_once_with()
        mock_flip.assert_called_once_with(
            src=self.fake_frame,
            flipCode=1,
        )

    @patch("src.camera.camera.cv2.flip")
    @patch("src.camera.camera.cv2.VideoCapture")
    def test_get_frame_camera_not_opened(
        self,
        mock_videocapture,
        mock_flip,
    ):
        mock_cap = self._make_camera_capture(is_opened=False)
        mock_videocapture.return_value = mock_cap

        cam = Camera(device_id=self.device_id)
        ret, frame = cam._get_frame()

        assert ret is False
        assert frame is None
        mock_cap.read.assert_not_called()
        mock_flip.assert_not_called()

    @patch("src.camera.camera.cv2.flip")
    @patch("src.camera.camera.cv2.VideoCapture")
    def test_get_frame_read_failed(
        self,
        mock_videocapture,
        mock_flip,
    ):
        mock_cap = self._make_camera_capture([(False, None)])
        mock_videocapture.return_value = mock_cap

        cam = Camera(device_id=self.device_id)
        ret, frame = cam._get_frame()

        assert ret is False
        assert frame is None
        mock_cap.read.assert_called_once_with()
        mock_flip.assert_not_called()

    @patch("src.camera.camera.cv2.flip")
    @patch("src.camera.camera.cv2.VideoCapture")
    def test_get_frame_returns_none_frame(
        self,
        mock_videocapture,
        mock_flip,
    ):
        mock_cap = self._make_camera_capture([(True, None)])
        mock_videocapture.return_value = mock_cap

        cam = Camera(device_id=self.device_id)
        ret, frame = cam._get_frame()

        assert ret is False
        assert frame is None
        mock_flip.assert_not_called()

    @patch("src.camera.camera.cv2.flip")
    @patch("src.camera.camera.cv2.VideoCapture")
    def test_stream_yields_frames_and_closes_camera(
        self,
        mock_videocapture,
        mock_flip,
    ):
        mock_cap = self._make_camera_capture(
            [(True, self.fake_frame), (False, None)]
        )
        mock_videocapture.return_value = mock_cap
        mock_flip.return_value = self.flipped_frame

        cam = Camera(device_id=self.device_id)
        frames = list(cam.stream())

        assert frames == [(True, self.flipped_frame)]
        mock_cap.release.assert_called_once_with()

    @patch("src.camera.camera.cv2.VideoCapture")
    def test_stream_returns_early_when_camera_not_opened(
        self,
        mock_videocapture,
        capsys,
    ):
        mock_cap = self._make_camera_capture(is_opened=False)
        mock_videocapture.return_value = mock_cap

        cam = Camera(device_id=self.device_id)
        frames = list(cam.stream())

        assert frames == []
        assert "Could not open the WebCam" in capsys.readouterr().out
        mock_cap.read.assert_not_called()

    @patch("src.camera.camera.cv2.VideoCapture")
    def test_close_releases_camera(self, mock_videocapture):
        mock_cap = self._make_camera_capture()
        mock_videocapture.return_value = mock_cap

        cam = Camera(device_id=self.device_id)
        cam.close()

        mock_cap.release.assert_called_once_with()

    @patch("src.camera.camera.cv2.VideoCapture")
    def test_close_without_opened_camera(self, mock_videocapture):
        mock_cap = self._make_camera_capture(is_opened=False)
        mock_videocapture.return_value = mock_cap

        cam = Camera(device_id=self.device_id)
        cam.close()

        mock_cap.release.assert_not_called()

    @patch("src.camera.camera.cv2.VideoCapture")
    def test_context_manager_closes_camera(self, mock_videocapture):
        mock_cap = self._make_camera_capture()
        mock_videocapture.return_value = mock_cap

        with Camera(device_id=self.device_id) as cam:
            assert isinstance(cam, Camera)

        mock_cap.release.assert_called_once_with()

    @patch("src.camera.camera.cv2.destroyWindow")
    @patch("src.camera.camera.cv2.waitKey")
    @patch("src.camera.camera.cv2.imshow")
    @patch("src.camera.camera.cv2.namedWindow")
    @patch("src.camera.camera.cv2.flip")
    @patch("src.camera.camera.cv2.VideoCapture")
    def test_run_displays_frames_until_quit(
        self,
        mock_videocapture,
        mock_flip,
        mock_namedwindow,
        mock_imshow,
        mock_waitkey,
        mock_destroywindow,
    ):
        mock_cap = self._make_camera_capture(
            [(True, self.fake_frame), (False, None)]
        )
        mock_videocapture.return_value = mock_cap
        mock_flip.return_value = self.flipped_frame
        mock_waitkey.return_value = ord("q")

        cam = Camera(device_id=self.device_id)
        cam.run()

        mock_namedwindow.assert_called_once_with(
            winname="Camera Feed Test",
            flags=camera_module.cv2.WINDOW_NORMAL,
        )
        mock_imshow.assert_called_once_with(
            "Camera Feed Test",
            self.flipped_frame,
        )
        mock_waitkey.assert_called_once_with(1)
        mock_destroywindow.assert_called_once_with(
            winname="Camera Feed Test"
        )
        mock_cap.release.assert_called_once_with()

    def test_run(self):
        with patch("src.camera.camera.cv2.VideoCapture") as mock_videocapture:
            mock_cap = self._make_camera_capture()
            mock_videocapture.return_value = mock_cap

            cam = Camera(device_id=self.device_id)
            cam.close()

        mock_videocapture.assert_called_once_with(self.device_id)
        assert cam.cap is mock_cap
        mock_cap.release.assert_called_once_with()
