---
description: エージェントスキルを使って画像生成・同期の一連の流れを実行します（APIキー設定不要）。
---

# Piste Threads Agent-Driven Automation

## 0. データ分析の実行とレポート更新
自動化スクリプト（piste_threads_autopost_minimal.sh）でデータ分析を実行し、`Piste_threads_report.md` と `Piste_threads_data.md` を最新データで更新します。

### 0-1. データ分析スクリプトの実行
// turbo
bash piste_threads_autopost_minimal.sh

### 0-2. レポートとデータファイルの更新
分析結果をもとに以下のファイルを更新してください：
- `Piste_threads_data.md` — Threads APIから取得した最新の投稿データ（日付・本文・いいね・インプレッション・コメント）を反映
- `Piste_threads_report.md` — 最新データに基づく週次レポート（概要・上位投稿ランキング・成功要因分析・今後の提言）を追記

## 1. 投稿案とプロンプトの作成
レポート内容 (`Piste_threads_report.md`) の最新分析結果を読み、インサイトに基づいて**来週1週間分（月〜日）**の投稿案を作成してください。
- 1日3投稿（06:00, 12:00, 18:00）、合計21件。
- 作成した投稿案は `Piste_threads_post.md` の末尾に追記してください（既存のフォーマット `## 投稿案...` を遵守）。
- 同時に、画像生成用のプロンプトを `Piste_threads_image_prompt.md` に追記してください。

### 画像添付ルール
- **画像は1日1投稿（06:00の投稿）のみに添付する。** 12:00・18:00の投稿にはテキストのみ。
- 06:00の投稿には**カルーセル形式で3枚の画像**を添付する。
- 3枚の画像は**共通のトーン・雰囲気・配色**で統一すること（同じテーマの異なる切り口を表現する）。
- プロンプト作成時は、1日分（3枚セット）ごとに共通のスタイル指示を明記し、各画像の差分（内容・視点）を個別に記述する。
- `Piste_threads_image_prompt.md` のフォーマット例：
  ```
  ## YYYY-MM-DD 06:00 カルーセル（3枚セット）
  **共通スタイル**: [配色・トーン・雰囲気の指示]

  **1枚目**: [プロンプト]
  **2枚目**: [プロンプト]
  **3枚目**: [プロンプト]
  ```

## 2. Notionへの同期
作成された投稿案をNotionデータベースに同期します。
// turbo
python3 notion＿post_script/piste_threads_notion.py

## 3. 画像の生成と保存（スキル使用）

汎用スキル `/generate_social_infographics` を使用：

Piste_threads_image_prompt.mdから画像を生成して、
Piste_threads_image/フォルダに保存してください。

- **06:00の投稿のみ画像を生成**（12:00・18:00は画像なし）
- 1日あたり**カルーセル用3枚セット**を生成する
- 3枚は共通のトーン・雰囲気で統一されていること
- 未生成の画像のみを自動的に抽出して生成
- ファイル名: `YYYY-MM-DD-6:00_carousel_1 piste_threads.png`, `_carousel_2`, `_carousel_3` の形式で保存

## 4. Googleドライブへのアップロード
保存された画像をGoogleドライブへアップロードし、ローカルから削除します。
// turbo
cd image_upload && python3 piste_threads_image_uplorder.py

## 5. Notionへの画像URLリンク同期
アップロードされた画像のGoogleドライブURLを、NotionページのURLプロパティに同期します。
// turbo
python3 piste_threads_drive_to_notion.py
