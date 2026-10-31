from .base import TestCases
import numpy as np
from unittest.mock import MagicMock, patch
from src.camera import HandMarker


class TestHandMarkers(TestCases):
    def setup_method(self):
        self.patchers = {
            "camera": patch("src.camera.hand_markers.Camera"),
            "cfg": patch("src.camera.hand_markers.CfgParse"),
            "landmark_create": patch.object(
                HandMarker.HandLandmarker,
                "create_from_options",
            ),
            "display": patch("src.camera.hand_markers.MarkerDisplay"),
            "imshow": patch("src.camera.hand_markers.cv2.imshow"),
            "wait_key": patch("src.camera.hand_markers.cv2.waitKey", return_value=ord('q')),
            "destroy_window": patch("src.camera.hand_markers.cv2.destroyWindow"),
        }
        self.mocks = {}
        for name, patcher in self.patchers.items():
            self.mocks[name] = patcher.start()

        mock_cfg_inst = self.mocks["cfg"].return_value
        mock_cfg_inst.process.return_value = {
            "handtasks": {"file_path": "fake/path/model.task"}
        }

        self.fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.model = "handtasks"
        self.fake_num_hands = 2

    def teardown_method(self):
        patch.stopall()

    def test_init_and_options(self):
        marker = HandMarker(
            model=self.model,
            num_hands=self.fake_num_hands
        )
        assert marker.num_hands == self.fake_num_hands
        assert marker.model_path == "fake/path/model.task"
        self.mocks["landmark_create"].assert_called_once()

    def test_result_callback(self):
        marker = HandMarker()
        mock_result = MagicMock()
        mock_img = MagicMock()
        timestamp = 1000

        marker._result_callback(
            result=mock_result,
            output_image=mock_img,
            timestamp_ms=timestamp
        )

        assert marker.latest_result == mock_result
        assert marker.latest_output_image == mock_img
        assert marker.latest_timestamp_ms == timestamp

    def test_process_frame_and_non_draw(self):
        marker = HandMarker()
        assert marker._process_frame_and_draw(bgr_frame=None) is None

    def test_process_frame_and_draw_with_landmarks(self):
        marker = HandMarker()
        mock_result = MagicMock()
        mock_result.hand_landmarks = [[MagicMock()]]
        marker.latest_result = mock_result

        annotated_rgb = self.fake_frame

        self.mocks["display"].draw_landmarks_on_image.return_value = annotated_rgb

        output_frame = marker._process_frame_and_draw(bgr_frame=self.fake_frame)

        marker.landmarker.detect_async.assert_called_once()
        self.mocks["display"].draw_landmarks_on_image.assert_called_once()
        assert output_frame is not None

    def test_process_frame_and_draw_exception_fallback(self):
        marker = HandMarker()

        mock_result = MagicMock()
        mock_result.hand_landmarks = [[MagicMock()]]
        marker.latest_result = mock_result

        self.mocks["display"].draw_landmarks_on_image.side_effect = Exception("Drawing Error")

        output_frame = marker._process_frame_and_draw(bgr_frame=self.fake_frame)
        np.testing.assert_array_equal(output_frame, self.fake_frame)

    def test_context_manager_and_cleanup(self):
        with HandMarker() as marker:
            landmarker_mock = marker.landmarker
            camera_mock = marker.camera

        landmarker_mock.close.assert_called_once()
        camera_mock.close.assert_called_once()

    def test_run(self):
        self.test_init_and_options()
        self.test_process_frame_and_non_draw()
        self.test_process_frame_and_draw_with_landmarks()
        self.test_process_frame_and_draw_exception_fallback()
        self.test_result_callback()
        self.test_context_manager_and_cleanup()
