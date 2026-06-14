"""场景静态信息（不启动 Isaac Sim，仅读仓库配置）。"""

from __future__ import annotations

from typing import Any

from lib.robots.kuka_allegro import (
    ARM_JOINT_PREFIX,
    NUM_ARM_DOFS,
    NUM_HAND_DOFS,
    OPEN_JOINTS,
    grasp_joints,
)
from lib.sim.scene import ROBOT_ASSETS

# 各场景 build() 的默认参数摘要（与 lib/scenes/*.py 保持一致）
SCENE_SPECS: dict[str, dict[str, Any]] = {
    "kuka_allegro": {
        "module": "lib.scenes.kuka_allegro",
        "description": "Kuka iiwa7 + Allegro 单臂 + 桌子 + 方块",
        "robots": {"main": {"key": "kuka_allegro", "prim": "/World/KukaAllegro"}},
        "objects": ["table", "cube"],
        "camera": {"eye": (1.8, 1.8, 1.4), "target": (0.15, 0.0, 0.85)},
    },
    "dual_kuka_allegro": {
        "module": "lib.scenes.dual_kuka_allegro",
        "description": "双 Kuka iiwa7 + Allegro + 桌子 + 方块",
        "robots": {
            "left": {"key": "kuka_allegro", "prim": "/World/KukaAllegroLeft"},
            "right": {"key": "kuka_allegro", "prim": "/World/KukaAllegroRight"},
        },
        "objects": ["table", "cube"],
    },
    "allegro_hand": {
        "module": "lib.scenes.allegro_hand",
        "description": "仅 Allegro 灵巧手 + 桌子 + 方块",
        "robots": {"hand": {"key": "allegro_hand", "prim": "/World/AllegroHand"}},
        "objects": ["table", "cube"],
    },
}


def list_scene_names() -> list[str]:
    return sorted(SCENE_SPECS.keys())


def get_scene_spec(name: str) -> dict[str, Any]:
    if name not in SCENE_SPECS:
        raise KeyError(f"未知场景: {name}，已知: {list(SCENE_SPECS)}")
    return SCENE_SPECS[name]


def robot_assets_table() -> list[dict[str, str]]:
    return [{"key": k, "usd_rel": v} for k, v in sorted(ROBOT_ASSETS.items())]


def kuka_allegro_joint_summary() -> dict[str, Any]:
    grasp = grasp_joints()
    return {
        "arm_prefix": ARM_JOINT_PREFIX,
        "num_arm_dofs": NUM_ARM_DOFS,
        "num_hand_dofs": NUM_HAND_DOFS,
        "open_joints": dict(OPEN_JOINTS),
        "grasp_joints": grasp,
        "joint_names_expected": list(OPEN_JOINTS.keys()),
    }


def summarize_all() -> dict[str, Any]:
    return {
        "scenes": SCENE_SPECS,
        "robot_assets": robot_assets_table(),
        "kuka_allegro": kuka_allegro_joint_summary(),
    }
