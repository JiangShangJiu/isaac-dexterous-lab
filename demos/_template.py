"""新演示脚本模板 — 复制此文件到 demos/ 下改名后编写。

用法:
  1. cp demos/_template.py demos/my_demo.py
  2. 编辑 my_demo.py
  3. ./restart.sh my_demo

推荐结构:
  - lib/sim/       启动仿真、加载原语
  - lib/scenes/    场景配方（可选，复杂布局放这里）
  - lib/control/   控制算法
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from isaacsim import SimulationApp

from lib.sim.config import get_sim_config

simulation_app = SimulationApp(launch_config=get_sim_config())

from lib.sim.bootstrap import setup_streaming_app
from lib.sim.loop import ensure_timeline_playing, simulation_tick
from lib.sim.scene import create_world_with_ground, setup_camera

assets_root = setup_streaming_app(simulation_app)
world = create_world_with_ground()
setup_camera()

# TODO: lib.scenes.<name>.build(world, assets_root) 或 load_robot(...)

print("演示场景已加载，开始仿真...", flush=True)

ensure_timeline_playing()
while simulation_app._app.is_running() and not simulation_app.is_exiting():
    simulation_tick(world, simulation_app)

simulation_app.close()
