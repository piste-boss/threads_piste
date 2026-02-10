# Social Infographic Generator - README

X・Threads共用のインフォグラフィック画像生成スキルです。

## ディレクトリ構成

```
social_infographic_generator/
├── SKILL.md                    # メインスキル定義
├── README.md                   # このファイル
├── examples/
│   ├── threads_prompt.md       # Threads用プロンプト例
│   └── x_prompt.md             # X用プロンプト例
└── scripts/
    └── (将来的な拡張用)
```

## クイックスタート

### Threads用画像生成

```
Piste_threads_image_prompt.mdから画像を生成して、
Piste_threads_image/フォルダに保存してください。
```

### X用画像生成（16:9横長）

```
X_image_prompt.mdから16:9の横長画像を生成して、
X_images/フォルダに保存してください。
```

## プロンプトファイルの作り方

### リスト形式（推奨）

```markdown
- **2026-02-15 06:00**: 日本のSNS向けインフォグラフィック...
- **2026-02-15 12:00**: 日本のSNS向けインフォグラフィック...
```

詳細は `examples/` フォルダの例文を参照してください。

## ファイル命名規則

- **Threads**: `2026-02-15-6:00 piste_threads.png`
- **X**: `2026-02-15-6:00 x.png`

## 既存の画像はスキップ

同じファイル名の画像が既に存在する場合、自動的にスキップされます。

## トラブルシューティング

問題が発生した場合は `SKILL.md` のトラブルシューティングセクションを参照してください。
