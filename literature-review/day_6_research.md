# REVIEW — Virtual Root Frame & Stability

## 1. Tại sao không lấy trực tiếp Index MCP - Pinky MCP làm X-axis?

Câu trả lời của bạn: Vì chưa chắc vector này vuông góc với Z-axis nên cần Projection.

Đúng

Giải thích:

Ta có hai vector:

\\[ z\_{raw}=P\_{middle}-P\_{wrist} \\]

\\[ x\_{raw}=P\_{index}-P\_{pinky} \\]

Hai vector này không đảm bảo vuông góc với nhau.

Do đó, ta sử dụng Gram–Schmidt để loại bỏ thành phần của \\(x\_{raw}\\) song song với Z-axis:

\\[ x\_{\perp}=x\_{raw}-(x\_{raw}\cdot\hat z)\hat z \\]

Sau đó chuẩn hóa:

\\[ \hat x=\frac{x\_{\perp}}{\\|x\_{\perp}\\|} \\]

Điều cần nhớ:

- Projection: lấy thành phần song song với base vector.
- Subtraction: loại bỏ thành phần song song.
- Normalize: biến residual thành vector đơn vị.

## 2. Projection trả về vector vuông góc hay song song với base vector?

Câu trả lời ban đầu của bạn: Projection trả về vector vuông góc với base.

Cần sửa lại

Câu trả lời chính xác:

Projection trả về vector song song với base vector.

\\[ \operatorname{proj}\_{z}(x) = (x\cdot z)z \\]

Vector vuông góc được tạo ra sau khi trừ projection:

\\[ x\_{\perp}=x-\operatorname{proj}\_{z}(x) \\]

Đây là điểm rất quan trọng vì nó chính là nền tảng của thuật toán Gram–Schmidt.

## 3. Điều gì xảy ra nếu X-axis ban đầu song song với Z-axis?

Giả sử:

\\[ x\_{raw}=3\hat z \\]

Câu hỏi: Projection trả về gì?

Đáp án:

\\[ \operatorname{proj}\_{z}(x\_{raw})=3\hat z \\]

Câu hỏi: Residual sau khi trừ projection bằng bao nhiêu?

\\[ x\_{\perp}=3\hat z-3\hat z=0 \\]

Câu hỏi: Điều gì xảy ra khi Normalize vector zero?

\\[ \operatorname{Normalize}(0)=\frac{0}{0} \\]

Phép toán không xác định.

Bạn đã hiểu sau khi được gợi ý

Bài học: Phải kiểm tra norm của residual trước khi Normalize.

## 4. Nếu Index MCP và Pinky MCP gần song song với Wrist → Middle MCP thì sao?

Bạn đã chọn A: Root Frame vẫn xác định được bình thường.

Sai

Đáp án đúng: B — Root Frame trở nên không ổn định.

Có hai trường hợp:

| Trường hợp                     | Kết quả                                             |
| ------------------------------ | --------------------------------------------------- |
| Hai vector song song hoàn toàn | Residual bằng 0, không xác định được X-axis         |
| Hai vector gần song song       | Residual rất nhỏ, Normalize có thể khuếch đại nhiễu |

Đặc biệt, trường hợp thứ hai rất nguy hiểm trong real-time tracking.

Một thay đổi nhỏ của landmark có thể khiến orientation thay đổi mạnh giữa các frame.

## 5. Nếu Projection bị suy biến, hệ thống nên xử lý thế nào?

Bạn chọn:

2\. Giữ lại rotation matrix hợp lệ từ frame trước.

Lựa chọn hợp lý

Ta có:

\\[ R_t=R\_{t-1} \\]

Thay vì cố tạo một rotation matrix từ dữ liệu không đáng tin cậy, hệ thống giữ orientation gần nhất đã được xác nhận hợp lệ.

Khái niệm cần nhớ:

Temporal Consistency

Đảm bảo orientation của Digital Twin không nhảy bất thường giữa các frame do nhiễu tracking.

Trade-off:

- Ưu điểm: ổn định.
- Nhược điểm: orientation có thể không còn phản ánh chuyển động hiện tại.

## 6. Nếu không detect được hand landmarks thì sao?

Bạn trả lời rằng hệ thống không thể tính toán và buộc phải giữ trạng thái để ổn định.

Đúng về hướng xử lý

Khi không có landmarks:

\\[ O_t,\ R_t \\]

không thể được tính từ dữ liệu frame hiện tại.

Một giải pháp là:

\\[ O_t=O\_{t-1} \\]

\\[ R_t=R\_{t-1} \\]

Nhưng cần phân biệt:

| Trạng thái | Ý nghĩa                                               |
| ---------- | ----------------------------------------------------- |
| TRACKING   | Detect được và dữ liệu hợp lệ                         |
| DEGRADED   | Detect được nhưng một phần dữ liệu không đáng tin cậy |
| LOST       | Không detect được bàn tay                             |

Lưu ý: Đây là đề xuất kiến trúc của chúng ta, không phải ba trạng thái được xác định bởi paper Cerveri.

## 7. Khi tracking mất rồi xuất hiện lại, Digital Twin nên làm gì?

Đây là câu hỏi cuối cùng mình đưa ra, bạn chưa trả lời.

Giả sử:

- Frame 1–100: tracking bình thường.
- Frame 101–110: mất tracking.
- Frame 111: tracking xuất hiện trở lại.

Có ba phương án:

| Phương án | Cách hoạt động                                         | Trade-off                                           |
| --------- | ------------------------------------------------------ | --------------------------------------------------- |
| A         | Nhảy ngay đến vị trí mới                               | Responsive nhưng có thể giật                        |
| B         | Interpolation từ vị trí cũ đến vị trí mới              | Mượt hơn nhưng có thể tạo chuyển động không thực tế |
| C         | Chờ tracking ổn định qua một số frame rồi mới cập nhật | Chắc chắn hơn nhưng tăng latency                    |

Câu trả lời hợp lý: Không có một lựa chọn luôn đúng cho mọi hệ thống.

Với prototype hiện tại, mình khuyến nghị C: xác nhận tracking hợp lệ qua một số frame liên tiếp, sau đó cập nhật trạng thái. Có thể kết hợp interpolation nếu cần giảm cảm giác giật.

Đây là quyết định thiết kế kỹ thuật, không phải kết luận từ hai paper.

# Tổng kết kiến thức hôm nay

## Virtual Root Frame

1. Vector operations: Normalize, Dot Product, Cross Product.
2. Projection: Tách thành phần song song và vuông góc.
3. Gram–Schmidt: Xây dựng các vector trực chuẩn.
4. Rotation Matrix: Xây dựng hệ trục tọa độ 3D.
5. Degenerate case: Phát hiện trường hợp không thể xác định orientation.
6. Temporal consistency: Giữ orientation hợp lệ từ frame trước.
7. Tracking state management: Phân biệt TRACKING, DEGRADED và LOST.
