#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最終的な記事構造を作成：リード文→本文→まとめ＋画像配置
OutputManager対応版 - 正しいディレクトリ構造で保存
"""

import os
import glob
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加
import sys
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from wordpress_client import WordPressClient, convert_markdown_to_gutenberg, create_image_block
from utils.output_manager import OutputManager

def create_final_article_structure():
    """正しい記事構造で最終版を作成（OutputManager使用）"""
    
    # OutputManagerを初期化
    output_manager = OutputManager()
    
    # 記事メタデータ
    title = "生成AI教育とは？子供の学習に革命をもたらす基礎知識完全ガイド"
    
    # リード文作成
    lead_text = """**「子供の教育に生成AIを取り入れるべきか迷っている」「安全性や効果が心配」「何から始めたらいいかわからない」** そんな保護者の皆様のお悩みにお答えします。

生成AI教育は、従来の一方向的な教育から個別最適化された対話型学習への革命的な転換を実現します。世界各国で既に目覚ましい成果を上げており、日本でも政府が580億円の大規模予算で本格推進中です。

本記事では、生成AI教育の基本概念から年齢別の活用法、科学的検証されたメリット・デメリット、そして実践的な導入チェックリストまで、保護者が知っておくべき情報を完全網羅。お子様の未来を左右する教育革新について、専門家の視点で分かりやすく解説します。"""
    
    # 動的にファイルを検索（現在のディレクトリからの相対パスを使用）
    
    # 最新の章ファイルを取得（新構造対応）
    chapter_pattern = './outputs/*/*_article_*_chapter*.md'
    chapter_files = sorted(glob.glob(chapter_pattern))
    if not chapter_files:
        # 旧構造もチェック
        chapter_pattern = './outputs/*_article_*_chapter*.md'
        chapter_files = sorted(glob.glob(chapter_pattern))
    
    # 最新のサムネイル画像ファイルを取得（新構造対応）
    thumbnail_pattern = './outputs/*/*_thumbnail_*_chapter*.png'
    thumbnail_files = sorted(glob.glob(thumbnail_pattern))
    if not thumbnail_files:
        # 旧構造もチェック
        thumbnail_pattern = './outputs/*_thumbnail_*_chapter*.png'
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
    summary_pattern = './outputs/*/*_article_summary.md'
    summary_files = glob.glob(summary_pattern)
    if not summary_files:
        # 旧構造もチェック
        summary_pattern = './outputs/*_article_summary.md'
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
    
    # OutputManagerを使用してメタデータ作成
    metadata = {
        'title': title,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'int_number': 'INT-01',
        'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S')
    }
    
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

if __name__ == "__main__":
    # 最終構造作成
    final_file, final_with_images_file = create_final_article_structure()
    print("\n" + "="*50)
    print("OutputManager対応版で記事作成完了!")