#!/bin/bash

# 🔗 Connection Test System - 指揮系統確認・停滞防止
# President0の「接続確認」合言葉を補完するスクリプト

set -e

# 色付きログ関数
log_info() { echo -e "\033[1;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }
log_success() { echo -e "\033[1;34m[SUCCESS]\033[0m $1"; }

# 階層確認プロトコル実行
execute_hierarchy_check() {
    log_info "🏛️ 指揮系統階層確認プロトコル開始"
    
    echo "=== President0 → Boss1 → Worker1,2,3 確認 ==="
    echo ""
    
    # タイムスタンプ記録
    local test_start=$(date +%s)
    mkdir -p tmp logs
    echo "$test_start" > tmp/connection_test_start.txt
    
    # Boss1への接続確認指示送信
    log_info "📤 Boss1に階層確認指示送信中..."
    
    ./agent-send.sh boss1 "【President0→Boss1】指揮系統接続確認テスト

## 階層確認プロトコル開始
あなたはboss1として、正しい指揮系統 President0←→Boss1←→Worker1,2,3 の確認を実行してください。

### Phase1: Boss1→Worker順次接続確認
以下の順序で各Workerに接続テストを送信：

**1. Worker1への確認:**
\`\`\`bash
./agent-send.sh worker1 \"【Boss1→Worker1】接続テスト1/3

あなたはworker1です。指揮系統確認のため以下を実行：
- 現在時刻確認: date
- 作業ディレクトリ確認: pwd
- 階層確認完了報告: ./agent-send.sh boss1 \\\"【Worker1→Boss1】接続確認完了。現在時刻:\$(date)、ディレクトリ:\$(pwd)\\\"

即座に実行してください。\"
\`\`\`

**2. Worker2への確認:**
\`\`\`bash  
./agent-send.sh worker2 \"【Boss1→Worker2】接続テスト2/3

あなたはworker2です。指揮系統確認のため以下を実行：
- 現在時刻確認: date
- 作業ディレクトリ確認: pwd
- 階層確認完了報告: ./agent-send.sh boss1 \\\"【Worker2→Boss1】接続確認完了。現在時刻:\$(date)、ディレクトリ:\$(pwd)\\\"

即座に実行してください。\"
\`\`\`

**3. Worker3への確認:**
\`\`\`bash
./agent-send.sh worker3 \"【Boss1→Worker3】接続テスト3/3

あなたはworker3です。指揮系統確認のため以下を実行：
- 現在時刻確認: date  
- 作業ディレクトリ確認: pwd
- 階層確認完了報告: ./agent-send.sh boss1 \\\"【Worker3→Boss1】接続確認完了。現在時刻:\$(date)、ディレクトリ:\$(pwd)\\\"

即座に実行してください。\"
\`\`\`

### Phase2: 結果集約・President0報告
30秒間全Worker応答を待機し、以下フォーマットで報告：

\`\`\`bash
./agent-send.sh president \"【Boss1→President0】指揮系統接続確認完了報告

## 接続テスト結果サマリー
- Worker1応答: [成功/失敗/無応答] - [応答時刻]
- Worker2応答: [成功/失敗/無応答] - [応答時刻]  
- Worker3応答: [成功/失敗/無応答] - [応答時刻]
- 総応答率: [成功数]/3
- 平均応答時間: [秒]

## システム正常性確認
- tmuxセッション状態: multiagent(確認済み/異常)
- 通信遅延状況: [低/中/高]
- ファイルアクセス: outputs/tmp(正常/異常)

## 指揮系統評価
✅ President0←→Boss1: 正常
✅ Boss1←→Worker1: [状況]
✅ Boss1←→Worker2: [状況]  
✅ Boss1←→Worker3: [状況]

## 推奨アクション
[問題があれば具体的対処法を記載。正常な場合は「指揮系統は正常に機能しています」]

指揮系統確認プロトコル完了。President0からの次の指示をお待ちしています。\"
\`\`\`

### 重要な階層ルール
- President0は直接Worker1-3に指示を送信しない
- Worker1-3は直接President0に報告しない  
- 全ての指示・報告はBoss1経由で実行
- 階層違反が発生した場合は即座に修正

この接続確認プロトコルを即座に開始してください。"

    log_success "✅ Boss1に階層確認指示送信完了"
    
    # 監視開始
    monitor_connection_test_progress
}

# 接続テスト進捗監視
monitor_connection_test_progress() {
    local test_start=$(cat tmp/connection_test_start.txt)
    local timeout=60  # 60秒タイムアウト
    local check_interval=10  # 10秒間隔チェック
    
    log_info "📊 接続テスト進捗監視開始（タイムアウト: ${timeout}秒）"
    
    for i in $(seq 1 $((timeout / check_interval))); do
        sleep $check_interval
        local elapsed=$(($(date +%s) - test_start))
        
        echo "⏱️  経過時間: ${elapsed}秒 / ${timeout}秒"
        
        # Boss1からの報告確認
        if grep -q "指揮系統接続確認完了報告" logs/send_log.txt 2>/dev/null; then
            log_success "✅ Boss1からの階層確認報告を検出"
            break
        fi
        
        # Worker応答確認
        local worker_responses=$(grep -c "Worker.*Boss1.*接続確認完了" logs/send_log.txt 2>/dev/null || echo "0")
        echo "👷 Worker応答数: ${worker_responses}/3"
        
        if [ $elapsed -ge $timeout ]; then
            log_warn "⚠️ 接続テストタイムアウト - 問題分析中..."
            analyze_connection_issues
            break
        fi
    done
}

# 接続問題分析
analyze_connection_issues() {
    log_warn "🔍 接続問題分析開始"
    
    echo ""
    echo "📋 問題診断レポート"
    echo "==================="
    
    # tmuxセッション確認
    if ! tmux has-session -t multiagent 2>/dev/null; then
        log_error "❌ multiagentセッションが存在しません"
        echo "対処法: ./setup.sh でセッション再作成"
    else
        log_success "✅ multiagentセッション正常"
    fi
    
    if ! tmux has-session -t president 2>/dev/null; then
        log_error "❌ presidentセッションが存在しません"  
        echo "対処法: ./setup.sh でセッション再作成"
    else
        log_success "✅ presidentセッション正常"
    fi
    
    # 送信ログ分析
    local recent_sends=$(tail -10 logs/send_log.txt 2>/dev/null || echo "ログファイルなし")
    echo ""
    echo "📝 直近の送信ログ:"
    echo "$recent_sends"
    
    # Worker別応答状況
    echo ""
    echo "👷 Worker別応答状況:"
    for worker in worker1 worker2 worker3; do
        local responses=$(grep -c "$worker.*Boss1" logs/send_log.txt 2>/dev/null || echo "0")
        echo "  - $worker: ${responses}回応答"
    done
    
    # 推奨復旧アクション
    echo ""
    echo "🔧 推奨復旧アクション:"
    echo "1. ./quick-recovery.sh          # 自動復旧実行"
    echo "2. ./setup.sh                   # セッション再構築"
    echo "3. ./connection-test.sh         # 接続テスト再実行"
    echo "4. ./auto-monitor.sh start &    # 自動監視開始"
}

# 階層違反検出・修正
detect_hierarchy_violations() {
    log_info "🏛️ 階層違反検出開始"
    
    # President→Worker直接指示の検出
    local direct_president_worker=$(grep -c "president.*worker[1-3]" logs/send_log.txt 2>/dev/null || echo "0")
    if [ $direct_president_worker -gt 0 ]; then
        log_error "❌ 階層違反検出: President0→Worker直接指示 (${direct_president_worker}件)"
        echo "修正必要: President0はBoss1経由でのみ指示を送信"
    fi
    
    # Worker→President直接報告の検出
    local direct_worker_president=$(grep -c "worker[1-3].*president" logs/send_log.txt 2>/dev/null || echo "0")
    if [ $direct_worker_president -gt 0 ]; then
        log_error "❌ 階層違反検出: Worker→President0直接報告 (${direct_worker_president}件)"
        echo "修正必要: Worker1-3はBoss1経由でのみ報告"
    fi
    
    if [ $direct_president_worker -eq 0 ] && [ $direct_worker_president -eq 0 ]; then
        log_success "✅ 階層違反なし - 正しい指揮系統が維持されています"
    fi
}

# 簡易接続テスト
quick_connection_test() {
    log_info "⚡ 簡易接続テスト実行"
    
    # President→Boss1テスト
    ./agent-send.sh boss1 "【簡易接続テスト】Boss1応答確認。「テスト受信確認」と返答してください。"
    
    sleep 3
    
    # Boss1→Worker順次テスト
    ./agent-send.sh boss1 "【Boss1指示】以下を順次実行:
./agent-send.sh worker1 \"応答テスト1\"
./agent-send.sh worker2 \"応答テスト2\"  
./agent-send.sh worker3 \"応答テスト3\""
    
    log_success "✅ 簡易テスト送信完了"
}

# メイン実行
main() {
    case "${1:-full}" in
        "full")
            echo "🔗 Connection Test System"
            echo "========================"
            echo ""
            execute_hierarchy_check
            ;;
        "quick")
            quick_connection_test
            ;;
        "analyze")
            analyze_connection_issues
            ;;
        "violations")
            detect_hierarchy_violations
            ;;
        "monitor")
            monitor_connection_test_progress
            ;;
        *)
            cat << EOF
Usage: $0 {full|quick|analyze|violations|monitor}

Commands:
  full        - 完全な階層確認プロトコル実行
  quick       - 簡易接続テスト
  analyze     - 接続問題分析
  violations  - 階層違反検出
  monitor     - 接続テスト進捗監視

Examples:
  $0           # 完全階層確認
  $0 quick     # 簡易テスト
  $0 analyze   # 問題分析

EOF
            exit 1
            ;;
    esac
}

main "$@"