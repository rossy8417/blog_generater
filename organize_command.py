#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
整理整頓コマンド実装
Claude Codeで「整理整頓」と入力された時に実行される
"""

import subprocess
import sys
from pathlib import Path

def run_organize():
    """整理整頓スクリプトを実行"""
    
    print("🧹 「整理整頓」コマンドを実行します...\n")
    
    # スクリプトパス
    script_path = Path(__file__).parent / "scripts" / "organize_outputs.py"
    
    try:
        # organize_outputs.py を実行
        result = subprocess.run([
            sys.executable, str(script_path)
        ], capture_output=True, text=True, encoding='utf-8')
        
        # 結果を表示
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(f"警告: {result.stderr}")
            
        if result.returncode == 0:
            print("\n✅ 整理整頓が完了しました！")
        else:
            print(f"\n❌ 整理整頓でエラーが発生しました (終了コード: {result.returncode})")
            
    except Exception as e:
        print(f"❌ 整理整頓の実行に失敗しました: {e}")

if __name__ == "__main__":
    run_organize()