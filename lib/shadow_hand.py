"""Shadow Robot Shadow Hand：姿态与控制器（须在 SimulationApp 启动后 import）。"""

import numpy as np

# 参考 Isaac Lab SHADOW_HAND_CFG / shadow_hand_env_cfg 驱动关节
ACTUATED_JOINTS = (
    "robot0_WRJ1",
    "robot0_WRJ0",
    "robot0_FFJ3",
    "robot0_FFJ2",
    "robot0_FFJ1",
    "robot0_MFJ3",
    "robot0_MFJ2",
    "robot0_MFJ1",
    "robot0_RFJ3",
    "robot0_RFJ2",
    "robot0_RFJ1",
    "robot0_LFJ4",
    "robot0_LFJ3",
    "robot0_LFJ2",
    "robot0_LFJ1",
    "robot0_THJ4",
    "robot0_THJ3",
    "robot0_THJ2",
    "robot0_THJ1",
    "robot0_THJ0",
)


def _finger_open(prefix: str) -> dict:
    return {
        f"robot0_{prefix}J3": 0.08,
        f"robot0_{prefix}J2": 0.12,
        f"robot0_{prefix}J1": 0.18,
    }


def open_joints() -> dict:
    joints = {name: 0.0 for name in ACTUATED_JOINTS}
    for prefix in ("FF", "MF", "RF"):
        joints.update(_finger_open(prefix))
    joints.update(
        {
            "robot0_LFJ4": 0.05,
            "robot0_LFJ3": 0.08,
            "robot0_LFJ2": 0.12,
            "robot0_LFJ1": 0.18,
            "robot0_THJ4": 0.0,
            "robot0_THJ3": 0.25,
            "robot0_THJ2": 0.15,
            "robot0_THJ1": 0.2,
            "robot0_THJ0": 0.1,
        }
    )
    return joints


def grasp_joints() -> dict:
    joints = open_joints()
    for prefix in ("FF", "MF", "RF"):
        joints[f"robot0_{prefix}J3"] = 0.65
        joints[f"robot0_{prefix}J2"] = 0.75
        joints[f"robot0_{prefix}J1"] = 0.85
    joints.update(
        {
            "robot0_LFJ4": 0.35,
            "robot0_LFJ3": 0.6,
            "robot0_LFJ2": 0.7,
            "robot0_LFJ1": 0.8,
            "robot0_THJ4": 0.2,
            "robot0_THJ3": 0.55,
            "robot0_THJ2": 0.45,
            "robot0_THJ1": 0.65,
            "robot0_THJ0": 0.5,
        }
    )
    return joints


def pose_from_map(joint_names: list[str], joint_map: dict) -> np.ndarray:
    return np.array([joint_map.get(name, 0.0) for name in joint_names], dtype=np.float64)


def make_poses(joint_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    return pose_from_map(joint_names, open_joints()), pose_from_map(joint_names, grasp_joints())


def configure_controller(robot) -> tuple[np.ndarray, np.ndarray]:
    joint_names = list(robot.dof_names)
    kps, kds = [], []
    for name in joint_names:
        if name.startswith("robot0_WR"):
            kps.append(5.0)
            kds.append(0.5)
        else:
            kps.append(1.0)
            kds.append(0.1)
    robot.get_articulation_controller().set_gains(kps=kps, kds=kds)
    return make_poses(joint_names)
