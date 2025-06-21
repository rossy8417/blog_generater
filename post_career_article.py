#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
エンジニアキャリアチェンジ戦略記事をWordPressに投稿するスクリプト
"""

import os
import sys
from wordpress_client import WordPressClient, convert_markdown_to_gutenberg, insert_chapter_images

def post_career_change_article():
    """キャリアチェンジ戦略記事をWordPressに投稿"""
    
    print("🚀 エンジニアキャリアチェンジ戦略記事の投稿を開始します...\n")
    
    try:
        # WordPress クライアント初期化
        print("📡 WordPressクライアント初期化中...")
        client = WordPressClient()
        
        # 接続テスト
        print("🔗 WordPress接続テスト中...")
        if not client.test_connection():
            print("❌ WordPress接続に失敗しました。設定を確認してください。")
            return False
        
        # 記事ファイル読み込み
        article_path = "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_complete_article_career_change.md"
        
        print(f"📖 記事ファイル読み込み中: {article_path}")
        
        if not os.path.exists(article_path):
            print(f"❌ 記事ファイルが見つかりません: {article_path}")
            return False
            
        with open(article_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"✅ 記事読み込み完了 ({len(markdown_content):,} 文字)")
        
        # 画像アップロード
        print("\n📤 章別画像をアップロード中...")
        
        # アップロードする画像リスト
        images_to_upload = [
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_eyecatch_INT-02.png",
                "alt": "エンジニアキャリアチェンジ戦略 - アイキャッチ画像",
                "type": "eyecatch"
            },
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_thumbnail_INT-02_chapter1.png",
                "alt": "第1章: キャリア変化の必要性",
                "type": "chapter",
                "chapter": "chapter1"
            },
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_thumbnail_INT-02_chapter2.png",
                "alt": "第2章: 現状分析と目標設定",
                "type": "chapter", 
                "chapter": "chapter2"
            },
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_thumbnail_INT-02_chapter3.png",
                "alt": "第3章: 最新技術トレンド",
                "type": "chapter",
                "chapter": "chapter3"
            },
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_thumbnail_INT-02_chapter4.png",
                "alt": "第4章: スキルアップロードマップ",
                "type": "chapter",
                "chapter": "chapter4"
            },
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_thumbnail_INT-02_chapter5.png",
                "alt": "第5章: 効果的な学習方法",
                "type": "chapter",
                "chapter": "chapter5"
            },
            {
                "path": "/mnt/c/home/hiroshi/blog_generator/outputs/20250621_012641_thumbnail_INT-02_chapter6.png",
                "alt": "第6章: 成功・失敗事例",
                "type": "chapter",
                "chapter": "chapter6"
            }
        ]
        
        uploaded_images = []
        eyecatch_image_id = None
        
        for image_info in images_to_upload:
            print(f"   📤 {os.path.basename(image_info['path'])} をアップロード中...")
            
            result = client.upload_image(image_info['path'], image_info['alt'])
            
            if result:
                uploaded_images.append({
                    'chapter': image_info.get('chapter', ''),
                    'attachment_id': result['attachment_id'],
                    'url': result['url'],
                    'type': image_info['type']
                })
                
                if image_info['type'] == 'eyecatch':
                    eyecatch_image_id = result['attachment_id']
                    print(f"   ✅ アイキャッチ画像アップロード完了 (ID: {eyecatch_image_id})")
                else:
                    print(f"   ✅ {image_info['chapter']} アップロード完了 (ID: {result['attachment_id']})")
            else:
                print(f"   ❌ {os.path.basename(image_info['path'])} のアップロードに失敗")
        
        # マークダウンをWordPress形式に変換
        print("\n🔄 マークダウンをWordPress形式に変換中...")
        
        # アイキャッチ画像の記法を削除（WordPress側で設定するため）
        markdown_content = markdown_content.replace('![エンジニアキャリアチェンジ戦略](./20250621_012641_eyecatch_INT-02.png)', '')
        
        # 章別画像の記法も削除（後で挿入するため）
        for i in range(1, 7):
            markdown_content = markdown_content.replace(f'![{["キャリア変化の必要性", "現状分析と目標設定", "最新技術トレンド", "スキルアップロードマップ", "変化に強い学習方法", "成功・失敗事例"][i-1]}](./20250621_012641_thumbnail_INT-02_chapter{i}.png)', '')
        
        wp_content = convert_markdown_to_gutenberg(markdown_content)
        
        # 章別画像を挿入
        chapter_images = [img for img in uploaded_images if img['type'] == 'chapter']
        if chapter_images:
            print("🖼️  章別画像を記事に挿入中...")
            wp_content = insert_chapter_images(wp_content, chapter_images)
            print(f"   ✅ {len(chapter_images)}個の章別画像を挿入完了")
        
        print(f"✅ 変換完了 ({len(wp_content):,} 文字のWordPressブロック)")
        
        # 記事投稿
        print("\n📝 WordPressに記事投稿中...")
        
        title = "エンジニアのキャリアチェンジ戦略｜変化への対応とスキルアップ"
        meta_description = "激変するIT業界で生き残るための実践的キャリア戦略！トレンド適応、スキルアップロードマップ、成功・失敗事例でキャリアチェンジを成功させよう。"
        excerpt = "エンジニアとしてのキャリアに不安を感じていませんか？適切な戦略と計画的な準備により、キャリアチェンジ成功率は70%を超え、年収も20-30%向上可能です。現状分析から最新技術トレンド、実践的な学習方法まで、成功のための6つの戦略を詳しく解説します。"
        
        result = client.create_post(
            title=title,
            content=wp_content,
            excerpt=excerpt,
            meta_description=meta_description,
            status="draft",  # 下書きとして作成
            featured_image_id=eyecatch_image_id
        )
        
        if result:
            print(f"\n🎉 記事投稿完了!")
            print(f"📝 投稿ID: {result.get('post_id')}")
            print(f"🔗 編集URL: {result.get('edit_url')}")
            print(f"📊 ステータス: 下書き")
            print(f"🖼️  アイキャッチ画像: 設定済み")
            print(f"📷 章別画像: {len(chapter_images)}個挿入済み")
            
            # 使用統計表示
            try:
                usage = client.get_usage_stats()
                print(f"\n📈 API使用状況:")
                print(f"   今日の投稿数: {usage.get('today_count', 0)}")
                print(f"   総投稿数: {usage.get('total_count', 0)}")
            except:
                pass
            
            return True
        else:
            print("❌ 記事投稿に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = post_career_change_article()
    if success:
        print("\n✅ 処理が正常に完了しました！")
        sys.exit(0)
    else:
        print("\n❌ 処理が失敗しました。")
        sys.exit(1)