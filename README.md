# Isaac Sim 仿真项目

基于 NVIDIA Isaac Sim 5.1.0 Docker，支持 WebRTC 远程查看。代码在宿主机编辑，Docker 容器内运行。

## 目录结构

```
code/
├── README.md              # 本文件
├── restart.sh             # 改完代码一键重启 ⭐
├── start.sh               # 首次启动
├── lib/
│   ├── config.py          # 启动配置、UI 缩放默认值
│   ├── livestream.py      # WebRTC 推流
│   ├── scene.py           # 场景、相机、机器人
│   ├── ui.py              # 界面缩放
│   └── mcp.py             # MCP Extension
├── demos/                 # 仿真入口脚本（每个文件可独立运行）
│   ├── franka_livestream.py   # 默认：Franka 机械臂演示
│   └── _template.py           # 新脚本模板
├── mcp/                       # MCP（setup_mcp.sh 安装）
│   ├── .venv/                 # MCP Server Python 环境
│   └── isaacsim-mcp-server/   # Omniverse Extension 源码
├── .cursor/
│   └── mcp.json               # Cursor MCP 配置
└── scripts/
    ├── docker_run.sh          # Docker 启动逻辑
    ├── run_mcp_server.sh      # MCP Server
    └── setup_mcp.sh           # MCP 安装
```

容器内路径：`/workspace/` ↔ 宿主机 `/home/ubuntu/code/`

## 日常开发流程

```bash
# 1. 在 Cursor 里改代码（lib/ 或 demos/）
# 2. 保存后按场景名重启
./restart.sh franka

# 3. WebRTC 连接 117.50.175.186
```

## 常用命令

| 命令 | 说明 |
|------|------|
| `./restart.sh` | 重启默认场景（franka） |
| `./restart.sh franka` | Franka 机械臂（默认） |
| `./restart.sh kuka_allegro` | Kuka iiwa7 + Allegro 灵巧手（单臂） |
| `./restart.sh allegro_hand` | Allegro 灵巧手（仅 hand）+ 桌子 + 方块 |
| `./restart.sh dual_kuka_allegro` | 双 Kuka+Allegro + 桌子 + 方块 |
| `./restart.sh bimanual` | OpenArm 双臂 + 桌子 + 方块 |
| `./restart.sh list` | 列出所有可用场景 |
| `./start.sh warehouse` | 首次启动指定场景 |
| `./start.sh --follow-logs` | 启动默认场景并跟踪日志 |
| `sudo docker logs -f isaac-sim-robot` | 查看运行日志 |
| `sudo docker stop isaac-sim-robot` | 停止仿真 |

## 写新场景

```bash
# 1. 从模板复制（文件名即场景名）
cp demos/_template.py demos/warehouse.py

# 2. 编辑 demos/warehouse.py

# 3. 按名字启动
./restart.sh warehouse
```

场景名规则：`warehouse` → `demos/warehouse.py`，若不存在则尝试 `demos/warehouse_livestream.py`。

### 调整 WebRTC 界面字体大小

默认 UI 放大 **2.0 倍**。启动时可通过环境变量修改：

```bash
UI_DPI_SCALE=2.0 ./restart.sh franka   # 放大 2 倍
UI_DPI_SCALE=1.0 ./restart.sh franka   # 恢复默认大小
```

也可直接改 `lib/config.py` 里的 `UI_DPI_SCALE` 默认值。

## MCP（Cursor 控制 Isaac Sim）

通过 [isaacsim-mcp-server](https://github.com/whats2000/isaacsim-mcp-server) 让 Cursor 用自然语言控制仿真（加载机器人、建场景、步进调试等）。

### 架构

```
Cursor  ←SSE 8767→  MCP Server（宿主机，restart.sh 自动后台拉起）
                    ↓ TCP 8766
               Docker 内 Isaac MCP Extension
```

### 首次安装

```bash
./scripts/setup_mcp.sh
```

### 日常使用（一个命令）

```bash
./restart.sh franka   # Isaac Sim + MCP Extension + MCP Server 一起就绪
```

然后在 Cursor **Settings → MCP** 启用 `isaac-sim`（`.cursor/mcp.json` 已配置 `http://127.0.0.1:8767/sse`）。

手动管理 MCP Server：

```bash
./scripts/run_mcp_server.sh --status
./scripts/run_mcp_server.sh --stop
./scripts/run_mcp_server.sh --daemon   # 单独拉起 SSE 后台
```

### Cursor 配置

项目已包含 `.cursor/mcp.json`。**Remote SSH 连到本云服务器**时，在 Cursor Settings → MCP 中应能看到 `isaac-sim`。

若 Cursor 在**本地电脑**、Isaac Sim 在云上，需 SSH 隧道（转发 MCP SSE 端口）：

```bash
ssh -L 8767:127.0.0.1:8767 ubuntu@117.50.175.186
```

然后在本地 Cursor 配置 MCP 连 `http://127.0.0.1:8767/sse`。

### 验证

在 Cursor 里让 AI 调用 `get_scene_info` 检查连接是否正常。

### 脚本结构约定

每个 `demos/*.py` 遵循固定顺序：

```python
from isaacsim import SimulationApp
simulation_app = SimulationApp(...)   # ① 必须最先

from lib.livestream import setup_livestream   # ② 再 import 其他
from lib.scene import create_world_with_ground, load_robot, ...

setup_livestream(simulation_app)      # ③ 配置 WebRTC
world = create_world_with_ground()    # ④ 搭建场景

while simulation_app._app.is_running():  # ⑤ 仿真循环
    world.step(render=True)
```

### lib/ 里有什么

| 模块 | 功能 |
|------|------|
| `lib/config.py` | 启动分辨率、`UI_DPI_SCALE` 默认值 |
| `lib/livestream.py` | `setup_livestream()` WebRTC 推流 |
| `lib/scene.py` | `create_world_with_ground()`、`load_robot()` 等 |
| `lib/mcp.py` | `setup_mcp()` 启用 MCP Extension |

`load_robot()` 内置机器人：`franka`、`ur10`，可在 `lib/scene.py` 的 `ROBOT_ASSETS` 里扩展。

## 环境信息

| 项目 | 值 |
|------|-----|
| Isaac Sim | 5.1.0 |
| Docker 镜像 | `nvcr.io/nvidia/isaac-sim:5.1.0` |
| GPU | RTX 4090 |
| 公网 IP | `117.50.175.186`（`/home/ubuntu/.env`） |

## WebRTC 连接

1. 下载 [WebRTC Streaming Client](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/manual_livestream_clients.html)
2. Server 填 `117.50.175.186`（只填 IP）
3. 安全组放行 TCP `49100`、UDP `47998`

## 宿主机 vs 容器

| 在哪 | 能做什么 |
|------|---------|
| 宿主机 `ubuntu@...` | 改代码、`./restart.sh`、`sudo docker ...` |
| 容器 `isaac-sim@...` | 只有 `./python.sh`，没有 docker/sudo |

## 默认空界面（不用 Python 脚本）

```bash
cd /home/ubuntu && sudo docker compose up -d
```

## 常见问题

**看不到机器人** → 确认用的是 `./restart.sh`，日志里有 `Franka 机械臂已加载`

**重启显示等待超时** → 容器可能还在加载（2-5 分钟），执行 `sudo docker logs -f isaac-sim-robot` 继续等

**停容器会重启云服务器吗** → 不会，只停 Docker 容器

## 参考

- [Isaac Sim 容器安装](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/installation/install_container.html)
- [Python 独立脚本](https://docs.isaacsim.omniverse.nvidia.com/5.1.0/python_scripting/manual_standalone_python.html)
