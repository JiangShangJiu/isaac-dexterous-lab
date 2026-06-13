"""场景搭建：地面、相机、机器人（须在 SimulationApp 启动后 import/调用）。"""

import sys

ROBOT_ASSETS = {
    "franka": "/Isaac/Robots/FrankaRobotics/FrankaPanda/franka.usd",
    "ur10": "/Isaac/Robots/UniversalRobots/ur10/ur10.usd",
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


def load_robot(world, robot_name: str, prim_path: str, assets_root: str, position=(0.0, 0.0, 0.0)):
    import numpy as np
    from isaacsim.core.api.robots import Robot
    from isaacsim.core.utils.stage import add_reference_to_stage, get_stage_units

    rel_path = ROBOT_ASSETS.get(robot_name)
    if rel_path is None:
        raise ValueError(f"未知机器人: {robot_name}，可选: {list(ROBOT_ASSETS)}")

    add_reference_to_stage(usd_path=assets_root + rel_path, prim_path=prim_path)
    robot = world.scene.add(Robot(prim_path=prim_path, name=robot_name))
    world.reset()
    robot.set_world_pose(position=np.array(position) / get_stage_units())
    return robot
