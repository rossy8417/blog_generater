#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ブログ記事をWordPressに投稿する汎用スクリプト
"""

import os
import sys
import glob
import re
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from wordpress_client import WordPressClient, convert_markdown_to_gutenberg, insert_chapter_images

def find_latest_article_files(outputs_dir):
    """最新の記事ファイルと関連画像を検索（新構造対応）"""
    # 新構造で検索（タイトル-INT番号）
    article_pattern = os.path.join(outputs_dir, "*-INT-*/*_complete_article_*.md")
    article_files = glob.glob(article_pattern)
    
    # 旧構造でも検索（ブログタイトル/日付/INT番号）
    if not article_files:
        article_pattern = os.path.join(outputs_dir, "*/20*/*/*_complete_article_*.md")
        article_files = glob.glob(article_pattern)
    
    # さらに旧構造でも検索
    if not article_files:
        article_files = glob.glob(os.path.join(outputs_dir, "*_complete_article_*.md"))
    
    if not article_files:
        return None, [], None
    
    # 最新のファイルを選択
    latest_article = max(article_files, key=os.path.getctime)
    article_dir = os.path.dirname(latest_article)
    
    # 同じディレクトリ内の関連ファイルを検索
    eyecatch_pattern = os.path.join(article_dir, "*_eyecatch_*.png")
    thumbnail_pattern = os.path.join(article_dir, "*_thumbnail_*_chapter*.png")
    
    eyecatch_files = glob.glob(eyecatch_pattern)
    thumbnail_files = glob.glob(thumbnail_pattern)
    
    # チャプター画像をソート
    thumbnail_files.sort(key=lambda x: int(re.search(r'chapter(\d+)', x).group(1)) if re.search(r'chapter(\d+)', x) else 0)
    
    return latest_article, thumbnail_files, eyecatch_files[0] if eyecatch_files else None

def extract_article_metadata(markdown_content):
    """記事からメタデータを抽出"""
    lines = markdown_content.split('\n')
    title = ""
    meta_description = ""
    
    for line in lines:
        if line.startswith('# ') and not title:  # 最初のH1見出しのみをタイトルとして取得
            title = line[2:].strip()
        elif line.startswith('**Meta Description:**'):
            meta_description = line.replace('**Meta Description:**', '').strip()
        elif title and meta_description:
            break
    
    # excerptは最初の段落から生成
    paragraphs = [line.strip() for line in lines if line.strip() and not line.startswith('#') and not line.startswith('**Meta Description:**') and not line.startswith('![')]
    excerpt = paragraphs[0] if paragraphs else ""
    if len(excerpt) > 300:
        excerpt = excerpt[:300] + "..."
    
    return title, meta_description, excerpt

def clean_markdown_content(markdown_content, image_files):
    """マークダウンからローカル画像参照を削除"""
    # Meta Description行を削除
    content = re.sub(r'\*\*Meta Description:\*\*[^\n]*\n?', '', markdown_content)
    
    # ローカル画像パスを削除
    content = re.sub(r'!\[[^\]]*\]\([^)]*outputs/[^)]*\)', '', content)
    content = re.sub(r'!\[[^\]]*\]\(\./[^)]*\)', '', content)
    
    # 連続する空行を削除
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    return content.strip()

def post_blog_article(article_path=None):
    """ブログ記事をWordPressに投稿"""
    
    print("🚀 ブログ記事の投稿を開始します...\n")
    
    try:
        # WordPress クライアント初期化
        client = WordPressClient()
        
        # 接続テスト
        if not client.test_connection():
            print("❌ WordPress接続に失敗しました。")
            return False
        
        # 記事ファイルを検索または指定されたものを使用
        outputs_dir = os.path.join(project_root, "outputs")
        
        if article_path:
            if not os.path.exists(article_path):
                print(f"❌ 指定された記事ファイルが見つかりません: {article_path}")
                return False
            markdown_file = article_path
            # 指定された記事ファイルの同じディレクトリで画像を検索
            article_dir = os.path.dirname(article_path)
            basename = os.path.basename(article_path)
            
            # ファイル名から記事IDを抽出してパターンマッチング
            if '_complete_article_' in basename:
                # ディレクトリ内の画像ファイルを検索
                eyecatch_pattern = os.path.join(article_dir, "*_eyecatch_*.png")
                thumbnail_pattern = os.path.join(article_dir, "*_thumbnail_*_chapter*.png")
                
                import glob
                eyecatch_files = glob.glob(eyecatch_pattern)
                thumbnail_files = glob.glob(thumbnail_pattern)
                eyecatch_file = eyecatch_files[0] if eyecatch_files else None
                
                # チャプター画像をソート
                thumbnail_files.sort(key=lambda x: int(re.search(r'chapter(\d+)', x).group(1)) if re.search(r'chapter(\d+)', x) else 0)
            else:
                thumbnail_files = []
                eyecatch_file = None
        else:
            markdown_file, thumbnail_files, eyecatch_file = find_latest_article_files(outputs_dir)
            if not markdown_file:
                print("❌ 記事ファイルが見つかりません")
                return False
        
        print(f"📖 記事ファイル: {os.path.basename(markdown_file)}")
        
        # 記事読み込み
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"✅ 記事読み込み完了 ({len(markdown_content):,} 文字)")
        
        # メタデータ抽出
        title, meta_description, excerpt = extract_article_metadata(markdown_content)
        print(f"📝 タイトル: {title}")
        
        # 画像アップロード
        uploaded_images = []
        eyecatch_image_id = None
        
        # アイキャッチ画像をアップロード
        if eyecatch_file and os.path.exists(eyecatch_file):
            print(f"📤 アイキャッチ画像をアップロード中: {os.path.basename(eyecatch_file)}")
            result = client.upload_image(eyecatch_file, f"{title} - アイキャッチ画像")
            if result:
                eyecatch_image_id = result['attachment_id']
                print(f"   ✅ アイキャッチ画像アップロード完了 (ID: {eyecatch_image_id})")
        
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
        
        # マークダウンをクリーンアップしてWordPress形式に変換
        print("🔄 マークダウンをWordPress形式に変換中...")
        cleaned_content = clean_markdown_content(markdown_content, thumbnail_files)
        wp_content = convert_markdown_to_gutenberg(cleaned_content)
        
        # 章別画像を挿入
        if chapter_images:
            print(f"🖼️  {len(chapter_images)}個の章別画像を記事に挿入中...")
            wp_content = insert_chapter_images(wp_content, chapter_images)
        
        # 記事投稿
        print("\n📝 WordPressに記事投稿中...")
        
        result = client.create_post(
            title=title,
            content=wp_content,
            excerpt=excerpt,
            meta_description=meta_description,
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
    import argparse
    
    parser = argparse.ArgumentParser(description='ブログ記事をWordPressに投稿')
    parser.add_argument('--article', help='投稿する記事ファイルパス（指定しない場合は最新を自動選択）')
    
    args = parser.parse_args()
    
    success = post_blog_article(args.article)
    if success:
        print("\n✅ 処理が正常に完了しました！")
        sys.exit(0)
    else:
        print("\n❌ 処理が失敗しました。")
        sys.exit(1)