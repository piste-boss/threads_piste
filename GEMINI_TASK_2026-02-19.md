# Gemini タスク指示書 (2026-02-19)

## 概要

Piste Threads の来週分（2/23〜3/1）のインフォグラフィック画像21枚を生成し、Googleドライブへアップロード、NotionへのURL同期まで実行してください。

## 作業ディレクトリ

`/Users/ishikawasuguru/Threads_piste/`

---

## Step 1: 画像生成（21枚）

`Piste_threads_image_prompt.md` の **セクション53〜73**（Feb 23 〜 Mar 01）のプロンプトから画像を生成してください。

### 生成ルール

- アスペクト比: **9:16（縦長）**
- プラットフォーム: **threads**
- 保存先: `Piste_threads_image/` フォルダ
- 既に存在する画像はスキップ

### ファイル命名規則

```
YYYY-MM-DD-H:MM piste_threads.png
```

- 日付形式: `YYYY-MM-DD`
- 時間形式: `H:MM`（先頭ゼロなし。例: `6:00`, `12:00`, `18:00`）
- プラットフォーム識別子: ` piste_threads`
- 拡張子: `.png`

### 生成対象一覧（21枚）

| # | ファイル名 | テーマ |
|---|---|---|
| 1 | `2026-02-23-6:00 piste_threads.png` | 月曜朝の5分ルーティン |
| 2 | `2026-02-23-12:00 piste_threads.png` | 花粉対策と腸活 |
| 3 | `2026-02-23-18:00 piste_threads.png` | 春に向けた体づくり |
| 4 | `2026-02-24-6:00 piste_threads.png` | 朝のタンパク質 |
| 5 | `2026-02-24-12:00 piste_threads.png` | 冬太り解消の食事術 |
| 6 | `2026-02-24-18:00 piste_threads.png` | 歩くだけダイエット |
| 7 | `2026-02-25-6:00 piste_threads.png` | 最強の味噌汁 |
| 8 | `2026-02-25-12:00 piste_threads.png` | コンビニ痩せ朝食 |
| 9 | `2026-02-25-18:00 piste_threads.png` | 夜の食欲コントロール |
| 10 | `2026-02-26-6:00 piste_threads.png` | 停滞期の突破法 |
| 11 | `2026-02-26-12:00 piste_threads.png` | 春野菜でデトックス |
| 12 | `2026-02-26-18:00 piste_threads.png` | 間食のゴールデンルール |
| 13 | `2026-02-27-6:00 piste_threads.png` | 朝の2分筋トレ |
| 14 | `2026-02-27-12:00 piste_threads.png` | サバ缶アレンジ |
| 15 | `2026-02-27-18:00 piste_threads.png` | 睡眠ダイエット |
| 16 | `2026-02-28-6:00 piste_threads.png` | 週末の買い物リスト |
| 17 | `2026-02-28-12:00 piste_threads.png` | お粥ダイエット |
| 18 | `2026-02-28-18:00 piste_threads.png` | 3月の目標設定 |
| 19 | `2026-03-01-6:00 piste_threads.png` | 日曜朝のルーティン |
| 20 | `2026-03-01-12:00 piste_threads.png` | 外食サバイバル |
| 21 | `2026-03-01-18:00 piste_threads.png` | 3月スタートの夜 |

各プロンプトの詳細は `Piste_threads_image_prompt.md` のセクション53〜73を参照してください。

---

## Step 2: Googleドライブへアップロード

画像生成が完了したら、以下を実行してください：

```bash
cd /Users/ishikawasuguru/Threads_piste/image_upload && python3 piste_threads_image_uplorder.py
```

---

## Step 3: NotionへのURL同期

アップロード完了後、以下を実行してください：

```bash
cd /Users/ishikawasuguru/Threads_piste && python3 piste_threads_drive_to_notion.py
```

---

## 完了確認

すべて完了したら以下を確認してください：
- [ ] `Piste_threads_image/` に21枚の画像が保存されている
- [ ] Googleドライブにアップロードされている
- [ ] NotionのURLプロパティに画像リンクが反映されている
