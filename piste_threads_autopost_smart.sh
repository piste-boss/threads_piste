#!/bin/bash

# ==============================================================================
# piste_threads_autopost_smart.sh
# 
# Piste Threads Smart Automation Script
# 完全自動化（画像生成はエージェント依頼用に通知）
# ==============================================================================

BASE_DIR="/Users/ishikawasuguru/Threads_piste"
LOG_FILE="$BASE_DIR/autopost.log"
NOTIFICATION_FILE="$BASE_DIR/IMAGE_GENERATION_NEEDED.txt"

# 環境変数読み込み
if [ -f "$BASE_DIR/90_System/.env" ]; then
    export $(grep -v '^#' "$BASE_DIR/90_System/.env" | xargs)
fi

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "========================================="
log "Starting Piste Threads Smart Automation"
log "========================================="

cd "$BASE_DIR" || exit 1

# ------------------------------------------------------------------------------
# STEP 1: データ分析・レポート更新
# ------------------------------------------------------------------------------
log "STEP 1: Analyzing Threads Data..."
python3 process_threads_data.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "❌ Error in STEP 1. Exiting."
    osascript -e 'display notification "データ分析でエラーが発生しました" with title "Piste Threads Automation"'
    exit 1
fi
log "✅ STEP 1 Complete"

# ------------------------------------------------------------------------------
# STEP 2: 投稿文章・プロンプト生成（LLM API使用）
# ------------------------------------------------------------------------------
log "STEP 2: Generating Content..."

# generate_content.pyが存在する場合（OpenAI/Claude APIを使う場合）
if [ -f "generate_content.py" ]; then
    python3 generate_content.py >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "❌ Error in STEP 2. Exiting."
        osascript -e 'display notification "コンテンツ生成でエラーが発生しました" with title "Piste Threads Automation"'
        exit 1
    fi
    log "✅ STEP 2 Complete (API)"
else
    # generate_content.pyがない場合は、エージェントに依頼する旨を通知
    log "⚠️  generate_content.py not found."
    log "ℹ️  コンテンツ生成はエージェントに依頼してください。"
fi

# ------------------------------------------------------------------------------
# STEP 3: Notionへ同期
# ------------------------------------------------------------------------------
log "STEP 3: Syncing to Notion..."
cd "$BASE_DIR/notion＿post_script" || exit 1
python3 piste_threads_notion.py "$BASE_DIR/Piste_threads_post.md" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "❌ Error in STEP 3. Continuing..."
fi
cd "$BASE_DIR" || exit 1
log "✅ STEP 3 Complete"

# ------------------------------------------------------------------------------
# STEP 4: 画像生成準備完了通知
# ------------------------------------------------------------------------------
log "STEP 4: Preparing Image Generation Request..."

# 生成が必要なプロンプト数を確認
PROMPT_COUNT=$(grep -c "^\- \*\*[0-9]\{4\}-[0-9]\{2\}-[0-9]\{2\}" "$BASE_DIR/Piste_threads_image_prompt.md")

# 通知ファイル作成
cat > "$NOTIFICATION_FILE" << EOF
🎨 画像生成準備完了！

生成が必要な画像数: 約 ${PROMPT_COUNT} 枚

次のステップ：
1. Antigravityエージェントを開く
2. 以下のコマンドを実行：
   /piste_threads_full_run

または手動で：
   「Piste_threads_image_prompt.mdの新しいプロンプトで画像を生成して、
    Googleドライブにアップロードし、Notionに同期して」

生成日時: $(date '+%Y年%m月%d日 %H:%M')
EOF

log "📝 Notification file created: $NOTIFICATION_FILE"
log "📊 Prompts to generate: $PROMPT_COUNT"

# macOS通知を送信
osascript -e "display notification \"${PROMPT_COUNT}枚の画像生成が必要です。Antigravityで /piste_threads_full_run を実行してください\" with title \"Piste Threads\" subtitle \"画像生成準備完了\" sound name \"Glass\""

log "✅ STEP 4 Complete"

# ------------------------------------------------------------------------------
# 完了ログ
# ------------------------------------------------------------------------------
log "========================================="
log "✨ Automation Phase 1 Complete!"
log "次回実行: エージェントで画像生成・アップロード"
log "========================================="

exit 0
