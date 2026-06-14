"""仿真 App 启动：WebRTC、MCP、资产路径（与具体场景无关）。"""

from __future__ import annotations


def setup_streaming_app(simulation_app, *, enable_mcp: bool = True) -> str:
    """配置 UI 缩放、WebRTC、可选 MCP，返回 Omniverse assets_root。"""
    from lib.sim.livestream import setup_livestream
    from lib.sim.mcp import setup_mcp
    from lib.sim.scene import get_assets_root_or_exit
    from lib.sim.ui import setup_ui_scale

    setup_ui_scale(simulation_app)
    setup_livestream(simulation_app)
    if enable_mcp:
        setup_mcp(simulation_app)
    return get_assets_root_or_exit(simulation_app)
