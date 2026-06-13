"""Wonik Allegro 灵巧手：姿态与控制器（须在 SimulationApp 启动后 import）。"""

import numpy as np

OPEN_JOINTS = {
    "index_joint_0": 0.0,
    "index_joint_1": 0.3,
    "index_joint_2": 0.3,
    "index_joint_3": 0.3,
    "middle_joint_0": 0.0,
    "middle_joint_1": 0.3,
    "middle_joint_2": 0.3,
    "middle_joint_3": 0.3,
    "ring_joint_0": 0.0,
    "ring_joint_1": 0.3,
    "ring_joint_2": 0.3,
    "ring_joint_3": 0.3,
    "thumb_joint_0": 1.5,
    "thumb_joint_1": 0.60147215,
    "thumb_joint_2": 0.33795027,
    "thumb_joint_3": 0.60845138,
}


def grasp_joints() -> dict:
    joints = dict(OPEN_JOINTS)
    for finger in ("index", "middle", "ring"):
        joints[f"{finger}_joint_1"] = 0.9
        joints[f"{finger}_joint_2"] = 0.9
        joints[f"{finger}_joint_3"] = 0.9
    joints["thumb_joint_1"] = 0.9
    joints["thumb_joint_2"] = 0.7
    joints["thumb_joint_3"] = 0.7
    return joints


def pose_from_map(joint_names: list[str], joint_map: dict) -> np.ndarray:
    return np.array([joint_map.get(name, 0.0) for name in joint_names], dtype=np.float64)


def make_poses(joint_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    return pose_from_map(joint_names, OPEN_JOINTS), pose_from_map(joint_names, grasp_joints())


def configure_controller(robot, hand_kp=8.0, hand_kd=0.5) -> tuple[np.ndarray, np.ndarray]:
    joint_names = list(robot.dof_names)
    robot.get_articulation_controller().set_gains(
        kps=[hand_kp] * len(joint_names),
        kds=[hand_kd] * len(joint_names),
    )
    return make_poses(joint_names)
