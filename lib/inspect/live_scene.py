"""与正在运行的 Isaac Sim 交互（TCP 8766 Extension API）。

统一入口 — notebook / 脚本只用本模块：

    from lib.inspect.live_scene import connect_isaac, fetch_live_snapshot

    with connect_isaac() as sim:
        sim.get_scene_info()
        sim.robot_joints_by_name("/World/KukaAllegro")
        sim.pause()

API 分组（IsaacSimClient）：
  场景   get_scene_info, list_prims, get_prim_info, clear_scene, ...
  机器人 list_robots, create_robot, get_robot_info, set_joint_positions, robot_joints_by_name, ...
  仿真   play, pause, stop, step, get_simulation_state, get_physics_state, ...
  物体   create_object, delete_object, transform_object, clone_object
  资产   import_urdf, load_usd, search_usd
  传感器 create_camera, capture_image, create_lidar, get_point_cloud
  灯光   create_light, modify_light
  材质   create_material, apply_material
  图     create_action_graph, edit_action_graph
"""

from __future__ import annotations

import json
import os
import socket
from typing import Any, Optional, Sequence

DEFAULT_PORT = int(os.environ.get("ISAAC_MCP_PORT", "8766"))
DEFAULT_HOST = os.environ.get("ISAAC_MCP_HOST", "127.0.0.1")
DEFAULT_TIMEOUT_SEC = float(os.environ.get("ISAAC_MCP_TIMEOUT", "120"))


def _params(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


class IsaacSimClient:
    """连接 Docker 内 Isaac MCP Extension（127.0.0.1:8766）。"""

    def __init__(
        self,
        host: str = DEFAULT_HOST,
        port: int = DEFAULT_PORT,
        timeout_sec: float = DEFAULT_TIMEOUT_SEC,
    ):
        self.host = host
        self.port = port
        self.timeout_sec = timeout_sec
        self._sock: Optional[socket.socket] = None

    # ── 连接 ─────────────────────────────────────────────────────────────

    @property
    def connected(self) -> bool:
        return self._sock is not None

    @property
    def endpoint(self) -> str:
        return f"{self.host}:{self.port}"

    def connect(self) -> bool:
        if self._sock:
            return True
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.connect((self.host, self.port))
            return True
        except OSError:
            self._sock = None
            return False

    def close(self) -> None:
        if self._sock:
            try:
                self._sock.close()
            finally:
                self._sock = None

    def __enter__(self) -> IsaacSimClient:
        if not self.connect():
            raise ConnectionError(self._connect_hint())
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def _connect_hint(self) -> str:
        return (
            f"无法连接 Isaac Sim Extension {self.endpoint}。"
            "请先 ./restart.sh <场景>，并确认日志有「MCP Extension 已启用」。"
        )

    def _recv_json(self) -> dict[str, Any]:
        if not self._sock:
            raise ConnectionError("未连接 Isaac Sim")
        chunks: list[bytes] = []
        self._sock.settimeout(self.timeout_sec)
        while True:
            chunk = self._sock.recv(16384)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks).decode("utf-8"))
            except json.JSONDecodeError:
                continue
        raise RuntimeError("未收到完整 JSON 响应")

    def _call(self, command_type: str, params: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        if not self._sock and not self.connect():
            raise ConnectionError(self._connect_hint())
        payload = {"type": command_type, "params": params or {}}
        self._sock.sendall(json.dumps(payload).encode("utf-8"))
        response = self._recv_json()
        if response.get("status") == "error":
            raise RuntimeError(response.get("message", "Isaac 返回错误"))
        return response.get("result", {})

    def ping(self) -> dict[str, Any]:
        """连通性检查（同 get_scene_info）。"""
        return self.get_scene_info()

    # ── 场景 ─────────────────────────────────────────────────────────────

    def get_scene_info(self) -> dict[str, Any]:
        """Stage 路径、资产根目录、Prim 总数。"""
        return self._call("scene.get_info")

    def prim_count(self) -> int:
        return int(self.get_scene_info().get("prim_count", 0))

    def list_prims(self, root_path: str = "/World", prim_type: Optional[str] = None) -> dict[str, Any]:
        return self._call("scene.list_prims", _params(root_path=root_path, prim_type=prim_type))

    def list_world_prims(self) -> list[dict[str, str]]:
        """/World 下顶层 Prim 列表。"""
        return self.list_prims("/World").get("prims", [])

    def get_prim_info(self, prim_path: str) -> dict[str, Any]:
        return self._call("scene.get_prim_info", {"prim_path": prim_path})

    def create_physics_scene(
        self,
        gravity: Optional[Sequence[float]] = None,
        scene_name: str = "PhysicsScene",
    ) -> dict[str, Any]:
        return self._call("scene.create_physics", _params(gravity=gravity, scene_name=scene_name))

    def clear_scene(self, keep_physics: bool = False) -> dict[str, Any]:
        return self._call("scene.clear", {"keep_physics": keep_physics})

    def list_environments(self) -> dict[str, Any]:
        return self._call("scene.list_environments")

    def load_environment(self, environment: str, prim_path: str = "/Environment") -> dict[str, Any]:
        return self._call("scene.load_environment", {"environment": environment, "prim_path": prim_path})

    # ── 机器人 ───────────────────────────────────────────────────────────

    def list_robots(self) -> dict[str, Any]:
        """资产库中可用机器人。"""
        return self._call("robots.list")

    def refresh_robots(self) -> dict[str, Any]:
        return self._call("robots.refresh")

    def create_robot(
        self,
        robot_type: str = "franka",
        position: Optional[Sequence[float]] = None,
        name: Optional[str] = None,
        prim_path: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._call(
            "robots.create",
            _params(robot_type=robot_type, position=position, name=name, prim_path=prim_path),
        )

    def get_robot_info(self, prim_path: str) -> dict[str, Any]:
        """关节名、DOF、限位。"""
        return self._call("robots.get_info", {"prim_path": prim_path})

    def get_joint_positions(self, prim_path: str) -> dict[str, Any]:
        """当前关节位置（弧度）。"""
        return self._call("robots.get_joints", {"prim_path": prim_path})

    def set_joint_positions(
        self,
        prim_path: str,
        joint_positions: Sequence[float],
        joint_indices: Optional[list[int]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "robots.set_joints",
            _params(
                prim_path=prim_path,
                joint_positions=list(joint_positions),
                joint_indices=joint_indices,
            ),
        )

    set_joints = set_joint_positions

    def get_joint_config(self, prim_path: str) -> dict[str, Any]:
        """刚度、阻尼、目标/实际位置。"""
        return self._call("simulation.get_joint_config", {"prim_path": prim_path})

    def robot_joints_by_name(self, prim_path: str, *, include_config: bool = True) -> dict[str, dict[str, Any]]:
        """按关节名返回：index、position_rad、type、限位、控制器配置。"""
        info = self.get_robot_info(prim_path)
        positions = self.get_joint_positions(prim_path).get("joint_positions", [])
        limits_by_name = {item["name"]: item for item in info.get("joint_limits", [])}

        config_by_name: dict[str, dict[str, Any]] = {}
        if include_config:
            try:
                for item in self.get_joint_config(prim_path).get("joints", []):
                    name = item.get("name")
                    if name:
                        config_by_name[name] = item
            except RuntimeError:
                pass

        out: dict[str, dict[str, Any]] = {}
        for i, name in enumerate(info.get("joint_names", [])):
            joint: dict[str, Any] = {"index": i}
            if i < len(positions):
                joint["position_rad"] = positions[i]
            if name in limits_by_name:
                for key, val in limits_by_name[name].items():
                    if key != "name":
                        joint[key] = val
            if name in config_by_name:
                for key, val in config_by_name[name].items():
                    if key != "name":
                        joint[key] = val
            out[name] = joint
        return out

    def summarize_robot_joints(self, prim_path: str) -> list[dict[str, Any]]:
        return [{"name": name, **data} for name, data in self.robot_joints_by_name(prim_path).items()]

    def list_robot_child_prims(self, prim_path: str, max_items: int = 50) -> list[dict[str, str]]:
        prims = self.list_prims(prim_path).get("prims", [])
        if len(prims) > max_items:
            return prims[:max_items] + [{"path": "...", "type": f"(共 {len(prims)} 项，已截断)"}]
        return prims

    # ── 仿真控制 ─────────────────────────────────────────────────────────

    def play(self) -> dict[str, Any]:
        return self._call("simulation.play")

    def pause(self) -> dict[str, Any]:
        return self._call("simulation.pause")

    def stop(self) -> dict[str, Any]:
        return self._call("simulation.stop")

    play_simulation = play
    pause_simulation = pause
    stop_simulation = stop

    def step(
        self,
        num_steps: int = 1,
        observe_prims: Optional[Sequence[str]] = None,
        observe_joints: Optional[Sequence[str]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "simulation.step",
            _params(num_steps=num_steps, observe_prims=observe_prims, observe_joints=observe_joints),
        )

    step_simulation = step

    def get_simulation_state(self) -> dict[str, Any]:
        """Timeline: playing / paused / stopped。"""
        return self._call("simulation.get_state")

    def timeline_state(self) -> str:
        return str(self.get_simulation_state().get("timeline_state", "unknown"))

    def get_physics_state(self, prim_path: str) -> dict[str, Any]:
        return self._call("simulation.get_physics_state", {"prim_path": prim_path})

    def set_physics_params(
        self,
        gravity: Optional[Sequence[float]] = None,
        time_step: Optional[float] = None,
        gpu_enabled: Optional[bool] = None,
    ) -> dict[str, Any]:
        return self._call(
            "simulation.set_physics",
            _params(gravity=gravity, time_step=time_step, gpu_enabled=gpu_enabled),
        )

    def execute_script(self, code: str, cwd: Optional[str] = None) -> dict[str, Any]:
        return self._call("simulation.execute_script", _params(code=code, cwd=cwd))

    def reload_script(self, file_path: str, module_name: Optional[str] = None) -> dict[str, Any]:
        return self._call("simulation.reload_script", _params(file_path=file_path, module_name=module_name))

    def get_logs(self) -> dict[str, Any]:
        return self._call("simulation.get_logs")

    # ── 物体 ─────────────────────────────────────────────────────────────

    def create_object(
        self,
        object_type: str = "Cube",
        position: Optional[Sequence[float]] = None,
        rotation: Optional[Sequence[float]] = None,
        scale: Optional[Sequence[float]] = None,
        color: Optional[Sequence[float]] = None,
        physics_enabled: bool = False,
        prim_path: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._call(
            "objects.create",
            _params(
                object_type=object_type,
                position=position,
                rotation=rotation,
                scale=scale,
                color=color,
                physics_enabled=physics_enabled,
                prim_path=prim_path,
            ),
        )

    def delete_object(self, prim_path: str) -> dict[str, Any]:
        return self._call("objects.delete", {"prim_path": prim_path})

    def transform_object(
        self,
        prim_path: str,
        position: Optional[Sequence[float]] = None,
        rotation: Optional[Sequence[float]] = None,
        scale: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "objects.transform",
            _params(prim_path=prim_path, position=position, rotation=rotation, scale=scale),
        )

    def clone_object(
        self,
        source_path: str,
        target_path: str,
        position: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "objects.clone",
            _params(source_path=source_path, target_path=target_path, position=position),
        )

    # ── 资产 ─────────────────────────────────────────────────────────────

    def import_urdf(
        self,
        urdf_path: str,
        prim_path: str = "/World/robot",
        position: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call("assets.import_urdf", _params(urdf_path=urdf_path, prim_path=prim_path, position=position))

    def load_usd(
        self,
        usd_url: str,
        prim_path: str = "/World/my_usd",
        position: Optional[Sequence[float]] = None,
        scale: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "assets.load_usd",
            _params(usd_url=usd_url, prim_path=prim_path, position=position, scale=scale),
        )

    def search_usd(
        self,
        text_prompt: str,
        target_path: str = "/World/my_usd",
        position: Optional[Sequence[float]] = None,
        scale: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "assets.search_usd",
            _params(text_prompt=text_prompt, target_path=target_path, position=position, scale=scale),
        )

    def generate_3d(
        self,
        text_prompt: Optional[str] = None,
        image_url: Optional[str] = None,
        position: Optional[Sequence[float]] = None,
        scale: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "assets.generate_3d",
            _params(text_prompt=text_prompt, image_url=image_url, position=position, scale=scale),
        )

    # ── 传感器 ───────────────────────────────────────────────────────────

    def create_camera(
        self,
        prim_path: str = "/World/Camera",
        position: Optional[Sequence[float]] = None,
        rotation: Optional[Sequence[float]] = None,
        resolution: Optional[Sequence[int]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "sensors.create_camera",
            _params(prim_path=prim_path, position=position, rotation=rotation, resolution=resolution),
        )

    def capture_image(self, prim_path: str = "/World/Camera", output_path: Optional[str] = None) -> dict[str, Any]:
        return self._call("sensors.capture_image", _params(prim_path=prim_path, output_path=output_path))

    def create_lidar(
        self,
        prim_path: str = "/World/Lidar",
        position: Optional[Sequence[float]] = None,
        rotation: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "sensors.create_lidar",
            _params(prim_path=prim_path, position=position, rotation=rotation),
        )

    def get_point_cloud(self, prim_path: str = "/World/Lidar") -> dict[str, Any]:
        return self._call("sensors.get_point_cloud", {"prim_path": prim_path})

    # ── 灯光 ─────────────────────────────────────────────────────────────

    def create_light(
        self,
        light_type: str = "DistantLight",
        position: Optional[Sequence[float]] = None,
        intensity: float = 1000.0,
        color: Optional[Sequence[float]] = None,
        rotation: Optional[Sequence[float]] = None,
        prim_path: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._call(
            "lighting.create",
            _params(
                light_type=light_type,
                position=position,
                intensity=intensity,
                color=color,
                rotation=rotation,
                prim_path=prim_path,
            ),
        )

    def modify_light(
        self,
        prim_path: str,
        intensity: Optional[float] = None,
        color: Optional[Sequence[float]] = None,
    ) -> dict[str, Any]:
        return self._call("lighting.modify", _params(prim_path=prim_path, intensity=intensity, color=color))

    # ── 材质 ─────────────────────────────────────────────────────────────

    def create_material(
        self,
        material_type: str = "pbr",
        prim_path: Optional[str] = None,
        color: Optional[Sequence[float]] = None,
        roughness: float = 0.5,
        metallic: float = 0.0,
        static_friction: float = 0.5,
        dynamic_friction: float = 0.5,
        restitution: float = 0.0,
    ) -> dict[str, Any]:
        return self._call(
            "materials.create",
            _params(
                material_type=material_type,
                prim_path=prim_path,
                color=color,
                roughness=roughness,
                metallic=metallic,
                static_friction=static_friction,
                dynamic_friction=dynamic_friction,
                restitution=restitution,
            ),
        )

    def apply_material(self, material_path: str, target_prim_path: str) -> dict[str, Any]:
        return self._call(
            "materials.apply",
            {"material_path": material_path, "target_prim_path": target_prim_path},
        )

    # ── Action Graph ─────────────────────────────────────────────────────

    def create_action_graph(
        self,
        graph_path: str = "/World/ActionGraph",
        nodes: Optional[list[dict[str, Any]]] = None,
        connections: Optional[list[list[str]]] = None,
        values: Optional[list[dict[str, Any]]] = None,
        evaluator: str = "push",
        script_file: Optional[str] = None,
    ) -> dict[str, Any]:
        return self._call(
            "graphs.create_action_graph",
            _params(
                graph_path=graph_path,
                nodes=nodes,
                connections=connections,
                values=values,
                evaluator=evaluator,
                script_file=script_file,
            ),
        )

    def edit_action_graph(
        self,
        graph_path: str,
        nodes: Optional[list[dict[str, Any]]] = None,
        connections: Optional[list[list[str]]] = None,
    ) -> dict[str, Any]:
        return self._call(
            "graphs.edit_action_graph",
            _params(graph_path=graph_path, nodes=nodes, connections=connections),
        )

    # ── 聚合 ─────────────────────────────────────────────────────────────

    def fetch_snapshot(
        self,
        robot_prim_paths: Sequence[str],
        *,
        world_root: str = "/World",
        object_prim_paths: Optional[Sequence[str]] = None,
        include_joints_by_name: bool = True,
    ) -> dict[str, Any]:
        """一次拉取场景 + 仿真状态 + 机器人 + 可选物体。"""
        snapshot: dict[str, Any] = {
            "connected": True,
            "endpoint": self.endpoint,
            "scene": self.get_scene_info(),
            "simulation": self.get_simulation_state(),
            "prims": self.list_prims(world_root),
            "robots": {},
            "objects": {},
        }
        for path in robot_prim_paths:
            if include_joints_by_name:
                snapshot["robots"][path] = self.robot_joints_by_name(path)
            else:
                snapshot["robots"][path] = {
                    "info": self.get_robot_info(path),
                    "positions": self.get_joint_positions(path),
                }
        for path in object_prim_paths or []:
            snapshot["objects"][path] = self.get_prim_info(path)
        return snapshot


LiveSceneClient = IsaacSimClient


def connect_isaac(
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
    timeout_sec: float = DEFAULT_TIMEOUT_SEC,
) -> IsaacSimClient:
    """连接已运行的 Isaac Sim；失败则抛 ConnectionError。"""
    client = IsaacSimClient(host=host, port=port, timeout_sec=timeout_sec)
    if not client.connect():
        raise ConnectionError(client._connect_hint())
    return client


def fetch_live_snapshot(
    robot_prim_paths: Sequence[str],
    *,
    world_root: str = "/World",
    object_prim_paths: Optional[Sequence[str]] = None,
    host: str = DEFAULT_HOST,
    port: int = DEFAULT_PORT,
) -> dict[str, Any]:
    """连接并拉取快照；失败返回 {connected: False, error: ...}。"""
    client = IsaacSimClient(host=host, port=port)
    try:
        if not client.connect():
            return {"connected": False, "error": client._connect_hint()}
        return client.fetch_snapshot(
            robot_prim_paths,
            world_root=world_root,
            object_prim_paths=object_prim_paths,
        )
    except Exception as e:
        return {"connected": False, "error": str(e)}
    finally:
        client.close()


def try_fetch_live_summary(robot_prim_paths: list[str]) -> dict[str, Any]:
    return fetch_live_snapshot(robot_prim_paths)
