"""SimulationApp 启动配置（可在 SimulationApp 实例化之前 import）。"""

import os

# UI 缩放：1.0=默认，1.5=放大 50%，可通过环境变量 UI_DPI_SCALE 调整
UI_DPI_SCALE = float(os.environ.get("UI_DPI_SCALE", "2.0"))

DEFAULT_SIM_CONFIG = {
    "width": 1920,
    "height": 1080,
    "window_width": 2560,
    "window_height": 1440,
    "headless": True,
    "hide_ui": False,
    "renderer": "RaytracedLighting",
    "display_options": 3286,
    "extra_args": [
        f"--/app/window/dpiScaleOverride={UI_DPI_SCALE}",
    ],
}
