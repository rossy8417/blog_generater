#\!/usr/bin/env python3
"""
簡単なアイキャッチ更新スクリプト - 再現性重視
使用方法: python3 scripts/update_eyecatch_simple.py 記事ID
"""

import os
import sys
import base64
import requests
from datetime import datetime
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def update_eyecatch(post_id):
    """記事IDのアイキャッチ画像をgpt-image-1で更新"""
    
    # 設定
    openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    wordpress_api_key = os.getenv('WORDPRESS_API_KEY')
    wordpress_endpoint = os.getenv('WORDPRESS_ENDPOINT')
    
    headers = {
        'X-API-Key': wordpress_api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"🚀 記事ID {post_id} のアイキャッチ更新開始")
    
    # 1. 記事取得
    response = requests.get(f'{wordpress_endpoint}/get-post/{post_id}', headers=headers)
    if response.status_code \!= 200:
        print(f"❌ 記事取得失敗: {response.status_code}")
        return False
    
    post_data = response.json()
    title = post_data.get('title', '')
    print(f"📖 記事タイトル: {title}")
    
    # 2. 画像生成
    prompt = f'Modern professional digital illustration for blog article titled "{title}". Clean tech design with blue/purple gradient background. Japanese text "{title}" prominently displayed. High-quality contemporary style.'
    
    print("🎨 gpt-image-1で画像生成中...")
    try:
        img_response = openai_client.images.generate(
            model='gpt-image-1',
            prompt=prompt,
            size='1536x1024',
            quality='high',
            n=1
        )
        
        image_data = base64.b64decode(img_response.data[0].b64_json)
        print(f"✅ 画像生成成功: {len(image_data)} bytes")
    except Exception as e:
        print(f"❌ 画像生成失敗: {e}")
        return False
    
    # 3. ローカル保存
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'outputs/eyecatch_{post_id}_{timestamp}.png'
    
    with open(filename, 'wb') as f:
        f.write(image_data)
    print(f"💾 画像保存: {filename}")
    
    # 4. WordPress アップロード
    with open(filename, 'rb') as f:
        files = {'file': (os.path.basename(filename), f, 'image/png')}
        upload_headers = {'X-API-Key': wordpress_api_key}
        
        upload_response = requests.post(
            f'{wordpress_endpoint}/upload-image',
            headers=upload_headers,
            files=files,
            timeout=60
        )
        
        if upload_response.status_code == 200:
            result = upload_response.json()
            attachment_id = result.get('id')
            print(f"📤 アップロード成功: ID {attachment_id}")
        else:
            print(f"❌ アップロード失敗: {upload_response.text}")
            return False
    
    # 5. アイキャッチ更新
    update_data = {'featured_image_id': attachment_id}
    
    update_response = requests.post(
        f'{wordpress_endpoint}/update-post/{post_id}',
        headers=headers,
        json=update_data,
        timeout=30
    )
    
    if update_response.status_code == 200:
        print("🔄 アイキャッチ更新成功\!")
        
        # 6. 検証
        verify_response = requests.get(f'https://www.ht-sw.tech/wp-json/wp/v2/posts/{post_id}')
        if verify_response.status_code == 200:
            verify_data = verify_response.json()
            current_id = verify_data.get('featured_media', 0)
            
            if current_id == attachment_id:
                print(f"🎉 完了\! アイキャッチID: {current_id}")
                return True
            else:
                print(f"⚠️ 検証で不一致: 期待{attachment_id}, 実際{current_id}")
                return False
        else:
            print("❌ 検証API失敗")
            return False
    else:
        print(f"❌ 更新失敗: {update_response.text}")
        return False

if __name__ == '__main__':
    if len(sys.argv) \!= 2:
        print("使用方法: python3 scripts/update_eyecatch_simple.py 記事ID")
        sys.exit(1)
    
    try:
        post_id = int(sys.argv[1])
        success = update_eyecatch(post_id)
        sys.exit(0 if success else 1)
    except ValueError:
        print("❌ 記事IDは数値で指定してください")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)
EOF < /dev/null
