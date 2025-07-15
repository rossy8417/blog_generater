#\!/bin/bash
# Boss1報告ログ定期自動クリーンアップ
# President0により設計

set -e

# 設定
BASE_DIR="/mnt/c/home/hiroshi/blog_generator"
MESSAGE_QUEUE_DIR="$BASE_DIR/tmp/message_queue"
BACKUP_DIR="$BASE_DIR/tmp/log_backups"
MAX_SIZE_KB=20
RETENTION_LINES=50

# ログ機能
log_info() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1"; }
log_success() { echo "[$(date +'%Y-%m-%d %H:%M:%S')] SUCCESS: $1"; }

# バックアップディレクトリ作成
mkdir -p "$BACKUP_DIR"

log_info "Boss1報告ログ定期クリーンアップ開始"

# 各ログファイルをチェック・クリーンアップ
for log_file in "$MESSAGE_QUEUE_DIR"/*_queue.log; do
    if [ \! -f "$log_file" ]; then
        continue
    fi
    
    filename=$(basename "$log_file")
    size_kb=$(du -k "$log_file"  < /dev/null |  cut -f1)
    
    log_info "チェック中: $filename (${size_kb}KB)"
    
    if [ $size_kb -gt $MAX_SIZE_KB ]; then
        # バックアップ作成
        timestamp=$(date +'%Y%m%d_%H%M%S')
        backup_file="$BACKUP_DIR/${filename%.log}_backup_${timestamp}.log"
        cp "$log_file" "$backup_file"
        log_success "バックアップ作成: $(basename "$backup_file")"
        
        # 最新行のみ保持
        tail -n $RETENTION_LINES "$log_file" > "$log_file.tmp"
        mv "$log_file.tmp" "$log_file"
        
        new_size_kb=$(du -k "$log_file" | cut -f1)
        log_success "クリーンアップ完了: ${size_kb}KB → ${new_size_kb}KB"
    else
        log_info "サイズ適正: ${size_kb}KB ≤ ${MAX_SIZE_KB}KB"
    fi
done

# 7日以上古いバックアップ削除
find "$BACKUP_DIR" -name "*_backup_*.log" -mtime +7 -delete 2>/dev/null || true

log_success "定期ログクリーンアップ完了"
