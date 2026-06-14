"""双 Kuka iiwa7 + Allegro 灵巧手 + 桌子 + 方块 + WebRTC 推流演示。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.sim.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config("dual_arm"))

from isaacsim.core.utils.types import ArticulationAction

from lib.scenes import dual_kuka_allegro as dual_scene
from lib.sim.bootstrap import setup_streaming_app
from lib.sim.scene import create_world_with_ground

assets_root = setup_streaming_app(simulation_app)
world = create_world_with_ground()
ctx = dual_scene.build(world, assets_root)

left_pose = ctx.extras["left_open"]
right_pose = ctx.extras["right_open"]
print("双 Kuka+Allegro 已加载（桌面张开姿态），开始仿真...", flush=True)

left_ctrl = ctx.robots["left"].get_articulation_controller()
right_ctrl = ctx.robots["right"].get_articulation_controller()

while simulation_app._app.is_running() and not simulation_app.is_exiting():
    left_ctrl.apply_action(ArticulationAction(joint_positions=left_pose))
    right_ctrl.apply_action(ArticulationAction(joint_positions=right_pose))
    world.step(render=True)

simulation_app.close()
