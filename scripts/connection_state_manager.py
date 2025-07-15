#\!/usr/bin/env python3
"""
完全正常状態再現・維持システム
President0により設計・実装
Boss1ターミナル落ち対策とワーカー連携復旧の自動化
"""

import os
import subprocess
import time
import datetime
from pathlib import Path
import json

class ConnectionStateManager:
    def __init__(self, base_dir="/mnt/c/home/hiroshi/blog_generator"):
        self.base_dir = Path(base_dir)
        self.state_file = self.base_dir / "tmp" / "connection_state.json"
        self.recovery_log = self.base_dir / "logs" / "connection_recovery.log"
        
        # 完全正常状態の定義
        self.target_state = {
            "sessions": {
                "multiagent": {
                    "required": True,
                    "panes": {
                        "0.0": {"role": "boss1", "command": "claude"},
                        "0.1": {"role": "worker1", "command": "claude"},
                        "0.2": {"role": "worker2", "command": "claude"},
                        "0.3": {"role": "worker3", "command": "claude"}
                    }
                },
                "president": {
                    "required": True,
                    "panes": {
                        "0.0": {"role": "president0", "command": "claude"}
                    }
                }
            },
            "communication_test": {
                "president_to_boss1": True,
                "boss1_to_workers": True,
                "workers_to_boss1": True
            }
        }
        
        # ディレクトリ作成
        self.recovery_log.parent.mkdir(parents=True, exist_ok=True)
        self.state_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, message, level="INFO"):
        """ログ記録"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {level}: {message}"
        print(log_entry)
        
        with open(self.recovery_log, 'a', encoding='utf-8') as f:
            f.write(log_entry + "\n")
    
    def check_tmux_sessions(self):
        """TMUXセッション状態確認"""
        try:
            result = subprocess.run(['tmux', 'list-sessions'], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode \!= 0:
                return {"status": "no_sessions", "sessions": []}
            
            sessions = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    session_name = line.split(':')[0]
                    sessions.append(session_name)
            
            return {"status": "active", "sessions": sessions}
            
        except Exception as e:
            self.log(f"TMUX確認エラー: {e}", "ERROR")
            return {"status": "error", "sessions": []}
    
    def check_pane_structure(self, session_name):
        """指定セッションのペイン構造確認"""
        try:
            result = subprocess.run(['tmux', 'list-panes', '-t', session_name, '-F', 
                                   '#{pane_index}:#{pane_width}x#{pane_height}:#{pane_current_command}'], 
                                  capture_output=True, text=True, check=False)
            
            if result.returncode \!= 0:
                return {"status": "error", "panes": {}}
            
            panes = {}
            for line in result.stdout.strip().split('\n'):
                if line:
                    parts = line.split(':')
                    if len(parts) >= 3:
                        pane_index = parts[0]
                        size = parts[1]
                        command = parts[2] if len(parts) > 2 else "unknown"
                        panes[f"0.{pane_index}"] = {
                            "size": size,
                            "command": command,
                            "active": command == "claude"
                        }
            
            return {"status": "active", "panes": panes}
            
        except Exception as e:
            self.log(f"ペイン構造確認エラー ({session_name}): {e}", "ERROR")
            return {"status": "error", "panes": {}}
    
    def test_communication_flow(self):
        """通信フロー簡易テスト"""
        test_results = {
            "president_to_boss1": False,
            "boss1_response": False,
            "overall_success": False
        }
        
        try:
            # 簡易テストメッセージ送信
            agent_send = self.base_dir / "Claude-Code-Blog-communication" / "agent-send.sh"
            
            if agent_send.exists():
                result = subprocess.run([str(agent_send), 'boss1', '【自動システム】簡易接続確認テスト'], 
                                      capture_output=True, text=True, check=False, timeout=10)
                
                if result.returncode == 0:
                    test_results["president_to_boss1"] = True
                    self.log("President0→Boss1通信: 成功")
                else:
                    self.log(f"President0→Boss1通信: 失敗 ({result.stderr})", "WARN")
            
            # 5秒待機してレスポンス確認（簡易）
            time.sleep(5)
            test_results["overall_success"] = test_results["president_to_boss1"]
            
        except Exception as e:
            self.log(f"通信テストエラー: {e}", "ERROR")
        
        return test_results
    
    def get_current_state(self):
        """現在の接続状態を完全分析"""
        current_state = {
            "timestamp": datetime.datetime.now().isoformat(),
            "tmux_sessions": self.check_tmux_sessions(),
            "pane_structures": {},
            "communication_test": {},
            "overall_health": "unknown"
        }
        
        # 各セッションのペイン構造確認
        for session_name in ["multiagent", "president"]:
            current_state["pane_structures"][session_name] = self.check_pane_structure(session_name)
        
        # 通信テスト実行
        current_state["communication_test"] = self.test_communication_flow()
        
        # 総合健康度評価
        current_state["overall_health"] = self.evaluate_health(current_state)
        
        return current_state
    
    def evaluate_health(self, state):
        """システム健康度評価"""
        if state["tmux_sessions"]["status"] \!= "active":
            return "critical"
        
        required_sessions = ["multiagent", "president"]
        active_sessions = state["tmux_sessions"]["sessions"]
        
        if not all(session in active_sessions for session in required_sessions):
            return "degraded"
        
        # multiagentセッションのペイン数確認
        multiagent_panes = state["pane_structures"].get("multiagent", {}).get("panes", {})
        if len(multiagent_panes) < 4:
            return "degraded"
        
        # Claude Codeプロセス確認
        claude_active_count = sum(1 for pane in multiagent_panes.values() if pane.get("active", False))
        if claude_active_count < 3:  # Boss1 + Worker2以上
            return "degraded"
        
        # 通信テスト結果
        if not state["communication_test"].get("overall_success", False):
            return "degraded"
        
        return "healthy"
    
    def save_state(self, state):
        """状態をファイルに保存"""
        try:
            with open(self.state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
            self.log("システム状態保存完了")
        except Exception as e:
            self.log(f"状態保存エラー: {e}", "ERROR")
    
    def restore_healthy_state(self):
        """完全正常状態への復旧実行"""
        self.log("=== 完全正常状態復旧開始 ===")
        
        # Phase1: TMUXセッション確認・再作成
        tmux_status = self.check_tmux_sessions()
        if tmux_status["status"] \!= "active" or "multiagent" not in tmux_status["sessions"]:
            self.log("multiagentセッション再作成実行中...")
            if not self.recreate_multiagent_session():
                return False
        
        # Phase2: Claude Code起動確認・再起動
        self.log("Claude Code起動状況確認中...")
        if not self.ensure_claude_code_running():
            return False
        
        # Phase3: 通信テスト実行
        self.log("通信フロー確認中...")
        time.sleep(10)  # Claude Code起動待機
        
        communication_result = self.test_communication_flow()
        if communication_result["overall_success"]:
            self.log("=== 完全正常状態復旧成功 ===", "SUCCESS")
            return True
        else:
            self.log("通信フロー復旧失敗", "ERROR")
            return False
    
    def recreate_multiagent_session(self):
        """multiagentセッション再作成"""
        try:
            # 既存セッション削除（存在する場合）
            subprocess.run(['tmux', 'kill-session', '-t', 'multiagent'], 
                         capture_output=True, check=False)
            
            # 新規セッション作成
            subprocess.run(['tmux', 'new-session', '-d', '-s', 'multiagent'], check=True)
            
            # ペイン分割
            subprocess.run(['tmux', 'split-window', '-h', '-t', 'multiagent'], check=True)
            subprocess.run(['tmux', 'split-window', '-v', '-t', 'multiagent:0.0'], check=True)
            subprocess.run(['tmux', 'split-window', '-v', '-t', 'multiagent:0.1'], check=True)
            
            self.log("multiagentセッション再作成完了")
            return True
            
        except Exception as e:
            self.log(f"multiagentセッション再作成エラー: {e}", "ERROR")
            return False
    
    def ensure_claude_code_running(self):
        """全ペインでClaude Code起動確保"""
        try:
            panes = ["multiagent:0.0", "multiagent:0.1", "multiagent:0.2", "multiagent:0.3"]
            
            for pane in panes:
                # プロセス停止
                subprocess.run(['tmux', 'send-keys', '-t', pane, 'C-c'], check=False)
                time.sleep(1)
                
                # Claude Code起動
                subprocess.run(['tmux', 'send-keys', '-t', pane, 'claude code', 'C-m'], check=True)
                time.sleep(2)
            
            self.log("全ペインClaude Code起動完了")
            return True
            
        except Exception as e:
            self.log(f"Claude Code起動エラー: {e}", "ERROR")
            return False

def main():
    """メイン実行"""
    manager = ConnectionStateManager()
    
    # 現在状態確認
    current_state = manager.get_current_state()
    manager.save_state(current_state)
    
    health = current_state["overall_health"]
    manager.log(f"現在のシステム健康度: {health}")
    
    if health == "critical" or health == "degraded":
        manager.log("復旧処理開始...")
        success = manager.restore_healthy_state()
        
        if success:
            # 復旧後状態確認
            final_state = manager.get_current_state()
            manager.save_state(final_state)
            manager.log(f"復旧後健康度: {final_state['overall_health']}")
        else:
            manager.log("自動復旧失敗 - 手動介入が必要です", "ERROR")
    else:
        manager.log("システム正常 - 維持モード")

if __name__ == "__main__":
    main()
EOF < /dev/null
