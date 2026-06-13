"""Kuka LBR iiwa7 + Allegro 灵巧手 + WebRTC 推流演示。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

import numpy as np
from isaacsim.core.api.objects import DynamicCuboid
from isaacsim.core.utils.types import ArticulationAction

from lib.kuka_allegro import configure_controller
from lib.livestream import setup_livestream
from lib.mcp import setup_mcp
from lib.scene import create_world_with_ground, get_assets_root_or_exit, load_robot, setup_camera, setup_scene_lighting
from lib.ui import setup_ui_scale

setup_ui_scale(simulation_app)
setup_livestream(simulation_app)
setup_mcp(simulation_app)
assets_root = get_assets_root_or_exit(simulation_app)

world = create_world_with_ground()
setup_scene_lighting()
setup_camera(eye=(1.8, 1.8, 1.4), target=(0.15, 0.0, 0.85))

robot = load_robot(world, "kuka_allegro", "/World/KukaAllegro", assets_root)

world.scene.add(
    DynamicCuboid(
        prim_path="/World/Cube",
        name="cube",
        position=np.array([0.55, 0.0, 0.92]),
        scale=np.array([0.04, 0.04, 0.04]),
        color=np.array([0.2, 0.6, 1.0]),
    )
)

pose_open, pose_grasp = configure_controller(robot)
print(f"Kuka+Allegro 关节数: {len(robot.dof_names)}, 名称: {list(robot.dof_names)}", flush=True)
print("Kuka+Allegro 已加载，开始仿真...", flush=True)

controller = robot.get_articulation_controller()

step = 0
while simulation_app._app.is_running() and not simulation_app.is_exiting():
    pose = pose_open if step % 400 < 200 else pose_grasp
    controller.apply_action(ArticulationAction(joint_positions=pose))
    world.step(render=True)
    step += 1

simulation_app.close()
