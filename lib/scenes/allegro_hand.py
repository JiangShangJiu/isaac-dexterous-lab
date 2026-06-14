"""仅 Allegro 灵巧手 + 桌面场景。"""

from __future__ import annotations

from lib.robots.allegro_hand import configure_controller
from lib.scenes.base import SceneContext
from lib.sim.scene import add_demo_cube, add_work_table, load_robot, setup_camera, setup_scene_lighting

# Isaac Lab ALLEGRO_HAND_CFG 掌心朝下朝向（w, x, y, z）
HAND_ORIENTATION = (0.257551, 0.283045, 0.683330, -0.621782)

DEFAULT_LAYOUT = {
    "table_top_z": 0.75,
    "table_center": (0.0, 0.0, 0.72),
    "table_size": (0.55, 0.55, 0.06),
    "cube_size": 0.04,
    "hand_position": (0.0, 0.0, 0.88),
    "camera_eye": (0.65, 0.65, 1.05),
    "camera_target": (0.0, 0.0, 0.78),
}


def build(world, assets_root: str, layout: dict | None = None) -> SceneContext:
    cfg = {**DEFAULT_LAYOUT, **(layout or {})}
    setup_scene_lighting()
    setup_camera(eye=cfg["camera_eye"], target=cfg["camera_target"])

    table_top = cfg["table_top_z"]
    table = add_work_table(world, center=cfg["table_center"], size=cfg["table_size"])
    cube = add_demo_cube(
        world,
        center=(cfg["table_center"][0], cfg["table_center"][1], table_top + cfg["cube_size"] / 2),
        size=cfg["cube_size"],
    )

    hand = load_robot(
        world,
        "allegro_hand",
        "/World/AllegroHand",
        assets_root,
        position=cfg["hand_position"],
        orientation=HAND_ORIENTATION,
    )
    pose_open, pose_grasp = configure_controller(hand)

    print(f"Allegro 灵巧手关节数: {len(hand.dof_names)}", flush=True)
    return SceneContext(
        robots={"hand": hand},
        objects={"table": table, "cube": cube},
        extras={"pose_open": pose_open, "pose_grasp": pose_grasp},
    )
