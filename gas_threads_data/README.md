# gas_threads_data - Threadsデータ収集 GAS

Makeシナリオ `threads_data` を GAS（Google Apps Script）で置き換えるスクリプト。

## 概要

Threads APIから投稿データ・メトリクス・返信を取得し、Google Sheetsに記録する。

**フロー:**
```
Threads API → 投稿一覧取得 → 各投稿のInsights/Replies取得 → Google Sheets書き込み
```

## ファイル構成

| ファイル | 説明 |
|---|---|
| Config.gs | 設定・定数・認証情報取得 |
| ThreadsDataAPI.gs | Threads API連携（投稿一覧・Insights・Replies） |
| SheetsWriter.gs | Google Sheets書き込み・重複チェック |
| Main.gs | メインフロー・トリガー設定・テスト関数 |

## セットアップ手順

### 1. GASプロジェクト作成
1. [Google Apps Script](https://script.google.com/) にアクセス
2. 「新しいプロジェクト」を作成
3. 各 `.gs` ファイルの内容をコピー＆ペースト

### 2. スクリプトプロパティ設定
1. GASエディタ → プロジェクトの設定 → スクリプトプロパティ
2. 以下を追加:

| プロパティ | 値 |
|---|---|
| `THREADS_ACCESS_TOKEN` | Threads Graph APIのアクセストークン |

> **Note:** `gas_threads_autopost` と同じアクセストークンを使用できます。

### 3. テスト実行
1. `testFetchThreads()` を実行 → 投稿一覧がログに表示されることを確認
2. `testFetchInsightsAndReplies()` を実行 → メトリクスと返信がログに表示されることを確認
3. `collectThreadsData()` を実行 → Google Sheetsにデータが書き込まれることを確認

### 4. トリガー設定
1. `setupTrigger()` を実行 → 毎日午前9時に自動実行されるトリガーが設定される

## Google Sheets出力

スプレッドシート: `Piste_instagram_Data` / シート: `Threads_Data`

| カラム | 内容 |
|---|---|
| A: 日付 | 投稿タイムスタンプ |
| B: 本文 | 投稿テキスト |
| C: いいね | いいね数 |
| D: 引用 | 引用数 |
| E: リポスト | リポスト数 |
| F: インプレッション | 閲覧数 |
| G: コメント欄1 | piste_bossの返信テキスト |
