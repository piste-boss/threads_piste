/**
 * Main.gs - メインフロー（MAKEシナリオの完全な置き換え）
 * 
 * piste_threds_auto_post シナリオの再現：
 *   1. Notionから投稿待ちレコードを1件取得
 *   2. 画像あり/なしで分岐
 *   3. Threadsに投稿（Container → Sleep → Publish）
 *   4. コメント欄の内容を返信として投稿
 *   5. Notionのステータスを更新
 */

/**
 * メイン実行関数（トリガーから呼び出される）
 * MAKEの「Every 6 hours」スケジュールを置き換え
 */
function publishScheduledPost() {
  Logger.log('========================================');
  Logger.log('Piste Threads Auto Post - GAS版');
  Logger.log('実行日時: ' + new Date().toLocaleString('ja-JP', {timeZone: 'Asia/Tokyo'}));
  Logger.log('========================================');
  
  // ── 認証チェック ──
  if (!getThreadsToken() || !getNotionApiKey()) {
    Logger.log('❌ エラー: スクリプトプロパティに認証情報が設定されていません');
    Logger.log('   THREADS_ACCESS_TOKEN と NOTION_API_KEY を設定してください');
    return;
  }
  
  // ── Step 1: Notionから投稿待ちレコードを取得 ──
  Logger.log('\n[Step 1] Notionデータベースから投稿待ちレコードを取得...');
  const page = fetchNextPost();
  
  if (!page) {
    Logger.log('投稿待ちのレコードがありません。処理を終了します。');
    return;
  }
  
  // ── Step 2: 投稿データを抽出 ──
  const postData = extractPostData(page);
  Logger.log('\n[Step 2] 投稿データ抽出:');
  Logger.log('  タイトル: ' + postData.title);
  Logger.log('  本文: ' + (postData.body ? postData.body.substring(0, 50) + '...' : '(空)'));
  Logger.log('  コメント: ' + (postData.comment ? postData.comment.substring(0, 50) + '...' : '(空)'));
  Logger.log('  画像URL: ' + (postData.imageUrl || '(なし)'));
  
  // 本文がない場合はスキップ
  if (!postData.body) {
    Logger.log('❌ 本文が空のためスキップします');
    return;
  }
  
  // ── Step 3: Threads Container作成（画像あり/なし分岐） ──
  let creationId;
  
  if (postData.imageUrl) {
    Logger.log('\n[Step 3] 画像ありルート → IMAGE Containerを作成...');
    creationId = createImageContainer(postData.body, postData.imageUrl);
  } else {
    Logger.log('\n[Step 3] 画像なしルート → TEXT Containerを作成...');
    creationId = createTextContainer(postData.body);
  }
  
  if (!creationId) {
    Logger.log('❌ Container作成に失敗しました');
    return;
  }
  
  // ── Step 4: 待機（MAKEのSleepモジュール相当） ──
  Logger.log('\n[Step 4] Container処理待機 (' + (SLEEP_AFTER_CONTAINER_MS / 1000) + '秒)...');
  Utilities.sleep(SLEEP_AFTER_CONTAINER_MS);
  
  // ── Step 5: Publish ──
  Logger.log('\n[Step 5] 投稿をPublish...');
  const publishedId = publishContainer(creationId);
  
  if (!publishedId) {
    Logger.log('❌ Publishに失敗しました');
    return;
  }
  
  Logger.log('✅ 投稿が公開されました！ ID: ' + publishedId);
  
  // ── Step 6: コメント欄の返信投稿 ──
  if (postData.comment) {
    Logger.log('\n[Step 6] コメント欄を返信として投稿...');
    
    // Publish後に少し待機
    Utilities.sleep(SLEEP_AFTER_PUBLISH_MS);
    
    const replyId = postReply(publishedId, postData.comment);
    
    if (replyId) {
      Logger.log('✅ コメント投稿成功: ' + replyId);
    } else {
      Logger.log('⚠️ コメント投稿に失敗（本投稿は成功済み）');
    }
  } else {
    Logger.log('\n[Step 6] コメント欄なし → スキップ');
  }
  
  // ── Step 7: Notionステータス更新 ──
  Logger.log('\n[Step 7] Notionステータスを「' + STATUS_POSTED + '」に更新...');
  updateNotionStatus(postData.pageId, STATUS_POSTED);
  
  Logger.log('\n========================================');
  Logger.log('✨ 処理完了！');
  Logger.log('  投稿: ' + postData.title);
  Logger.log('  Threads ID: ' + publishedId);
  Logger.log('========================================');
}


/**
 * テスト用：Notionからデータ取得のみ（投稿はしない）
 * 初回セットアップ時に使用
 */
function testFetchPost() {
  Logger.log('=== テスト: Notionから投稿データ取得 ===');
  
  if (!getNotionApiKey()) {
    Logger.log('❌ NOTION_API_KEY がスクリプトプロパティに設定されていません');
    return;
  }
  
  const page = fetchNextPost();
  
  if (!page) {
    Logger.log('投稿待ちのレコードはありません');
    return;
  }
  
  const data = extractPostData(page);
  Logger.log('タイトル: ' + data.title);
  Logger.log('本文: ' + data.body);
  Logger.log('コメント: ' + data.comment);
  Logger.log('画像URL: ' + data.imageUrl);
  Logger.log('ページID: ' + data.pageId);
  Logger.log('=== テスト完了 ===');
}


/**
 * 6時間ごとのトリガーを設定
 * GASエディタからこの関数を1回実行するだけでOK
 */
function setupTrigger() {
  // 既存のトリガーを削除
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'publishScheduledPost') {
      ScriptApp.deleteTrigger(trigger);
      Logger.log('既存のトリガーを削除しました');
    }
  });
  
  // 6時間ごとのトリガーを作成
  ScriptApp.newTrigger('publishScheduledPost')
    .timeBased()
    .everyHours(6)
    .create();
  
  Logger.log('✅ トリガーを設定しました: publishScheduledPost を6時間ごとに実行');
}


/**
 * トリガーを削除
 */
function removeTrigger() {
  const triggers = ScriptApp.getProjectTriggers();
  triggers.forEach(trigger => {
    if (trigger.getHandlerFunction() === 'publishScheduledPost') {
      ScriptApp.deleteTrigger(trigger);
    }
  });
  Logger.log('✅ トリガーを削除しました');
}
