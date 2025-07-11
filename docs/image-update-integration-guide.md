# 統合画像更新ガイド

## 🎨 WordPress記事画像更新システム総合案内

WordPress記事の画像を効率的に更新するための統合メニューガイドです。アイキャッチ画像、章別画像、または両方を選択して更新できます。

## 🎯 画像更新オプション一覧

### 📸 1. アイキャッチ画像のみ更新
記事のメインビジュアルとなるアイキャッチ画像をgpt-image-1で更新

**適用場面**:
- 記事タイトルに合った新しいアイキャッチが欲しい
- SNS拡散用の魅力的な画像に変更したい
- ブランディングに合わせた統一感のある画像に更新したい

**使用方法**:
```bash
python3 scripts/update_eyecatch_simple.py 記事ID
```

### 📊 2. 章別画像のみ更新
記事内の各章（第1章〜第6章）のサムネイル画像をImagen 3で更新

**適用場面**:
- 章の内容により適した画像に変更したい
- 古い章画像を現代的なデザインに刷新したい
- 特定の章の視覚的インパクトを向上させたい

**使用方法**:
```bash
# 個別章更新（例：第3章）
python3 -c "
import sys; sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()
result = engine.smart_replace_image(記事ID, 'chapter_3', 'regenerate')
print('✅ 更新完了' if result['success'] else '❌ 更新失敗')
"
```

### 🎉 3. 完全画像リニューアル（アイキャッチ + 全章）
記事のすべての画像を一新してビジュアル面を完全刷新

**適用場面**:
- 記事全体のイメージを一新したい
- 古い記事を現代的なビジュアルに完全アップデート
- ブランドリニューアルに合わせた画像統一

### 🔧 4. カスタム選択更新
アイキャッチ + 指定した章のみの柔軟な組み合わせ更新

**適用場面**:
- アイキャッチと特定の章のみ更新したい
- 予算やAPI使用量を考慮した部分更新
- 段階的な画像改善を実施したい

## 🚀 統合更新メニューの使用方法

### Step 1: 更新方針の決定
以下の質問で最適なオプションを選択：

1. **アイキャッチを更新したいですか？** Yes/No
2. **章別画像を更新したいですか？** Yes/No  
3. **更新したい章番号は？** (章別画像更新の場合)

### Step 2: 選択パターン別実行

#### パターンA: アイキャッチのみ
```bash
echo "🎨 アイキャッチ画像更新開始"
python3 scripts/update_eyecatch_simple.py 記事ID
echo "✅ アイキャッチ更新完了"
```

#### パターンB: 章別画像のみ（全章）
```bash
echo "📊 全章画像更新開始"
python3 -c "
import sys; sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()

updates = [{'post_id': 記事ID, 'target_type': f'chapter_{i}', 'replacement_strategy': 'regenerate'} for i in range(1, 7)]
results = engine.batch_update_images(updates)
success = len([r for r in results if r['success']])
print(f'✅ 章別画像更新完了: {success}/6 章成功')
"
```

#### パターンC: 完全画像リニューアル
```bash
echo "🎉 完全画像リニューアル開始"

# Step 1: アイキャッチ更新
echo "📸 アイキャッチ画像更新中..."
python3 scripts/update_eyecatch_simple.py 記事ID

# Step 2: 全章画像更新
echo "📊 全章画像更新中..."
python3 -c "
import sys; sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()

updates = [{'post_id': 記事ID, 'target_type': f'chapter_{i}', 'replacement_strategy': 'regenerate'} for i in range(1, 7)]
results = engine.batch_update_images(updates)
success = len([r for r in results if r['success']])
print(f'📊 章別画像更新: {success}/6 章成功')
"

echo "🎉 完全画像リニューアル完了"
```

#### パターンD: カスタム選択（例：アイキャッチ + 第1,3,5章）
```bash
echo "🔧 カスタム画像更新開始"

# アイキャッチ更新
echo "📸 アイキャッチ更新中..."
python3 scripts/update_eyecatch_simple.py 記事ID

# 指定章更新
echo "📊 指定章画像更新中..."
python3 -c "
import sys; sys.path.append('scripts')
from image_update_manager import ImageUpdateEngine
engine = ImageUpdateEngine()

# 第1,3,5章のみ更新
target_chapters = ['chapter_1', 'chapter_3', 'chapter_5']
updates = [{'post_id': 記事ID, 'target_type': ch, 'replacement_strategy': 'regenerate'} for ch in target_chapters]
results = engine.batch_update_images(updates)
success = len([r for r in results if r['success']])
print(f'📊 カスタム章更新: {success}/{len(target_chapters)} 章成功')
"

echo "🔧 カスタム更新完了"
```

## 📋 更新前のチェックリスト

### 事前確認事項
- [ ] 記事IDの正確性確認
- [ ] 必要なAPI キー設定（OPENAI_API_KEY, GOOGLE_API_KEY, WORDPRESS_API_KEY）
- [ ] 記事の章構成確認（H2見出し）
- [ ] 更新対象画像の現状確認

### 更新戦略の決定
- [ ] 予算とAPI使用量の考慮
- [ ] 更新優先度の明確化（アイキャッチ優先 vs 章別優先）
- [ ] 段階的更新 vs 一括更新の選択
- [ ] バックアップ戦略の確認

## 🎨 画像品質と最適化

### アイキャッチ画像仕様
- **生成エンジン**: gpt-image-1
- **特徴**: 日本語テキスト入り、高品質
- **最適化**: 500KB以下に自動調整
- **スタイル**: モダンプロフェッショナル

### 章別画像仕様  
- **生成エンジン**: Imagen 3
- **特徴**: 章内容に最適化、統一スタイル
- **最適化**: 800KB以下に自動調整
- **品質**: 高解像度、ビジネス適合

## 🛡️ 安全性とバックアップ

### 自動バックアップ機能
- **アイキャッチ**: 更新前画像の自動保存
- **章別画像**: バージョン管理による履歴保存
- **復元機能**: ワンクリックでの元画像復元

### エラー処理
- **更新失敗時**: 自動リトライ機能
- **部分失敗時**: 成功した部分は保持、失敗部分のみ再試行
- **完全失敗時**: バックアップからの自動復元オプション

## 📊 更新効果の測定

### 即座に確認できる指標
- **ファイルサイズ**: 最適化効果
- **視覚的インパクト**: 更新前後の比較
- **生成成功率**: API呼び出し成功率

### 中長期的指標
- **SEO効果**: 画像最適化によるページ速度向上
- **エンゲージメント**: 視覚的魅力向上による滞在時間
- **ソーシャルシェア**: アイキャッチ更新による拡散効果

## 🔗 詳細ガイドへのリンク

### 専門ガイド
- **[アイキャッチ画像更新ガイド](eyecatch-update-guide.md)**: アイキャッチ更新の詳細手順
- **[章別画像更新ガイド](chapter-image-update-guide.md)**: 章別画像更新の完全マニュアル

### システムガイド
- **[記事更新システムガイド](article-update-system-guide.md)**: 記事更新全般の手順
- **[記事リライトガイド](rewrite-guide.md)**: 記事内容と画像の統合的な改善

## 💡 画像更新のベストプラクティス

### 効率的な更新順序
1. **アイキャッチ優先**: 最も目立つ画像から更新
2. **重要章優先**: 記事の核となる章から更新  
3. **段階的実施**: 一度に全部ではなく段階的に更新
4. **効果確認**: 各段階で更新効果を確認

### 品質保証のコツ
- **プレビュー確認**: 更新前に生成画像をプレビュー
- **スタイル統一**: 記事全体の一貫性維持
- **読者視点**: 読者にとって価値ある画像かチェック
- **モバイル対応**: スマートフォンでの表示確認

## ⚠️ よくある質問とトラブルシューティング

### Q: どの更新オプションを選ぶべきですか？
**A**: 以下を参考に選択してください：
- **記事のリブランディング** → 完全画像リニューアル
- **アイキャッチの魅力向上** → アイキャッチのみ更新
- **特定章の改善** → 章別画像のみ更新
- **予算制約がある** → カスタム選択更新

### Q: 更新に失敗した場合は？
**A**: 以下の順序で対処：
1. ネットワーク接続確認
2. APIキー設定確認  
3. バックアップからの復元
4. 再実行

### Q: 更新頻度の推奨は？
**A**: 記事タイプによって異なります：
- **技術記事**: 3-6ヶ月ごと（トレンド反映）
- **ビジネス記事**: 6-12ヶ月ごと（安定性重視）
- **トレンド記事**: 1-3ヶ月ごと（鮮度重視）

### Q: API使用量の節約方法は？
**A**: 以下の方法が効果的：
- カスタム選択更新で必要最小限に限定
- 段階的更新で効果確認しながら実施
- 重要度の高い記事から優先的に更新

この統合ガイドにより、WordPress記事の画像を戦略的かつ効率的に更新できます。