"""控制器注册表：demo 通过名称创建算法实例。"""

from __future__ import annotations

from typing import Any, Type

from lib.control.base import Controller
from lib.control.joint_position import JointPositionController

CONTROLLER_REGISTRY: dict[str, Type[Controller]] = {
    JointPositionController.name: JointPositionController,
}


def create_controller(name: str, **kwargs: Any) -> Controller:
    try:
        cls = CONTROLLER_REGISTRY[name]
    except KeyError as exc:
        available = ", ".join(sorted(CONTROLLER_REGISTRY))
        raise ValueError(f"未知控制器: {name!r}，可选: {available}") from exc
    return cls(**kwargs)
