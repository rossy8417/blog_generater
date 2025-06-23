# ファイル管理ルール

## 📂 ディレクトリ構造と用途

### `/` (ルートディレクトリ)
- **README.md**: プロジェクト概要（必須、移動禁止）
- **設定ファイル**: .env, requirements.txt など
- **実行ファイル**: メインスクリプトのみ

### `/outputs/`
**最終成果物・保管すべきファイル**
```
outputs/
├── articles/           # 完成記事
├── reports/           # 実行レポート・分析結果
├── images/            # 生成画像
├── article_operations/ # 記事更新結果
├── rewrite_1388_outputs/ # 記事リライト結果
└── rewrites/          # 今後のリライト結果
```

### `/tmp/`
**一時的な作業ファイル・プロセス中間生成物**
```
tmp/
├── worker_outputs/    # Worker出力ファイル
├── analysis/          # 分析中間結果
├── processing/        # 処理中ファイル
└── scattered_files/   # 整理待ちファイル
```

### `/docs/`
**ドキュメント・ガイド類**
```
docs/
├── setup-guides/      # セットアップガイド
├── user-guides/       # 使用方法ガイド
└── api-docs/          # API仕様書
```

### `/templates/`
**テンプレートファイル**
```
templates/
├── article-templates/ # 記事テンプレート
├── prompt-templates/  # プロンプトテンプレート
└── format-templates/  # 出力フォーマット
```

## 🔄 ファイル出力ルール

### 自動生成ファイルの出力先

#### 記事・コンテンツ系
- **完成記事**: `outputs/articles/`
- **記事リライト**: `outputs/rewrites/article_{id}_rewrite/`
- **記事分析**: `outputs/reports/article_analysis/`
- **SEO分析**: `outputs/reports/seo_analysis/`

#### システム実行結果
- **更新レポート**: `outputs/reports/update_reports/`
- **エラーログ**: `logs/errors/`
- **成功レポート**: `outputs/reports/success_reports/`

#### 一時作業ファイル
- **Worker出力**: `tmp/worker_outputs/`
- **処理中ファイル**: `tmp/processing/`
- **デバッグファイル**: `tmp/debug/`

### スクリプト実装例

```python
# ファイル出力の統一化
import os
from pathlib import Path

class FileManager:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.outputs_dir = self.base_dir / "outputs"
        self.tmp_dir = self.base_dir / "tmp"
        self.docs_dir = self.base_dir / "docs"
    
    def get_output_path(self, file_type: str, filename: str) -> Path:
        """適切な出力パスを取得"""
        paths = {
            'article': self.outputs_dir / "articles",
            'rewrite': self.outputs_dir / "rewrites",
            'report': self.outputs_dir / "reports", 
            'image': self.outputs_dir / "images",
            'temp': self.tmp_dir,
            'worker': self.tmp_dir / "worker_outputs",
            'analysis': self.tmp_dir / "analysis"
        }
        
        output_dir = paths.get(file_type, self.tmp_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir / filename
```

## 🧹 定期クリーンアップルール

### 自動削除対象
- **tmp/processing/**: 30日以上経過したファイル
- **tmp/debug/**: 7日以上経過したファイル
- **logs/**: 90日以上経過したログファイル

### 手動確認対象
- **tmp/worker_outputs/**: 分析結果は保管価値を確認
- **outputs/reports/**: 重要なレポートは保管

### 保管対象
- **outputs/articles/**: 恒久保管
- **docs/**: 恒久保管
- **templates/**: 恒久保管

## 📋 ファイル命名規則

### タイムスタンプ形式
- **日時**: `YYYYMMDD_HHMMSS`
- **例**: `article_1388_update_20250623_143022.json`

### カテゴリ別命名
- **記事**: `article_{id}_{action}_{timestamp}.{ext}`
- **リライト**: `rewritten_article_{id}_{timestamp}.{ext}`
- **レポート**: `{type}_report_{id}_{timestamp}.{ext}`
- **分析**: `{subject}_analysis_{timestamp}.{ext}`
- **Worker出力**: `worker{n}_{task}_{timestamp}.{ext}`

## 🚀 実装済み移動

### 完了した整理
- ✅ `boss1_*_report.md` → `outputs/reports/`
- ✅ `tmux-windows-setup-guide.md` → `docs/`
- ✅ `rewrite_1388_outputs/` → `outputs/article_1388_project/`
- ✅ `*1388*` ファイル群 → `outputs/article_1388_project/`
- ✅ レポート用ディレクトリ作成
- ✅ 記事別プロジェクト整理

### 今後の自動化
スクリプト実行時に適切なディレクトリへの出力を自動化し、ルートディレクトリの散乱を防止します。

## 🚫 ルートディレクトリ散乱防止策

### 記事別プロジェクト管理
- **記事ID特化ファイル**: `outputs/article_{id}_project/` にまとめて管理
- **命名規則**: `*{記事ID}*` パターンのファイルは自動検出・移動対象

### 自動検出・移動スクリプト例
```python
def organize_scattered_files():
    """散乱ファイルの自動整理"""
    import re
    from pathlib import Path
    
    root = Path(".")
    outputs = Path("outputs")
    
    # 記事ID特化ファイルの検出パターン
    article_patterns = [
        r".*_(\d+)_.*",  # ファイル名に数字ID含む
        r".*article_(\d+).*",  # article_ID形式
        r".*(\d+).*\.(py|json|txt|md)$"  # 数字を含むファイル
    ]
    
    for file in root.glob("*"):
        if file.is_file() and not file.name.startswith("."):
            for pattern in article_patterns:
                match = re.search(pattern, file.name)
                if match:
                    article_id = match.group(1)
                    target_dir = outputs / f"article_{article_id}_project"
                    target_dir.mkdir(exist_ok=True)
                    file.rename(target_dir / file.name)
                    print(f"移動: {file.name} → {target_dir}")
                    break
```

### 予防策の実装
1. **スクリプト出力先指定**: 全ての生成ファイルに適切な出力先を明示
2. **定期クリーンアップ**: 週次でルートディレクトリをチェック
3. **命名規則の徹底**: プロジェクト統一の命名規則を適用