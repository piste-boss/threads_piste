/**
 * Config.gs - threads_data 設定・定数
 * 
 * GASデプロイ後にスクリプトプロパティへ以下を設定してください：
 *   THREADS_ACCESS_TOKEN : Threads Graph APIのアクセストークン
 * 
 * スクリプトプロパティの設定方法（GASエディタ）：
 *   プロジェクトの設定 → スクリプトプロパティ → プロパティを追加
 */

// ─── Threads API 設定 ───
const THREADS_API_BASE = 'https://graph.threads.net/v1.0';

// 投稿一覧取得時に要求するフィールド
const THREADS_FIELDS = 'id,permalink,text,timestamp,like_count,repost_count,quote_count';

// Insights で取得するメトリクス
const INSIGHTS_METRICS = 'views,likes,reposts,quotes';

// Replies で取得するフィールド
const REPLIES_FIELDS = 'text,username,timestamp';

// ─── Google Sheets 設定 ───
const SPREADSHEET_NAME = 'Piste_instagram_Data';
const SHEET_NAME = 'Threads_Data';

// ─── フィルター設定 ───
// コメント欄に自分（piste_boss）の返信のみ抽出
const THREADS_USER_NAME = 'piste_boss';

// ─── API レート制限対策（ミリ秒） ───
const API_DELAY_MS = 500; // 各API呼び出し間の待機時間

/**
 * スクリプトプロパティからアクセストークンを取得
 */
function getThreadsToken() {
  return PropertiesService.getScriptProperties().getProperty('THREADS_ACCESS_TOKEN');
}
