#!/bin/bash
# 首次启动
# 用法: ./start.sh [场景名] [--follow-logs]
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
scene=""
follow_logs=false

for arg in "$@"; do
  case "$arg" in
    --follow-logs) follow_logs=true ;;
    list | --list | -l) scene="$arg" ;;
    -h | --help | help) scene="help" ;;
    *)
      if [[ -z "$scene" ]]; then
        scene="$arg"
      fi
      ;;
  esac
done

if [[ -n "$scene" ]]; then
  "${SCRIPT_DIR}/restart.sh" "$scene"
else
  "${SCRIPT_DIR}/restart.sh"
fi

if $follow_logs; then
  sudo docker logs -f isaac-sim-robot
fi
