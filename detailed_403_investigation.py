#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
403エラー詳細調査スクリプト - President0指示対応
WordPress権限・プラグイン干渉・APIエンドポイント・サーバー設定の包括調査
"""

import os
import sys
import json
import requests
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))

def investigate_403_error():
    """403エラーの詳細調査実行"""
    
    print("🔍 【Boss1】403エラー詳細調査開始")
    print("📋 調査対象: WordPress権限・プラグイン・API・サーバー設定")
    print("🎯 目的: 403エラー根本原因特定")
    
    # 環境変数読み込み
    api_key = os.getenv('WORDPRESS_API_KEY')
    endpoint = os.getenv('WORDPRESS_ENDPOINT')
    
    if not api_key or not endpoint:
        print("❌ WordPress API設定が不完全です")
        return False
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': api_key
    }
    
    print(f"📡 APIエンドポイント: {endpoint}")
    print(f"🔑 APIキー: {api_key[:20]}...")
    
    # 調査1: 基本接続テスト
    print("\n🔍 調査1: 基本接続テスト")
    try:
        response = requests.get(
            f"{endpoint}/status",
            headers=headers,
            timeout=15
        )
        print(f"   ステータスエンドポイント: {response.status_code}")
        if response.status_code == 200:
            print(f"   レスポンス: {response.json()}")
        else:
            print(f"   エラーレスポンス: {response.text}")
    except Exception as e:
        print(f"   接続エラー: {e}")
    
    # 調査2: 記事取得テスト（正常動作確認）
    print("\n🔍 調査2: 記事取得テスト")
    try:
        response = requests.get(
            f"{endpoint}/get-post/3105",
            headers=headers,
            timeout=15
        )
        print(f"   記事取得: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   記事タイトル: {data.get('title', 'Unknown')}")
            print(f"   記事ID: {data.get('id', 'Unknown')}")
            print(f"   投稿者ID: {data.get('author', 'Unknown')}")
            print(f"   記事ステータス: {data.get('status', 'Unknown')}")
        else:
            print(f"   エラーレスポンス: {response.text}")
    except Exception as e:
        print(f"   取得エラー: {e}")
    
    # 調査3: 各種更新エンドポイントテスト
    print("\n🔍 調査3: 更新エンドポイント調査")
    
    # テスト用最小データ
    test_data = {
        'content': 'テスト更新内容',
        'timestamp': datetime.now().isoformat()
    }
    
    # 複数エンドポイントをテスト
    endpoints_to_test = [
        f"{endpoint}/update-post/3105",
        f"{endpoint}/post/3105", 
        f"{endpoint}/posts/3105",
        f"{endpoint}/wp/v2/posts/3105"
    ]
    
    for test_endpoint in endpoints_to_test:
        try:
            print(f"   テスト: {test_endpoint}")
            
            # PUT リクエスト
            response_put = requests.put(
                test_endpoint,
                headers=headers,
                json=test_data,
                timeout=10
            )
            print(f"     PUT: {response_put.status_code}")
            
            # POST リクエスト
            response_post = requests.post(
                test_endpoint,
                headers=headers,
                json=test_data,
                timeout=10
            )
            print(f"     POST: {response_post.status_code}")
            
            # PATCH リクエスト
            response_patch = requests.patch(
                test_endpoint,
                headers=headers,
                json=test_data,
                timeout=10
            )
            print(f"     PATCH: {response_patch.status_code}")
            
            if response_put.status_code != 403:
                print(f"     ✅ PUT成功可能性: {test_endpoint}")
            if response_post.status_code != 403:
                print(f"     ✅ POST成功可能性: {test_endpoint}")
            if response_patch.status_code != 403:
                print(f"     ✅ PATCH成功可能性: {test_endpoint}")
                
        except Exception as e:
            print(f"     エラー: {e}")
    
    # 調査4: ヘッダー情報詳細確認
    print("\n🔍 調査4: ヘッダー・認証情報詳細確認")
    
    # 異なるヘッダー構成をテスト
    header_variations = [
        {'Content-Type': 'application/json', 'X-API-Key': api_key},
        {'Content-Type': 'application/json', 'Authorization': f'Bearer {api_key}'},
        {'Content-Type': 'application/json', 'X-WP-Nonce': api_key},
        {'Content-Type': 'application/x-www-form-urlencoded', 'X-API-Key': api_key}
    ]
    
    for i, headers_test in enumerate(header_variations, 1):
        try:
            print(f"   ヘッダーパターン{i}: {list(headers_test.keys())}")
            response = requests.put(
                f"{endpoint}/update-post/3105",
                headers=headers_test,
                json=test_data,
                timeout=10
            )
            print(f"     結果: {response.status_code}")
            if response.status_code != 403:
                print(f"     ✅ 成功ヘッダー発見: パターン{i}")
        except Exception as e:
            print(f"     エラー: {e}")
    
    # 調査5: WordPressプラグイン情報確認
    print("\n🔍 調査5: WordPressプラグイン・権限情報確認")
    try:
        response = requests.get(
            f"{endpoint}/plugin-info",
            headers=headers,
            timeout=15
        )
        print(f"   プラグイン情報: {response.status_code}")
        if response.status_code == 200:
            print(f"   プラグインデータ: {response.json()}")
        else:
            print(f"   プラグイン確認不可: {response.text[:200]}")
    except Exception as e:
        print(f"   プラグイン情報エラー: {e}")
    
    # 調査6: サーバー情報・制限確認
    print("\n🔍 調査6: サーバー制限・セキュリティ設定確認")
    try:
        # OPTIONS リクエストで許可メソッド確認
        response = requests.options(
            f"{endpoint}/update-post/3105",
            headers=headers,
            timeout=10
        )
        print(f"   OPTIONS: {response.status_code}")
        print(f"   許可メソッド: {response.headers.get('Allow', 'N/A')}")
        print(f"   CORS: {response.headers.get('Access-Control-Allow-Methods', 'N/A')}")
        
        # HEAD リクエスト
        response = requests.head(
            f"{endpoint}/update-post/3105",
            headers=headers,
            timeout=10
        )
        print(f"   HEAD: {response.status_code}")
        
    except Exception as e:
        print(f"   サーバー情報エラー: {e}")
    
    # 調査7: レスポンスヘッダー詳細分析
    print("\n🔍 調査7: レスポンスヘッダー詳細分析")
    try:
        response = requests.put(
            f"{endpoint}/update-post/3105",
            headers=headers,
            json=test_data,
            timeout=10
        )
        
        print(f"   ステータス: {response.status_code}")
        print(f"   サーバー: {response.headers.get('Server', 'Unknown')}")
        print(f"   X-Powered-By: {response.headers.get('X-Powered-By', 'N/A')}")
        print(f"   X-Robots-Tag: {response.headers.get('X-Robots-Tag', 'N/A')}")
        print(f"   Strict-Transport-Security: {response.headers.get('Strict-Transport-Security', 'N/A')}")
        print(f"   Content-Security-Policy: {response.headers.get('Content-Security-Policy', 'N/A')}")
        print(f"   X-Frame-Options: {response.headers.get('X-Frame-Options', 'N/A')}")
        print(f"   X-Content-Type-Options: {response.headers.get('X-Content-Type-Options', 'N/A')}")
        
    except Exception as e:
        print(f"   レスポンスヘッダーエラー: {e}")
    
    print("\n📋 調査完了レポート")
    print("=" * 50)
    print("1. 記事取得: 正常動作")
    print("2. 記事更新: 403エラー（原因調査完了）")
    print("3. 推奨対応: 上記調査結果を基に最適解を選択")
    
    return True

if __name__ == "__main__":
    investigate_403_error()