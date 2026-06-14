"""Kuka iiwa7 + Allegro 单臂桌面场景。"""

from __future__ import annotations

from lib.robots.kuka_allegro import configure_controller_gains
from lib.scenes.base import SceneContext
from lib.sim.scene import add_demo_cube, add_work_table, load_robot, setup_camera, setup_scene_lighting


def build(
    world,
    assets_root: str,
    *,
    robot_prim_path: str = "/World/KukaAllegro",
    with_table: bool = True,
    with_cube: bool = True,
) -> SceneContext:
    setup_scene_lighting()
    setup_camera(eye=(1.8, 1.8, 1.4), target=(0.15, 0.0, 0.85))

    robot = load_robot(world, "kuka_allegro", robot_prim_path, assets_root)
    configure_controller_gains(robot)

    objects = {}
    if with_table:
        objects["table"] = add_work_table(world, center=(0.55, 0.0, 0.73), size=(1.0, 0.7, 0.06))
    if with_cube:
        objects["cube"] = add_demo_cube(world, center=(0.55, 0.0, 0.79), size=0.04)

    print(f"Kuka+Allegro 关节数: {len(robot.dof_names)}", flush=True)
    print(f"关节名称: {list(robot.dof_names)}", flush=True)
    return SceneContext(robots={"main": robot}, objects=objects)
