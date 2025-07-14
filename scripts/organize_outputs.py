#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Blog Generator - Output File Organizer
散らばったファイルを適切なディレクトリに自動整理するスクリプト

Usage:
    python organize_outputs.py
    
Functions:
    - 散らばったファイルの自動分類・移動
    - プロジェクト別ディレクトリ構造の整理
    - 重複ファイルの統合
    - 空ディレクトリの削除
    - 整理結果の分析・レポート
"""

import os
import shutil
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

class OutputOrganizer:
    """出力ファイル自動整理クラス"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.outputs_dir = self.project_root / "outputs"
        self.misc_dir = self.outputs_dir / "misc_files"
        self.reports_dir = self.outputs_dir / "reports"
        
        # 保護対象ファイル（削除・移動禁止）
        self.protected_files = {
            "CLAUDE.md",
            "README.md", 
            "codeediter_example.txt",
            "requirements.txt",
            ".env",
            ".gitignore"
        }
        
        # 保護対象ディレクトリ（変更禁止）
        self.protected_dirs = {
            "scripts",
            "templates", 
            "docs",
            "utils",
            "config",
            "Claude-Code-Blog-communication",
            ".git"
        }
        
        # 移動対象ファイルパターン
        self.file_patterns = {
            "temp_files": [
                r".*_temp\..*",
                r".*_tmp\..*", 
                r"temp_.*",
                r"tmp_.*"
            ],
            "backup_files": [
                r".*\.backup",
                r".*_backup\..*",
                r"backup_.*"
            ],
            "working_files": [
                r"current_.*\.txt",
                r".*_example\.txt",
                r"final_.*\.txt",
                r".*_check\.txt"
            ],
            "misc_images": [
                r"eyecatch_\d+_\d+.*\.(png|jpg|jpeg)",
                r"\d{8}_.*\.jpg",
                r".*_optimized\.(png|jpg|jpeg)"
            ]
        }
        
        self.stats = {
            "files_moved": 0,
            "directories_created": 0,
            "duplicates_removed": 0,
            "empty_dirs_removed": 0,
            "total_size_before": 0,
            "total_size_after": 0
        }

    def organize_all(self) -> Dict:
        """全ファイル整理を実行"""
        print("🚀 Blog Generator - 自動ファイル整理開始")
        print("=" * 50)
        
        # 事前サイズ計算
        self.stats["total_size_before"] = self._calculate_total_size()
        
        # 必要ディレクトリ作成
        self._create_required_directories()
        
        # 散らばったファイルの整理
        self._organize_scattered_files()
        
        # プロジェクトディレクトリの整理
        self._organize_project_directories()
        
        # 重複ファイルの処理
        self._handle_duplicate_files()
        
        # 空ディレクトリの削除
        self._remove_empty_directories()
        
        # 事後サイズ計算
        self.stats["total_size_after"] = self._calculate_total_size()
        
        # 結果レポート生成
        report = self._generate_report()
        
        print("\n✅ 自動ファイル整理完了!")
        print(f"📊 詳細レポート: {report['report_file']}")
        
        return report

    def _create_required_directories(self):
        """必要なディレクトリを作成"""
        required_dirs = [
            self.outputs_dir,
            self.misc_dir,
            self.reports_dir
        ]
        
        for dir_path in required_dirs:
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.stats["directories_created"] += 1
                print(f"📁 ディレクトリ作成: {dir_path.relative_to(self.project_root)}")

    def _organize_scattered_files(self):
        """ルートディレクトリの散らばったファイルを整理"""
        print("\n📋 散らばったファイルの整理中...")
        
        for file_path in self.project_root.iterdir():
            if file_path.is_file() and file_path.name not in self.protected_files:
                target_dir = self._determine_target_directory(file_path)
                if target_dir:
                    self._move_file_safely(file_path, target_dir)

    def _determine_target_directory(self, file_path: Path) -> Path:
        """ファイルの移動先ディレクトリを決定"""
        file_name = file_path.name
        
        # パターンマッチングで分類
        for category, patterns in self.file_patterns.items():
            for pattern in patterns:
                if re.match(pattern, file_name, re.IGNORECASE):
                    return self.misc_dir
        
        # ファイル拡張子による分類
        suffix = file_path.suffix.lower()
        
        if suffix in ['.md']:
            # プロジェクト関連のmdファイルかチェック
            if self._is_project_file(file_path):
                return self._find_project_directory(file_path)
            else:
                return self.misc_dir
                
        elif suffix in ['.txt']:
            # 作業ファイルはmisc_filesへ
            return self.misc_dir
            
        elif suffix in ['.jpg', '.jpeg', '.png']:
            # 画像ファイルの処理
            if self._is_project_image(file_path):
                return self._find_project_directory(file_path)
            else:
                return self.misc_dir
        
        # その他のファイル
        return self.misc_dir

    def _is_project_file(self, file_path: Path) -> bool:
        """プロジェクト関連ファイルかどうか判定"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # 最初の1000文字をチェック
                
            # プロジェクト関連キーワード
            project_keywords = [
                'INT-01', 'INT-02', 'INT-03',
                'chapter1', 'chapter2', 'chapter3',
                'outline_content', 'metadata.json'
            ]
            
            return any(keyword in content for keyword in project_keywords)
        except:
            return False

    def _is_project_image(self, file_path: Path) -> bool:
        """プロジェクト関連画像かどうか判定"""
        file_name = file_path.name
        
        # プロジェクト画像のパターン
        project_patterns = [
            r'.*chapter\d+\.jpg',
            r'.*eyecatch.*\.jpg',
            r'.*thumbnail.*\.jpg'
        ]
        
        return any(re.match(pattern, file_name, re.IGNORECASE) 
                  for pattern in project_patterns)

    def _find_project_directory(self, file_path: Path) -> Path:
        """ファイルに適したプロジェクトディレクトリを探す"""
        # 既存のプロジェクトディレクトリを検索
        project_dirs = list(self.outputs_dir.glob("*-INT-*"))
        
        if project_dirs:
            # 最新のプロジェクトディレクトリに配置
            return sorted(project_dirs, key=lambda x: x.stat().st_mtime)[-1]
        else:
            # プロジェクトディレクトリがない場合はmisc_filesへ
            return self.misc_dir

    def _organize_project_directories(self):
        """プロジェクトディレクトリ内の整理"""
        print("\n🗂️  プロジェクトディレクトリの整理中...")
        
        project_dirs = list(self.outputs_dir.glob("*-INT-*"))
        
        for project_dir in project_dirs:
            self._organize_single_project(project_dir)

    def _organize_single_project(self, project_dir: Path):
        """単一プロジェクトディレクトリの整理"""
        print(f"   📁 {project_dir.name} を整理中...")
        
        # 入れ子構造の修正
        self._fix_nested_structure(project_dir)
        
        # ファイル名の正規化
        self._normalize_file_names(project_dir)

    def _fix_nested_structure(self, project_dir: Path):
        """入れ子になったディレクトリ構造を修正"""
        for item in project_dir.iterdir():
            if item.is_dir() and item.name == project_dir.name:
                # 同名ディレクトリが入れ子になっている場合
                print(f"   🔧 入れ子構造を修正: {item.name}")
                
                for nested_file in item.iterdir():
                    target_path = project_dir / nested_file.name
                    if not target_path.exists():
                        shutil.move(str(nested_file), str(target_path))
                        self.stats["files_moved"] += 1
                
                # 空になったディレクトリを削除
                if not any(item.iterdir()):
                    shutil.rmtree(item)

    def _normalize_file_names(self, project_dir: Path):
        """ファイル名の正規化"""
        for file_path in project_dir.iterdir():
            if file_path.is_file():
                old_name = file_path.name
                new_name = self._normalize_filename(old_name)
                
                if old_name != new_name:
                    new_path = project_dir / new_name
                    if not new_path.exists():
                        file_path.rename(new_path)
                        print(f"   📝 ファイル名正規化: {old_name} → {new_name}")

    def _normalize_filename(self, filename: str) -> str:
        """ファイル名を正規化"""
        # 不要な文字の削除
        filename = re.sub(r'[^\w\-_.\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', '_', filename)
        
        # 連続するアンダースコアを単一に
        filename = re.sub(r'_+', '_', filename)
        
        # 先頭・末尾のアンダースコア削除
        filename = filename.strip('_')
        
        return filename

    def _handle_duplicate_files(self):
        """重複ファイルの処理"""
        print("\n🔍 重複ファイルの検出・処理中...")
        
        file_hashes = {}
        
        for file_path in self.outputs_dir.rglob("*"):
            if file_path.is_file():
                file_hash = self._calculate_file_hash(file_path)
                
                if file_hash in file_hashes:
                    # 重複ファイル発見
                    original_file = file_hashes[file_hash]
                    print(f"   🔄 重複ファイル削除: {file_path.relative_to(self.project_root)}")
                    file_path.unlink()
                    self.stats["duplicates_removed"] += 1
                else:
                    file_hashes[file_hash] = file_path

    def _calculate_file_hash(self, file_path: Path) -> str:
        """ファイルハッシュを計算"""
        import hashlib
        
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return hashlib.md5(content).hexdigest()
        except:
            return str(file_path.stat().st_size)  # サイズをハッシュ代替

    def _remove_empty_directories(self):
        """空のディレクトリを削除"""
        print("\n🗑️  空ディレクトリの削除中...")
        
        for dir_path in list(self.outputs_dir.rglob("*")):
            if dir_path.is_dir() and dir_path != self.outputs_dir:
                try:
                    if not any(dir_path.iterdir()):
                        dir_path.rmdir()
                        self.stats["empty_dirs_removed"] += 1
                        print(f"   📁 空ディレクトリ削除: {dir_path.relative_to(self.project_root)}")
                except:
                    pass

    def _move_file_safely(self, source: Path, target_dir: Path):
        """ファイルを安全に移動"""
        if not target_dir.exists():
            target_dir.mkdir(parents=True, exist_ok=True)
        
        target_path = target_dir / source.name
        
        # 同名ファイルが存在する場合はタイムスタンプ付きにリネーム
        if target_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            stem = target_path.stem
            suffix = target_path.suffix
            target_path = target_dir / f"{stem}_{timestamp}{suffix}"
        
        try:
            shutil.move(str(source), str(target_path))
            self.stats["files_moved"] += 1
            print(f"   📤 移動: {source.name} → {target_dir.relative_to(self.project_root)}")
        except Exception as e:
            print(f"   ❌ 移動失敗: {source.name} - {e}")

    def _calculate_total_size(self) -> int:
        """総ファイルサイズを計算"""
        total_size = 0
        for file_path in self.project_root.rglob("*"):
            if file_path.is_file():
                try:
                    total_size += file_path.stat().st_size
                except:
                    pass
        return total_size

    def _generate_report(self) -> Dict:
        """整理結果レポートを生成"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_dir / f"organize_report_{timestamp}.json"
        
        # サイズ変化の計算
        size_reduction = self.stats["total_size_before"] - self.stats["total_size_after"]
        reduction_percentage = (size_reduction / self.stats["total_size_before"] * 100) if self.stats["total_size_before"] > 0 else 0
        
        report_data = {
            "timestamp": timestamp,
            "summary": {
                "files_moved": self.stats["files_moved"],
                "directories_created": self.stats["directories_created"], 
                "duplicates_removed": self.stats["duplicates_removed"],
                "empty_dirs_removed": self.stats["empty_dirs_removed"]
            },
            "storage": {
                "size_before_mb": round(self.stats["total_size_before"] / (1024*1024), 2),
                "size_after_mb": round(self.stats["total_size_after"] / (1024*1024), 2),
                "reduction_mb": round(size_reduction / (1024*1024), 2),
                "reduction_percentage": round(reduction_percentage, 2)
            },
            "directories": {
                "outputs_structure": self._get_directory_structure()
            }
        }
        
        # レポートファイル保存
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        # コンソール出力
        self._print_summary_report(report_data)
        
        return {
            "report_file": str(report_file),
            "stats": report_data
        }

    def _get_directory_structure(self) -> Dict:
        """ディレクトリ構造を取得"""
        structure = {}
        
        for item in self.outputs_dir.iterdir():
            if item.is_dir():
                file_count = len(list(item.rglob("*")))
                structure[item.name] = {
                    "files": file_count,
                    "size_mb": round(sum(f.stat().st_size for f in item.rglob("*") if f.is_file()) / (1024*1024), 2)
                }
        
        return structure

    def _print_summary_report(self, report_data: Dict):
        """サマリーレポートをコンソール出力"""
        print("\n" + "="*50)
        print("📊 整理結果サマリー")
        print("="*50)
        
        summary = report_data["summary"]
        storage = report_data["storage"]
        
        print(f"📁 移動ファイル数: {summary['files_moved']:,}")
        print(f"📂 作成ディレクトリ数: {summary['directories_created']:,}")
        print(f"🔄 削除重複ファイル数: {summary['duplicates_removed']:,}")
        print(f"🗑️  削除空ディレクトリ数: {summary['empty_dirs_removed']:,}")
        print(f"💾 容量削減: {storage['reduction_mb']:.1f}MB ({storage['reduction_percentage']:.1f}%)")
        
        print("\n📋 ディレクトリ構造:")
        for dir_name, info in report_data["directories"]["outputs_structure"].items():
            print(f"   {dir_name}: {info['files']}ファイル ({info['size_mb']:.1f}MB)")

def main():
    """メイン実行関数"""
    organizer = OutputOrganizer()
    result = organizer.organize_all()
    return result

if __name__ == "__main__":
    main()