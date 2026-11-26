Cụ thể có 6 lý do:
1. Khác biệt về phương pháp thu thập dữ liệu
- Cerveri: Sử dụng hệ thống multi-camera và 24 surface markers được gắn lên bàn tay.
- Project chúng ta: Sử dụng 21 landmarks được Google MediaPipe phát hiện.
- Hai hệ thống có cách biểu diễn và vị trí điểm đo khác nhau.
- Vì vậy, không thể mặc định rằng mỗi MediaPipe landmark tương đương trực tiếp với một physical marker của Cerveri. finger-kinematic-modeling-and-real-time-hand-motion-estimation.pdf
2. Khác biệt về thông tin giải phẫu có thể thu thập
- Cerveri sử dụng các marker được bố trí có chủ đích để xác định vị trí CoR và hướng AoR.
- Họ còn sử dụng anthropometric measurements và geometric constraints trong calibration.
- MediaPipe cung cấp landmark coordinates, nhưng không trực tiếp cung cấp:
  - Anatomical Center of Rotation (CoR).
  - Anatomical Axis of Rotation (AoR).
  - Joint thickness.
  - Vị trí chính xác của các trục xoay giải phẫu.
Do đó, chúng ta phải xây dựng phương pháp suy luận hoặc xấp xỉ các thông số này từ dữ liệu sẵn có. finger-kinematic-modeling-and-real-time-hand-motion-estimation.pdf

3. Khác biệt về quy trình calibration
- Cerveri thực hiện calibration từ một static reference posture có kiểm soát.
- Các marker được sử dụng để xác định Root, hand coordinate frame, CoR và AoR.
- Chúng ta có dataset gồm 8 điều kiện chụp tĩnh, không có continuous motion sequence trong thư mục videos.
- Vì vậy, không thể mặc định áp dụng nguyên vẹn các phương pháp cần chuỗi chuyển động để ước lượng trục hoặc tâm xoay.
Đặc biệt, paper còn đề cập dynamic calibration như một hướng phát triển trong tương lai để cải thiện việc ước lượng AoR và CoR. finger-kinematic-modeling-and-real-time-hand-motion-estimation.pdf

4. Không thể sao chép nguyên vẹn hệ tọa độ của Cerveri
- Cerveri xây dựng Root Frame dựa trên một rigid structure gồm 4 wrist markers.
- Chúng ta không có rigid structure đó.
- Chúng ta đã tự xây dựng Virtual Root Frame từ MediaPipe landmarks.
- Vì vậy, các local coordinate frames phía sau phải nhất quán với Root Frame của chúng ta, thay vì sao chép nguyên hệ tọa độ của Cerveri.
5. Phải điều chỉnh mô hình theo khả năng của MediaPipe
- Cerveri sử dụng hierarchical rigid-body hand model.
- Chúng ta có thể kế thừa nguyên lý phân cấp này.
- Tuy nhiên, các giả định về joint DoFs, joint axes và anatomical constraints cần được kiểm tra lại khi áp dụng với MediaPipe.
- Ví dụ, quan hệ \(\theta_{DIP}=\frac{2}{3}\theta_{PIP}\) trong mô hình Cerveri là một constraint được sử dụng trong phương pháp của họ, không nên mặc định đó là quy luật chính xác cho mọi dữ liệu MediaPipe. finger-kinematic-modeling-and-real-time-hand-motion-estimation.pdf
6. Mục tiêu của project khác với mục tiêu thực nghiệm của Cerveri
- Cerveri hướng đến quantitative biomechanical analysis và real-time hand motion estimation.
- Project chúng ta hướng đến việc sử dụng MediaPipe như virtual sensors, ước lượng joint angles và điều khiển mô hình robotic hand thông qua ROS2 và Unity.
- Vì vậy, chúng ta cần một anatomical model đủ hợp lý để hỗ trợ joint angle estimation và hand motion reconstruction.
- Không nhất thiết phải tái tạo toàn bộ hệ thống đo lường, marker protocol và calibration pipeline của Cerveri.