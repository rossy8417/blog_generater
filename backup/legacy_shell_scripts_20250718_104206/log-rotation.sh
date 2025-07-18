#!/bin/bash

# 🔄 ログローテーション自動化スクリプト
# 定期実行でログファイルの肥大化を防止

set -e

# 設定
BASE_DIR="/mnt/c/home/hiroshi/blog_generator"
LOG_DIR="$BASE_DIR/logs"
CLAUDE_LOG_DIR="$BASE_DIR/Claude-Code-Blog-communication/logs"
MAX_SIZE_MB=10
KEEP_FILES=5

# 色付きログ
log_info() { echo -e "\033[1;32m[INFO]\033[0m $1"; }
log_warn() { echo -e "\033[1;33m[WARN]\033[0m $1"; }
log_error() { echo -e "\033[1;31m[ERROR]\033[0m $1"; }
log_success() { echo -e "\033[1;34m[SUCCESS]\033[0m $1"; }

# ファイルサイズチェック（MB単位）
get_file_size_mb() {
    local file="$1"
    if [[ -f "$file" ]]; then
        local size_bytes=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null || echo "0")
        echo $((size_bytes / 1024 / 1024))
    else
        echo "0"
    fi
}

# ログローテーション実行
rotate_log_file() {
    local log_file="$1"
    local max_size="$2"
    local keep_count="$3"
    
    if [[ ! -f "$log_file" ]]; then
        log_warn "ログファイルが存在しません: $log_file"
        return 0
    fi
    
    local current_size=$(get_file_size_mb "$log_file")
    local filename=$(basename "$log_file")
    local dirname=$(dirname "$log_file")
    
    if [[ $current_size -gt $max_size ]]; then
        log_info "ローテーション実行: $filename (${current_size}MB > ${max_size}MB)"
        
        # タイムスタンプ付きバックアップ作成
        local timestamp=$(date +"%Y%m%d_%H%M%S")
        local backup_file="${log_file}.${timestamp}"
        
        # ファイル移動
        mv "$log_file" "$backup_file"
        
        # 圧縮
        if command -v gzip >/dev/null 2>&1; then
            gzip "$backup_file"
            backup_file="${backup_file}.gz"
            log_success "ローテーション完了: $filename -> $(basename "$backup_file")"
        else
            log_success "ローテーション完了: $filename -> $(basename "$backup_file")"
        fi
        
        # 新しいログファイル作成
        touch "$log_file"
        chmod 664 "$log_file" 2>/dev/null || true
        
        # 古いファイル清理
        cleanup_old_rotated_files "$dirname" "$filename" "$keep_count"
        
        return 0
    else
        log_info "ローテーション不要: $filename (${current_size}MB <= ${max_size}MB)"
        return 1
    fi
}

# 古いローテーションファイル清理
cleanup_old_rotated_files() {
    local dir="$1"
    local base_filename="$2"
    local keep_count="$3"
    
    # ローテーションファイル一覧取得（時間順ソート）
    local rotated_files=()
    while IFS= read -r -d $'\0' file; do
        rotated_files+=("$file")
    done < <(find "$dir" -name "${base_filename}.*" -type f -print0 | sort -z)
    
    # 保持数を超えるファイルを削除
    local file_count=${#rotated_files[@]}
    if [[ $file_count -gt $keep_count ]]; then
        local delete_count=$((file_count - keep_count))
        log_info "古いファイル削除: ${delete_count}個"
        
        for ((i=0; i<delete_count; i++)); do
            local old_file="${rotated_files[$i]}"
            rm -f "$old_file"
            log_info "削除: $(basename "$old_file")"
        done
    fi
}

# メインのログローテーション処理
execute_log_rotation() {
    log_info "=== ログローテーション開始 ==="
    
    local rotated_count=0
    
    # 重要ログファイルのローテーション
    local log_files=(
        "$LOG_DIR/send_log.txt"
        "$CLAUDE_LOG_DIR/send_log.txt"
        "$LOG_DIR/error.log"
        "$LOG_DIR/system.log"
    )
    
    for log_file in "${log_files[@]}"; do
        if rotate_log_file "$log_file" "$MAX_SIZE_MB" "$KEEP_FILES"; then
            ((rotated_count++))
        fi
    done
    
    # TMUXメッセージキューログのローテーション
    local queue_dirs=(
        "$BASE_DIR/tmp/message_queue"
        "$BASE_DIR/Claude-Code-Blog-communication/tmp/message_queue"
    )
    
    for queue_dir in "${queue_dirs[@]}"; do
        if [[ -d "$queue_dir" ]]; then
            for queue_log in "$queue_dir"/*.log; do
                if [[ -f "$queue_log" ]]; then
                    if rotate_log_file "$queue_log" 5 3; then  # 5MB, 3世代
                        ((rotated_count++))
                    fi
                fi
            done
        fi
    done
    
    if [[ $rotated_count -gt 0 ]]; then
        log_success "ログローテーション完了: ${rotated_count}ファイル処理"
    else
        log_info "ローテーション対象ファイルなし"
    fi
}

# 緊急清理処理
emergency_cleanup() {
    log_warn "=== 緊急ログ清理開始 ==="
    
    # 大きなファイルを強制ローテーション
    local large_files=()
    while IFS= read -r -d $'\0' file; do
        large_files+=("$file")
    done < <(find "$LOG_DIR" "$CLAUDE_LOG_DIR" -name "*.log" -o -name "*.txt" -size +1M -print0 2>/dev/null)
    
    for large_file in "${large_files[@]}"; do
        log_warn "大容量ファイル強制ローテーション: $(basename "$large_file")"
        rotate_log_file "$large_file" 1 2  # 1MB, 2世代
    done
    
    # 古いファイル削除（7日以上古い）
    find "$LOG_DIR" "$CLAUDE_LOG_DIR" -name "*.log.*" -o -name "*.txt.*" -mtime +7 -delete 2>/dev/null || true
    
    log_success "緊急清理完了"
}

# システム状態確認
check_log_status() {
    log_info "=== ログファイル状態確認 ==="
    
    local total_size=0
    local large_files=0
    
    # 重要ログファイルのチェック
    local log_files=(
        "$LOG_DIR/send_log.txt"
        "$CLAUDE_LOG_DIR/send_log.txt"
        "$LOG_DIR/error.log"
        "$LOG_DIR/system.log"
    )
    
    for log_file in "${log_files[@]}"; do
        if [[ -f "$log_file" ]]; then
            local size_mb=$(get_file_size_mb "$log_file")
            total_size=$((total_size + size_mb))
            
            if [[ $size_mb -gt $MAX_SIZE_MB ]]; then
                log_warn "$(basename "$log_file"): ${size_mb}MB (要ローテーション)"
                ((large_files++))
            else
                log_info "$(basename "$log_file"): ${size_mb}MB (正常)"
            fi
        fi
    done
    
    echo ""
    log_info "総ログサイズ: ${total_size}MB"
    
    if [[ $large_files -gt 0 ]]; then
        log_warn "ローテーション必要ファイル: ${large_files}個"
        return 1
    else
        log_success "全ログファイル正常"
        return 0
    fi
}

# 使用法表示
show_usage() {
    cat << EOF
🔄 ログローテーション自動化スクリプト

使用法:
  $0                     # 通常のログローテーション実行
  $0 --check            # ログファイル状態確認
  $0 --emergency        # 緊急清理実行
  $0 --cron             # cron用（出力最小化）
  $0 --help             # このヘルプを表示

設定:
  最大ファイルサイズ: ${MAX_SIZE_MB}MB
  保持世代数: ${KEEP_FILES}世代
  対象ディレクトリ: $LOG_DIR, $CLAUDE_LOG_DIR

例:
  # 定期実行設定（毎時実行）
  echo "0 * * * * $0 --cron" | crontab -
  
  # 手動状態確認
  $0 --check
EOF
}

# メイン処理
main() {
    case "${1:-}" in
        "--check")
            check_log_status
            ;;
        "--emergency")
            emergency_cleanup
            ;;
        "--cron")
            # cron用（静かな実行）
            exec > /tmp/log_rotation_$(date +%Y%m%d).log 2>&1
            execute_log_rotation
            ;;
        "--help"|"-h")
            show_usage
            ;;
        "")
            execute_log_rotation
            ;;
        *)
            log_error "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
}

main "$@"