# Gemini タスク指示書 (2026-02-24)【テスト実行】

## 概要

Piste Threads の **2026-02-24 12:00** の投稿（冬太り解消の最終兵器）用のカルーセル画像3枚を生成し、Googleドライブへアップロード、NotionへのURL同期まで実行してください。

**注意**: これはテスト実行です。通常は06:00の投稿のみ画像を添付しますが、特例として12:00の投稿にカルーセル画像を添付します。

## 作業ディレクトリ

`/Users/ishikawasuguru/Threads_piste/`

---

## Step 1: 画像生成（1日×3枚 = 3枚）

`Piste_threads_image_prompt.md` の **セクション57**（冬太り解消の食事術 カルーセル）のプロンプトから画像を生成してください。

**重要: Gemini自身の画像生成機能（nanobananapro / Imagen）を使って画像を生成してください。既存のPythonスクリプトは使用しないでください。**

### 画像ルール

- **2026-02-24 12:00の投稿にカルーセル用3枚セット**を生成する
- 3枚は**共通のトーン・雰囲気・配色**で統一されていること
- 共通スタイル: 冬から春への季節の変わり目をイメージ。冷たいアイスブルーから温かい桜ピンク・新緑グリーンへのグラデーション背景。清潔感のあるミニマルな図解スタイル。

### 生成ルール

- アスペクト比: **9:16（縦長）**
- プラットフォーム: **threads**
- 保存先: `Piste_threads_image/` フォルダ
- 既に存在する画像はスキップ

### ファイル命名規則

YYYY-MM-DD-HH:MM_carousel_N piste_threads.png

- 日付形式: `YYYY-MM-DD`
- 時間: `12:00`（特例）
- カルーセル番号: `_carousel_1`, `_carousel_2`, `_carousel_3`
- プラットフォーム識別子: ` piste_threads`
- 拡張子: `.png`

### 生成対象一覧（3枚）

| # | ファイル名 | テーマ |
|---|-----------|--------|
| 1 | `2026-02-24-12:00_carousel_1 piste_threads.png` | 冬太り卒業宣言＋16時間断食の時計図解 |
| 2 | `2026-02-24-12:00_carousel_2 piste_threads.png` | 食材チェンジ（白米→もち麦、揚げ→蒸し料理）の対比図解 |
| 3 | `2026-02-24-12:00_carousel_3 piste_threads.png` | 汁物ファースト＋食事順番図解＋春ボディへのまとめ |

各プロンプトの詳細は `Piste_threads_image_prompt.md` のセクション57を参照してください。

---

## Step 2: Googleドライブへアップロード

画像生成が完了したら、以下を実行してください：

```
cd /Users/ishikawasuguru/Threads_piste/image_upload && python3 piste_threads_image_uplorder.py
```

---

## Step 3: NotionへのURL同期

アップロード完了後、以下を実行してください：

```
cd /Users/ishikawasuguru/Threads_piste && python3 piste_threads_drive_to_notion.py
```

NotionのURL, URL2, URL3プロパティにそれぞれカルーセル画像1〜3枚目のURLが格納されます。

---

## 完了確認

すべて完了したら以下を確認してください：
- [ ] `Piste_threads_image/` に3枚の画像が保存されている
- [ ] Googleドライブにアップロードされている
- [ ] Notionの `URL`, `URL2`, `URL3` プロパティにそれぞれ画像リンクが反映されている
