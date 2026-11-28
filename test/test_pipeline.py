import numpy as np
from omegaconf import OmegaConf

from src.pipeline import HandProcessor, PipeLineOneFrame

CFG_PATH = "src/process/config/cfg.yaml"

def valid_landmarks():
    points = np.zeros((21, 3), dtype=float)

    points[0] = [0.0, 0.0, 0.0]

    points[1] = [-0.2, 0.1, 0.0]
    points[2] = [-0.4, 0.2, 0.0]
    points[3] = [-0.5, 0.4, 0.1]
    points[4] = [-0.6, 0.5, 0.2]

    points[5] = [0.1, 0.2, 0.0]
    points[6] = [0.1, 0.4, 0.0]
    points[7] = [0.2, 0.6, 0.1]
    points[8] = [0.3, 0.8, 0.2]

    points[9] = [0.0, 0.2, 0.0]
    points[10] = [0.0, 0.5, 0.0]
    points[11] = [0.1, 0.7, 0.1]
    points[12] = [0.2, 0.9, 0.2]

    points[13] = [-0.1, 0.2, 0.0]
    points[14] = [-0.1, 0.4, 0.0]
    points[15] = [-0.2, 0.6, 0.1]
    points[16] = [-0.3, 0.8, 0.2]

    points[17] = [-0.2, 0.15, 0.0]
    points[18] = [-0.3, 0.35, 0.0]
    points[19] = [-0.4, 0.5, 0.1]
    points[20] = [-0.5, 0.65, 0.2]

    return points


def test_hand_processor_builds_root_and_local_frames():
    state = HandProcessor(hands_cfg_path=CFG_PATH).process(valid_landmarks())

    assert set(state) == {"root", "local", "calibration"}
    assert state["root"]["rotation_matrix"].shape == (3, 3)
    assert set(state["local"]) == {"index", "middle", "ring", "pinky"}
    assert set(state["local"]["index"]["local_frames"]) == {
        "proximal",
        "intermediate",
        "distal",
    }


def test_calibration_is_skipped_when_not_configured():
    state = HandProcessor(hands_cfg_path=CFG_PATH).process(valid_landmarks())

    assert state["calibration"] is None


def test_calibration_is_applied_when_configured(tmp_path):
    cfg = OmegaConf.load(CFG_PATH)
    cfg.calibration.epsilon = 1e-6
    for finger in ("index", "middle", "ring", "pinky"):
        for joint in ("mcp", "pip", "dip"):
            cfg.calibration.joint_thickness[finger][joint] = 0.012

    cfg_path = tmp_path / "cfg.yaml"
    OmegaConf.save(cfg, cfg_path)

    state = HandProcessor(hands_cfg_path=str(cfg_path)).process(valid_landmarks())

    calibrated = state["calibration"]
    assert set(calibrated) == {"index", "middle", "ring", "pinky"}

    for finger in calibrated.values():
        assert set(finger) == {"proximal", "intermediate", "distal"}
        for frame in finger.values():
            assert frame["is_valid"]
            assert np.asarray(frame["origin"]).shape == (3,)
            assert np.asarray(frame["offset_vector"]).shape == (3,)


def test_one_frame_pipeline_returns_all_stages():
    pipeline = PipeLineOneFrame(hands_cfg_path=CFG_PATH)

    state = pipeline.run(valid_landmarks())

    assert set(state) == {"root", "local", "calibration"}
