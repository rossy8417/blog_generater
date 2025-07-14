#!/usr/bin/env python3
"""
ログローテーションとログ管理システム
肥大化するログファイルの自動管理
"""

import os
import gzip
import shutil
import time
import glob
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
import threading
import schedule

class LogRotationManager:
    """ログローテーション管理"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # デフォルト設定
        self.rotation_configs = {
            "send_log.txt": {
                "max_size_mb": 10,      # 10MBでローテーション
                "keep_files": 5,        # 5世代保持
                "compress": True        # 古いファイルを圧縮
            },
            "error.log": {
                "max_size_mb": 5,
                "keep_files": 10,
                "compress": True
            },
            "system.log": {
                "max_size_mb": 20,
                "keep_files": 7,
                "compress": True
            }
        }
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
        self._setup_logging()
        
        # スケジューラー設定
        self._setup_scheduler()
    
    def _setup_logging(self):
        """ログ設定セットアップ"""
        # 基本的なログ設定（必要に応じて）
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def _setup_scheduler(self):
        """スケジューラーセットアップ"""
        # 毎時間チェック
        schedule.every().hour.do(self.check_and_rotate_all)
        # 毎日午前2時に古いファイル清理
        schedule.every().day.at("02:00").do(self.cleanup_old_files)
    
    def add_log_config(self, filename: str, max_size_mb: int, 
                      keep_files: int = 5, compress: bool = True):
        """ログファイル設定追加"""
        self.rotation_configs[filename] = {
            "max_size_mb": max_size_mb,
            "keep_files": keep_files,
            "compress": compress
        }
        self.logger.info(f"Log config added: {filename}")
    
    def check_log_size(self, filename: str) -> Dict[str, any]:
        """ログファイルサイズチェック"""
        log_path = self.log_dir / filename
        
        if not log_path.exists():
            return {"exists": False, "size_mb": 0, "needs_rotation": False}
        
        size_bytes = log_path.stat().st_size
        size_mb = size_bytes / (1024 * 1024)
        
        config = self.rotation_configs.get(filename, {"max_size_mb": 10})
        needs_rotation = size_mb > config["max_size_mb"]
        
        return {
            "exists": True,
            "size_bytes": size_bytes,
            "size_mb": round(size_mb, 2),
            "max_size_mb": config["max_size_mb"],
            "needs_rotation": needs_rotation
        }
    
    def rotate_log(self, filename: str) -> bool:
        """ログファイルローテーション実行"""
        log_path = self.log_dir / filename
        
        if not log_path.exists():
            self.logger.warning(f"Log file not found: {filename}")
            return False
        
        config = self.rotation_configs.get(filename, {})
        
        try:
            # タイムスタンプ付きバックアップファイル名生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"{filename}.{timestamp}"
            backup_path = self.log_dir / backup_filename
            
            # ファイル移動
            shutil.move(str(log_path), str(backup_path))
            
            # 圧縮実行
            if config.get("compress", False):
                compressed_path = backup_path.with_suffix(backup_path.suffix + '.gz')
                with open(backup_path, 'rb') as f_in:
                    with gzip.open(compressed_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                backup_path.unlink()  # 元ファイル削除
                self.logger.info(f"Log rotated and compressed: {filename} -> {compressed_path.name}")
            else:
                self.logger.info(f"Log rotated: {filename} -> {backup_filename}")
            
            # 新しいログファイル作成
            log_path.touch()
            
            # 古いファイル清理
            self._cleanup_old_rotated_files(filename, config.get("keep_files", 5))
            
            return True
            
        except Exception as e:
            self.logger.error(f"Log rotation failed for {filename}: {e}")
            return False
    
    def _cleanup_old_rotated_files(self, base_filename: str, keep_files: int):
        """古いローテーションファイル清理"""
        # パターンマッチでローテーションファイル検索
        pattern = f"{base_filename}.*"
        rotated_files = list(self.log_dir.glob(pattern))
        
        # ベースファイル以外でソート（新しい順）
        rotated_files = [f for f in rotated_files if f.name != base_filename]
        rotated_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # 保持数を超えるファイルを削除
        for old_file in rotated_files[keep_files:]:
            try:
                old_file.unlink()
                self.logger.info(f"Old log file deleted: {old_file.name}")
            except Exception as e:
                self.logger.error(f"Failed to delete old log file {old_file.name}: {e}")
    
    def check_and_rotate_all(self):
        """全ログファイルチェック・ローテーション"""
        self.logger.info("Starting scheduled log rotation check")
        
        rotated_count = 0
        for filename in self.rotation_configs.keys():
            status = self.check_log_size(filename)
            
            if status["needs_rotation"]:
                self.logger.info(f"Rotating log: {filename} ({status['size_mb']}MB)")
                if self.rotate_log(filename):
                    rotated_count += 1
        
        if rotated_count > 0:
            self.logger.info(f"Log rotation completed: {rotated_count} files rotated")
    
    def cleanup_old_files(self, max_age_days: int = 30):
        """古いログファイルの清理"""
        cutoff_time = time.time() - (max_age_days * 24 * 60 * 60)
        cleaned_count = 0
        
        # 全ログファイルをチェック
        for log_file in self.log_dir.glob("*.log*"):
            if log_file.stat().st_mtime < cutoff_time:
                try:
                    log_file.unlink()
                    cleaned_count += 1
                    self.logger.info(f"Old log file cleaned: {log_file.name}")
                except Exception as e:
                    self.logger.error(f"Failed to clean old log file {log_file.name}: {e}")
        
        self.logger.info(f"Log cleanup completed: {cleaned_count} old files removed")
    
    def get_log_statistics(self) -> Dict[str, Dict]:
        """ログファイル統計情報取得"""
        stats = {}
        
        for filename in self.rotation_configs.keys():
            log_status = self.check_log_size(filename)
            
            # ローテーションファイル数取得
            pattern = f"{filename}.*"
            rotated_files = list(self.log_dir.glob(pattern))
            rotated_count = len([f for f in rotated_files if f.name != filename])
            
            stats[filename] = {
                **log_status,
                "rotated_files_count": rotated_count,
                "config": self.rotation_configs[filename]
            }
        
        return stats
    
    def force_rotate_all(self):
        """全ログファイル強制ローテーション"""
        self.logger.info("Force rotating all log files")
        
        for filename in self.rotation_configs.keys():
            if (self.log_dir / filename).exists():
                self.rotate_log(filename)
    
    def start_background_scheduler(self):
        """バックグラウンドスケジューラー開始"""
        def run_scheduler():
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1分間隔でチェック
        
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        self.logger.info("Background log rotation scheduler started")

class SystemLogManager:
    """システム全体のログ管理"""
    
    def __init__(self):
        self.rotation_manager = LogRotationManager()
        
        # システム固有のログ設定
        self._setup_system_logs()
    
    def _setup_system_logs(self):
        """システムログ設定"""
        # 既存の重要ログファイルを登録
        self.rotation_manager.add_log_config("send_log.txt", max_size_mb=5, keep_files=10)
        
        # agent-send.shのログも管理
        for log_dir in ["tmp/message_queue", "Claude-Code-Blog-communication/logs"]:
            if os.path.exists(log_dir):
                for log_file in glob.glob(f"{log_dir}/*.log"):
                    basename = os.path.basename(log_file)
                    self.rotation_manager.add_log_config(basename, max_size_mb=2, keep_files=5)
    
    def emergency_log_cleanup(self):
        """緊急ログ清理（ディスク容量不足時など）"""
        self.rotation_manager.logger.warning("Emergency log cleanup initiated")
        
        # 強制ローテーション
        self.rotation_manager.force_rotate_all()
        
        # 古いファイル清理（保守的: 7日）
        self.rotation_manager.cleanup_old_files(max_age_days=7)
    
    def get_system_log_summary(self) -> Dict:
        """システムログサマリー取得"""
        stats = self.rotation_manager.get_log_statistics()
        
        total_size_mb = sum(s.get("size_mb", 0) for s in stats.values())
        needs_attention = [name for name, s in stats.items() if s.get("needs_rotation", False)]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_log_size_mb": round(total_size_mb, 2),
            "files_needing_rotation": needs_attention,
            "total_files": len(stats),
            "details": stats
        }

# 便利な関数
def setup_log_rotation():
    """ログローテーション設定"""
    system_log_manager = SystemLogManager()
    system_log_manager.rotation_manager.start_background_scheduler()
    return system_log_manager

def emergency_cleanup():
    """緊急ログ清理実行"""
    system_log_manager = SystemLogManager()
    system_log_manager.emergency_log_cleanup()

def check_log_status():
    """ログ状態確認"""
    system_log_manager = SystemLogManager()
    return system_log_manager.get_system_log_summary()

# CLIスクリプト機能
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Log Management Utility")
    parser.add_argument("--check", action="store_true", help="Check log status")
    parser.add_argument("--rotate", action="store_true", help="Force rotate all logs")
    parser.add_argument("--cleanup", action="store_true", help="Emergency cleanup")
    parser.add_argument("--start-scheduler", action="store_true", help="Start background scheduler")
    
    args = parser.parse_args()
    
    if args.check:
        summary = check_log_status()
        print("=== Log Status Summary ===")
        print(f"Total size: {summary['total_log_size_mb']}MB")
        print(f"Files needing rotation: {len(summary['files_needing_rotation'])}")
        for filename, details in summary['details'].items():
            status = "⚠️ NEEDS ROTATION" if details.get('needs_rotation') else "✅ OK"
            print(f"  {filename}: {details.get('size_mb', 0)}MB {status}")
    
    elif args.rotate:
        manager = SystemLogManager()
        manager.rotation_manager.force_rotate_all()
        print("✅ All logs rotated")
    
    elif args.cleanup:
        emergency_cleanup()
        print("✅ Emergency cleanup completed")
    
    elif args.start_scheduler:
        manager = setup_log_rotation()
        print("✅ Background log rotation scheduler started")
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n🛑 Scheduler stopped")
    
    else:
        parser.print_help()