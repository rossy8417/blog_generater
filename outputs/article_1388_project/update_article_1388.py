#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記事ID 1388更新スクリプト
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'scripts'))

from wordpress_update_client import WordPressUpdateClient

def main():
    try:
        # コンテンツファイル読み込み
        with open('codeediter_example.txt', 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📖 コンテンツファイル読み込み完了: {len(content)}文字")
        
        # WordPress更新クライアント初期化
        client = WordPressUpdateClient()
        print("✅ WordPressクライアント初期化完了")
        
        # 記事更新実行
        print("🚀 記事ID 1388 更新開始...")
        result = client.update_post(
            post_id=1388,
            content=content,
            backup=True,
            diff_update=True
        )
        
        if result.get('success'):
            print("🎉 記事更新が完了しました！")
            print(f"   投稿ID: {result.get('post_id')}")
            print(f"   更新時刻: {result.get('updated_at')}")
            if result.get('content_length'):
                print(f"   コンテンツ長: {result.get('content_length')}文字")
            if result.get('edit_link'):
                print(f"   編集リンク: {result.get('edit_link')}")
        else:
            print(f"❌ 記事更新に失敗しました: {result.get('message', 'Unknown error')}")
            return 1
            
    except FileNotFoundError:
        print("❌ codeediter_example.txt ファイルが見つかりません")
        return 1
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())