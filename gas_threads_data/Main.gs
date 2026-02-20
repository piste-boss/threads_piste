/**
 * Main.gs - メインフロー（threads_data Makeシナリオの完全な置き換え）
 * 
 * Makeシナリオ threads_data の再現：
 *   1. Threads APIから投稿一覧を取得 (HTTP[1])
 *   2. 各投稿をループ (Iterator[10])
 *   3. 各投稿の Insights を取得 (HTTP[11])
 *   4. 各投稿の Replies を取得 (HTTP[15])
 *   5. Google Sheetsに行を追加 (Google Sheets[13])
 */

/**
 * メイン実行関数（トリガーから呼び出される）
 * Makeの「Custom schedule」スケジュールを置き換え
 */
function collectThreadsData() {
  Logger.log('========================================');
  Logger.log('Threads Data Collector - GAS版');
  Logger.log('実行日時: ' + new Date().toLocaleString('ja-JP', {timeZone: 'Asia/Tokyo'}));
  Logger.log('========================================');
  
  // ── 認証チェック ──
  if (!getThreadsToken()) {
    Logger.log('❌ エラー: THREADS_ACCESS_TOKEN がスクリプトプロパティに設定されていません');
    return;
  }
  
  // ── Step 1: 投稿一覧を取得（HTTP[1] 相当） ──
  Logger.log('\n[Step 1] Threads投稿一覧を取得...');
  const threads = fetchAllThreads();
  
  if (threads.length === 0) {
    Logger.log('取得する投稿がありません。処理を終了します。');
    return;
  }
  
  Logger.log('取得件数: ' + threads.length + '件');
  
  // ── シートを準備 ──
  const sheet = getOrCreateSheet();
  
  // ── Step 2-5: 各投稿をループ（Iterator[10] 相当） ──
  let newCount = 0;
  let skipCount = 0;
  
  for (let i = 0; i < threads.length; i++) {
    const thread = threads[i];
    Logger.log('\n[投稿 ' + (i + 1) + '/' + threads.length + '] ID: ' + thread.id);
    Logger.log('  本文: ' + (thread.text ? thread.text.substring(0, 50) + '...' : '(空)'));
    
    // ── 重複チェック ──
    if (isDuplicate(sheet, thread.timestamp, thread.text)) {
      Logger.log('  ⏭️ 既に登録済み → スキップ');
      skipCount++;
      continue;
    }
    
    // ── Step 3: Insights取得（HTTP[11] 相当） ──
    Utilities.sleep(API_DELAY_MS);
    const insights = fetchThreadInsights(thread.id);
    Logger.log('  📊 いいね: ' + insights.likes + ' / ビュー: ' + insights.views +
               ' / リポスト: ' + insights.reposts + ' / 引用: ' + insights.quotes);
    
    // ── Step 4: Replies取得（HTTP[15] 相当） ──
    Utilities.sleep(API_DELAY_MS);
    const replies = fetchThreadReplies(thread.id);
    const comment1 = filterPisteBossReplies(replies);
    Logger.log('  💬 返信: ' + replies.length + '件 / piste_boss: ' + (comment1 || '(なし)'));
    
    // ── Step 5: Google Sheetsに書き込み（Google Sheets[13] 相当） ──
    appendRowData(sheet, {
      timestamp: thread.timestamp,
      text: thread.text || '',
      likes: insights.likes,
      quotes: insights.quotes,
      reposts: insights.reposts,
      views: insights.views,
      comment1: comment1
    });
    
    newCount++;
    Logger.log('  ✅ Sheetsに追加完了');
  }
  
  Logger.log('\n========================================');
  Logger.log('✨ 処理完了！');
  Logger.log('  新規追加: ' + newCount + '件');
  Logger.log('  スキップ: ' + skipCount + '件（重複）');
  Logger.log('  合計処理: ' + threads.length + '件');
  Logger.log('========================================');
}


/**
 * テスト用：投稿一覧の取得のみ（書き込みなし）
 */
function testFetchThreads() {
  Logger.log('=== テスト: Threads投稿一覧取得 ===');
  
  if (!getThreadsToken()) {
    Logger.log('❌ THREADS_ACCESS_TOKEN が設定されていません');
    return;
  }
  
  const threads = fetchAllThreads();
  
  if (threads.length === 0) {
    Logger.log('投稿が見つかりません');
    return;
  }
  
  threads.forEach(function(t, i) {
    Logger.log('\n--- 投稿 ' + (i + 1) + ' ---');
    Logger.log('ID: ' + t.id);
    Logger.log('日時: ' + t.timestamp);
    Logger.log('本文: ' + (t.text ? t.text.substring(0, 100) : '(空)'));
    Logger.log('パーマリンク: ' + (t.permalink || ''));
  });
  
  Logger.log('\n=== テスト完了: ' + threads.length + '件取得 ===');
}


/**
 * テスト用：特定投稿のInsightsとRepliesを取得
 */
function testFetchInsightsAndReplies() {
  Logger.log('=== テスト: Insights & Replies取得 ===');
  
  if (!getThreadsToken()) {
    Logger.log('❌ THREADS_ACCESS_TOKEN が設定されていません');
    return;
  }
  
  // まず投稿一覧を取得して最初の1件を使う
  const threads = fetchAllThreads();
  if (threads.length === 0) {
    Logger.log('投稿が見つかりません');
    return;
  }
  
  const thread = threads[0];
  Logger.log('対象投稿: ' + thread.id);
  Logger.log('本文: ' + (thread.text ? thread.text.substring(0, 100) : '(空)'));
  
  // Insights
  const insights = fetchThreadInsights(thread.id);
  Logger.log('\n📊 Insights:');
  Logger.log('  いいね: ' + insights.likes);
  Logger.log('  引用: ' + insights.quotes);
  Logger.log('  リポスト: ' + insights.reposts);
  Logger.log('  ビュー: ' + insights.views);
  
  // Replies
  const replies = fetchThreadReplies(thread.id);
  Logger.log('\n💬 Replies: ' + replies.length + '件');
  replies.forEach(function(r, i) {
    Logger.log('  [' + (i + 1) + '] @' + r.username + ': ' + (r.text ? r.text.substring(0, 50) : ''));
  });
  
  const comment1 = filterPisteBossReplies(replies);
  Logger.log('\nコメント欄1: ' + (comment1 || '(piste_bossの返信なし)'));
  
  Logger.log('\n=== テスト完了 ===');
}


/**
 * 定期実行トリガーを設定（1日1回）
 * GASエディタからこの関数を1回実行するだけでOK
 */
function setupTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'collectThreadsData') {
      ScriptApp.deleteTrigger(trigger);
      Logger.log('既存のトリガーを削除しました');
    }
  });
  
  // 毎日午前9時に実行
  ScriptApp.newTrigger('collectThreadsData')
    .timeBased()
    .everyDays(1)
    .atHour(9)
    .create();
  
  Logger.log('✅ トリガーを設定しました: collectThreadsData を毎日午前9時に実行');
}


/**
 * トリガーを削除
 */
function removeTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(function(trigger) {
    if (trigger.getHandlerFunction() === 'collectThreadsData') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  Logger.log('✅ トリガーを削除しました');
}
