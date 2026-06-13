#!/bin/bash
# 安装 Isaac Sim MCP（扩展 + 宿主机 MCP Server）
set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MCP_REPO="${ROOT}/mcp/isaacsim-mcp-server"
VENV="${ROOT}/mcp/.venv"

echo ">>> [1/2] 克隆 isaacsim-mcp-server..."
if [[ ! -f "${MCP_REPO}/isaac.sim.mcp_extension/config/extension.toml" ]]; then
  mkdir -p "${ROOT}/mcp"
  git clone --depth 1 https://github.com/whats2000/isaacsim-mcp-server.git "${MCP_REPO}"
else
  echo "    已存在，跳过克隆"
fi

echo ">>> [2/2] 安装 MCP Server（宿主机 Python venv）..."
if [[ ! -d "${VENV}" ]]; then
  python3 -m venv "${VENV}"
fi
"${VENV}/bin/pip" install -q --upgrade pip
"${VENV}/bin/pip" install -q isaacsim-mcp-server

echo ""
echo "✅ MCP 安装完成"
echo "   ./restart.sh franka   # 启动 Isaac Sim + MCP Server（SSE 后台）"
echo "   Cursor: Settings → MCP → isaac-sim（http://127.0.0.1:8767/sse）"
