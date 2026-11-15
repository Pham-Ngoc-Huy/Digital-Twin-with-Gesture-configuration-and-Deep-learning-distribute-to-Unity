# Digital Twin Hand — Trao đổi về Anatomical Calibration và Virtual Local Frame

> Bản xuất nội dung cuộc trao đổi hiện tại, tập trung vào việc phát triển Virtual Sensing System dựa trên MediaPipe và paper Cerveri.

## 1. Bối cảnh dự án

- Mục tiêu: xây dựng Digital Twin bàn tay, sử dụng MediaPipe hand landmarks như virtual sensors thay cho glove sensors vật lý.
- Pipeline hướng tới: MediaPipe/Python → xử lý landmarks và kinematics → ROS2 → Unity.
- Paper tham chiếu chính cho mô hình giải phẫu và ước lượng chuyển động: _Finger Kinematic Modeling and Real-Time Hand Motion Estimation_ của Cerveri et al.
- Cần phân biệt mô hình của Cerveri với paper glove sensing: Cerveri mô tả MCP 2DOF, PIP/DIP 1DOF; không nên giản lược toàn bộ thành việc chỉ dựng rotation matrices.

## 2. Trao đổi về các quan hệ hình học và chức năng trong Cerveri

**Người dùng:** Các bạn làm hiện tại nó đang bị hơi đơn giản quá — bởi vì cái hướng trong Cerveri nó còn nhiều hơn thế 2DOF với 1DOF ... các geometrical and functional relations.

**Trợ lý:** Đồng ý rằng chỉ dựng local frames bằng vector và pháp tuyến mặt phẳng mới giải quyết coordinate-frame construction, chưa triển khai đầy đủ hand motion estimation. Cerveri cần được nhìn theo nhiều lớp:

1. Hand kinematic model.
2. Calibration và coordinate frames.
3. Geometrical relations.
4. Functional relations.
5. Real-time motion estimation.

Cần phân biệt:

- **Geometrical relations:** quan hệ hình học giữa marker/segment, ví dụ khoảng cách và vị trí tương đối.
- **Functional relations:** các ràng buộc chuyển động, DOF, giới hạn góc và coupling giữa các khớp.

Đề xuất kiến trúc triển khai phải được xem là adaptation cho MediaPipe, không phải sơ đồ nguyên văn trong paper. MediaPipe có 21 landmarks, khác với protocol 24 physical markers của Cerveri.

## 3. Suy luận DIP từ PIP

**Người dùng:** Dùng từ PIP để suy ngược về DIP.

**Trợ lý:** Có thể dùng functional relation được Cerveri sử dụng:

\[
\theta*{DIP} = \frac{2}{3}\theta*{PIP}
\]

Ví dụ:

- PIP = 90° → DIP = 60°.
- PIP = 60° → DIP = 40°.

Tuy nhiên, cần phân biệt hai bước:

1. Ước lượng góc DIP từ góc PIP.
2. Dùng forward kinematics cùng segment geometry và orientation để khôi phục vị trí DIP.

Functional relation cung cấp góc, không tự cung cấp tọa độ 3D.

**Người dùng:** Ý là cái phần anatomical calibration cần tới cái này không — nếu mà không thì mình có thể vừa làm vừa code phần này.

**Trợ lý:** Có thể phát triển song song. Functional relation DIP–PIP có thể implement riêng; nhưng để khôi phục vị trí 3D cần segment lengths, local frames và joint axes từ calibration.

Các thông tin calibration được nêu gồm:

- Root coordinate frame.
- Local coordinate frames.
- Joint centers.
- Axes of rotation.
- Anthropometric measurements.
- Marker local coordinates.

## 4. Ước lượng chiều dài middle phalanx

**Người dùng:** Tất nhiên là xấp xỉ — hiện tại nếu chỉ tính middle phalanx thì phải tính khoảng cách của PIP-DIP để ra được nhưng mà phải quy chiếu từ root.

**Trợ lý:** Đúng, khoảng cách PIP–DIP là ước lượng chiều dài middle phalanx, không phải chiều dài xương giải phẫu thực tế.

Với MediaPipe index finger:

- Landmark 5: Index MCP.
- Landmark 6: Index PIP.
- Landmark 7: Index DIP.
- Landmark 8: Index TIP.

Chuyển landmarks từ World Frame sang Root Frame:

\[
P*{root}=(P*{world}-O*{root})R*{root}
\]

Sau đó:

\[
L*{middle} = \|P*{DIP}^{root}-P\_{PIP}^{root}\|\_2
\]

Một phép rigid transformation chỉ quay và tịnh tiến hệ tọa độ nên khoảng cách Euclidean không đổi:

\[
\|P*{DIP}^{world}-P*{PIP}^{world}\|
=
\|P*{DIP}^{root}-P*{PIP}^{root}\|
\]

Root Frame không làm khoảng cách chính xác hơn; nó tạo hệ quy chiếu chung để biểu diễn segments, local frames và kinematic chain.

Đề xuất implementation: thu thập nhiều frame calibration tĩnh và dùng median để giảm ảnh hưởng outlier:

\[
L*{middle} =
\operatorname{median}
\left(
L*{middle}^{(1)},\ldots,L\_{middle}^{(N)}
\right)
\]

Đây là đề xuất triển khai cho MediaPipe, không phải thuật toán được Cerveri mô tả nguyên văn.

## 5. Tranh luận về 1DOF và hướng của segment

**Người dùng:** Đủ rồi — không cần hướng sở dĩ nó là 1DOF.

**Trợ lý:** 1DOF không có nghĩa là không cần hướng. Nó có nghĩa chuyển động tương đối tại khớp chỉ có một biến góc quanh một trục quay đã xác định. Để xác định vị trí đầu xa của segment, vẫn cần biết orientation của segment hoặc trạng thái ban đầu và joint axis.

Ví dụ minh họa:

\[
P*{DIP}=P*{PIP}+R*{middle}
\begin{bmatrix}
0\\L*{middle}\\0
\end{bmatrix}
\]

Trong đó \(R\_{middle}\) là orientation của middle phalanx theo quy ước local frame.

**Người dùng:** Ý là mình thực sự xây dựng chưa á.

**Trợ lý:** Chưa. Tới thời điểm đó, dự án mới có nền tảng và một số phần lý thuyết, chưa có hệ thống Virtual Sensing hoàn chỉnh theo hướng Cerveri.

| Thành phần                     | Trạng thái tại thời điểm trao đổi   |
| ------------------------------ | ----------------------------------- |
| MediaPipe 21 landmarks         | Đã có pipeline streaming            |
| Root Coordinate Frame          | Đã có implementation                |
| World → Root transformation    | Đã có công thức và hướng triển khai |
| Finger Local Coordinate Frames | Chưa hoàn thành                     |
| Anatomical Calibration         | Chưa hoàn thành                     |
| Segment length estimation      | Mới xác định phương pháp            |
| Joint centers / rotation axes  | Chưa hoàn thành                     |
| Geometrical relations          | Chưa implement                      |
| Functional relations           | Mới phân tích DIP–PIP               |
| Forward Kinematics             | Chưa implement                      |
| Occlusion reconstruction       | Chưa implement                      |

Thứ tự phát triển được đề xuất:

1. Virtual Local Frames.
2. Anatomical Calibration.
3. Geometrical Relations.
4. Functional Relations.
5. Forward Kinematics và reconstruction.

## 6. Code VirtualRootFrame hiện tại

Người dùng cung cấp implementation sau:

```python
from typing import Any, Dict, List, Optional

import numpy as np
from mediapipe.tasks.python.components.containers.landmark import (
    Landmark,
)

from src.utils import CfgParse, CrossProduct, Normalize, Projection

from .base import Kinematics


class VirtualRootFrame(Kinematics):
    """
    with `virtual-root-frame`:
    Landmark IDs:
        0  : Wrist
        5  : Index MCP
        9  : Middle MCP
        17 : Pinky MCP

    Convention:
        Origin = centroid of landmarks 0, 5, 9, 17
        Z-axis = Wrist -> Middle MCP
        X-axis = Pinky MCP -> Index MCP,
                 orthogonalized against Z
        Y-axis = Z cross X

    Rotation matrix columns are [X, Y, Z].
    This is a project-specific approximation, not an
    exact reproduction of the physical marker setup.
    """

    def __init__(self, hands_cfg_path: str = "src/kinematics/config/cfg.yaml"):
        self.hands_cfg_path = hands_cfg_path
        self.hands_cfg = CfgParse(path=self.hands_cfg_path).process()

        self.last_valid_state: Optional[Dict[str, Any]] = None

        self.idx_wrist = self.hands_cfg["handmotion"]["wrist"]["wrist"]["index"]
        self.idx_index_mcp = self.hands_cfg["handmotion"]["index_finger"]["mcp"][
            "index"
        ]
        self.idx_middle_mcp = self.hands_cfg["handmotion"]["middle_finger"]["mcp"][
            "index"
        ]
        self.idx_pinky_mcp = self.hands_cfg["handmotion"]["pinky"]["mcp"]["index"]

        self.required_indices = [
            self.idx_wrist,
            self.idx_index_mcp,
            self.idx_middle_mcp,
            self.idx_pinky_mcp,
        ]

    def _get_points(
        self, world_landmarks: List[Landmark], landmark_id: int
    ) -> np.ndarray:
        landmark = world_landmarks[landmark_id]
        if hasattr(landmark, "x"):
            point = np.array([landmark.x, landmark.y, landmark.z], dtype=float)
        else:
            point = np.asarray(landmark, dtype=float)

        if point.shape != (3,):
            raise ValueError("Each landmark must be a 3D point.")

        if not np.all(np.isfinite(point)):
            raise ValueError("Landmark contains invalid values.")

        return point

    def _is_valid_input(self, world_landmarks: Optional[List[Landmark]]) -> bool:
        if world_landmarks is None or len(world_landmarks) == 0:
            return False

        max_idx = max(self.required_indices)

        if len(world_landmarks) <= max_idx:
            return False

        return True

    def process(self, world_landmarks: Optional[List[Landmark]]):
        if not self._is_valid_input(world_landmarks=world_landmarks):
            return self.last_valid_state

        try:
            wrist = self._get_points(
                world_landmarks=world_landmarks, landmark_id=self.idx_wrist
            )

            index_mcp = self._get_points(
                world_landmarks=world_landmarks, landmark_id=self.idx_index_mcp
            )

            middle_mcp = self._get_points(
                world_landmarks=world_landmarks, landmark_id=self.idx_middle_mcp
            )

            pinky_mcp = self._get_points(
                world_landmarks=world_landmarks, landmark_id=self.idx_pinky_mcp
            )

            # 1. Virtual origin
            origin = np.mean([wrist, index_mcp, middle_mcp, pinky_mcp], axis=0)

            # 2. Z-axis: longitudinal direction of the hand
            z_hat = Normalize(middle_mcp - wrist).process()

            # 3. X-axis: across the palm, orthogonal to Z
            x_raw = index_mcp - pinky_mcp

            x_hat = Projection(z_hat, x_raw).process()

            # 4. Y-axis: right-handed normal direction
            y_hat = CrossProduct(z_hat, x_hat).process()

            # Re-orthogonalize X to reduce numerical error
            x_hat = CrossProduct(y_hat, z_hat).process()

            # Rotation matrix: axes are columns
            R = np.column_stack((x_hat, y_hat, z_hat))

            # 5. Validate the rotation matrix
            if not np.allclose(R.T @ R, np.eye(3), atol=1e-6):
                raise ValueError("Root frame is not orthonormal.")

            if not np.isclose(np.linalg.det(R), 1.0, atol=1e-6):
                raise ValueError("Root frame is not right-handed.")

            state = {
                "origin": origin,
                "rotation_matrix": R,
                "x_axis": x_hat,
                "y_axis": y_hat,
                "z_axis": z_hat,
            }
            self.last_valid_state = state
            return state
        except (ValueError, IndexError, TypeError):
            return self.last_valid_state
```

## 7. Đánh giá VirtualRootFrame

Trợ lý đánh giá đây là nền tảng root reference frame hợp lý, nhưng chưa phải Anatomical Calibration.

Các điểm đã có:

- Landmark selection: wrist, index MCP, middle MCP, pinky MCP.
- Origin: centroid của bốn landmarks.
- Z-axis: wrist → middle MCP.
- X-axis: vector ngang lòng bàn tay sau projection trực giao với Z.
- Y-axis: cross product.
- Rotation matrix: các axis được lưu theo columns.
- Có kiểm tra orthonormality và determinant +1.
- Có `last_valid_state` để xử lý frame không hợp lệ.

Với convention columns `[X,Y,Z]`, và dữ liệu landmarks lưu theo từng hàng, phép chuyển World → Root là:

```python
root_points = (world_points - origin) @ R
```

Các điểm cần cải thiện:

1. **Degenerate geometry:** kiểm tra norm trước Normalize và Projection để tránh vector zero hoặc gần zero.
2. **Temporal continuity:** theo dõi dấu/hướng của axes qua các frame để tránh flip đột ngột; cần kiểm thử cẩn thận khi bàn tay đổi tư thế lớn.
3. **Stale state:** nếu trả về `last_valid_state`, cần đánh dấu state là stale/invalid và giữ timestamp để downstream không coi dữ liệu cũ là dữ liệu mới.
4. **Anatomical meaning:** Root Frame chưa xác định PIP/DIP joint centers, rotation axes, segment lengths hoặc marker local coordinates.

## 8. Kiến trúc module đề xuất

```text
kinematics/
│
├── base.py
├── virtual_root_frame.py
├── virtual_local_frame.py
├── anatomical_calibration.py
├── geometrical_constraints.py
├── functional_constraints.py
└── forward_kinematics.py
```

| Module                   | Trách nhiệm                              |
| ------------------------ | ---------------------------------------- |
| `VirtualRootFrame`       | Global hand reference                    |
| `VirtualLocalFrame`      | Local coordinate frames của từng phalanx |
| `AnatomicalCalibration`  | Segment lengths, joint centers, axes     |
| `GeometricalConstraints` | Marker/segment geometric relations       |
| `FunctionalConstraints`  | DOF, joint limits, angular coupling      |
| `ForwardKinematics`      | Reconstruct landmark positions           |

Đây là kiến trúc implementation đề xuất, không phải cấu trúc phần mềm nguyên bản của Cerveri.

## 9. Milestone tiếp theo: Index Finger Anatomical Calibration

Bắt đầu với index finger:

| MediaPipe ID | Anatomical point |
| -----------: | ---------------- |
|            5 | Index MCP        |
|            6 | Index PIP        |
|            7 | Index DIP        |
|            8 | Index TIP        |

Các chiều dài segment được ước lượng từ nhiều frame calibration:

\[
L\_{proximal}=\operatorname{median}(\|P_6-P_5\|)
\]

\[
L\_{middle}=\operatorname{median}(\|P_7-P_6\|)
\]

\[
L\_{distal}=\operatorname{median}(\|P_8-P_7\|)
\]

Các điểm có thể được biểu diễn trong Root Frame để thống nhất hệ tọa độ. Khoảng cách Euclidean không đổi khi chuyển đổi bằng phép rigid transformation.

Đây là ước lượng segment length từ MediaPipe landmarks, không phải phép đo trực tiếp chiều dài xương.

## 10. Câu hỏi/challenge đang chờ trả lời

Giả sử thu thập 100 frames trong tư thế calibration tĩnh. Trong 100 frames:

- MCP, PIP, DIP, TIP đều có tracking noise.
- Chiều dài PIP–DIP dao động nhẹ.
- Root Frame cũng dao động nhẹ theo từng frame.

Có ba phương án:

**A.** Tính từng khoảng cách trong World Frame rồi lấy median.

**B.** Chuyển từng frame sang Root Frame, tính khoảng cách rồi lấy median.

**C.** Lấy trung bình tọa độ từng landmark qua 100 frames trước, sau đó mới tính khoảng cách.

Người học cần chọn và giải thích ảnh hưởng của noise và calibration trước khi viết `AnatomicalCalibration.py`.

---

## 11. Nguyên tắc làm việc tiếp theo

- Không giản lược Cerveri thành chỉ dựng rotation matrices.
- Phân biệt rõ geometrical relations và functional relations.
- Phân biệt thông tin được paper hỗ trợ với adaptation/implementation decision cho MediaPipe.
- Phát triển từng bước, bắt đầu với Index Finger.
- Không viết lại `VirtualRootFrame`; xây dựng các module tiếp theo tương thích với output hiện tại.
- Người học muốn được challenge và tự suy luận trước khi nhận lời giải đầy đủ.
