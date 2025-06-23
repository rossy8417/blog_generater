# WordPress記事更新機能開発プロジェクト - 技術分析報告書

## 作成者情報
- **担当者**: Worker1
- **作成日時**: 2025-06-22 15:33:00
- **プロジェクト**: WordPress記事更新機能開発

---

## 1. 既存API実装分析

### 1.1 現在のWordPressClientアーキテクチャ

#### 基本構成
```python
class WordPressClient:
    - __init__(): 認証情報とエンドポイント設定
    - create_post(): 新規記事作成（主要機能）
    - upload_image(): 画像アップロード
    - get_usage_stats(): API使用統計取得
    - test_connection(): 接続テスト
```

#### 認証方式
- **認証タイプ**: X-API-Key ヘッダーベース認証
- **環境変数**: WORDPRESS_API_KEY, WORDPRESS_ENDPOINT
- **セキュリティ**: HTTPSによる暗号化通信

#### 現在の機能範囲
- ✅ 記事作成（create-post エンドポイント）
- ✅ 画像アップロード（upload-image エンドポイント）
- ✅ 使用統計取得（usage エンドポイント）
- ❌ 記事更新（未実装）
- ❌ 記事削除（未実装）
- ❌ 記事一覧取得（未実装）

### 1.2 技術的特徴と制約

#### 優れた設計要素
1. **エラーハンドリング**: 包括的な例外処理とレスポンス検証
2. **WordPressブロック対応**: Gutenbergエディタ完全サポート
3. **マークダウン変換**: 高精度なmarkdown→WordPressブロック変換
4. **画像統合**: 章別画像自動挿入機能

#### 現在の制約
1. **CRUD制限**: Create操作のみ、Read/Update/Delete未対応
2. **カスタムAPI依存**: WordPress標準REST APIではなく独自プラグインAPI使用
3. **エンドポイント固定**: create-post, upload-image, usage の3つのみ

---

## 2. WordPress REST API記事更新エンドポイント調査

### 2.1 WordPress標準REST API仕様

#### 更新エンドポイント
```
PUT /wp-json/wp/v2/posts/{id}
POST /wp-json/wp/v2/posts/{id}
```

#### 必須パラメータ
- **URL Parameter**: `{id}` - 更新対象の投稿ID
- **HTTP Method**: PUT または POST
- **Content-Type**: application/json

#### 更新可能フィールド
```json
{
  "title": "記事タイトル",
  "content": "記事本文（HTML）",
  "excerpt": "記事抜粋",
  "status": "publish|draft|private",
  "featured_media": 123,
  "meta": {
    "custom_field": "value"
  }
}
```

#### 認証要求
- **Basic認証**: username:password（Application Password推奨）
- **Cookie認証**: WordPressセッション
- **OAuth**: WordPress.com OAuth（第三者アプリ向け）

### 2.2 レスポンス形式

#### 成功レスポンス（200 OK）
```json
{
  "id": 123,
  "date": "2025-06-22T15:33:00",
  "modified": "2025-06-22T15:33:00",
  "title": {
    "rendered": "更新された記事タイトル"
  },
  "content": {
    "rendered": "更新された記事本文"
  },
  "status": "publish",
  "link": "https://example.com/post-url"
}
```

#### エラーレスポンス
```json
{
  "code": "rest_post_invalid_id",
  "message": "投稿IDが無効です",
  "data": {"status": 404}
}
```

---

## 3. 投稿ID指定更新機能要件定義

### 3.1 機能要件

#### 基本機能
1. **投稿ID指定更新**: 既存記事の部分的または全体的更新
2. **フィールド選択更新**: title, content, excerpt, status等の個別更新
3. **画像更新対応**: featured_media（アイキャッチ）更新
4. **メタデータ更新**: カスタムフィールド更新対応

#### 高度機能
1. **バックアップ作成**: 更新前の自動バックアップ
2. **差分更新**: 変更箇所のみ更新（パフォーマンス最適化）
3. **バッチ更新**: 複数記事の一括更新
4. **更新確認**: 更新前の内容確認とプレビュー

### 3.2 技術要件

#### パフォーマンス要件
- **レスポンス時間**: 5秒以内（通常更新）
- **タイムアウト**: 30秒（大容量コンテンツ更新時）
- **同時実行**: 最大3記事の並行更新対応

#### セキュリティ要件
- **権限確認**: 更新権限の事前チェック
- **データ検証**: 入力データの妥当性検証
- **ログ記録**: 更新操作の監査ログ

#### 互換性要件
- **WordPress版**: 5.0以降（Gutenbergエディタ必須）
- **PHP版**: 7.4以降
- **プラグイン**: 既存カスタムプラグインとの互換性維持

---

## 4. 技術仕様とAPI設計案

### 4.1 新機能実装設計

#### update_post メソッド設計
```python
def update_post(self, 
               post_id: int,
               title: Optional[str] = None,
               content: Optional[str] = None,
               excerpt: Optional[str] = None,
               meta_description: Optional[str] = None,
               status: Optional[str] = None,
               featured_image_id: Optional[int] = None,
               backup: bool = True) -> Dict[str, Any]:
    """
    WordPress記事更新
    
    Args:
        post_id: 更新対象の投稿ID
        title: 新しいタイトル（Noneの場合は更新しない）
        content: 新しい本文（WordPressブロック形式）
        excerpt: 新しい抜粋
        meta_description: SEO用メタディスクリプション
        status: 投稿ステータス (draft, publish, private)
        featured_image_id: アイキャッチ画像ID
        backup: 更新前のバックアップ作成有無
    
    Returns:
        更新結果とメタデータ
    """
```

#### カスタムプラグインAPI拡張案

##### 新エンドポイント設計
```
PUT  /update-post/{id}     # 記事更新
POST /backup-post/{id}     # バックアップ作成
GET  /get-post/{id}        # 記事取得
GET  /list-posts           # 記事一覧取得
```

##### update-post エンドポイント仕様
```json
{
  "endpoint": "/update-post/{id}",
  "method": "PUT",
  "headers": {
    "Content-Type": "application/json",
    "X-API-Key": "your-api-key"
  },
  "body": {
    "title": "新しいタイトル",
    "content": "WordPressブロック形式の本文",
    "excerpt": "抜粋",
    "meta_description": "メタディスクリプション",
    "status": "publish",
    "featured_image_id": 123,
    "backup": true
  }
}
```

### 4.2 実装優先度とマイルストーン

#### Phase 1: 基本更新機能（1週間）
- ✅ 基本的なupdate_postメソッド実装
- ✅ タイトル・本文・ステータス更新対応
- ✅ エラーハンドリング強化

#### Phase 2: 高度機能（2週間）
- ✅ バックアップ機能実装
- ✅ 画像更新対応
- ✅ メタデータ更新対応

#### Phase 3: 最適化（1週間）
- ✅ 差分更新機能
- ✅ バッチ更新機能
- ✅ パフォーマンス最適化

### 4.3 実装コード案

#### 基本的なupdate_postメソッド
```python
def update_post(self, post_id: int, **kwargs) -> Dict[str, Any]:
    """WordPress記事更新実装"""
    
    # 1. 入力検証
    if not isinstance(post_id, int) or post_id <= 0:
        raise ValueError("有効な投稿IDを指定してください")
    
    # 2. バックアップ作成（オプション）
    if kwargs.get('backup', True):
        backup_result = self._create_backup(post_id)
        print(f"📋 バックアップ作成: {backup_result.get('backup_id')}")
    
    # 3. 更新データ構築
    update_data = {}
    if 'title' in kwargs and kwargs['title']:
        update_data['title'] = kwargs['title']
    if 'content' in kwargs and kwargs['content']:
        update_data['content'] = kwargs['content']
    if 'excerpt' in kwargs and kwargs['excerpt']:
        update_data['excerpt'] = kwargs['excerpt']
    if 'meta_description' in kwargs and kwargs['meta_description']:
        update_data['meta_description'] = kwargs['meta_description']
    if 'status' in kwargs and kwargs['status']:
        update_data['status'] = kwargs['status']
    if 'featured_image_id' in kwargs and kwargs['featured_image_id']:
        update_data['featured_image_id'] = kwargs['featured_image_id']
    
    # 4. API呼び出し
    try:
        print(f"✏️  記事更新中... (ID: {post_id})")
        response = requests.put(
            f"{self.endpoint}/update-post/{post_id}",
            headers=self.headers,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 記事更新成功!")
            print(f"   投稿ID: {result.get('post_id')}")
            print(f"   更新時刻: {result.get('modified_time')}")
            return result
        else:
            error_msg = f"更新エラー: {response.status_code} - {response.text}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
            
    except requests.exceptions.RequestException as e:
        error_msg = f"接続エラー: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)

def _create_backup(self, post_id: int) -> Dict[str, Any]:
    """記事のバックアップ作成"""
    response = requests.post(
        f"{self.endpoint}/backup-post/{post_id}",
        headers=self.headers,
        timeout=15
    )
    return response.json() if response.status_code == 200 else {}
```

#### 差分更新機能
```python
def update_post_diff(self, post_id: int, new_content: str) -> Dict[str, Any]:
    """差分ベースの効率的更新"""
    
    # 1. 現在の記事取得
    current_post = self.get_post(post_id)
    current_content = current_post.get('content', '')
    
    # 2. 差分計算
    diff_ratio = self._calculate_diff_ratio(current_content, new_content)
    
    # 3. 差分が小さい場合は部分更新、大きい場合は全体更新
    if diff_ratio < 0.3:  # 30%未満の変更
        return self._partial_update(post_id, current_content, new_content)
    else:
        return self.update_post(post_id, content=new_content)

def _calculate_diff_ratio(self, old_content: str, new_content: str) -> float:
    """変更率計算"""
    from difflib import SequenceMatcher
    return 1.0 - SequenceMatcher(None, old_content, new_content).ratio()
```

### 4.4 エラーハンドリング強化

#### カスタム例外クラス
```python
class WordPressUpdateError(Exception):
    """WordPress更新関連エラー"""
    pass

class PostNotFoundError(WordPressUpdateError):
    """記事が見つからない"""
    pass

class InsufficientPermissionError(WordPressUpdateError):
    """更新権限不足"""
    pass

class UpdateConflictError(WordPressUpdateError):
    """更新競合エラー"""
    pass
```

#### エラー処理の実装
```python
def update_post(self, post_id: int, **kwargs) -> Dict[str, Any]:
    try:
        # 更新処理
        pass
    except requests.exceptions.Timeout:
        raise WordPressUpdateError("更新処理がタイムアウトしました")
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            raise PostNotFoundError(f"投稿ID {post_id} が見つかりません")
        elif e.response.status_code == 403:
            raise InsufficientPermissionError("記事更新の権限がありません")
        elif e.response.status_code == 409:
            raise UpdateConflictError("他のユーザーが同時に編集中です")
        else:
            raise WordPressUpdateError(f"更新エラー: {e.response.status_code}")
```

---

## 5. 実装推奨アプローチ

### 5.1 段階的実装戦略

#### Step 1: 最小実行可能プロダクト（MVP）
- 基本的なupdate_postメソッドの実装
- title, content, statusの更新のみ
- 既存のcreate_postメソッドをベースに開発

#### Step 2: 機能拡張
- 画像更新機能追加
- メタデータ更新対応
- バックアップ機能実装

#### Step 3: 最適化とテスト
- パフォーマンス最適化
- 包括的テストスイート作成
- ドキュメント整備

### 5.2 テスト戦略

#### 単体テスト
```python
import unittest
from unittest.mock import patch, MagicMock

class TestWordPressUpdate(unittest.TestCase):
    def test_update_post_success(self):
        # 正常系テスト
        pass
    
    def test_update_post_invalid_id(self):
        # 異常系テスト：無効なID
        pass
    
    def test_update_post_permission_error(self):
        # 異常系テスト：権限エラー
        pass
```

#### 統合テスト
- 実際のWordPress環境での動作確認
- 各種エラーケースの検証
- パフォーマンステスト

---

## 6. 結論と次のステップ

### 6.1 技術的実現可能性
- ✅ **高い実現可能性**: 既存のWordPressClientアーキテクチャを活用可能
- ✅ **拡張性**: モジュラー設計により段階的な機能追加が容易
- ✅ **保守性**: 既存のコードスタイルと一貫性を保った実装が可能

### 6.2 開発工数見積もり
- **Phase 1（MVP）**: 3-5日
- **Phase 2（機能拡張）**: 5-7日
- **Phase 3（最適化）**: 3-5日
- **合計**: 約2-3週間

### 6.3 リスクと対策

#### 主要リスク
1. **カスタムプラグインAPI拡張**: サーバーサイドの開発が必要
2. **権限管理の複雑性**: WordPress権限システムとの統合
3. **データ整合性**: 更新操作の原子性確保

#### 対策案
1. **段階的実装**: 最小機能から開始し、段階的に拡張
2. **十分なテスト**: 包括的なテストスイートによる品質確保
3. **バックアップ機能**: 更新前の自動バックアップによるリスク軽減

### 6.4 推奨次のステップ
1. **Boss1との要件詳細化**: 具体的な更新シナリオの確認
2. **プロトタイプ開発**: 基本的なupdate_postメソッドの実装
3. **カスタムプラグイン拡張**: サーバーサイドAPIの拡張
4. **テスト環境構築**: 安全な開発・テスト環境の準備

---

**分析完了日時**: 2025-06-22 15:34:00  
**次回レビュー予定**: Boss1からのフィードバック後  
**ステータス**: 分析完了・実装準備完了