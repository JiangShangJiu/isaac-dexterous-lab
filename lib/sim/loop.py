"""仿真主循环辅助：与 Kit Timeline 联动，支持 MCP `simulation.pause` / `play`。"""

from __future__ import annotations


def ensure_timeline_playing() -> None:
    """demo 启动后调用一次，与原先「一直 world.step」行为一致。"""
    import omni.timeline

    timeline = omni.timeline.get_timeline_interface()
    if not timeline.is_playing():
        timeline.play()


def is_timeline_playing() -> bool:
    import omni.timeline

    return omni.timeline.get_timeline_interface().is_playing()


def simulation_tick(world, simulation_app, render: bool = True) -> bool:
    """暂停时只渲染画面（WebRTC 不断），播放时物理步进。返回本次是否执行了物理步。"""
    if is_timeline_playing():
        world.step(render=render)
        return True
    if render:
        world.render()
    return False
