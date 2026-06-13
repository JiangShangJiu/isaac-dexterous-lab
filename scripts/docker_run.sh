#!/bin/bash
# Docker 启动逻辑（被 restart.sh 调用，一般不直接执行）
set -e

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
ENTRY_SCRIPT="${ENTRY_SCRIPT:-demos/franka_livestream.py}"
CONTAINER_NAME="${CONTAINER_NAME:-isaac-sim-robot}"
IMAGE="${ISAAC_IMAGE:-nvcr.io/nvidia/isaac-sim:5.1.0}"

PUBLIC_IP="${PUBLIC_IP:-117.50.175.186}"
if [[ -f /home/ubuntu/.env ]]; then
  # shellcheck disable=SC1091
  source /home/ubuntu/.env
fi

if [[ ! -f "${ROOT_DIR}/${ENTRY_SCRIPT}" ]]; then
  echo "❌ 入口脚本不存在: ${ROOT_DIR}/${ENTRY_SCRIPT}"
  exit 1
fi

echo ">>> 入口脚本: ${ENTRY_SCRIPT}"
echo ">>> [1/4] 停止旧 MCP Server..."
"${ROOT_DIR}/scripts/run_mcp_server.sh" --stop 2>/dev/null || true

echo ">>> [2/4] 停止旧容器..."
sudo docker compose -f /home/ubuntu/docker-compose.yml down 2>/dev/null || true
# 清理所有 isaac-sim 相关容器，避免多个实例抢 GPU
sudo docker ps -aq --filter "name=isaac-sim" | xargs -r sudo docker rm -f 2>/dev/null || true

echo ">>> [3/4] 启动新容器..."
sudo docker run --name "${CONTAINER_NAME}" --gpus all -d \
  --entrypoint bash \
  --network=host \
  -e "ACCEPT_EULA=Y" \
  -e "PRIVACY_CONSENT=Y" \
  -e "PYTHONUNBUFFERED=1" \
  -e "UI_DPI_SCALE=${UI_DPI_SCALE:-1.8}" \
  -e "ISAAC_MCP_PORT=${ISAAC_MCP_PORT:-8766}" \
  -e "MCP_EXT_FOLDER=/workspace/mcp/isaacsim-mcp-server" \
  -e "PUBLIC_IP=${PUBLIC_IP}" \
  -v /home/ubuntu/docker/isaac-sim/cache/main:/isaac-sim/.cache \
  -v /home/ubuntu/docker/isaac-sim/cache/computecache:/isaac-sim/.nv/ComputeCache \
  -v /home/ubuntu/docker/isaac-sim/logs:/isaac-sim/.nvidia-omniverse/logs \
  -v /home/ubuntu/docker/isaac-sim/config:/isaac-sim/.nvidia-omniverse/config \
  -v /home/ubuntu/docker/isaac-sim/data:/isaac-sim/.local/share/ov/data \
  -v /home/ubuntu/docker/isaac-sim/pkg:/isaac-sim/.local/share/ov/pkg \
  -v "${ROOT_DIR}:/workspace:rw" \
  -w /isaac-sim \
  "${IMAGE}" \
  -c "./python.sh /workspace/${ENTRY_SCRIPT} --/app/livestream/publicEndpointAddress=\$PUBLIC_IP"

MAX_WAIT_SEC="${MAX_WAIT_SEC:-360}"
INTERVAL_SEC=5
MAX_ROUNDS=$((MAX_WAIT_SEC / INTERVAL_SEC))
READY_MSG="${READY_MSG:-机械臂已加载|演示场景已加载}"

echo ">>> [4/4] 等待就绪（首次约 2-5 分钟，最长 ${MAX_WAIT_SEC} 秒）..."
last_stage=""
for round in $(seq 1 "$MAX_ROUNDS"); do
  if ! sudo docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Names}}' | grep -q "${CONTAINER_NAME}"; then
    echo ""
    echo "❌ 容器已退出，启动失败。最近日志："
    sudo docker logs "${CONTAINER_NAME}" 2>&1 | tail -30 || true
    exit 1
  fi

  logs=$(sudo docker logs "${CONTAINER_NAME}" 2>&1 || true)

  if echo "$logs" | grep -qE "${READY_MSG}"; then
    echo ""
    echo "✅ Isaac Sim 启动完成！"
    echo "   WebRTC 连接: ${PUBLIC_IP}"
    echo "   查看日志: sudo docker logs -f ${CONTAINER_NAME}"
    if [[ -x "${ROOT_DIR}/mcp/.venv/bin/isaacsim-mcp-server" ]]; then
      echo ""
      echo ">>> 启动 MCP Server..."
      if "${ROOT_DIR}/scripts/run_mcp_server.sh" --daemon; then
        echo "   Cursor: Settings → MCP → isaac-sim（连 http://127.0.0.1:8767/sse）"
      fi
    else
      echo ""
      echo "   MCP 未安装，运行 ./scripts/setup_mcp.sh 后可随 restart 自动拉起"
    fi
    exit 0
  fi

  if echo "$logs" | grep -qiE "traceback|module not found|there was an error running python|could not find isaac sim assets|找不到 Isaac Sim 资产"; then
    echo ""
    echo "❌ 启动失败，最近日志："
    echo "$logs" | tail -20
    exit 1
  fi

  stage="启动中"
  if echo "$logs" | grep -q "app ready"; then
    stage="Kit 已就绪，加载仿真场景..."
  fi
  if echo "$logs" | grep -q "Simulation App Startup Complete"; then
    stage="仿真应用已启动，加载资产..."
  fi
  if echo "$logs" | grep -q "WebRTC 推流地址"; then
    stage="WebRTC 已配置，下载/加载机器人模型（约 1-2 分钟）..."
  fi
  if echo "$logs" | grep -q "Franka 机械臂已加载"; then
    stage="机械臂已就绪"
  fi

  elapsed=$((round * INTERVAL_SEC))
  if [[ "$stage" != "$last_stage" ]]; then
    echo "   [${elapsed}s] ${stage}"
    last_stage="$stage"
  elif (( elapsed % 30 == 0 && elapsed > 0 )); then
    echo "   [${elapsed}s] ${stage}（仍在进行，请稍候）"
  fi

  sleep "$INTERVAL_SEC"
done

echo ""
if sudo docker ps --filter "name=${CONTAINER_NAME}" --format '{{.Names}}' | grep -q "${CONTAINER_NAME}"; then
  echo "⏳ 等待超时，但容器仍在运行（可能还在加载）。"
  echo "   sudo docker logs -f ${CONTAINER_NAME}"
  echo "   就绪后连 WebRTC: ${PUBLIC_IP}"
else
  echo "❌ 容器已退出: sudo docker logs ${CONTAINER_NAME}"
  exit 1
fi
