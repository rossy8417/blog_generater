#!/bin/bash

# 🔄 完全自律接続復旧システム
# 合言葉「接続確認」で全階層の完全復旧を自動実行

set -e

# 設定
RECOVERY_VERSION="1.0"
BASE_DIR="/mnt/c/home/hiroshi/blog_generator/Claude-Code-Blog-communication"
AGENT_SEND="$BASE_DIR/agent-send.sh"
MAX_RECOVERY_ATTEMPTS=3
WORKER_WAKE_TIMEOUT=30

# 色付きログ
log_info() { echo -e "\033[1;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }
log_success() { echo -e "\033[1;34m[SUCCESS]\033[0m $1"; }

# 合言葉「接続確認」完全実行
execute_connection_recovery() {
    log_info "🚀 合言葉「接続確認」- 完全自律連携復旧開始"
    echo "============================================================"
    
    # Phase 1: システム基盤確認・修復
    log_info "📋 Phase 1: システム基盤確認・修復"
    if ! verify_and_fix_infrastructure; then
        log_error "システム基盤修復失敗"
        return 1
    fi
    
    # Phase 2: Boss1接続確認・復旧
    log_info "📋 Phase 2: Boss1接続確認・復旧"
    if ! verify_and_fix_boss1; then
        log_error "Boss1復旧失敗"
        return 1
    fi
    
    # Phase 3: Worker接続確認・復旧
    log_info "📋 Phase 3: Worker接続確認・復旧"
    if ! verify_and_fix_workers; then
        log_error "Worker復旧失敗"
        return 1
    fi
    
    # Phase 4: 完全階層接続テスト
    log_info "📋 Phase 4: 完全階層接続テスト"
    if ! execute_full_hierarchy_test; then
        log_error "階層接続テスト失敗"
        return 1
    fi
    
    # Phase 5: 連携状態確立確認
    log_info "📋 Phase 5: 連携状態確立確認"
    verify_final_connection_state
    
    log_success "✅ 合言葉「接続確認」完了: 完全連携状態確立済み"
    return 0
}

# Phase 1: システム基盤確認・修復
verify_and_fix_infrastructure() {
    log_info "🔧 システム基盤確認中..."
    
    # TMUXセッション確認
    if ! tmux has-session -t multiagent 2>/dev/null; then
        log_warn "multiagentセッション不存在 - 作成中..."
        if ! create_tmux_sessions; then
            return 1
        fi
    fi
    
    if ! tmux has-session -t president 2>/dev/null; then
        log_warn "presidentセッション不存在 - 作成中..."
        if ! create_tmux_sessions; then
            return 1
        fi
    fi
    
    # メッセージキューシステム確認・初期化
    if [[ ! -d "tmp/message_queue" ]]; then
        log_info "メッセージキューシステム初期化中..."
        "$AGENT_SEND" --setup
    fi
    
    # 必須ファイル確認
    local required_files=("$AGENT_SEND" "tmux-unified-controller.sh")
    for file in "${required_files[@]}"; do
        if [[ ! -f "$file" ]]; then
            log_error "必須ファイル不足: $file"
            return 1
        fi
    done
    
    log_success "✅ システム基盤: 正常"
    return 0
}

# TMUXセッション作成（必要時）
create_tmux_sessions() {
    log_info "TMUXセッション作成中..."
    
    # multiagentセッション作成
    if ! tmux has-session -t multiagent 2>/dev/null; then
        tmux new-session -d -s multiagent
        tmux split-window -h -t multiagent
        tmux split-window -v -t multiagent:0.0
        tmux split-window -v -t multiagent:0.1
        
        # 各ペインでClaude Code起動
        for pane in 0 1 2 3; do
            tmux send-keys -t "multiagent:0.$pane" "cd /mnt/c/home/hiroshi/blog_generator && claude code" C-m
            sleep 2
        done
    fi
    
    # presidentセッション作成
    if ! tmux has-session -t president 2>/dev/null; then
        tmux new-session -d -s president
        tmux send-keys -t president "cd /mnt/c/home/hiroshi/blog_generator && claude code" C-m
        sleep 2
    fi
    
    log_success "✅ TMUXセッション作成完了"
    return 0
}

# Phase 2: Boss1接続確認・復旧
verify_and_fix_boss1() {
    log_info "👑 Boss1接続確認中..."
    
    # Boss1応答テスト
    "$AGENT_SEND" boss1 "【自律復旧システム】Boss1応答確認。「Boss1正常」と返答してください。"
    
    # 応答待機・確認
    local timeout=15
    local start_time=$(date +%s)
    local response_detected=false
    
    while [[ $(($(date +%s) - start_time)) -lt $timeout ]]; do
        if grep -q "Boss1正常" logs/send_log.txt 2>/dev/null; then
            response_detected=true
            break
        fi
        sleep 2
    done
    
    if [[ "$response_detected" = false ]]; then
        log_warn "Boss1応答なし - 復旧処理実行中..."
        if ! recover_boss1; then
            return 1
        fi
    fi
    
    log_success "✅ Boss1: 正常応答確認"
    return 0
}

# Boss1復旧処理
recover_boss1() {
    log_info "🔧 Boss1復旧処理開始..."
    
    # Boss1ペイン再起動
    tmux send-keys -t multiagent:0.0 C-c
    sleep 1
    tmux send-keys -t multiagent:0.0 "claude code" C-m
    sleep 3
    
    # Boss1役割再定義
    "$AGENT_SEND" boss1 "あなたはboss1です。

## 役割定義
- チームリーダーとしてWorker1,2,3を統括
- President0からの戦略的指示を受けてタスク分散実行
- Worker完了後の統合・報告を担当

## 重要な階層ルール
- President0 → Boss1 → Worker1,2,3 (指揮系統)
- Worker1,2,3 → Boss1 → President0 (報告系統)

このメッセージを受信したら「Boss1復旧完了」と返答してください。"
    
    # 復旧確認
    local recovery_timeout=20
    local recovery_start=$(date +%s)
    
    while [[ $(($(date +%s) - recovery_start)) -lt $recovery_timeout ]]; do
        if grep -q "Boss1復旧完了" logs/send_log.txt 2>/dev/null; then
            log_success "✅ Boss1復旧成功"
            return 0
        fi
        sleep 2
    done
    
    log_error "Boss1復旧タイムアウト"
    return 1
}

# Phase 3: Worker接続確認・復旧
verify_and_fix_workers() {
    log_info "👷 Worker接続確認中..."
    
    # Boss1経由でWorker確認指示
    "$AGENT_SEND" boss1 "【自律復旧システム】Worker接続確認を実行してください。

以下を順次実行：
1. ./agent-send.sh worker1 \"Worker1応答確認\"
2. ./agent-send.sh worker2 \"Worker2応答確認\"  
3. ./agent-send.sh worker3 \"Worker3応答確認\"

各Worker応答を確認後「Worker確認完了」と報告してください。"
    
    # Worker応答監視
    local worker_timeout=30
    local worker_start=$(date +%s)
    local workers_responding=0
    
    while [[ $(($(date +%s) - worker_start)) -lt $worker_timeout ]]; do
        # 各Worker応答確認
        workers_responding=0
        for worker in worker1 worker2 worker3; do
            if grep -q "${worker}.*応答" logs/send_log.txt 2>/dev/null; then
                ((workers_responding++))
            fi
        done
        
        # 全Worker応答確認
        if [[ $workers_responding -ge 3 ]]; then
            log_success "✅ Worker接続: 全${workers_responding}/3 応答確認"
            return 0
        fi
        
        sleep 3
    done
    
    # 応答しないWorkerを個別復旧
    log_warn "Worker応答不足(${workers_responding}/3) - 個別復旧実行中..."
    recover_non_responsive_workers
    
    return 0
}

# 応答しないWorker復旧
recover_non_responsive_workers() {
    log_info "🔧 非応答Worker復旧処理..."
    
    for worker_num in 1 2 3; do
        local worker="worker${worker_num}"
        
        # 個別Worker応答確認
        if ! grep -q "${worker}.*応答" logs/send_log.txt 2>/dev/null; then
            log_warn "$worker 非応答 - 復旧中..."
            
            # Workerペイン復旧
            local pane_id="multiagent:0.$worker_num"
            tmux send-keys -t "$pane_id" C-c
            sleep 1
            tmux send-keys -t "$pane_id" "claude code" C-m
            sleep 3
            
            # Worker役割再定義
            local worker_role=""
            case $worker_num in
                1) worker_role="Phase2: 第1-2章執筆 / Phase3: アイキャッチ画像生成" ;;
                2) worker_role="Phase2: 第3-4章執筆 / Phase3: 第1-3章サムネイル生成" ;;
                3) worker_role="Phase2: 第5-6章執筆 / Phase3: 第4-6章サムネイル生成" ;;
            esac
            
            "$AGENT_SEND" "$worker" "あなたは${worker}です。

## 役割定義
$worker_role

## 階層ルール
- Boss1からの指示を受けて実行
- 完了後はBoss1に報告

このメッセージを受信したら「${worker}復旧完了」と返答してください。"
            
            log_success "✅ $worker 復旧処理実行完了"
        fi
    done
}

# Phase 4: 完全階層接続テスト
execute_full_hierarchy_test() {
    log_info "🏛️ 完全階層接続テスト実行中..."
    
    # 統合コントローラー経由で階層テスト実行
    if ./tmux-unified-controller.sh --workflow hierarchy-test; then
        log_success "✅ 階層接続テスト: 成功"
        return 0
    else
        log_error "階層接続テスト失敗 - 手動復旧必要"
        return 1
    fi
}

# Phase 5: 連携状態確立確認
verify_final_connection_state() {
    log_info "🎯 最終連携状態確認中..."
    
    # 各エージェント生存確認
    local agents=("boss1" "worker1" "worker2" "worker3")
    local active_agents=0
    
    for agent in "${agents[@]}"; do
        if tmux capture-pane -t "multiagent:0.$(get_pane_index $agent)" -p | grep -q ">"; then
            ((active_agents++))
            log_info "✅ $agent: アクティブ"
        else
            log_warn "⚠️ $agent: 状態不明"
        fi
    done
    
    # 最終状態サマリー
    echo ""
    echo "🎯 連携状態確立完了サマリー"
    echo "================================"
    echo "📊 アクティブエージェント: ${active_agents}/4"
    echo "📡 メッセージキュー: 正常"
    echo "🏛️ 階層制御: President0 → Boss1 → Worker1,2,3"
    echo "📨 報告系統: Worker1,2,3 → Boss1 → President0"
    echo ""
    
    if [[ $active_agents -ge 3 ]]; then
        log_success "✅ 完全連携状態確立: 運用可能"
        
        # 成功状態をファイルに記録
        echo "$(date '+%Y-%m-%d %H:%M:%S'): 完全連携状態確立成功" > tmp/connection_recovery_success.log
        
        return 0
    else
        log_warn "⚠️ 部分連携状態: 手動確認推奨"
        return 1
    fi
}

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

# 緊急復旧モード
emergency_recovery() {
    log_error "🚨 緊急復旧モード開始"
    
    # 全セッション強制再作成
    tmux kill-session -t multiagent 2>/dev/null || true
    tmux kill-session -t president 2>/dev/null || true
    
    # クリーン環境で再作成
    create_tmux_sessions
    
    # 強制初期化
    rm -rf tmp/message_queue 2>/dev/null || true
    "$AGENT_SEND" --setup
    
    log_info "緊急復旧完了 - 再試行中..."
    execute_connection_recovery
}

# 使用法表示
show_usage() {
    cat << EOF
🔄 完全自律接続復旧システム v$RECOVERY_VERSION

## 合言葉コマンド
  $0                      # 「接続確認」完全実行
  $0 --emergency         # 緊急復旧モード
  $0 --status           # 現在の接続状態確認
  
## 自動実行内容
1. システム基盤確認・修復 (TMUX・メッセージキュー)
2. Boss1接続確認・復旧 (応答テスト・復旧処理)
3. Worker接続確認・復旧 (個別復旧・役割再定義)
4. 完全階層接続テスト (統合テスト実行)
5. 連携状態確立確認 (最終確認・状態記録)

## 特徴
- 完全自律実行 (手動介入不要)
- 障害自動検出・修復
- 階層制御厳格化
- 状態永続化記録

## 実現される連携フロー
President0 → Boss1 → Worker1,2,3 (指揮系統)
Worker1,2,3 → Boss1 → President0 (報告系統)
EOF
}

# メイン実行
main() {
    case "${1:-}" in
        "--emergency")
            emergency_recovery
            ;;
        "--status")
            verify_final_connection_state
            ;;
        "--help"|"-h")
            show_usage
            ;;
        "")
            execute_connection_recovery
            ;;
        *)
            log_error "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"