"""Isaac Sim MCP Extension（须在 SimulationApp 启动后调用）。"""

import os

from lib.config import ISAAC_MCP_PORT, MCP_EXT_FOLDER


def setup_mcp(simulation_app) -> bool:
    """启用 MCP Extension，供 Cursor 等 MCP 客户端控制仿真。"""
    ext_toml = os.path.join(MCP_EXT_FOLDER, "isaac.sim.mcp_extension", "config", "extension.toml")
    if not os.path.isfile(ext_toml):
        print(
            f"MCP 未安装: 请运行 scripts/setup_mcp.sh（缺少 {ext_toml}）",
            flush=True,
        )
        return False

    try:
        from isaacsim.core.utils.extensions import enable_extension

        enable_extension("isaac.sim.mcp_extension")

        print(
            f"MCP Extension 已启用，TCP 端口 {ISAAC_MCP_PORT}（MCP Server 连 127.0.0.1:{ISAAC_MCP_PORT}）",
            flush=True,
        )
        return True
    except Exception as exc:
        print(f"MCP Extension 启用失败: {exc}", flush=True)
        return False
