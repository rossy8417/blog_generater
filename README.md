# ブログ記事作成ワークフロー（完全自動化版）

## 🚀 ブログ完全生成コマンド

Claude Codeに以下の合言葉を入力すると、キーワードからWordPress投稿まで完全自動実行されます：

```
ブログ完全生成
```

**実行フロー：**
1. キーワード入力（例：「バイブコーディング エンジニア 未来」）
2. 検索意図分析→意図分割→章立て作成
3. 全章ライティング実行（6章構成）
4. ファクトチェック・記事修正
5. リード文・まとめ文作成
6. **画像生成**：アイキャッチ（gpt-image-1）+ サムネイル×6（imagen-3.0）
7. **WordPress投稿**：画像付き完全版記事をドラフト投稿

## ⚠️ 重要なルール・エラーハンドリング

### 🔑 APIキー要件
```bash
# 必須APIキー（.envファイルで設定）
GOOGLE_API_KEY=your_gemini_api_key        # Imagen 3画像生成用
OPENAI_API_KEY=your_openai_api_key        # gpt-image-1画像生成用（組織認証必須）
WORDPRESS_API_KEY=your_wordpress_api_key  # WordPress投稿用
WORDPRESS_ENDPOINT=your_wordpress_url     # WordPress API URL
```

### ❌ エラー発生時の対応ルール

**APIエラーで先に進めない場合：**
- **401 Unauthorized**: APIキーが無効
- **429 Rate Limit**: API使用量上限
- **500 Server Error**: サーバー側問題

**→ 上記エラー発生時は、その旨を明確に伝えて処理を中断する**
**→ ユーザーにAPIキー確認・更新を依頼してから再開する**

### 🎯 確実な実行順序

1. **画像生成**
   - アイキャッチ: `gpt-image-1` (日本語タイトル付き、1920x1080)
   - サムネイル: `imagen-3.0` (各章専用、1408x768)
   - 拡張子付きファイル作成（.png）

2. **WordPress投稿**
   - 画像アップロード（全7枚）
   - 各章h2タグ下部にサムネイル1枚ずつ配置
   - アイキャッチ設定（featured_image_id）
   - ドラフトステータスで安全投稿

### 🖼️ 画像配置の確実な実現

**正しい配置パターン：**
```
記事構成：
├── アイキャッチ画像（gpt-image-1、日本語タイトル付き）
├── リード文
├── 目次
├── 第1章 h2見出し
│   ├── chapter1サムネイル画像（imagen-3.0）
│   └── 第1章本文
├── 第2章 h2見出し
│   ├── chapter2サムネイル画像（imagen-3.0）
│   └── 第2章本文
...（第6章まで）
└── まとめ文
```

**技術実装：**
- `insert_chapter_images()` 関数で各h2見出し直後に対応画像を挿入
- 章番号順でソート処理
- WordPressブロック形式で正確な画像埋め込み

## 📝 部分実行コマンド

### ブログ構成作成のみ
```
ブログワークフロー実行
```

### 記事執筆のみ
```
ライティング実行
```

### WordPress投稿のみ
```
ブログ投稿
```

## 🎨 画像生成の特徴

### アイキャッチ画像（gpt-image-1）
- **日本語テキスト対応**: 記事タイトルを画像内に日本語で表示
- **プロフェッショナルデザイン**: 高品質なビジュアルデザイン
- **16:9自動拡張**: 1536x1024 → 1920x1080に自動変換
- **SNS最適化**: シェア時の視認性確保

### サムネイル画像（imagen-3.0）
- **テキストなし**: 純粋なビジュアル表現
- **章別統一感**: 一貫したデザインテーマ
- **高解像度**: 1408x768の鮮明な画質
- **内容象徴化**: 各章テーマの視覚的表現

## 🔧 汎用システム設計

### wordpress_client.py主要機能
```python
# 画像アップロード
client.upload_image(image_path, alt_text)

# 章別画像挿入（汎用関数）
insert_chapter_images(wp_content, chapter_images)

# WordPress投稿
client.create_post(title, content, featured_image_id=id)
```

### 自動ファイル管理
```
outputs/
├── YYYYMMDD_HHMMSS_intent_analysis.md       # 検索意図分析
├── YYYYMMDD_HHMMSS_divided_intents.json     # 意図分割JSON
├── YYYYMMDD_HHMMSS_outline_INT-01.md        # 章立てアウトライン
├── YYYYMMDD_HHMMSS_article_INT-01_chapter*.md  # 各章記事
├── YYYYMMDD_HHMMSS_lead_summary_INT-01.md   # リード・まとめ文
├── YYYYMMDD_HHMMSS_complete_article_INT-01.md # 統合記事
├── YYYYMMDD_HHMMSS_image_prompts_INT-01.md  # 画像生成プロンプト
├── YYYYMMDD_HHMMSS_generated_images.json    # 画像データ
├── eyecatch_***.png                         # アイキャッチ画像
├── chapter1_***.png                         # 各章サムネイル
└── uploaded_thumbnails.json                 # アップロード結果
```

## 🎯 品質保証機能

### ファクトチェック
- WebSearch/WebFetchによる事実確認
- 複数情報源での照合
- 統計データ・研究結果の検証
- 専門家・機関情報の信頼性確認

### 記事修正・引用元追加
- 不正確な情報の特定・修正
- 信頼できる参考文献の追加
- 専門家名の匿名化
- 研究機関情報の一般化

### 完成度保証
- **文字数**: 約25,000文字の包括的ガイド
- **章構成**: 6章の論理的構成
- **画像品質**: プロフェッショナルレベル
- **WordPress互換**: ブロックエディタ完全対応

## 🚀 次回以降の実行

**汎用性確保により、毎回同じ手順で高品質ブログが生成可能：**

1. 「ブログ完全生成」コマンド実行
2. キーワード入力（任意のテーマ）
3. APIキー確認（エラー時は処理中断）
4. 自動生成（約30-60分）
5. WordPress確認・公開

**ハードコード排除：**
- ファイル名・記事内容の動的生成
- 汎用的な画像挿入機能
- タイムスタンプベースの管理
- 再利用可能なワークフロー

## 📊 実績・成果例

**生成記事例：「バイブコーディング」**
- 投稿ID: 2765
- 画像: アイキャッチ(ID:2752) + サムネイル×6(ID:2756-2761)
- 文字数: 約25,000文字
- 構成: 完全なエンジニアガイド
- 品質: 出版レベルの専門性

---

**🌟 これで「真のブログ完全生成」システムが確立されました！**# blog_generater
