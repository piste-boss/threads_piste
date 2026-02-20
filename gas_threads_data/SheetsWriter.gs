/**
 * SheetsWriter.gs - Google Sheets書き込み
 * 
 * Makeシナリオ threads_data の Google Sheets[13] モジュール相当：
 *   スプレッドシート: Piste_instagram_Data
 *   シート: Threads_Data
 * 
 * カラム構成:
 *   A: 日付        B: 本文
 *   C: いいね      D: 引用
 *   E: リポスト    F: インプレッション
 *   G: コメント欄1 H: コメント欄2
 *   I: コメント欄3 J: コメント欄4
 */

/**
 * スプレッドシートとシートを取得（なければ作成）
 * @return {Sheet} Google Sheetsのシートオブジェクト
 */
function getOrCreateSheet() {
  // 名前でスプレッドシートを検索
  const files = DriveApp.getFilesByName(SPREADSHEET_NAME);
  
  let spreadsheet;
  if (files.hasNext()) {
    spreadsheet = SpreadsheetApp.open(files.next());
    Logger.log('既存スプレッドシートを使用: ' + spreadsheet.getName());
  } else {
    spreadsheet = SpreadsheetApp.create(SPREADSHEET_NAME);
    Logger.log('新規スプレッドシートを作成: ' + spreadsheet.getName());
  }
  
  // シートを取得（なければ作成）
  let sheet = spreadsheet.getSheetByName(SHEET_NAME);
  if (!sheet) {
    sheet = spreadsheet.insertSheet(SHEET_NAME);
    // ヘッダー行を設定
    sheet.getRange(1, 1, 1, 10).setValues([[
      '日付', '本文', 'いいね', '引用', 'リポスト', 'インプレッション',
      'コメント欄1', 'コメント欄2', 'コメント欄3', 'コメント欄4'
    ]]);
    // ヘッダー行を太字に
    sheet.getRange(1, 1, 1, 10).setFontWeight('bold');
    Logger.log('新規シートを作成: ' + SHEET_NAME);
  }
  
  return sheet;
}


/**
 * シート上に同じ投稿が既に存在するか確認（重複防止）
 * タイムスタンプと本文の先頭部分で判定
 * @param {Sheet} sheet シートオブジェクト
 * @param {string} timestamp 投稿タイムスタンプ
 * @param {string} text 投稿本文
 * @return {boolean} 重複していればtrue
 */
function isDuplicate(sheet, timestamp, text) {
  const lastRow = sheet.getLastRow();
  if (lastRow <= 1) return false; // ヘッダーのみ
  
  // A列（日付）の全データを取得してチェック
  const dateRange = sheet.getRange(2, 1, lastRow - 1, 2).getValues();
  const textPrefix = text ? text.substring(0, 30) : '';
  
  for (let i = 0; i < dateRange.length; i++) {
    const existingDate = String(dateRange[i][0]);
    const existingText = String(dateRange[i][1]);
    
    // タイムスタンプが一致 OR 本文の先頭30文字が一致
    if (existingDate === timestamp || 
        (textPrefix && existingText.substring(0, 30) === textPrefix)) {
      return true;
    }
  }
  
  return false;
}


/**
 * 投稿データをシートに書き込み
 * @param {Sheet} sheet シートオブジェクト
 * @param {Object} rowData 書き込むデータ
 *   {timestamp, text, likes, quotes, reposts, views, comment1}
 */
function appendRowData(sheet, rowData) {
  sheet.appendRow([
    rowData.timestamp || '',   // A: 日付
    rowData.text || '',        // B: 本文
    rowData.likes || 0,        // C: いいね
    rowData.quotes || 0,       // D: 引用
    rowData.reposts || 0,      // E: リポスト
    rowData.views || 0,        // F: インプレッション
    rowData.comment1 || '',    // G: コメント欄1
    '',                        // H: コメント欄2（未使用）
    '',                        // I: コメント欄3（未使用）
    ''                         // J: コメント欄4（未使用）
  ]);
}
