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
WEEK_START=$(date -v+mon '+%Y年%m月%d日')
WEEK_END=$(date -v+sun '+%Y年%m月%d日')

cat > "$AGENT_REQUEST_FILE" << EOF
🤖 Antigravityエージェントへのタスク依頼

実行日時: $(date '+%Y年%m月%d日 %H:%M:%S')

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 実行してほしいタスク
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

以下のコマンドを実行してください：

/piste_threads_full_run

または、以下の手順を実行：

1. Piste_threads_report.mdの最新分析結果を読む
2. ${WEEK_START}〜${WEEK_END}の1週間分の投稿案を作成
   - 1日3投稿（6:00, 12:00, 18:00）× 7日 = 21投稿
   - Piste_threads_post.mdに追記
   - Piste_threads_image_prompt.mdに画像プロンプトを追記
3. Notionに同期（python3 notion＿post_script/piste_threads_notion.py）
4. 画像を生成（generate_imageツール使用）
5. 画像をGoogleドライブにアップロード
6. NotionにURLを同期

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 準備完了データ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ Piste_threads_report.md - 最新分析完了
✅ スプレッドシートデータ同期済み
⏳ 投稿案作成待ち
⏳ 画像生成待ち

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
EOF

log "📝 Agent task request created: $AGENT_REQUEST_FILE"

# デスクトップにもコピー
cp "$AGENT_REQUEST_FILE" ~/Desktop/

# macOS通知
osascript << APPLESCRIPT
display notification "データ分析完了。Antigravityで /piste_threads_full_run を実行してください" with title "Piste Threads" subtitle "エージェント実行準備完了" sound name "Glass"
APPLESCRIPT

# AI StudioをブラウザでWake up（オプション）
# open "https://aistudio.google.com/app/prompts/new_chat"

log "========================================="
log "✨ Minimal Automation Complete!"
log "📌 Next: Run /piste_threads_full_run in Antigravity"
log "========================================="

exit 0
