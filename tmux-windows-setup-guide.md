# 🚀 Windows WSL tmux セットアップ完全ガイド

## 📋 概要
このガイドでは、Windows WSL環境でのtmux Multi-Agent Communication Demo環境の構築と、tmuxマウス操作の有効化について実践的に解説します。

---

## 🛠 Part 1: Multi-Agent Communication Demo 環境構築

### 🔧 前提条件
- Windows WSL がインストール済み
- tmux がインストール済み
- PowerShell 使用

### ⚠️ 解決した問題と対策

#### 問題1: 改行コード問題
**症状**: `Claude-Code-Communication/setup.sh: line 5: $'\r': command not found`

**解決方法**:
```bash
# Windows形式（CRLF）からLinux形式（LF）に変換
wsl dos2unix Claude-Code-Communication/setup.sh
```

#### 問題2: PowerShellでのBash構文エラー
**症状**: `Missing opening '(' after keyword 'for'`

**解決方法**: PowerShellではWSLコマンドとして実行
```bash
# ❌ 間違い (PowerShellでBash構文)
for i in {0..3}; do 
  tmux send-keys -t multiagent:0.$i 'claude --dangerously-skip-permissions' C-m
done

# ✅ 正解 (WSL環境でBash実行)
wsl bash -c "for i in {0..3}; do tmux send-keys -t multiagent:0.\$i 'claude --dangerously-skip-permissions' C-m; done"
```

#### 問題3: tmuxペインが見つからないエラー
**症状**: `can't find pane: claude --dangerously-skip-permissions`

**解決方法**: セッションを完全にクリーンアップして再構築
```bash
# 全セッション削除
wsl tmux kill-server

# 環境再構築
wsl bash Claude-Code-Communication/setup.sh

# ペイン構成確認
wsl tmux list-panes -t multiagent -F "#{pane_index}: #{pane_title}"
```

#### 問題4: OAuth認証ポート競合エラー
**症状**: `OAuth error: Port 54545 is already in use`

**原因**: 複数のClaudeインスタンスが同時に同じポートで認証を試行

**解決方法**: 段階的起動で認証を避ける
```bash
# 1. Presidentのみ先に起動
wsl bash -c "tmux send-keys -t president 'claude --dangerously-skip-permissions' C-m"

# 2. President認証完了後、間隔を空けてMultiagent起動
wsl bash -c "sleep 10 && for i in {0..3}; do tmux send-keys -t multiagent:0.\$i 'claude --dangerously-skip-permissions' C-m; sleep 2; done"
```

### 🎯 正しい環境構築手順

#### Step 1: スクリプト実行権限設定
```bash
# 改行コード修正
wsl dos2unix Claude-Code-Communication/setup.sh

# 実行権限付与
wsl chmod +x Claude-Code-Communication/setup.sh
```

#### Step 2: 環境構築実行
```bash
wsl bash Claude-Code-Communication/setup.sh
```

#### Step 3: ペイン構成確認
```bash
# セッション一覧確認
wsl tmux list-sessions

# ペイン構成確認
wsl tmux list-panes -t multiagent -F "#{pane_index}: #{pane_title}"
```

#### Step 4: Claude一括起動
```bash
# President起動
wsl bash -c "tmux send-keys -t president 'claude --dangerously-skip-permissions' C-m"

# Multiagent一括起動（4ペイン）
wsl bash -c "for i in {0..3}; do tmux send-keys -t multiagent:0.\$i 'claude --dangerously-skip-permissions' C-m; done"
```

### 📺 作成される環境

#### tmuxセッション構成
```
multiagent: 1 windows (4ペイン構成)
├── Pane 0: boss1     (チームリーダー)
├── Pane 1: worker1   (実行担当者A)
├── Pane 2: worker2   (実行担当者B)
└── Pane 3: worker3   (実行担当者C)

president: 1 windows (1ペイン構成)
└── Pane 0: PRESIDENT (プロジェクト統括)
```

### 🔗 環境アクセス方法
```bash
# マルチエージェント環境確認
wsl tmux attach-session -t multiagent

# プレジデント環境確認
wsl tmux attach-session -t president

# セッション一覧確認
wsl tmux list-sessions
```

---

## 🖱 Part 2: tmuxマウス操作有効化設定

### 🔍 Step 1: `.tmux.conf` の場所確認
```bash
ls -la ~/.tmux.conf
```

**存在しない場合の出力例**:
```
ls: cannot access '/home/hiroshi/.tmux.conf': No such file or directory
```

### 🛠 Step 2: `.tmux.conf` 作成
```bash
# ホームディレクトリに移動
cd ~

# ファイル編集
nano ~/.tmux.conf
```

**設定内容**:
```tmux
# マウス操作を有効にする
set -g mouse on

# （任意）ダブルクリックでペインを自動整列
bind -n DoubleClick1Pane select-layout tiled

# （任意）ペイン境界の視認性向上
set -g pane-border-style fg=colour238
set -g pane-active-border-style fg=colour39

# （任意）ステータスバーの色設定
set -g status-bg colour235
set -g status-fg colour136
```

### 💾 保存方法（nano使用時）
1. `Ctrl + O` → `Enter` (保存)
2. `Ctrl + X` (終了)

### 🔁 Step 3: 設定反映
```bash
# tmux内で設定リロード
tmux source-file ~/.tmux.conf

# または tmux再起動
exit   # tmux終了
tmux   # 再起動
```

### 🖱 Step 4: マウス操作確認項目
- ✅ **ペイン境界のドラッグ**でリサイズ
- ✅ **タブクリック**でウィンドウ切り替え
- ✅ **ダブルクリック**でレイアウト整列
- ✅ **スクロール**でコンテンツ閲覧

---

## 🎮 tmux基本操作

### プレフィックスキー: `Ctrl + B`

#### 基本コマンド
```bash
Ctrl + B → %     # 垂直分割
Ctrl + B → "     # 水平分割
Ctrl + B → 矢印   # ペイン移動
Ctrl + B → D     # セッションデタッチ
Ctrl + B → Q     # ペイン番号表示
Ctrl + B → C     # 新しいウィンドウ
Ctrl + B → N     # 次のウィンドウ
Ctrl + B → P     # 前のウィンドウ
```

### セッション管理
```bash
tmux new-session -s セッション名    # 新セッション作成
tmux attach-session -t セッション名  # セッション接続
tmux list-sessions                 # セッション一覧
tmux kill-session -t セッション名    # セッション削除
tmux kill-server                   # 全セッション削除
```

---

## 📂 ファイル場所

### Windows側からのアクセス
```
\\wsl$\Ubuntu\home\ユーザー名\.tmux.conf
```

### WSL内でのパス
```
/home/ユーザー名/.tmux.conf
```

---

## 🚨 トラブルシューティング

### 問題: tmuxセッションが見つからない
```bash
# セッション確認
wsl tmux list-sessions

# 全セッション削除して再構築
wsl tmux kill-server
wsl bash Claude-Code-Communication/setup.sh
```

### 問題: ペインが見つからない（can't find pane）
```bash
# ペイン構成確認
wsl tmux list-panes -t multiagent -F "#{pane_index}: #{pane_title}"

# 環境完全再構築
wsl tmux kill-server
wsl bash Claude-Code-Communication/setup.sh
```

### 問題: マウス操作が効かない
```bash
# 設定ファイル確認
cat ~/.tmux.conf

# 設定リロード
tmux source-file ~/.tmux.conf
```

### 問題: PowerShellでのBash構文エラー
```bash
# WSL環境でBashを明示的に実行
wsl bash -c "コマンド"
```

---

## 🎯 実践チェックリスト

### 環境構築
- [ ] WSL環境でsetup.sh実行
- [ ] multiagentセッション（4ペイン）作成確認
- [ ] presidentセッション作成確認
- [ ] ペイン構成確認（boss1, worker1-3）
- [ ] Claude一括起動完了

### マウス設定
- [ ] .tmux.conf作成
- [ ] mouse on設定追加
- [ ] 設定反映完了
- [ ] マウス操作動作確認

### 動作確認
- [ ] ペイン境界ドラッグでリサイズ
- [ ] マウスクリックでペイン切り替え
- [ ] セッション間の移動
- [ ] Claude各エージェント動作確認

### 問題対応
- [ ] 改行コード問題解決済み
- [ ] PowerShell構文エラー解決済み
- [ ] ペイン検出エラー解決済み

---

## 🔄 緊急時のリセット手順

環境が不安定になった場合の完全リセット：

```bash
# 1. 全セッション停止
wsl tmux kill-server

# 2. 環境確認
wsl tmux list-sessions  # 何も表示されないことを確認

# 3. 環境再構築
wsl bash Claude-Code-Communication/setup.sh

# 4. ペイン構成確認
wsl tmux list-panes -t multiagent -F "#{pane_index}: #{pane_title}"

# 5. Claude再起動
wsl bash -c "tmux send-keys -t president 'claude --dangerously-skip-permissions' C-m"
wsl bash -c "for i in {0..3}; do tmux send-keys -t multiagent:0.\$i 'claude --dangerously-skip-permissions' C-m; done"
```

---

**🎉 以上で、Windows WSL環境でのtmux Multi-Agent Communication Demo環境が完全に構築されました！**

各エージェントの指示書：
- `instructions/president.md` - President用
- `instructions/boss.md` - Boss用  
- `instructions/worker.md` - Worker用
- `CLAUDE.md` - システム構造説明 