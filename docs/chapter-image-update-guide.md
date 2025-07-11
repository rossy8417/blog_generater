# 章別画像更新ガイド

## 📊 章別画像更新機能概要

WordPress記事の各章（第1章〜第6章）に挿入されているサムネイル画像を、Imagen 3を使用して個別または一括で更新する機能です。

## 🎯 章別画像更新の特徴

### 🔍 コンテキスト認識更新
- **章内容分析**: 各章の内容とテーマを自動解析
- **最適化画像生成**: 章の内容に最も適した画像をImagen 3で生成
- **一貫性維持**: 記事全体で統一されたビジュアルスタイル

### ⚡ 効率的な更新システム
- **個別更新**: 特定の章のみピンポイント更新
- **一括更新**: 全6章の画像を一度に更新
- **範囲指定更新**: 第3-5章など範囲を指定して更新

### 🛡️ 安全性とバックアップ
- **自動バックアップ**: 更新前の画像を自動保存
- **バージョン管理**: 画像更新履歴の完全追跡
- **復元機能**: 任意のバージョンへの簡単復元

## 🚀 基本的な使用方法

### 1. 個別章画像更新
```bash
# 第3章の画像のみ更新
python3 -c "
import sys
sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()

result = engine.smart_replace_image(
    post_id=記事ID,
    target_type='chapter_3',
    replacement_strategy='regenerate'
)
print('✅ 第3章画像更新完了' if result['success'] else '❌ 更新失敗')
"
```

### 2. 複数章一括更新
```bash
# 第1-3章の画像を一括更新
python3 -c "
import sys
sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()

chapters = ['chapter_1', 'chapter_2', 'chapter_3']
updates = [
    {
        'post_id': 記事ID,
        'target_type': chapter,
        'replacement_strategy': 'regenerate'
    }
    for chapter in chapters
]

results = engine.batch_update_images(updates)
print(f'✅ 一括更新完了: {len([r for r in results if r[\"success\"]])}/{len(updates)} 件成功')
"
```

### 3. 全章画像一新
```bash
# 第1-6章すべての画像を更新
python3 -c "
import sys
sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()

all_chapters = [f'chapter_{i}' for i in range(1, 7)]
updates = [
    {
        'post_id': 記事ID,
        'target_type': chapter,
        'replacement_strategy': 'regenerate'
    }
    for chapter in all_chapters
]

results = engine.batch_update_images(updates)
success_count = len([r for r in results if r['success']])
print(f'🎉 全章画像更新完了: {success_count}/6 章成功')
"
```

## 📋 章別画像更新の詳細フロー

### Step 1: 記事内容分析
1. **章構成解析**: H2見出しによる章分けの自動認識
2. **内容抽出**: 各章のテキスト内容とキーワード抽出
3. **テーマ分析**: 章ごとの主要テーマと目的の特定

### Step 2: 画像生成戦略決定
1. **スタイル統一**: 記事全体の一貫したビジュアルスタイル設定
2. **章別最適化**: 各章内容に特化したプロンプト生成
3. **品質基準**: 800KB以下、高品質維持の最適化設定

### Step 3: Imagen 3による画像生成
1. **コンテキスト生成**: 章内容を反映したプロンプト作成
2. **高品質画像生成**: Imagen 3による専門的画像作成
3. **自動最適化**: ファイルサイズとクオリティの最適バランス

### Step 4: WordPress統合
1. **メディアライブラリアップロード**: 生成画像の自動アップロード
2. **章別画像差し替え**: 既存画像から新画像への自動置換
3. **検証**: 更新結果の自動確認

## 🎨 章別画像の品質基準

### 画像仕様
- **サイズ**: 800KB以下に自動最適化
- **形式**: JPG（WordPress最適化）
- **解像度**: 高品質維持（1200x800推奨）
- **スタイル**: 記事テーマに統一されたデザイン

### 内容品質
- **関連性**: 章内容との高い関連性
- **プロフェッショナル**: ビジネス・技術記事に適した品質
- **視覚的魅力**: 読者の注意を引く魅力的なデザイン
- **SEO対応**: alt属性とファイル名の最適化

## 🔧 高度な機能

### バージョン管理機能
```bash
# 画像更新履歴の確認
python3 -c "
import sys
sys.path.append('scripts')
from image_update_manager import ImageVersionManager
manager = ImageVersionManager()

history = manager.get_image_history(記事ID, 'chapter_3')
for version in history[-3:]:  # 最新3バージョン表示
    print(f'バージョン: {version[\"version_id\"]}')
    print(f'作成日時: {version[\"created_at\"]}')
    print(f'ファイルサイズ: {version[\"file_size\"]} bytes')
    print('---')
"
```

### 画像復元機能
```bash
# 特定バージョンへの復元
python3 -c "
import sys
sys.path.append('scripts')
from image_update_manager import ImageVersionManager
manager = ImageVersionManager()

# バージョンIDを指定して復元
result = manager.restore_image_version('バージョンID')
if result:
    print('✅ 画像復元完了')
else:
    print('❌ 復元失敗')
"
```

### 画像分析機能
```bash
# 画像互換性分析
python3 -c "
import sys
sys.path.append('scripts')
from image_update_manager import ImageAnalyzer
analyzer = ImageAnalyzer()

# 新旧画像の互換性チェック
with open('old_image.jpg', 'rb') as f1, open('new_image.jpg', 'rb') as f2:
    compatibility = analyzer.analyze_image_compatibility(f1.read(), f2.read())
    print(f'互換性スコア: {compatibility[\"compatibility_score\"]}')
    print(f'推奨更新: {\"Yes\" if compatibility[\"recommend_update\"] else \"No\"}')
"
```

## ⚠️ 注意事項とベストプラクティス

### 更新前の確認事項
1. **記事ID確認**: 正しい記事IDを指定
2. **章構成確認**: H2見出しによる章分けが適切か確認
3. **バックアップ確認**: 自動バックアップ機能の動作確認

### 効率的な更新のコツ
1. **段階的更新**: 1-2章ずつ更新して結果確認
2. **品質チェック**: 生成画像の内容適合性確認
3. **一貫性維持**: 記事全体のビジュアル統一性確保

### トラブルシューティング
- **生成失敗**: プロンプトの調整で再試行
- **アップロード失敗**: ネットワーク状況確認後再実行
- **サイズオーバー**: 自動最適化機能で解決（通常自動対応）

## 🎯 使用例とケーススタディ

### 例1: 技術記事の章別画像刷新
```bash
# AI関連技術記事（記事ID: 1234）の全章画像を最新トレンドに更新
記事ID: 1234
対象: 全6章
戦略: regenerate（AI最新トレンド反映）
結果: 6/6章成功、視覚的統一性大幅向上
```

### 例2: 特定章のみ画像改善
```bash
# ビジネス記事の第4章「導入事例」画像のみ更新
記事ID: 5678
対象: 第4章のみ
戦略: 実際の導入事例イメージに最適化
結果: エンゲージメント率 25% 向上
```

### 例3: 古い記事の画像モダン化
```bash
# 2年前の記事の画像を現代的なデザインに更新
記事ID: 9012
対象: 第1-3章（特に古い印象の章）
戦略: モダンなビジネスイメージに刷新
結果: 視覚的魅力度とプロフェッショナル感が大幅向上
```

## 📊 更新効果の測定

### 品質指標
- **視覚的統一性**: 記事全体の一貫したデザイン
- **内容関連性**: 章内容との適合度
- **プロフェッショナル度**: ビジネス記事としての品質

### パフォーマンス指標
- **ファイルサイズ**: 800KB以下達成率
- **生成成功率**: 画像生成の成功/失敗比率
- **更新速度**: 章あたりの更新時間

## 🔗 関連ガイド

- **[アイキャッチ画像更新ガイド](eyecatch-update-guide.md)**: アイキャッチ画像の更新方法
- **[統合画像更新ガイド](image-update-integration-guide.md)**: アイキャッチ+章別画像の統合更新
- **[記事リライトガイド](rewrite-guide.md)**: 記事内容と合わせた総合的な記事改善

## 💡 よくある質問（FAQ）

**Q: 章別画像更新に必要な環境変数は？**
A: `GOOGLE_API_KEY`（Imagen 3用）と`WORDPRESS_API_KEY`が必要です。

**Q: 更新に失敗した場合の対処法は？**
A: 自動バックアップから復元し、プロンプトを調整して再実行してください。

**Q: 6章未満の記事でも使用できますか？**
A: はい。存在する章のみ自動認識して更新します。

**Q: 更新画像の品質はどの程度ですか？**
A: Imagen 3による高品質生成で、800KB以下に最適化されたプロフェッショナルレベルです。

**Q: 一度に何章まで更新できますか？**
A: 技術的制限はありませんが、API制限とパフォーマンスを考慮し、3-4章ずつの更新を推奨します。