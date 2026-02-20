/**
 * ThreadsAPI.gs - Threads Graph API連携
 * 
 * Threads APIの投稿フロー（MAKEと同じ2段階方式）：
 *   1. Container作成 → creation_id を取得
 *   2. 待機（30秒）
 *   3. Publish → メディアIDを取得
 *   4. （コメントがある場合）返信として投稿
 */

/**
 * GoogleドライブのURLをThreads APIが読める直接URLに変換
 * @param {string} driveUrl Googleドライブの共有URL
 * @return {string} 直接アクセスURL
 */
function convertDriveUrlToDirectUrl(driveUrl) {
  if (!driveUrl) return '';
  
  // パターン1: https://drive.google.com/file/d/FILE_ID/view?...
  let match = driveUrl.match(/\/file\/d\/([a-zA-Z0-9_-]+)/);
  if (match) {
    return 'https://lh3.googleusercontent.com/d/' + match[1];
  }
  
  // パターン2: https://drive.google.com/open?id=FILE_ID
  match = driveUrl.match(/[?&]id=([a-zA-Z0-9_-]+)/);
  if (match) {
    return 'https://lh3.googleusercontent.com/d/' + match[1];
  }
  
  // パターン3: https://drive.google.com/uc?export=...&id=FILE_ID
  match = driveUrl.match(/uc\?.*id=([a-zA-Z0-9_-]+)/);
  if (match) {
    return 'https://lh3.googleusercontent.com/d/' + match[1];
  }
  
  // パターン4: 既にlh3形式
  if (driveUrl.includes('googleusercontent.com')) {
    return driveUrl;
  }
  
  // その他: そのまま返す
  return driveUrl;
}


/**
 * テキスト投稿のContainerを作成
 * @param {string} text 投稿テキスト
 * @return {string|null} creation_id
 */
function createTextContainer(text) {
  const token = getThreadsToken();
  
  const payload = {
    text: text,
    media_type: 'TEXT',
    access_token: token
  };
  
  const options = {
    method: 'post',
    payload: payload,
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(THREADS_CONTAINER_URL, options);
  const data = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() === 200 && data.id) {
    Logger.log('✅ TEXT Container作成: ' + data.id);
    return data.id;
  } else {
    Logger.log('❌ TEXT Container作成失敗: ' + response.getContentText());
    return null;
  }
}


/**
 * 画像付き投稿のContainerを作成
 * @param {string} text 投稿テキスト
 * @param {string} imageUrl 画像URL（公開アクセス可能なURL）
 * @return {string|null} creation_id
 */
function createImageContainer(text, imageUrl) {
  const token = getThreadsToken();
  
  // GoogleドライブURLを直接URLに変換
  const directUrl = convertDriveUrlToDirectUrl(imageUrl);
  Logger.log('画像URL変換: ' + imageUrl + ' → ' + directUrl);
  
  const payload = {
    text: text,
    media_type: 'IMAGE',
    image_url: directUrl,
    access_token: token
  };
  
  const options = {
    method: 'post',
    payload: payload,
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(THREADS_CONTAINER_URL, options);
  const data = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() === 200 && data.id) {
    Logger.log('✅ IMAGE Container作成: ' + data.id);
    return data.id;
  } else {
    Logger.log('❌ IMAGE Container作成失敗: ' + response.getContentText());
    return null;
  }
}


/**
 * Containerを公開（Publish）
 * @param {string} creationId Container作成時に取得したID
 * @return {string|null} 公開された投稿のID
 */
function publishContainer(creationId) {
  const token = getThreadsToken();
  
  const payload = {
    creation_id: creationId,
    access_token: token
  };
  
  const options = {
    method: 'post',
    payload: payload,
    muteHttpExceptions: true
  };
  
  const response = UrlFetchApp.fetch(THREADS_PUBLISH_URL, options);
  const data = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() === 200 && data.id) {
    Logger.log('✅ Publish成功: ' + data.id);
    return data.id;
  } else {
    Logger.log('❌ Publish失敗: ' + response.getContentText());
    return null;
  }
}


/**
 * 返信（コメント欄）を投稿
 * @param {string} replyToId 返信先の投稿ID
 * @param {string} text 返信テキスト
 * @return {string|null} 返信投稿のID
 */
function postReply(replyToId, text) {
  const token = getThreadsToken();
  
  // Step 1: 返信Containerを作成
  const containerPayload = {
    text: text,
    media_type: 'TEXT',
    reply_to_id: replyToId,
    access_token: token
  };
  
  const containerOptions = {
    method: 'post',
    payload: containerPayload,
    muteHttpExceptions: true
  };
  
  const containerResponse = UrlFetchApp.fetch(THREADS_CONTAINER_URL, containerOptions);
  const containerData = JSON.parse(containerResponse.getContentText());
  
  if (containerResponse.getResponseCode() !== 200 || !containerData.id) {
    Logger.log('❌ コメントContainer作成失敗: ' + containerResponse.getContentText());
    return null;
  }
  
  Logger.log('✅ コメントContainer作成: ' + containerData.id);
  
  // Step 2: 待機
  Utilities.sleep(SLEEP_AFTER_CONTAINER_MS);
  
  // Step 3: コメントをPublish
  const publishPayload = {
    creation_id: containerData.id,
    access_token: token
  };
  
  const publishOptions = {
    method: 'post',
    payload: publishPayload,
    muteHttpExceptions: true
  };
  
  const publishResponse = UrlFetchApp.fetch(THREADS_PUBLISH_URL, publishOptions);
  const publishData = JSON.parse(publishResponse.getContentText());
  
  if (publishResponse.getResponseCode() === 200 && publishData.id) {
    Logger.log('✅ コメントPublish成功: ' + publishData.id);
    return publishData.id;
  } else {
    Logger.log('❌ コメントPublish失敗: ' + publishResponse.getContentText());
    return null;
  }
}
