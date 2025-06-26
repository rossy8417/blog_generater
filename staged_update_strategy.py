#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress分割更新戦略実行スクリプト - President0指示対応
記事ID 3105の57,231字リライトを3段階Update APIで実行
"""

import os
import sys
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.wordpress_update_client import WordPressUpdateClient
from scripts.wordpress_client import convert_markdown_to_gutenberg

def execute_staged_update_strategy():
    """3段階WordPress分割更新戦略の実行"""
    
    print("🚀 【Boss1】WordPress分割更新戦略実行開始")
    print("📋 対象: 記事ID 3105 - 57,231字リライト")
    print("🎯 戦略: 3段階Update API・既存記事ID保持")
    
    # WordPress更新クライアント初期化
    try:
        client = WordPressUpdateClient(integration_mode=True)
        print("✅ WordPress更新クライアント初期化完了")
    except Exception as e:
        print(f"❌ クライアント初期化エラー: {e}")
        return False
    
    # リライトコンテンツ読み込み
    rewrite_files = {
        'lead': '/mnt/c/home/hiroshi/blog_generator/outputs/【2025年最新】生成AI資料作成最前線｜完全ガイド-INT-01/rewrite_lead.md',
        'worker1_ch1': '/mnt/c/home/hiroshi/blog_generator/tmp/worker_outputs/worker1_chapter1_rewrite.md',
        'worker1_ch2': '/mnt/c/home/hiroshi/blog_generator/tmp/worker_outputs/worker1_chapter2_rewrite.md',
        'summary': '/mnt/c/home/hiroshi/blog_generator/outputs/【2025年最新】生成AI資料作成最前線｜完全ガイド-INT-01/rewrite_summary.md'
    }
    
    print("📖 リライトコンテンツ統合中...")
    
    # 段階1: リード文+第1-2章（Worker1）更新
    stage1_content = ""
    try:
        with open(rewrite_files['lead'], 'r', encoding='utf-8') as f:
            stage1_content += f.read() + "\n\n"
        
        with open(rewrite_files['worker1_ch1'], 'r', encoding='utf-8') as f:
            stage1_content += f.read() + "\n\n"
            
        with open(rewrite_files['worker1_ch2'], 'r', encoding='utf-8') as f:
            stage1_content += f.read() + "\n\n"
            
        print(f"✅ 段階1コンテンツ準備完了: {len(stage1_content)}文字")
    except Exception as e:
        print(f"❌ 段階1コンテンツ読み込みエラー: {e}")
        return False
    
    # 段階1実行: 基本構造+第1-2章
    print("\n🔄 段階1実行: リード文+第1-2章更新")
    try:
        # マークダウンをWordPress形式に変換
        wp_content = convert_markdown_to_gutenberg(stage1_content)
        
        # 記事ID 3105を更新
        result1 = client.update_post(
            post_id=3105,
            title="【2025年最新】生成AI資料作成最前線｜802.8億円市場の完全攻略法",
            content=wp_content,
            meta_description="2028年802.8億円規模の生成AI市場で資料作成効率を284%向上させる科学的手法。ChatGPT vs Claude中立比較とROI387-584%実証事例を完全解説。",
            status="draft",
            backup=True
        )
        
        print(f"✅ 段階1更新完了: 投稿ID {result1['post_id']}")
        print(f"📊 更新内容: {len(stage1_content)}文字")
        
    except Exception as e:
        print(f"❌ 段階1更新エラー: {e}")
        return False
    
    print("\n🎉 WordPress分割更新戦略 段階1完了")
    print("📋 次段階: Worker2-3コンテンツ統合準備")
    print("💾 既存記事ID 3105保持完了")
    
    return True

if __name__ == "__main__":
    success = execute_staged_update_strategy()
    if success:
        print("\n✅ 分割更新戦略実行成功")
        sys.exit(0)
    else:
        print("\n❌ 分割更新戦略実行失敗")
        sys.exit(1)