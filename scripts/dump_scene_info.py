#!/usr/bin/env python3
"""一次性启动 Isaac Sim、加载场景、导出 JSON，不启用 MCP。

用法（在宿主机）:
  ./scripts/dump_scene_info.sh kuka_allegro
  ./scripts/dump_scene_info.sh kuka_allegro -o ipynb/scene_snapshot.json

注意: 会独占 GPU，请先停掉 ./restart.sh 起的容器。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

_CODE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, _CODE_ROOT)

from isaacsim import SimulationApp

# 无 WebRTC / MCP，尽量轻量
_LAUNCH = {
    "width": 1280,
    "height": 720,
    "window_width": 1280,
    "window_height": 720,
    "headless": True,
    "hide_ui": True,
    "renderer": "RaytracedLighting",
}

SCENE_BUILDERS = {
    "kuka_allegro": ("lib.scenes.kuka_allegro", "build"),
    "dual_kuka_allegro": ("lib.scenes.dual_kuka_allegro", "build"),
    "allegro_hand": ("lib.scenes.allegro_hand", "build"),
}


def _load_scene(name: str, world, assets_root):
    import importlib

    if name not in SCENE_BUILDERS:
        raise ValueError(f"未知场景 {name}，可选: {list(SCENE_BUILDERS)}")
    mod_name, fn_name = SCENE_BUILDERS[name]
    mod = importlib.import_module(mod_name)
    return getattr(mod, fn_name)(world, assets_root)


def main() -> int:
    parser = argparse.ArgumentParser(description="导出 Isaac Sim 场景快照（无 MCP）")
    parser.add_argument("scene", nargs="?", default="kuka_allegro", help="场景名")
    parser.add_argument("-o", "--output", help="写入 JSON 文件（默认打印到 stdout）")
    args = parser.parse_args()

    simulation_app = SimulationApp(launch_config=_LAUNCH)

    from lib.inspect.in_process import collect_scene_snapshot
    from lib.sim.scene import create_world_with_ground, get_assets_root_or_exit

    assets_root = get_assets_root_or_exit(simulation_app)
    world = create_world_with_ground()
    ctx = _load_scene(args.scene, world, assets_root)
    world.step(render=True)

    snapshot = collect_scene_snapshot(ctx)
    snapshot["scene_name"] = args.scene
    text = json.dumps(snapshot, indent=2, ensure_ascii=False)

    if args.output:
        out_path = args.output if os.path.isabs(args.output) else os.path.join(_CODE_ROOT, args.output)
        os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"已写入: {out_path}", flush=True)
    else:
        print(text, flush=True)

    simulation_app.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
