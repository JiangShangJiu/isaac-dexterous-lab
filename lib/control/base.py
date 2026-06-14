"""控制器统一接口。"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ControlObservation:
    """单步控制所需的机器人状态（与具体传感器解耦，后续可扩展）。"""

    step: int
    sim_time: float
    joint_names: tuple[str, ...]
    joint_positions: np.ndarray
    joint_velocities: np.ndarray


class Controller(ABC):
    """算法库基类：子类实现 reset + step，demo 只负责驱动仿真循环。"""

    name: str = "base"

    @abstractmethod
    def reset(self, robot) -> None:
        """仿真 reset 或切换任务时调用。"""

    @abstractmethod
    def step(self, obs: ControlObservation) -> np.ndarray:
        """根据观测返回本步关节命令（长度 = robot.num_dof）。"""
