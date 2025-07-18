# 統合画像管理システム - Consolidated Image Manager

## 概要

統合画像管理システム(`consolidated_image_manager.py`)は、3つの既存の画像管理機能を統合した包括的なソリューションです：

- **画像生成** (`image_generator.py`): 新規アイキャッチ・サムネイル画像の生成
- **画像更新管理** (`image_update_manager.py`): WordPressの画像更新・バージョン管理
- **簡単アイキャッチ更新** (`update_eyecatch_simple.py`): 簡単なアイキャッチ更新

## 主要機能

### 1. 新規画像生成
- OpenAI gpt-image-1を使用したアイキャッチ画像生成（日本語テキスト対応）
- Google Imagen 3を使用したサムネイル画像生成（テキストなし）
- 自動画像最適化（ファイルサイズ削減）
- アウトライン解析と章タイトル抽出

### 2. WordPress画像更新
- 既存記事のアイキャッチ画像差し替え
- 章別画像の個別更新
- WordPressメディアライブラリへの自動アップロード
- 更新後の検証機能

### 3. 画像バージョン管理
- 画像更新履歴の自動記録
- バージョン別の画像メタデータ保存
- 画像互換性分析
- ロールバック機能（メタデータレベル）

### 4. 画像最適化
- JPEG品質の段階的調整
- ファイルサイズの自動最適化
- アスペクト比の維持
- Web表示用のリサイズ

## コマンド体系

### 新規画像生成

```bash
# 全画像生成（アイキャッチ + サムネイル）
python3 scripts/consolidated_image_manager.py generate --outline outputs/article/outline.md --mode all

# アイキャッチのみ生成
python3 scripts/consolidated_image_manager.py generate --outline outputs/article/outline.md --mode eyecatch

# 特定章のサムネイル生成
python3 scripts/consolidated_image_manager.py generate --outline outputs/article/outline.md --mode thumbnail --chapter 1
```

### WordPress画像更新

```bash
# アイキャッチ画像の更新
python3 scripts/consolidated_image_manager.py update --post-id 1234 --type eyecatch

# カスタムプロンプトでアイキャッチ更新
python3 scripts/consolidated_image_manager.py update --post-id 1234 --type eyecatch --prompt "Custom image prompt"

# 特定章の画像更新
python3 scripts/consolidated_image_manager.py update --post-id 1234 --type chapter --chapter-num 1
```

### 簡単更新（後方互換性）

```bash
# 従来のupdate_eyecatch_simple.pyと同等の機能
python3 scripts/consolidated_image_manager.py quick-update 1234

# カスタムプロンプト指定
python3 scripts/consolidated_image_manager.py quick-update 1234 --prompt "Custom prompt"
```

### バージョン管理

```bash
# 画像更新履歴の表示
python3 scripts/consolidated_image_manager.py version --post-id 1234 --action history

# 特定タイプの履歴表示
python3 scripts/consolidated_image_manager.py version --post-id 1234 --action history --type eyecatch

# バージョン復元（メタデータ表示）
python3 scripts/consolidated_image_manager.py version --post-id 1234 --action restore --version-id VERSION_ID
```

## 技術仕様

### 対応API
- **OpenAI gpt-image-1**: アイキャッチ画像生成（日本語テキスト対応）
- **Google Imagen 3**: サムネイル画像生成（テキストなし、16:9アスペクト比）
- **WordPress REST API**: 画像アップロード・記事更新

### 画像最適化設定

#### アイキャッチ画像
- **ターゲットサイズ**: 1200×675px（16:9）
- **最大ファイルサイズ**: 500KB
- **JPEG品質**: 85（段階的に調整）
- **フォーマット**: JPEG（最適化済み）

#### サムネイル画像
- **ターゲットサイズ**: 800×450px（16:9）
- **最大ファイルサイズ**: 800KB
- **JPEG品質**: 80（段階的に調整）
- **フォーマット**: JPEG（最適化済み）

### ファイル構造

```
outputs/
├── image_version_db.json          # バージョン管理データベース
└── {title}-INT-{number}/          # 記事別フォルダ
    ├── complete_article.md
    ├── metadata.json
    ├── {timestamp}_eyecatch.jpg   # アイキャッチ画像
    └── {timestamp}_chapter*.jpg   # 章別画像
```

## 環境設定

### 必要な環境変数（.env）

```env
GOOGLE_API_KEY=your_gemini_api_key        # Google Imagen 3用
OPENAI_API_KEY=your_openai_api_key        # OpenAI gpt-image-1用
WORDPRESS_API_KEY=your_wordpress_api_key  # WordPress更新用
WORDPRESS_ENDPOINT=your_wordpress_url     # WordPress API URL
```

### 依存関係

```python
google-genai          # Google Imagen 3
openai               # OpenAI gpt-image-1
Pillow              # 画像処理
requests            # HTTP通信
python-dotenv       # 環境変数管理
numpy               # 数値計算
```

## 統合システムの利点

### 1. 一元管理
- 全ての画像操作を単一のコマンドで実行
- 統一されたコマンド体系とオプション
- 統合された設定とログ管理

### 2. 後方互換性
- 既存スクリプトとの互換性維持
- `quick-update`コマンドで従来の簡単更新を提供
- 既存のワークフローに影響なし

### 3. 機能拡張
- バージョン管理システムの追加
- 画像互換性分析
- 自動最適化の強化
- エラーハンドリングの改善

### 4. 運用効率
- コマンド実行の簡素化
- 自動分類と整理
- 詳細なログとステータス表示
- バッチ処理対応

## エラーハンドリング

### 画像生成エラー
- API接続失敗時のリトライ機能
- フォールバック処理（テンプレート直接使用）
- 部分的成功時の継続処理

### WordPress更新エラー
- 記事存在確認
- アップロード失敗時の自動復旧
- 更新検証とロールバック

### バージョン管理エラー
- データベース破損時の自動修復
- 履歴制限（最新10件まで保持）
- メタデータの自動バックアップ

## 使用例

### 基本的なワークフロー

```bash
# 1. 新規記事の全画像生成
python3 scripts/consolidated_image_manager.py generate \
  --outline outputs/new-article-INT-01/outline.md \
  --mode all

# 2. 既存記事のアイキャッチ更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1234 \
  --type eyecatch

# 3. 更新履歴の確認
python3 scripts/consolidated_image_manager.py version \
  --post-id 1234 \
  --action history

# 4. 特定章の画像更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1234 \
  --type chapter \
  --chapter-num 3
```

### 高度な使用例

```bash
# カスタムプロンプトでの画像生成
python3 scripts/consolidated_image_manager.py update \
  --post-id 1234 \
  --type eyecatch \
  --prompt "Futuristic AI illustration with holographic elements"

# アイキャッチのみの履歴表示
python3 scripts/consolidated_image_manager.py version \
  --post-id 1234 \
  --action history \
  --type eyecatch
```

## 今後の拡張計画

### 短期計画
- バッチ画像更新機能の実装
- WordPress記事内容に基づく適応的画像生成
- 画像スタイル分析とプロファイル抽出

### 長期計画
- 機械学習を使った画像品質評価
- 自動A/Bテスト機能
- クラウドストレージ連携
- リアルタイム画像最適化

## トラブルシューティング

### よくある問題

1. **API接続エラー**: `.env`ファイルのAPIキー設定を確認
2. **権限エラー**: `outputs/`ディレクトリの書き込み権限を確認
3. **画像生成失敗**: プロンプトの長さ制限（400文字以下）を確認
4. **WordPress更新失敗**: 記事IDの存在とAPI権限を確認

### ログ確認

```bash
# 詳細なエラーログは標準出力に表示
python3 scripts/consolidated_image_manager.py generate \
  --outline outputs/article/outline.md \
  --mode all 2>&1 | tee image_generation.log
```

## サポート

統合画像管理システムの使用に関するご質問やご要望は、プロジェクトのissueまでお寄せください。継続的な改善と機能拡張を進めてまいります。