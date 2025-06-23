# アイキャッチ画像自動更新ガイド

## 🚀 既存記事のアイキャッチ画像更新

記事タイトルからgpt-image-1で日本語テキスト入りアイキャッチ画像を生成し、既存WordPress記事に自動更新する機能を追加しました。

### 使用方法

```bash
# 記事ID 1388のアイキャッチ画像を更新（バックアップ付き）
python3 scripts/update_eyecatch_from_title.py 1388

# バックアップなしで更新
python3 scripts/update_eyecatch_from_title.py 1388 --no-backup
```

### 自動処理フロー

1. **記事情報取得**: WordPress APIから記事タイトルを取得
2. **画像生成**: gpt-image-1で日本語テキスト入りアイキャッチを生成
3. **ローカル保存**: outputs/ディレクトリに画像を保存
4. **WordPress アップロード**: 画像をWordPress メディアライブラリにアップロード
5. **アイキャッチ更新**: 記事のアイキャッチ画像を新しい画像に更新
6. **検証**: WordPress標準APIで更新結果を確認

### 特徴

- **🎯 完全自動化**: 記事IDを指定するだけで全自動処理
- **🎨 gpt-image-1**: 日本語テキスト対応の高品質アイキャッチ生成
- **🛡️ バックアップ**: 更新前の記事データ自動バックアップ
- **✅ 検証機能**: WordPress標準APIでの更新結果確認
- **🔧 エラーハンドリング**: 詳細なエラー情報とステップ表示

### WordPress API認証について

このスクリプトでは2つの認証方式を使い分けています：

- **画像アップロード**: `X-API-Key` ヘッダー
- **記事取得/更新**: `X-API-Key` ヘッダー（統一）

### 実行例

```bash
$ python3 scripts/update_eyecatch_from_title.py 1388

🚀 記事ID 1388 のアイキャッチ画像更新開始
============================================================
📖 記事情報取得中...
✅ 記事タイトル取得: ChatGPT完全攻略｜プロンプトマスターガイド
   現在のアイキャッチ: 3089

🎨 gpt-image-1でアイキャッチ画像生成...
🎨 gpt-image-1でアイキャッチ生成中...
   タイトル: ChatGPT完全攻略｜プロンプトマスターガイド
   プロンプト: Modern professional digital illustration for blog article titled...
✅ 画像生成成功: 2548612 bytes

💾 画像をローカルに保存...
💾 画像保存完了: outputs/eyecatch_gpt1_ChatGPT完全攻略プロンプトマスターガイド_20250623_101456.png

📤 WordPressに画像アップロード...
📤 WordPress画像アップロード中: eyecatch_gpt1_ChatGPT完全攻略プロンプトマスターガイド_20250623_101456.png
   レスポンスコード: 200
✅ アップロード成功!
   画像ID: 3090
   URL: https://www.ht-sw.tech/wp-content/uploads/2025/06/eyecatch_gpt1_ChatGPT完全攻略プロンプトマスターガイド_20250623_101456.png

🔄 アイキャッチ画像更新...
🔄 記事1388のアイキャッチ画像更新中...
   レスポンスコード: 200
✅ アイキャッチ画像更新成功!
   編集リンク: https://www.ht-sw.tech/wp-admin/post.php?action=edit&post=1388

🔍 更新結果検証...
🔍 更新結果検証中...
✅ 検証成功: アイキャッチ画像ID 3090

============================================================
🎉 アイキャッチ画像更新が完全に成功しました！
   記事ID: 1388
   新しいアイキャッチID: 3090
   生成画像: outputs/eyecatch_gpt1_ChatGPT完全攻略プロンプトマスターガイド_20250623_101456.png
```

## WordPress記事更新機能

詳細は[README.md](../README.md)の「WordPress記事更新機能」セクションを参照してください。

### 必要な環境変数

```bash
# .envファイル
OPENAI_API_KEY=your_openai_api_key
WORDPRESS_API_KEY=your_wordpress_plugin_api_key  
WORDPRESS_ENDPOINT=https://your-site.com/wp-json/blog-generator/v1
```