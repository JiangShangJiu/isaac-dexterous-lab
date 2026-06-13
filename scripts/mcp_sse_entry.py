#!/usr/bin/env python3
"""Isaac MCP Server — SSE 模式（供 restart.sh 后台常驻，Cursor 通过 URL 连接）。"""

import os

from isaac_mcp.server import mcp

mcp.settings.host = os.environ.get("MCP_SSE_HOST", "127.0.0.1")
mcp.settings.port = int(os.environ.get("MCP_SSE_PORT", "8767"))
mcp.run(transport="sse")
