#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用WordPress記事投稿スクリプト（品質チェック統合版）
WordPress投稿前品質チェック・自動修正システム統合版
"""

import os
import sys
import glob
import re
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.wordpress_client import WordPressClient, convert_markdown_to_gutenberg, insert_chapter_images
from scripts.pre_wordpress_quality_checker import run_pre_wordpress_quality_check

def find_latest_article_files(outputs_dir):
    """最新の記事ファイルと関連画像を検索（全フォーマット対応）"""
    
    print("🔍 記事ファイルを検索中...")
    
    # 検索パターン（優先順位順）
    search_patterns = [
        # 新構造（タイトル-INT番号）
        os.path.join(outputs_dir, "*-INT-*/*complete_article*.md"),
        # 旧構造（ブログタイトル/日付/INT番号）  
        os.path.join(outputs_dir, "*/20*/*/*complete_article*.md"),
        # さらに旧構造（直接配置）
        os.path.join(outputs_dir, "*complete_article*.md"),
        # 任意のマークダウンファイル
        os.path.join(outputs_dir, "**/*.md"),
    ]
    
    article_files = []
    for pattern in search_patterns:
        article_files = glob.glob(pattern, recursive=True)
        if article_files:
            print(f"✅ 記事ファイル発見: {len(article_files)}個")
            break
    
    if not article_files:
        print("❌ 記事ファイルが見つかりません")
        return None, [], None
    
    # 最新のファイルを選択
    latest_article = max(article_files, key=os.path.getctime)
    article_dir = os.path.dirname(latest_article)
    
    print(f"📖 最新記事: {os.path.basename(latest_article)}")
    print(f"📁 ディレクトリ: {article_dir}")
    
    # 画像ファイル検索パターン（PNG/JPG対応）
    image_patterns = {
        "eyecatch_png": os.path.join(article_dir, "*eyecatch*.png"),
        "eyecatch_jpg": os.path.join(article_dir, "*eyecatch*.jpg"),
        "thumbnail_png": os.path.join(article_dir, "*thumbnail*chapter*.png"),
        "thumbnail_jpg": os.path.join(article_dir, "*thumbnail*chapter*.jpg"),
        # 追加パターン
        "chapter_png": os.path.join(article_dir, "*chapter*.png"),
        "chapter_jpg": os.path.join(article_dir, "*chapter*.jpg"),
    }
    
    # アイキャッチ画像検索（JPGを優先）
    eyecatch_files = []
    eyecatch_files.extend(glob.glob(image_patterns["eyecatch_jpg"]))
    eyecatch_files.extend(glob.glob(image_patterns["eyecatch_png"]))
    
    eyecatch_file = None
    if eyecatch_files:
        eyecatch_file = max(eyecatch_files, key=os.path.getctime)
        print(f"📷 アイキャッチ画像: {os.path.basename(eyecatch_file)}")
        file_size_kb = os.path.getsize(eyecatch_file) / 1024
        print(f"   ファイルサイズ: {file_size_kb:.1f}KB")
    else:
        print("⚠️  アイキャッチ画像が見つかりません")
    
    # 章別画像検索（JPGを優先）
    thumbnail_files = []
    thumbnail_files.extend(glob.glob(image_patterns["thumbnail_jpg"]))
    thumbnail_files.extend(glob.glob(image_patterns["thumbnail_png"]))
    thumbnail_files.extend(glob.glob(image_patterns["chapter_jpg"]))
    thumbnail_files.extend(glob.glob(image_patterns["chapter_png"]))
    
    # 重複除去
    thumbnail_files = list(set(thumbnail_files))
    
    # 章番号でソート（複数のパターンに対応）
    def extract_chapter_number(filename):
        # chapter1, chapter2... パターン
        match = re.search(r"chapter(\d+)", filename)
        if match:
            return int(match.group(1))
        # その他の数値パターン
        match = re.search(r"(\d+)", filename)
        if match:
            return int(match.group(1))
        return 0
    
    thumbnail_files.sort(key=extract_chapter_number)
    
    if thumbnail_files:
        print(f"📷 章別画像: {len(thumbnail_files)}個")
        for i, thumb in enumerate(thumbnail_files, 1):
            print(f"   {i}. {os.path.basename(thumb)}")
    else:
        print("⚠️  章別画像が見つかりません")
    
    return latest_article, thumbnail_files, eyecatch_file

def extract_title_from_content(markdown_content):
    """マークダウンコンテンツからタイトルを抽出"""
    lines = markdown_content.split('\n')
    
    # H1タイトルを検索
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            # テンプレート識別子を除去
            title = re.sub(r'H\d+-\d+(-\d+)?\s*', '', title)
            return title
    
    # タイトルが見つからない場合はファイル名から推測
    return "自動生成記事"

def generate_meta_description(title, content):
    """タイトルと内容から自動的にメタディスクリプションを生成"""
    
    # 既存のメタディスクリプションを検索
    meta_match = re.search(r'\*\*Meta Description:\*\*\s*([^\n]+)', content)
    if meta_match:
        return meta_match.group(1).strip()
    
    # 自動生成（タイトルベース）
    if "AI" in title and "ルーチンワーク" in title:
        return "AI技術を活用したルーチンワーク負担軽減の完全ガイド。実践的な導入手順と具体的効果を専門家が詳細解説。"
    elif "生成AI" in title:
        return "生成AI活用の基本概念から実践手法まで専門家が解説。効率化・生産性向上の完全ガイド"
    else:
        # 汎用的なメタディスクリプション
        first_paragraph = content.split('\n\n')[0] if content else ""
        first_paragraph = re.sub(r'[#*\[\]()]', '', first_paragraph)
        if len(first_paragraph) > 150:
            return first_paragraph[:150] + "..."
        return first_paragraph or "専門家による詳細ガイド"

def post_blog_universal_with_quality_check():
    """汎用WordPress記事投稿（品質チェック統合版）"""
    
    print("🚀 WordPress記事投稿（品質チェック統合版）を開始します...\n")
    
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
        
        # 記事読み込み
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        print(f"✅ 記事読み込み完了 ({len(markdown_content):,} 文字)")
        
        # タイトル抽出
        title = extract_title_from_content(markdown_content)
        print(f"📝 タイトル: {title}")
        
        # メタディスクリプション生成
        meta_description = generate_meta_description(title, markdown_content)
        print(f"📄 メタディスクリプション: {meta_description}")
        
        # アイキャッチ画像をアップロード
        eyecatch_image_id = None
        if eyecatch_file and os.path.exists(eyecatch_file):
            print(f"\n📤 アイキャッチ画像をアップロード中: {os.path.basename(eyecatch_file)}")
            result = client.upload_image(eyecatch_file, f"{title} - アイキャッチ画像")
            if result:
                eyecatch_image_id = result['attachment_id']
                print(f"   ✅ アイキャッチ画像アップロード完了 (ID: {eyecatch_image_id})")
            else:
                print(f"   ❌ アイキャッチ画像アップロード失敗")
        
        # 章別画像をアップロード
        chapter_images = []
        if thumbnail_files:
            print(f"\n📤 章別画像をアップロード中...")
            for i, thumbnail_file in enumerate(thumbnail_files, 1):
                if os.path.exists(thumbnail_file):
                    print(f"   第{i}章画像: {os.path.basename(thumbnail_file)}")
                    result = client.upload_image(thumbnail_file, f"第{i}章サムネイル画像")
                    if result:
                        chapter_images.append({
                            'chapter': f'chapter{i}',
                            'attachment_id': result['attachment_id'],
                            'url': result['url']
                        })
                        print(f"   ✅ 第{i}章画像アップロード完了 (ID: {result['attachment_id']})")
                    else:
                        print(f"   ❌ 第{i}章画像アップロード失敗")
        
        # マークダウンをWordPress形式に変換
        print(f"\n🔄 マークダウンをWordPress形式に変換中...")
        
        # コンテンツクリーニング
        cleaned_content = markdown_content
        
        # Meta Description行を削除
        cleaned_content = re.sub(r'\*\*Meta Description:\*\*[^\n]*\n?', '', cleaned_content)
        
        # ローカル画像パスを削除
        cleaned_content = re.sub(r'\\!\[[^\]]*\]\([^)]*outputs/[^)]*\)', '', cleaned_content)
        cleaned_content = re.sub(r'\\!\[[^\]]*\]\(\./[^)]*\)', '', cleaned_content)
        cleaned_content = re.sub(r'\\!\[[^\]]*\]\([^)]*mnt/[^)]*\)', '', cleaned_content)
        
        # 連続する空行を削除
        cleaned_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', cleaned_content).strip()
        
        # WordPress形式に変換
        wp_content = convert_markdown_to_gutenberg(cleaned_content, debug=True)
        
        # 章別画像を挿入
        if chapter_images:
            print(f"🖼️  {len(chapter_images)}個の章別画像を記事に挿入中...")
            wp_content = insert_chapter_images(wp_content, chapter_images)
        
        # =========================
        # 🔍 WordPress投稿前品質チェック実行
        # =========================
        print(f"\n🔍 WordPress投稿前品質チェック・自動修正を実行中...")
        
        # 品質チェック実行
        corrected_wp_content, can_proceed = run_pre_wordpress_quality_check(
            wp_content,
            cleaned_content,
            chapter_images,
            title
        )
        
        # 投稿可否判定
        if not can_proceed:
            print(f"\n❌ 品質チェックでエラーが検出されました。")
            print(f"📋 品質問題を解決後に再実行してください。")
            print(f"💾 修正すべきコンテンツは tmp/quality_checks/ に保存されています。")
            return False
        
        print(f"\n✅ 品質チェック合格！WordPressへの投稿を続行します...")
        
        # 修正後のコンテンツを使用
        wp_content = corrected_wp_content
        
        # =========================
        # WordPress投稿実行
        # =========================
        
        # 抜粋生成
        lines = markdown_content.split('\n')
        excerpt = ""
        for line in lines:
            line = line.strip()
            if line and not line.startswith('#') and not line.startswith('*'):
                excerpt = line
                break
        
        if len(excerpt) > 300:
            excerpt = excerpt[:300] + "..."
        
        # 記事投稿
        print(f"\n📝 WordPressに記事投稿中...")
        
        result = client.create_post(
            title=title,
            content=wp_content,
            excerpt=excerpt,
            meta_description=meta_description,
            status="draft",
            featured_image_id=eyecatch_image_id
        )
        
        if result:
            print(f"\n🎉 記事投稿完了\!")
            print(f"📝 投稿ID: {result.get('post_id')}")
            print(f"🔗 編集URL: {result.get('edit_url')}")
            print(f"📊 ステータス: 下書き")
            if eyecatch_image_id:
                print(f"🖼️  アイキャッチ画像: 設定済み (ID: {eyecatch_image_id})")
            if chapter_images:
                print(f"📷 章別画像: {len(chapter_images)}個挿入済み")
            
            print(f"\n✅ 品質チェック完了:")
            print(f"   🔧 自動修正が適用されました")
            print(f"   📋 H5/H6タグ禁止ルール適用済み")
            print(f"   🖼️  章別画像配置確認済み")
            print(f"   📝 見出し構造最適化済み")
            
            # 投稿情報をファイルに保存
            post_info_file = os.path.join(project_root, "outputs", "latest_post_info.txt")
            with open(post_info_file, 'w', encoding='utf-8') as f:
                f.write(f"投稿ID: {result.get('post_id')}\n")
                f.write(f"タイトル: {title}\n")
                f.write(f"編集URL: {result.get('edit_url')}\n")
                f.write(f"投稿日時: {os.popen('date').read().strip()}\n")
                f.write(f"品質チェック: 合格\n")
                f.write(f"自動修正適用: あり\n")
            
            return True
        else:
            print("❌ 記事投稿に失敗しました")
            return False
            
    except Exception as e:
        print(f"❌ エラーが発生しました: {str(e)}")
        import traceback
        print(f"詳細: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = post_blog_universal_with_quality_check()
    
    if success:
        print("\n✅ 処理が正常に完了しました！")
        print("🔍 品質チェック統合版による安全な投稿が完了しました")
    else:
        print("\n❌ 処理が失敗しました。")
        print("📋 品質チェック結果を確認してください")
EOF < /dev/null
