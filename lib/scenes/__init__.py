"""场景配方：组合 robots + 环境；每个文件对应一类 demo 布局。

新增场景步骤:
  1. 在本目录添加 `<name>.py`，实现 build(world, assets_root, ...) -> SceneContext
  2. 在 demos/ 添加薄入口 `<name>_livestream.py`
  3. ./restart.sh <name>
"""

from lib.scenes.base import SceneContext

__all__ = ["SceneContext"]
