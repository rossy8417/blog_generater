#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記事検証CLIツール
投稿前に記事の見出し構造を検証
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from scripts.heading_validator import validate_article_file

def main():
    """メイン処理"""
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  python scripts/validate_article.py <記事ファイル.md>")
        print("  python scripts/validate_article.py outputs/final_articles/記事名-INT-01/complete_article.md")
        sys.exit(1)
    
    file_path = sys.argv[1]
    
    print("🔍 記事の見出し構造を検証しています...")
    print(f"📁 ファイル: {file_path}")
    print("-" * 60)
    
    success = validate_article_file(file_path)
    
    if success:
        print("-" * 60)
        print("✅ 検証完了: 記事は投稿可能です")
        sys.exit(0)
    else:
        print("-" * 60)
        print("❌ 検証失敗: 問題を修正してから投稿してください")
        sys.exit(1)

if __name__ == "__main__":
    main()
