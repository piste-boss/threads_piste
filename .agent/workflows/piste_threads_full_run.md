---
description: エージェントの機能を使って、分析・投稿作成・画像生成・同期・アップロードの一連の流れを実行します（APIキー設定不要）。
---

# Piste Threads Agent-Driven Automation

このワークフローは、エージェント自身の生成能力（Gemini/画像生成ツール）を使用してタスクを実行します。
ユーザーのAPIキー設定は不要ですが、実行時にエージェントが順次作業を行います。

## 1. データ分析とレポート更新
// turbo
python3 process_threads_data.py

## 2. 投稿案とプロンプトの作成
レポート内容 (`Piste_threads_report.md`) の最新分析結果を読み、インサイトに基づいて**来週1週間分（月〜日）**の投稿案を作成してください。
- 1日3投稿（06:00, 12:00, 18:00）、合計21件。
- 作成した投稿案は `Piste_threads_post.md` の末尾に追記してください（既存のフォーマット `## 投稿案...` を遵守）。
- 同時に、画像生成用のプロンプトを `Piste_threads_image_prompt.md` に追記してください（フォーマット `- **YYYY-MM-DD HH:MM**: ...` を遵守）。

## 3. Notionへの同期
作成された投稿案をNotionデータベースに同期します。
// turbo
python3 notion＿post_script/piste_threads_notion.py

## 4. 画像の生成と保存
`Piste_threads_image_prompt.md` に追加された新しいプロンプトに従って、`generate_image` ツールで画像を生成してください。
**重要**: 生成された画像は、必ず `/Users/ishikawasuguru/Threads_piste/Piste_threads_image` フォルダに移動・保存してください。
- ファイル名規則: `YYYY-MM-DD-H:MM piste_threads.png` (例: `2026-02-01-6:00 piste_threads.png`)
- 時間の「分」が00の場合はそのまま、時間が1桁の場合は0をつけない（例: 6:00）。
- ※生成枚数が多い場合、数回に分けて実行するか、ユーザーに確認を求めてください。

## 5. Googleドライブへのアップロード
保存された画像をGoogleドライブへアップロードし、ローカルから削除します。
// turbo
cd image_upload && python3 piste_threads_image_uplorder.py

## 6. Notionへの画像URLリンク同期
アップロードされた画像のGoogleドライブURLを、NotionページのURLプロパティに同期します。
// turbo
python3 piste_threads_drive_to_notion.py
