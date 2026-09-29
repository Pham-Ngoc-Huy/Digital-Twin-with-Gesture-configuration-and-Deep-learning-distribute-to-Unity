# Day 5

## Objective:

Ứng dụng Cerveri model để phát triển Virtual Sensor và thực hiện programming

Trả lời được câu hỏi
> Từ mediapipe 21 landmarks $\rightarrow$ làm thế nào để lấy được joint angles $\rightarrow$ đưa ra joint angles vào một kinematic hand model

## Processing:

### Part 1: Container "Cerveri model"

từ paper của Cerveri, có kết luận rằng:

hand = hierarchical rigid-body system

Mỗi anatomical distinct có:
- vị trí
- orientation
- hirerachy
- marker positions
- kinematic variables
- geometric properties

**Ví dụ**: với 1 ngón tay

```mermaid
flowchart TD
id1[Palm] --> id2[MCP]
id2 --> id3[Proximal phalanx]
id3 --> id4[PIP]
id4 --> id5[DIP]
id5 --> id6[Distal phalanx]
```

> [!Note]:
> Trong mô hình 21 điểm (landmarks) chuẩn của `MediaPipe`, lòng bàn tay không phải là 1 điểm đơn lẻ, mà là **mặt phẳng cơ sở (palm landmarks)** được tạo bởi các điểm gốc

### Bài toán cơ sở:

Ta lấy: `PIP Joint`

Ví dụ index finger

```mermaid
flowchart LR
id1[MCP] --> id2[PIP] 
id2 --> id3[DIP] 
id3 --> id4[TIP]
```

ta đang muốn tìm 

```math
\theta_{PIP}
```
Cerveri biểu diễn 1-DoF rotation bằng rotation matrix quanh một local axis. Paper đang viết marker relation dưới dạng:

```math
P_{p} = R_{1DoF}(X,\alpha) P_{t}

```
và sau đó expand rotation matrix để tìm $\alpha$

> Điều này khá thuận lợi khi áp dụng `MediaPipe` khi đó chúng ta đã có trực tiếp 3D coordinates của các landmarks. Implement bước đầu sẽ dễ hơn

### Cerveri cần trong coordinate system.

Nếu chỉ dùng:

```math
MCP \rightarrow PIP \\
PIP \rightarrow DIP
```

thì mình chỉ đang biết **hai bone đang tạo với nhau bao nhiêu góc.**

```math
\overrightarrow{PIP\rightarrow DIP} \\
\\
\text{hay} \\
\\
\overrightarrow{DIP\rightarrow PIP} 
```

>[!NOTE] 
>
> Công thức thông thường xử lí:
>
> ```math
>  \theta = \cos^{-1}
>  \left(\frac{\vec{v_1} \cdot \vec{v_2}}{|\vec{v_1}| |\vec{v_2}|}\right)
>
> ```

nhưng mình không biết đó là

> nó đang là `flexion` hay đang `abduct`?

$\rightarrow$ Cerveri xây dựng `local coordinate system` cho từng **anatomical district**. Paper mô tả các coordinate axes được xác định từ **marker geometry** và dùng chúng để biểu diễn motion của từng segment.

_Ví dụ_:

```bash
            Y
            |
            |
            |
MCP ------- PIP
 \
  \ 
   DIP
```

Ta cần định nghĩa:

```bash
local X = flexion axis
local Z = another anatomical axis
local Y = remaining orthogonal axis
```

Sau đó rotation trở thành:

```math

R(X, \theta)
```

Where:

$X$: là local rotation axis
$\theta$: là rotation angle quanh axis đó 

hoặc với joint 2-DoF:

```math
R(X, \alpha) R(Z, \beta)
```
Where:

$\alpha$: flexion rotation angle
$\beta$: abduction rotation angle
$X$: intersect axes
$Z$: orthogonal axes

Nói cách khác:

```mermaid

flowchart TD
    %% Luồng cơ bản (chưa đủ)
    A(Bone geometry) --> B(angle giữa 2 bones)
    B --> C[❌ chưa đủ]
    
    %% Chuyển hướng sang Cerveri
    C -.-> |"Giải pháp: Cerveri"| D
    
    %% Luồng của Cerveri
    subgraph Cerveri [Phương pháp Cerveri]
        direction TB
        D[reference/local frame] -- "+" --> E[rotation axis X]
        E -- "+" --> F[segment transformation]
        F --> |"="| G((α = joint motion))
    end
    
    %% Style để sơ đồ dễ nhìn hơn
    style C fill:#ffe6e6,stroke:#ff6666,stroke-width:2px,color:#cc0000
    style G fill:#e6ffe6,stroke:#66cc66,stroke-width:2px
    style Cerveri fill:#f9f9f9,stroke:#333,stroke-dasharray: 5 5

```