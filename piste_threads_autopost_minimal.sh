#!/bin/bash

# ==============================================================================
# piste_threads_autopost_minimal.sh
# 
# 最小限の自動化スクリプト（データ分析のみ）
# コンテンツ生成・画像生成はすべてエージェントに依頼
# ==============================================================================

BASE_DIR="/Users/ishikawasuguru/Threads_piste"
LOG_FILE="$BASE_DIR/autopost.log"
AGENT_REQUEST_FILE="$BASE_DIR/AGENT_TASK_REQUEST.txt"

if [ -f "$BASE_DIR/90_System/.env" ]; then
    export $(grep -v '^#' "$BASE_DIR/90_System/.env" | xargs)
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Piste Threads Minimal Automation"
log "========================================="

cd "$BASE_DIR" || exit 1

# ------------------------------------------------------------------------------
# STEP 1: データ分析のみ実行（これは完全自動化可能）
# ------------------------------------------------------------------------------
log "STEP 1: Analyzing Threads Data..."
python3 process_threads_data.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "❌ Error in data analysis. Exiting."
    osascript -e 'display notification "データ分析でエラーが発生しました" with title "Piste Threads"'
    exit 1
fi
log "✅ Data analysis complete"

# ------------------------------------------------------------------------------
# エージェントへのタスクリクエスト作成
# ------------------------------------------------------------------------------
cat > "$AGENT_REQUEST_FILE" << 'EOFTASK'
🤖 Piste Threads 自動化タスク

木曜20:00のデータ分析が完了しました。
以下のコマンドをAntigravityで実行してください：

Piste_threads_image_prompt.mdから画像を生成して、
Piste_threads_image/フォルダに保存してください。

完了後、以下を実行：
1. cd image_upload && python3 piste_threads_image_uplorder.py
2. python3 piste_threads_drive_to_notion.py

詳細: /piste_threads_full_run
EOFTASK

log "📝 Agent task request created: $AGENT_REQUEST_FILE"

# デスクトップにもコピー
cp "$AGENT_REQUEST_FILE" ~/Desktop/

# macOS通知
osascript << APPLESCRIPT
display notification "データ分析完了。Antigravityで画像生成を依頼してください" with title "Piste Threads" subtitle "エージェントタスク準備完了" sound name "Glass"
APPLESCRIPT

# AI StudioをブラウザでWake up（オプション）
# open "https://aistudio.google.com/app/prompts/new_chat"

log "========================================="
log "✨ Minimal Automation Complete!"
log "📌 Next: Run /piste_threads_full_run in Antigravity"
log "========================================="

exit 0
