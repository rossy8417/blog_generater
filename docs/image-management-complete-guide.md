# 🎨 画像管理完全ガイド

## 概要

WordPress記事の画像管理を包括的にカバーする統合ガイドです。アイキャッチ画像と章別画像の生成・更新・管理について、従来の個別ガイドを統合し、新しい統合画像管理システムも含めた完全版を提供します。

## 🎯 画像管理システム構成

### 対応画像タイプ
- **アイキャッチ画像**: gpt-image-1による日本語テキスト対応メインビジュアル
- **章別画像**: Imagen 3による各章コンテンツ最適化画像（第1章〜第6章）

### 管理レベル
1. **新規生成**: 新記事用の画像セット一括生成
2. **個別更新**: 特定画像のみピンポイント更新
3. **一括更新**: 全画像の包括的リニューアル
4. **バージョン管理**: 更新履歴追跡・復元機能

## 🚀 統合画像管理システム

### 推奨：consolidated_image_manager.py
新しい統合システムにより、全ての画像操作が一元化されました。

#### 新規画像生成
```bash
# 全画像生成（アイキャッチ + サムネイル）
python3 scripts/consolidated_image_manager.py generate \
  --outline outputs/article/outline.md \
  --mode all

# アイキャッチのみ生成
python3 scripts/consolidated_image_manager.py generate \
  --outline outputs/article/outline.md \
  --mode eyecatch

# 特定章のサムネイル生成
python3 scripts/consolidated_image_manager.py generate \
  --outline outputs/article/outline.md \
  --mode thumbnail --chapter 3
```

#### 既存記事の画像更新
```bash
# アイキャッチ画像の更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1234 \
  --type eyecatch

# カスタムプロンプトでアイキャッチ更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1234 \
  --type eyecatch \
  --prompt "Custom image prompt"

# 特定章の画像更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1234 \
  --type chapter \
  --chapter-num 3
```

#### 簡単更新（後方互換性）
```bash
# 従来のupdate_eyecatch_simple.pyと同等
python3 scripts/consolidated_image_manager.py quick-update 1234

# カスタムプロンプト指定
python3 scripts/consolidated_image_manager.py quick-update 1234 \
  --prompt "Custom prompt"
```

#### バージョン管理
```bash
# 画像更新履歴の表示
python3 scripts/consolidated_image_manager.py version \
  --post-id 1234 \
  --action history

# 特定タイプの履歴表示
python3 scripts/consolidated_image_manager.py version \
  --post-id 1234 \
  --action history \
  --type eyecatch
```

## 📊 画像更新シナリオ別ガイド

### シナリオ1: 新記事の画像生成
**目的**: 新しく作成した記事に必要な全画像を生成

**推奨手順**:
1. アウトライン作成確認
2. 統合画像管理システムで一括生成
3. 品質確認・最適化
4. WordPress投稿準備

```bash
# Step 1: アウトライン確認
ls outputs/[記事名-INT-XX]/outline.md

# Step 2: 全画像生成
python3 scripts/consolidated_image_manager.py generate \
  --outline outputs/[記事名-INT-XX]/outline.md \
  --mode all

# Step 3: 生成確認
ls outputs/[記事名-INT-XX]/*.jpg
```

### シナリオ2: アイキャッチのみ更新
**目的**: 既存記事のメインビジュアルを改善

**適用場面**:
- SNS拡散力向上のため魅力的な画像に変更
- ブランディング統一のためデザイン刷新
- 記事タイトル変更に伴う画像更新

```bash
# 基本更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type eyecatch

# カスタムプロンプト使用
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type eyecatch \
  --prompt "プロフェッショナルで現代的なChatGPT活用イメージ"
```

### シナリオ3: 特定章の画像更新
**目的**: 特定章の内容により適した画像に変更

**適用場面**:
- 章内容の大幅改訂後
- より理解しやすいビジュアルに変更
- 古い画像の現代化

```bash
# 第3章のみ更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type chapter \
  --chapter-num 3

# 複数章の更新（1-3章）
for i in {1..3}; do
  python3 scripts/consolidated_image_manager.py update \
    --post-id 1388 \
    --type chapter \
    --chapter-num $i
done
```

### シナリオ4: 完全画像リニューアル
**目的**: 記事全体のビジュアル面を一新

**適用場面**:
- 古い記事の現代化
- ブランドリニューアル対応
- 記事の大幅リライト後

```bash
# アイキャッチ更新
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type eyecatch

# 全章画像更新
for i in {1..6}; do
  python3 scripts/consolidated_image_manager.py update \
    --post-id 1388 \
    --type chapter \
    --chapter-num $i
done

# 更新履歴確認
python3 scripts/consolidated_image_manager.py version \
  --post-id 1388 \
  --action history
```

## 🔧 レガシーシステム（段階的廃止予定）

### 従来のアイキャッチ更新
```bash
# update_eyecatch_simple.py（廃止予定）
python3 scripts/update_eyecatch_simple.py 1388

# update_eyecatch_from_title.py（廃止予定）
python3 scripts/update_eyecatch_from_title.py 1388
```

### 従来の章別画像更新
```bash
# image_update_manager.py（廃止予定）
python3 -c "
import sys; sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()
result = engine.smart_replace_image(1388, 'chapter_3', 'regenerate')
"
```

## 📋 画像仕様・最適化

### アイキャッチ画像仕様
- **API**: OpenAI gpt-image-1
- **特徴**: 日本語テキスト対応
- **ターゲットサイズ**: 1200×675px（16:9）
- **最大ファイルサイズ**: 500KB
- **JPEG品質**: 85（段階的調整）
- **フォーマット**: JPEG（最適化済み）

### サムネイル画像仕様
- **API**: Google Imagen 3
- **特徴**: テキストなし、16:9アスペクト比
- **ターゲットサイズ**: 800×450px（16:9）
- **最大ファイルサイズ**: 800KB
- **JPEG品質**: 80（段階的調整）
- **フォーマット**: JPEG（最適化済み）

### 自動最適化機能
- **95%サイズ削減**: 大幅なファイルサイズ圧縮
- **WordPress 504エラー回避**: アップロード制限対応
- **プログレッシブJPEG**: 段階的読み込み対応
- **透明背景合成**: PNG→JPEG変換時の背景処理

## 🛡️ バックアップ・バージョン管理

### 自動バックアップ機能
```bash
# バックアップ有効（デフォルト）
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type eyecatch

# バックアップ無効
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type eyecatch \
  --no-backup
```

### バージョン履歴管理
```json
// outputs/image_version_db.json
{
  "post_1388": {
    "eyecatch": [
      {
        "version_id": "v1_20250718_103045",
        "file_path": "outputs/article-1388/20250718_103045_eyecatch.jpg",
        "prompt": "ChatGPT完全攻略の魅力的なアイキャッチ",
        "created_at": "2025-07-18 10:30:45",
        "file_size": 485672,
        "wordpress_media_id": 3089
      }
    ],
    "chapters": {
      "chapter_1": [
        {
          "version_id": "v1_20250718_103120",
          "file_path": "outputs/article-1388/20250718_103120_chapter1.jpg",
          "created_at": "2025-07-18 10:31:20"
        }
      ]
    }
  }
}
```

### 復元機能
```bash
# 特定バージョンへの復元情報表示
python3 scripts/consolidated_image_manager.py version \
  --post-id 1388 \
  --action restore \
  --version-id v1_20250718_103045
```

## 🔍 品質管理・検証

### 画像品質チェック
```bash
# 生成画像の品質確認
check_image_quality() {
    local image_file="$1"
    local max_size="$2"
    
    # ファイルサイズ確認
    local file_size=$(stat -c%s "$image_file" 2>/dev/null || echo 0)
    if [[ $file_size -gt $max_size ]]; then
        echo "⚠️ ファイルサイズ超過: ${file_size}B > ${max_size}B"
        return 1
    fi
    
    # 画像フォーマット確認
    if file "$image_file" | grep -q "JPEG"; then
        echo "✅ 画像フォーマット: JPEG"
    else
        echo "⚠️ 予期しない画像フォーマット"
        return 1
    fi
    
    echo "✅ 画像品質: 正常"
    return 0
}
```

### WordPress連携確認
```bash
# WordPress画像アップロード確認
verify_wordpress_upload() {
    local post_id="$1"
    local image_type="$2"
    
    # WordPress APIで画像情報取得
    local api_response=$(curl -s -H "X-API-Key: $WORDPRESS_API_KEY" \
        "$WORDPRESS_ENDPOINT/get-post/$post_id")
    
    if echo "$api_response" | grep -q "featured_media"; then
        echo "✅ WordPress連携: 正常"
        return 0
    else
        echo "❌ WordPress連携: 異常"
        return 1
    fi
}
```

## 🚀 運用ベストプラクティス

### 日常運用フロー
1. **新記事作成時**: 統合システムで全画像生成
2. **記事更新時**: 関連画像のみピンポイント更新
3. **定期リニューアル**: 古い記事の画像一括更新
4. **品質監視**: 画像サイズ・品質の定期チェック

### 効率化Tips
```bash
# 複数記事の一括アイキャッチ更新
update_multiple_eyecatch() {
    local post_ids=(1388 1389 1390)
    
    for post_id in "${post_ids[@]}"; do
        echo "記事ID $post_id のアイキャッチ更新中..."
        python3 scripts/consolidated_image_manager.py update \
          --post-id "$post_id" \
          --type eyecatch
        sleep 5  # API制限対策
    done
}

# バッチ処理用スクリプト
python3 -c "
from scripts.consolidated_image_manager import ConsolidatedImageManager
manager = ConsolidatedImageManager()

# 複数記事の処理
post_ids = [1388, 1389, 1390]
for post_id in post_ids:
    manager.update_eyecatch(post_id)
    print(f'記事ID {post_id} 完了')
"
```

### 緊急時対応
```bash
# 画像生成失敗時の再試行
retry_image_generation() {
    local post_id="$1"
    local max_retries=3
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        if python3 scripts/consolidated_image_manager.py update \
           --post-id "$post_id" --type eyecatch; then
            echo "✅ 再試行成功"
            return 0
        fi
        
        retry_count=$((retry_count + 1))
        echo "⏳ 再試行 $retry_count/$max_retries"
        sleep 10
    done
    
    echo "❌ 再試行上限到達"
    return 1
}
```

## 📊 パフォーマンス最適化

### API制限対策
- **リクエスト間隔**: 画像生成間に5秒待機
- **並行処理制限**: 同時生成数を3個以下に制限
- **エラーハンドリング**: API制限エラー時の自動リトライ

### ストレージ最適化
- **自動圧縮**: 95%サイズ削減による容量節約
- **古いバージョン削除**: 10世代を超える履歴の自動削除
- **一時ファイル清理**: 生成失敗時の中間ファイル削除

## 🔧 トラブルシューティング

### よくある問題と解決方法

#### 画像生成エラー
```bash
# エラー原因確認
python3 scripts/consolidated_image_manager.py update \
  --post-id 1388 \
  --type eyecatch \
  --verbose

# API接続確認
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
  https://api.openai.com/v1/models
```

#### WordPress連携エラー
```bash
# WordPress API接続確認
curl -H "X-API-Key: $WORDPRESS_API_KEY" \
  "$WORDPRESS_ENDPOINT/get-post/1388"

# 画像アップロード権限確認
curl -X POST -H "X-API-Key: $WORDPRESS_API_KEY" \
  "$WORDPRESS_ENDPOINT/test-upload"
```

#### ファイルシステムエラー
```bash
# 出力ディレクトリ権限確認
ls -la outputs/
mkdir -p outputs/test_dir
echo "test" > outputs/test_dir/test.txt
rm -rf outputs/test_dir
```

---

この統合ガイドにより、WordPress記事の画像管理が効率的かつ確実に実行できるようになります。統合画像管理システムを活用して、高品質なビジュアルコンテンツを維持してください。