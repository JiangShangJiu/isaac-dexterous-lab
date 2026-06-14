"""Wuji Hand 2 灵巧手 + 桌子 + 方块 + WebRTC 推流演示。

环境变量:
  WUJI_HAND_SIDE=right|left   默认 right
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.sim.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

from isaacsim.core.utils.types import ArticulationAction

from lib.robots.wuji_hand2 import configure_controller
from lib.sim.bootstrap import setup_streaming_app
from lib.sim.scene import (
    add_demo_cube,
    add_work_table,
    create_world_with_ground,
    load_robot,
    setup_camera,
    setup_scene_lighting,
)

SIDE = os.environ.get("WUJI_HAND_SIDE", "right").lower()
if SIDE not in ("left", "right"):
    SIDE = "right"

# 掌心朝下（w, x, y, z）
HAND_ORIENTATION = (0.7071068, 0.7071068, 0.0, 0.0)

SCENE = {
    "table_top_z": 0.75,
    "table_center": (0.0, 0.0, 0.72),
    "table_size": (0.55, 0.55, 0.06),
    "cube_size": 0.04,
    "hand_position": (0.0, 0.0, 0.88),
    "camera_eye": (0.65, 0.65, 1.05),
    "camera_target": (0.0, 0.0, 0.78),
}

assets_root = setup_streaming_app(simulation_app)

world = create_world_with_ground()
setup_scene_lighting()
setup_camera(eye=SCENE["camera_eye"], target=SCENE["camera_target"])

table_top = SCENE["table_top_z"]
add_work_table(world, center=SCENE["table_center"], size=SCENE["table_size"])
cube_half = SCENE["cube_size"] / 2
add_demo_cube(
    world,
    center=(SCENE["table_center"][0], SCENE["table_center"][1], table_top + cube_half),
    size=SCENE["cube_size"],
)

robot_name = f"wuji_hand2_{SIDE}"
hand = load_robot(
    world,
    robot_name,
    "/World/WujiHand2",
    assets_root,
    position=SCENE["hand_position"],
    orientation=HAND_ORIENTATION,
)

pose_open, pose_grasp = configure_controller(hand, side=SIDE)
print(f"Wuji Hand 2 ({SIDE}) 关节数: {len(hand.dof_names)}, 名称: {list(hand.dof_names)}", flush=True)
print("Wuji Hand 2 已加载，开始仿真...", flush=True)

controller = hand.get_articulation_controller()

step = 0
while simulation_app._app.is_running() and not simulation_app.is_exiting():
    pose = pose_open if step % 400 < 200 else pose_grasp
    controller.apply_action(ArticulationAction(joint_positions=pose))
    world.step(render=True)
    step += 1

simulation_app.close()
