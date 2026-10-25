import mediapipe as mp
import numpy as np
import cv2

MARGIN = 10
FONT_SIZE = 1
FONT_THICKNESS = 1
HANDEDNESS_TEXT_COLOR = (88, 205, 54)  # vibrant green


class MarkerDisplay:

    @staticmethod
    def draw_landmarks_on_image(image, detection_result):
        mp_hands_connections = mp.tasks.vision.HandLandmarksConnections
        mp_drawing = mp.tasks.vision.drawing_utils
        mp_drawing_styles = mp.tasks.vision.drawing_styles

        if detection_result is None:
            return np.copy(image)

        hand_landmarks_list = getattr(detection_result, "hand_landmarks", None) or []
        handedness_list = getattr(detection_result, "handedness", None) or []

        annotated_image = np.copy(image)

        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]
            handedness = handedness_list[idx] if idx < len(handedness_list) else []

            try:
                mp_drawing.draw_landmarks(
                    annotated_image,
                    hand_landmarks,
                    mp_hands_connections.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style(),
                )
            except Exception:
                # Try to draw manually if drawing_utils fails
                try:
                    height, width, _ = annotated_image.shape
                    for lm in hand_landmarks:
                        cx, cy = int(lm.x * width), int(lm.y * height)
                        cv2.circle(annotated_image, (cx, cy), 3, (0, 255, 0), -1)
                except Exception:
                    pass

            try:
                height, width, _ = annotated_image.shape
                x_coordinates = [lm.x for lm in hand_landmarks]
                y_coordinates = [lm.y for lm in hand_landmarks]
                if x_coordinates and y_coordinates:
                    text_x = int(min(x_coordinates) * width)
                    text_y = int(min(y_coordinates) * height) - MARGIN
                    category_name = "Hand"
                    if handedness:
                        try:
                            h0 = handedness[0]
                            if hasattr(h0, "category_name"):
                                category_name = h0.category_name
                            elif isinstance(h0, list) and h0 and hasattr(h0[0], "category_name"):
                                category_name = h0[0].category_name
                        except Exception:
                            pass
                    cv2.putText(
                        img=annotated_image,
                        text=f"{category_name}",
                        org=(text_x, text_y),
                        fontFace=cv2.FONT_HERSHEY_DUPLEX,
                        fontScale=FONT_SIZE,
                        color=HANDEDNESS_TEXT_COLOR,
                        thickness=FONT_THICKNESS,
                        lineType=cv2.LINE_AA,
                    )
            except Exception:
                pass
        return annotated_image
