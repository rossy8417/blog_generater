#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
出力ファイル自動整理スクリプト
ルートディレクトリに散らばったファイルを正しいディレクトリ構造に移動
"""

import os
import sys
import re
import shutil
import json
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from utils.output_manager import OutputManager

def organize_scattered_files():
    """散らばったファイルを自動整理"""
    
    print("🧹 散らばったファイルの自動整理を開始します...\n")
    
    manager = OutputManager()
    root_dir = project_root
    
    # 整理対象のファイルパターン
    target_patterns = [
        r'.*outline.*\.md$',
        r'.*complete_article.*\.md$',
        r'.*_eyecatch_.*\.(png < /dev/null | jpg)$',
        r'.*_thumbnail_.*\.(png|jpg)$',
        r'.*divided_intents.*\.json$',
        r'.*intent_analysis.*\.md$',
        r'.*_lead_.*\.md$',
        r'.*_summary_.*\.md$',
    ]
    
    moved_files = []
    
    # ルートディレクトリ内のファイルをチェック
    for file_path in root_dir.iterdir():
        if file_path.is_file():
            filename = file_path.name
            
            # 対象パターンにマッチするかチェック
            is_target = False
            for pattern in target_patterns:
                if re.match(pattern, filename, re.IGNORECASE):
                    is_target = True
                    break
            
            if not is_target:
                continue
            
            print(f"🔍 処理中: {filename}")
            
            try:
                # ファイル内容からメタデータを抽出
                if filename.endswith(('.md', '.json')):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    metadata = manager.extract_metadata_from_content(content, filename)
                else:
                    # バイナリファイルはファイル名からメタデータを抽出
                    metadata = manager.extract_metadata_from_content("", filename)
                
                # タイトルが取得できない場合は手動設定
                if not metadata.get('title'):
                    if 'AI' in filename and 'ルーチンワーク' in filename:
                        metadata['title'] = '【2024年最新】AI ルーチンワーク 負担軽減完全ガイド｜97%が実感した6つの実践法'
                    else:
                        metadata['title'] = 'Unknown_Article'
                
                # INT番号が取得できない場合はデフォルト
                if not metadata.get('int_number'):
                    metadata['int_number'] = 'INT-01'
                
                # 出力ディレクトリを生成
                output_dir = manager.generate_output_directory(metadata)
                
                # 新しいファイルパスを生成
                new_file_path = output_dir / filename
                
                # ファイルを移動
                shutil.move(str(file_path), str(new_file_path))
                moved_files.append({
                    'original': str(file_path),
                    'new': str(new_file_path),
                    'title': metadata.get('title', 'Unknown'),
                    'int_number': metadata.get('int_number', 'INT-01')
                })
                
                print(f"   ✅ 移動完了: {output_dir.name}/")
                
            except Exception as e:
                print(f"   ❌ 移動失敗: {e}")
    
    # 結果レポート
    print(f"\n📊 整理結果:")
    print(f"✅ 移動されたファイル: {len(moved_files)}個")
    
    if moved_files:
        print("\n📁 移動先一覧:")
        for item in moved_files:
            print(f"   {os.path.basename(item['original'])} → {item['int_number']}/")
    
    # メタデータファイルも作成
    for item in moved_files:
        metadata = {
            'title': item['title'],
            'int_number': item['int_number'],
            'timestamp': re.search(r'(\d{8}_\d{6})', item['new']).group(1) if re.search(r'(\d{8}_\d{6})', item['new']) else '',
            'organized_at': manager.extract_metadata_from_content("", "")['timestamp']
        }
        manager.create_metadata_file(metadata)
    
    print("\n✅ ファイル整理が完了しました！")
    return len(moved_files)

if __name__ == "__main__":
    try:
        moved_count = organize_scattered_files()
        print(f"\n🎉 整理完了\! {moved_count}個のファイルを整理しました")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
