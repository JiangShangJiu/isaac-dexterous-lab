"""Franka 机械臂 + WebRTC 推流演示（默认入口）。"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.sim.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

import numpy as np
from isaacsim.core.utils.types import ArticulationAction

from lib.sim.bootstrap import setup_streaming_app
from lib.sim.loop import ensure_timeline_playing, simulation_tick
from lib.sim.scene import create_world_with_ground, load_robot, setup_camera

assets_root = setup_streaming_app(simulation_app)

world = create_world_with_ground()
setup_camera()
franka = load_robot(world, "franka", "/World/Franka", assets_root)

print("Franka 机械臂已加载，开始仿真...", flush=True)

POSE_A = np.array([0.0, -0.5, 0.0, -2.0, 0.0, 1.5, 0.8, 0.04, 0.04])
POSE_B = np.array([0.0, 0.0, 0.0, -1.0, 0.0, 1.0, 0.5, 0.04, 0.04])

step = 0
ensure_timeline_playing()
while simulation_app._app.is_running() and not simulation_app.is_exiting():
    pose = POSE_A if step % 300 < 150 else POSE_B
    franka.get_articulation_controller().apply_action(ArticulationAction(joint_positions=pose))
    if simulation_tick(world, simulation_app):
        step += 1

simulation_app.close()
