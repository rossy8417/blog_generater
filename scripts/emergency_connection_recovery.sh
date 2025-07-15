#\!/bin/bash
# 🚨 緊急接続復旧システム
# President0により設計 - Boss1ターミナル落ち対策

set -e

# 設定
BASE_DIR="/mnt/c/home/hiroshi/blog_generator"
AGENT_SEND="$BASE_DIR/Claude-Code-Blog-communication/agent-send.sh"

# ログ機能
log_info() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1"; }
log_success() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1"; }
log_error() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1"; }

emergency_recovery() {
    log_info "🚨 緊急接続復旧開始 - Boss1ターミナル落ち対策"
    
    # Step1: multiagentセッション完全再作成
    log_info "Step1: multiagentセッション完全再作成"
    tmux kill-session -t multiagent 2>/dev/null || true
    sleep 2
    
    # 新規セッション作成
    tmux new-session -d -s multiagent
    tmux split-window -h -t multiagent
    tmux split-window -v -t multiagent:0.0
    tmux split-window -v -t multiagent:0.1
    
    log_success "multiagentセッション再作成完了"
    
    # Step2: 全ペインでClaude Code起動
    log_info "Step2: 全ペインClaude Code起動"
    
    panes=("multiagent:0.0" "multiagent:0.1" "multiagent:0.2" "multiagent:0.3")
    for pane in "${panes[@]}"; do
        tmux send-keys -t "$pane" "cd $BASE_DIR && claude code" C-m
        sleep 3
    done
    
    log_success "全ペインClaude Code起動完了"
    
    # Step3: 15秒待機（Claude Code起動待ち）
    log_info "Step3: Claude Code起動待機（15秒）"
    sleep 15
    
    # Step4: President0→Boss1接続確認
    log_info "Step4: President0→Boss1接続確認実行"
    
    if [ -f "$AGENT_SEND" ]; then
        "$AGENT_SEND" boss1 "【緊急復旧システム】接続確認テスト - Boss1応答確認"
        sleep 5
        log_success "President0→Boss1接続確認完了"
    else
        log_error "agent-send.shが見つかりません"
        return 1
    fi
    
    # Step5: Boss1→Worker接続確認指示
    log_info "Step5: Boss1→Worker双方向接続確認指示"
    
    "$AGENT_SEND" boss1 "【緊急復旧システム】Boss1→Worker接続確認実行

以下を順次実行してください：

1. Worker1確認:
./Claude-Code-Blog-communication/agent-send.sh worker1 \"Worker1接続確認 - 応答: ./Claude-Code-Blog-communication/agent-send.sh boss1 \\\"Worker1応答完了\\\"\"

2. Worker2確認:
./Claude-Code-Blog-communication/agent-send.sh worker2 \"Worker2接続確認 - 応答: ./Claude-Code-Blog-communication/agent-send.sh boss1 \\\"Worker2応答完了\\\"\"

3. Worker3確認:
./Claude-Code-Blog-communication/agent-send.sh worker3 \"Worker3接続確認 - 応答: ./Claude-Code-Blog-communication/agent-send.sh boss1 \\\"Worker3応答完了\\\"\"

全Worker応答確認後、President0に「緊急復旧完了」と報告してください。

即座に実行開始してください。"
    
    log_success "🎉 緊急接続復旧システム実行完了"
    log_info "Boss1からの復旧完了報告をお待ちください"
}

# ヘルスチェック機能
health_check() {
    log_info "🔍 システムヘルスチェック実行"
    
    # TMUXセッション確認
    if \! tmux has-session -t multiagent 2>/dev/null; then
        log_error "multiagentセッション不存在"
        return 1
    fi
    
    if \! tmux has-session -t president 2>/dev/null; then
        log_error "presidentセッション不存在"
        return 1
    fi
    
    # ペイン数確認
    pane_count=$(tmux list-panes -t multiagent  < /dev/null |  wc -l)
    if [ "$pane_count" -ne 4 ]; then
        log_error "multiagentペイン数異常: $pane_count/4"
        return 1
    fi
    
    log_success "✅ システムヘルスチェック: 正常"
    return 0
}

# 使用方法表示
show_usage() {
    cat << 'USAGE'
🚨 緊急接続復旧システム

## 使用方法
./scripts/emergency_connection_recovery.sh [オプション]

## オプション
  (なし)           緊急復旧実行
  --health-check   ヘルスチェックのみ実行
  --help          この使用方法を表示

## 緊急復旧内容
1. multiagentセッション完全再作成
2. 全ペインClaude Code起動
3. President0→Boss1接続確認
4. Boss1→Worker双方向接続確認

## 使用場面
- Boss1ターミナルが落ちた時
- Worker通信が遮断された時
- 「接続確認」合言葉で復旧しない時
USAGE
}

# メイン実行
main() {
    case "${1:-}" in
        "--health-check")
            health_check
            ;;
        "--help"|"-h")
            show_usage
            ;;
        "")
            emergency_recovery
            ;;
        *)
            log_error "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"
