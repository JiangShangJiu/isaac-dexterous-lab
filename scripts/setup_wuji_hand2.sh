#!/bin/bash
# 克隆 Wuji Hand 2 USD 资产到 assets/wuji-description
set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DEST="${ROOT_DIR}/assets/wuji-description"
REPO="https://github.com/wuji-technology/wuji-description.git"

if [[ -f "${DEST}/hand2/body/usd/right/wujihand.usd" ]]; then
  echo "✅ Wuji Hand 2 资产已存在: ${DEST}"
  exit 0
fi

echo ">>> 克隆 wuji-description ..."
mkdir -p "${ROOT_DIR}/assets"
git clone --depth 1 "${REPO}" "${DEST}"

if [[ ! -f "${DEST}/hand2/body/usd/right/wujihand.usd" ]]; then
  echo "❌ 未找到 hand2 USD，请检查仓库结构是否更新"
  exit 1
fi

echo "✅ Wuji Hand 2 资产已就绪"
echo "   右手: hand2/body/usd/right/wujihand.usd"
echo "   左手: hand2/body/usd/left/wujihand.usd"
echo "   启动: ./restart.sh wuji_hand2"
