from os import PathLike
from pathlib import Path

import numpy as np

from src.pipeline import PipeLineOneFrame

_FINGER_ORDER = ("wrist", "thumb", "index", "middle", "ring", "pinky")


def load_world_landmarks(
    landmark_path: str | PathLike[str],
    hand: str = "Left",
) -> np.ndarray:
    """Load landmarks and return MediaPipe-style (21, 3) array."""

    data = np.load(landmark_path, allow_pickle=True)

    if isinstance(data, np.ndarray) and data.dtype == object:
        data = data.item()

    if isinstance(data, dict):
        if hand not in data:
            available = ", ".join(sorted(data)) or "none"
            raise KeyError(f"Hand {hand!r} not found. Available hands: {available}")

        hand_data = data[hand]

        points = [np.asarray(hand_data["wrist"], dtype=float).reshape(1, 3)]

        for finger in _FINGER_ORDER[1:]:
            points.append(np.asarray(hand_data[finger], dtype=float))

        world_landmarks = np.vstack(points)

    else:
        world_landmarks = np.asarray(data, dtype=float)

    if world_landmarks.shape != (21, 3):
        raise ValueError(f"Expected (21, 3), got {world_landmarks.shape}")

    if not np.isfinite(world_landmarks).all():
        raise ValueError("Landmarks contain NaN or Inf values.")

    return world_landmarks


def validate_rotation_matrix(R, tolerance=1e-6):
    """Validate orthogonality and proper rotation."""

    R = np.asarray(R, dtype=float)

    if R.shape != (3, 3) or not np.isfinite(R).all():
        return {
            "orthogonality_error": np.inf,
            "determinant": np.nan,
            "is_orthogonal": False,
            "is_proper_rotation": False,
            "is_valid": False,
        }

    identity = np.eye(3)

    orthogonality_error = np.linalg.norm(R.T @ R - identity)

    determinant = np.linalg.det(R)

    is_orthogonal = orthogonality_error < tolerance
    is_proper_rotation = abs(determinant - 1.0) < tolerance

    return {
        "orthogonality_error": orthogonality_error,
        "determinant": determinant,
        "is_orthogonal": is_orthogonal,
        "is_proper_rotation": is_proper_rotation,
        "is_valid": is_orthogonal and is_proper_rotation,
    }


def print_rotation_validation(name, R):
    validation = validate_rotation_matrix(R)

    print(f"\n[{name}]")
    print(f"Orthogonality error : {validation['orthogonality_error']:.2e}")
    print(f"Determinant         : {validation['determinant']:.6f}")
    print(f"Orthogonal          : {validation['is_orthogonal']}")
    print(f"Proper rotation     : {validation['is_proper_rotation']}")
    print(f"Overall             : {validation['is_valid']}")

    return validation["is_valid"]


def validate_pipeline_result(result):
    print("\n" + "=" * 65)
    print("ROTATION MATRIX VALIDATION")
    print("=" * 65)

    validation_results = {}

    # 1. Root frame
    root_state = result["root"]

    validation_results["root"] = print_rotation_validation(
        "ROOT FRAME",
        root_state["rotation_matrix"],
    )

    # 2. Local frames
    local_state = result["local"]

    for finger_name, finger_data in local_state.items():
        print(f"\n--- {finger_name.upper()} ---")

        for frame_name, frame_data in finger_data["local_frames"].items():
            if not frame_data["is_valid"]:
                print(f"\n[{frame_name.upper()}] INVALID / SKIPPED")
                validation_results[f"{finger_name}_{frame_name}"] = False
                continue

            validation_results[f"{finger_name}_{frame_name}"] = (
                print_rotation_validation(
                    f"{finger_name.upper()} - {frame_name.upper()}",
                    frame_data["rotation_matrix"],
                )
            )

    # 3. Summary
    passed = sum(validation_results.values())
    total = len(validation_results)

    print("\n" + "=" * 65)
    print(f"VALIDATION SUMMARY: {passed}/{total} PASSED")
    print("=" * 65)

    return validation_results


def main():
    landmark_path = Path("src/data/landmarks/T01-open-palm.npy")

    hands_cfg_path = "src/kinematics/config/cfg.yaml"

    # Step 1: Load landmarks
    world_landmarks = load_world_landmarks(
        landmark_path=landmark_path,
        hand="Left",
    )

    print(f"Loaded: {landmark_path.name}")
    print(f"Landmark shape: {world_landmarks.shape}")

    # Step 2: Initialize pipeline
    pipeline = PipeLineOneFrame(hands_cfg_path=hands_cfg_path)

    # Step 3: Run kinematics
    result = pipeline.run(landmark_path=world_landmarks)

    # Step 4: Validate rotation matrices
    validation_results = validate_pipeline_result(result)

    return result, validation_results


if __name__ == "__main__":
    main()
