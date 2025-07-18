#\!/usr/bin/env python3
"""
Boss1混乱防止システム
- 現在のプロジェクト情報の明確化
- 古いプロジェクト参照の防止
- プロジェクト境界の確立
"""

import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

class Boss1ConfusionPrevention:
    def __init__(self, base_dir: str = "/mnt/c/home/hiroshi/blog_generator"):
        self.base_dir = Path(base_dir)
        self.tmp_dir = self.base_dir / "tmp"
        self.archive_dir = self.base_dir / "tmp" / "archived_projects"
        
    def create_current_project_reference(self, project_id: str, keyword: str, project_type: str = "blog_article") -> None:
        """現在のプロジェクト参照ファイルを作成"""
        reference_content = f"""# 現在のプロジェクト情報 - Boss1参照用

⚠️ **重要**: このファイルは自動生成されます。手動編集禁止。

## 基本情報
- **プロジェクトID**: {project_id}
- **プロジェクトタイプ**: {project_type}
- **キーワード**: {keyword}
- **作成日時**: {datetime.now(timezone.utc).isoformat()}

## 作業ディレクトリ
- **出力ディレクトリ**: outputs/{project_id}/
- **一時作業領域**: tmp/project_{project_id}/

## 重要な注意事項
- 古いプロジェクト（ancient_documents等）の情報は参照しないでください
- 現在のプロジェクトのみに集中してください
- 不明な点がある場合は、President0に確認してください

## 実行フェーズ
- Phase1: 意図分析・アウトライン作成
- Phase2: 並行記事作成（Worker1-3）
- Phase3: 画像生成・WordPress投稿

---
**生成時刻**: {datetime.now(timezone.utc).isoformat()}
**システム**: Boss1ConfusionPrevention
"""
        
        reference_file = self.tmp_dir / "current_project_reference.md"
        try:
            with open(reference_file, 'w', encoding='utf-8') as f:
                f.write(reference_content)
            print(f"✅ Boss1参照ファイル作成: {reference_file}")
        except Exception as e:
            print(f"❌ Boss1参照ファイル作成エラー: {e}")
    
    def isolate_old_projects(self) -> Dict[str, Any]:
        """古いプロジェクトファイルの分離"""
        isolation_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "conflicts_found": [],
            "conflicts_resolved": [],
            "warnings": []
        }
        
        # 古いプロジェクトパターンを検出
        old_patterns = ["ancient_documents", "古文書", "古代文献"]
        
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        
        for pattern in old_patterns:
            for item in self.tmp_dir.glob(f"*{pattern}*"):
                if item.exists():
                    isolation_report["conflicts_found"].append(str(item))
                    
                    # アーカイブに移動
                    timestamp = int(datetime.now().timestamp())
                    archive_path = self.archive_dir / f"isolated_{item.name}_{timestamp}"
                    
                    try:
                        if item.is_dir():
                            shutil.move(str(item), str(archive_path))
                        else:
                            shutil.move(str(item), str(archive_path))
                        isolation_report["conflicts_resolved"].append(f"{item} → {archive_path}")
                    except Exception as e:
                        isolation_report["warnings"].append(f"移動エラー {item}: {str(e)}")
        
        return isolation_report
    
    def clear_worker_confusion(self) -> Dict[str, Any]:
        """Worker混乱要因の除去"""
        clear_report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "cleared_items": [],
            "preserved_items": []
        }
        
        # Worker関連の古いファイルパターン
        worker_patterns = ["worker1_", "worker2_", "worker3_", "boss1_"]
        
        for pattern in worker_patterns:
            for item in self.tmp_dir.glob(f"{pattern}*"):
                if item.exists():
                    # ファイルの年齢チェック（24時間以上古い）
                    file_age_hours = (datetime.now().timestamp() - item.stat().st_mtime) / 3600
                    
                    if file_age_hours > 24:
                        try:
                            if item.is_dir():
                                shutil.rmtree(item)
                            else:
                                item.unlink()
                            clear_report["cleared_items"].append(str(item))
                        except Exception as e:
                            clear_report["preserved_items"].append(f"削除失敗 {item}: {str(e)}")
                    else:
                        clear_report["preserved_items"].append(f"最近のファイル: {item}")
        
        return clear_report
    
    def generate_prevention_summary(self, project_id: str, keyword: str) -> None:
        """混乱防止処理のサマリー表示"""
        print("\n" + "="*60)
        print("🛡️ Boss1混乱防止システム実行結果")
        print("="*60)
        
        # 古いプロジェクト分離
        isolation_report = self.isolate_old_projects()
        
        # Worker混乱要因除去
        clear_report = self.clear_worker_confusion()
        
        # 現在プロジェクト参照作成
        self.create_current_project_reference(project_id, keyword)
        
        print(f"\n📊 現在のプロジェクト: {project_id}")
        print(f"🔍 キーワード: {keyword}")
        
        print(f"\n🔧 古いプロジェクト分離:")
        print(f"  - 検出: {len(isolation_report['conflicts_found'])}項目")
        print(f"  - 解決: {len(isolation_report['conflicts_resolved'])}項目")
        
        print(f"\n🧹 Worker混乱要因除去:")
        print(f"  - 除去: {len(clear_report['cleared_items'])}項目")
        print(f"  - 保持: {len(clear_report['preserved_items'])}項目")
        
        print(f"\n✅ Boss1参照ファイル: tmp/current_project_reference.md")
        print("="*60)

def main():
    parser = argparse.ArgumentParser(description="Boss1混乱防止システム")
    parser.add_argument('project_id', help='現在のプロジェクトID')
    parser.add_argument('keyword', help='プロジェクトキーワード')
    parser.add_argument('--type', default='blog_article', help='プロジェクトタイプ')
    
    args = parser.parse_args()
    
    prevention = Boss1ConfusionPrevention()
    prevention.generate_prevention_summary(args.project_id, args.keyword)

if __name__ == "__main__":
    main()
