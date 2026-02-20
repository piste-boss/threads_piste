/**
 * ThreadsDataAPI.gs - Threads Graph API データ取得
 * 
 * Makeシナリオ threads_data の HTTP モジュール相当：
 *   1. HTTP[1]  → fetchAllThreads()     : 投稿一覧取得
 *   2. HTTP[11] → fetchThreadInsights()  : メトリクス取得
 *   3. HTTP[15] → fetchThreadReplies()   : 返信取得
 */

/**
 * 投稿一覧を取得（HTTP[1] 相当）
 * GET /me/threads?fields=id,permalink,text,timestamp,...
 * @return {Array} 投稿オブジェクトの配列
 */
function fetchAllThreads() {
  const token = getThreadsToken();
  const url = THREADS_API_BASE + '/me/threads'
    + '?fields=' + encodeURIComponent(THREADS_FIELDS)
    + '&access_token=' + encodeURIComponent(token);
  
  const options = {
    method: 'get',
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  
  if (response.getResponseCode() !== 200) {
    Logger.log('❌ 投稿一覧取得失敗: ' + response.getContentText());
    return [];
  }
  
  const data = JSON.parse(response.getContentText());
  
  if (!data.data || data.data.length === 0) {
    Logger.log('投稿データがありません');
    return [];
  }
  
  Logger.log('✅ 投稿一覧取得: ' + data.data.length + '件');
  return data.data;
}


/**
 * 特定投稿のInsights（メトリクス）を取得（HTTP[11] 相当）
 * GET /{thread_id}/insights?metric=views,likes,reposts,quotes
 * @param {string} threadId 投稿ID
 * @return {Object} {likes, quotes, reposts, views} のオブジェクト
 */
function fetchThreadInsights(threadId) {
  const token = getThreadsToken();
  const url = THREADS_API_BASE + '/' + threadId + '/insights'
    + '?metric=' + encodeURIComponent(INSIGHTS_METRICS)
    + '&access_token=' + encodeURIComponent(token);
  
  const options = {
    method: 'get',
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  
  // デフォルト値
  const result = {
    likes: 0,
    quotes: 0,
    reposts: 0,
    views: 0
  };
  
  if (response.getResponseCode() !== 200) {
    Logger.log('⚠️ Insights取得失敗 (ID: ' + threadId + '): ' + response.getContentText());
    return result;
  }
  
  const data = JSON.parse(response.getContentText());
  
  if (data.data && Array.isArray(data.data)) {
    data.data.forEach(function(metric) {
      // Makeの get(map(11.data[]; values.1.value; name; likes); 1) 相当
      const name = metric.name;
      const value = (metric.values && metric.values.length > 0) ? metric.values[0].value : 0;
      
      if (result.hasOwnProperty(name)) {
        result[name] = value;
      }
    });
  }
  
  return result;
}


/**
 * 特定投稿の返信を取得（HTTP[15] 相当）
 * GET /{thread_id}/replies?fields=text,username,timestamp
 * @param {string} threadId 投稿ID
 * @return {Array} 返信オブジェクトの配列
 */
function fetchThreadReplies(threadId) {
  const token = getThreadsToken();
  const url = THREADS_API_BASE + '/' + threadId + '/replies'
    + '?fields=' + encodeURIComponent(REPLIES_FIELDS)
    + '&access_token=' + encodeURIComponent(token);
  
  const options = {
    method: 'get',
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(url, options);
  
  if (response.getResponseCode() !== 200) {
    Logger.log('⚠️ Replies取得失敗 (ID: ' + threadId + '): ' + response.getContentText());
    return [];
  }
  
  const data = JSON.parse(response.getContentText());
  
  if (!data.data || data.data.length === 0) {
    return [];
  }
  
  return data.data;
}


/**
 * 返信から piste_boss のテキストのみ抽出して結合
 * Makeの join(map(15.Data.data[]; text; username; piste_boss); "; ") 相当
 * @param {Array} replies 返信オブジェクトの配列
 * @return {string} piste_boss の返信テキスト（セミコロン区切り）
 */
function filterPisteBossReplies(replies) {
  if (!replies || replies.length === 0) return '';
  
  const filtered = replies
    .filter(function(reply) {
      return reply.username === THREADS_USER_NAME;
    })
    .map(function(reply) {
      return reply.text;
    });
  
  return filtered.join('; ');
}
