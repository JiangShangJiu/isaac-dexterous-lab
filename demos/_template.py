"""新演示脚本模板 — 复制此文件到 demos/ 下改名后编写。

用法:
  1. cp demos/_template.py demos/my_demo.py
  2. 编辑 my_demo.py
  3. ./restart.sh my_demo
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.config import DEFAULT_SIM_CONFIG

simulation_app = SimulationApp(launch_config=DEFAULT_SIM_CONFIG)

from lib.livestream import setup_livestream
from lib.scene import create_world_with_ground, get_assets_root_or_exit, setup_camera
from lib.ui import setup_ui_scale

setup_ui_scale(simulation_app)
setup_livestream(simulation_app)
get_assets_root_or_exit(simulation_app)

world = create_world_with_ground()
setup_camera()

# TODO: 在这里添加你的机器人、物体、传感器等
# assets_root = get_assets_root_or_exit(simulation_app)
# robot = load_robot(world, "franka", "/World/Franka", assets_root)

print("演示场景已加载，开始仿真...", flush=True)

while simulation_app._app.is_running() and not simulation_app.is_exiting():
    world.step(render=True)

simulation_app.close()
