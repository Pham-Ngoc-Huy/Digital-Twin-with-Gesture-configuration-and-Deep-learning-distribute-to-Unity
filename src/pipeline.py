import cv2
from src.camera import HandMarker
from src.kinematics import VirtualRootFrame

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
        self.root_frames = [
            VirtualRootFrame(hands_cfg_path=hands_cfg_path)
            for _ in range(num_hands)
        ]

    def _extract_world_landmarks(self, result):
        if result is None:
            return []
        return result.hand_world_landmarks or []

    def process_frame(self, result):
        hands = self._extract_world_landmarks(result)
        return [
            rf.process(hands[i] if i < len(hands) else None)
            for i, rf in enumerate(self.root_frames)
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
            for frame, result in self.hand_marker.stream():
                if frame is None:
                    continue

                if self._is_new_result():
                    print("="*80)
                    states = self.process_frame(result)
                    print("-"*80)
                    self._log(result, states)

                cv2.imshow(self.window_name, frame)
                if cv2.waitKey(1) & 0xFF in (ord("q"), 27):
                    break
        finally:
            cv2.destroyAllWindows()

    def _log(self, result, states):
        hands = self._extract_world_landmarks(result)
        if hands:
            wrist = hands[0][0]
            print(f"[world wrist] x={wrist.x:.3f} y={wrist.y:.3f} z={wrist.z:.3f}")
        if states and states[0] is not None:
            o = states[0]["origin"]
            print(f"[root origin] x={o[0]:.3f} y={o[1]:.3f} z={o[2]:.3f}")

    def close(self):
        self.hand_marker.close()

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.close()