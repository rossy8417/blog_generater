#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Output Manager - ブログ記事出力時の自動分類管理
ファイル出力時に正しいディレクトリ構造（ブログタイトル/日付/INT番号）で自動分類
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

class OutputManager:
    """ブログ記事出力の自動分類管理クラス"""
    
    def __init__(self, base_outputs_dir: str = "outputs"):
        """
        初期化
        
        Args:
            base_outputs_dir: 基本出力ディレクトリ
        """
        self.base_outputs_dir = Path(base_outputs_dir)
        self.base_outputs_dir.mkdir(exist_ok=True)
    
    def extract_metadata_from_outline(self, outline_path: str) -> Dict[str, str]:
        """
        アウトラインファイルからメタデータを抽出
        
        Args:
            outline_path: アウトラインファイルのパス
            
        Returns:
            メタデータ辞書 (title, date, int_number)
        """
        metadata = {
            'title': '',
            'date': '',
            'int_number': '',
            'timestamp': ''
        }
        
        try:
            if not os.path.exists(outline_path):
                return metadata
            
            with open(outline_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # タイトル抽出 (Title: 行から)
            title_match = re.search(r'^Title:\s*(.+)$', content, re.MULTILINE)
            if title_match:
                metadata['title'] = title_match.group(1).strip()
            
            # ファイル名から日付とINT番号を抽出
            filename = os.path.basename(outline_path)
            
            # タイムスタンプ抽出 (YYYYMMDD_HHMMSS)
            timestamp_match = re.search(r'(\d{8}_\d{6})', filename)
            if timestamp_match:
                metadata['timestamp'] = timestamp_match.group(1)
                # 日付部分を YYYY-MM-DD 形式に変換
                date_part = timestamp_match.group(1)[:8]
                metadata['date'] = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
            
            # INT番号抽出
            int_match = re.search(r'INT-(\d+)', filename)
            if int_match:
                metadata['int_number'] = f"INT-{int_match.group(1)}"
            
            return metadata
            
        except Exception as e:
            print(f"Warning: Failed to extract metadata from outline: {e}")
            return metadata
    
    def extract_metadata_from_content(self, content: str, filename: str = "") -> Dict[str, str]:
        """
        コンテンツからメタデータを抽出
        
        Args:
            content: ファイル内容
            filename: ファイル名（タイムスタンプ・INT番号抽出用）
            
        Returns:
            メタデータ辞書
        """
        metadata = {
            'title': '',
            'date': '',
            'int_number': '',
            'timestamp': ''
        }
        
        try:
            # タイトル抽出（複数パターン）
            title_patterns = [
                r'^Title:\s*(.+)$',          # Title: 形式
                r'^#\s*(.+)$',               # Markdown H1
                r'^\*\*Title:\*\*\s*(.+)$',  # **Title:** 形式
            ]
            
            for pattern in title_patterns:
                title_match = re.search(pattern, content, re.MULTILINE)
                if title_match:
                    metadata['title'] = title_match.group(1).strip()
                    break
            
            # ファイル名から日付とINT番号を抽出
            if filename:
                # タイムスタンプ抽出
                timestamp_match = re.search(r'(\d{8}_\d{6})', filename)
                if timestamp_match:
                    metadata['timestamp'] = timestamp_match.group(1)
                    date_part = timestamp_match.group(1)[:8]
                    metadata['date'] = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:8]}"
                
                # INT番号抽出
                int_match = re.search(r'INT-(\d+)', filename)
                if int_match:
                    metadata['int_number'] = f"INT-{int_match.group(1)}"
            
            # 現在の日時を使用（タイムスタンプが取得できない場合）
            if not metadata['date']:
                now = datetime.now()
                metadata['date'] = now.strftime('%Y-%m-%d')
                metadata['timestamp'] = now.strftime('%Y%m%d_%H%M%S')
            
            return metadata
            
        except Exception as e:
            print(f"Warning: Failed to extract metadata from content: {e}")
            return metadata
    
    def generate_output_directory(self, metadata: Dict[str, str]) -> Path:
        """
        メタデータから出力ディレクトリパスを生成
        
        Args:
            metadata: メタデータ辞書
            
        Returns:
            出力ディレクトリパス
        """
        # デフォルト値設定
        title = metadata.get('title', 'Unknown_Article').strip()
        date = metadata.get('date', datetime.now().strftime('%Y-%m-%d'))
        int_number = metadata.get('int_number', 'INT-01')
        
        # ファイル名として使用できない文字を置換
        safe_title = self._sanitize_filename(title)
        
        # ディレクトリパス生成: outputs/ブログタイトル/日付/INT番号/
        output_dir = self.base_outputs_dir / safe_title / date / int_number
        output_dir.mkdir(parents=True, exist_ok=True)
        
        return output_dir
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        ファイル名・ディレクトリ名として安全な文字列に変換
        
        Args:
            filename: 元のファイル名
            
        Returns:
            サニタイズされたファイル名
        """
        # 使用できない文字を置換
        unsafe_chars = r'[<>:"/\\|?*]'
        safe_name = re.sub(unsafe_chars, '_', filename)
        
        # 連続するアンダースコアを単一に
        safe_name = re.sub(r'_{2,}', '_', safe_name)
        
        # 前後の空白・アンダースコアを削除
        safe_name = safe_name.strip('_ ')
        
        # 空文字の場合はデフォルト名
        if not safe_name:
            safe_name = 'Unknown_Article'
        
        # 長すぎる場合は短縮
        if len(safe_name) > 50:
            safe_name = safe_name[:50].rstrip('_')
        
        return safe_name
    
    def get_output_filepath(self, metadata: Dict[str, str], file_type: str, chapter: Optional[int] = None) -> str:
        """
        出力ファイルのフルパスを生成
        
        Args:
            metadata: メタデータ辞書
            file_type: ファイルタイプ (outline, article, eyecatch, thumbnail, etc.)
            chapter: チャプター番号（サムネイル等で使用）
            
        Returns:
            出力ファイルパス
        """
        output_dir = self.generate_output_directory(metadata)
        timestamp = metadata.get('timestamp', datetime.now().strftime('%Y%m%d_%H%M%S'))
        int_number = metadata.get('int_number', 'INT-01')
        
        # ファイル名生成
        if file_type == 'outline':
            filename = f"{timestamp}_outline_{int_number}.md"
        elif file_type == 'complete_article':
            filename = f"{timestamp}_complete_article_{int_number}.md"
        elif file_type == 'article_chapter':
            filename = f"{timestamp}_article_{int_number}_chapter{chapter}.md"
        elif file_type == 'eyecatch':
            filename = f"{timestamp}_eyecatch_{int_number}.png"
        elif file_type == 'thumbnail':
            filename = f"{timestamp}_thumbnail_{int_number}_chapter{chapter}.png"
        elif file_type == 'lead_summary':
            filename = f"{timestamp}_lead_summary_{int_number}.md"
        elif file_type == 'divided_intents':
            filename = f"{timestamp}_divided_intents.json"
        else:
            filename = f"{timestamp}_{file_type}_{int_number}"
        
        return str(output_dir / filename)
    
    def save_content(self, content: str, metadata: Dict[str, str], file_type: str, chapter: Optional[int] = None) -> str:
        """
        コンテンツを適切なディレクトリに保存
        
        Args:
            content: 保存するコンテンツ
            metadata: メタデータ辞書
            file_type: ファイルタイプ
            chapter: チャプター番号
            
        Returns:
            保存されたファイルパス
        """
        filepath = self.get_output_filepath(metadata, file_type, chapter)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save {file_type}: {e}")
            return ""
    
    def save_binary(self, data: bytes, metadata: Dict[str, str], file_type: str, chapter: Optional[int] = None) -> str:
        """
        バイナリデータを適切なディレクトリに保存
        
        Args:
            data: 保存するバイナリデータ
            metadata: メタデータ辞書
            file_type: ファイルタイプ
            chapter: チャプター番号
            
        Returns:
            保存されたファイルパス
        """
        filepath = self.get_output_filepath(metadata, file_type, chapter)
        
        try:
            with open(filepath, 'wb') as f:
                f.write(data)
            
            print(f"✅ Saved: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"❌ Failed to save {file_type}: {e}")
            return ""
    
    def create_metadata_file(self, metadata: Dict[str, str]) -> str:
        """
        メタデータファイルを作成
        
        Args:
            metadata: メタデータ辞書
            
        Returns:
            メタデータファイルパス
        """
        output_dir = self.generate_output_directory(metadata)
        metadata_path = output_dir / "metadata.json"
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Metadata saved: {metadata_path}")
            return str(metadata_path)
            
        except Exception as e:
            print(f"❌ Failed to save metadata: {e}")
            return ""

# ユーティリティ関数
def get_output_manager() -> OutputManager:
    """
    OutputManagerのシングルトンインスタンスを取得
    
    Returns:
        OutputManagerインスタンス
    """
    return OutputManager()

def auto_categorize_output(content: str, filename: str, file_type: str, chapter: Optional[int] = None) -> str:
    """
    コンテンツを自動分類して保存
    
    Args:
        content: 保存するコンテンツ
        filename: 元のファイル名
        file_type: ファイルタイプ
        chapter: チャプター番号
        
    Returns:
        保存されたファイルパス
    """
    manager = get_output_manager()
    metadata = manager.extract_metadata_from_content(content, filename)
    return manager.save_content(content, metadata, file_type, chapter)

def auto_categorize_binary(data: bytes, filename: str, file_type: str, chapter: Optional[int] = None) -> str:
    """
    バイナリデータを自動分類して保存
    
    Args:
        data: 保存するバイナリデータ
        filename: 元のファイル名
        file_type: ファイルタイプ
        chapter: チャプター番号
        
    Returns:
        保存されたファイルパス
    """
    manager = get_output_manager()
    # バイナリデータの場合はファイル名からメタデータを抽出
    metadata = manager.extract_metadata_from_content("", filename)
    return manager.save_binary(data, metadata, file_type, chapter)

# テスト用
if __name__ == "__main__":
    # テスト実行
    manager = OutputManager()
    
    # テストメタデータ
    test_metadata = {
        'title': '【年齢別】生成AI教育完全ガイド｜3歳〜18歳の発達段階別活用法',
        'date': '2025-06-19',
        'int_number': 'INT-02',
        'timestamp': '20250619_145151'
    }
    
    # ディレクトリ作成テスト
    output_dir = manager.generate_output_directory(test_metadata)
    print(f"Generated directory: {output_dir}")
    
    # ファイルパス生成テスト
    outline_path = manager.get_output_filepath(test_metadata, 'outline')
    print(f"Outline path: {outline_path}")
    
    eyecatch_path = manager.get_output_filepath(test_metadata, 'eyecatch')
    print(f"Eyecatch path: {eyecatch_path}")
    
    thumbnail_path = manager.get_output_filepath(test_metadata, 'thumbnail', chapter=1)
    print(f"Thumbnail path: {thumbnail_path}")