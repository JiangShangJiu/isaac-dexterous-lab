#!/bin/bash
# 无 MCP：一次性容器内启动 Isaac Sim，导出场景 JSON 后退出
# 用法:
#   ./scripts/dump_scene_info.sh kuka_allegro
#   ./scripts/dump_scene_info.sh kuka_allegro ipynb/scene_snapshot.json
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SCENE="${1:-kuka_allegro}"
OUTPUT="${2:-}"
IMAGE="${ISAAC_IMAGE:-nvcr.io/nvidia/isaac-sim:5.1.0}"

EXTRA_ARGS=()
if [[ -n "$OUTPUT" ]]; then
  if [[ "$OUTPUT" == /* ]]; then
    EXTRA_ARGS=(-o "$OUTPUT")
  else
    EXTRA_ARGS=(-o "/workspace/$OUTPUT")
  fi
fi

echo ">>> 停止可能占用 GPU 的 Isaac 容器..."
sudo docker ps -aq --filter "name=isaac-sim" | xargs -r sudo docker rm -f 2>/dev/null || true
sleep 2

echo ">>> 导出场景: $SCENE（进程内 API，无 MCP）"

sudo docker run --rm --gpus all \
  --entrypoint bash \
  --network=host \
  -e "ACCEPT_EULA=Y" \
  -e "PRIVACY_CONSENT=Y" \
  -e "PYTHONUNBUFFERED=1" \
  -v /home/ubuntu/docker/isaac-sim/cache/main:/isaac-sim/.cache \
  -v /home/ubuntu/docker/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache \
  -v /home/ubuntu/docker/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs \
  -v /home/ubuntu/docker/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config \
  -v /home/ubuntu/docker/isaac-sim/data:/isaac-sim/.local/share/ov/data \
  -v /home/ubuntu/docker/isaac-sim/pkg:/isaac-sim/.local/share/ov/pkg \
  -v "${ROOT_DIR}:/workspace:rw" \
  -w /isaac-sim \
  "${IMAGE}" \
  -c "./python.sh /workspace/scripts/dump_scene_info.py ${SCENE} ${EXTRA_ARGS[*]}"
