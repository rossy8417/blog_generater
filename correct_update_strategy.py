#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
正しいWordPress更新戦略 - President0指示対応
post/{post_id}エンドポイントで記事ID 3105を更新
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

from scripts.wordpress_client import convert_markdown_to_gutenberg

def execute_correct_update():
    """正しいpost/{post_id}エンドポイントで記事ID 3105を更新"""
    
    print("🚀 【Boss1】正しいWordPress更新実行")
    print("📋 対象: 記事ID 3105")
    print("🎯 エンドポイント: post/3105")
    
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
    
    # リライトコンテンツ統合
    print("📖 Worker1-3リライトコンテンツ統合中...")
    
    try:
        # リード文読み込み
        with open('/mnt/c/home/hiroshi/blog_generator/outputs/【2025年最新】生成AI資料作成最前線｜完全ガイド-INT-01/rewrite_lead.md', 'r', encoding='utf-8') as f:
            lead_content = f.read()
        
        # Worker1第1章読み込み
        with open('/mnt/c/home/hiroshi/blog_generator/tmp/worker_outputs/worker1_chapter1_rewrite.md', 'r', encoding='utf-8') as f:
            chapter1_content = f.read()
        
        # Worker1第2章読み込み
        with open('/mnt/c/home/hiroshi/blog_generator/tmp/worker_outputs/worker1_chapter2_rewrite.md', 'r', encoding='utf-8') as f:
            chapter2_content = f.read()
        
        # まとめ読み込み
        with open('/mnt/c/home/hiroshi/blog_generator/outputs/【2025年最新】生成AI資料作成最前線｜完全ガイド-INT-01/rewrite_summary.md', 'r', encoding='utf-8') as f:
            summary_content = f.read()
        
        # 統合コンテンツ作成
        full_content = f"""# リード文（導入部）

{lead_content}

{chapter1_content}

{chapter2_content}

[NOTE: Worker2とWorker3のコンテンツは段階2で統合予定]

{summary_content}
"""
        
        print(f"✅ コンテンツ統合完了: {len(full_content)}文字")
        
        # マークダウンをWordPress形式に変換
        wp_content = convert_markdown_to_gutenberg(full_content)
        
        # 更新データ構築
        update_data = {
            'title': '【2025年最新】生成AI資料作成最前線｜802.8億円市場の完全攻略法',
            'content': wp_content,
            'meta_description': '2028年802.8億円規模の生成AI市場で資料作成効率を284%向上させる科学的手法。ChatGPT vs Claude中立比較とROI387-584%実証事例を完全解説。',
            'status': 'draft',
            'excerpt': '生成AI資料作成の革新的手法を57,000字で完全解説。市場動向から実践法まで、ROI387-584%達成の実証データを提供。',
            'timestamp': datetime.now().isoformat()
        }
        
        # 記事ID 3105を正しいエンドポイントで更新
        print("🔄 記事ID 3105更新実行中...")
        
        response = requests.post(
            f"{endpoint}/post/3105",
            headers=headers,
            json=update_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 記事更新成功!")
            print(f"   投稿ID: {result.get('post_id', 3105)}")
            print(f"   編集URL: {result.get('edit_link', 'N/A')}")
            print(f"   文字数: {len(full_content)}")
            return True
        else:
            print(f"❌ 更新エラー: {response.status_code}")
            print(f"   レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 実行エラー: {e}")
        return False

if __name__ == "__main__":
    success = execute_correct_update()
    if success:
        print("\n✅ 正しい更新戦略実行成功")
        sys.exit(0)
    else:
        print("\n❌ 更新戦略実行失敗")
        sys.exit(1)