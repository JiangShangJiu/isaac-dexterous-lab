#!/bin/bash
# 改完代码后一键重启（日常开发用这个）
# 用法: ./restart.sh [场景名]    例: ./restart.sh franka
#       ./restart.sh list        列出所有场景
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck disable=SC1091
source "${SCRIPT_DIR}/scripts/resolve_scene.sh"

case "${1:-}" in
  list | --list | -l | help | --help | -h)
    resolve_scene "$1"
    ;;
  "")
    export ENTRY_SCRIPT="$(resolve_scene "")"
    ;;
  *)
    export ENTRY_SCRIPT="$(resolve_scene "$1")"
    ;;
esac

echo ">>> 场景: ${ENTRY_SCRIPT}"
exec "${SCRIPT_DIR}/scripts/docker_run.sh"
