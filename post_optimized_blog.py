#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最適化画像対応ブログ記事投稿スクリプト
scripts/image_generator.pyで生成された最適化画像を自動認識して投稿
"""

import os
import sys
import glob
import re
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from wordpress_client import WordPressClient, convert_markdown_to_gutenberg, insert_chapter_images

def find_latest_article_files(outputs_dir):
    """最新の記事ファイルと関連画像を検索（最適化画像対応）"""
    # 新構造で検索（タイトル-INT番号）
    article_pattern = os.path.join(outputs_dir, "*-INT-*/*complete_article*.md")
    article_files = glob.glob(article_pattern)
    
    # 旧構造でも検索（ブログタイトル/日付/INT番号）
    if not article_files:
        article_pattern = os.path.join(outputs_dir, "*/20*/*/*complete_article*.md")
        article_files = glob.glob(article_pattern)
    
    # さらに旧構造でも検索
    if not article_files:
        article_files = glob.glob(os.path.join(outputs_dir, "*complete_article*.md"))
    
    if not article_files:
        return None, [], None
    
    # 最新のファイルを選択
    latest_article = max(article_files, key=os.path.getctime)
    article_dir = os.path.dirname(latest_article)
    
    # 同じディレクトリ内の関連ファイルを検索（最適化画像対応）
    eyecatch_pattern_png = os.path.join(article_dir, "*_eyecatch_*.png")
    eyecatch_pattern_jpg = os.path.join(article_dir, "*_eyecatch_*.jpg")
    thumbnail_pattern = os.path.join(article_dir, "*_thumbnail_*_chapter*.png")
    
    eyecatch_files_png = glob.glob(eyecatch_pattern_png)
    eyecatch_files_jpg = glob.glob(eyecatch_pattern_jpg)
    eyecatch_files = eyecatch_files_jpg + eyecatch_files_png  # JPGを優先
    thumbnail_files = glob.glob(thumbnail_pattern)
    
    # 最新のアイキャッチファイルを選択（最適化されたものを優先）
    eyecatch_file = None
    if eyecatch_files:
        eyecatch_file = max(eyecatch_files, key=os.path.getctime)
        print(f"📷 Found eyecatch: {os.path.basename(eyecatch_file)}")
        file_size_kb = os.path.getsize(eyecatch_file) / 1024
        print(f"   File size: {file_size_kb:.1f}KB")
    
    # チャプター画像をソート
    thumbnail_files.sort(key=lambda x: int(re.search(r'chapter(\d+)', x).group(1)) if re.search(r'chapter(\d+)', x) else 0)
    
    return latest_article, thumbnail_files, eyecatch_file

def post_optimized_blog():
    """最適化画像対応ブログ記事をWordPressに投稿"""
    
    print("🚀 最適化画像対応ブログ記事の投稿を開始します...\n")
    
    try:
        # WordPress クライアント初期化
        client = WordPressClient()
        
        # 接続テスト
        if not client.test_connection():
            print("❌ WordPress接続に失敗しました。")
            return False
        
        # 最新記事ファイルを検索
        outputs_dir = os.path.join(project_root, "outputs")
        markdown_file, thumbnail_files, eyecatch_file = find_latest_article_files(outputs_dir)
        
        if not markdown_file:
            print("❌ 記事ファイルが見つかりません")
            return False
        
        print(f"📖 記事ファイル: {os.path.basename(markdown_file)}")
        
        # 記事読み込み
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"✅ 記事読み込み完了 ({len(markdown_content):,} 文字)")
        
        # タイトル抽出
        lines = markdown_content.split('\n')
        title = ""
        for line in lines:
            if line.startswith('# ') and not title:
                title = line[2:].strip()
                break
        
        if not title:
            title = "生成AI定型業務自動化完全ガイド"
        
        print(f"📝 タイトル: {title}")
        
        # アイキャッチ画像をアップロード
        eyecatch_image_id = None
        if eyecatch_file and os.path.exists(eyecatch_file):
            print(f"📤 アイキャッチ画像をアップロード中: {os.path.basename(eyecatch_file)}")
            result = client.upload_image(eyecatch_file, f"{title} - アイキャッチ画像")
            if result:
                eyecatch_image_id = result['attachment_id']
                print(f"   ✅ アイキャッチ画像アップロード完了 (ID: {eyecatch_image_id})")
            else:
                print(f"   ❌ アイキャッチ画像アップロード失敗")
        
        # 章別画像をアップロード
        chapter_images = []
        for i, thumbnail_file in enumerate(thumbnail_files, 1):
            if os.path.exists(thumbnail_file):
                print(f"📤 第{i}章画像をアップロード中: {os.path.basename(thumbnail_file)}")
                result = client.upload_image(thumbnail_file, f"第{i}章サムネイル画像")
                if result:
                    chapter_images.append({
                        'chapter': f'chapter{i}',
                        'attachment_id': result['attachment_id'],
                        'url': result['url']
                    })
                    print(f"   ✅ 第{i}章画像アップロード完了 (ID: {result['attachment_id']})")
        
        # マークダウンをWordPress形式に変換
        print("🔄 マークダウンをWordPress形式に変換中...")
        # Meta Description行を削除
        cleaned_content = re.sub(r'\*\*Meta Description:\*\*[^\n]*\n?', '', markdown_content)
        # ローカル画像パスを削除
        cleaned_content = re.sub(r'!\[[^\]]*\]\([^)]*outputs/[^)]*\)', '', cleaned_content)
        cleaned_content = re.sub(r'!\[[^\]]*\]\(\./[^)]*\)', '', cleaned_content)
        # 連続する空行を削除
        cleaned_content = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned_content).strip()
        
        wp_content = convert_markdown_to_gutenberg(cleaned_content, debug=True)
        
        # 章別画像を挿入
        if chapter_images:
            print(f"🖼️  {len(chapter_images)}個の章別画像を記事に挿入中...")
            wp_content = insert_chapter_images(wp_content, chapter_images)
        
        # 記事投稿
        print("\n📝 WordPressに記事投稿中...")
        
        excerpt = lines[0] if lines else ""
        if len(excerpt) > 300:
            excerpt = excerpt[:300] + "..."
        
        result = client.create_post(
            title=title,
            content=wp_content,
            excerpt=excerpt,
            meta_description="生成AI定型業務自動化の基本概念から実践手法まで専門家が解説。効率化・生産性向上の完全ガイド",
            status="draft",
            featured_image_id=eyecatch_image_id
        )
        
        if result:
            print(f"\n🎉 記事投稿完了!")
            print(f"📝 投稿ID: {result.get('post_id')}")
            print(f"🔗 編集URL: {result.get('edit_url')}")
            print(f"📊 ステータス: 下書き")
            if eyecatch_image_id:
                print(f"🖼️  アイキャッチ画像: 設定済み (ID: {eyecatch_image_id})")
            if chapter_images:
                print(f"📷 章別画像: {len(chapter_images)}個挿入済み")
            return True
        else:
            print("❌ 記事投稿に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        return False

if __name__ == "__main__":
    success = post_optimized_blog()
    
    if success:
        print("\n✅ 処理が正常に完了しました！")
    else:
        print("\n❌ 処理が失敗しました。")