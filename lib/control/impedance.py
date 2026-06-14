"""阻抗 / 物体级控制（骨架，待实现）。

实现步骤建议:
1. 在此文件编写 ImpedanceController(Controller)
2. 在 lib/control/registry.py 的 CONTROLLER_REGISTRY 中注册
3. demo 里把 CONTROLLER 改为 "impedance"
"""

from __future__ import annotations

import numpy as np

from lib.control.base import ControlObservation, Controller


class ImpedanceController(Controller):
    """占位：后续在此实现 doc/ 中物体级阻抗等算法。"""

    name = "impedance"

    def __init__(self, **kwargs):
        self._kwargs = kwargs

    def reset(self, robot) -> None:
        raise NotImplementedError("ImpedanceController 尚未实现，请在 lib/control/impedance.py 中补充")

    def step(self, obs: ControlObservation) -> np.ndarray:
        raise NotImplementedError("ImpedanceController 尚未实现，请在 lib/control/impedance.py 中补充")
