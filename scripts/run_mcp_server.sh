#!/bin/bash
# MCP Server（连接 Docker 内 Isaac Sim MCP Extension）
#
# 架构:
#   Cursor ←SSE 8767→ MCP Server（宿主机，restart.sh 自动后台拉起）
#              ↓ TCP 8766
#         Isaac MCP Extension（Docker 内）
#
# 用法:
#   ./scripts/run_mcp_server.sh           # 前台 stdio（调试用）
#   ./scripts/run_mcp_server.sh --daemon  # 后台 SSE（restart.sh 自动调用）
#   ./scripts/run_mcp_server.sh --stop
#   ./scripts/run_mcp_server.sh --status
#   ./scripts/run_mcp_server.sh --wait-ready
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
VENV="${ROOT}/mcp/.venv"
PYTHON="${VENV}/bin/python"
CLI="${VENV}/bin/isaacsim-mcp-server"
SSE_ENTRY="${ROOT}/scripts/mcp_sse_entry.py"
PIDFILE="${ROOT}/mcp/.mcp-server.pid"
LOGFILE="${ROOT}/mcp/mcp-server.log"

export ISAAC_MCP_PORT="${ISAAC_MCP_PORT:-8766}"
export ISAAC_SIM_HOST="${ISAAC_SIM_HOST:-127.0.0.1}"
export ISAAC_SIM_PORT="${ISAAC_SIM_PORT:-${ISAAC_MCP_PORT}}"
export MCP_SSE_HOST="${MCP_SSE_HOST:-127.0.0.1}"
export MCP_SSE_PORT="${MCP_SSE_PORT:-8767}"

mcp_cli_ready() {
  [[ -x "${PYTHON}" && -f "${SSE_ENTRY}" ]]
}

port_open() {
  local host="$1" port="$2"
  (echo >/dev/tcp/"${host}"/"${port}") 2>/dev/null
}

wait_for_extension() {
  local max_wait="${1:-90}"
  local i
  for ((i = 1; i <= max_wait; i++)); do
    if port_open "${ISAAC_SIM_HOST}" "${ISAAC_SIM_PORT}"; then
      return 0
    fi
    sleep 1
  done
  return 1
}

ping_extension() {
  "${PYTHON}" - <<'PY'
import json
import os
import socket
import sys

host = os.environ.get("ISAAC_SIM_HOST", "127.0.0.1")
port = int(os.environ.get("ISAAC_SIM_PORT", "8766"))
cmd = json.dumps({"type": "scene.get_info", "params": {}}).encode()

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(5)
sock.connect((host, port))
sock.sendall(cmd)

chunks = []
while True:
    chunk = sock.recv(16384)
    if not chunk:
        break
    chunks.append(chunk)
    try:
        json.loads(b"".join(chunks).decode())
        break
    except json.JSONDecodeError:
        continue
sock.close()

data = json.loads(b"".join(chunks).decode())
if data.get("status") != "success":
    print(data.get("message", "extension ping failed"), file=sys.stderr)
    sys.exit(1)
result = data.get("result", {})
print(f"prim_count={result.get('prim_count', '?')}")
PY
}

wait_ready() {
  if ! mcp_cli_ready; then
    echo "❌ 未找到 MCP Server，请先运行: ${ROOT}/scripts/setup_mcp.sh"
    return 1
  fi

  echo "等待 Isaac MCP Extension (${ISAAC_SIM_HOST}:${ISAAC_SIM_PORT})..."
  if ! wait_for_extension 90; then
    echo "❌ Extension 端口未就绪"
    return 1
  fi

  if ping_extension; then
    echo "✅ Isaac MCP Extension 已就绪"
    return 0
  fi

  echo "❌ Extension 无响应"
  return 1
}

stop_mcp() {
  if [[ -f "${PIDFILE}" ]]; then
    local pid
    pid="$(cat "${PIDFILE}")"
    if kill -0 "${pid}" 2>/dev/null; then
      kill "${pid}" 2>/dev/null || true
      for _ in $(seq 1 20); do
        kill -0 "${pid}" 2>/dev/null || break
        sleep 0.2
      done
      if kill -0 "${pid}" 2>/dev/null; then
        kill -9 "${pid}" 2>/dev/null || true
      fi
      echo "MCP Server 已停止 (pid ${pid})"
    fi
    rm -f "${PIDFILE}"
  fi
}

start_daemon() {
  if ! mcp_cli_ready; then
    echo "❌ 未找到 MCP Server，请先运行: ${ROOT}/scripts/setup_mcp.sh"
    return 1
  fi

  stop_mcp
  mkdir -p "$(dirname "${LOGFILE}")"

  if ! wait_ready; then
    return 1
  fi

  echo ""
  echo "MCP Server 后台启动 (SSE)..."
  echo "  Cursor 连接: http://${MCP_SSE_HOST}:${MCP_SSE_PORT}/sse"
  echo "  Isaac Extension: ${ISAAC_SIM_HOST}:${ISAAC_SIM_PORT}"
  echo "  日志: ${LOGFILE}"

  # stdio 模式无法在后台常驻；使用 SSE HTTP 服务
  nohup "${PYTHON}" "${SSE_ENTRY}" >>"${LOGFILE}" 2>&1 &
  echo $! >"${PIDFILE}"

  for _ in $(seq 1 30); do
    if port_open "${MCP_SSE_HOST}" "${MCP_SSE_PORT}"; then
      local pid
      pid="$(cat "${PIDFILE}")"
      echo "✅ MCP Server 已启动 (pid ${pid})"
      return 0
    fi
    if ! kill -0 "$(cat "${PIDFILE}")" 2>/dev/null; then
      break
    fi
    sleep 0.5
  done

  echo "❌ MCP Server 启动失败，查看日志: ${LOGFILE}"
  rm -f "${PIDFILE}"
  tail -20 "${LOGFILE}" 2>/dev/null || true
  return 1
}

show_status() {
  if [[ -f "${PIDFILE}" ]]; then
    local pid
    pid="$(cat "${PIDFILE}")"
    if kill -0 "${pid}" 2>/dev/null; then
      echo "MCP Server 运行中 (pid ${pid})"
      echo "  SSE: http://${MCP_SSE_HOST}:${MCP_SSE_PORT}/sse"
      echo "  Extension: ${ISAAC_SIM_HOST}:${ISAAC_SIM_PORT}"
      echo "  日志: ${LOGFILE}"
      return 0
    fi
  fi
  echo "MCP Server 未运行"
  return 1
}

case "${1:-}" in
  --daemon)
    start_daemon
    ;;
  --stop)
    stop_mcp
    ;;
  --status)
    show_status
    ;;
  --wait-ready)
    wait_ready
    ;;
  -h | --help)
    echo "用法: $0 [--daemon | --stop | --status | --wait-ready]"
    ;;
  *)
    if ! [[ -x "${CLI}" ]]; then
      echo "❌ 未找到 MCP Server，请先运行: ${ROOT}/scripts/setup_mcp.sh"
      exit 1
    fi
    echo "MCP Server 启动中 (stdio)..."
    echo "  连接 Isaac Sim Extension: ${ISAAC_SIM_HOST}:${ISAAC_SIM_PORT}"
    exec "${CLI}"
    ;;
esac
