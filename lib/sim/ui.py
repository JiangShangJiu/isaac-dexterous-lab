"""界面缩放（须在 SimulationApp 启动后调用，用于运行时二次调整）。"""

from lib.sim.config import UI_DPI_SCALE


def setup_ui_scale(simulation_app, scale: float | None = None) -> float:
    """放大 WebRTC 界面字体和菜单。scale=1.5 表示放大 50%。"""
    import carb

    ui_scale = scale if scale is not None else UI_DPI_SCALE
    settings = carb.settings.get_settings()
    settings.set("/app/window/dpiScaleOverride", ui_scale)

    try:
        import omni.appwindow

        app_window = omni.appwindow.get_default_app_window()
        if app_window is not None:
            app_window.set_dpi_scale_override(ui_scale)
    except Exception:
        pass

    print(f"UI 缩放: {ui_scale}x（可通过环境变量 UI_DPI_SCALE 调整）", flush=True)
    return ui_scale
