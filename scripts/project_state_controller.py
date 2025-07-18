#\!/usr/bin/env python3
"""
プロジェクト状態統合管理コントローラー
- スマートクリーンアップ
- Boss1混乱防止
- プロジェクト状態管理
- 魔法のキーワード実装
"""

import argparse
import subprocess
import sys
from pathlib import Path

def execute_smart_cleanup(force: bool = False) -> None:
    """スマートクリーンアップの実行"""
    script_path = Path(__file__).parent / "smart_tmp_cleanup.py"
    cmd = [sys.executable, str(script_path)]
    if force:
        cmd.append('--force')
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ 警告: {result.stderr}")
    except Exception as e:
        print(f"❌ スマートクリーンアップエラー: {e}")

def execute_boss1_prevention(project_id: str, keyword: str) -> None:
    """Boss1混乱防止の実行"""
    script_path = Path(__file__).parent / "boss1_confusion_prevention.py"
    cmd = [sys.executable, str(script_path), project_id, keyword]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ 警告: {result.stderr}")
    except Exception as e:
        print(f"❌ Boss1混乱防止エラー: {e}")

def handle_magic_keywords(keyword: str) -> bool:
    """魔法のキーワード処理"""
    if keyword == "バルス":
        print("🔥 バルス！outputs ディレクトリを完全削除します...")
        import shutil
        outputs_dir = Path("/mnt/c/home/hiroshi/blog_generator/outputs")
        if outputs_dir.exists():
            shutil.rmtree(outputs_dir)
            print("✅ outputs ディレクトリを削除しました")
        else:
            print("❌ outputs ディレクトリが見つかりません")
        return True
    
    elif keyword == "整理整頓":
        print("🧹 整理整頓を開始します...")
        execute_smart_cleanup(force=True)
        
        # OutputManagerの実行
        try:
            from utils.output_manager import OutputManager
            manager = OutputManager()
            manager.organize_outputs()
            print("✅ ファイル整理完了")
        except Exception as e:
            print(f"⚠️ OutputManager実行エラー: {e}")
        return True
    
    return False

def main():
    parser = argparse.ArgumentParser(description="プロジェクト状態統合管理")
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # スマートクリーンアップ
    cleanup_parser = subparsers.add_parser('cleanup', help='スマートクリーンアップ')
    cleanup_parser.add_argument('--force', action='store_true', help='強制実行')
    
    # Boss1混乱防止
    prevent_parser = subparsers.add_parser('prevent', help='Boss1混乱防止')
    prevent_parser.add_argument('project_id', help='プロジェクトID')
    prevent_parser.add_argument('keyword', help='キーワード')
    
    # 魔法のキーワード
    magic_parser = subparsers.add_parser('magic', help='魔法のキーワード実行')
    magic_parser.add_argument('keyword', choices=['バルス', '整理整頓'], help='魔法のキーワード')
    
    # 統合実行
    integrated_parser = subparsers.add_parser('integrated', help='統合実行')
    integrated_parser.add_argument('project_id', help='プロジェクトID')
    integrated_parser.add_argument('keyword', help='キーワード')
    integrated_parser.add_argument('--with-cleanup', action='store_true', help='クリーンアップも実行')
    
    args = parser.parse_args()
    
    if args.command == 'cleanup':
        execute_smart_cleanup(args.force)
    elif args.command == 'prevent':
        execute_boss1_prevention(args.project_id, args.keyword)
    elif args.command == 'magic':
        handle_magic_keywords(args.keyword)
    elif args.command == 'integrated':
        if args.with_cleanup:
            print("🧹 統合クリーンアップ実行中...")
            execute_smart_cleanup(force=True)
        
        print("🛡️ Boss1混乱防止実行中...")
        execute_boss1_prevention(args.project_id, args.keyword)
        
        print("✅ 統合実行完了")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
EOF < /dev/null
