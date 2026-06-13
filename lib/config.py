"""SimulationApp 启动配置（可在 SimulationApp 实例化之前 import）。"""

import os

_CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MCP_EXT_FOLDER = os.environ.get(
    "MCP_EXT_FOLDER",
    os.path.join(_CODE_ROOT, "mcp", "isaacsim-mcp-server"),
)
ISAAC_MCP_PORT = os.environ.get("ISAAC_MCP_PORT", "8766")

# UI 缩放：1.0=默认，2.0=放大一倍
UI_DPI_SCALE = float(os.environ.get("UI_DPI_SCALE", "2.0"))


def _build_extra_args() -> list[str]:
    args = [f"--/app/window/dpiScaleOverride={UI_DPI_SCALE}"]

    ext_toml = os.path.join(MCP_EXT_FOLDER, "isaac.sim.mcp_extension", "config", "extension.toml")
    if os.path.isfile(ext_toml):
        args.extend(
            [
                "--ext-folder",
                MCP_EXT_FOLDER,
                "--enable",
                "isaac.sim.mcp_extension",
                f"--/exts/isaac.sim.mcp/server.port={ISAAC_MCP_PORT}",
                "--/exts/isaac.sim.mcp/server.host=0.0.0.0",
            ]
        )
    return args


def get_sim_config() -> dict:
    return {
        "width": 1920,
        "height": 1080,
        "window_width": 2560,
        "window_height": 1440,
        "headless": True,
        "hide_ui": False,
        "renderer": "RaytracedLighting",
        "display_options": 3286,
        "extra_args": _build_extra_args(),
    }


# 兼容旧引用
DEFAULT_SIM_CONFIG = get_sim_config()
