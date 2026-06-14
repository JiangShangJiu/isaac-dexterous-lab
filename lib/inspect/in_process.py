"""进程内读取 Isaac Sim 场景（omni.usd / Robot API），不经过 MCP。

须在同一进程里已启动 SimulationApp 并建好场景后调用。
无法从宿主机 Python 连到 ./restart.sh 已在跑的另一个进程。
"""

from __future__ import annotations

from typing import Any, Optional


def collect_prim_tree(stage, root_path: str, max_nodes: int = 50) -> list[dict[str, str]]:
    from pxr import Usd

    root = stage.GetPrimAtPath(root_path)
    if not root.IsValid():
        return []
    out: list[dict[str, str]] = []
    for prim in Usd.PrimRange(root):
        if len(out) >= max_nodes:
            out.append({"path": "...", "type": "(truncated)"})
            break
        out.append({"path": str(prim.GetPath()), "type": prim.GetTypeName()})
    return out


def collect_robot_state(robot) -> dict[str, Any]:
    import numpy as np

    names = list(robot.dof_names)
    pos = robot.get_joint_positions()
    vel = robot.get_joint_velocities()
    pos_w, orn_w = robot.get_world_pose()
    return {
        "prim_path": robot.prim_path,
        "num_dof": len(names),
        "dof_names": names,
        "joint_positions": [float(x) for x in pos],
        "joint_velocities": [float(x) for x in vel],
        "world_pose": {
            "position": [float(x) for x in pos_w],
            "orientation_wxyz": [float(x) for x in orn_w],
        },
    }


def collect_object_pose(obj, name: str) -> dict[str, Any]:
    import numpy as np

    pos, orn = obj.get_world_pose()
    return {
        "name": name,
        "position": [float(x) for x in pos],
        "orientation_wxyz": [float(x) for x in orn],
    }


def collect_scene_snapshot(
    ctx,
    *,
    robot_prim_paths: Optional[list[str]] = None,
    prim_tree_max: int = 50,
) -> dict[str, Any]:
    """从 SceneContext 收集当前仿真快照（进程内 API）。"""
    import omni.usd
    from isaacsim.storage.native import get_assets_root_path

    stage = omni.usd.get_context().get_stage()
    assets_root = get_assets_root_path()

    snapshot: dict[str, Any] = {
        "source": "in_process_api",
        "stage_default_prim": str(stage.GetDefaultPrim().GetPath()),
        "assets_root": assets_root,
        "robots": {},
        "objects": {},
        "prim_trees": {},
    }

    for name, robot in ctx.robots.items():
        snapshot["robots"][name] = collect_robot_state(robot)
        path = robot.prim_path
        snapshot["prim_trees"][path] = collect_prim_tree(stage, path, prim_tree_max)

    if robot_prim_paths:
        for path in robot_prim_paths:
            if path not in snapshot["prim_trees"]:
                snapshot["prim_trees"][path] = collect_prim_tree(stage, path, prim_tree_max)

    for name, obj in ctx.objects.items():
        snapshot["objects"][name] = collect_object_pose(obj, name)

    return snapshot
