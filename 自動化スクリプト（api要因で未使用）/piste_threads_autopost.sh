#!/bin/bash

# ==============================================================================
# piste_threads_autopost.sh
# 
# Piste Threads Weekly Automation Script
# Runs every Thursday at 20:00 (via launchd/cron) to:
# 1. Analyze data & Update Report (process_threads_data.py)
# 2. Generate New Posts & Prompts (generate_content.py)
# 3. Sync Posts to Notion (piste_threads_notion.py)
# 4. Generate Images (generate_images_api.py)
# 5. Upload Images to Google Drive (piste_threads_image_uplorder.py)
# ==============================================================================

# Directory Setup
BASE_DIR="/Users/ishikawasuguru/Threads_piste"
LOG_FILE="$BASE_DIR/autopost.log"

# Load Environment Variables (API Keys)
if [ -f "$BASE_DIR/90_System/.env" ]; then
    export $(grep -v '^#' "$BASE_DIR/90_System/.env" | xargs)
fi

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log "Starting Piste Threads Automation..."

cd "$BASE_DIR" || exit 1

# ------------------------------------------------------------------------------
# 1. Data Analysis & Reporting
# ------------------------------------------------------------------------------
log "Step 1: Processing Threads Data..."
python3 process_threads_data.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "Error in Step 1. Exiting."
    exit 1
fi

# ------------------------------------------------------------------------------
# 2. Generate Content (Posts & Prompts)
# ------------------------------------------------------------------------------
log "Step 2: Generating New Content..."
if [ -f "generate_content.py" ]; then
    python3 generate_content.py >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "Error in Step 2. Exiting."
        exit 1
    fi
else
    log "Warning: generate_content.py not found. Skipping generation."
fi

# ------------------------------------------------------------------------------
# 3. Sync to Notion
# ------------------------------------------------------------------------------
log "Step 3: Syncing to Notion..."
# Copy .env to notion_post_script if needed or use environment variable
cd notion＿post_script || exit 1
python3 piste_threads_notion.py "$BASE_DIR/Piste_threads_post.md" >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "Error in Step 3. Exiting."
    exit 1
fi
cd "$BASE_DIR" || exit 1

# ------------------------------------------------------------------------------
# 4. Generate Images
# ------------------------------------------------------------------------------
log "Step 4: Generating Images..."
if [ -f "generate_images_api.py" ]; then
    python3 generate_images_api.py >> "$LOG_FILE" 2>&1
    if [ $? -ne 0 ]; then
        log "Error in Step 4. Exiting."
        exit 1
    fi
else
    log "Warning: generate_images_api.py not found. Skipping image generation."
fi

# ------------------------------------------------------------------------------
# 5. Upload to Google Drive
# ------------------------------------------------------------------------------
log "Step 5: Uploading to Google Drive..."
cd image_upload || exit 1
python3 piste_threads_image_uplorder.py >> "$LOG_FILE" 2>&1
if [ $? -ne 0 ]; then
    log "Error in Step 5. Exiting."
    exit 1
fi
cd "$BASE_DIR" || exit 1

log "Automation Completed Successfully."
