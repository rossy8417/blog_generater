#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終的な記事構造を作成：リード文→本文→まとめ＋画像配置
"""

import os
import glob
from wordpress_client import WordPressClient, convert_markdown_to_gutenberg, create_image_block

def create_final_article_structure():
    """正しい記事構造で最終版を作成"""
    
    # 記事メタデータ
    title = "生成AI教育とは？子供の学習に革命をもたらす基礎知識完全ガイド"
    
    # リード文作成
    lead_text = """**「子供の教育に生成AIを取り入れるべきか迷っている」「安全性や効果が心配」「何から始めたらいいかわからない」** そんな保護者の皆様のお悩みにお答えします。

生成AI教育は、従来の一方向的な教育から個別最適化された対話型学習への革命的な転換を実現します。世界各国で既に目覚ましい成果を上げており、日本でも政府が580億円の大規模予算で本格推進中です。

本記事では、生成AI教育の基本概念から年齢別の活用法、科学的検証されたメリット・デメリット、そして実践的な導入チェックリストまで、保護者が知っておくべき情報を完全網羅。お子様の未来を左右する教育革新について、専門家の視点で分かりやすく解説します。"""

    # 動的にファイルを検索
    
    # 最新の章ファイルを取得
    chapter_pattern = '/mnt/c/home/hiroshi/blog_generator/outputs/*_article_*_chapter*.md'
    chapter_files = sorted(glob.glob(chapter_pattern))
    
    # 最新のサムネイル画像ファイルを取得
    thumbnail_pattern = '/mnt/c/home/hiroshi/blog_generator/outputs/*_thumbnail_*_chapter*.png'
    thumbnail_files = sorted(glob.glob(thumbnail_pattern))
    
    main_content = ""
    for i, chapter_file in enumerate(chapter_files):
        if os.path.exists(chapter_file):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_content = f.read().strip()
            
            # 章間の改行
            if i > 0:
                main_content += "\n\n"
            
            # 章のH1タイトルの後にサムネイル画像を挿入
            lines = chapter_content.split('\n')
            modified_chapter = ""
            
            for j, line in enumerate(lines):
                modified_chapter += line + '\n'
                
                # H1タイトルの直後にサムネイル画像を挿入
                if line.startswith('# ') and i < len(thumbnail_files):
                    thumbnail_file = thumbnail_files[i]
                    if os.path.exists(thumbnail_file):
                        modified_chapter += f"\n![第{i+1}章のサムネイル画像](thumbnail_chapter{i+1}_url)\n"
            
            main_content += modified_chapter.rstrip()
    
    # まとめセクション読み込み（動的検索）
    summary_pattern = '/mnt/c/home/hiroshi/blog_generator/outputs/*_article_summary.md'
    summary_files = glob.glob(summary_pattern)
    summary_content = ""
    if summary_files:
        summary_file = sorted(summary_files)[-1]  # 最新のサマリーファイル
        with open(summary_file, 'r', encoding='utf-8') as f:
            summary_content = f.read().strip()
    
    # 完全版記事構築
    complete_article = f"""{lead_text}

{main_content}

{summary_content}"""

    # 画像配置版記事構築（WordPressブロック用）
    article_with_images = f"""{lead_text}

<!-- アイキャッチ画像 -->
![生成AI教育の基本概念を表すイメージ](eyecatch_image_url)

{main_content}

<!-- まとめセクション前の画像 -->
![まとめと実践ガイドのイメージ](summary_image_url)

{summary_content}"""
    
    # ファイル保存
    final_file = '/mnt/c/home/hiroshi/blog_generator/outputs/20250620_181500_article_INT-01_final_structure.md'
    with open(final_file, 'w', encoding='utf-8') as f:
        f.write(complete_article)
    
    # 画像付き版も保存
    final_with_images_file = '/mnt/c/home/hiroshi/blog_generator/outputs/20250620_181500_article_INT-01_with_images.md'
    with open(final_with_images_file, 'w', encoding='utf-8') as f:
        f.write(article_with_images)
    
    print(f"✅ 最終構造記事を作成しました:")
    print(f"   📄 基本版: {final_file}")
    print(f"   🖼️ 画像付き版: {final_with_images_file}")
    print(f"   📊 総文字数: {len(complete_article):,} 文字")
    print(f"   📁 章ファイル数: {len(chapter_files)}")
    print(f"   🖼️ サムネイル数: {len(thumbnail_files)}")
    
    # 構造確認
    lines = complete_article.split('\n')
    h1_count = 0
    for line_num, line in enumerate(lines, 1):
        if line.startswith('# '):
            h1_count += 1
            print(f"   H1 #{h1_count} (行{line_num}): {line}")
    
    return final_file, final_with_images_file

def upload_to_wordpress():
    """WordPressに最終記事をアップロード"""
    try:
        # WordPressクライアント初期化
        client = WordPressClient()
        
        if not client.test_connection():
            print("❌ WordPress接続に失敗しました")
            return
        
        # 最終構造記事読み込み（動的検索）
        final_pattern = '/mnt/c/home/hiroshi/blog_generator/outputs/*_article_*_final_structure.md'
        final_files = glob.glob(final_pattern)
        if not final_files:
            print("❌ 最終構造記事ファイルが見つかりません")
            return None
            
        final_file = sorted(final_files)[-1]  # 最新のファイル
        with open(final_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # 記事メタデータ
        title = "生成AI教育とは？子供の学習に革命をもたらす基礎知識完全ガイド"
        meta_description = "生成AI教育の基本概念から子供への影響まで専門家が解説。保護者必見の教育革新ガイド"
        excerpt = "生成AI教育の基本概念、年齢別活用法、科学的検証、実践チェックリストまで完全網羅。保護者必見の教育革新ガイド。"
        
        # 画像アップロードとURL置換（動的検索）
        
        # アイキャッチ画像
        eyecatch_pattern = '/mnt/c/home/hiroshi/blog_generator/outputs/*_eyecatch_*.png'
        eyecatch_files = glob.glob(eyecatch_pattern)
        eyecatch_url = ""
        eyecatch_id = None
        if eyecatch_files:
            eyecatch_path = sorted(eyecatch_files)[-1]  # 最新のアイキャッチ
            eyecatch_result = client.upload_image(eyecatch_path, "生成AI教育アイキャッチ画像")
            if eyecatch_result:
                eyecatch_url = eyecatch_result['url']
                eyecatch_id = eyecatch_result.get('attachment_id')
        
        # 各章のサムネイル画像アップロード（動的検索）
        thumbnail_data = {}
        thumbnail_pattern = '/mnt/c/home/hiroshi/blog_generator/outputs/*_thumbnail_*_chapter*.png'
        thumbnail_files = sorted(glob.glob(thumbnail_pattern))
        
        for i, thumb_path in enumerate(thumbnail_files):
            if os.path.exists(thumb_path):
                thumb_result = client.upload_image(thumb_path, f"第{i+1}章サムネイル画像")
                if thumb_result:
                    placeholder = f"thumbnail_chapter{i+1}_url"
                    thumbnail_data[placeholder] = {
                        'url': thumb_result['url'],
                        'id': thumb_result.get('attachment_id', 0),
                        'alt': f"第{i+1}章サムネイル画像"
                    }
        
        # マークダウン画像記法を実際のURLに置換
        for i, (placeholder, data) in enumerate(thumbnail_data.items(), 1):
            # プレースホルダーを実際のURLに置換
            markdown_pattern = f"![第{i}章のサムネイル画像]({placeholder})"
            markdown_replacement = f"![第{i}章のサムネイル画像]({data['url']})"
            markdown_content = markdown_content.replace(markdown_pattern, markdown_replacement)
            print(f"🔄 URL置換: {placeholder} → {data['url']}")
        
        # WordPressブロック形式に変換（画像URL置換後）
        wordpress_content = convert_markdown_to_gutenberg(markdown_content)
        
        # アイキャッチ画像は featured_image_id として設定されるため、記事内への挿入は不要
        
        # WordPress投稿
        print(f"📝 最終記事投稿開始...")
        print(f"   構成: リード文→本文→まとめ")
        print(f"   画像: {1 + len(thumbnail_data)}枚追加（アイキャッチ + 各章サムネイル）")
        print(f"   文字数: {len(markdown_content):,} 文字")
        
        result = client.create_post(
            title=title,
            content=wordpress_content,
            excerpt=excerpt,
            featured_image_id=eyecatch_id,
            meta_description=meta_description,
            status="draft"
        )
        
        print(f"\n🎉 最終記事投稿完了!")
        print(f"   投稿ID: {result.get('post_id')}")
        print(f"   編集URL: {result.get('edit_url')}")
        print(f"   プレビューURL: {result.get('preview_url')}")
        
        return result
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return None

if __name__ == "__main__":
    # 最終構造作成
    final_file, final_with_images_file = create_final_article_structure()
    
    print("\n" + "="*50)
    
    # WordPress投稿
    result = upload_to_wordpress()