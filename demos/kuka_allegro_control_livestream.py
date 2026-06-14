"""Kuka+Allegro + lib.control 算法库示例（薄入口）。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.sim.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

from lib.control import create_controller, run_control_loop
from lib.scenes import kuka_allegro as kuka_allegro_scene
from lib.sim.bootstrap import setup_streaming_app
from lib.sim.scene import create_world_with_ground

CONTROLLER = "joint_position"
CONTROLLER_KWARGS = {"hold_steps": 200}

assets_root = setup_streaming_app(simulation_app)
world = create_world_with_ground()
ctx = kuka_allegro_scene.build(world, assets_root)

controller = create_controller(CONTROLLER, **CONTROLLER_KWARGS)
print(f"控制器: {controller.name}，开始仿真...", flush=True)

run_control_loop(simulation_app, world, ctx.robot, controller)

simulation_app.close()
