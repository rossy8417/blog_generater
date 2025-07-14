# OutputManager完全準拠ルール

## 🎯 ファイル管理統一基準

### 必須遵守事項

#### 1. 出力先統一
- **全ファイル出力**: `outputs/[タイトル-INT-XX]/`構造必須
- **tmp/使用制限**: 一時作業のみ、最終成果物禁止
- **散乱ファイル禁止**: root直下への出力完全禁止

#### 2. ディレクトリ構造標準
```
outputs/
└── [記事タイトル-INT-01]/
    ├── complete_article.md      # 最終統合記事
    ├── eyecatch.jpg            # アイキャッチ画像
    ├── chapter1.jpg            # 第1章画像
    ├── chapter2.jpg            # 第2章画像
    ├── chapter3.jpg            # 第3章画像
    ├── chapter4.jpg            # 第4章画像
    ├── chapter5.jpg            # 第5章画像
    ├── chapter6.jpg            # 第6章画像
    ├── metadata.json           # 記事メタデータ
    ├── outline_content.md      # アウトライン（任意）
    ├── lead_content.md         # リード文（任意）
    └── summary_content.md      # まとめ（任意）
```

#### 3. ファイル命名規則
- **記事ファイル**: `complete_article.md`（固定）
- **画像ファイル**: `eyecatch.jpg`, `chapter1.jpg`〜`chapter6.jpg`（固定）
- **メタデータ**: `metadata.json`（固定）
- **プレフィックス禁止**: `boss1_`, `worker1_`等のプレフィックス使用禁止

#### 4. 各Agent責任範囲

##### Boss1
- Phase1: `outputs/[タイトル-INT-XX]/`ディレクトリ作成
- Phase2: 統合作業時の正しい出力先確保
- Phase3: WordPress投稿前の構造確認

##### Worker1-3
- Phase2: 章別ファイルを正しい`outputs/`構造に保存
- Phase3: 画像ファイルを正しいファイル名で保存
- 完了時: `ls outputs/[プロジェクト名]/`で必ず確認実行

#### 5. WordPress投稿連携
- `scripts/post_blog_universal.py`は`outputs/`の最新ディレクトリを自動検出
- 正しい構造の記事のみを投稿対象とする
- 投稿後の`outputs/latest_post_info.txt`更新確認

#### 6. 品質確認プロセス
```bash
# 各プロジェクト完了時の必須確認
ls -la outputs/[タイトル-INT-XX]/
# 必要ファイルの存在確認
# - complete_article.md: ✅
# - eyecatch.jpg: ✅  
# - chapter1-6.jpg: ✅（6個）
# - metadata.json: ✅（推奨）
```

#### 7. 緊急時対応
tmp/に散乱したファイルがある場合：
```bash
# 正しい構造に移動
mkdir -p "outputs/[正しいタイトル-INT-XX]/"
cp tmp/boss1_* outputs/[正しいタイトル-INT-XX]/
# ファイル名標準化
cd outputs/[正しいタイトル-INT-XX]/
mv boss1_complete_article.md complete_article.md
mv boss1_eyecatch.jpg eyecatch.jpg
mv boss1_chapter*.jpg chapter*.jpg
```

## 🔄 今後の運用

### 新規プロジェクト開始時
1. Boss1がキーワード分析後、即座に`outputs/[タイトル-INT-XX]/`作成
2. 全Worker に正しい出力先を明示指示
3. Phase完了時に構造確認実行

### 継続的改善
- 各プロジェクトでの遵守状況記録
- 違反発生時の即座修正
- システム改善提案の継続実施

**このルールの完全遵守により、ファイル管理の混乱を防止し、WordPress投稿の確実性を保証します。**