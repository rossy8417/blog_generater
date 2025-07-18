#!/bin/bash

# 🔄 Multi-Agent Auto Monitor & Recovery System
# 停滞検出・自動復旧システム

set -e

# 設定
MONITOR_INTERVAL=120  # 2分間隔でチェック
TIMEOUT_THRESHOLD=600  # 10分で停滞判定
RECOVERY_ATTEMPTS=3   # 復旧試行回数
LOG_DIR="logs"
STATUS_DIR="tmp"

# 色付きログ関数
log_info() {
    echo -e "\033[1;32m[INFO]\033[0m $1"
}

log_warn() {
    echo -e "\033[1;33m[WARN]\033[0m $1"
}

log_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

log_success() {
    echo -e "\033[1;34m[SUCCESS]\033[0m $1"
}

# 初期化
init_monitor() {
    mkdir -p "$LOG_DIR" "$STATUS_DIR"
    
    # 監視状態ファイル初期化
    echo "$(date +%s)" > "$STATUS_DIR/monitor_start.txt"
    echo "0" > "$STATUS_DIR/last_activity.txt"
    echo "idle" > "$STATUS_DIR/project_phase.txt"
    
    log_info "🔄 Auto Monitor システム開始"
    log_info "監視間隔: ${MONITOR_INTERVAL}秒"
    log_info "停滞判定: ${TIMEOUT_THRESHOLD}秒"
}

# エージェント活動検出
detect_agent_activity() {
    local current_time=$(date +%s)
    local activity_detected=false
    
    # tmux画面の変化を検出
    for agent in "multiagent:0.0" "multiagent:0.1" "multiagent:0.2" "multiagent:0.3"; do
        if tmux has-session -t multiagent 2>/dev/null; then
            # 画面内容を取得
            local current_content=$(tmux capture-pane -t "$agent" -p 2>/dev/null || echo "")
            local content_hash=$(echo "$current_content" | md5sum | cut -d' ' -f1)
            local last_hash_file="$STATUS_DIR/$(echo $agent | tr ':' '_')_hash.txt"
            
            if [ -f "$last_hash_file" ]; then
                local last_hash=$(cat "$last_hash_file" 2>/dev/null || echo "")
                if [ "$content_hash" != "$last_hash" ]; then
                    activity_detected=true
                    echo "$current_time" > "$STATUS_DIR/last_activity.txt"
                    log_info "活動検出: $agent"
                fi
            fi
            
            echo "$content_hash" > "$last_hash_file"
        fi
    done
    
    # ファイル変更検出
    local file_patterns=("outputs/*" "tmp/*_done.txt" "tmp/*_phase3_done.txt")
    for pattern in "${file_patterns[@]}"; do
        if [ "$(find $pattern -newer "$STATUS_DIR/last_activity.txt" 2>/dev/null | wc -l)" -gt 0 ]; then
            activity_detected=true
            echo "$current_time" > "$STATUS_DIR/last_activity.txt"
            log_info "ファイル変更検出: $pattern"
        fi
    done
    
    return $([ "$activity_detected" = true ] && echo 0 || echo 1)
}

# 停滞検出
detect_stagnation() {
    local current_time=$(date +%s)
    local last_activity=$(cat "$STATUS_DIR/last_activity.txt" 2>/dev/null || echo "$current_time")
    local time_diff=$((current_time - last_activity))
    
    if [ $time_diff -gt $TIMEOUT_THRESHOLD ]; then
        log_warn "🚨 停滞検出: ${time_diff}秒間活動なし"
        return 0
    fi
    
    return 1
}

# プロジェクト進捗状況判定
get_project_status() {
    local status="idle"
    
    # Phase判定
    if [ -f "outputs/*/outline_content.md" ] 2>/dev/null; then
        status="phase2"  # 章執筆フェーズ
        
        if [ -f "tmp/worker1_done.txt" ] && [ -f "tmp/worker2_done.txt" ] && [ -f "tmp/worker3_done.txt" ]; then
            status="phase3"  # 画像生成フェーズ
            
            if [ -f "tmp/worker1_phase3_done.txt" ] && [ -f "tmp/worker2_phase3_done.txt" ] && [ -f "tmp/worker3_phase3_done.txt" ]; then
                status="completion"  # 完了フェーズ
            fi
        fi
    fi
    
    echo "$status" > "$STATUS_DIR/project_phase.txt"
    echo "$status"
}

# フェーズ別自動復旧
auto_recovery() {
    local phase=$(get_project_status)
    local attempt_count=$(cat "$STATUS_DIR/recovery_attempts.txt" 2>/dev/null || echo "0")
    
    if [ $attempt_count -ge $RECOVERY_ATTEMPTS ]; then
        log_error "❌ 復旧試行回数上限に達しました。手動介入が必要です。"
        return 1
    fi
    
    log_info "🔧 自動復旧開始 (フェーズ: $phase, 試行: $((attempt_count + 1)))"
    
    case "$phase" in
        "idle")
            recovery_idle_phase
            ;;
        "phase2") 
            recovery_phase2
            ;;
        "phase3")
            recovery_phase3
            ;;
        "completion")
            recovery_completion_phase
            ;;
        *)
            log_warn "不明なフェーズ: $phase"
            ;;
    esac
    
    echo $((attempt_count + 1)) > "$STATUS_DIR/recovery_attempts.txt"
}

# Idle フェーズ復旧
recovery_idle_phase() {
    log_info "アイドル状態からの復旧..."
    
    # Boss1にステータス確認
    ./agent-send.sh boss1 "【自動監視システム】現在の作業状況を報告してください。

## 確認事項
- 現在実行中のタスク
- 待機している理由
- 次に必要なアクション

30秒以内に応答してください。"
}

# Phase2 復旧
recovery_phase2() {
    log_info "Phase2 (章執筆) 復旧中..."
    
    # 未完了workerの特定と催促
    local pending_workers=()
    
    for worker in worker1 worker2 worker3; do
        if [ ! -f "tmp/${worker}_done.txt" ]; then
            pending_workers+=("$worker")
        fi
    done
    
    if [ ${#pending_workers[@]} -gt 0 ]; then
        log_info "未完了worker検出: ${pending_workers[*]}"
        
        for worker in "${pending_workers[@]}"; do
            ./agent-send.sh "$worker" "【自動監視システム】執筆作業の進捗を確認します。

## 緊急確認
- 現在の執筆進捗 (0-100%)
- 困っている点
- 完了予定時刻

## 問題がある場合
「サポート要請」と返答してください。即座に対応します。

30秒以内に応答してください。"
        done
    else
        # 全worker完了済みなのにBoss1が統合していない
        ./agent-send.sh boss1 "【自動監視システム】全worker執筆完了済みです。

Phase2統合作業（リード文・まとめ・記事統合）を即座に実行してください。"
    fi
}

# Phase3 復旧
recovery_phase3() {
    log_info "Phase3 (画像生成) 復旧中..."
    
    # 未完了画像タスクの特定
    local pending_image_workers=()
    
    for worker in worker1 worker2 worker3; do
        if [ ! -f "tmp/${worker}_phase3_done.txt" ]; then
            pending_image_workers+=("$worker")
        fi
    done
    
    if [ ${#pending_image_workers[@]} -gt 0 ]; then
        log_info "未完了画像worker検出: ${pending_image_workers[*]}"
        
        # Worker別の直接指示
        for worker in "${pending_image_workers[@]}"; do
            case "$worker" in
                "worker1")
                    ./agent-send.sh worker1 "【自動復旧】アイキャッチ生成を即座に実行してください。

手順: python scripts/image_generator.py --mode eyecatch
完了後: ./agent-send.sh boss1 \"Worker1アイキャッチ完了\""
                    ;;
                "worker2")
                    ./agent-send.sh worker2 "【自動復旧】第1-3章画像生成を即座に実行してください。

手順: python scripts/image_generator.py --mode thumbnails --chapters 1,2,3
完了後: ./agent-send.sh boss1 \"Worker2画像完了\""
                    ;;
                "worker3")
                    ./agent-send.sh worker3 "【自動復旧】第4-6章画像生成を即座に実行してください。

手順: python scripts/image_generator.py --mode thumbnails --chapters 4,5,6
完了後: ./agent-send.sh boss1 \"Worker3画像完了\""
                    ;;
            esac
        done
    else
        # 全画像完了済みなのにWordPress投稿していない
        ./agent-send.sh boss1 "【自動監視システム】全画像生成完了済みです。

WordPress投稿を即座に実行してください:
python scripts/post_blog_universal.py"
    fi
}

# Completion フェーズ復旧
recovery_completion_phase() {
    log_info "完了フェーズ確認中..."
    
    if [ ! -f "tmp/wordpress_post_info.txt" ]; then
        ./agent-send.sh boss1 "【自動監視システム】WordPress投稿が未完了です。

python scripts/post_blog_universal.py を実行してください。"
    else
        log_success "✅ プロジェクト完了確認済み"
        echo "completed" > "$STATUS_DIR/project_phase.txt"
    fi
}

# 緊急停止条件チェック
check_emergency_conditions() {
    # tmuxセッション死活確認
    if ! tmux has-session -t multiagent 2>/dev/null; then
        log_error "🚨 multiagentセッションが存在しません"
        return 1
    fi
    
    # 必須ファイル確認
    local required_files=("agent-send.sh" "scripts/image_generator.py" "scripts/post_blog_universal.py")
    for file in "${required_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "🚨 必須ファイル不足: $file"
            return 1
        fi
    done
    
    return 0
}

# 定期レポート生成
generate_status_report() {
    local current_time=$(date '+%Y-%m-%d %H:%M:%S')
    local phase=$(cat "$STATUS_DIR/project_phase.txt" 2>/dev/null || echo "unknown")
    local last_activity=$(cat "$STATUS_DIR/last_activity.txt" 2>/dev/null || echo "0")
    local time_since_activity=$(( $(date +%s) - last_activity ))
    
    cat > "$LOG_DIR/monitor_status.txt" << EOF
# Auto Monitor Status Report
Generated: $current_time

## Current Status
- Project Phase: $phase
- Time Since Last Activity: ${time_since_activity}s
- Monitor Running: $(( $(date +%s) - $(cat "$STATUS_DIR/monitor_start.txt") ))s

## File Status
$(ls -la tmp/*_done.txt tmp/*_phase3_done.txt 2>/dev/null || echo "No completion files found")

## Output Status
$(ls -la outputs/ 2>/dev/null || echo "No outputs found")

## Recovery Attempts
$(cat "$STATUS_DIR/recovery_attempts.txt" 2>/dev/null || echo "0")

EOF
}

# メイン監視ループ
monitor_loop() {
    log_info "🔄 監視ループ開始"
    
    while true; do
        # 緊急停止条件チェック
        if ! check_emergency_conditions; then
            log_error "緊急停止条件検出。監視を終了します。"
            break
        fi
        
        # 活動検出
        if detect_agent_activity; then
            echo "0" > "$STATUS_DIR/recovery_attempts.txt"  # 復旧カウンターリセット
        fi
        
        # 停滞検出と自動復旧
        if detect_stagnation; then
            auto_recovery
        fi
        
        # 定期レポート生成
        generate_status_report
        
        sleep $MONITOR_INTERVAL
    done
}

# シグナルハンドリング
cleanup() {
    log_info "🛑 監視システム終了中..."
    echo "stopped" > "$STATUS_DIR/monitor_status.txt"
    exit 0
}

trap cleanup SIGTERM SIGINT

# メイン実行
main() {
    case "${1:-start}" in
        "start")
            init_monitor
            monitor_loop
            ;;
        "status")
            if [ -f "$LOG_DIR/monitor_status.txt" ]; then
                cat "$LOG_DIR/monitor_status.txt"
            else
                echo "監視システムが実行されていません"
            fi
            ;;
        "stop")
            if pgrep -f "auto-monitor.sh" >/dev/null; then
                pkill -f "auto-monitor.sh"
                log_success "監視システムを停止しました"
            else
                log_info "監視システムは実行されていません"
            fi
            ;;
        *)
            echo "Usage: $0 {start|status|stop}"
            exit 1
            ;;
    esac
}

main "$@"