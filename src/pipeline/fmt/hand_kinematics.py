from tabulate import tabulate

def fmt_vec(vec, precision=4):
    vals = ", ".join(f"{x:>{precision+4}.{precision}f}" for x in vec)
    return f"[{vals}]"

def print_hand_kinematics(hand_dict, precision=4):
    # 1. Points & Geometry Vectors
    geom_headers = ["Finger", "Joint / Segment", "Point (x, y, z)", "Segment Vector (x, y, z)", "Valid"]
    geom_rows = []
    seg_map = [("mcp", "proximal_vector"), ("pip", "intermediate_vector"), ("dip", "distal_vector"), ("tip", None)]
    
    for finger, content in hand_dict.items():
        pts = content["points"]
        geom = content["geometry"]
        for i, (pt_key, vec_key) in enumerate(seg_map):
            vec_str = fmt_vec(geom[vec_key]["vector"], precision) if vec_key else "-"
            valid_str = str(bool(geom[vec_key]["is_valid"])) if vec_key else "-"
            geom_rows.append([
                finger.upper() if i == 0 else "",
                pt_key.upper(),
                fmt_vec(pts[pt_key], precision),
                vec_str,
                valid_str
            ])
            
    print("=== Points-and-Geometry-Vectors ===")
    print(tabulate(geom_rows, headers=geom_headers, tablefmt="pretty"))

    # 2. Local Coordinate Frames (X, Y, Z axes form the columns of rotation_matrix)
    frame_headers = ["Finger", "Phalanx", "Valid", "X Axis (x, y, z)", "Y Axis (x, y, z)", "Z Axis (x, y, z)"]
    frame_rows = []
    
    for finger, content in hand_dict.items():
        for i, (phalanx, frame) in enumerate(content["local_frames"].items()):
            frame_rows.append([
                finger.upper() if i == 0 else "",
                phalanx,
                bool(frame["is_valid"]),
                fmt_vec(frame["x_axis"], precision),
                fmt_vec(frame["y_axis"], precision),
                fmt_vec(frame["z_axis"], precision)
            ])
            
    print("\n=== Local-Frames-(Axes) ===")
    print(tabulate(frame_rows, headers=frame_headers, tablefmt="pretty"))