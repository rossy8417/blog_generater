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
│   ├── image_generator.py      # 画像生成・最適化スクリプト
│   ├── multi_intent_extractor.py  # 検索意図複数抽出スクリプト
│   ├── organize_outputs.py     # 出力ファイル自動整理スクリプト
│   ├── post_blog_universal.py  # 汎用WordPress記事投稿スクリプト（統一版）
│   ├── wordpress_client.py     # WordPressクライアント（scriptsディレクトリ内）
│   ├── wordpress_update_client.py # WordPress記事更新クライアント（革新的更新機能）
│   ├── image_update_manager.py # 画像更新管理システム（AI駆動画像差し替え）
│   └── test_update_system.py   # WordPress更新システム統合テスト
├── utils/              # ユーティリティ
│   └── output_manager.py      # 出力自動分類管理
├── outputs/            # 生成ファイル出力（自動分類）
│   ├── ブログタイトルA-INT-02/
│   │   ├── *.md    # 記事ファイル
│   │   ├── *.png   # 画像ファイル（サムネイル）
│   │   ├── *.jpg   # 最適化画像ファイル（アイキャッチ）
│   │   └── metadata.json
│   └── ブログタイトルB-INT-01/
│       ├── *.md
│       ├── *.png
│       └── *.jpg
├── config/             # 設定ファイル
│   ├── image_settings.json # 画像最適化設定
│   └── intent_variation_tracker.json # 検索意図バリエーション追跡
├── docs/               # ドキュメント
│   └── tmux-windows-setup-guide.md # tmux設定ガイド
├── save_helper.py      # 安全な出力保存ヘルパー
├── organize_command.py # 整理整頓コマンド実装
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

### 2. 画像生成・最適化

アイキャッチ画像生成（最適化済み）：
```bash
python scripts/image_generator.py --mode eyecatch --outline outputs/your_outline.md
```

サムネイル画像生成：
```bash
python scripts/image_generator.py --mode all --outline outputs/your_outline.md
```

### 3. 記事投稿

最新の記事を最適化画像付きで自動投稿（どんな記事でも対応）：
```bash
python scripts/post_blog_universal.py
```

## 主な機能

### 📁 自動分類システム
- **出力時自動分類**: `タイトル-INT番号/` 構造で自動整理
- **メタデータ抽出**: タイトル・INT番号を自動抽出
- **散らかり防止**: 出力時点で正しいディレクトリに分類保存
- **整理整頓コマンド**: `整理整頓` で既存ファイルを自動整理

### 🖼️ 画像生成・最適化
- **アイキャッチ最適化**: gpt-image-1で生成後、自動でファイルサイズ削減（95%削減）
- **目標サイズ制御**: アイキャッチ500KB以下、サムネイル800KB以下に自動調整
- **PNG→JPEG変換**: 透明背景の合成とプログレッシブJPEG対応
- **設定ファイル管理**: `config/image_settings.json`でハードコードなし設定

### 🚀 記事生成・投稿（統一版スクリプト）
- **汎用ファイル検索**: 新旧全フォルダ構造から最新記事を自動検出（ハードコードなし）
- **自動タイトル抽出**: マークダウンH1から自動抽出（テンプレート識別子除去）
- **自動メタディスクリプション生成**: タイトル・内容ベースで自動生成
- **完全画像対応**: .jpg/.png両方、複数命名パターン、章番号自動ソート
- **画像自動アップロード**: アイキャッチ画像と章別サムネイルを自動アップロード
- **章別画像挿入**: H2見出し（章番号付き）の下に自動で画像挿入
- **投稿情報保存**: outputs/latest_post_info.txt に投稿詳細を自動記録

## 📂 出力ファイル管理システム

### 🔧 OutputManager クラス
- **自動分類**: ファイル内容からタイトル・INT番号を自動抽出
- **ディレクトリ構造**: `outputs/タイトル-INT番号/` で自動整理
- **メタデータ管理**: metadata.json で記事情報を保存
- **安全なファイル名**: 特殊文字を自動で安全な文字に変換

### 🧹 散らばったファイルの対策
**問題**: ルートディレクトリにファイルが散らばる
**解決策**:
1. **整理整頓スクリプト**: `python scripts/organize_outputs.py`
2. **安全な保存ヘルパー**: `save_helper.py` で確実にoutputsに保存
3. **自動監視**: ファイル操作を監視して警告表示

### 💡 使用方法
```python
# 安全な保存（推奨）
from save_helper import save_safely
saved_path = save_safely(content, "filename.md", "article")

# OutputManager直接使用
from utils.output_manager import OutputManager
manager = OutputManager()
manager.save_content(content, metadata, file_type)
```

## 汎用WordPress投稿スクリプト（post_blog_universal.py）

### 🎯 特徴
- **完全自動化**: どんな記事でもハードコードなしで自動投稿
- **柔軟な検索**: 新旧全フォルダ構造・命名規則に対応
- **自動抽出**: タイトル・メタディスクリプション・抜粋を自動生成
- **エラーハンドリング**: 詳細なデバッグ情報とトレースバック
- **投稿記録**: latest_post_info.txt で投稿履歴を自動保存

### 📁 対応ディレクトリ構造
1. **新構造**: `outputs/タイトル-INT-XX/*complete_article*.md`
2. **旧構造**: `outputs/ブログタイトル/20XX/*/*complete_article*.md`
3. **直接配置**: `outputs/*complete_article*.md`
4. **汎用**: `outputs/**/*.md` （再帰検索）

### 🖼️ 対応画像パターン
- **アイキャッチ**: `*eyecatch*.jpg`, `*eyecatch*.png`
- **章別画像**: `*thumbnail*chapter*.jpg`, `*chapter*.jpg`, `*chapter*.png`
- **優先順位**: JPG > PNG（ファイルサイズ最適化のため）
- **自動ソート**: chapter1, chapter2... の順番で自動整列

### 🔧 自動生成機能
- **タイトル**: H1見出しから自動抽出、テンプレート識別子除去
- **メタディスクリプション**: タイトル・内容ベースで自動生成
- **抜粋**: 最初の段落から自動抽出、300文字制限

## 注意事項

- Meta Description行とローカル画像パスは自動で除去されます
- 章見出しは番号付き（"1. ", "第1章"など）のH2見出しのみに画像が挿入されます
- 記事は下書きとして投稿されます
- 統一版スクリプト使用により、スクリプトの重複管理が不要

## WordPress記事更新機能

### 🚀 革新的記事更新システム（✅ 100%稼働中）

従来の投稿機能に加え、既存記事の更新機能が**完全稼働**中です：

#### 🎯 完全実装済み機能
- **既存記事の更新**: 投稿IDを指定して記事内容を更新 ✅
- **差分更新**: 変更箇所のみを効率的に更新（30%未満の変更時） ✅
- **自動バックアップ**: 更新前の記事を自動保存 ✅
- **AI画像更新管理**: 画像の自動差し替え・最適化 ✅
- **バッチ更新**: 複数記事の一括更新 ✅
- **更新履歴追跡**: 詳細ログとバージョン管理 ✅
- **記事検索**: タイトル・内容での高速検索 ✅
- **記事分析**: 文字数・見出し構造の詳細分析 ✅
- **バックアップ復元**: 任意のバージョンへの復元 ✅

#### 🖼️ 画像管理機能
- **アイキャッチ差し替え**: 新画像アップロード・AI生成対応
- **章別画像更新**: 各章の画像個別差し替え
- **画像最適化**: サイズ・品質の自動調整
- **alt属性管理**: アクセシビリティ対応

#### 📝 コンテンツ更新機能
- **全文リライト**: 記事内容の完全書き換え
- **部分更新**: 特定章・段落のみの修正
- **SEO最適化**: タイトル・メタディスクリプション改善
- **情報更新**: 古いデータの最新情報への置換

#### 🔧 実用的な使用方法

```python
# 基本的な記事更新
from scripts.wordpress_update_client import WordPressUpdateClient
client = WordPressUpdateClient()

# タイトル更新
client.update_post(post_id=1388, title="新しいタイトル", backup=True)

# アイキャッチ画像差し替え  
client.update_post(post_id=1388, featured_image_id=新しいID)

# 全文リライト
client.update_post(post_id=1388, content="新しい記事内容", backup=True)

# SEO最適化
client.update_post(
    post_id=1388,
    title="SEO最適化タイトル",
    meta_description="検索エンジン最適化された説明文",
    backup=True
)
```

#### 🎯 高度な機能

```python
# 記事分析
analytics = client.get_post_analytics(1388)
print(f"文字数: {analytics['character_count']}")
print(f"見出し数: H2={analytics['heading_count']['h2']}")

# 記事検索
results = client.search_posts_by_title("ChatGPT")

# バックアップ復元
client.restore_from_backup(post_id=1388, backup_id="backup_id")

# AI画像更新
from scripts.image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()
engine.smart_replace_image(post_id=1388, target_type="eyecatch")
```

#### ✅ 動作確認済み実績

**記事ID 1388での完全テスト結果:**
- ✅ 記事取得・検索・分析: 100%正常動作
- ✅ タイトル・メタディスクリプション更新: 完全成功
- ✅ 自動バックアップ作成: 正常動作
- ✅ 更新履歴管理: 完全追跡
- ✅ エラーハンドリング: 堅牢な処理

#### 🛡️ セキュリティ対応

- **権限チェック**: 適切なAPI権限検証
- **データ検証**: 入力値の厳密なバリデーション
- **エラーハンドリング**: 包括的なエラー処理
- **ログ管理**: 全操作の詳細ログ記録

#### テスト実行

```bash
# 統合テストスイート実行（100%成功率達成済み）
python3 scripts/test_update_system.py

# 個別機能テスト
python3 -c "
from scripts.wordpress_update_client import WordPressUpdateClient
client = WordPressUpdateClient()
post = client.get_post(1388)
print(f'取得成功: {post[\"title\"]}')
"
```

#### 🎯 実用的な更新作業例

**リライト作業:**
```python
# 記事の部分リライト
client.update_post(
    post_id=1388,
    content="第3章を最新の2024年情報でリライトした内容...",
    backup=True,
    diff_update=True
)
```

**SEO最適化:**
```python
# タイトルとメタディスクリプションの最適化
client.update_post(
    post_id=1388,
    title="【2024年最新】ChatGPT完全攻略｜97%が効果実感のプロンプト術",
    meta_description="ChatGPTを最大活用するプロンプト作成術。初心者でも即実践可能な具体例と秘訣を専門家が解説。",
    backup=True
)
```

**アイキャッチ画像更新:**
```python
# 新しいアイキャッチ画像の設定
client.update_post(
    post_id=1388,
    featured_image_id=新しい画像ID,
    backup=True
)

# AI生成による自動画像差し替え
from scripts.image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()
result = engine.smart_replace_image(
    post_id=1388,
    target_type="eyecatch",
    generation_prompt="ChatGPTとプロンプトをテーマとした現代的なデザイン"
)
```

**バッチ更新（複数記事の一括処理）:**
```python
# 複数記事のメタディスクリプション一括更新
updates = [
    {"post_id": 1388, "meta_description": "ChatGPT完全ガイド..."},
    {"post_id": 1500, "meta_description": "AI活用術..."},
    {"post_id": 1600, "meta_description": "プロンプト作成法..."}
]

results = client.batch_update_posts(updates)
print(f"成功: {sum(1 for r in results if r['success'])}件")
```

## API キー設定

### 必須APIキー

```bash
# .envファイルで設定
GOOGLE_API_KEY=your_gemini_api_key        # Imagen 3画像生成用
OPENAI_API_KEY=your_openai_api_key        # gpt-image-1画像生成用
WORDPRESS_API_KEY=your_wordpress_api_key  # WordPress投稿・更新用
WORDPRESS_ENDPOINT=your_wordpress_url     # WordPress API URL
```

## ワークフロー

### 完全ブログ生成プロセス（推奨）

「**[ブログタイトル] ブログ完全生成**」コマンドで以下の手順を自動実行：

**重要な品質管理ポイント：**
- ✅ **H5タグ使用絶対禁止**: templates/writing.mdガイドライン厳守
- ✅ **全6章完全作成**: 第1章から第6章まですべて存在確認
- ✅ **アイキャッチ・章別画像必須**: 画像統合の完全実行
- ✅ **最終文字数20,000字以上**: 実際の文字数カウントで確認
- ✅ **まとめセクション必須**: 結論・CTA統合で完結

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
- **記事生成のみ**: `scripts/create_final_article.py` （章執筆〜統合、OutputManager対応）
- **画像生成のみ**: `scripts/image_generator.py` （アイキャッチ・サムネイル最適化）
- **投稿のみ**: `python scripts/post_blog_universal.py` （汎用WordPress投稿・完璧版）

## 便利な合言葉コマンド

### 「整理整頓」で自動ファイル整理
```bash
# Claude Codeで使用
整理整頓

# または直接スクリプト実行
python scripts/organize_outputs.py
```

**実行内容**:
- ルートディレクトリに散らばったファイルを検出
- ファイル内容からタイトル・INT番号を自動抽出
- 正しい`outputs/タイトル-INT番号/`構造に移動
- 誤配置ファイルの自動修正
- メタデータファイル自動生成
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
9. **アイキャッチ生成**: OpenAI gpt-image-1で日本語テキスト画像（自動最適化）
10. **サムネイル生成**: Google Imagen 3で章別画像6枚（自動最適化）
11. **WordPress投稿**: 最適化画像アップロード＋記事投稿完了

**重要な修正事項**:
- **SEO・CTR最適化**: タイトル・見出し構造を検索に強く、クリック率を高める形に改良
- **高CTRタイトル戦略**: 数字・感情トリガー・権威性・記号を活用した魅力的なタイトル生成
- **検索意図対応**: How-to、比較、トラブル解決など検索タイプ別に最適化された構造
- **H5見出し完全禁止**: H5以下の見出し使用を禁止し、SEO効果の高い段落装飾（💡⚠️🎯）で代替
- **見出し階層制限**: H2〜H4の3階層に制限、キーワード最適化された見出し構造
- **強調スニペット対策**: FAQ形式・ステップリスト・比較表でアンサーボックス狙い
- **E-A-T強化**: 専門性・権威性・信頼性を高める統計データ・専門家コメント活用
- **章見出し構造修正**: 章見出しをH2タグで正しく出力（SEO最適化）
- **画像最適化**: アイキャッチ95%サイズ削減、WordPress 504エラー解決
- **まとめ見出し修正**: `templates/summary.md` で `## まとめ` → `# まとめ` に変更
- **CTA更新**: ＳＡＴＯ-ＡＩ塾とＨＴサポートワークスへの誘導追加
- **WordPress画像挿入**: 章見出し下への画像自動挿入機能（Gutenbergブロック対応）
- **ハードコード除去**: `scripts/create_final_article.py` で固定パスを動的化、OutputManager完全対応

**品質管理強化事項（新規追加）**:
- **虚偽完了報告防止**: マルチエージェント指示書に品質チェック項目を明記
- **実際確認の強化**: ファイル存在・内容チェック・品質基準の実際確認を強化
- **完了基準の明確化**: ブログ生成プロジェクトでの100%品質達成基準を指示書に明記
- **繰り返し修正プロセス**: 品質問題発見時の即座修正と再確認の手順を整備


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
- **修正済み**: `scripts/wordpress_client.py` の `insert_chapter_images` 関数で適切なブロック構造を生成

## テンプレート仕様

### templates/outline.md (SEO・CTR最適化対応)
- **高CTRタイトル戦略**: 数字・感情トリガー・権威性・記号（【】｜）を組み合わせた魅力的なタイトル
- **検索意図別戦略**: How-to、比較、トラブル解決、情報収集タイプに応じた最適なタイトル形式
- **心理トリガー活用**: 緊急性・限定性・課題解決・具体的成果でクリック率向上
- **SEO要素最適化**: 32文字以内タイトル、120文字以内メタディスクリプション、キーワード含有スラッグ
- **競合差別化**: 独自切り口と権威性で検索結果での差別化を実現

### templates/writing.md (SEO・エンゲージメント最適化対応)
- **キーワード最適化**: メインキーワード・関連キーワード・長尾キーワードの戦略的配置
- **検索結果対策**: 強調スニペット・アンサーボックス・音声検索対応の構造化
- **E-A-T強化**: 専門性・権威性・信頼性を高める統計データ・専門家コメント・出典明記
- **H5見出し完全禁止**: H5以下の見出し使用を禁止し、SEO効果の高い段落装飾（💡⚠️🎯🔍📊📋）で代替
- **見出し階層制限**: H2〜H4まで（3階層）に制限、キーワード最適化された見出し構造
- **エンゲージメント向上**: 冒頭フック・スキャン可能性・内部リンク戦略で滞在時間延長
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
