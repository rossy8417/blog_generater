#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress Client - H4 Compliance Fixed Version
Fixed to ensure H4 markdown converts to H4 HTML (not H5)
"""

import re

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

def convert_markdown_to_gutenberg_h4_compliant(markdown_content: str, debug: bool = False) -> str:
    """
    マークダウンをWordPressブロックエディタ形式に変換（H4コンプライアント版）
    H4 markdown (####) → H4 HTML (<h4>) に変換（H5 HTMLは使用しない）
    """
    content = ""
    lines = markdown_content.split('\n')
    i = 0
    
    # デバッグ情報収集用
    heading_info = []
    skipped_lines = []
    template_ids_found = []
    
    if debug:
        print("🔍 マークダウン→WordPress変換デバッグ開始（H4コンプライアント版）")
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
            
        # H2見出し（章見出しまたは小見出し）
        elif line.startswith('## '):
            heading_text = line[3:].strip()
            
            # テンプレート識別子チェック
            if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                template_ids_found.append(f"H2: {heading_text}")
            
            # 章見出し（第X章）はH2として変換、その他の小見出しはH3として変換
            if '第' in heading_text and '章' in heading_text:
                heading_info.append(f"H2章→H2: {heading_text}")
                content += f'<!-- wp:heading {{"level":2}} -->\n'
                content += f'<h2 class="wp-block-heading">{heading_text}</h2>\n'
                content += f'<!-- /wp:heading -->\n\n'
            else:
                heading_info.append(f"H2→H3: {heading_text}")
                content += f'<!-- wp:heading {{"level":3}} -->\n'
                content += f'<h3 class="wp-block-heading">{heading_text}</h3>\n'
                content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H3見出し
        elif line.startswith('### '):
            heading_text = line[4:].strip()
            
            # テンプレート識別子チェック
            if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                template_ids_found.append(f"H3: {heading_text}")
            
            heading_info.append(f"H3→H4: {heading_text}")
            content += f'<!-- wp:heading {{"level":4}} -->\n'
            content += f'<h4 class="wp-block-heading">{heading_text}</h4>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H4見出し（修正版：H4 HTMLに変換）
        elif line.startswith('#### '):
            heading_text = line[5:].strip()
            heading_info.append(f"H4→H4: {heading_text}")
            content += f'<!-- wp:heading {{"level":4}} -->\n'
            content += f'<h4 class="wp-block-heading">{heading_text}</h4>\n'
            content += f'<!-- /wp:heading -->\n\n'
            i += 1
            
        # H5見出し以降は段落として処理（President0要求の完全禁止）
        elif line.startswith('#####'):
            heading_text = line[5:].strip()
            paragraph_text = f"**{heading_text}**"
            content += f'<!-- wp:paragraph -->\n'
            content += f'<p>{format_text(paragraph_text)}</p>\n'
            content += f'<!-- /wp:paragraph -->\n\n'
            heading_info.append(f"H5→段落: {heading_text}")
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
        
        # H5タグの検証
        h5_count = content.count('<h5')
        if h5_count == 0:
            print("\n✅ H5コンプライアンス: H5タグなし")
        else:
            print(f"\n❌ H5コンプライアンス: {h5_count}個のH5タグ発見")
        
        print("🔍 変換デバッグ完了\n")
    
    return content