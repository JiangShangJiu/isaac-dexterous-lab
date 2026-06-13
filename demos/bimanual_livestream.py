"""OpenArm 双臂 + 桌子 + 方块 + WebRTC 推流演示。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

import numpy as np
from isaacsim.core.utils.types import ArticulationAction

from lib.livestream import setup_livestream
from lib.mcp import setup_mcp
from lib.scene import (
    add_demo_cube,
    add_work_table,
    create_world_with_ground,
    get_assets_root_or_exit,
    load_robot,
    setup_camera,
)
from lib.ui import setup_ui_scale

setup_ui_scale(simulation_app)
setup_livestream(simulation_app)
setup_mcp(simulation_app)
assets_root = get_assets_root_or_exit(simulation_app)

world = create_world_with_ground()
setup_camera(eye=(1.6, 1.9, 1.35), target=(0.55, 0.0, 0.82))

# 工作台与方块（桌面高度约 0.76 m）
TABLE_TOP_Z = 0.76
add_work_table(world, center=(0.55, 0.0, TABLE_TOP_Z - 0.03))
add_demo_cube(world, center=(0.55, 0.0, TABLE_TOP_Z + 0.02))

robot = load_robot(world, "openarm_bimanual", "/World/OpenArm", assets_root, position=(0.0, 0.0, 0.0))

controller = robot.get_articulation_controller()
joint_names = list(robot.dof_names)
num_dof = len(joint_names)
print(f"双臂关节数: {num_dof}, 名称: {joint_names}", flush=True)


def _build_bimanual_poses(names: list[str]) -> tuple[np.ndarray, np.ndarray]:
    pose_a = np.zeros(len(names), dtype=np.float64)
    pose_b = np.zeros(len(names), dtype=np.float64)
    for i, name in enumerate(names):
        if "finger" in name:
            pose_a[i] = 0.0
            pose_b[i] = 0.035
        elif "left_joint2" in name:
            pose_a[i] = 0.7
            pose_b[i] = 0.2
        elif "left_joint4" in name:
            pose_a[i] = -1.1
            pose_b[i] = -1.5
        elif "right_joint2" in name:
            pose_a[i] = -0.2
            pose_b[i] = 0.7
        elif "right_joint4" in name:
            pose_a[i] = -1.5
            pose_b[i] = -1.1
        elif "left_joint6" in name:
            pose_a[i] = 0.4
            pose_b[i] = -0.4
        elif "right_joint6" in name:
            pose_a[i] = -0.4
            pose_b[i] = 0.4
    return pose_a, pose_b


POSE_A, POSE_B = _build_bimanual_poses(joint_names)

kps = [100.0 if "finger" not in n else 500.0 for n in joint_names]
kds = [8.0 if "finger" not in n else 50.0 for n in joint_names]
controller.set_gains(kps=kps, kds=kds)

print("双臂场景已加载，开始仿真...", flush=True)

step = 0
while simulation_app._app.is_running() and not simulation_app.is_exiting():
    pose = POSE_A if step % 400 < 200 else POSE_B
    controller.apply_action(ArticulationAction(joint_positions=pose))
    world.step(render=True)
    step += 1

simulation_app.close()
