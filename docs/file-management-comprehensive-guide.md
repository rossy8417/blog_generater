# 📂 ファイル管理包括ガイド

## 概要

このガイドは、ブログ生成システムにおける全ファイル管理のルールと最適化方法を統合的に定義します。OutpurManager準拠ルールと一般的なファイル管理ルールを統一し、システム全体の整合性を保証します。

## 🎯 基本原則

### 1. 統一された出力構造
- **メイン原則**: 全成果物は`outputs/[タイトル-INT-XX]/`構造で管理
- **散乱防止**: ルートディレクトリへの直接出力完全禁止
- **一時ファイル分離**: `tmp/`は作業用のみ、成果物保存禁止

### 2. 責任範囲の明確化
- **Boss1**: ディレクトリ作成・統合作業・WordPress投稿準備
- **Worker1-3**: 担当ファイルの正しい場所への出力・完了確認
- **自動システム**: 品質チェック・整理・バックアップ

## 📁 ディレクトリ構造標準

### ✅ 推奨構造（統一基準）
```
blog_generator/
├── outputs/                    # 【重要】全成果物の統一管理
│   ├── [記事タイトル-INT-01]/   # ブログ生成プロジェクト（必須形式）
│   │   ├── complete_article.md  # 最終統合記事（固定ファイル名）
│   │   ├── eyecatch.jpg        # アイキャッチ画像（固定ファイル名）
│   │   ├── chapter1.jpg        # 第1章画像（固定ファイル名）
│   │   ├── chapter2.jpg        # 第2章画像（固定ファイル名）
│   │   ├── chapter3.jpg        # 第3章画像（固定ファイル名）
│   │   ├── chapter4.jpg        # 第4章画像（固定ファイル名）
│   │   ├── chapter5.jpg        # 第5章画像（固定ファイル名）
│   │   ├── chapter6.jpg        # 第6章画像（固定ファイル名）
│   │   ├── metadata.json       # 記事メタデータ（自動生成）
│   │   ├── outline_content.md  # アウトライン（任意）
│   │   ├── lead_content.md     # リード文（任意）
│   │   └── summary_content.md  # まとめ（任意）
│   ├── reports/                # システム実行レポート
│   │   ├── update_reports/     # 記事更新レポート
│   │   ├── analysis_reports/   # 分析結果
│   │   └── success_reports/    # 成功実行記録
│   ├── archives/               # 過去プロジェクト保管
│   │   ├── article_updates/    # 記事更新履歴
│   │   └── completed_projects/ # 完了プロジェクト
│   └── backups/                # 自動バックアップ
├── tmp/                        # 一時作業領域
│   ├── worker_outputs/         # Worker個別出力（一時）
│   ├── processing/             # 処理中ファイル（一時）
│   ├── quality_check/          # 品質チェック作業（一時）
│   ├── message_queue/          # エージェント通信キュー
│   └── debug/                  # デバッグファイル（一時）
├── docs/                       # ドキュメント（恒久保管）
├── templates/                  # テンプレート（恒久保管）
├── scripts/                    # 実行スクリプト（恒久保管）
├── config/                     # 設定ファイル（恒久保管）
└── logs/                       # システムログ
    ├── connection_recovery.log
    ├── monitoring.log
    └── archives/               # 古いログのアーカイブ
```

## 🔧 運用ルール詳細

### Phase別ファイル管理責任

#### Phase1: 企画・設計（Boss1）
```bash
# 必須実行
mkdir -p "outputs/[タイトル-INT-XX]/"
cd "outputs/[タイトル-INT-XX]/"

# 出力ファイル
- outline_content.md     # アウトライン保存
- metadata.json          # プロジェクト情報記録
```

#### Phase2: 並行執筆（Worker1-3）
```bash
# Worker個別責任
# Worker1: 第1-2章担当
outputs/[タイトル-INT-XX]/chapter1.md
outputs/[タイトル-INT-XX]/chapter2.md

# Worker2: 第3-4章担当  
outputs/[タイトル-INT-XX]/chapter3.md
outputs/[タイトル-INT-XX]/chapter4.md

# Worker3: 第5-6章担当
outputs/[タイトル-INT-XX]/chapter5.md
outputs/[タイトル-INT-XX]/chapter6.md

# 必須確認コマンド
ls -la outputs/[タイトル-INT-XX]/
```

#### Phase3: 画像生成・統合（Boss1 + Worker1-3）
```bash
# Worker1: アイキャッチ担当
outputs/[タイトル-INT-XX]/eyecatch.jpg

# Worker2: 第1-3章画像担当
outputs/[タイトル-INT-XX]/chapter1.jpg
outputs/[タイトル-INT-XX]/chapter2.jpg  
outputs/[タイトル-INT-XX]/chapter3.jpg

# Worker3: 第4-6章画像担当
outputs/[タイトル-INT-XX]/chapter4.jpg
outputs/[タイトル-INT-XX]/chapter5.jpg
outputs/[タイトル-INT-XX]/chapter6.jpg

# Boss1: 最終統合
outputs/[タイトル-INT-XX]/complete_article.md
outputs/[タイトル-INT-XX]/lead_content.md
outputs/[タイトル-INT-XX]/summary_content.md
```

## 📋 ファイル命名規則

### 必須命名（変更禁止）
| ファイル種別 | 必須ファイル名 | 説明 |
|-------------|----------------|------|
| 最終記事 | `complete_article.md` | 統合された完成記事 |
| アイキャッチ | `eyecatch.jpg` | メイン画像 |
| 章別画像 | `chapter1.jpg`〜`chapter6.jpg` | 各章の画像 |
| メタデータ | `metadata.json` | 記事情報 |

### 任意命名（推奨形式）
| ファイル種別 | 推奨ファイル名 | 説明 |
|-------------|----------------|------|
| アウトライン | `outline_content.md` | 記事構成 |
| リード文 | `lead_content.md` | 導入部分 |
| まとめ | `summary_content.md` | 結論部分 |

### 禁止命名
- `boss1_*`、`worker1_*`等のプレフィックス使用禁止
- プロジェクト外のIDや日付の混入禁止

## 🛡️ 品質保証システム

### 自動品質チェック
```bash
# プロジェクト完了時の必須確認
verify_project_structure() {
    local project_dir="outputs/[タイトル-INT-XX]"
    
    echo "=== プロジェクト構造確認 ==="
    
    # 必須ファイル存在確認
    local required_files=(
        "complete_article.md"
        "eyecatch.jpg"
        "chapter1.jpg" "chapter2.jpg" "chapter3.jpg"
        "chapter4.jpg" "chapter5.jpg" "chapter6.jpg"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$project_dir/$file" ]]; then
            echo "✅ $file: 存在"
        else
            echo "❌ $file: 不存在"
            return 1
        fi
    done
    
    echo "✅ プロジェクト構造: 正常"
    return 0
}
```

### WordPress投稿連携確認
```bash
# WordPress投稿前チェック
pre_wordpress_check() {
    local project_dir="$1"
    
    # 画像サイズ確認
    local oversized_images=$(find "$project_dir" -name "*.jpg" -size +1M)
    if [[ -n "$oversized_images" ]]; then
        echo "⚠️ 1MB超過画像あり - 最適化が必要"
        echo "$oversized_images"
    fi
    
    # 記事文字数確認
    local char_count=$(wc -c < "$project_dir/complete_article.md")
    if [[ $char_count -lt 20000 ]]; then
        echo "⚠️ 文字数不足: ${char_count}文字 (20,000文字以上推奨)"
    fi
    
    echo "✅ WordPress投稿準備: 完了"
}
```

## 🔄 緊急時復旧手順

### 散乱ファイル緊急整理
```bash
# 自動検出・移動スクリプト
emergency_organize() {
    echo "=== 緊急ファイル整理開始 ==="
    
    # tmp/からの移動
    if [[ -d "tmp" ]]; then
        find tmp -name "boss1_*" -o -name "worker*_*" | while read file; do
            if [[ "$file" =~ complete_article|eyecatch|chapter ]]; then
                echo "緊急移動: $file"
                # 適切なプロジェクトディレクトリに移動
                # （実際の移動ロジックは実装時に詳細化）
            fi
        done
    fi
    
    # ルートディレクトリからの移動
    find . -maxdepth 1 -name "*-INT-*" -type f | while read file; do
        echo "ルート散乱ファイル検出: $file"
        # 適切な場所に移動
    done
    
    echo "✅ 緊急整理完了"
}
```

### 品質基準違反時の自動修正
```bash
# ファイル名標準化
standardize_filenames() {
    local project_dir="$1"
    
    cd "$project_dir" || return 1
    
    # プレフィックス除去
    for file in boss1_* worker*_*; do
        if [[ -f "$file" ]]; then
            local new_name
            case "$file" in
                *complete_article*) new_name="complete_article.md" ;;
                *eyecatch*) new_name="eyecatch.jpg" ;;
                *chapter1*) new_name="chapter1.jpg" ;;
                *chapter2*) new_name="chapter2.jpg" ;;
                *chapter3*) new_name="chapter3.jpg" ;;
                *chapter4*) new_name="chapter4.jpg" ;;
                *chapter5*) new_name="chapter5.jpg" ;;
                *chapter6*) new_name="chapter6.jpg" ;;
            esac
            
            if [[ -n "$new_name" ]]; then
                mv "$file" "$new_name"
                echo "標準化: $file → $new_name"
            fi
        fi
    done
}
```

## 🧹 定期メンテナンス

### 自動クリーンアップ対象
| ディレクトリ | 削除基準 | 実行頻度 |
|-------------|----------|----------|
| `tmp/processing/` | 30日以上経過 | 週次 |
| `tmp/debug/` | 7日以上経過 | 日次 |
| `tmp/worker_outputs/` | 14日以上経過 | 週次 |
| `logs/` | 90日以上経過 | 月次 |

### 保管対象（削除禁止）
- `outputs/[タイトル-INT-XX]/` - 恒久保管
- `docs/` - 恒久保管
- `templates/` - 恒久保管
- `config/` - 恒久保管

### アーカイブ対象
- 完了プロジェクト → `outputs/archives/completed_projects/`
- 古いレポート → `outputs/archives/reports/`
- 更新履歴 → `outputs/archives/article_updates/`

## 🚀 自動化システム

### 統合スクリプト実装例
```python
# scripts/organize_outputs.py の拡張
class ComprehensiveFileManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.outputs_dir = self.base_dir / "outputs"
        self.tmp_dir = self.base_dir / "tmp"
    
    def ensure_project_structure(self, project_name: str):
        """プロジェクト構造の自動作成"""
        project_dir = self.outputs_dir / project_name
        project_dir.mkdir(parents=True, exist_ok=True)
        return project_dir
    
    def validate_project_completion(self, project_dir: Path) -> bool:
        """プロジェクト完了の検証"""
        required_files = [
            "complete_article.md",
            "eyecatch.jpg",
            *[f"chapter{i}.jpg" for i in range(1, 7)]
        ]
        
        for file in required_files:
            if not (project_dir / file).exists():
                return False
        
        return True
    
    def auto_organize_scattered_files(self):
        """散乱ファイルの自動整理"""
        # 実装詳細...
        pass
```

## 📊 運用効果測定

### KPI指標
- **構造準拠率**: 正しい構造で作成されたプロジェクトの割合
- **散乱ファイル数**: ルート・tmp/に残存するファイル数
- **自動化率**: 手動介入が必要だった作業の割合
- **復旧時間**: 問題発生から正常化までの時間

### 継続改善
1. **月次レビュー**: 構造準拠状況の確認
2. **四半期改善**: システム改善・ルール更新
3. **年次評価**: 全体的な効率性評価

---

このガイドにより、ファイル管理の一貫性とシステムの信頼性が大幅に向上します。全てのエージェントと自動システムがこのルールに従うことで、混乱のない効率的な運用が実現されます。