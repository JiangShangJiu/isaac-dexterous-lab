"""Wonik Allegro 灵巧手（单 hand）+ 桌子 + 方块 + WebRTC 推流演示。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.sim.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

from isaacsim.core.utils.types import ArticulationAction

from lib.scenes import allegro_hand as allegro_scene
from lib.sim.bootstrap import setup_streaming_app
from lib.sim.scene import create_world_with_ground

assets_root = setup_streaming_app(simulation_app)
world = create_world_with_ground()
ctx = allegro_scene.build(world, assets_root)

pose_open = ctx.extras["pose_open"]
pose_grasp = ctx.extras["pose_grasp"]
print("Allegro 灵巧手已加载，开始仿真...", flush=True)

controller = ctx.robots["hand"].get_articulation_controller()
step = 0
while simulation_app._app.is_running() and not simulation_app.is_exiting():
    pose = pose_open if step % 400 < 200 else pose_grasp
    controller.apply_action(ArticulationAction(joint_positions=pose))
    world.step(render=True)
    step += 1

simulation_app.close()
