"""场景搭建：地面、相机、机器人（须在 SimulationApp 启动后 import/调用）。"""

import sys

ROBOT_ASSETS = {
    "franka": "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
    "ur10": "/Isaac/Robots/UniversalRobots/ur10/ur10.usd",
    # Isaac Lab 预置：Kuka LBR iiwa7 + Allegro Hand（单 USD，臂与手同一 articulation）
    "kuka_allegro": "/Isaac/IsaacLab/Robots/KukaAllegro/kuka.usd",
    # OpenArm 双臂（每侧 7 轴臂 + 夹爪）
    "openarm_bimanual": "/Isaac/Robots/OpenArm/openarm_bimanual/openarm_bimanual.usd",
}


def get_assets_root_or_exit(simulation_app):
    import carb
    from isaacsim.storage.native import get_assets_root_path

    root = get_assets_root_path()
    if root is None:
        carb.log_error("找不到 Isaac Sim 资产目录，请确认网络可访问 Omniverse 资产服务器")
        simulation_app.close()
        sys.exit(1)
    return root


def create_world_with_ground():
    from isaacsim.core.api import World

    world = World(stage_units_in_meters=1.0)
    world.scene.add_default_ground_plane()
    return world


def setup_camera(
    eye=(2.5, 2.5, 1.8),
    target=(0.0, 0.0, 0.5),
    camera_prim_path="/OmniverseKit_Persp",
):
    from isaacsim.core.utils.viewports import set_camera_view

    set_camera_view(eye=list(eye), target=list(target), camera_prim_path=camera_prim_path)


def quat_yaw_deg(yaw_deg: float):
    """绕 Z 轴旋转四元数 (w, x, y, z)，用于调整机器人底座朝向。"""
    import numpy as np

    half = np.deg2rad(yaw_deg) * 0.5
    return np.array([np.cos(half), 0.0, 0.0, np.sin(half)], dtype=np.float64)


def load_robot(
    world,
    robot_name: str,
    prim_path: str,
    assets_root: str,
    position=(0.0, 0.0, 0.0),
    orientation=None,
    scene_name: str | None = None,
    reset: bool = True,
    apply_pose: bool = True,
):
    import numpy as np
    from isaacsim.core.api.robots import Robot
    from isaacsim.core.utils.stage import add_reference_to_stage, get_stage_units

    rel_path = ROBOT_ASSETS.get(robot_name)
    if rel_path is None:
        raise ValueError(f"未知机器人: {robot_name}，可选: {list(ROBOT_ASSETS)}")

    unique_name = scene_name or prim_path.rstrip("/").split("/")[-1]
    add_reference_to_stage(usd_path=assets_root + rel_path, prim_path=prim_path)
    robot = world.scene.add(Robot(prim_path=prim_path, name=unique_name))
    if reset:
        world.reset()
    if apply_pose:
        set_robot_pose(robot, position, orientation)
    return robot


def set_robot_pose(robot, position=(0.0, 0.0, 0.0), orientation=None):
    import numpy as np
    from isaacsim.core.utils.stage import get_stage_units

    pos = np.array(position, dtype=np.float64) / get_stage_units()
    if orientation is not None:
        robot.set_world_pose(position=pos, orientation=np.array(orientation, dtype=np.float64))
    else:
        robot.set_world_pose(position=pos)


def add_work_table(
    world,
    center=(0.55, 0.0, 0.73),
    size=(1.0, 0.7, 0.06),
    color=(0.55, 0.42, 0.32),
):
    """在场景中添加固定工作台（桌面）。"""
    import numpy as np
    from isaacsim.core.api.objects import FixedCuboid

    return world.scene.add(
        FixedCuboid(
            prim_path="/World/Table",
            name="table",
            position=np.array(center, dtype=np.float64),
            scale=np.array(size, dtype=np.float64),
            color=np.array(color, dtype=np.float64),
        )
    )


def add_demo_cube(
    world,
    center=(0.55, 0.0, 0.79),
    size=0.04,
    color=(0.2, 0.6, 1.0),
    prim_path="/World/Cube",
):
    """在场景中添加可交互小方块。"""
    import numpy as np
    from isaacsim.core.api.objects import DynamicCuboid

    s = float(size)
    return world.scene.add(
        DynamicCuboid(
            prim_path=prim_path,
            name="cube",
            position=np.array(center, dtype=np.float64),
            scale=np.array([s, s, s], dtype=np.float64),
            color=np.array(color, dtype=np.float64),
        )
    )
