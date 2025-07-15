#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress Blog Generator Client (COMPLETELY FIXED VERSION)
Claude CodeからWordPressプラグインAPIを呼び出して記事を作成するクライアント（完全修正版）

主な修正点:
1. H2見出しの保持 - すべてのMarkdown H2をWordPress H2として保持（章見出し用）
2. H5/H6禁止処理 - H5/H6を検出してH4に自動降格
3. 見出し構造の完全修正 - 正しい階層構造の維持
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
    return f'''<!-- wp:image {{{id_attr}"className":"wp-block-image size-full"}} -->
<figure class="wp-block-image size-full"><img src="{image_url}" alt="{alt_text}" class="wp-image-{image_id}"/></figure>
<!-- /wp:image -->

'''

def validate_heading_structure(content: str) -> dict:
    """
    WordPress投稿前の見出し構造チェック
    """
    import re
    
    # 見出しレベル別カウント
    h2_count = len(re.findall(r'<!-- wp:heading \{"level":2\}', content))
    h3_count = len(re.findall(r'<!-- wp:heading \{"level":3\}', content))
    h4_count = len(re.findall(r'<!-- wp:heading \{"level":4\}', content))
    h5_count = len(re.findall(r'<!-- wp:heading \{"level":5\}', content))
    h6_count = len(re.findall(r'<!-- wp:heading \{"level":6\}', content))
    
    # H5以上の禁止タグ検出
    forbidden_tags = h5_count + h6_count
    
    # 理想的な構造チェック
    structure_issues = []
    if h3_count == 0 and h4_count > 0:
        structure_issues.append("H3見出しが欠落してH4が直接使用されています")
    if forbidden_tags > 0:
        structure_issues.append(f"H5/H6タグが{forbidden_tags}個使用されています（禁止）")
    
    return {
        "h2": h2_count,
        "h3": h3_count, 
        "h4": h4_count,
        "h5": h5_count,
        "h6": h6_count,
        "forbidden_count": forbidden_tags,
        "structure_issues": structure_issues,
        "is_valid": len(structure_issues) == 0
    }

def convert_markdown_to_gutenberg(markdown_content: str, debug: bool = False) -> str:
    """
    マークダウンをWordPressブロックエディタ形式に変換（完全修正版）
    
    変換ルール:
    - Markdown H1 → Skip (タイトル用)
    - Markdown H2 → WordPress H2 (章見出し・画像挿入ポイント)
    - Markdown H3 → WordPress H3 (セクション見出し)
    - Markdown H4 → WordPress H4 (サブセクション見出し)
    - Markdown H5/H6 → ERROR/WARNING → H4に自動降格
    
    Args:
        markdown_content: マークダウン形式のコンテンツ
        debug: デバッグ情報を表示するかどうか
    
    Returns:
        WordPressブロック形式のHTML
    """
    content = ""
    lines = markdown_content.split('\n')
    i = 0
    
    # デバッグ情報収集用
    heading_info = []
    skipped_lines = []
    template_ids_found = []
    errors_found = []
    
    if debug:
        print("🔍 マークダウン→WordPress変換デバッグ開始")
        print(f"📝 総行数: {len(lines)}")
    
    while i < len(lines):
        line = lines[i].strip()
        
        # 空行スキップ
        if not line:
            i += 1
            continue
            
        # H1見出し（メインタイトル）- 常にスキップ
        if line.startswith('# '):
            heading_text = line[2:].strip()
            
            # テンプレート識別子チェック
            if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                template_ids_found.append(f"H1: {heading_text}")
            
            # H1見出しは常にスキップ（メインタイトル用）
            skipped_lines.append(f"H1スキップ: {heading_text}")
            i += 1
            
        # H2見出し（章見出し） - 常にH2として保持（修正済み）
        elif line.startswith('## '):
            heading_text = line[3:].strip()
            
            # テンプレート識別子チェック
            if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                template_ids_found.append(f"H2: {heading_text}")
            
            # すべてのH2見出しをWordPressのH2として保持（画像挿入ポイント）
            heading_info.append(f"H2→H2: {heading_text}")
            content += f'<!-- wp:heading {{"level":2}} -->\n'
            content += f'<h2 class="wp-block-heading">{heading_text}</h2>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H3見出し
        elif line.startswith('### '):
            heading_text = line[4:].strip()
            
            # テンプレート識別子チェック
            if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                template_ids_found.append(f"H3: {heading_text}")
            
            heading_info.append(f"H3→H3: {heading_text}")
            content += f'<!-- wp:heading {{"level":3}} -->\n'
            content += f'<h3 class="wp-block-heading">{heading_text}</h3>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H4見出し
        elif line.startswith('#### '):
            heading_text = line[5:].strip()
            
            # テンプレート識別子チェック
            if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                template_ids_found.append(f"H4: {heading_text}")
            
            heading_info.append(f"H4→H4: {heading_text}")
            content += f'<!-- wp:heading {{"level":4}} -->\n'
            content += f'<h4 class="wp-block-heading">{heading_text}</h4>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H5見出し（禁止） - エラー処理と自動修正
        elif line.startswith('##### '):
            heading_text = line[6:].strip()
            error_msg = f"❌ H5見出しが検出されました（禁止）: {heading_text}"
            errors_found.append(error_msg)
            print(error_msg)
            
            # H5をH4に降格して変換
            print(f"🔄 H5→H4に自動修正: {heading_text}")
            heading_info.append(f"H5→H4 (修正): {heading_text}")
            content += f'<!-- wp:heading {{"level":4}} -->\n'
            content += f'<h4 class="wp-block-heading">{heading_text}</h4>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H6見出し（禁止） - エラー処理と自動修正
        elif line.startswith('###### '):
            heading_text = line[7:].strip()
            error_msg = f"❌ H6見出しが検出されました（禁止）: {heading_text}"
            errors_found.append(error_msg)
            print(error_msg)
            
            # H6をH4に降格して変換
            print(f"🔄 H6→H4に自動修正: {heading_text}")
            heading_info.append(f"H6→H4 (修正): {heading_text}")
            content += f'<!-- wp:heading {{"level":4}} -->\n'
            content += f'<h4 class="wp-block-heading">{heading_text}</h4>\n'
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
                content += f'<!-- wp:image {{"className":"wp-block-image size-full"}} -->\n'
                content += f'<figure class="wp-block-image size-full"><img src="{image_url}" alt="{alt_text}" class="wp-image-0"/></figure>\n'
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
    
    # デバッグ情報出力
    if debug:
        print("\n📊 変換結果サマリー:")
        print(f"✅ 変換された見出し: {len(heading_info)}個")
        for heading in heading_info:
            print(f"   {heading}")
        
        if skipped_lines:
            print(f"\n⏭️  スキップされた行: {len(skipped_lines)}個")
            for skipped in skipped_lines:
                print(f"   {skipped}")
        
        if template_ids_found:
            print(f"\n⚠️  テンプレート識別子発見: {len(template_ids_found)}個")
            for template_id in template_ids_found:
                print(f"   {template_id}")
        else:
            print("\n✅ テンプレート識別子: なし")
            
        if errors_found:
            print(f"\n❌ エラー検出: {len(errors_found)}個")
            for error in errors_found:
                print(f"   {error}")
        else:
            print("\n✅ 見出し構造エラー: なし")
        
        # WordPressブロック数カウント
        block_counts = {
            'heading': content.count('<!-- wp:heading'),
            'paragraph': content.count('<!-- wp:paragraph'),
            'list': content.count('<!-- wp:list'),
            'table': content.count('<!-- wp:table'),
            'image': content.count('<!-- wp:image')
        }
        print(f"\n📝 生成されたWordPressブロック:")
        for block_type, count in block_counts.items():
            if count > 0:
                print(f"   {block_type}: {count}個")
        
        print("🔍 変換デバッグ完了\n")
    
    # エラーがあった場合の警告表示
    if errors_found:
        print(f"\n⚠️  変換中に{len(errors_found)}個のエラーが検出され、自動修正されました")
        print("📋 修正内容を確認してください")
    
    return content

def insert_chapter_images(wp_content: str, chapter_images: list) -> str:
    """
    WordPressブロック形式のコンテンツに章別画像を挿入
    
    Args:
        wp_content: WordPressブロック形式のコンテンツ
        chapter_images: [{'chapter': 'chapter1', 'attachment_id': 123, 'url': '...'}] 形式のリスト
                      または [{'chapter_counter': 1, 'id': 123, 'url': '...'}] 形式のリスト
    
    Returns:
        画像が挿入されたWordPressブロック形式のコンテンツ
    """
    import re
    
    # 章番号順にソート（新旧両フォーマット対応）
    if chapter_images and 'chapter_counter' in chapter_images[0]:
        # 新フォーマット: {'chapter_counter': 1, 'id': 123, 'url': '...'}
        chapter_images_sorted = sorted(chapter_images, key=lambda x: x['chapter_counter'])
    else:
        # 旧フォーマット: {'chapter': 'chapter1', 'attachment_id': 123, 'url': '...'}
        chapter_images_sorted = sorted(chapter_images, key=lambda x: x['chapter'])
    
    # H2見出しブロックのパターン（修正版）
    heading_pattern = r'(<!-- wp:heading \{"level":2\} -->\s*<h2[^>]*>[^<]*</h2>\s*<!-- /wp:heading -->)'
    
    chapter_counter = 0
    def replace_heading(match):
        original_h2 = match.group(1)
        nonlocal chapter_counter
        chapter_counter += 1
        
        # 対応する章の画像を検索
        image_info = None
        for img in chapter_images_sorted:
            if 'chapter_counter' in img and img['chapter_counter'] == chapter_counter:
                image_info = img
                break
            elif 'chapter' in img and img['chapter'] == f'chapter{chapter_counter}':
                image_info = img
                break
        
        if image_info:
            # 画像ID・URLを取得（新旧フォーマット対応）
            image_id = image_info.get('id', image_info.get('attachment_id'))
            image_url = image_info['url']
            
            # 独立した画像ブロックを作成（paragraphブロックに入らないよう注意）
            image_block = f'''

<!-- wp:image {{"id":{image_id},"className":"wp-block-image size-full"}} -->
<figure class="wp-block-image size-full"><img src="{image_url}" alt="第{chapter_counter}章 サムネイル画像" class="wp-image-{image_id}"/></figure>
<!-- /wp:image -->'''
            
            return original_h2 + image_block
        
        return original_h2
    
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