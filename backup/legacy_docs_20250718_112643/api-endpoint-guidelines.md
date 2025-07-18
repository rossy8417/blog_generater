# WordPress APIエンドポイント使用ガイドライン

## 🚨 ハードコードURL禁止

**絶対に使用禁止**:
- `https://www.ht-sw.tech` 等の直接URL指定
- 環境に依存する固定URLの記述

## ✅ 正しいエンドポイント構築方法

### 1. 環境変数の使用
```python
import os
from dotenv import load_dotenv

load_dotenv()
wordpress_endpoint = os.getenv('WORDPRESS_ENDPOINT')  # カスタムAPI用
```

### 2. 標準REST API使用時
```python
# .envのWORDPRESS_ENDPOINTからベースURLを取得
base_url = wordpress_endpoint.replace('/wp-json/blog-generator/v1', '')
standard_api_url = f'{base_url}/wp-json/wp/v2/posts/{post_id}'
```

### 3. カスタムAPI使用時
```python
# WORDPRESS_ENDPOINTをそのまま使用
custom_api_url = f'{wordpress_endpoint}/get-post/{post_id}'
```

## 📋 API使用パターン

### 記事取得（標準REST API）
```python
def get_post_standard_api(post_id):
    base_url = os.getenv('WORDPRESS_ENDPOINT').replace('/wp-json/blog-generator/v1', '')
    response = requests.get(f'{base_url}/wp-json/wp/v2/posts/{post_id}')
    return response.json()
```

### 記事更新（カスタムAPI）
```python
def update_post_custom_api(post_id, content):
    endpoint = os.getenv('WORDPRESS_ENDPOINT')
    headers = {'X-API-Key': os.getenv('WORDPRESS_API_KEY')}
    response = requests.post(f'{endpoint}/update-post/{post_id}', 
                           json={'content': content}, headers=headers)
    return response.json()
```

### 画像アップロード（カスタムAPI）
```python
def upload_image(image_path):
    endpoint = os.getenv('WORDPRESS_ENDPOINT')
    headers = {'X-API-Key': os.getenv('WORDPRESS_API_KEY')}
    with open(image_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f'{endpoint}/upload-image', 
                               files=files, headers=headers)
    return response.json()
```

## 🔍 検証・確認時のURL構築

### WordPress編集画面URL
```python
def get_edit_url(post_id):
    base_url = os.getenv('WORDPRESS_ENDPOINT').replace('/wp-json/blog-generator/v1', '')
    return f'{base_url}/wp-admin/post.php?post={post_id}&action=edit'
```

### フロントエンド表示URL
```python
def get_post_url(post_id):
    base_url = os.getenv('WORDPRESS_ENDPOINT').replace('/wp-json/blog-generator/v1', '')
    return f'{base_url}/?p={post_id}'
```

## ⚡ 修正が必要なファイル

以下のファイルでハードコードされたURLが検出されています：

1. **scripts/update_eyecatch_simple.py:104**
   ```python
   # 修正前（NG）
   verify_response = requests.get(f'https://www.ht-sw.tech/wp-json/wp/v2/posts/{post_id}')
   
   # 修正後（OK）
   base_url = os.getenv('WORDPRESS_ENDPOINT').replace('/wp-json/blog-generator/v1', '')
   verify_response = requests.get(f'{base_url}/wp-json/wp/v2/posts/{post_id}')
   ```

## 🎯 実装時のチェックリスト

- [ ] .envのWORDPRESS_ENDPOINTを使用
- [ ] 標準API時はbase_url変換を実行
- [ ] カスタムAPI時はWORDPRESS_ENDPOINTを直接使用
- [ ] ハードコードされたURL（www.ht-sw.tech等）なし
- [ ] 環境変数のNullチェック実装
- [ ] 適切なエラーハンドリング実装

この構造により、開発環境・本番環境・テスト環境で同じコードが動作します。