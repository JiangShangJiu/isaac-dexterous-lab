"""Wuji Hand 2 灵巧手：姿态与控制器（须在 SimulationApp 启动后 import）。"""

import numpy as np

_REVOLUTE_SUFFIXES = (
    "thumb_cmc_flex",
    "thumb_cmc_abd",
    "thumb_mcp",
    "thumb_ip",
    "index_finger_mcp_flex",
    "index_finger_mcp_abd",
    "index_finger_pip",
    "index_finger_dip",
    "middle_finger_mcp_flex",
    "middle_finger_mcp_abd",
    "middle_finger_pip",
    "middle_finger_dip",
    "ring_finger_mcp_flex",
    "ring_finger_mcp_abd",
    "ring_finger_pip",
    "ring_finger_dip",
    "pinky_mcp_flex",
    "pinky_mcp_abd",
    "pinky_pip",
    "pinky_dip",
)

_FLEX_SUFFIXES = (
    "thumb_cmc_flex",
    "index_finger_mcp_flex",
    "middle_finger_mcp_flex",
    "ring_finger_mcp_flex",
    "pinky_mcp_flex",
)

_GRASP_SUFFIXES = (
    "thumb_cmc_flex",
    "thumb_mcp",
    "thumb_ip",
    "index_finger_mcp_flex",
    "index_finger_pip",
    "index_finger_dip",
    "middle_finger_mcp_flex",
    "middle_finger_pip",
    "middle_finger_dip",
    "ring_finger_mcp_flex",
    "ring_finger_pip",
    "ring_finger_dip",
    "pinky_mcp_flex",
    "pinky_pip",
    "pinky_dip",
)


def _prefix(side: str) -> str:
    return "r" if side == "right" else "l"


def open_joints(side: str = "right") -> dict:
    # 参考 wuji isaaclab-sim 默认微曲姿态
    prefix = _prefix(side)
    joints = {f"{prefix}_{suffix}": 0.0 for suffix in _REVOLUTE_SUFFIXES}
    for suffix in _FLEX_SUFFIXES:
        joints[f"{prefix}_{suffix}"] = 0.06
    return joints


def grasp_joints(side: str = "right") -> dict:
    joints = open_joints(side)
    prefix = _prefix(side)
    grasp_values = {
        "thumb_cmc_flex": 0.55,
        "thumb_mcp": 0.45,
        "thumb_ip": 0.35,
        "index_finger_mcp_flex": 0.85,
        "index_finger_pip": 0.75,
        "index_finger_dip": 0.65,
        "middle_finger_mcp_flex": 0.85,
        "middle_finger_pip": 0.75,
        "middle_finger_dip": 0.65,
        "ring_finger_mcp_flex": 0.8,
        "ring_finger_pip": 0.7,
        "ring_finger_dip": 0.6,
        "pinky_mcp_flex": 0.75,
        "pinky_pip": 0.65,
        "pinky_dip": 0.55,
    }
    for suffix, value in grasp_values.items():
        joints[f"{prefix}_{suffix}"] = value
    return joints


def pose_from_map(joint_names: list[str], joint_map: dict) -> np.ndarray:
    return np.array([joint_map.get(name, 0.0) for name in joint_names], dtype=np.float64)


def make_poses(joint_names: list[str], side: str = "right") -> tuple[np.ndarray, np.ndarray]:
    return pose_from_map(joint_names, open_joints(side)), pose_from_map(joint_names, grasp_joints(side))


def configure_controller(robot, side: str = "right", hand_kp: float = 5.0, hand_kd: float = 0.08) -> tuple[np.ndarray, np.ndarray]:
    joint_names = list(robot.dof_names)
    robot.get_articulation_controller().set_gains(
        kps=[hand_kp] * len(joint_names),
        kds=[hand_kd] * len(joint_names),
    )
    return make_poses(joint_names, side)
