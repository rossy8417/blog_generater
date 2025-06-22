#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終的な記事構造を作成：リード文→本文→まとめ＋画像配置
完全動的版 - ハードコード部分を除去し、OutputManager使用
"""

import os
import glob
import re
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
import sys
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from wordpress_client import WordPressClient, convert_markdown_to_gutenberg, create_image_block
from utils.output_manager import OutputManager

def create_final_article_structure():
    """正しい記事構造で最終版を作成（完全動的版）"""
    
    # OutputManagerを初期化
    output_manager = OutputManager()
    
    # 動的にファイルを検索
    outputs_dir = output_manager.base_outputs_dir
    
    # 最新の章ファイルを取得（新構造対応）
    chapter_pattern = os.path.join(outputs_dir, '*/*_article_*_chapter*.md')
    chapter_files = sorted(glob.glob(chapter_pattern))
    if not chapter_files:
        # 旧構造もチェック
        chapter_pattern = os.path.join(outputs_dir, '*_article_*_chapter*.md')
        chapter_files = sorted(glob.glob(chapter_pattern))
    
    # リード文ファイルを動的検索
    lead_pattern = os.path.join(outputs_dir, '*/*_lead_*.md')
    lead_files = glob.glob(lead_pattern)
    if not lead_files:
        lead_pattern = os.path.join(outputs_dir, '*_lead_*.md')
        lead_files = glob.glob(lead_pattern)
    
    # デフォルト値を設定
    title = "生成AI教育ガイド"
    lead_text = "AI教育の基本概念について解説します。"
    
    # 最新のリード文ファイルから内容を取得
    if lead_files:
        latest_lead_file = sorted(lead_files)[-1]
        try:
            with open(latest_lead_file, 'r', encoding='utf-8') as f:
                lead_content = f.read().strip()
                # タイトルを抽出
                title_match = re.search(r'^# (.+)$', lead_content, re.MULTILINE)
                if title_match:
                    title = title_match.group(1).strip()
                # リード文を抽出（最初のH1の後の内容）
                lead_parts = lead_content.split('\n', 1)
                if len(lead_parts) > 1:
                    lead_text = lead_parts[1].strip()
        except Exception as e:
            print(f"Warning: Failed to load lead file: {e}")
    
    # 章ファイルからメタデータを抽出
    metadata = {'title': title, 'date': '', 'int_number': 'INT-01', 'timestamp': ''}
    if chapter_files:
        # 最初の章ファイルからメタデータを抽出
        chapter_filename = os.path.basename(chapter_files[0])
        extracted_metadata = output_manager.extract_metadata_from_content("", chapter_filename)
        metadata.update(extracted_metadata)
        if not metadata['title'] or metadata['title'] == 'Unknown_Article':
            metadata['title'] = title
    
    # 最新のサムネイル画像ファイルを取得（新構造対応）
    thumbnail_pattern = os.path.join(outputs_dir, '*/*_thumbnail_*_chapter*.png')
    thumbnail_files = sorted(glob.glob(thumbnail_pattern))
    if not thumbnail_files:
        # 旧構造もチェック
        thumbnail_pattern = os.path.join(outputs_dir, '*_thumbnail_*_chapter*.png')
        thumbnail_files = sorted(glob.glob(thumbnail_pattern))
    
    main_content = ""
    for i, chapter_file in enumerate(chapter_files):
        if os.path.exists(chapter_file):
            with open(chapter_file, 'r', encoding='utf-8') as f:
                chapter_content = f.read().strip()
            
            # 章間の改行
            if i > 0:
                main_content += "\n\n"
            
            # 章のH2タイトルの後にサムネイル画像を挿入
            lines = chapter_content.split('\n')
            modified_chapter = ""
            
            for j, line in enumerate(lines):
                modified_chapter += line + '\n'
                
                # H2章タイトルの直後にサムネイル画像を挿入
                if line.startswith('## ') and i < len(thumbnail_files):
                    thumbnail_file = thumbnail_files[i]
                    if os.path.exists(thumbnail_file):
                        modified_chapter += f"\n![第{i+1}章のサムネイル画像](thumbnail_chapter{i+1}_url)\n"
            
            main_content += modified_chapter.rstrip()
    
    # まとめセクション読み込み（動的検索、新構造対応）
    summary_pattern = os.path.join(outputs_dir, '*/*_article_summary.md')
    summary_files = glob.glob(summary_pattern)
    if not summary_files:
        # 旧構造もチェック
        summary_pattern = os.path.join(outputs_dir, '*_article_summary.md')
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
![{title}のアイキャッチ画像](eyecatch_image_url)

{main_content}

<!-- まとめセクション前の画像 -->
![まとめと実践ガイドのイメージ](summary_image_url)

{summary_content}"""
    
    # メタデータの最終確認・補完
    if not metadata.get('date'):
        metadata['date'] = datetime.now().strftime('%Y-%m-%d')
    if not metadata.get('timestamp'):
        metadata['timestamp'] = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    print(f"📊 検出されたメタデータ:")
    print(f"   Title: {metadata['title']}")
    print(f"   INT Number: {metadata['int_number']}")
    print(f"   Date: {metadata['date']}")
    
    # OutputManagerでファイル保存
    final_file = output_manager.save_content(complete_article, metadata, 'final_structure')
    final_with_images_file = output_manager.save_content(article_with_images, metadata, 'with_images')
    
    print(f"✅ 最終構造記事を作成しました:")
    print(f"   📄 基本版: {final_file}")
    print(f"   🖼️ 画像付き版: {final_with_images_file}")
    print(f"   📊 総文字数: {len(complete_article):,} 文字")
    print(f"   📁 章ファイル数: {len(chapter_files)}")
    print(f"   🖼️ サムネイル数: {len(thumbnail_files)}")
    
    # 構造確認
    lines = complete_article.split('\n')
    h2_count = 0
    for line_num, line in enumerate(lines, 1):
        if line.startswith('## ') and '第' in line and '章' in line:
            h2_count += 1
            print(f"   H2章 #{h2_count} (行{line_num}): {line}")
    
    return final_file, final_with_images_file

def upload_to_wordpress():
    """WordPressに最終記事をアップロード（動的版）"""
    try:
        # WordPressクライアント初期化
        client = WordPressClient()
        
        if not client.test_connection():
            print("❌ WordPress接続に失敗しました")
            return
        
        # OutputManagerを初期化
        output_manager = OutputManager()
        outputs_dir = output_manager.base_outputs_dir
        
        # 最終構造記事読み込み（動的検索、新構造対応）
        final_pattern = os.path.join(outputs_dir, '*/final_structure.md')
        final_files = glob.glob(final_pattern)
        if not final_files:
            # 旧構造もチェック
            final_pattern = os.path.join(outputs_dir, '*_article_*_final_structure.md')
            final_files = glob.glob(final_pattern)
        if not final_files:
            print("❌ 最終構造記事ファイルが見つかりません")
            return None
            
        final_file = sorted(final_files)[-1]  # 最新のファイル
        with open(final_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # タイトルとメタデータを動的抽出
        lines = markdown_content.split('\n')
        title = "生成AI教育ガイド"  # デフォルト値
        for line in lines:
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        meta_description = f"{title[:50]}の基本概念から実践手法まで専門家が解説"
        excerpt = markdown_content[:300] + "..." if len(markdown_content) > 300 else markdown_content
        
        # 画像アップロードとURL置換（動的検索）
        
        # アイキャッチ画像（新構造対応）
        eyecatch_pattern = os.path.join(outputs_dir, '*/*_eyecatch_*.png')
        eyecatch_files = glob.glob(eyecatch_pattern)
        if not eyecatch_files:
            # JPGファイルもチェック
            eyecatch_pattern = os.path.join(outputs_dir, '*/*_eyecatch_*.jpg')
            eyecatch_files = glob.glob(eyecatch_pattern)
        if not eyecatch_files:
            # 旧構造もチェック
            eyecatch_pattern = os.path.join(outputs_dir, '*_eyecatch_*.png')
            eyecatch_files = glob.glob(eyecatch_pattern)
        if not eyecatch_files:
            eyecatch_pattern = os.path.join(outputs_dir, '*_eyecatch_*.jpg')
            eyecatch_files = glob.glob(eyecatch_pattern)
            
        eyecatch_url = ""
        eyecatch_id = None
        if eyecatch_files:
            eyecatch_path = sorted(eyecatch_files)[-1]  # 最新のアイキャッチ
            eyecatch_result = client.upload_image(eyecatch_path, f"{title}アイキャッチ画像")
            if eyecatch_result:
                eyecatch_url = eyecatch_result['url']
                eyecatch_id = eyecatch_result.get('attachment_id')
        
        # 各章のサムネイル画像アップロード（動的検索、新構造対応）
        thumbnail_data = {}
        thumbnail_pattern = os.path.join(outputs_dir, '*/*_thumbnail_*_chapter*.png')
        thumbnail_files = sorted(glob.glob(thumbnail_pattern))
        if not thumbnail_files:
            # 旧構造もチェック
            thumbnail_pattern = os.path.join(outputs_dir, '*_thumbnail_*_chapter*.png')
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
    print("完全動的版で記事作成完了!")