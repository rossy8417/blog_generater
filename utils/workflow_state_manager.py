#!/usr/bin/env python3
"""
ワークフロー状態永続化システム
進行中の作業状態を永続化し、障害復旧時に継続可能にする
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
import fcntl
import logging

class WorkflowStateManager:
    """ワークフロー状態の永続化管理"""
    
    def __init__(self, state_dir: str = "tmp/workflow_states"):
        self.state_dir = Path(state_dir)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.lock_timeout = 30  # 30秒でロックタイムアウト
        
        # ログ設定
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def create_project_state(self, project_id: str, keyword: str, 
                           metadata: Optional[Dict] = None) -> Dict:
        """新規プロジェクト状態を作成"""
        state = {
            "project_id": project_id,
            "keyword": keyword,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "current_phase": "Phase0_initialization",
            "overall_status": "initialized",
            "phases": {
                "Phase1": {
                    "status": "pending",
                    "tasks": {
                        "intent_analysis": {"status": "pending", "started_at": None, "completed_at": None},
                        "intent_division": {"status": "pending", "started_at": None, "completed_at": None},
                        "outline_generation": {"status": "pending", "started_at": None, "completed_at": None}
                    }
                },
                "Phase2": {
                    "status": "pending",
                    "tasks": {
                        "chapter1_2_writing": {"status": "pending", "assigned_to": "worker1", "started_at": None, "completed_at": None},
                        "chapter3_4_writing": {"status": "pending", "assigned_to": "worker2", "started_at": None, "completed_at": None},
                        "chapter5_6_writing": {"status": "pending", "assigned_to": "worker3", "started_at": None, "completed_at": None},
                        "lead_generation": {"status": "pending", "assigned_to": "boss1", "started_at": None, "completed_at": None},
                        "summary_generation": {"status": "pending", "assigned_to": "boss1", "started_at": None, "completed_at": None},
                        "article_integration": {"status": "pending", "assigned_to": "boss1", "started_at": None, "completed_at": None}
                    }
                },
                "Phase3": {
                    "status": "pending",
                    "tasks": {
                        "eyecatch_generation": {"status": "pending", "assigned_to": "worker1", "started_at": None, "completed_at": None},
                        "thumbnail_1_3_generation": {"status": "pending", "assigned_to": "worker2", "started_at": None, "completed_at": None},
                        "thumbnail_4_6_generation": {"status": "pending", "assigned_to": "worker3", "started_at": None, "completed_at": None},
                        "wordpress_posting": {"status": "pending", "assigned_to": "boss1", "started_at": None, "completed_at": None}
                    }
                }
            },
            "file_paths": {
                "output_directory": f"outputs/{project_id}",
                "intent_analysis": None,
                "outline": None,
                "chapters": {},
                "images": {},
                "complete_article": None
            },
            "error_log": [],
            "retry_count": 0,
            "last_checkpoint": None,
            "metadata": metadata or {}
        }
        
        self._save_state(project_id, state)
        self.logger.info(f"プロジェクト状態作成: {project_id}")
        return state
    
    def update_phase_status(self, project_id: str, phase: str, status: str) -> bool:
        """フェーズステータス更新"""
        state = self.load_state(project_id)
        if not state:
            self.logger.error(f"プロジェクト状態が見つかりません: {project_id}")
            return False
        
        if phase in state["phases"]:
            state["phases"][phase]["status"] = status
            state["current_phase"] = phase
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            if status == "in_progress":
                state["phases"][phase]["started_at"] = datetime.now(timezone.utc).isoformat()
            elif status == "completed":
                state["phases"][phase]["completed_at"] = datetime.now(timezone.utc).isoformat()
                # 次のフェーズをpendingからreadyに変更
                self._advance_to_next_phase(state, phase)
            
            self._save_state(project_id, state)
            self.logger.info(f"フェーズ更新: {project_id} - {phase}: {status}")
            return True
        
        return False
    
    def update_task_status(self, project_id: str, phase: str, task: str, 
                          status: str, assigned_to: Optional[str] = None) -> bool:
        """タスクステータス更新"""
        state = self.load_state(project_id)
        if not state:
            return False
        
        if phase in state["phases"] and task in state["phases"][phase]["tasks"]:
            task_data = state["phases"][phase]["tasks"][task]
            task_data["status"] = status
            
            if assigned_to:
                task_data["assigned_to"] = assigned_to
            
            if status == "in_progress":
                task_data["started_at"] = datetime.now(timezone.utc).isoformat()
            elif status == "completed":
                task_data["completed_at"] = datetime.now(timezone.utc).isoformat()
            elif status == "failed":
                # エラーログに記録
                error = {
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "phase": phase,
                    "task": task,
                    "error_type": "task_failure",
                    "assigned_to": assigned_to
                }
                state["error_log"].append(error)
            
            state["updated_at"] = datetime.now(timezone.utc).isoformat()
            
            # フェーズ内の全タスク完了チェック
            if self._all_tasks_completed(state["phases"][phase]):
                self.update_phase_status(project_id, phase, "completed")
            
            self._save_state(project_id, state)
            self.logger.info(f"タスク更新: {project_id} - {phase}/{task}: {status}")
            return True
        
        return False
    
    def add_file_path(self, project_id: str, file_type: str, file_path: str) -> bool:
        """ファイルパス記録"""
        state = self.load_state(project_id)
        if not state:
            return False
        
        if file_type in ["chapters", "images"]:
            if file_type not in state["file_paths"]:
                state["file_paths"][file_type] = {}
            # ファイル名から章番号やタイプを推定
            filename = os.path.basename(file_path)
            state["file_paths"][file_type][filename] = file_path
        else:
            state["file_paths"][file_type] = file_path
        
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save_state(project_id, state)
        return True
    
    def record_error(self, project_id: str, error_type: str, error_message: str, 
                    context: Optional[Dict] = None) -> bool:
        """エラー記録"""
        state = self.load_state(project_id)
        if not state:
            return False
        
        error = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error_type": error_type,
            "message": error_message,
            "context": context or {}
        }
        
        state["error_log"].append(error)
        state["retry_count"] += 1
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        self._save_state(project_id, state)
        self.logger.error(f"エラー記録: {project_id} - {error_type}: {error_message}")
        return True
    
    def create_checkpoint(self, project_id: str, checkpoint_name: str, 
                         checkpoint_data: Optional[Dict] = None) -> bool:
        """チェックポイント作成"""
        state = self.load_state(project_id)
        if not state:
            return False
        
        checkpoint = {
            "name": checkpoint_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "phase": state["current_phase"],
            "data": checkpoint_data or {}
        }
        
        state["last_checkpoint"] = checkpoint
        state["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        self._save_state(project_id, state)
        self.logger.info(f"チェックポイント作成: {project_id} - {checkpoint_name}")
        return True
    
    def load_state(self, project_id: str) -> Optional[Dict]:
        """状態ファイル読み込み"""
        state_file = self.state_dir / f"{project_id}.json"
        
        if not state_file.exists():
            return None
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                # ファイルロック取得
                fcntl.flock(f.fileno(), fcntl.LOCK_SH)
                state = json.load(f)
                return state
        except (json.JSONDecodeError, OSError) as e:
            self.logger.error(f"状態ファイル読み込みエラー: {state_file} - {e}")
            return None
    
    def get_active_projects(self) -> List[str]:
        """アクティブなプロジェクト一覧取得"""
        active_projects = []
        
        for state_file in self.state_dir.glob("*.json"):
            project_id = state_file.stem
            state = self.load_state(project_id)
            
            if state and state["overall_status"] in ["initialized", "in_progress"]:
                active_projects.append(project_id)
        
        return active_projects
    
    def get_recovery_candidates(self) -> List[Dict]:
        """復旧候補プロジェクト取得"""
        candidates = []
        
        for project_id in self.get_active_projects():
            state = self.load_state(project_id)
            if not state:
                continue
            
            # 最終更新から30分以上経過しているプロジェクト
            last_update = datetime.fromisoformat(state["updated_at"])
            now = datetime.now(timezone.utc)
            
            if (now - last_update).total_seconds() > 1800:  # 30分
                candidates.append({
                    "project_id": project_id,
                    "last_update": state["updated_at"],
                    "current_phase": state["current_phase"],
                    "error_count": len(state["error_log"])
                })
        
        return candidates
    
    def mark_project_completed(self, project_id: str, wordpress_post_id: Optional[str] = None) -> bool:
        """プロジェクト完了マーク"""
        state = self.load_state(project_id)
        if not state:
            return False
        
        state["overall_status"] = "completed"
        state["completed_at"] = datetime.now(timezone.utc).isoformat()
        
        if wordpress_post_id:
            state["metadata"]["wordpress_post_id"] = wordpress_post_id
        
        self._save_state(project_id, state)
        self.logger.info(f"プロジェクト完了: {project_id}")
        return True
    
    def cleanup_old_states(self, days: int = 30) -> int:
        """古い状態ファイルの清理"""
        cleaned_count = 0
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        
        for state_file in self.state_dir.glob("*.json"):
            if state_file.stat().st_mtime < cutoff_time:
                project_id = state_file.stem
                state = self.load_state(project_id)
                
                # 完了済みプロジェクトのみ削除
                if state and state.get("overall_status") == "completed":
                    state_file.unlink()
                    cleaned_count += 1
                    self.logger.info(f"古い状態ファイル削除: {project_id}")
        
        return cleaned_count
    
    def _save_state(self, project_id: str, state: Dict) -> bool:
        """状態ファイル保存（ロック付き）"""
        state_file = self.state_dir / f"{project_id}.json"
        temp_file = state_file.with_suffix('.tmp')
        
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                # ファイルロック取得
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                json.dump(state, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            
            # アトミックな上書き
            temp_file.replace(state_file)
            return True
            
        except OSError as e:
            self.logger.error(f"状態ファイル保存エラー: {state_file} - {e}")
            if temp_file.exists():
                temp_file.unlink()
            return False
    
    def _advance_to_next_phase(self, state: Dict, completed_phase: str) -> None:
        """次フェーズへの自動進行"""
        phase_order = ["Phase1", "Phase2", "Phase3"]
        
        try:
            current_index = phase_order.index(completed_phase)
            if current_index + 1 < len(phase_order):
                next_phase = phase_order[current_index + 1]
                state["phases"][next_phase]["status"] = "ready"
        except ValueError:
            pass
    
    def _all_tasks_completed(self, phase_data: Dict) -> bool:
        """フェーズ内全タスク完了チェック"""
        for task_data in phase_data["tasks"].values():
            if task_data["status"] != "completed":
                return False
        return True


# 便利な関数群
def get_current_project_state(project_id: str) -> Optional[Dict]:
    """現在のプロジェクト状態取得"""
    manager = WorkflowStateManager()
    return manager.load_state(project_id)

def create_new_project(project_id: str, keyword: str, metadata: Optional[Dict] = None) -> Dict:
    """新規プロジェクト作成"""
    manager = WorkflowStateManager()
    return manager.create_project_state(project_id, keyword, metadata)

def update_task_progress(project_id: str, phase: str, task: str, status: str, assigned_to: Optional[str] = None) -> bool:
    """タスク進捗更新"""
    manager = WorkflowStateManager()
    return manager.update_task_status(project_id, phase, task, status, assigned_to)

def record_project_error(project_id: str, error_type: str, error_message: str, context: Optional[Dict] = None) -> bool:
    """プロジェクトエラー記録"""
    manager = WorkflowStateManager()
    return manager.record_error(project_id, error_type, error_message, context)

def get_recovery_candidates() -> List[Dict]:
    """復旧候補プロジェクト取得"""
    manager = WorkflowStateManager()
    return manager.get_recovery_candidates()


if __name__ == "__main__":
    # 使用例・テスト
    manager = WorkflowStateManager()
    
    # テストプロジェクト作成
    test_project = "test-AI時代を制する記事-INT-01"
    state = manager.create_project_state(test_project, "AI 効率化", {"test": True})
    
    # フェーズ開始
    manager.update_phase_status(test_project, "Phase1", "in_progress")
    
    # タスク更新
    manager.update_task_status(test_project, "Phase1", "intent_analysis", "completed")
    
    # エラー記録
    manager.record_error(test_project, "API_ERROR", "OpenAI API rate limit", {"retry_count": 1})
    
    # チェックポイント作成
    manager.create_checkpoint(test_project, "phase1_completed", {"notes": "意図分析完了"})
    
    print("✅ ワークフロー状態管理システムのテスト完了")