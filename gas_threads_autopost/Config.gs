/**
 * Config.gs - 設定・定数
 * 
 * GASデプロイ後にスクリプトプロパティへ以下を設定してください：
 *   THREADS_ACCESS_TOKEN : Threads Graph APIのアクセストークン
 *   NOTION_API_KEY       : Notion APIトークン
 * 
 * スクリプトプロパティの設定方法（GASエディタ）：
 *   プロジェクトの設定 → スクリプトプロパティ → プロパティを追加
 */

// ─── Notion 設定 ───
const NOTION_DATABASE_ID = '2efc991b-527b-8090-a546-c89a11a5455d';
const NOTION_API_VERSION = '2022-06-28';

// ─── Threads 設定 ───
const THREADS_API_BASE = 'https://graph.threads.net/v1.0';
const THREADS_CONTAINER_URL = THREADS_API_BASE + '/me/threads';
const THREADS_PUBLISH_URL  = THREADS_API_BASE + '/me/threads_publish';

// ─── 待機時間（ミリ秒） ───
// Threads APIはContainer作成→Publish間に待機が必要
const SLEEP_AFTER_CONTAINER_MS = 30000; // 30秒
const SLEEP_AFTER_PUBLISH_MS   = 10000; // 10秒
const SLEEP_BETWEEN_CAROUSEL_ITEMS_MS = 5000; // カルーセルアイテム間 5秒

// ─── Notion プロパティ名 ───
const PROP_TITLE    = 'タイトル';
const PROP_DATE     = '投稿日';
const PROP_BODY     = '本文';
const PROP_COMMENT  = 'コメント欄';
const PROP_STATUS   = 'ステータス';
const PROP_IMAGE_URL  = 'URL';
const PROP_IMAGE_URL2 = 'URL2';
const PROP_IMAGE_URL3 = 'URL3';

// ─── ステータス値 ───
const STATUS_NOT_STARTED = '未着手';
const STATUS_POSTED      = '完了';
const STATUS_ERROR       = 'エラー';

/**
 * スクリプトプロパティから認証情報を取得
 */
function getThreadsToken() {
  return PropertiesService.getScriptProperties().getProperty('THREADS_ACCESS_TOKEN');
}

function getNotionApiKey() {
  return PropertiesService.getScriptProperties().getProperty('NOTION_API_KEY');
}
