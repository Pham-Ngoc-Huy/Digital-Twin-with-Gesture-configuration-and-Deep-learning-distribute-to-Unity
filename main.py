from src.pipeline import PipeLine


def main():
    num_hands = 1
    hands_cfg_path = "src/kinematics/config/cfg.yaml"
    with PipeLine(num_hands=num_hands, hands_cfg_path=hands_cfg_path) as p:
        p.run()


if __name__ == "__main__":
    main()
