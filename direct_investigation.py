#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接403エラー調査 - President0指示対応
"""

import os
import requests
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

def execute_investigation():
    """直接調査実行"""
    
    print("🔍 【Boss1】403エラー直接調査")
    
    # 環境変数取得
    api_key = os.getenv('WORDPRESS_API_KEY')
    endpoint = os.getenv('WORDPRESS_ENDPOINT')
    
    print(f"📡 エンドポイント: {endpoint}")
    print(f"🔑 APIキー: {api_key[:20] if api_key else 'None'}...")
    
    if not api_key or not endpoint:
        print("❌ API設定不完全")
        return
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    
    # 調査1: 記事取得（正常動作確認）
    print("\n🔍 調査1: 記事取得テスト")
    try:
        response = requests.get(
            f"{endpoint}/get-post/3105",
            headers=headers,
            timeout=15
        )
        print(f"   記事取得: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 記事タイトル: {data.get('title', 'Unknown')[:50]}...")
            print(f"   ✅ 記事ID: {data.get('id', 'Unknown')}")
        else:
            print(f"   ❌ エラー: {response.text[:200]}")
    except Exception as e:
        print(f"   ❌ 接続エラー: {e}")
    
    # 調査2: 更新エンドポイントテスト
    print("\n🔍 調査2: 更新エンドポイント詳細テスト")
    
    test_data = {'content': 'test', 'timestamp': '2025-06-26'}
    
    # 複数エンドポイント・メソッドテスト
    test_configs = [
        ('PUT', f"{endpoint}/update-post/3105"),
        ('POST', f"{endpoint}/update-post/3105"),
        ('PATCH', f"{endpoint}/update-post/3105"),
        ('PUT', f"{endpoint}/post/3105"),
        ('POST', f"{endpoint}/post/3105"),
    ]
    
    for method, url in test_configs:
        try:
            print(f"   テスト: {method} {url}")
            
            if method == 'PUT':
                response = requests.put(url, headers=headers, json=test_data, timeout=10)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=test_data, timeout=10)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=test_data, timeout=10)
            
            print(f"     結果: {response.status_code}")
            
            if response.status_code == 403:
                print(f"     403詳細: {response.text[:100]}...")
            elif response.status_code in [200, 201]:
                print(f"     ✅ 成功可能性: {method} {url}")
            else:
                print(f"     その他: {response.status_code} - {response.text[:50]}...")
                
        except Exception as e:
            print(f"     ❌ エラー: {e}")
    
    # 調査3: ヘッダー変更テスト
    print("\n🔍 調査3: 認証ヘッダー変更テスト")
    
    header_tests = [
        {'Content-Type': 'application/json', 'X-API-Key': api_key},
        {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
        {'Content-Type': 'application/json', 'X-WordPress-Nonce': api_key},
        {'X-API-Key': api_key},  # Content-Type無し
    ]
    
    for i, test_headers in enumerate(header_tests, 1):
        try:
            print(f"   ヘッダーパターン{i}: {list(test_headers.keys())}")
            response = requests.put(
                f"{endpoint}/update-post/3105",
                headers=test_headers,
                json=test_data,
                timeout=10
            )
            print(f"     結果: {response.status_code}")
            if response.status_code != 403:
                print(f"     ✅ 有効ヘッダー: パターン{i}")
        except Exception as e:
            print(f"     ❌ エラー: {e}")
    
    # 調査4: OPTIONS・HEAD確認
    print("\n🔍 調査4: サーバー応答・許可メソッド確認")
    try:
        # OPTIONS
        response = requests.options(f"{endpoint}/update-post/3105", headers=headers, timeout=10)
        print(f"   OPTIONS: {response.status_code}")
        print(f"   許可メソッド: {response.headers.get('Allow', 'N/A')}")
        
        # HEAD
        response = requests.head(f"{endpoint}/update-post/3105", headers=headers, timeout=10)
        print(f"   HEAD: {response.status_code}")
        
        # 403時の詳細ヘッダー
        response = requests.put(f"{endpoint}/update-post/3105", headers=headers, json=test_data, timeout=10)
        print(f"   403レスポンス詳細:")
        print(f"     Server: {response.headers.get('Server', 'N/A')}")
        print(f"     X-Powered-By: {response.headers.get('X-Powered-By', 'N/A')}")
        print(f"     WWW-Authenticate: {response.headers.get('WWW-Authenticate', 'N/A')}")
        
    except Exception as e:
        print(f"   ❌ サーバー情報エラー: {e}")
    
    print("\n📋 調査完了")
    print("=" * 50)

if __name__ == "__main__":
    execute_investigation()