# Blog Generator

WordPressブログ記事の自動生成・投稿システム

## フォルダ構造

```
blog_generator/
├── templates/          # プロンプトテンプレート
│   ├── writing.md      # 記事執筆用テンプレート
│   ├── lead.md         # リード文生成テンプレート
│   ├── summary.md      # まとめ生成テンプレート
│   ├── outline.md      # アウトライン生成テンプレート
│   ├── intent.md       # インテント分析テンプレート
│   ├── division.md     # 章分割テンプレート
│   ├── eyecatch.md     # アイキャッチ画像生成テンプレート
│   ├── thumbnail.md    # サムネイル画像生成テンプレート
│   └── paragraph-example.md  # 段落例テンプレート
├── scripts/            # 実行用スクリプト
│   ├── post_blog_article.py   # 汎用記事投稿スクリプト
│   ├── create_final_article.py  # 記事作成スクリプト
│   └── image_generator.py      # 画像生成スクリプト
│  
├── utils/              # ユーティリティ
│   └── output_manager.py      # 出力自動分類管理
├── outputs/            # 生成ファイル出力（自動分類）
│   ├── ブログタイトルA-INT-02/
│   │   ├── *.md    # 記事ファイル
│   │   ├── *.png   # 画像ファイル
│   │   └── metadata.json
│   └── ブログタイトルB-INT-01/
│       ├── *.md
│       └── *.png
├── wordpress_client.py # WordPressクライアント
├── requirements.txt   # Python依存関係
├── generate_template.yaml  # 生成設定
└── README.md          # このファイル
```

## 使用方法

### 1. 環境設定

```bash
pip install -r requirements.txt
```

`.env`ファイルを作成し、以下を設定：

```
WORDPRESS_API_KEY=your_api_key
WORDPRESS_ENDPOINT=https://your-site.com/wp-json/blog-generator/v1
OPENAI_API_KEY=your_openai_key
```

### 2. 記事投稿

最新の記事を自動投稿：
```bash
python scripts/post_blog_article.py
```

特定の記事を投稿：
```bash
python scripts/post_blog_article.py --article outputs/your_article.md
```

## 主な機能

### 📁 自動分類システム
- **出力時自動分類**: `タイトル-INT番号/` 構造で自動整理
- **メタデータ抽出**: タイトル・INT番号を自動抽出
- **散らかり防止**: 出力時点で正しいディレクトリに分類保存
- **整理整頓コマンド**: `整理整頓` で既存ファイルを自動整理

### 🚀 記事生成・投稿
- **自動ファイル検索**: outputs/フォルダから最新の記事と画像を自動検出
- **画像自動アップロード**: アイキャッチ画像と章別サムネイルを自動アップロード
- **章別画像挿入**: H2見出し（章番号付き）の下に自動で画像挿入
- **メタデータ抽出**: 記事からタイトル、メタディスクリプション、抜粋を自動抽出
- **マークダウン変換**: WordPressブロックエディタ形式に自動変換

## 注意事項

- Meta Description行とローカル画像パスは自動で除去されます
- 章見出しは番号付き（"1. ", "第1章"など）のH2見出しのみに画像が挿入されます
- 記事は下書きとして投稿されます

## API キー設定

### 必須APIキー

```bash
# .envファイルで設定
GOOGLE_API_KEY=your_gemini_api_key        # Imagen 3画像生成用
OPENAI_API_KEY=your_openai_api_key        # gpt-image-1画像生成用
WORDPRESS_API_KEY=your_wordpress_api_key  # WordPress投稿用
WORDPRESS_ENDPOINT=your_wordpress_url     # WordPress API URL
```

## ワークフロー

1. **記事生成**: プロンプトテンプレートを使用してコンテンツ作成
2. **画像生成**: アイキャッチ（OpenAI）とサムネイル（Imagen）を生成  
3. **ファクトチェック**: 専門的内容の正確性検証と信頼性確保
4. **自動分類保存**: `OutputManager`が適切なディレクトリに自動分類
5. **マークダウン変換**: WordPressブロック形式に変換
6. **画像アップロード**: WordPress メディアライブラリにアップロード
7. **記事投稿**: 章別画像付きで WordPress に投稿

## 便利な合言葉コマンド

### 「整理整頓」で自動ファイル整理
```bash
# Claude Codeで使用
整理整頓
```

**実行内容**:
- outputs配下の散らかったファイルを検出
- ファイル内容からタイトル・INT番号を自動抽出
- 正しい`タイトル-INT番号/`構造に移動
- 誤配置ファイルの自動修正
- 整理結果の詳細レポート表示

### 「ブログ完全生成」でワンストップ作成
```bash
# Claude Codeで使用
[ブログタイトル] ブログ完全生成
```

**実行内容**:
1. アウトライン生成（章構成）
2. 各章コンテンツ作成
3. リード文・まとめ生成
4. ファクトチェック実施
5. 完全版記事統合
6. アイキャッチ・サムネイル画像生成（全章分）
7. WordPress投稿準備完了

### OutputManager クラス
```python
from utils.output_manager import OutputManager

manager = OutputManager()

# 自動分類して保存
manager.save_content(content, metadata, 'complete_article')
manager.save_binary(image_data, metadata, 'eyecatch')
```

## 画像挿入仕様

- **対象見出し**: H2見出しで章番号付き（`1. `, `第1章` など）
- **挿入位置**: 見出し直後
- **画像順序**: chapter1, chapter2, ... の順番で自動対応
- **画像形式**: WordPress ブロックエディタ形式
