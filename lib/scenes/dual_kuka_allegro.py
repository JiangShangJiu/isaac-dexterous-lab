"""双 Kuka iiwa7 + Allegro + 桌面场景。"""

from __future__ import annotations

from lib.robots.kuka_allegro import configure_controller_gains, make_table_open_pose
from lib.scenes.base import SceneContext
from lib.sim.scene import (
    add_demo_cube,
    add_work_table,
    load_robot,
    quat_yaw_deg,
    set_robot_pose,
    setup_camera,
)

DEFAULT_LAYOUT = {
    "table_top_z": 0.76,
    "table_center": (0.42, 0.0, 0.73),
    "table_size": (0.85, 0.55, 0.06),
    "cube_size": 0.04,
    "left_base": (-0.28, 0.58, 0.0),
    "right_base": (-0.28, -0.58, 0.0),
    "left_yaw_deg": -18.0,
    "right_yaw_deg": 18.0,
    "camera_eye": (1.15, 1.55, 1.38),
    "camera_target": (0.42, 0.0, 0.82),
}


def build(world, assets_root: str, layout: dict | None = None) -> SceneContext:
    cfg = {**DEFAULT_LAYOUT, **(layout or {})}
    setup_camera(eye=cfg["camera_eye"], target=cfg["camera_target"])

    table_top = cfg["table_top_z"]
    table = add_work_table(world, center=cfg["table_center"], size=cfg["table_size"])
    cube_half = cfg["cube_size"] / 2
    cube = add_demo_cube(
        world,
        center=(cfg["table_center"][0], cfg["table_center"][1], table_top + cube_half),
        size=cfg["cube_size"],
    )

    left = load_robot(
        world,
        "kuka_allegro",
        "/World/KukaAllegroLeft",
        assets_root,
        scene_name="kuka_allegro_left",
        reset=False,
        apply_pose=False,
    )
    right = load_robot(
        world,
        "kuka_allegro",
        "/World/KukaAllegroRight",
        assets_root,
        scene_name="kuka_allegro_right",
        reset=False,
        apply_pose=False,
    )
    world.reset()
    set_robot_pose(left, position=cfg["left_base"], orientation=quat_yaw_deg(cfg["left_yaw_deg"]))
    set_robot_pose(right, position=cfg["right_base"], orientation=quat_yaw_deg(cfg["right_yaw_deg"]))

    configure_controller_gains(left)
    configure_controller_gains(right)

    print(f"左臂关节数: {len(left.dof_names)}, 右臂关节数: {len(right.dof_names)}", flush=True)
    return SceneContext(
        robots={"left": left, "right": right},
        objects={"table": table, "cube": cube},
        extras={
            "left_open": make_table_open_pose(list(left.dof_names), "left"),
            "right_open": make_table_open_pose(list(right.dof_names), "right"),
        },
    )
