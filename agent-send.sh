#!/bin/bash

# 🚀 Agent間双方向通信統合システム

# 永続的メッセージキューシステム設定
MESSAGE_QUEUE_DIR="tmp/message_queue"
PRESIDENT_INBOX="$MESSAGE_QUEUE_DIR/president_queue.log"
BOSS1_INBOX="$MESSAGE_QUEUE_DIR/boss1_queue.log"
WORKER1_INBOX="$MESSAGE_QUEUE_DIR/worker1_queue.log"
WORKER2_INBOX="$MESSAGE_QUEUE_DIR/worker2_queue.log"
WORKER3_INBOX="$MESSAGE_QUEUE_DIR/worker3_queue.log"
POLLING_INTERVAL=5

# メッセージキュー初期化
init_message_queues() {
    mkdir -p "$MESSAGE_QUEUE_DIR"
    touch "$PRESIDENT_INBOX" "$BOSS1_INBOX" "$WORKER1_INBOX" "$WORKER2_INBOX" "$WORKER3_INBOX"
    
    # ファイルロック用ディレクトリ
    mkdir -p "$MESSAGE_QUEUE_DIR/locks"
}

# エージェント→tmuxターゲット マッピング
get_agent_target() {
    case "$1" in
        "president") echo "president" ;;
        "boss1") echo "multiagent:0.0" ;;
        "worker1") echo "multiagent:0.1" ;;
        "worker2") echo "multiagent:0.2" ;;
        "worker3") echo "multiagent:0.3" ;;
        *) echo "" ;;
    esac
}

# エージェント→受信ボックス マッピング
get_agent_inbox() {
    case "$1" in
        "president") echo "$PRESIDENT_INBOX" ;;
        "boss1") echo "$BOSS1_INBOX" ;;
        "worker1") echo "$WORKER1_INBOX" ;;
        "worker2") echo "$WORKER2_INBOX" ;;
        "worker3") echo "$WORKER3_INBOX" ;;
        *) echo "" ;;
    esac
}

show_usage() {
    cat << EOF
🤖 Agent間双方向通信統合システム

使用方法:
  $0 [エージェント名] [メッセージ]     - メッセージ送信
  $0 --list                         - エージェント一覧表示
  $0 --monitor [エージェント名]       - 受信監視開始
  $0 --setup                        - 受信ボックス初期化
  $0 --check [エージェント名]         - 受信メッセージ確認

利用可能エージェント:
  president - プロジェクト統括責任者
  boss1     - チームリーダー  
  worker1   - 実行担当者A
  worker2   - 実行担当者B
  worker3   - 実行担当者C

使用例:
  $0 boss1 "Hello World プロジェクト開始指示"
  $0 --monitor president
  $0 --check boss1
EOF
}

# エージェント一覧表示
show_agents() {
    echo "📋 利用可能なエージェント:"
    echo "=========================="
    echo "  president → president:0     (プロジェクト統括責任者)"
    echo "  boss1     → multiagent:0.0  (チームリーダー)"
    echo "  worker1   → multiagent:0.1  (実行担当者A)"
    echo "  worker2   → multiagent:0.2  (実行担当者B)" 
    echo "  worker3   → multiagent:0.3  (実行担当者C)"
}

# ログ記録
log_send() {
    local agent="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    mkdir -p logs
    echo "[$timestamp] $agent: SENT - \"$message\"" >> logs/send_log.txt
}

# メッセージ送信（受信記録統合版）
send_message() {
    local target="$1"
    local message="$2"
    local from_agent="$3"
    
    echo "📤 送信中: $target ← '$message'"
    
    # Claude Codeのプロンプトを一度クリア
    tmux send-keys -t "$target" C-c
    sleep 0.3
    
    # メッセージ送信
    tmux send-keys -t "$target" "$message"
    sleep 0.1
    
    # エンター押下
    tmux send-keys -t "$target" C-m
    sleep 0.5
    
    # 送信確認をステータスファイルに記録
    mkdir -p tmp
    echo "$(date +%s):$target:sent" >> tmp/agent_activity.log
    
    # 受信側にも安全に自動記録（双方向確実性確保）
    if [[ -n "$from_agent" ]]; then
        local target_agent=""
        case "$target" in
            "president") target_agent="president" ;;
            "multiagent:0.0") target_agent="boss1" ;;
            "multiagent:0.1") target_agent="worker1" ;;
            "multiagent:0.2") target_agent="worker2" ;;
            "multiagent:0.3") target_agent="worker3" ;;
        esac
        
        if [[ -n "$target_agent" ]]; then
            local message_entry="$(date '+%Y-%m-%d %H:%M:%S') FROM $from_agent: $message"
            if safe_append_message "$target_agent" "$message_entry"; then
                echo "📨 安全受信記録: $target_agent へ記録完了"
            else
                echo "⚠️ 受信記録失敗: $target_agent"
            fi
        fi
    fi
}

# ターゲット存在確認
check_target() {
    local target="$1"
    local session_name="${target%%:*}"
    
    if ! tmux has-session -t "$session_name" 2>/dev/null; then
        echo "❌ セッション '$session_name' が見つかりません"
        return 1
    fi
    
    return 0
}

# メイン処理
main() {
    if [[ $# -eq 0 ]]; then
        show_usage
        exit 1
    fi
    
    # --listオプション
    if [[ "$1" == "--list" ]]; then
        show_agents
        exit 0
    fi
    
    if [[ $# -lt 2 ]]; then
        show_usage
        exit 1
    fi
    
    local agent_name="$1"
    local message="$2"
    
    # エージェントターゲット取得
    local target
    target=$(get_agent_target "$agent_name")
    
    if [[ -z "$target" ]]; then
        echo "❌ エラー: 不明なエージェント '$agent_name'"
        echo "利用可能エージェント: $0 --list"
        exit 1
    fi
    
    # ターゲット確認
    if ! check_target "$target"; then
        exit 1
    fi
    
    # メッセージ送信（from_agent付き）
    send_message "$target" "$message" "president"
    
    # ログ記録
    log_send "$agent_name" "$message"
    
    echo "✅ 送信完了: $agent_name に '$message'"
    
    return 0
}

# ファイルロック機能
acquire_lock() {
    local lock_file="$MESSAGE_QUEUE_DIR/locks/$1.lock"
    local timeout=10
    local count=0
    
    while [[ $count -lt $timeout ]]; do
        if (set -C; echo $$ > "$lock_file") 2>/dev/null; then
            return 0
        fi
        sleep 0.1
        ((count++))
    done
    return 1
}

release_lock() {
    local lock_file="$MESSAGE_QUEUE_DIR/locks/$1.lock"
    rm -f "$lock_file"
}

# 安全なメッセージ追記
safe_append_message() {
    local agent="$1"
    local message="$2"
    local inbox_file
    inbox_file=$(get_agent_inbox "$agent")
    
    if acquire_lock "$agent"; then
        echo "$message" >> "$inbox_file"
        release_lock "$agent"
        return 0
    else
        echo "❌ ロック取得失敗: $agent"
        return 1
    fi
}

# 永続的受信ボックス初期化
setup_inboxes() {
    init_message_queues
    echo "✅ 永続的メッセージキューシステム初期化完了"
}

# 受信監視
monitor_messages() {
    local agent="$1"
    local inbox_file
    inbox_file=$(get_agent_inbox "$agent")
    
    if [[ -z "$inbox_file" ]]; then
        echo "❌ 不明なエージェント: $agent"
        exit 1
    fi
    
    echo "📡 $agent 受信監視開始..."
    
    while true; do
        if [[ -s "$inbox_file" ]]; then
            echo "📨 新着メッセージ検出:"
            cat "$inbox_file"
            > "$inbox_file"  # メッセージクリア
        fi
        sleep "$POLLING_INTERVAL"
    done
}

# 受信メッセージ確認（永続保存版）
check_messages() {
    local agent="$1"
    local inbox_file
    inbox_file=$(get_agent_inbox "$agent")
    
    if [[ -z "$inbox_file" ]]; then
        echo "❌ 不明なエージェント: $agent"
        exit 1
    fi
    
    if [[ -s "$inbox_file" ]]; then
        echo "📨 $agent 受信メッセージ:"
        cat "$inbox_file"
        
        # バックアップコピー作成（削除防止）
        cp "$inbox_file" "${inbox_file}.backup_$(date +%s)"
    else
        echo "📭 $agent 新着メッセージなし"
    fi
}

# 受信確認付きメッセージ送信（安全版）
send_with_receipt() {
    local to_agent="$1"
    local message="$2"
    local from_agent="$3"
    
    # 送信実行
    local target
    target=$(get_agent_target "$to_agent")
    if [[ -z "$target" ]]; then
        echo "❌ 不明なエージェント: $to_agent"
        return 1
    fi
    
    # メッセージ送信
    send_message "$target" "$message" "$from_agent"
    
    # ログ記録
    log_send "$to_agent" "$message"
    
    echo "✅ 受信確認付き送信完了: $to_agent に '$message'"
}

# 指示出し→報告確認セットワークフロー
command_with_report() {
    local to_agent="$1"
    local command="$2"
    local timeout="${3:-300}"  # 5分デフォルト
    
    echo "🎯 指示出し→報告確認ワークフロー開始"
    echo "📤 指示: $to_agent へ「$command」"
    
    # 指示送信
    main "$to_agent" "$command"
    
    # 報告待機
    local start_time=$(date +%s)
    local inbox_file
    inbox_file=$(get_agent_inbox "president")
    local initial_size=0
    [[ -f "$inbox_file" ]] && initial_size=$(wc -c < "$inbox_file")
    
    echo "📋 報告待機中... (タイムアウト: ${timeout}秒)"
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [[ $elapsed -gt $timeout ]]; then
            echo "⚠️ タイムアウト: $to_agent からの報告がありません"
            echo "🔄 催促送信..."
            main "$to_agent" "【President0催促】前回指示への報告を即座にお願いします: $command"
            return 1
        fi
        
        if [[ -f "$inbox_file" ]]; then
            local current_size=$(wc -c < "$inbox_file")
            if [[ $current_size -gt $initial_size ]]; then
                echo "✅ 報告受信確認！"
                echo "📨 受信内容："
                tail -n 10 "$inbox_file"
                return 0
            fi
        fi
        
        sleep 5
    done
}

# 拡張メイン処理
case "$1" in
    "--monitor") monitor_messages "$2" ;;
    "--setup") setup_inboxes ;;
    "--check") check_messages "$2" ;;
    "--send-with-receipt") send_with_receipt "$2" "$3" "$4" ;;
    "--command-report") command_with_report "$2" "$3" "$4" ;;
    *) main "$@" ;;
esac 