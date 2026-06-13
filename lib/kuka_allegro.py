"""Kuka iiwa7 + Allegro 灵巧手：姿态与控制器配置（须在 SimulationApp 启动后 import）。"""

import numpy as np

# 参考 Isaac Lab KUKA_ALLEGRO_CFG
OPEN_JOINTS = {
    "iiwa7_joint_1": 0.0,
    "iiwa7_joint_2": 0.0,
    "iiwa7_joint_3": 0.7854,
    "iiwa7_joint_4": 1.5708,
    "iiwa7_joint_5": -1.5708,
    "iiwa7_joint_6": -1.5708,
    "iiwa7_joint_7": 0.0,
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
    joints["iiwa7_joint_4"] = 1.35
    joints["iiwa7_joint_6"] = -1.35
    return joints


def table_open_joints(side: str = "left") -> dict:
    """手臂前伸、手指张开，悬在桌面上方（配合双臂场景布局）。"""
    joints = dict(OPEN_JOINTS)
    yaw = 0.35 if side == "left" else -0.35
    joints["iiwa7_joint_1"] = yaw
    joints["iiwa7_joint_2"] = 0.35
    joints["iiwa7_joint_3"] = 1.05
    joints["iiwa7_joint_4"] = 1.25
    joints["iiwa7_joint_5"] = -1.57
    joints["iiwa7_joint_6"] = -1.35
    joints["iiwa7_joint_7"] = 0.0
    return joints


def pose_from_map(joint_names: list[str], joint_map: dict) -> np.ndarray:
    return np.array([joint_map.get(name, 0.0) for name in joint_names], dtype=np.float64)


def make_poses(joint_names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    return pose_from_map(joint_names, OPEN_JOINTS), pose_from_map(joint_names, grasp_joints())


def make_table_open_pose(joint_names: list[str], side: str = "left") -> np.ndarray:
    return pose_from_map(joint_names, table_open_joints(side))


def configure_controller_gains(robot, arm_kp=120.0, arm_kd=12.0, hand_kp=8.0, hand_kd=0.5) -> None:
    joint_names = list(robot.dof_names)
    kps, kds = [], []
    for name in joint_names:
        if name.startswith("iiwa7_"):
            kps.append(arm_kp)
            kds.append(arm_kd)
        else:
            kps.append(hand_kp)
            kds.append(hand_kd)
    robot.get_articulation_controller().set_gains(kps=kps, kds=kds)


def configure_controller(robot, arm_kp=120.0, arm_kd=12.0, hand_kp=8.0, hand_kd=0.5) -> tuple[np.ndarray, np.ndarray]:
    joint_names = list(robot.dof_names)
    configure_controller_gains(robot, arm_kp, arm_kd, hand_kp, hand_kd)
    return make_poses(joint_names)
