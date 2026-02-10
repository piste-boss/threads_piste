#!/bin/bash

# ==============================================================================
# trigger_agent_image_generation.sh
# 
# Antigravityエージェントに画像生成を依頼するトリガースクリプト
# （実験的：Cursor/VSCodeのコマンドラインから実行する場合）
# ==============================================================================

BASE_DIR="/Users/ishikawasuguru/Threads_piste"
LOG_FILE="$BASE_DIR/autopost.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "🤖 Attempting to trigger Antigravity agent..."

# Method 1: ブラウザでAntigravityを開く（手動操作が必要）
open "https://aistudio.google.com/app/prompts/new_chat"

# Method 2: macOS通知で指示を出す
osascript -e 'display notification "Please run: /piste_threads_full_run in Antigravity" with title "Image Generation Required" sound name "Hero"'

# Method 3: 通知ファイルをデスクトップにも配置（目立つように）
cp "$BASE_DIR/IMAGE_GENERATION_NEEDED.txt" ~/Desktop/

log "✅ Agent trigger notification sent"
log "📌 Next: Open Antigravity and run /piste_threads_full_run"

exit 0
