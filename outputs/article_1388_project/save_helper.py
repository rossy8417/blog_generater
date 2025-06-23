#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡単保存ヘルパー - outputsディレクトリへの確実な保存
"""

import os
import sys
import re
from pathlib import Path

# プロジェクトルートを特定
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from utils.output_manager import OutputManager

def save_safely(content, filename="auto_generated.md", file_type="article"):
    """確実にoutputsディレクトリに保存"""
    
    manager = OutputManager()
    
    # メタデータを抽出/推測
    metadata = manager.extract_metadata_from_content(content, filename)
    
    # タイトルが取得できない場合は内容から推測
    if not metadata.get('title'):
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            metadata['title'] = h1_match.group(1).strip()
        elif 'AI' in content and 'ルーチンワーク' in content:
            metadata['title'] = '【2024年最新】AI ルーチンワーク 負担軽減完全ガイド｜97%が実感した6つの実践法'
        else:
            metadata['title'] = 'Auto_Generated_Article'
    
    # INT番号が取得できない場合はデフォルト
    if not metadata.get('int_number'):
        metadata['int_number'] = 'INT-01'
    
    # 保存実行
    return manager.save_content(content, metadata, file_type)

# 使いやすいエイリアス
def write_article(content, title=None, int_number=None):
    """記事を保存"""
    filename = ""
    if title and int_number:
        filename = f"article_{int_number}.md"
    return save_safely(content, filename, "complete_article")

def write_outline(content, title=None, int_number=None):
    """アウトラインを保存"""
    filename = ""
    if title and int_number:
        filename = f"outline_{int_number}.md"
    return save_safely(content, filename, "outline")

if __name__ == "__main__":
    # テスト
    test_content = """# テスト記事

これはテスト用の記事です。
"""
    saved_path = save_safely(test_content, "test.md", "article")
    print(f"✅ 保存完了: {saved_path}")