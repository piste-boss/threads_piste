/**
 * NotionAPI.gs - Notion API連携
 */

/**
 * Notionデータベースから投稿待ちレコードを1件取得
 * フィルタ: ステータス = 「未着手」 AND 投稿日 ≤ 現在時刻
 * @return {Object|null} ページオブジェクト（該当なしの場合null）
 */
function fetchNextPost() {
  const now = new Date().toISOString();
  
  const payload = {
    filter: {
      and: [
        {
          property: PROP_STATUS,
          status: {
            equals: STATUS_NOT_STARTED
          }
        },
        {
          property: PROP_DATE,
          date: {
            on_or_before: now
          }
        }
      ]
    },
    sorts: [
      {
        property: PROP_DATE,
        direction: 'ascending'
      }
    ],
    page_size: 1
  };
  
  const options = {
    method: 'post',
    headers: {
      'Authorization': 'Bearer ' + getNotionApiKey(),
      'Notion-Version': NOTION_API_VERSION,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const url = 'https://api.notion.com/v1/databases/' + NOTION_DATABASE_ID + '/query';
  const response = UrlFetchApp.fetch(url, options);
  const data = JSON.parse(response.getContentText());
  
  if (response.getResponseCode() !== 200) {
    Logger.log('Notion API Error: ' + response.getContentText());
    return null;
  }
  
  if (!data.results || data.results.length === 0) {
    Logger.log('投稿待ちのレコードはありません');
    return null;
  }
  
  return data.results[0];
}


/**
 * Notionページからプロパティ値を抽出
 * @param {Object} page Notionページオブジェクト
 * @return {Object} 抽出されたデータ {title, body, comment, imageUrl, pageId}
 */
function extractPostData(page) {
  const props = page.properties;
  
  // タイトル
  let title = '';
  if (props[PROP_TITLE] && props[PROP_TITLE].title) {
    title = props[PROP_TITLE].title.map(t => t.plain_text).join('');
  }
  
  // 本文
  let body = '';
  if (props[PROP_BODY] && props[PROP_BODY].rich_text) {
    body = props[PROP_BODY].rich_text.map(t => t.plain_text).join('');
  }
  
  // コメント欄
  let comment = '';
  if (props[PROP_COMMENT] && props[PROP_COMMENT].rich_text) {
    comment = props[PROP_COMMENT].rich_text.map(t => t.plain_text).join('');
  }
  
  // 画像URL（URL, URL2, URL3 の3プロパティから取得）
  const imageUrls = [];
  [PROP_IMAGE_URL, PROP_IMAGE_URL2, PROP_IMAGE_URL3].forEach(propName => {
    const urlProp = props[propName];
    if (!urlProp) return;
    let url = '';
    if (urlProp.type === 'url' && urlProp.url) {
      url = urlProp.url;
    } else if (urlProp.type === 'rich_text' && urlProp.rich_text && urlProp.rich_text.length > 0) {
      url = urlProp.rich_text.map(t => t.plain_text).join('');
    }
    if (url.trim()) {
      imageUrls.push(url.trim());
    }
  });

  return {
    pageId: page.id,
    title: title,
    body: body,
    comment: comment,
    imageUrls: imageUrls
  };
}


/**
 * Notionページのステータスを更新
 * @param {string} pageId ページID
 * @param {string} status 新しいステータス値
 */
function updateNotionStatus(pageId, status) {
  const payload = {
    properties: {
      [PROP_STATUS]: {
        status: {
          name: status
        }
      }
    }
  };
  
  const options = {
    method: 'patch',
    headers: {
      'Authorization': 'Bearer ' + getNotionApiKey(),
      'Notion-Version': NOTION_API_VERSION,
      'Content-Type': 'application/json'
    },
    payload: JSON.stringify(payload),
    muteHttpExceptions: true
  };
  
  const url = 'https://api.notion.com/v1/pages/' + pageId;
  const response = UrlFetchApp.fetch(url, options);
  
  if (response.getResponseCode() === 200) {
    Logger.log('✅ ステータスを「' + status + '」に更新しました: ' + pageId);
  } else {
    Logger.log('❌ ステータス更新失敗: ' + response.getContentText());
  }
}
