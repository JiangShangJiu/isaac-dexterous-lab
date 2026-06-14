"""WebRTC 推流相关配置（须在 SimulationApp 启动后调用）。"""

import os


def setup_livestream(simulation_app, public_ip: str | None = None) -> str:
    """开启 WebRTC 推流，返回实际使用的 IP。"""
    import carb
    from isaacsim.core.utils.extensions import enable_extension

    ip = public_ip or os.environ.get("PUBLIC_IP", "127.0.0.1")

    simulation_app.set_setting("/app/window/drawMouse", True)
    enable_extension("omni.services.livestream.nvcf")
    carb.settings.get_settings().set("/app/livestream/publicEndpointAddress", ip)

    print(f"WebRTC 推流地址: {ip}，请用 WebRTC 客户端连接此 IP", flush=True)
    return ip
