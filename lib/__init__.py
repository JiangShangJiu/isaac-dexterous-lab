"""项目 Python 库 — 分层说明:

  lib/sim/      仿真平台（config、scene 原语、推流、MCP、bootstrap）
  lib/robots/   各机器人关节配置与预设姿态
  lib/scenes/   场景配方（机器人 + 桌子/物体/相机布局）
  lib/control/  控制算法（与场景解耦，可跨场景复用）

  demos/        薄入口：启动 SimulationApp → 选场景 → 选控制器 → 主循环

须在 SimulationApp 实例化之后再 import sim.scene / robots / scenes / control。
get_sim_config 可在 SimulationApp 之前 import（lib.sim.config）。
"""
