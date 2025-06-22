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

#### Step 3: Claude一括起動
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

---

**🎉 以上で、Windows WSL環境でのtmux Multi-Agent Communication Demo環境が完全に構築されました！**

各エージェントの指示書：
- `instructions/president.md` - President用
- `instructions/boss.md` - Boss用  
- `instructions/worker.md` - Worker用
- `CLAUDE.md` - システム構造説明 