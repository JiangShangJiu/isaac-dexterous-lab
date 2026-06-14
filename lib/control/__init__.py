"""控制算法库：与场景/机器人解耦，可在多个 demo 中复用。"""

from lib.control.base import ControlObservation, Controller
from lib.control.joint_position import JointPositionController
from lib.control.registry import CONTROLLER_REGISTRY, create_controller
from lib.control.runner import apply_joint_command, read_observation, run_control_loop

__all__ = [
    "ControlObservation",
    "Controller",
    "JointPositionController",
    "CONTROLLER_REGISTRY",
    "create_controller",
    "apply_joint_command",
    "read_observation",
    "run_control_loop",
]
