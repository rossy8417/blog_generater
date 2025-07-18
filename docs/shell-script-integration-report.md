# 🔧 エージェント通信システム統合ガイド

## 概要

エージェント通信システムが大幅に統合・最適化されました。13個のシェルスクリプトが8個に集約され、重複機能の排除と保守性の向上を実現しています。

## 🎯 統合後のシステム構成

### Tier 1: コア機能
- **`agent-send.sh`** - エージェント間双方向通信の核となるシステム
- **`tmux-unified-controller.sh`** - 最上位統合コントローラー

### Tier 2: 統合システム（新規）
- **`connection-recovery-unified.sh`** - 接続復旧統合システム（3機能統合）
- **`log-management-unified.sh`** - ログ管理統合システム（2機能統合）
- **`monitoring-unified.sh`** - 監視システム統合版（3機能統合）
- **`troubleshooting-workflow.sh`** - トラブルシューティング・ワークフロー管理（新規）

### Tier 3: 専門機能
- **`setup.sh`** - 初期環境構築専用
- **`quality-check.sh`** - 品質検証専用
- **`quick-recovery.sh`** - 緊急復旧専用

## 🚀 主要な改善点

### 1. ファイル数削減
- **38%削減**: 13ファイル → 8ファイル
- 重複機能の完全排除
- 統一インターフェースによるユーザビリティ向上

### 2. 機能統合の詳細

#### 接続復旧統合（3→1）
```bash
# 統合前
auto-connection-recovery.sh      # 通常復旧
emergency_connection_recovery.sh # 緊急復旧
connection-test.sh               # 階層テスト

# 統合後
connection-recovery-unified.sh   # 全機能統合
```

#### ログ管理統合（2→1）
```bash
# 統合前
log-rotation.sh                  # 一般ログローテーション
auto_log_cleanup.sh              # キューログクリーンアップ

# 統合後
log-management-unified.sh        # 全機能統合
```

#### 監視システム統合（3→1）
```bash
# 統合前
auto-monitor.sh                  # 高頻度監視
monitoring_system.sh             # 定期監視
system-health-check.sh           # ヘルスチェック

# 統合後
monitoring-unified.sh            # 全機能統合
```

## 📖 使用方法

### 基本的なトラブルシューティング

#### Step 1: 問題診断
```bash
./troubleshooting-workflow.sh --diagnose
```

#### Step 2: 自動修復
```bash
./troubleshooting-workflow.sh --diagnose --auto-fix
```

#### Step 3: 緊急時復旧
```bash
./troubleshooting-workflow.sh --emergency
```

### システム別詳細操作

#### 接続復旧
```bash
# 自動復旧（推奨）
./connection-recovery-unified.sh --auto

# 通常復旧（5フェーズ）
./connection-recovery-unified.sh --normal

# 緊急復旧（Boss1落ち対策）
./connection-recovery-unified.sh --emergency

# ヘルスチェックのみ
./connection-recovery-unified.sh --health-check
```

#### ログ管理
```bash
# 自動管理（推奨）
./log-management-unified.sh --auto

# ログ分析
./log-management-unified.sh --analyze

# 緊急クリーンアップ
./log-management-unified.sh --emergency

# 完全バックアップ
./log-management-unified.sh --backup
```

#### 監視システム
```bash
# 統合監視（24/7監視）
./monitoring-unified.sh --continuous --daemon

# ヘルスチェック
./monitoring-unified.sh --health

# 監視状況確認
./monitoring-unified.sh --status

# 監視停止
./monitoring-unified.sh --stop
```

#### ワークフロー復旧
```bash
# ブログ生成ワークフロー復旧
./troubleshooting-workflow.sh --workflow blog-gen

# 画像生成ワークフロー復旧
./troubleshooting-workflow.sh --workflow image-gen

# 通信システム復旧
./troubleshooting-workflow.sh --workflow communication

# 予防メンテナンス
./troubleshooting-workflow.sh --prevention
```

## 🛡️ 推奨運用

### 日常運用
1. **システム起動時**: `./troubleshooting-workflow.sh --diagnose`
2. **継続監視開始**: `./monitoring-unified.sh --continuous --daemon`
3. **問題発生時**: `./troubleshooting-workflow.sh --diagnose --auto-fix`

### 定期メンテナンス
```bash
# 毎日実行
./troubleshooting-workflow.sh --prevention

# 週次実行
./log-management-unified.sh --auto
./troubleshooting-workflow.sh --diagnose --auto-fix
```

### 緊急時対応
```bash
# Level 1: 自動診断・修復
./troubleshooting-workflow.sh --diagnose --auto-fix

# Level 2: 接続問題特化
./connection-recovery-unified.sh --auto

# Level 3: 全システム緊急復旧
./troubleshooting-workflow.sh --emergency
```

## 🔄 後方互換性

### レガシーコマンドの新コマンド対応表

| レガシーコマンド | 新統合コマンド |
|-----------------|----------------|
| `./auto-connection-recovery.sh` | `./connection-recovery-unified.sh --normal` |
| `./emergency_connection_recovery.sh` | `./connection-recovery-unified.sh --emergency` |
| `./connection-test.sh` | `./connection-recovery-unified.sh --test` |
| `./log-rotation.sh` | `./log-management-unified.sh --general` |
| `./auto_log_cleanup.sh` | `./log-management-unified.sh --queue` |
| `./auto-monitor.sh` | `./monitoring-unified.sh --intensive` |
| `./monitoring_system.sh` | `./monitoring-unified.sh --periodic` |
| `./system-health-check.sh` | `./monitoring-unified.sh --health` |

## 📊 効果と利点

### 運用効率化
- **コマンド体系統一**: 覚えるコマンドが大幅削減
- **自動復旧強化**: 問題の自動検出・修復機能
- **統合監視**: 24/7継続監視による問題予防

### 保守性向上
- **重複排除**: メンテナンスポイントの一元化
- **機能統合**: 関連機能のグループ化
- **インターフェース統一**: 一貫したオプション体系

### トラブルシューティング改善
- **段階的対応**: Level 1-3の体系的対応
- **問題分類**: 6種類の問題タイプ別対応
- **ワークフロー復旧**: 5種類のワークフロー専用復旧

## 🔧 開発者向け情報

### 統合システムの設計原則
1. **単一責任**: 各統合システムは明確な責任範囲
2. **オプション統一**: 全システム共通のオプション体系
3. **ログ統合**: 全システム共通のログ形式
4. **エラーハンドリング**: 統一されたエラー処理

### 拡張性
- 新機能は既存統合システムに追加
- 新しい問題タイプはtroublehooting-workflowに統合
- 新しいワークフローは専用復旧機能として追加

## 📝 変更履歴

### v2.0.0 (2025-07-18)
- **重大変更**: 13→8ファイルの大規模統合
- **新機能**: troubleshooting-workflow.sh追加
- **改善**: 全システムの統一インターフェース化
- **削除**: 8個のレガシーファイル削除（バックアップ済み）

## 🚨 重要な注意事項

### バックアップ
削除されたレガシーファイルは以下にバックアップされています：
```
backup/legacy_shell_scripts_20250718_104206/
```

### 移行期間中の対応
- 既存のcronジョブやスクリプトで旧コマンドを使用している場合は、新コマンドに更新してください
- 上記の対応表を参考に段階的に移行してください

### サポート
- 問題が発生した場合は、まず `./troubleshooting-workflow.sh --guide` を参照してください
- ログファイル（`logs/`ディレクトリ）で詳細な情報を確認できます

---

このシステム統合により、エージェント通信の信頼性と運用効率が大幅に向上しました。