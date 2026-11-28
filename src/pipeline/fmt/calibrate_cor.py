from tabulate import tabulate

def print_calibrate_cor_tabulate(cor_dict, precision=4):
    headers = ["Finger", "Joint", "Valid", "Sign", "Origin (x, y, z)", "Offset Vector (x, y, z)"]
    rows = []

    print("\n=== Calibration-Center-Of-Rotation ===")
    for finger, joints in cor_dict.items():
        for i, (joint, vals) in enumerate(joints.items()):
            orig = ", ".join(f"{x:>{precision+4}.{precision}f}" for x in vals['origin'])
            off = ", ".join(f"{x:>{precision+4}.{precision}f}" for x in vals['offset_vector'])
            
            rows.append([
                finger.upper() if i == 0 else "",  # Show finger name once per group
                joint,
                vals['is_valid'],
                vals['sign'],
                f"[{orig}]",
                f"[{off}]"
            ])
            
    print(tabulate(rows, headers=headers, tablefmt="pretty"))