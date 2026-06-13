#!/bin/bash
# 将场景名解析为 demos/ 下的入口脚本路径
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEMOS_DIR="${ROOT_DIR}/demos"
DEFAULT_SCENE="franka"

list_scenes() {
  echo "可用场景："
  local found=0
  for f in "${DEMOS_DIR}"/*.py; do
    [[ -f "$f" ]] || continue
    local name
    name="$(basename "$f" .py)"
    [[ "$name" == _* ]] && continue
    found=1
    local suffix=""
    [[ "$name" == "${DEFAULT_SCENE}_livestream" ]] && suffix=" (默认)"
    echo "  ${name%_livestream}${suffix}  →  demos/$(basename "$f")"
  done
  if [[ "$found" -eq 0 ]]; then
    echo "  (无) 请在 demos/ 下添加 .py 文件"
  fi
  echo ""
  echo "用法: ./restart.sh [场景名]"
  echo "示例: ./restart.sh franka"
}

resolve_scene() {
  local name="${1:-$DEFAULT_SCENE}"

  case "$name" in
    list | --list | -l | help | --help | -h)
      list_scenes
      exit 0
      ;;
  esac

  if [[ -f "${DEMOS_DIR}/${name}.py" ]]; then
    echo "demos/${name}.py"
    return 0
  fi

  if [[ -f "${DEMOS_DIR}/${name}_livestream.py" ]]; then
    echo "demos/${name}_livestream.py"
    return 0
  fi

  echo "❌ 未知场景: ${name}" >&2
  echo "" >&2
  list_scenes >&2
  exit 1
}

if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  resolve_scene "$@"
fi
