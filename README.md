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
│   ├── image_generator.py      # 画像生成スクリプト
│   └── post_career_article.py  # キャリア記事投稿（旧版）
├── outputs/            # 生成ファイル出力
│   ├── *.md           # 生成記事ファイル
│   └── *.png          # 生成画像ファイル
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
3. **マークダウン変換**: WordPressブロック形式に変換
4. **画像アップロード**: WordPress メディアライブラリにアップロード
5. **記事投稿**: 章別画像付きで WordPress に投稿

## 画像挿入仕様

- **対象見出し**: H2見出しで章番号付き（`1. `, `第1章` など）
- **挿入位置**: 見出し直後
- **画像順序**: chapter1, chapter2, ... の順番で自動対応
- **画像形式**: WordPress ブロックエディタ形式
