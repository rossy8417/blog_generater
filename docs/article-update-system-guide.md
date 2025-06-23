# 汎用記事更新システムガイド

## 🎯 概要

再現性と汎用性を重視した記事更新システムです。ハードコーディングを排除し、設定ベースの管理により、任意の記事IDで安定した更新処理を実現します。

## 🚀 成功要因の分析結果

### ✅ 実際に機能した要因
1. **POST メソッドの使用**: PUT ではなく POST が SiteGuard セキュリティを通過
2. **X-API-Key 認証**: WordPress プラグインの専用認証ヘッダーが有効
3. **適切なコンテンツ前処理**: H5 タグ除去、重複 H4 修正、画像復元
4. **バックアップからの画像復元**: 元記事から画像 URL を取得して復元

### ❌ 問題となった要因
1. **ファイル散乱**: 23 個の Python ファイルがルートディレクトリに散らばり
2. **ハードコーディング**: 記事 ID 1388 が複数箇所に埋め込み
3. **設定の非統一**: 各スクリプトが独自の設定を持つ
4. **再現性の欠如**: 成功した手順の体系化不足

## 📋 システム構成

### ディレクトリ構造
```
blog_generator/
├── config/
│   └── article_update_config.json  # 統一設定ファイル
├── scripts/
│   └── article_update_manager.py   # メイン更新スクリプト
├── outputs/
│   └── article_operations/         # 更新結果レポート
├── backups/                        # 自動バックアップ
├── tmp/
│   └── scattered_files/            # 整理済み散乱ファイル
└── logs/
    └── article_updates/            # 更新ログ
```

### 設定ファイル (`config/article_update_config.json`)
```json
{
  "wordpress_settings": {
    "endpoint_base": "https://www.ht-sw.tech/wp-json/blog-generator/v1",
    "timeout": 30,
    "retry_attempts": 3
  },
  "update_strategies": {
    "proven_method": {
      "endpoint": "/update-post/{post_id}",
      "method": "POST",
      "backup_required": true
    }
  },
  "content_processing": {
    "h5_tag_removal": true,
    "duplicate_h4_fix": true,
    "image_restoration": true
  }
}
```

## 🔧 使用方法

### 基本的な記事更新
```bash
# 記事ID 1388 を codeediter_example.txt で更新
python3 scripts/article_update_manager.py 1388 codeediter_example.txt

# 異なる記事ID での更新
python3 scripts/article_update_manager.py 2045 outputs/new_article_content.txt

# 更新戦略を指定
python3 scripts/article_update_manager.py 1388 codeediter_example.txt --strategy proven_method
```

### プログラムでの使用
```python
from scripts.article_update_manager import ArticleUpdateManager

# マネージャー初期化
manager = ArticleUpdateManager()

# 記事更新実行
result = manager.update_article(
    post_id=1388,
    content_file="codeediter_example.txt",
    strategy="proven_method"
)

if result['success']:
    print(f"更新成功: {result['report_file']}")
else:
    print(f"更新失敗: {result['error']}")
```

## 📊 更新戦略

### 1. proven_method (推奨)
- **説明**: 実証済みの成功パターン
- **メソッド**: POST
- **バックアップ**: あり
- **用途**: 既存記事の安全な更新

### 2. direct_update
- **説明**: 直接更新（リスク高）
- **メソッド**: PUT
- **バックアップ**: あり
- **用途**: セキュリティ制限が緩い環境

### 3. new_post
- **説明**: 新規記事作成
- **メソッド**: POST
- **バックアップ**: なし
- **用途**: 全く新しい記事の作成

## 🔄 自動処理機能

### コンテンツ前処理
1. **H5 タグ除去**: H5 タグを H4 タグに自動変換
2. **重複 H4 修正**: 連続する H4 見出しの構造最適化
3. **画像復元**: バックアップから画像ブロックを自動復元

### ファイル管理
1. **自動ディレクトリ作成**: 必要なディレクトリを自動生成
2. **タイムスタンプ付きバックアップ**: 更新前の自動バックアップ
3. **構造化ログ**: JSON 形式での詳細ログ記録

## 📋 出力ファイル

### 更新レポート (`outputs/article_operations/update_report_[ID]_[timestamp].json`)
```json
{
  "post_id": 1388,
  "strategy": "proven_method",
  "timestamp": "20250623_143022",
  "success": true,
  "update_result": {
    "api_status_code": 200,
    "message": "更新完了"
  },
  "backup_created": true,
  "report_file": "/path/to/report.json"
}
```

### バックアップファイル (`backups/article_update_backup_[ID]_[timestamp].json`)
```json
{
  "post_id": 1388,
  "backup_timestamp": "20250623_143020",
  "original_data": {
    "id": 1388,
    "title": "元のタイトル",
    "content": "元のコンテンツ..."
  }
}
```

## ⚠️ 制限事項と対策

### SiteGuard Lite セキュリティ制限
- **問題**: WordPress セキュリティプラグインによる API ブロック
- **対策**: proven_method 戦略使用、手動更新併用

### API レート制限
- **問題**: 連続 API 呼び出しによる制限
- **対策**: リトライ機能、適切なタイムアウト設定

### 権限制限
- **問題**: WordPress 更新権限の不足
- **対策**: 適切な API キー設定、バックアップからの復元機能

## 🔧 トラブルシューティング

### よくあるエラーと対処法

#### 1. 「WORDPRESS_API_KEY が設定されていません」
```bash
# .env ファイルに API キーを設定
echo "WORDPRESS_API_KEY=your_api_key_here" >> .env
```

#### 2. 「設定ファイルが見つかりません」
```bash
# 設定ファイルの存在確認
ls config/article_update_config.json

# カスタム設定ファイル指定
python3 scripts/article_update_manager.py 1388 content.txt --config custom_config.json
```

#### 3. 「API 呼び出し失敗」
- WordPress サイトの稼働状況確認
- API エンドポイントの正確性確認
- セキュリティプラグイン設定の確認

## 🚀 今後の改善計画

### Phase 1: 基本機能強化
- [ ] マルチサイト対応
- [ ] バッチ更新機能
- [ ] 詳細エラーハンドリング

### Phase 2: 運用改善
- [ ] Web UI インターフェース
- [ ] 更新履歴管理
- [ ] 自動テスト機能

### Phase 3: 高度機能
- [ ] AI による品質チェック
- [ ] 自動 SEO 最適化
- [ ] マルチメディア統合管理

## 📞 サポート

問題や改善提案がある場合は、以下のログファイルとともにご報告ください：

- `logs/article_updates/article_update_[date].log`
- `outputs/article_operations/update_report_[ID]_[timestamp].json`
- 使用した設定ファイル (`config/article_update_config.json`)