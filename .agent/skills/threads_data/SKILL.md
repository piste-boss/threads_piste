---
name: threads_data
description: Threads投稿データ収集GASスクリプトの生成・セットアップスキル（Threads API → Google Sheets）
---

# Threads Data Collector (GAS)

Threads Graph APIから投稿データ・メトリクス（いいね、ビュー等）・返信を取得し、Google Sheetsに記録するGASプロジェクトを生成・セットアップします。

## 使用方法

### 基本コマンド
```
Threadsデータ収集のGASプロジェクトをセットアップしてください。
```

## 必要情報

以下の情報をユーザーに確認してください：

| 情報 | 必須 | 説明 |
|------|:---:|---------| 
| Threads APIアクセストークン（FBアクセストークン） | ✅ | Meta for Developers で発行。`THAAM5S...` 形式 |
| 出力先スプレッドシートURL | ✅ | データ書き込み先のGoogle SheetsのURL |

### 確認プロンプト例
```
GASセットアップに以下の情報が必要です：
1. Threads API（FB）アクセストークン
2. 出力先Google SheetsのURL（例: https://docs.google.com/spreadsheets/d/xxxxx/edit）
```

### スプレッドシートURLからIDを抽出する方法

URL例: `https://docs.google.com/spreadsheets/d/1aBcDeFgHiJkLmNoPqRsTuVwXyZ/edit`

`/d/` と `/edit` の間の文字列がスプレッドシートID：
```
1aBcDeFgHiJkLmNoPqRsTuVwXyZ
```

## 実行手順

### 1. GASファイルを生成

`gas_threads_data/` ディレクトリに以下の4ファイルを生成します。テンプレートは `scripts/` ディレクトリにあります。

| ファイル | 役割 |
|---------|------|
| `Config.gs` | 定数・認証情報・スプレッドシート設定 |
| `ThreadsDataAPI.gs` | Threads API連携（投稿一覧・Insights・Replies取得） |
| `SheetsWriter.gs` | Google Sheets書き込み・重複チェック |
| `Main.gs` | メインフロー・テスト・トリガー管理 |

**Config.gs のカスタマイズ箇所:**
```javascript
// スプレッドシートIDまたは名前をユーザー指定値に設定
const SPREADSHEET_ID = 'ユーザーが指定したスプレッドシートID';
// または名前で検索
const SPREADSHEET_NAME = 'Piste_instagram_Data';
const SHEET_NAME = 'Threads_Data';
```

### 2. ファイル生成のテンプレート

各ファイルの実装は以下の参照ファイルをベースに生成してください：

- [Config.gs](file:///Users/ishikawasuguru/Threads_piste/gas_threads_data/Config.gs)
- [ThreadsDataAPI.gs](file:///Users/ishikawasuguru/Threads_piste/gas_threads_data/ThreadsDataAPI.gs)
- [SheetsWriter.gs](file:///Users/ishikawasuguru/Threads_piste/gas_threads_data/SheetsWriter.gs)
- [Main.gs](file:///Users/ishikawasuguru/Threads_piste/gas_threads_data/Main.gs)

ユーザーの回答に応じて、Config.gs のスプレッドシートID/名前・シート名を書き換えてください。

### 3. ユーザーへセットアップ案内

以下の手順をユーザーに伝えてください：

```
GASプロジェクトのセットアップ手順：

1. https://script.google.com/ で新規プロジェクト作成
2. プロジェクト名を「threads_data」に変更
3. 既存の「コード.gs」を削除し、以下4ファイルを作成：
   - Config → Config.gsの内容を貼り付け
   - ThreadsDataAPI → ThreadsDataAPI.gsの内容を貼り付け
   - SheetsWriter → SheetsWriter.gsの内容を貼り付け
   - Main → Main.gsの内容を貼り付け
4. ⚙「プロジェクトの設定」→「スクリプトプロパティ」に追加：
   - THREADS_ACCESS_TOKEN: [FBアクセストークン]
5. 上部プルダウンで「testFetchThreads」を選択 → ▶実行（初回は認証承認）
6. 「testFetchInsightsAndReplies」を実行 → メトリクスと返信を確認
7. 「collectThreadsData」を実行 → Sheetsにデータ書き込み確認
8. 動作確認後「setupTrigger」を実行（毎日午前9時に自動実行開始）
```

### 4. 完了サマリーを表示

```
✅ GASデータ収集プロジェクト生成完了

ファイル: gas_threads_data/
  - Config.gs（スプレッドシート設定済み）
  - ThreadsDataAPI.gs
  - SheetsWriter.gs
  - Main.gs

次のステップ：
1. GASエディタでプロジェクト作成 → 4ファイルを貼り付け
2. スクリプトプロパティにFBアクセストークンを設定
3. testFetchThreads で動作確認
4. collectThreadsData で全データ取得＆書き込み確認
5. setupTrigger でトリガー設定
```

## フローの仕組み

```
毎日午前9時にトリガー実行
  ↓
Threads API: /me/threads で投稿一覧取得
  ↓
各投稿をループ（Iterator相当）
  ├─ /{id}/insights → いいね・ビュー・リポスト・引用 を取得
  └─ /{id}/replies → piste_boss の返信テキストを抽出
  ↓
重複チェック（既にシートに登録済みならスキップ）
  ↓
Google Sheetsに行を追加
  日付 | 本文 | いいね | 引用 | リポスト | インプレッション | コメント欄1
```

## Google Sheets カラム構成

| カラム | 内容 | データソース |
|---|---|---|
| A: 日付 | 投稿タイムスタンプ | `timestamp` |
| B: 本文 | 投稿テキスト | `text` |
| C: いいね | いいね数 | insights `likes` |
| D: 引用 | 引用数 | insights `quotes` |
| E: リポスト | リポスト数 | insights `reposts` |
| F: インプレッション | 閲覧数 | insights `views` |
| G: コメント欄1 | 自分(piste_boss)の返信 | replies (フィルター) |
| H-J: コメント欄2-4 | 予備 | 未使用 |

## Threads APIの注意点

- **トークン有効期限**: Long-lived tokenは約60日で期限切れ
- **更新URL**: https://developers.facebook.com/tools/debug/accesstoken/
- **レート制限**: 短時間に大量リクエストするとエラー。API_DELAY_MS（500ms）で制御
- **Insights API**: 投稿から24時間以上経過していないとデータが0の場合あり

## トラブルシューティング

| エラー | 対処 |
|-------|------|
| `Invalid access token` | FBトークンを更新してスクリプトプロパティを書き換え |
| Insights取得失敗 | 投稿が新しすぎる場合は正常（24時間後に再取得） |
| Sheets書き込みエラー | スプレッドシートのアクセス権限を確認 |
| 重複データ | isDuplicate() がタイムスタンプ・本文先頭30文字で判定 |
