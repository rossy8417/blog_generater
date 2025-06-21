#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress Blog Generator Client (Fixed Version)
Claude CodeからWordPressプラグインAPIを呼び出して記事を作成するクライアント（修正版）
"""

import os
import requests
import json
import re
from dotenv import load_dotenv
from typing import Dict, Any, Optional

# 環境変数読み込み
load_dotenv()

class WordPressClient:
    """WordPressプラグインAPI クライアント"""
    
    def __init__(self):
        self.api_key = os.getenv('WORDPRESS_API_KEY')
        self.endpoint = os.getenv('WORDPRESS_ENDPOINT')
        
        if not self.api_key:
            raise ValueError("WORDPRESS_API_KEY が .env ファイルに設定されていません")
        if not self.endpoint:
            raise ValueError("WORDPRESS_ENDPOINT が .env ファイルに設定されていません")
        
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
    
    def create_post(self, 
                   title: str, 
                   content: str, 
                   excerpt: str = "", 
                   meta_description: str = "",
                   status: str = "draft",
                   featured_image_id: Optional[int] = None) -> Dict[str, Any]:
        """
        WordPressに記事を作成
        
        Args:
            title: 記事タイトル
            content: 記事本文（WordPressブロック形式）
            excerpt: 記事の抜粋
            meta_description: SEO用メタディスクリプション
            status: 投稿ステータス (draft, publish, private)
            featured_image_id: アイキャッチ画像のID
        
        Returns:
            作成結果とメタデータ
        """
        
        data = {
            'title': title,
            'content': content,
            'excerpt': excerpt,
            'meta_description': meta_description,
            'status': status
        }
        
        if featured_image_id:
            data['featured_image_id'] = featured_image_id
        
        try:
            print(f"📝 WordPress記事作成中...")
            print(f"   タイトル: {title}")
            print(f"   ステータス: {status}")
            print(f"   エンドポイント: {self.endpoint}/create-post")
            
            response = requests.post(
                f"{self.endpoint}/create-post",
                headers=self.headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 記事作成成功!")
                print(f"   投稿ID: {result.get('post_id')}")
                print(f"   編集URL: {result.get('edit_url')}")
                return result
            else:
                error_msg = f"API呼び出しエラー: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                raise Exception(error_msg)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"接続エラー: {str(e)}"
            print(f"❌ {error_msg}")
            raise Exception(error_msg)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        プラグインAPI使用状況を取得
        
        Returns:
            使用統計データ
        """
        try:
            response = requests.get(
                f"{self.endpoint}/usage",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"使用状況取得エラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"接続エラー: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        WordPress プラグインへの接続テスト
        
        Returns:
            接続成功可否
        """
        try:
            print(f"🔗 WordPress接続テスト中...")
            print(f"   エンドポイント: {self.endpoint}")
            
            usage = self.get_usage_stats()
            print(f"✅ 接続成功!")
            print(f"   今日の記事生成数: {usage.get('today_count', 0)}")
            print(f"   総記事生成数: {usage.get('total_count', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ 接続失敗: {str(e)}")
            print("\n📋 確認事項:")
            print("1. WordPressプラグインが有効化されているか")
            print("2. .envファイルのWORDPRESS_API_KEYが正しいか")
            print("3. .envファイルのWORDPRESS_ENDPOINTが正しいか")
            print("4. WordPressサイトがアクセス可能か")
            return False

    def upload_image(self, image_path: str, alt_text: str = "") -> Optional[Dict[str, Any]]:
        """
        画像をWordPressにアップロード（WordPress Media API互換）
        
        Args:
            image_path: ローカル画像ファイルのパス
            alt_text: 画像のalt属性
            
        Returns:
            アップロード結果（URL、ID等）
        """
        try:
            if not os.path.exists(image_path):
                print(f"❌ 画像ファイルが見つかりません: {image_path}")
                return None
                
            print(f"📤 画像アップロード中: {os.path.basename(image_path)}")
            
            # 既存のupload-imageエンドポイントを使用
            upload_endpoint = f"{self.endpoint}/upload-image"
            print(f"   エンドポイント: {upload_endpoint}")
            
            with open(image_path, 'rb') as f:
                files = {
                    'file': (os.path.basename(image_path), f, 'image/png')
                }
                headers = {
                    'X-API-Key': self.api_key
                }
                
                response = requests.post(
                    upload_endpoint,
                    headers=headers,
                    files=files,
                    timeout=60
                )
                
                print(f"   レスポンスコード: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ 画像アップロード成功!")
                    
                    # CozeのJSコードと同じレスポンス形式を期待
                    if 'source_url' in result and 'id' in result:
                        print(f"   画像ID: {result.get('id')}")
                        print(f"   URL: {result.get('source_url')}")
                        return {
                            'attachment_id': result.get('id'),
                            'url': result.get('source_url')
                        }
                    # 従来のレスポンス形式もサポート
                    elif 'attachment_id' in result:
                        print(f"   画像ID: {result.get('attachment_id')}")
                        print(f"   URL: {result.get('url')}")
                        return result
                    else:
                        print(f"❌ 予期しないレスポンス形式: {result}")
                        return None
                else:
                    error_text = response.text
                    print(f"❌ 画像アップロード失敗: {response.status_code}")
                    print(f"   エラー詳細: {error_text}")
                    return None
                    
        except Exception as e:
            print(f"❌ 画像アップロードエラー: {str(e)}")
            return None

def format_text(text: str) -> str:
    """
    テキストの書式設定を適用
    """
    # 太字 **text** → <strong>text</strong>
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    
    # イタリック *text* → <em>text</em>
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'<em>\1</em>', text)
    
    # コード `code` → <code>code</code>
    text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
    
    # マーカー ==text== → <mark>text</mark>
    text = re.sub(r'==([^=]+)==', r'<mark>\1</mark>', text)
    
    return text

def convert_table_to_gutenberg(table_lines: list) -> str:
    """
    マークダウンテーブルをWordPressテーブルブロックに変換
    """
    if not table_lines:
        return ''
    
    # ヘッダー行とデータ行を分離
    header_row = None
    data_rows = []
    
    for line in table_lines:
        # パイプで分割してセルを抽出
        cells = [cell.strip() for cell in line.split('|')]
        # 空のセル（行の両端）を除去
        cells = [cell for cell in cells if cell]
        
        if cells:
            if header_row is None:
                header_row = cells
            else:
                data_rows.append(cells)
    
    if not header_row:
        return ''
    
    # テーブルHTML生成
    table_html = '<figure class="wp-block-table"><table>'
    
    # ヘッダー
    table_html += '<thead><tr>'
    for cell in header_row:
        table_html += f'<th>{format_text(cell)}</th>'
    table_html += '</tr></thead>'
    
    # データ行
    if data_rows:
        table_html += '<tbody>'
        for row in data_rows:
            table_html += '<tr>'
            for cell in row:
                table_html += f'<td>{format_text(cell)}</td>'
            table_html += '</tr>'
        table_html += '</tbody>'
    
    table_html += '</table></figure>'
    
    return f'<!-- wp:table -->\n{table_html}\n<!-- /wp:table -->\n\n'

def create_image_block(image_url: str, alt_text: str = "", image_id: int = 0) -> str:
    """
    Coze形式のWordPress画像ブロックを生成
    
    Args:
        image_url: 画像URL
        alt_text: alt属性
        image_id: WordPress画像ID
    
    Returns:
        WordPressブロック形式のHTML
    """
    # 画像IDが設定されている場合のみid属性を追加
    id_attr = f'"id":{image_id},' if image_id > 0 else ''
    return f'''<!-- wp:image {{{id_attr}"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full"><img src="{image_url}" alt="{alt_text}"/></figure>
<!-- /wp:image -->

'''

def convert_markdown_to_gutenberg(markdown_content: str) -> str:
    """
    マークダウンをWordPressブロックエディタ形式に変換（修正版）
    
    Args:
        markdown_content: マークダウン形式のコンテンツ
    
    Returns:
        WordPressブロック形式のHTML
    """
    content = ""
    lines = markdown_content.split('\n')
    i = 0
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 空行スキップ
        if not line:
            i += 1
            continue
            
        # H1見出し（章タイトル）
        if line.startswith('# '):
            heading_text = line[2:].strip()
            content += f'<!-- wp:heading {{"level":2}} -->\n'
            content += f'<h2 class="wp-block-heading">{heading_text}</h2>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H2見出し
        elif line.startswith('## '):
            heading_text = line[3:].strip()
            content += f'<!-- wp:heading {{"level":3}} -->\n'
            content += f'<h3 class="wp-block-heading">{heading_text}</h3>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H3見出し
        elif line.startswith('### '):
            heading_text = line[4:].strip()
            content += f'<!-- wp:heading {{"level":4}} -->\n'
            content += f'<h4 class="wp-block-heading">{heading_text}</h4>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H4見出し
        elif line.startswith('#### '):
            heading_text = line[5:].strip()
            content += f'<!-- wp:heading {{"level":5}} -->\n'
            content += f'<h5 class="wp-block-heading">{heading_text}</h5>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # 表の検出と変換（改善版）
        elif '|' in line and line.count('|') >= 2:
            table_lines = []
            
            # 表の全行を収集
            while i < len(lines):
                current_line = lines[i].strip()
                if not current_line:
                    break
                if '|' in current_line and current_line.count('|') >= 2:
                    # 区切り線（|---|---|）はスキップ
                    if not re.match(r'^\|[\s\-:|]+\|$', current_line):
                        table_lines.append(current_line)
                    i += 1
                else:
                    break
            
            if table_lines:
                content += convert_table_to_gutenberg(table_lines)
            continue
            
        # 番号付きリスト
        elif re.match(r'^\d+\.\s', line):
            list_items = []
            while i < len(lines):
                current_line = lines[i].strip()
                if re.match(r'^\d+\.\s', current_line):
                    item_text = re.sub(r'^\d+\.\s*', '', current_line)
                    list_items.append(format_text(item_text))
                    i += 1
                else:
                    break
            
            content += f'<!-- wp:list {{"ordered":true}} -->\n'
            content += '<ol>'
            for item in list_items:
                content += f'<li>{item}</li>'
            content += '</ol>\n'
            content += '<!-- /wp:list -->\n\n'
            continue
            
        # 箇条書きリスト
        elif re.match(r'^[\-\*]\s', line):
            list_items = []
            while i < len(lines):
                current_line = lines[i].strip()
                if re.match(r'^[\-\*]\s', current_line):
                    item_text = re.sub(r'^[\-\*]\s*', '', current_line)
                    list_items.append(format_text(item_text))
                    i += 1
                else:
                    break
            
            content += f'<!-- wp:list -->\n'
            content += '<ul>'
            for item in list_items:
                content += f'<li>{item}</li>'
            content += '</ul>\n'
            content += '<!-- /wp:list -->\n\n'
            continue
            
        # 引用ブロック
        elif line.startswith('> '):
            quote_text = line[2:].strip()
            quote_text = format_text(quote_text)
            content += f'<!-- wp:quote -->\n'
            content += f'<blockquote class="wp-block-quote"><p>{quote_text}</p></blockquote>\n'
            content += f'<!-- /wp:quote -->\n\n'
            i += 1
            
        # コードブロック
        elif line.startswith('```'):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code_lines.append(lines[i])
                i += 1
            if i < len(lines):
                i += 1  # 終了の```をスキップ
            
            code_content = '\n'.join(code_lines)
            content += f'<!-- wp:code -->\n'
            content += f'<pre class="wp-block-code"><code>{code_content}</code></pre>\n'
            content += f'<!-- /wp:code -->\n\n'
            
        # 画像記法の検出と変換
        elif line.strip().startswith('![') and '](http' in line:
            # マークダウン画像記法: ![alt](url) を WordPress画像ブロックに変換
            match = re.match(r'!\[([^\]]*)\]\(([^)]+)\)', line.strip())
            if match:
                alt_text = match.group(1)
                image_url = match.group(2)
                
                # Coze形式のWordPress画像ブロックを生成（画像IDは後で設定される）
                content += f'<!-- wp:image {{"sizeSlug":"full","linkDestination":"none"}} -->\n'
                content += f'<figure class="wp-block-image size-full"><img src="{image_url}" alt="{alt_text}"/></figure>\n'
                content += f'<!-- /wp:image -->\n\n'
            i += 1
            
        # Meta Description行をスキップ
        elif re.match(r'\*\*Meta Description:\*\*', line):
            i += 1
            
        # ローカルファイルパスの画像記法をスキップ
        elif line.strip().startswith('![') and ('outputs/' in line or './' in line or '/mnt/' in line):
            i += 1
            
        # 通常の段落
        else:
            paragraph_text = format_text(line)
            content += f'<!-- wp:paragraph -->\n'
            content += f'<p>{paragraph_text}</p>\n'
            content += f'<!-- /wp:paragraph -->\n\n'
            i += 1
    
    return content

def insert_chapter_images(wp_content: str, chapter_images: list) -> str:
    """
    WordPressブロック形式のコンテンツに章別画像を挿入
    
    Args:
        wp_content: WordPressブロック形式のコンテンツ
        chapter_images: [{'chapter': 'chapter1', 'attachment_id': 123, 'url': '...'}] 形式のリスト
    
    Returns:
        画像が挿入されたWordPressブロック形式のコンテンツ
    """
    import re
    
    # 章番号順にソート
    chapter_images_sorted = sorted(chapter_images, key=lambda x: x['chapter'])
    
    # 章番号付きのH2見出しのみを対象にする
    heading_pattern = r'<!-- wp:heading \{"level":2\} -->\s*\n<h2 class="wp-block-heading">([^<]*(?:<a[^>]*>[^<]*</a>)?[^<]*)</h2>\s*\n<!-- /wp:heading -->'
    
    heading_count = 0
    
    def replace_heading(match):
        nonlocal heading_count
        heading_content = match.group(0)
        heading_text = match.group(1).strip()
        
        # アンカータグを除去して見出しテキストを抽出
        clean_heading = re.sub(r'<a[^>]*>[^<]*</a>\s*', '', heading_text)
        
        # 章番号付きの見出しのみ処理（"1. ", "2. " などで始まる、または数字のみ）
        if re.match(r'^\d+[\.\s]', clean_heading) or re.match(r'^第?\d+章', clean_heading):
            # 対応する章の画像があるかチェック
            if heading_count < len(chapter_images_sorted):
                image_info = chapter_images_sorted[heading_count]
                
                # WordPress画像ブロックを作成
                image_block = f'''<!-- wp:image {{"id":{image_info["attachment_id"]},"sizeSlug":"full","linkDestination":"none"}} -->
<figure class="wp-block-image size-full"><img src="{image_info["url"]}" alt="第{heading_count + 1}章サムネイル画像" class="wp-image-{image_info["attachment_id"]}"/></figure>
<!-- /wp:image -->

'''
                heading_count += 1
                return heading_content + '\n\n' + image_block
        
        return heading_content
    
    # すべてのh2見出しに対して処理
    wp_content = re.sub(heading_pattern, replace_heading, wp_content)
    
    return wp_content

# テスト実行用
if __name__ == "__main__":
    try:
        client = WordPressClient()
        
        # 接続テスト
        if client.test_connection():
            print("\n🎉 WordPressクライアント準備完了!")
        else:
            print("\n⚠️  WordPressクライアント設定を確認してください")
            
    except Exception as e:
        print(f"❌ 初期化エラー: {str(e)}")