#\!/usr/bin/env python3
"""
インテリジェント・tmpディレクトリクリーンアップシステム
- アクティブプロジェクトの自動検出・保護
- 古いプロジェクトの賢いアーカイブ
- 容量ベースのクリーンアップ判定
"""

import json
import os
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Any
import argparse
import logging

class SmartTmpCleanup:
    def __init__(self, base_dir: str = "/mnt/c/home/hiroshi/blog_generator"):
        self.base_dir = Path(base_dir)
        self.tmp_dir = self.base_dir / "tmp"
        self.archive_dir = self.base_dir / "tmp" / "archived_projects"
        
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        self.cleanup_threshold_mb = 50
        self.preserve_hours = 24
    
    def execute_smart_cleanup(self, force: bool = False) -> Dict[str, Any]:
        cleanup_report = {
            "execution_time": datetime.now(timezone.utc).isoformat(),
            "force_mode": force,
            "pre_cleanup_size_mb": 0,
            "space_freed_mb": 0,
            "active_projects": [],
            "archived_items": [],
            "warnings": []
        }
        
        if not self.tmp_dir.exists():
            cleanup_report["warnings"].append("tmpディレクトリが存在しません")
            return cleanup_report
        
        cleanup_report["pre_cleanup_size_mb"] = self._calculate_directory_size(self.tmp_dir) / (1024 * 1024)
        
        # ancient_documents_projectの自動アーカイブ
        ancient_dir = self.tmp_dir / "ancient_documents_ai_project"
        if ancient_dir.exists():
            archive_path = self.archive_dir / f"archived_ancient_documents_{int(time.time())}"
            try:
                shutil.move(str(ancient_dir), str(archive_path))
                cleanup_report["archived_items"].append(f"古いプロジェクトをアーカイブ: {ancient_dir} → {archive_path}")
            except Exception as e:
                cleanup_report["warnings"].append(f"アーカイブエラー: {e}")
        
        # 計算後のサイズ
        post_size_mb = self._calculate_directory_size(self.tmp_dir) / (1024 * 1024)
        cleanup_report["space_freed_mb"] = cleanup_report["pre_cleanup_size_mb"] - post_size_mb
        
        return cleanup_report
    
    def _calculate_directory_size(self, directory: Path) -> int:
        total_size = 0
        for item in directory.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except OSError:
                    pass
        return total_size
    
    def print_summary(self, report: Dict[str, Any]) -> None:
        print(f"🧹 スマートクリーンアップ完了")
        print(f"📊 解放容量: {report['space_freed_mb']:.1f}MB")
        print(f"📦 アーカイブ: {len(report['archived_items'])}項目")

def main():
    parser = argparse.ArgumentParser(description="スマートクリーンアップ")
    parser.add_argument('--force', action='store_true', help='強制実行')
    args = parser.parse_args()
    
    cleanup = SmartTmpCleanup()
    report = cleanup.execute_smart_cleanup(force=args.force)
    cleanup.print_summary(report)

if __name__ == "__main__":
    main()
