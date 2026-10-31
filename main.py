from src.camera import HandMarker
from src.camera import Camera
from src.kinematics import VirtualRootFrame
class PipeLine:
    def __init__(
        self,
        num_hands:int
    ):
        self.num_hands = num_hands

        self.hand_marker = HandMarker(
            model="handtasks",
            num_hands=self.num_hands
        )
        self.world_landmarks = self.hand_marker.latest_result.hand_world_landmarks

        self.virtual_frame = VirtualRootFrame(
            world_landmarks=self.world_landmarks
        )

    def _hand_marker(self):
        return self.hand_marker.run()

    def _virtual_root_frame(self):
        return self.virtual_frame.process()
        
    def process(self):
       self._hand_marker()
       self._virtual_root_frame()
       
def main():
    PipeLine(
        num_hands=2
    ).process()

if __name__ == "__main__":
    main()