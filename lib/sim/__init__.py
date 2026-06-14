"""仿真平台层：配置、场景原语、推流、MCP（与机器人/算法无关）。"""

from lib.sim.bootstrap import setup_streaming_app
from lib.sim.config import DEFAULT_SIM_CONFIG, get_sim_config

__all__ = ["setup_streaming_app", "get_sim_config", "DEFAULT_SIM_CONFIG"]
