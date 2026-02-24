# Piste Threads 自動投稿 - GAS版

MAKEの `piste_threds_auto_post` シナリオをGoogle Apps Scriptで内製化したものです。

## フロー

```
Notion DB（投稿日 ≤ 現在 & ステータス = 未着手）
  → 1件取得
  → 画像URLの数で分岐
     ├─ 複数URL → CAROUSEL投稿（カルーセル3枚、6:00投稿用）
     │    ├─ 各画像のアイテムContainer作成（is_carousel_item）
     │    ├─ 30秒待機
     │    └─ CAROUSEL Container作成（childrenにアイテムIDを指定）
     ├─ 1つのURL → IMAGE Container作成（Google Drive URL）
     └─ URLなし  → TEXT Container作成
  → 30秒待機
  → Publish
  → コメント欄あり？ → 返信として投稿
  → Notionステータスを「投稿済み」に更新
```

### カルーセル投稿について
- 6:00の投稿のみカルーセル形式（3枚の画像を1投稿に添付）
- 12:00・18:00の投稿はテキストのみ
- Notionの `URL`, `URL2`, `URL3` プロパティにそれぞれ画像URLを格納

## セットアップ手順

### 1. GASプロジェクト作成
1. [Google Apps Script](https://script.google.com/) を開く
2. 「新しいプロジェクト」を作成
3. プロジェクト名を `piste_threads_autopost` に変更

### 2. スクリプトファイルをコピー
以下の4ファイルをGASエディタに貼り付け：

| ファイル | 役割 |
|---------|------|
| `Config.gs` | 設定・定数 |
| `NotionAPI.gs` | Notion API連携 |
| `ThreadsAPI.gs` | Threads Graph API連携 |
| `Main.gs` | メインフロー・トリガー |

> **注意**: GASエディタでは `.gs` 拡張子は不要です。  
> ファイル追加方法: `+` → `スクリプト` → ファイル名を入力

### 3. スクリプトプロパティを設定
1. GASエディタ左メニュー「⚙ プロジェクトの設定」
2. 「スクリプトプロパティ」→「プロパティを追加」

| プロパティ名 | 値 |
|-------------|---|
| `THREADS_ACCESS_TOKEN` | Threads APIのアクセストークン |
| `NOTION_API_KEY` | Notion APIトークン（`ntn_...`） |

### 4. テスト実行
1. GASエディタで `testFetchPost` 関数を選択 → ▶実行
2. 初回は「承認」ダイアログが表示されるので承認
3. 実行ログで投稿データが正しく取得できるか確認

### 5. トリガー設定
1. GASエディタで `setupTrigger` 関数を選択 → ▶実行
2. これで6時間ごとに `publishScheduledPost` が自動実行されます

### 6. MAKEの停止
GASの動作確認ができたら、MAKEのシナリオを停止（Active → Off）してください。

## 関数一覧

| 関数名 | 用途 |
|-------|------|
| `publishScheduledPost()` | メイン関数（トリガーから自動実行） |
| `testFetchPost()` | テスト用（Notionからデータ取得のみ） |
| `setupTrigger()` | 6時間ごとのトリガーを設定 |
| `removeTrigger()` | トリガーを削除 |

## トラブルシューティング

- **トークン有効期限切れ**: Threads APIのlong-lived tokenは約60日で期限切れ。[Meta for Developers](https://developers.facebook.com/tools/debug/accesstoken/)でトークンを更新してスクリプトプロパティを書き換え。
- **画像投稿失敗**: GoogleドライブのファイルのURL共有設定「リンクを知っている全員」が有効か確認。
- **GAS実行時間制限**: GASは1回の実行が6分まで。通常は1分以内に完了。
