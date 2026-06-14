"""示例控制器：关节位置目标（张开 / 抓取交替）。"""

from __future__ import annotations

import numpy as np

from lib.control.base import ControlObservation, Controller
from lib.robots import kuka_allegro as ka


class JointPositionController(Controller):
    """占位示例：演示如何把算法放进 lib/control/。

    后续可新增 ImpedanceController、RLPolicy 等，接口保持一致。
    """

    name = "joint_position"

    def __init__(self, hold_steps: int = 200):
        self.hold_steps = max(1, int(hold_steps))
        self._open_pose: np.ndarray | None = None
        self._grasp_pose: np.ndarray | None = None

    def reset(self, robot) -> None:
        joint_names = list(robot.dof_names)
        self._open_pose, self._grasp_pose = ka.make_poses(joint_names)

    def step(self, obs: ControlObservation) -> np.ndarray:
        if self._open_pose is None or self._grasp_pose is None:
            raise RuntimeError("JointPositionController.reset() must be called before step()")
        use_open = (obs.step // self.hold_steps) % 2 == 0
        return self._open_pose if use_open else self._grasp_pose
