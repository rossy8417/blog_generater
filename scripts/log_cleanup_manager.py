#\!/usr/bin/env python3
"""
Boss1報告ログ自動クリーンアップシステム
President0により設計・実装
"""

import os
import shutil
import datetime
import re
from pathlib import Path

class LogCleanupManager:
    def __init__(self, base_dir="/mnt/c/home/hiroshi/blog_generator"):
        self.base_dir = Path(base_dir)
        self.message_queue_dir = self.base_dir / "tmp" / "message_queue"
        self.backup_dir = self.base_dir / "tmp" / "log_backups"
        
        # クリーンアップ設定
        self.max_log_size_kb = 20  # 20KB制限
        self.max_entries_per_log = 100  # 最新100エントリのみ保持
        self.retention_hours = 24  # 24時間以上古いエントリ削除
        
        # バックアップディレクトリ作成
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def get_log_files(self):
        """対象ログファイル一覧取得"""
        log_files = []
        if self.message_queue_dir.exists():
            for log_file in self.message_queue_dir.glob("*_queue.log"):
                log_files.append(log_file)
        return log_files
    
    def parse_log_entry_timestamp(self, line):
        """ログエントリのタイムスタンプ解析"""
        timestamp_pattern = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"
        match = re.match(timestamp_pattern, line)
        if match:
            try:
                return datetime.datetime.strptime(match.group(1), "%Y-%m-%d %H:%M:%S")
            except ValueError:
                return None
        return None
    
    def backup_log_file(self, log_file):
        """ログファイルバックアップ作成"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{log_file.stem}_backup_{timestamp}.log"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(log_file, backup_path)
        print(f"✅ バックアップ作成: {backup_path}")
        return backup_path
    
    def cleanup_old_entries_by_time(self, log_file):
        """時間ベースでの古いエントリ削除"""
        if not log_file.exists():
            return
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(hours=self.retention_hours)
        kept_lines = []
        
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                entry_time = self.parse_log_entry_timestamp(line.strip())
                if entry_time and entry_time >= cutoff_time:
                    kept_lines.append(line)
                elif not entry_time:  # タイムスタンプなしの行は保持
                    kept_lines.append(line)
        
        # ファイル書き換え
        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(kept_lines)
        
        print(f"✅ 時間ベース削除完了: {log_file.name} ({len(kept_lines)}行保持)")
    
    def cleanup_excess_entries(self, log_file):
        """エントリ数制限での削除"""
        if not log_file.exists():
            return
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        if len(lines) > self.max_entries_per_log:
            # 最新のエントリのみ保持
            kept_lines = lines[-self.max_entries_per_log:]
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.writelines(kept_lines)
            
            print(f"✅ エントリ数制限削除完了: {log_file.name} ({len(kept_lines)}行保持)")
    
    def cleanup_by_file_size(self, log_file):
        """ファイルサイズ制限での削除"""
        if not log_file.exists():
            return
        
        file_size_kb = log_file.stat().st_size / 1024
        
        if file_size_kb > self.max_log_size_kb:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # ファイルサイズが制限以下になるまで古いエントリ削除
            while len(lines) > 10:  # 最低10行は保持
                lines = lines[10:]  # 10行ずつ削除
                
                temp_content = ''.join(lines)
                if len(temp_content.encode('utf-8')) / 1024 <= self.max_log_size_kb:
                    break
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✅ ファイルサイズ制限削除完了: {log_file.name} ({len(lines)}行保持)")
    
    def cleanup_old_backups(self):
        """古いバックアップファイル削除（7日以上古い）"""
        if not self.backup_dir.exists():
            return
        
        cutoff_time = datetime.datetime.now() - datetime.timedelta(days=7)
        deleted_count = 0
        
        for backup_file in self.backup_dir.glob("*_backup_*.log"):
            if backup_file.stat().st_mtime < cutoff_time.timestamp():
                backup_file.unlink()
                deleted_count += 1
        
        if deleted_count > 0:
            print(f"✅ 古いバックアップ削除: {deleted_count}ファイル")
    
    def execute_full_cleanup(self):
        """完全クリーンアップ実行"""
        print("🧹 Boss1報告ログ自動クリーンアップ開始")
        print(f"📁 対象ディレクトリ: {self.message_queue_dir}")
        
        log_files = self.get_log_files()
        
        if not log_files:
            print("⚠️ 対象ログファイルが見つかりません")
            return
        
        for log_file in log_files:
            print(f"\n📋 処理中: {log_file.name}")
            
            # ファイルサイズ確認
            file_size_kb = log_file.stat().st_size / 1024
            print(f"   現在サイズ: {file_size_kb:.1f}KB")
            
            # 大きなファイルはバックアップ作成
            if file_size_kb > self.max_log_size_kb:
                self.backup_log_file(log_file)
                
                # 段階的クリーンアップ実行
                self.cleanup_old_entries_by_time(log_file)
                self.cleanup_excess_entries(log_file)
                self.cleanup_by_file_size(log_file)
                
                # クリーンアップ後のサイズ確認
                new_size_kb = log_file.stat().st_size / 1024
                print(f"   クリーンアップ後: {new_size_kb:.1f}KB")
            else:
                print(f"   ✅ サイズ適正（{file_size_kb:.1f}KB ≤ {self.max_log_size_kb}KB）")
        
        # 古いバックアップファイル削除
        self.cleanup_old_backups()
        
        print("\n✅ Boss1報告ログクリーンアップ完了")
        
        # クリーンアップ結果サマリー
        self.print_cleanup_summary()
    
    def print_cleanup_summary(self):
        """クリーンアップ結果サマリー表示"""
        print("\n📊 クリーンアップ結果サマリー")
        print("=" * 50)
        
        log_files = self.get_log_files()
        total_size = 0
        
        for log_file in log_files:
            file_size_kb = log_file.stat().st_size / 1024
            total_size += file_size_kb
            print(f"  {log_file.name}: {file_size_kb:.1f}KB")
        
        print(f"  合計サイズ: {total_size:.1f}KB")
        print(f"  バックアップ保存先: {self.backup_dir}")

def main():
    """メイン実行"""
    cleanup_manager = LogCleanupManager()
    cleanup_manager.execute_full_cleanup()

if __name__ == "__main__":
    main()
EOF < /dev/null
