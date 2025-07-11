#!/bin/bash

# President0 監視システム - Boss1活動監視
# 30分間隔でBoss1の活動状況を監視し、必要に応じて催促

MONITORING_INTERVAL=1800  # 30分 (1800秒)
LAST_ACTIVITY_FILE="./tmp/boss1_last_activity.txt"
MONITORING_LOG="./logs/monitoring_log.txt"

# 監視開始
echo "$(date): President0監視システム開始" >> "$MONITORING_LOG"
echo "監視間隔: ${MONITORING_INTERVAL}秒 (30分)"

while true; do
    echo "$(date): Boss1活動監視中..." >> "$MONITORING_LOG"
    
    # 最新のsend_logを確認
    if [ -f "logs/send_log.txt" ]; then
        LAST_BOSS_ACTIVITY=$(grep -n "boss1: SENT" logs/send_log.txt | tail -1 | cut -d: -f1)
        echo "$LAST_BOSS_ACTIVITY" > "$LAST_ACTIVITY_FILE"
        
        # 30分以上活動なしの場合
        CURRENT_TIME=$(date +%s)
        if [ -f "$LAST_ACTIVITY_FILE" ]; then
            LAST_ACTIVITY_TIME=$(stat -c %Y "$LAST_ACTIVITY_FILE" 2>/dev/null || echo "0")
            TIME_DIFF=$((CURRENT_TIME - LAST_ACTIVITY_TIME))
            
            if [ $TIME_DIFF -gt $MONITORING_INTERVAL ]; then
                echo "$(date): Boss1活動停止検出 - 催促送信" >> "$MONITORING_LOG"
                
                # 催促メッセージ送信
                ./agent-send.sh boss1 "President0監視システムからの催促：

【活動停止警告】
30分以上の活動停止が検出されました。

【即座実行指示】
1. 現在の作業状況を詳細報告
2. 記事ID 2127リライトの継続実行
3. 進捗状況の詳細報告

【重要】
作業が完了していない場合は、即座に継続してください。
問題が発生している場合は、詳細を報告してください。

President0監視システムより"
                
                echo "$(date): 催促メッセージ送信完了" >> "$MONITORING_LOG"
            fi
        fi
    fi
    
    # 次の監視まで待機
    sleep $MONITORING_INTERVAL
done