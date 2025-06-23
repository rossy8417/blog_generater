# 非推奨スクリプト保管庫

## 📂 概要

開発時に使用されたが、本番運用では不要になったスクリプトを保管しています。

## 📋 保管されているスクリプト

### organize_outputs.py
- **用途**: ファイル自動整理スクリプト
- **状態**: 手動整理完了により不要
- **理由**: ファイル管理ルール策定により、自動整理の必要性が低下

### test_update_system.py  
- **用途**: WordPress記事更新システム統合テスト
- **状態**: 開発・検証用
- **理由**: 本番運用では実際のAPIテストで十分

## 🔄 復活条件

以下の場合には scripts/ ディレクトリに復活させる価値があります：

### organize_outputs.py
- 大量のファイル散乱が再発生した場合
- 自動整理システムが必要になった場合

### test_update_system.py
- 大規模なシステム変更前の回帰テストが必要な場合
- 新機能追加時の統合テストが必要な場合

## ⚠️ 注意事項

これらのスクリプトは削除ではなく保管しているため、必要時には即座に利用可能です。

## 📈 本番scripts/ディレクトリ

クリーンアップ後の scripts/ ディレクトリには以下の核心機能のみが残っています：

- **記事管理系**: article_update_manager.py, wordpress_update_client.py, wordpress_client.py
- **画像管理系**: image_generator.py, image_update_manager.py, update_eyecatch_simple.py  
- **コンテンツ系**: post_blog_universal.py, multi_intent_extractor.py