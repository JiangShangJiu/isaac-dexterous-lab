"""双 Kuka iiwa7 + Allegro 灵巧手 + 桌子 + 方块 + WebRTC 推流演示。

布局说明（单位：米，可改下方 SCENE 字典）：
  - 两台 Kuka 底座在桌子后方两侧，默认朝 +X 伸出机械臂
  - 桌子在双臂前方中间，方块在桌面中央
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config("dual_arm"))

import numpy as np
from isaacsim.core.utils.types import ArticulationAction

from lib.kuka_allegro import configure_controller_gains, make_table_open_pose
from lib.livestream import setup_livestream
from lib.mcp import setup_mcp
from lib.scene import (
    add_demo_cube,
    add_work_table,
    create_world_with_ground,
    get_assets_root_or_exit,
    load_robot,
    quat_yaw_deg,
    set_robot_pose,
    setup_camera,
)
from lib.ui import setup_ui_scale

# ── 场景布局（按需修改）────────────────────────────────────
SCENE = {
  # 桌面高度（桌面顶面 z）
    "table_top_z": 0.76,
  # 桌子中心 (x 朝前, y 朝左)
    "table_center": (0.42, 0.0, 0.73),
    "table_size": (0.85, 0.55, 0.06),
  # 方块在桌面正中
    "cube_center": (0.42, 0.0, 0.78),
    "cube_size": 0.04,
  # 左/右臂底座：在桌子后方两侧，略向桌面中心偏转
    "left_base": (-0.28, 0.58, 0.0),
    "right_base": (-0.28, -0.58, 0.0),
    "left_yaw_deg": -18.0,
    "right_yaw_deg": 18.0,
  # 相机
    "camera_eye": (1.15, 1.55, 1.38),
    "camera_target": (0.42, 0.0, 0.82),
}

setup_ui_scale(simulation_app)
setup_livestream(simulation_app)
setup_mcp(simulation_app)
assets_root = get_assets_root_or_exit(simulation_app)

world = create_world_with_ground()
setup_camera(eye=SCENE["camera_eye"], target=SCENE["camera_target"])

table_top = SCENE["table_top_z"]
add_work_table(world, center=SCENE["table_center"], size=SCENE["table_size"])
cube_half = SCENE["cube_size"] / 2
cube_center = (
    SCENE["table_center"][0],
    SCENE["table_center"][1],
    table_top + cube_half,
)
add_demo_cube(world, center=cube_center, size=SCENE["cube_size"])

left = load_robot(
    world,
    "kuka_allegro",
    "/World/KukaAllegroLeft",
    assets_root,
    scene_name="kuka_allegro_left",
    reset=False,
    apply_pose=False,
)
right = load_robot(
    world,
    "kuka_allegro",
    "/World/KukaAllegroRight",
    assets_root,
    scene_name="kuka_allegro_right",
    reset=False,
    apply_pose=False,
)
world.reset()
set_robot_pose(left, position=SCENE["left_base"], orientation=quat_yaw_deg(SCENE["left_yaw_deg"]))
set_robot_pose(right, position=SCENE["right_base"], orientation=quat_yaw_deg(SCENE["right_yaw_deg"]))

configure_controller_gains(left)
configure_controller_gains(right)
left_pose = make_table_open_pose(list(left.dof_names), "left")
right_pose = make_table_open_pose(list(right.dof_names), "right")

print(
    f"左臂关节数: {len(left.dof_names)}, 右臂关节数: {len(right.dof_names)}",
    flush=True,
)
print("双 Kuka+Allegro 已加载（桌面张开姿态），开始仿真...", flush=True)

left_ctrl = left.get_articulation_controller()
right_ctrl = right.get_articulation_controller()

while simulation_app._app.is_running() and not simulation_app.is_exiting():
    left_ctrl.apply_action(ArticulationAction(joint_positions=left_pose))
    right_ctrl.apply_action(ArticulationAction(joint_positions=right_pose))
    world.step(render=True)

simulation_app.close()
