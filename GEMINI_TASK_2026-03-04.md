# Gemini タスク指示書 (2026-03-04) — 画像生成残件

## 概要

Piste Threads の未生成画像約75枚を生成し、Googleドライブへアップロード、NotionへのURL同期まで実行してください。

## 作業ディレクトリ

`/Users/ishikawasuguru/Threads_piste/`

---

## Step 1: 画像生成（約75枚）

`Piste_threads_image_prompt.md` の全セクションのプロンプトから画像を生成してください。

**重要: Gemini自身の画像生成機能（Imagen）を使って画像を生成してください。既存のPythonスクリプトは使用しないでください。**

### 生成ルール

- アスペクト比: **9:16（縦長）**
- 保存先: `Piste_threads_image/` フォルダ

### ファイル命名規則

YYYY-MM-DD-H:MM piste_threads.png

### 優先度

直近の投稿分（3月分）を最優先で生成し、その後過去分を順次生成してください。

---

## Step 2: Googleドライブへアップロード

cd /Users/ishikawasuguru/Threads_piste/image_upload && python3 piste_threads_image_uplorder.py

---

## Step 3: NotionへのURL同期

cd /Users/ishikawasuguru/Threads_piste && python3 piste_threads_drive_to_notion.py

---

## 完了確認

- [ ] `Piste_threads_image/` に未生成だった画像が保存されている
- [ ] Googleドライブにアップロードされている
- [ ] NotionのURLプロパティに画像リンクが反映されている
