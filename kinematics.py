import numpy as np

def vector_between(p1, p2):
    """vector pointing from p1 to p2"""
    return np.array(p2, dtype=float) - np.array(p1, dtype=float)


def angle_between(v1, v2):
    """calculate the angle between 2 vectors in degree"""

    v1 = np.array(v1, dtype=float)
    v2 = np.array(v2, dtype=float)

    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    if v1_norm == 0 or v2_norm == 0:
        raise ValueError("cannot calculate angle between zero-length vector")

    cos_theta = np.dot(v1, v2) / (v1_norm * v2_norm)
    
    # protect again numerical errors
    cos_theta = np.clip(cos_theta, -1.0, 1.0)

    # this is for changing from rad to degree
    theta = np.arccos(cos_theta)
    
    return np.degrees(theta)