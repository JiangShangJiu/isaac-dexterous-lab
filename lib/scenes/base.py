"""场景构建公共类型。"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class SceneContext:
    """场景 build 的返回值：保存机器人与物体引用，供 demo / 控制器使用。"""

    robots: dict[str, Any] = field(default_factory=dict)
    objects: dict[str, Any] = field(default_factory=dict)
    extras: dict[str, Any] = field(default_factory=dict)

    @property
    def robot(self):
        if len(self.robots) != 1:
            raise AttributeError(
                f"SceneContext.robot 仅适用于单机器人场景（当前 {len(self.robots)} 台）；请用 .robots['name']"
            )
        return list(self.robots.values())[0]
