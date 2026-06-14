"""仿真控制循环：读观测 → 调算法 → 写命令。"""

from __future__ import annotations

import numpy as np
from isaacsim.core.utils.types import ArticulationAction

from lib.control.base import ControlObservation, Controller


def read_observation(robot, step: int, sim_time: float) -> ControlObservation:
    positions = robot.get_joint_positions()
    velocities = robot.get_joint_velocities()
    if positions is None:
        positions = np.zeros(robot.num_dof, dtype=np.float64)
    if velocities is None:
        velocities = np.zeros(robot.num_dof, dtype=np.float64)
    return ControlObservation(
        step=step,
        sim_time=sim_time,
        joint_names=tuple(robot.dof_names),
        joint_positions=np.asarray(positions, dtype=np.float64),
        joint_velocities=np.asarray(velocities, dtype=np.float64),
    )


def apply_joint_command(robot, joint_positions: np.ndarray) -> None:
    robot.get_articulation_controller().apply_action(
        ArticulationAction(joint_positions=np.asarray(joint_positions, dtype=np.float64))
    )


def run_control_loop(
    simulation_app,
    world,
    robot,
    controller: Controller,
    *,
    sim_dt: float = 1.0 / 60.0,
    render: bool = True,
) -> None:
    """标准控制主循环；算法逻辑全部在 controller 内。"""
    controller.reset(robot)
    step = 0
    while simulation_app._app.is_running() and not simulation_app.is_exiting():
        obs = read_observation(robot, step, step * sim_dt)
        command = controller.step(obs)
        apply_joint_command(robot, command)
        world.step(render=render)
        step += 1
