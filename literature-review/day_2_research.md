# Day2:

Content:

- Tại sao lại cần flexible beam ?
- Equation (1) thực sự đang nói gì?
- Forward kinematics và inverse kinematics nằm ở đâu trong pipeline?
- Tại sao sensing glove có thể biến deformation của beam thành joint angles của ngón tay?

## 1. Look-back:

**Equation(1):**

paper viết:

```math

g_{st,f}(\alpha_1,\alpha_2,\alpha_3,\alpha_4) = g_t = g_{st,b}(\phi_1,\phi_2,\phi_3,\phi_4)

```

> Beam tip và Finger tip đang bị ràng buộc cùng pose

```bash
Human finger
   │
   │ α1 α2 α3
   ▼
Finger kinematics
   │
   ▼
Finger tip pose
       ║
       ║  same physical tip
       ║
       ▼
Beam tip pose
   │
   │ φ1 φ2 φ3 φ4
   ▼
Flexible beam deformation
```

**Finger model:**

Paper đang giả sử mỗi ngón tay có 3 joints:

- PIP
- MCP
- DIP

và mỗi joint được giới hạn thành 1-DOF Hinge

Do đó finger được mô hình hoá thành 3-DOF serial linkage với 3 revoluate-joint

```math
\alpha =

\begin{bmatrix}
\alpha_1 \\
\alpha_2 \\
\alpha_3
\end{bmatrix}

```

và đây chính là `joint variables`

**Forward Kinematics:**

```math

(\alpha_1, \alpha_2, \alpha_3) \rightarrow g_{st, f}
```

và paper biểu diễn điều này lại bằng POE (product of exponental)

```math
g_{st,f} = e^{\hat{\eta_1}\alpha_1} e^{\hat{\eta_2}\alpha_2} e^{\hat{\eta_3}\alpha_3} g_{st,f_0}
```

---

**Sensing:**

với sensing thì ta cần đi ngược lại:

Khi dùng glove, ta **không trực tiếp biết**

$\alpha_1, \alpha_2, \alpha_3$

Ta chỉ đo được deformation của beam

$\phi_1, \phi_2, \phi_3, \phi_4$

Vậy phải làm

$\phi \rightarrow g_t \rightarrow \alpha$

Bước này gọi là **Inverse Kinematics**

```math
[\alpha_1, \alpha_2, \alpha_3]^T = g_{st,f}^{-1} \cdot g_{st, b}(\phi_1, \phi_2, \phi_3, \phi_4)
```

## 2. Explore Day-2:

### 1. Equation (4): (Biến đổi flexible beam thành serial mechanism)

```math

g_{st,b}(\theta) = e^{\hat{\eta_1}\theta_1} ... e^{\hat{\eta_n}\theta_n} g_{st, b_0}
```

Intuition:

Hiểu đơn giản trên công thức này thì mình back lại cái hình:

```bash
Initial:

───────────────→ x
●────●────●────●


Deformed:

      ╭────
   ╭──╯
●──╯
```

Thì workflow sẽ như thế này đây:

```mermaid
flowchart TD
A[Flexible beam] --> B[chia thành nhiều segment]
B --> C[mỗi segment ≈ một rigid link]
C --> D[giữa các link có elastic joint]
D --> E[θ1, θ2, ..., θn]
E --> F[mô hình hóa deformation của beam]
```

**Ngoài ra:**

Joint variables không chỉ là thoả các điều kiện về góc xoay giữa cái serial linkage mechanism, mà còn phải thoả mãn về `static equilibrium`

> [!NOTE] > **tóm tắt**
>
> nói đại khái là:
>
> Khi flexible beam bị biến dạng, các elastic joints sinh ra restoring torque. Ở trạng thái cân bằng tĩnh, restoring torque này phải cân bằng với torque do external wrench tác dụng lên fingertip.

### 2. Equation 4 - 5:

---

Trước khi vào phần này:

Để thống nhất concept - thì pipeline chuyển đổi lúc này là: **(SENSING)**

```math
\phi \rightarrow \theta \rightarrow g_{t} \rightarrow \alpha

```

thì từ $\phi \rightarrow \theta$ phải thoả mãn sensors constraint + static equalibrium

Phân biệt:
| kí hiệu | ý nghĩa |
|---------|---------|
| $\phi$ | local defections do sensors đo |
| $\alpha$ | joint angles của human finger |
| $\theta$ | joint variables của equivalent flexible beam mechanism |

> [!NOTE]:
> 3 cái này khác nhau hoàn toàn không có lẫn lộn

---

theo paper:

**Equation(4): sensors constraint** (where $p$: $\text{local defection constraint}$)

```math

p = S_e \theta - \Phi = 0

```

với

- $\Phi = [\phi_1, \phi_2, \phi_3, \phi_4]^T$: sensed local curvatures
- $\theta$ (nx1): joint variable of equivalent linkage
- $S_e$: 4x1: Sensor location matrix (đang sử dụng 4 sensors)
  > Nghĩa là 4 sensor measurements đang đặt constraint lên trạng thái deformation $\theta$ của toàn bộ beam

**Equation(5): Static Equilibrium**

```math
\tau = K_{\theta} \theta - J^{T}_{t} F_{t} = 0
```

công thức này nghĩa là:

> Trong không gian khớp, mô-men phục hồi của các khớp đần hồi phải được cân bằng bởi phản lực của ngoại lực tác động lên đầu ngón tay.

- $K_{\theta}$ = $diag(k_1, ... k_n)$ $ \in R^{nxn}$: represents the diagonal stiffness matrix of the elastic joint which are determined by the beam's mechanical properties
- $F_t \in R^{6x1}$: denotes the external wrench (mô-men ngoại lực) applied by finger tip at {T}, which generates the forced deflection of the flexible beam.
- $J_t \in R^{6xn}$: is the Jacobian matrix relating the joint space to the tip frame

Để mà giải thích dễ hiểu hơn thì

- $K_{\theta}$: beam/elastic joint này cứng đến mức nào?

- $\theta$: beam/elastic joint này đã biến dạng bao nhiêu?

thì $\rightarrow$ $K_{\theta}$ $\cdot$ $\theta$: = độ cứng x độ biến dạng = elastic restoring torque

> Hay đơn giản dễ hiểu hơn là torque của spring sinh ra để chống lại biến dạng

Trong cùng ngữ cảnh, nếu beam đang bị cong thì elastic deformation tạo ra 1 torque:

```math
K_{\theta} \cdot \theta
```

**Tại sao $F_{t}$ lại là unknown ?**

Paper viết:

```math
K_{\theta} \theta - J^{T}_{t} F_{t} = 0
```

Trong đó $J_{t}$ là **Jacobian** tại tip của equivalent beam mechanism

> $J_t$: biến đổi joint motion $\rightarrow$ tip motion

Ví dụ:

```math
\dot{x} = J_{t} \dot{\theta}

```

Nghĩa là nếu các elastic joints thay đổi một chút $\dot{\theta}$ thì tip sẽ chuyển động $\dot{x}$

Trong trường hợp này thì mình đang đi ngược chiều:

Ở paper đang xét force tại tip

Một lực $F_{t}$ tác dụng ở tip sẽ tạo ra torque lên các joints

Vậy -> để chuyển ---> tip force -> joint torque

thì dùng:

```math
\tau = J^{T}_{t} F_{t}
```

đó là lý do có **transpose**

Hãy tưởng tượng một thanh đơn giản

```mermaid
flowchart LR
   subgraph Ngang [ ]
      A[joint] --> B[tip]
   end
   B --> C[F]
```

Lực \(F\) ở tip tạo moment quanh joint:

$$ \tau = rF $$

Nếu khoảng cách \(r\) lớn → torque lớn.

Jacobian chính là thứ encode hình học/mechanical advantage giữa joint và tip.

Với nhiều joints:

$$ F_t \overset{J_t^T}{\longrightarrow} \tau $$

nên:

```math
\boxed{J_t^TF_t}
```

là **generalized torque do external wrench** tại tip gây ra trên các elastic joints.

### Q: Why do you need the static equilibrium equation ?

> **Answer:** Because the deformation of the flexible beam is not determined only by the target fingertip pose. The deformation generates elastic restoring torques, which must be balanced by the torque induced by the external wrench at the fingertip. Therefore, the geometric constraint and static equilibrium must be solved simultaneously.
