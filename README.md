# Blog Generator

WordPressブログ記事の自動生成・投稿システム

## フォルダ構造

```
blog_generator/
├── templates/          # プロンプトテンプレート
│   ├── writing.md      # 記事執筆用テンプレート（SEO最適化パターン）
│   ├── lead.md         # リード文生成テンプレート
│   ├── summary.md      # まとめ生成テンプレート
│   ├── outline.md      # アウトライン生成テンプレート（SEO最適化パターン）
│   ├── intent.md       # インテント分析テンプレート（検索キーワード用）
│   ├── division.md     # 章分割テンプレート（検索意図分割用）
│   ├── story_outline_template.md  # ストーリー型アウトライン（読み物重視パターン）
│   ├── story_writing_template.md  # ストーリー型執筆（読み物重視パターン）
│   ├── eyecatch.md     # アイキャッチ画像生成テンプレート
│   ├── thumbnail.md    # サムネイル画像生成テンプレート
│   └── paragraph-example.md  # 段落例テンプレート
├── scripts/            # 実行用スクリプト
│   ├── consolidated_image_manager.py # 統合画像管理システム（新規生成・更新・バージョン管理）
│   ├── image_generator.py      # 画像生成・最適化スクリプト（後方互換性）
│   ├── multi_intent_extractor.py  # 検索意図複数抽出スクリプト
│   ├── post_blog_universal.py  # 汎用WordPress記事投稿スクリプト（品質チェック統合版）
│   ├── pre_wordpress_quality_checker.py # WordPress投稿前品質チェック・自動修正システム
│   ├── wordpress_client.py     # WordPressクライアント（scriptsディレクトリ内）
│   ├── wordpress_update_client.py # WordPress記事更新クライアント（革新的更新機能）
│   ├── # ※ 以下のレガシーファイルはconsolidated_image_manager.pyへ統合済み
│   ├── # image_update_manager.py -> consolidated_image_manager.py
│   ├── # update_eyecatch_simple.py -> consolidated_image_manager.py
│   ├── heading_validator.py    # 見出し構造検証ツール（H5禁止・階層チェック）
│   ├── validate_article.py     # 投稿前記事検証CLIツール（レガシー）
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
├── config/             # 設定・ルールファイル（AI最適化YAML形式）
│   ├── api_endpoint_rules.yaml   # WordPress APIエンドポイント使用ルール
│   ├── rewrite_options.yaml      # 記事リライト戦略・オプション
│   ├── article_update_procedures.yaml # 記事更新手順・プロシージャ
│   ├── file_management_rules.yaml # ファイル管理統一ルール
│   ├── image_management_rules.yaml # 画像管理統一ルール（consolidated統合版）
│   ├── quality_check_rules.yaml  # WordPress品質チェック・自動修正ルール
│   ├── image_settings.json       # 画像最適化設定
│   └── intent_variation_tracker.json # 検索意図バリエーション追跡
├── docs/               # ドキュメント・履歴（説明系）
│   ├── system-improvements-history.md # Phase1開発履歴
│   └── shell-script-integration-report.md # シェルスクリプト統合レポート
├── Claude-Code-Blog-communication/ # tmux関連システム
│   ├── agent-send.sh             # エージェント間通信スクリプト
│   ├── monitoring_system.sh      # 監視システム
│   ├── docs/
│   │   └── tmux-windows-setup-guide.md # tmux設定ガイド
│   └── instructions/             # エージェント指示書
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

#### 統合画像管理システム（推奨）
アイキャッチ画像生成（最適化済み）：
```bash
python scripts/consolidated_image_manager.py generate --mode eyecatch --outline outputs/your_outline.md
```

サムネイル画像生成：
```bash
python scripts/consolidated_image_manager.py generate --mode all --outline outputs/your_outline.md
```

#### WordPress画像更新（統合版）
```bash
# アイキャッチ更新
python scripts/consolidated_image_manager.py update --post-id 1234 --type eyecatch

# 章別画像更新
python scripts/consolidated_image_manager.py update --post-id 1234 --type chapter --chapter-num 1

# 簡単更新（後方互換性）
python scripts/consolidated_image_manager.py quick-update 1234
```

#### レガシー版（統合版への移行推奨）
```bash
# 新規画像生成（レガシー）
python scripts/image_generator.py --mode eyecatch --outline outputs/your_outline.md
python scripts/image_generator.py --mode all --outline outputs/your_outline.md

# ※ レガシーファイルは統合版へ移行済み・削除済み
# レガシーコマンド統合:
# update_eyecatch_simple.py -> consolidated_image_manager.py quick-update
# image_update_manager.py -> consolidated_image_manager.py update
```

### 3. 記事投稿

#### 3.1 投稿前品質チェック（推奨）
```bash
# 包括的品質チェック・自動修正
python scripts/pre_wordpress_quality_checker.py outputs/記事名-INT-01/complete_article.md

# 従来の見出し構造検証のみ（レガシー）
python scripts/validate_article.py outputs/記事名-INT-01/complete_article.md
```

#### 3.2 記事投稿
最新の記事を品質チェック付きで自動投稿（推奨）：
```bash
# 品質チェック統合版（推奨）- post_blog_universal.pyに統合済み
python scripts/post_blog_universal.py
```
**注意**: 品質チェックで問題が発見された場合、自動修正を実施するか投稿を中止します

## 主な機能

### 🎯 WordPress投稿前品質チェック・自動修正システム（NEW）
- **包括的品質検証**: 見出し構造・コンテンツ・SEO要素の統合チェック
- **自動修正機能**: テンプレート識別子除去・見出し階層修正・形式整備
- **H5/H6タグ防止**: 見出し階層ルールの厳格な執行と自動修正
- **WordPress変換検証**: Gutenbergブロック生成の事前確認
- **品質レポート生成**: 詳細な品質評価と改善提案の自動生成
- **投稿可否判定**: 品質基準に基づく自動投稿制御

### 🔍 見出し構造検証システム（レガシー）
- **投稿前検証**: H5/H6タグ禁止・階層構造の自動チェック
- **テンプレート識別子検出**: H3-1等の残存を自動検出・警告
- **WordPress変換検証**: Gutenbergブロック生成時の構造確認
- **自動投稿中止**: 問題発見時にWordPress投稿を自動停止
- **詳細レポート**: 修正すべき問題の具体的な指摘と解決方法

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

### 🚀 記事生成・投稿（品質チェック統合版スクリプト）
- **品質チェック統合**: WordPress投稿前の包括的品質検証と自動修正（post_blog_universal.pyに統合済み）
- **汎用ファイル検索**: 新旧全フォルダ構造から最新記事を自動検出（ハードコードなし）
- **自動タイトル抽出**: マークダウンH1から自動抽出（テンプレート識別子自動除去）
- **自動メタディスクリプション生成**: タイトル・内容ベースで自動生成
- **完全画像対応**: .jpg/.png両方、複数命名パターン、章番号自動ソート
- **画像自動アップロード**: アイキャッチ画像と章別サムネイルを自動アップロード
- **章別画像挿入**: H2見出し（章番号付き）の下に自動で画像挿入
- **包括的品質検証**: 見出し構造・コンテンツ・SEO要素の統合チェック
- **自動修正機能**: 品質問題の自動検出と修正実行
- **品質レポート生成**: 詳細な品質評価と改善提案の自動出力
- **投稿可否制御**: 品質基準に基づく自動投稿制御
- **投稿情報保存**: outputs/latest_post_info.txt に投稿詳細を自動記録

### 🖼️ 統合画像管理システム（NEW）
- **統合機能**: 新規画像生成・WordPress画像更新・バージョン管理を統合
- **新規画像生成**: アイキャッチ（OpenAI gpt-image-1）・サムネイル（Google Imagen 3）
- **WordPress画像更新**: 既存記事の画像差し替え・最適化・バージョン管理
- **後方互換性**: 従来のimage_generator.pyインターフェース維持
- **コマンド統合**: generate（新規生成）・update（更新）・version（バージョン管理）
- **簡単更新**: quick-update機能で統合された操作体系

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

詳細は `save_helper.py` および `utils/output_manager.py` を参照してください。

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

#### 🖼️ 画像管理機能（統合画像管理システム強化）
- **統合管理**: 新規生成・WordPress更新・バージョン管理を単一システムで統合
- **アイキャッチ差し替え**: 新画像アップロード・AI生成対応（consolidated_image_manager.py）
- **gpt-image-1自動生成**: 記事タイトルから日本語テキスト入りアイキャッチを自動生成・更新
- **章別画像更新**: 各章の画像個別差し替え（Imagen 3使用）
- **統合画像更新**: アイキャッチ+章別画像の選択的更新システム
- **画像最適化**: サイズ・品質の自動調整（95%削減・Progressive JPEG変換）
- **バージョン管理**: 画像更新履歴の追跡・復元機能
- **alt属性管理**: アクセシビリティ対応
- **統合システム**: consolidated_image_manager.pyによる一元化

> **📋 画像更新ガイド**: 
> - **[統合画像管理ルール](config/image_management_rules.yaml)**: 新規生成・更新・バージョン管理の統合システム（AI最適化YAML形式）

#### 📝 コンテンツ更新機能
- **全文リライト**: 記事内容の完全書き換え
- **部分更新**: 特定章・段落のみの修正
- **SEO最適化**: タイトル・メタディスクリプション改善
- **情報更新**: 古いデータの最新情報への置換

#### 🔧 使用例

詳細な使用方法は `docs/` 内の各ガイドを参照してください。

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

詳細なテスト手順は関連ドキュメントを参照してください。

#### 🎯 更新作業例

詳細なコード例と手順は関連ドキュメントを参照してください。

## API キー設定

### 必須APIキー

```bash
# .envファイルで設定
GOOGLE_API_KEY=your_gemini_api_key        # Imagen 3画像生成 + ファクトチェック用
OPENAI_API_KEY=your_openai_api_key        # gpt-image-1画像生成用
WORDPRESS_API_KEY=your_wordpress_api_key  # WordPress投稿・更新用
WORDPRESS_ENDPOINT=your_wordpress_url     # WordPress API URL
```

## ワークフロー

### 完全ブログ生成プロセス（推奨）

#### 📝 2つの記事生成パターン

**🔍 SEO最適化重視パターン（キーワードベース）**
- 検索キーワードから検索意図を分析→複数の記事企画に分割→SEO特化記事作成
- テンプレート: intent.md → division.md → outline.md → writing.md
- 適用例: "AI 業務効率化", "リモートワーク ツール", "DX 導入手順" など

**📖 読み物品質重視パターン（テーマベース）**
- 確定したテーマから直接読み物として魅力的な記事を作成
- テンプレート: story_outline_template.md → story_writing_template.md
- 適用例: ジェミニ記事アイデア、特定のトピック深掘り記事など

「**ブログ完全生成**」コマンドでユーザーの目的に応じた最適パターンを自動実行：

**重要な品質管理ポイント：**
- ✅ **H5タグ使用絶対禁止**: config/content_generation_template.yamlガイドライン厳守
- ✅ **全6章完全作成**: 第1章から第6章まですべて存在確認
- ✅ **アイキャッチ・章別画像必須**: 画像統合の完全実行
- ✅ **最終文字数20,000字以上**: 実際の文字数カウントで確認
- ✅ **まとめセクション必須**: 結論・CTA統合で完結

#### Phase 1: コンテンツ企画・設計
1. **検索意図分析**: `config/intent_analysis_template.yaml` で3語キーワードの複合的ニーズを分析
2. **意図分割**: `templates/division.md` で個別検索意図をINT-01, INT-02...に分割・JSON化
3. **アウトライン生成**: `config/outline_strategy_template.yaml` で記事構成・章立て作成

#### Phase 2: コンテンツ作成
4. **各章コンテンツ作成**: `config/content_generation_template.yaml` または `templates/story_writing_template.md` で章別内容執筆（第1章〜第6章）
5. **ファクトチェック実施**: 
   - WebSearchツールで統計データ・市場規模の最新性確認
   - WebFetchツールで公式ソース・専門機関データの検証
   - 技術仕様の正確性をメーカー公式サイトで確認
   - ファクトチェックレポート作成（factcheck_report_worker*.md）
   - 検出された問題点の修正と信頼性向上
6. **見出し構造検証**: 各章の見出し階層とH5禁止ルールの確認
7. **リード文生成**: `templates/lead.md` で導入部分作成
8. **まとめ生成**: `templates/summary.md` で結論・CTA作成
9. **完全記事統合**: 全セクションを統合した完全版記事作成
10. **最終構造検証**: 統合記事の見出し構造最終チェック

#### Phase 3: 画像生成・公開
11. **アイキャッチ画像生成**: OpenAI gpt-image-1で日本語テキスト付き画像作成（自動最適化）
12. **章別サムネイル生成**: Google Imagen 3で各章のサムネイル画像作成（6章分）
13. **WordPress投稿**: 画像アップロード＋記事投稿（章別画像自動挿入）

### 個別実行の場合

#### Phase 1: 企画・設計段階
- **キーワード分析**: `config/intent_analysis_template.yaml` で3語キーワードの検索意図分析
- **意図分割**: `templates/division.md` で意図をINT-01, INT-02形式でJSON化
- **アウトライン作成**: `config/outline_strategy_template.yaml` で章立て・構成設計

#### Phase 2-3: 作成・公開段階
- **記事生成のみ**: `scripts/create_final_article.py` （章執筆〜統合、OutputManager対応）
- **画像生成のみ**: `scripts/image_generator.py` （アイキャッチ・サムネイル最適化）
- **投稿のみ**: `python scripts/post_blog_universal.py` （汎用WordPress投稿・完璧版）

## 便利な合言葉コマンド

### 「品質チェック」で包括的記事検証（NEW）
```bash
# Claude Codeで使用
品質チェック outputs/記事名-INT-01/complete_article.md

# または直接スクリプト実行
python scripts/pre_wordpress_quality_checker.py outputs/記事名-INT-01/complete_article.md

# WordPress投稿時に自動実行（post_blog_universal.pyに統合済み）
python scripts/post_blog_universal.py
```

**実行内容**:
- 見出し構造の包括的検証（H5/H6禁止・階層チェック）
- テンプレート識別子の自動検出・除去
- コンテンツ構造の整合性確認
- SEO要素の最適化検証
- WordPress変換の事前確認
- 自動修正の実行（必要に応じて）
- 詳細品質レポートの生成
- 投稿可否の最終判定

### 「記事検証」で見出し構造チェック（レガシー）
```bash
# Claude Codeで使用
記事検証 outputs/記事名-INT-01/complete_article.md

# または直接スクリプト実行
python scripts/validate_article.py outputs/記事名-INT-01/complete_article.md
```

**実行内容**:
- H5/H6タグ禁止ルールの確認
- テンプレート識別子（H3-1等）の残存チェック
- 見出し階層（H2→H3→H4）の構造確認  
- 具体的な修正方法の提示
- 投稿可否の判定表示

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

### 「リライト」でリライトメニュー表示
```bash
# Claude Codeで使用
リライト 記事ID
```

**実行内容**:
- 指定した記事IDのリライトメニューを表示
- 6つのリライトオプションから選択可能
- Claude Code主導の高品質リライト実行

> **📋 詳細ガイド**: リライト機能の詳細な手順と各オプションについては [config/rewrite_options.yaml](config/rewrite_options.yaml) を参照してください

### 「ブログ完全生成」でワンストップ作成
```bash
# Claude Codeで使用
[ブログタイトル] ブログ完全生成
```

**実行プロセス（11ステップ）**:

**Phase 1: 企画・設計**
1. **検索意図分析**: `config/intent_analysis_template.yaml` でキーワード複合ニーズ分析
2. **意図分割**: `templates/division.md` で個別意図をINT番号付きJSON化
3. **アウトライン生成**: `config/outline_strategy_template.yaml` で記事構成・章立て作成

**Phase 2: コンテンツ作成**
4. **各章執筆**: `config/content_generation_template.yaml` で第1章〜第6章作成
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

詳細は `utils/output_manager.py` を参照してください。

## 画像挿入仕様

- **対象見出し**: H2見出しで章番号付き（`第1章`, `第2章` など）
- **挿入位置**: 見出し直後に独立した画像ブロックとして挿入
- **画像順序**: chapter1, chapter2, ... の順番で章番号と自動対応
- **画像形式**: WordPress Gutenbergブロックエディタ形式（paragraphブロックに入れない）
- **修正済み**: `scripts/wordpress_client.py` の `insert_chapter_images` 関数で適切なブロック構造を生成

## テンプレート仕様

### config/outline_strategy_template.yaml (SEO・CTR最適化対応)
- **高CTRタイトル戦略**: 数字・感情トリガー・権威性・記号（【】｜）を組み合わせた魅力的なタイトル
- **検索意図別戦略**: How-to、比較、トラブル解決、情報収集タイプに応じた最適なタイトル形式
- **心理トリガー活用**: 緊急性・限定性・課題解決・具体的成果でクリック率向上
- **SEO要素最適化**: 32文字以内タイトル、120文字以内メタディスクリプション、キーワード含有スラッグ
- **競合差別化**: 独自切り口と権威性で検索結果での差別化を実現

### config/content_generation_template.yaml (SEO・エンゲージメント最適化対応)
- **キーワード最適化**: メインキーワード・関連キーワード・長尾キーワードの戦略的配置
- **検索結果対策**: 強調スニペット・アンサーボックス・音声検索対応の構造化
- **E-A-T強化**: 専門性・権威性・信頼性を高める統計データ・専門家コメント・出典明記
- **H5見出し完全禁止**: H5以下の見出し使用を禁止し、SEO効果の高い段落装飾（💡⚠️🎯🔍📊📋）で代替
- **見出し階層制限**: H2〜H4まで（3階層）に制限、キーワード最適化された見出し構造
- **エンゲージメント向上**: 冒頭フック・スキャン可能性・内部リンク戦略で滞在時間延長
- **章末まとめ禁止**: 各章の末尾にまとめセクションは作成しない
- **テンプレート識別子除去**: `H3-1`、`H3-2`などの識別子は実際の見出し名に変換

### templates/summary.md
- **見出しレベル**: `## まとめ` （H2タグでWordPress表示対応）
- **CTA更新**: SATO-AI塾とHTサポートワークスへの誘導リンク追加
- **行動促進**: 具体的なアクションプランと次のステップ提示

### templates/story_outline_template.md（NEW）
- **読み物重視**: テーマから直接魅力的なアウトライン作成
- **知的好奇心**: 新しい視点・考え方の提供重視
- **物語性**: エピソード・感情的共感を中心とした構成

### templates/story_writing_template.md（NEW）
- **ストーリー型執筆**: 物語性・エピソード中心の章執筆
- **感情的共感**: 人間的体験・感情移入を重視
- **実用的価値**: 生活・仕事に役立つ気づき提供

## WordPress投稿での注意事項

- **画像ブロック構造**: 章見出し下に独立した画像ブロックとして挿入
- **メタデータ除去**: Meta Description行とローカル画像パスは自動除去
- **ブロック形式**: マークダウンからWordPressブロックエディタ形式に自動変換
- **下書き投稿**: 記事は下書き状態で投稿される

## 📝 記事企画・執筆候補

検索意図を分析した記事執筆候補は `config/intent_variation_tracker.json` を参照してください。ターゲット読者・検索意図・差別化ポイント別に整理された記事候補が保管されています。

## 関連ドキュメント

- **[config/quality_check_rules.yaml](config/quality_check_rules.yaml)**: WordPress投稿前品質チェック・自動修正システム（AI最適化YAML形式）
- **[config/image_management_rules.yaml](config/image_management_rules.yaml)**: アイキャッチ画像自動生成・更新機能（統合版）
- **[config/rewrite_options.yaml](config/rewrite_options.yaml)**: 記事リライト機能
