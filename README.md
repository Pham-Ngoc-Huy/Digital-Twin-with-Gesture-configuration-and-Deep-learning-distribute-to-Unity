## Project details:

> ![INFO]
>
> **Project name:** Real-time Hand-Gesture Tracking and Control
>
> **Techique:** Digital-twin
> 
> **Author:** Jedi (Pham Ngoc Huy)
>
> **Major**: Electrical Computer Engineer

_**Tech-stacks**_: 
 - MediaPipe, CV2
 - Deep Learning (MLP - with `n` hidden layers)
 - Python
 - Unity (3D Sketch Model)
 - Matlab/C++ (Controlling Theory and Signal Monitoring)
 - ROS2 (Model deployment)

## Workflow-expectation:
```mermaid
sequenceDiagram
    autonumber
    participant Cam as Video Camera
    participant MP as MediaPipe Node
    participant Bio as Biomechanical Engine
    participant MAT as MATLAB Controller
    participant ROS as ROS 2 Middleware
    participant Unity as Unity Digital Twin

    Cam->>MP: Push RGB Frame (~16ms)
    MP->>Bio: Extract 21 Landmarks (x, y, z)
    Note over Bio: Apply Joint Limits &<br/>Biomechanical Constraints
    Bio->>MAT: Validated Joint Vector ($Q_{valid}$)
    Note over MAT: Run EKF & Trajectory<br/>Smoothing Filter
    MAT->>ROS: Publish to /joint_states
    ROS->>Unity: Receive Joint Command
    Unity->>Unity: PhysX Kinematic Update & Render
    Unity-->>MAT: (Optional) Send Trajectory Lag & Position Error
```

TBC
--

