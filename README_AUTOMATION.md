# Piste Threads セミオート自動化

週次のThreads投稿プロセスをセミオートで運用するための仕組みです。

## アーキテクチャ

```
【完全自動フェーズ】木曜20:00（launchd）
├─ データ分析・レポート更新（Python）
└─ macOS通知「エージェントタスク準備完了」

【手動フェーズ】金曜朝（約1分）
├─ Antigravityで画像生成依頼（スキル使用・無料）
├─ Googleドライブアップロード（Python）
└─ Notion画像URL同期（Python）

【Make継続部分】
├─ Threadsデータ採取 → スプレッドシート書き込み
└─ Threads投稿実行
```

## ファイル構成

### 必須スクリプト
| ファイル | 役割 |
|---------|------|
| `process_threads_data.py` | データ分析（木曜自動実行） |
| `piste_threads_autopost_minimal.sh` | メイン自動化スクリプト |
| `com.ishikawasuguru.piste_threads_autopost.plist` | launchd設定 |
| `piste_threads_drive_to_notion.py` | Drive→Notion画像URL同期 |
| `notion＿post_script/piste_threads_notion.py` | Notion投稿同期 |
| `image_upload/piste_threads_image_uplorder.py` | Googleドライブ画像アップロード |
| `.agent/workflows/piste_threads_full_run.md` | エージェントワークフロー |
| `.agent/skills/social_infographic_generator/` | 汎用画像生成スキル |

### オプション
| ファイル | 役割 |
|---------|------|
| `generate_content.py` | Gemini APIでコンテンツ生成 |
| `generate_images_api.py` | DALL-E画像生成（保存のみ） |

### データファイル
| ファイル | 役割 |
|---------|------|
| `Piste_threads_data.md` | 元データ |
| `Piste_threads_report.md` | 分析レポート |
| `Piste_threads_post.md` | 投稿案 |
| `Piste_threads_image_prompt.md` | 画像プロンプト |

## 週次運用フロー

### 木曜 20:00（自動）
launchdが `piste_threads_autopost_minimal.sh` を実行：
1. `process_threads_data.py` でデータ分析
2. `Piste_threads_report.md` を更新
3. macOS通知を表示
4. デスクトップに `AGENT_TASK_REQUEST.txt` を配置

### 金曜 朝（手動・約1分）

**オプション1: 画像生成のみ（最速）**
```
1. Antigravityで実行：
   「Piste_threads_image_prompt.mdから画像を生成して、
    Piste_threads_image/フォルダに保存してください」

2. ターミナルで実行：
   cd image_upload && python3 piste_threads_image_uplorder.py
   cd .. && python3 piste_threads_drive_to_notion.py
```

**オプション2: 投稿案作成も含む（フルフロー）**
```
Antigravityで /piste_threads_full_run を実行
```

### 土曜〜日曜（自動）
Makeが投稿を自動実行（既存フロー）

## launchdサービス管理

```bash
# サービス登録
cp com.ishikawasuguru.piste_threads_autopost.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.ishikawasuguru.piste_threads_autopost.plist

# ステータス確認
launchctl list | grep piste_threads

# サービス停止
launchctl unload ~/Library/LaunchAgents/com.ishikawasuguru.piste_threads_autopost.plist

# 手動テスト実行
./piste_threads_autopost_minimal.sh
```

## トラブルシューティング

- **ログ確認**: `autopost.log` にスクリプト実行ログが記録されます
- **launchd出力**: `launchd_stdout.log` / `launchd_stderr.log` を確認
- **画像生成失敗**: `Piste_threads_image/` フォルダの存在を確認
- **Drive同期失敗**: `image_upload/token.pickle` の有効期限を確認
- **アーカイブ**: 過去のデバッグスクリプトは `archive/` に保管しています
