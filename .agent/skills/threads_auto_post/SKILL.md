---
name: threads_auto_post
description: Notion→Threads自動投稿GASスクリプトの生成・セットアップスキル
---

# Threads Auto Post (GAS)

NotionデータベースからThreadsへの自動投稿を行うGoogle Apps Scriptプロジェクトを生成・セットアップします。

## 使用方法

### 基本コマンド
```
Threads自動投稿のGASプロジェクトをセットアップしてください。
```

## 必要情報

以下の情報をユーザーに確認してください：

| 情報 | 必須 | 取得方法 |
|------|:---:|---------|
| Notion APIトークン | ✅ | Notion Integrations で発行 (`ntn_...`) |
| NotionデータベースURL or ID | ✅ | 対象DBページのURLから取得 |
| Threads APIアクセストークン | ✅ | Meta for Developers で発行 |

### 確認プロンプト例
```
GASセットアップに以下の情報が必要です：
1. Notion APIトークン（`ntn_` で始まるもの）
2. NotionデータベースのURL（投稿データが入っているDB）
3. Threads APIのアクセストークン
```

## NotionデータベースのURLからIDを抽出する方法

URL例: `https://www.notion.so/2efc991b527b8090a546c89a11a5455d?v=...`

`notion.so/` と `?` の間の32文字がデータベースID。ハイフンを挿入してUUID形式にする：
```
2efc991b527b8090a546c89a11a5455d
→ 2efc991b-527b-8090-a546-c89a11a5455d
```

## 前提条件：Notionデータベース構造

対象のNotionデータベースには以下のプロパティが必要です：

| プロパティ名 | 型 | 用途 |
|-------------|---|------|
| タイトル | Title | 投稿のタイトル |
| 投稿日 | Date | 投稿予定日時 |
| 本文 | Rich text | Threadsに投稿するテキスト |
| コメント欄 | Rich text | 返信として追加するコメント |
| ステータス | Status | 「未着手」→「投稿済み」管理 |
| URL | URL | 画像のGoogleドライブ共有URL |

## 実行手順

### 1. GASファイルを生成

`gas_threads_autopost/` ディレクトリに以下の4ファイルを生成します。テンプレートは `scripts/` ディレクトリにあります。

| ファイル | 役割 |
|---------|------|
| `Config.gs` | 定数・認証情報（DB IDをユーザー指定値に設定） |
| `NotionAPI.gs` | Notion DB照会・ステータス更新 |
| `ThreadsAPI.gs` | Container作成・Publish・コメント返信・DriveURL変換 |
| `Main.gs` | メインフロー・テスト・トリガー管理 |

**Config.gs のカスタマイズ箇所:**
```javascript
const NOTION_DATABASE_ID = 'ユーザーが指定したDB ID';
```

### 2. ユーザーへセットアップ案内

以下の手順をユーザーに伝えてください：

```
GASプロジェクトのセットアップ手順：

1. https://script.google.com/ で新規プロジェクト作成
2. プロジェクト名を「piste_threads_autopost」に変更
3. 既存の「コード.gs」を「Config」にリネーム → Config.gsの内容を貼り付け
4. 「＋」→「スクリプト」で以下3ファイルを追加：
   - NotionAPI → NotionAPI.gsの内容を貼り付け
   - ThreadsAPI → ThreadsAPI.gsの内容を貼り付け
   - Main → Main.gsの内容を貼り付け
5. ⚙「プロジェクトの設定」→「スクリプトプロパティ」に追加：
   - THREADS_ACCESS_TOKEN: [トークン]
   - NOTION_API_KEY: [トークン]
6. 上部プルダウンで「testFetchPost」を選択 → ▶実行（初回は認証承認）
7. 動作確認後「setupTrigger」を実行（6時間ごと自動投稿開始）
```

### 3. 完了サマリーを表示

```
✅ GAS自動投稿プロジェクト生成完了

ファイル: gas_threads_autopost/
  - Config.gs（DB ID設定済み）
  - NotionAPI.gs
  - ThreadsAPI.gs
  - Main.gs

次のステップ：
1. GASエディタでプロジェクト作成 → 4ファイルを貼り付け
2. スクリプトプロパティにトークン2つを設定
3. testFetchPost で動作確認
4. setupTrigger でトリガー設定
```

## フローの仕組み

```
6時間ごとにトリガー実行
  ↓
Notion DB検索（ステータス=未着手 & 投稿日≤現在時刻、1件）
  ↓
画像URLあり？
  ├─ YES → Google Drive URL → lh3直接URL変換 → IMAGE Container
  └─ NO  → TEXT Container
  ↓
30秒待機 → Publish
  ↓
コメント欄あり？ → 返信として投稿
  ↓
Notionステータスを「投稿済み」に更新
```

## Threads APIの注意点

- **トークン有効期限**: Long-lived tokenは約60日で期限切れ
- **更新URL**: https://developers.facebook.com/tools/debug/accesstoken/
- **画像要件**: 公開URLが必要（GoogleドライブはリンクURL共有が有効なこと）
- **Container → Publish**: 2段階方式、間に30秒の待機が必要

## トラブルシューティング

| エラー | 対処 |
|-------|------|
| `object_not_found` (Notion) | DB IDを確認 / Notionで接続にインテグレーション追加 |
| `メディアをダウンロードできません` | Drive画像の共有設定を「リンクを知っている全員」に |
| `Invalid access token` | トークンを更新してスクリプトプロパティを書き換え |
| ステータス更新失敗 | Notionのステータス選択肢に「投稿済み」があるか確認 |
