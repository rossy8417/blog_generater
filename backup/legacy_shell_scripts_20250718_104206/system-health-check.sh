#!/bin/bash

# 🏥 システムヘルスチェック統合スクリプト
# 全エージェント・API・ファイルシステムの健全性を総合監視

set -e

# 設定
BASE_DIR="/mnt/c/home/hiroshi/blog_generator"
HEALTH_LOG="tmp/system_health.log"
ALERT_THRESHOLD_HIGH=80
ALERT_THRESHOLD_CRITICAL=95

# 色付きログ
log_info() { echo -e "\033[1;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }
log_success() { echo -e "\033[1;34m[SUCCESS]\033[0m $1"; }
log_critical() { echo -e "\033[1;41m[CRITICAL]\033[0m $1"; }

# ヘルスチェック結果格納
declare -A HEALTH_STATUS
OVERALL_HEALTH="healthy"
ISSUES_FOUND=()

# ペインインデックス取得
get_pane_index() {
    case "$1" in
        "boss1") echo "0" ;;
        "worker1") echo "1" ;;
        "worker2") echo "2" ;;
        "worker3") echo "3" ;;
        *) echo "0" ;;
    esac
}

# TMUXセッション健全性チェック
check_tmux_sessions() {
    log_info "=== TMUXセッション健全性チェック ==="
    
    local session_health="healthy"
    local required_sessions=("multiagent" "president")
    
    for session in "${required_sessions[@]}"; do
        if tmux has-session -t "$session" 2>/dev/null; then
            log_success "✅ $session セッション: 正常"
            
            # multiagentセッション詳細チェック
            if [[ "$session" == "multiagent" ]]; then
                check_multiagent_panes
            fi
        else
            log_error "❌ $session セッション: 未検出"
            session_health="unhealthy"
            ISSUES_FOUND+=("tmux_session_missing_$session")
        fi
    done
    
    HEALTH_STATUS["tmux_sessions"]="$session_health"
    
    if [[ "$session_health" != "healthy" ]]; then
        OVERALL_HEALTH="degraded"
    fi
}

# multiagentペイン詳細チェック
check_multiagent_panes() {
    local agents=("boss1" "worker1" "worker2" "worker3")
    local active_agents=0
    
    for agent in "${agents[@]}"; do
        local pane_index=$(get_pane_index "$agent")
        
        # ペイン応答性チェック
        if tmux capture-pane -t "multiagent:0.$pane_index" -p | grep -q ">" 2>/dev/null; then
            log_success "  ✅ $agent: アクティブ"
            ((active_agents++))
        else
            log_warn "  ⚠️ $agent: 非応答"
            ISSUES_FOUND+=("agent_non_responsive_$agent")
        fi
    done
    
    local agent_health_percent=$((active_agents * 100 / 4))
    log_info "エージェント応答性: ${active_agents}/4 (${agent_health_percent}%)"
    
    if [[ $agent_health_percent -lt 75 ]]; then
        HEALTH_STATUS["agents"]="degraded"
        if [[ "$OVERALL_HEALTH" == "healthy" ]]; then
            OVERALL_HEALTH="degraded"
        fi
    else
        HEALTH_STATUS["agents"]="healthy"
    fi
}

# メッセージキューシステム健全性チェック
check_message_queue() {
    log_info "=== メッセージキューシステム健全性チェック ==="
    
    local queue_health="healthy"
    local queue_dirs=("tmp/message_queue" "Claude-Code-Blog-communication/tmp/message_queue")
    
    for queue_dir in "${queue_dirs[@]}"; do
        if [[ -d "$queue_dir" ]]; then
            log_success "✅ キューディレクトリ: $queue_dir"
            
            # キューファイル健全性チェック
            local queue_files=$(find "$queue_dir" -name "*.log" | wc -l)
            local large_queues=$(find "$queue_dir" -name "*.log" -size +1M | wc -l)
            
            log_info "  キューファイル数: $queue_files"
            
            if [[ $large_queues -gt 0 ]]; then
                log_warn "  ⚠️ 大容量キューファイル: ${large_queues}個"
                ISSUES_FOUND+=("large_queue_files")
            fi
        else
            log_error "❌ キューディレクトリ未検出: $queue_dir"
            queue_health="unhealthy"
            ISSUES_FOUND+=("queue_directory_missing")
        fi
    done
    
    # ロックファイルチェック
    local lock_dir="tmp/message_queue/locks"
    if [[ -d "$lock_dir" ]]; then
        local old_locks=$(find "$lock_dir" -name "*.lock" -mmin +30 | wc -l)
        if [[ $old_locks -gt 0 ]]; then
            log_warn "⚠️ 古いロックファイル: ${old_locks}個"
            ISSUES_FOUND+=("stale_lock_files")
        fi
    fi
    
    HEALTH_STATUS["message_queue"]="$queue_health"
    
    if [[ "$queue_health" != "healthy" ]]; then
        OVERALL_HEALTH="degraded"
    fi
}

# ファイルシステム健全性チェック
check_filesystem() {
    log_info "=== ファイルシステム健全性チェック ==="
    
    local fs_health="healthy"
    
    # ディスク使用量チェック
    local disk_usage=$(df "$BASE_DIR" | tail -1 | awk '{print $5}' | sed 's/%//')
    log_info "ディスク使用量: ${disk_usage}%"
    
    if [[ $disk_usage -gt $ALERT_THRESHOLD_CRITICAL ]]; then
        log_critical "💥 ディスク使用量クリティカル: ${disk_usage}%"
        fs_health="critical"
        OVERALL_HEALTH="critical"
        ISSUES_FOUND+=("disk_usage_critical")
    elif [[ $disk_usage -gt $ALERT_THRESHOLD_HIGH ]]; then
        log_warn "⚠️ ディスク使用量高: ${disk_usage}%"
        fs_health="degraded"
        if [[ "$OVERALL_HEALTH" == "healthy" ]]; then
            OVERALL_HEALTH="degraded"
        fi
        ISSUES_FOUND+=("disk_usage_high")
    else
        log_success "✅ ディスク使用量: 正常"
    fi
    
    # 重要ディレクトリ確認
    local required_dirs=("outputs" "templates" "scripts" "utils" "logs" "tmp")
    
    for dir in "${required_dirs[@]}"; do
        if [[ -d "$dir" ]]; then
            # 書き込み権限チェック
            if [[ -w "$dir" ]]; then
                log_success "✅ $dir: 正常（書き込み可能）"
            else
                log_error "❌ $dir: 書き込み権限なし"
                fs_health="unhealthy"
                ISSUES_FOUND+=("directory_permission_$dir")
            fi
        else
            log_error "❌ $dir: ディレクトリ未検出"
            fs_health="unhealthy"
            ISSUES_FOUND+=("directory_missing_$dir")
        fi
    done
    
    # ログファイルサイズチェック
    local large_logs=$(find logs/ -name "*.log" -o -name "*.txt" -size +50M 2>/dev/null | wc -l)
    if [[ $large_logs -gt 0 ]]; then
        log_warn "⚠️ 大容量ログファイル: ${large_logs}個"
        ISSUES_FOUND+=("large_log_files")
    fi
    
    HEALTH_STATUS["filesystem"]="$fs_health"
    
    if [[ "$fs_health" == "critical" ]]; then
        OVERALL_HEALTH="critical"
    elif [[ "$fs_health" != "healthy" && "$OVERALL_HEALTH" == "healthy" ]]; then
        OVERALL_HEALTH="degraded"
    fi
}

# API健全性チェック
check_api_connectivity() {
    log_info "=== API接続健全性チェック ==="
    
    local api_health="healthy"
    
    # 環境変数チェック
    local required_apis=("OPENAI_API_KEY" "GOOGLE_API_KEY" "WORDPRESS_API_KEY" "WORDPRESS_ENDPOINT")
    
    for api_var in "${required_apis[@]}"; do
        if [[ -n "${!api_var}" && "${!api_var}" != "your_"* ]]; then
            log_success "✅ $api_var: 設定済み"
        else
            log_error "❌ $api_var: 未設定または初期値"
            api_health="unhealthy"
            ISSUES_FOUND+=("api_config_missing_$api_var")
        fi
    done
    
    # 簡単な接続テスト（curlが利用可能な場合）
    if command -v curl >/dev/null 2>&1; then
        # WordPress API接続テスト
        if [[ -n "$WORDPRESS_ENDPOINT" && "$WORDPRESS_ENDPOINT" != "your_"* ]]; then
            local wp_response=$(curl -s -o /dev/null -w "%{http_code}" -m 10 "$WORDPRESS_ENDPOINT" 2>/dev/null || echo "000")
            if [[ "$wp_response" =~ ^[2-5][0-9][0-9]$ ]]; then
                log_success "✅ WordPress API: 接続可能 (HTTP $wp_response)"
            else
                log_warn "⚠️ WordPress API: 接続問題 (HTTP $wp_response)"
                ISSUES_FOUND+=("wordpress_api_connectivity")
            fi
        fi
    fi
    
    HEALTH_STATUS["api_connectivity"]="$api_health"
    
    if [[ "$api_health" != "healthy" ]]; then
        OVERALL_HEALTH="degraded"
    fi
}

# プロセス健全性チェック
check_processes() {
    log_info "=== プロセス健全性チェック ==="
    
    local process_health="healthy"
    
    # メモリ使用量チェック
    if command -v free >/dev/null 2>&1; then
        local memory_usage=$(free | grep Mem | awk '{printf "%.0f", $3/$2 * 100}')
        log_info "メモリ使用量: ${memory_usage}%"
        
        if [[ $memory_usage -gt 90 ]]; then
            log_warn "⚠️ メモリ使用量高: ${memory_usage}%"
            ISSUES_FOUND+=("high_memory_usage")
        fi
    fi
    
    # Pythonプロセス数チェック
    local python_processes=$(pgrep -f python | wc -l)
    log_info "Pythonプロセス数: $python_processes"
    
    if [[ $python_processes -gt 20 ]]; then
        log_warn "⚠️ Pythonプロセス数多: $python_processes"
        ISSUES_FOUND+=("many_python_processes")
    fi
    
    HEALTH_STATUS["processes"]="$process_health"
}

# システム復旧提案
suggest_recovery_actions() {
    if [[ ${#ISSUES_FOUND[@]} -eq 0 ]]; then
        return
    fi
    
    log_info "=== 復旧アクション提案 ==="
    
    for issue in "${ISSUES_FOUND[@]}"; do
        case "$issue" in
            "tmux_session_missing_"*)
                log_info "💡 TMUXセッション復旧: ./auto-connection-recovery.sh"
                ;;
            "agent_non_responsive_"*)
                log_info "💡 エージェント復旧: 接続確認"
                ;;
            "large_queue_files")
                log_info "💡 キューファイル清理: ./log-rotation.sh --emergency"
                ;;
            "disk_usage_"*)
                log_info "💡 ディスク清理: ./log-rotation.sh --emergency"
                ;;
            "large_log_files")
                log_info "💡 ログ清理: ./log-rotation.sh"
                ;;
            "api_config_missing_"*)
                log_info "💡 API設定確認: .envファイル設定を確認"
                ;;
            *)
                log_info "💡 $issue: 手動確認が必要"
                ;;
        esac
    done
}

# ヘルスレポート生成
generate_health_report() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    cat > "$HEALTH_LOG" << EOF
# システムヘルスチェックレポート
生成日時: $timestamp
総合健全性: $OVERALL_HEALTH

## コンポーネント別状態
EOF
    
    for component in "${!HEALTH_STATUS[@]}"; do
        echo "- $component: ${HEALTH_STATUS[$component]}" >> "$HEALTH_LOG"
    done
    
    if [[ ${#ISSUES_FOUND[@]} -gt 0 ]]; then
        echo "" >> "$HEALTH_LOG"
        echo "## 検出された問題" >> "$HEALTH_LOG"
        for issue in "${ISSUES_FOUND[@]}"; do
            echo "- $issue" >> "$HEALTH_LOG"
        done
    fi
    
    log_info "ヘルスレポート保存: $HEALTH_LOG"
}

# メインヘルスチェック実行
execute_health_check() {
    log_info "🏥 システムヘルスチェック開始"
    
    # 各コンポーネントチェック実行
    check_tmux_sessions
    check_message_queue
    check_filesystem
    check_api_connectivity
    check_processes
    
    # 結果サマリー
    echo ""
    log_info "=== ヘルスチェック結果サマリー ==="
    
    case "$OVERALL_HEALTH" in
        "healthy")
            log_success "🟢 システム状態: 正常"
            ;;
        "degraded")
            log_warn "🟡 システム状態: 一部問題あり"
            ;;
        "critical")
            log_critical "🔴 システム状態: 緊急対応必要"
            ;;
    esac
    
    echo "検出された問題数: ${#ISSUES_FOUND[@]}"
    
    # 復旧提案
    suggest_recovery_actions
    
    # レポート生成
    generate_health_report
    
    # 終了コード設定
    case "$OVERALL_HEALTH" in
        "healthy") return 0 ;;
        "degraded") return 1 ;;
        "critical") return 2 ;;
    esac
}

# 自動復旧実行
execute_auto_recovery() {
    log_info "🔧 自動復旧機能実行"
    
    # まずヘルスチェック実行
    execute_health_check
    
    if [[ ${#ISSUES_FOUND[@]} -eq 0 ]]; then
        log_success "復旧不要: システム正常"
        return 0
    fi
    
    # 自動復旧可能な問題の対処
    for issue in "${ISSUES_FOUND[@]}"; do
        case "$issue" in
            "large_queue_files"|"large_log_files"|"disk_usage_high")
                log_info "ログローテーション実行中..."
                ./log-rotation.sh --emergency
                ;;
            "tmux_session_missing_"*|"agent_non_responsive_"*)
                log_info "接続復旧実行中..."
                ./auto-connection-recovery.sh
                ;;
        esac
    done
    
    # 復旧後再チェック
    log_info "復旧後再チェック実行中..."
    execute_health_check
}

# 使用法表示
show_usage() {
    cat << EOF
🏥 システムヘルスチェック統合スクリプト

使用法:
  $0                    # 基本ヘルスチェック実行
  $0 --check           # 詳細ヘルスチェック
  $0 --auto-recovery   # 自動復旧付きチェック
  $0 --monitor         # 継続監視モード
  $0 --report          # レポートのみ表示
  $0 --help            # このヘルプを表示

チェック項目:
  - TMUXセッション状態
  - エージェント応答性
  - メッセージキューシステム
  - ファイルシステム健全性
  - API接続設定
  - プロセス状態

終了コード:
  0: 正常
  1: 一部問題あり
  2: 緊急対応必要
EOF
}

# メイン処理
main() {
    # ベースディレクトリ移動
    cd "$BASE_DIR" 2>/dev/null || true
    
    case "${1:-}" in
        "--check")
            execute_health_check
            ;;
        "--auto-recovery")
            execute_auto_recovery
            ;;
        "--monitor")
            log_info "継続監視モード開始（Ctrl+Cで停止）"
            while true; do
                execute_health_check
                echo "次回チェックまで300秒待機..."
                sleep 300
            done
            ;;
        "--report")
            if [[ -f "$HEALTH_LOG" ]]; then
                cat "$HEALTH_LOG"
            else
                log_error "ヘルスレポートが見つかりません"
                exit 1
            fi
            ;;
        "--help"|"-h")
            show_usage
            ;;
        "")
            execute_health_check
            ;;
        *)
            log_error "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"