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

### 完全ブログ生成プロセス（推奨）

「**[ブログタイトル] ブログ完全生成**」コマンドで以下の手順を自動実行：

#### Phase 1: コンテンツ企画・設計
1. **検索意図分析**: `templates/intent.md` で3語キーワードの複合的ニーズを分析
2. **意図分割**: `templates/division.md` で個別検索意図をINT-01, INT-02...に分割・JSON化
3. **アウトライン生成**: `templates/outline.md` で記事構成・章立て作成

#### Phase 2: コンテンツ作成
4. **各章コンテンツ作成**: `templates/writing.md` で章別内容執筆（第1章〜第6章）
5. **ファクトチェック実施**: 専門的内容の正確性検証と信頼性確保
6. **リード文生成**: `templates/lead.md` で導入部分作成
7. **まとめ生成**: `templates/summary.md` で結論・CTA作成
8. **完全記事統合**: 全セクションを統合した完全版記事作成

#### Phase 3: 画像生成・公開
9. **アイキャッチ画像生成**: OpenAI gpt-image-1で日本語テキスト付き画像作成
10. **章別サムネイル生成**: Google Imagen 3で各章のサムネイル画像作成（6章分）
11. **WordPress投稿**: 画像アップロード＋記事投稿（章別画像自動挿入）

### 個別実行の場合

#### Phase 1: 企画・設計段階
- **キーワード分析**: `templates/intent.md` で3語キーワードの検索意図分析
- **意図分割**: `templates/division.md` で意図をINT-01, INT-02形式でJSON化
- **アウトライン作成**: `templates/outline.md` で章立て・構成設計

#### Phase 2-3: 作成・公開段階
- **記事生成のみ**: `scripts/create_final_article.py` （章執筆〜統合）
- **画像生成のみ**: `scripts/image_generator.py` （アイキャッチ・サムネイル）
- **投稿のみ**: `scripts/post_blog_article.py` （WordPress投稿）

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

### 「バルス」で出力ディレクトリ完全消去
```bash
# Claude Codeで使用
バルス
```

**実行内容**:
- outputs/ディレクトリ内の全ファイル・フォルダを削除
- 古い記事データや画像ファイルを一括削除
- 新しいプロジェクト開始時のクリーン環境作成

### 「ブログ完全生成」でワンストップ作成
```bash
# Claude Codeで使用
[ブログタイトル] ブログ完全生成
```

**実行プロセス（11ステップ）**:

**Phase 1: 企画・設計**
1. **検索意図分析**: `templates/intent.md` でキーワード複合ニーズ分析
2. **意図分割**: `templates/division.md` で個別意図をINT番号付きJSON化
3. **アウトライン生成**: `templates/outline.md` で記事構成・章立て作成

**Phase 2: コンテンツ作成**
4. **各章執筆**: `templates/writing.md` で第1章〜第6章作成
5. **ファクトチェック**: 専門内容の正確性検証
6. **リード文作成**: `templates/lead.md` で導入部分作成
7. **まとめ作成**: `templates/summary.md` で結論・CTA作成
8. **記事統合**: 全セクション統合で完全版記事完成

**Phase 3: 画像生成・公開**
9. **アイキャッチ生成**: OpenAI gpt-image-1で日本語テキスト画像
10. **サムネイル生成**: Google Imagen 3で章別画像6枚
11. **WordPress投稿**: 画像アップロード＋記事投稿完了

**重要な修正事項**:
- **H5見出し禁止**: `templates/writing.md` でH5以下の見出し使用を禁止（段落より小さくなるため）
- **まとめ見出し修正**: `templates/summary.md` で `## まとめ` → `# まとめ` に変更
- **CTA更新**: ＳＡＴＯ-ＡＩ塾とＨＴサポートワークスへの誘導追加
- **WordPress画像挿入**: 章見出し下への画像自動挿入機能（Gutenbergブロック対応）


### OutputManager クラス
```python
from utils.output_manager import OutputManager

manager = OutputManager()

# 自動分類して保存
manager.save_content(content, metadata, 'complete_article')
manager.save_binary(image_data, metadata, 'eyecatch')
```

## 画像挿入仕様

- **対象見出し**: H2見出しで章番号付き（`第1章`, `第2章` など）
- **挿入位置**: 見出し直後に独立した画像ブロックとして挿入
- **画像順序**: chapter1, chapter2, ... の順番で章番号と自動対応
- **画像形式**: WordPress Gutenbergブロックエディタ形式（paragraphブロックに入れない）
- **修正済み**: `wordpress_client.py` の `insert_chapter_images` 関数で適切なブロック構造を生成

## テンプレート仕様

### templates/writing.md
- **H5見出し禁止**: `####`（H5）や`#####`（H6）は段落より字が小さくなるため使用禁止
- **章末まとめ禁止**: 各章の末尾にまとめセクションは作成しない
- **テンプレート識別子除去**: `H3-1`、`H3-2`などの識別子は実際の見出し名に変換

### templates/summary.md
- **見出しレベル**: `## まとめ` → `# まとめ` に変更
- **CTA更新**: SATO-AI塾とHTサポートワークスへの誘導リンク追加

## WordPress投稿での注意事項

- **画像ブロック構造**: 章見出し下に独立した画像ブロックとして挿入
- **メタデータ除去**: Meta Description行とローカル画像パスは自動除去
- **ブロック形式**: マークダウンからWordPressブロックエディタ形式に自動変換
- **下書き投稿**: 記事は下書き状態で投稿される
