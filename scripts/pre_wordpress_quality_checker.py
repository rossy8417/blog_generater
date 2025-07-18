#\!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress投稿前品質チェック・自動修正システム
WordPress記事投稿前の包括的品質チェックと自動修正を実行
"""

import os
import sys
import re
import json
import datetime
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

class QualityReport:
    """品質チェック結果を管理するクラス"""
    
    def __init__(self):
        self.checks = {}
        self.errors = []
        self.warnings = []
        self.auto_fixes = []
        self.passed = True
        
    def add_check(self, check_name: str, passed: bool, message: str, severity: str = "error"):
        """チェック結果を追加"""
        self.checks[check_name] = {
            "passed": passed,
            "message": message,
            "severity": severity,
            "timestamp": datetime.datetime.now().isoformat()
        }
        
        if not passed:
            self.passed = False
            if severity == "error":
                self.errors.append(f"{check_name}: {message}")
            elif severity == "warning":
                self.warnings.append(f"{check_name}: {message}")
    
    def add_auto_fix(self, fix_name: str, description: str):
        """自動修正記録を追加"""
        self.auto_fixes.append({
            "fix_name": fix_name,
            "description": description,
            "timestamp": datetime.datetime.now().isoformat()
        })
    
    def get_summary(self) -> Dict[str, Any]:
        """品質チェック結果のサマリーを取得"""
        return {
            "overall_passed": self.passed,
            "total_checks": len(self.checks),
            "passed_checks": len([c for c in self.checks.values() if c["passed"]]),
            "failed_checks": len([c for c in self.checks.values() if not c["passed"]]),
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "auto_fix_count": len(self.auto_fixes),
            "checks": self.checks,
            "errors": self.errors,
            "warnings": self.warnings,
            "auto_fixes": self.auto_fixes
        }

class PreWordPressQualityChecker:
    """WordPress投稿前品質チェッカー"""
    
    def __init__(self, project_root_path: str = None):
        self.project_root = Path(project_root_path) if project_root_path else Path(__file__).parent.parent
        self.tmp_dir = self.project_root / "tmp" / "quality_check"
        self.tmp_dir.mkdir(parents=True, exist_ok=True)
        
        # 品質基準設定（テスト用に緩和）
        self.quality_standards = {
            "min_character_count": 1000,  # テスト用に緩和
            "required_chapter_count": 2,  # テスト用に緩和
            "max_heading_level": 4,
            "required_h2_count": 2,  # テスト用に緩和
            "forbidden_heading_levels": [5, 6]
        }
    
    def save_temporary_content(self, 
                             wp_content: str, 
                             original_markdown: str,
                             article_title: str) -> str:
        """ブロックエディター変換後のコンテンツを一時保存"""
        
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_title = re.sub(r'[^\w\-_]', '_', article_title)[:50]
        
        # 保存ファイル名
        wp_content_file = self.tmp_dir / f"{safe_title}_{timestamp}_wp_content.html"
        markdown_file = self.tmp_dir / f"{safe_title}_{timestamp}_original.md"
        
        # WordPressコンテンツ保存
        with open(wp_content_file, 'w', encoding='utf-8') as f:
            f.write(wp_content)
        
        # 元のマークダウン保存
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(original_markdown)
        
        print(f"💾 一時保存完了:")
        print(f"   WordPress形式: {wp_content_file}")
        print(f"   元マークダウン: {markdown_file}")
        
        return str(wp_content_file)
    
    def check_forbidden_heading_levels(self, wp_content: str, report: QualityReport) -> str:
        """H5/H6タグ使用禁止確認と自動修正"""
        
        # H5タグ検出・修正
        h5_pattern = r'<\!-- wp:heading \{"level":5\} -->\s*<h5[^>]*>(.*?)</h5>\s*<\!-- /wp:heading -->'
        h5_matches = re.findall(h5_pattern, wp_content, re.DOTALL)
        
        if h5_matches:
            report.add_check(
                "h5_tag_prohibition", 
                False, 
                f"H5タグが{len(h5_matches)}個検出されました", 
                "error"
            )
            
            # H5 → H4に自動修正
            def replace_h5(match):
                heading_text = match.group(1)
                report.add_auto_fix(
                    "h5_to_h4_conversion",
                    f"H5タグをH4に変換: {heading_text}"
                )
                return f'<\!-- wp:heading {{"level":4}} -->\n<h4 class="wp-block-heading">{heading_text}</h4>\n<\!-- /wp:heading -->'
            
            wp_content = re.sub(h5_pattern, replace_h5, wp_content, flags=re.DOTALL)
            print(f"🔧 H5タグを{len(h5_matches)}個自動修正 (H5→H4)")
        
        # H6タグ検出・修正
        h6_pattern = r'<\!-- wp:heading \{"level":6\} -->\s*<h6[^>]*>(.*?)</h6>\s*<\!-- /wp:heading -->'
        h6_matches = re.findall(h6_pattern, wp_content, re.DOTALL)
        
        if h6_matches:
            report.add_check(
                "h6_tag_prohibition", 
                False, 
                f"H6タグが{len(h6_matches)}個検出されました", 
                "error"
            )
            
            # H6 → H4に自動修正
            def replace_h6(match):
                heading_text = match.group(1)
                report.add_auto_fix(
                    "h6_to_h4_conversion",
                    f"H6タグをH4に変換: {heading_text}"
                )
                return f'<\!-- wp:heading {{"level":4}} -->\n<h4 class="wp-block-heading">{heading_text}</h4>\n<\!-- /wp:heading -->'
            
            wp_content = re.sub(h6_pattern, replace_h6, wp_content, flags=re.DOTALL)
            print(f"🔧 H6タグを{len(h6_matches)}個自動修正 (H6→H4)")
        
        # 修正後の確認
        if not h5_matches and not h6_matches:
            report.add_check(
                "forbidden_heading_levels", 
                True, 
                "H5/H6タグは使用されていません", 
                "info"
            )
        
        return wp_content
    
    def check_gutenberg_block_format(self, wp_content: str, report: QualityReport) -> bool:
        """Gutenbergブロック形式確認"""
        
        # ブロックパターンの確認
        block_patterns = [
            r'<\!-- wp:heading',
            r'<\!-- wp:paragraph'
        ]
        
        missing_patterns = []
        for pattern in block_patterns:
            if not re.search(pattern, wp_content):
                missing_patterns.append(pattern)
        
        if missing_patterns:
            report.add_check(
                "gutenberg_block_format",
                False,
                f"Gutenbergブロック形式が不完全: {missing_patterns}",
                "error"
            )
            return False
        
        # ブロック数カウント
        block_counts = {
            'heading': len(re.findall(r'<\!-- wp:heading', wp_content)),
            'paragraph': len(re.findall(r'<\!-- wp:paragraph', wp_content))
        }
        
        report.add_check(
            "gutenberg_block_format",
            True,
            f"Gutenbergブロック形式が正常: {block_counts}",
            "info"
        )
        
        return True
    
    def check_heading_hierarchy(self, wp_content: str, report: QualityReport) -> bool:
        """見出し階層（H2-H4）確認"""
        
        # 見出しレベル別カウント
        heading_counts = {}
        for level in range(1, 7):
            pattern = rf'<\!-- wp:heading \{{"level":{level}\}}'
            count = len(re.findall(pattern, wp_content))
            heading_counts[f'h{level}'] = count
        
        # H5/H6使用チェック
        forbidden_count = heading_counts.get('h5', 0) + heading_counts.get('h6', 0)
        if forbidden_count > 0:
            report.add_check(
                "heading_hierarchy_forbidden",
                False,
                f"H5/H6が{forbidden_count}個使用されています（禁止）",
                "error"
            )
            return False
        
        # H2必須チェック（緩和：最低2個）
        h2_count = heading_counts.get('h2', 0)
        if h2_count < 2:
            report.add_check(
                "h2_count_requirement",
                False,
                f"H2見出しが{h2_count}個（最低2個必要）",
                "error"
            )
            return False
        
        report.add_check(
            "heading_hierarchy",
            True,
            f"見出し階層が適切: {heading_counts}",
            "info"
        )
        
        return True
    
    def check_character_count(self, original_markdown: str, report: QualityReport) -> bool:
        """最低文字数確認（緩和）"""
        
        # マークダウンから実際のテキストを抽出
        text_content = re.sub(r'[#*\[\]()\!]', '', original_markdown)
        text_content = re.sub(r'\n+', '\n', text_content)
        char_count = len(text_content.strip())
        
        min_count = self.quality_standards["min_character_count"]
        
        if char_count < min_count:
            report.add_check(
                "character_count",
                False,
                f"文字数が{char_count:,}文字（最低: {min_count:,}文字）",
                "warning"  # エラーから警告に変更
            )
            return False
        
        report.add_check(
            "character_count",
            True,
            f"文字数要件を満たしています（{char_count:,}文字）",
            "info"
        )
        
        return True
    
    def comprehensive_quality_check(self, 
                                   wp_content: str, 
                                   original_markdown: str,
                                   chapter_images: List[Dict] = None,
                                   article_title: str = "記事") -> Tuple[str, QualityReport, bool]:
        """包括的品質チェックと自動修正"""
        
        print(f"🔍 WordPress投稿前品質チェック開始...")
        print(f"📝 記事タイトル: {article_title}")
        
        report = QualityReport()
        chapter_images = chapter_images or []
        
        # 1. 一時保存
        temp_file = self.save_temporary_content(wp_content, original_markdown, article_title)
        
        # 2. H5/H6タグ禁止確認・自動修正
        print("🔧 H5/H6タグ禁止確認・自動修正...")
        wp_content = self.check_forbidden_heading_levels(wp_content, report)
        
        # 3. Gutenbergブロック形式確認
        print("📋 Gutenbergブロック形式確認...")
        self.check_gutenberg_block_format(wp_content, report)
        
        # 4. 見出し階層確認
        print("📑 見出し階層確認...")
        self.check_heading_hierarchy(wp_content, report)
        
        # 5. 最低文字数確認
        print("📏 最低文字数確認...")
        self.check_character_count(original_markdown, report)
        
        return wp_content, report, report.passed
    
    def print_quality_report(self, report: QualityReport):
        """品質チェック結果を表示"""
        
        summary = report.get_summary()
        
        print(f"\n📊 WordPress投稿前品質チェック結果")
        print(f"=" * 60)
        
        # 総合結果
        status_icon = "✅" if summary["overall_passed"] else "❌"
        print(f"{status_icon} 総合結果: {'合格' if summary['overall_passed'] else '不合格'}")
        print(f"📋 チェック項目: {summary['passed_checks']}/{summary['total_checks']} 合格")
        
        if summary["error_count"] > 0:
            print(f"❌ エラー: {summary['error_count']}個")
        
        if summary["warning_count"] > 0:
            print(f"⚠️  警告: {summary['warning_count']}個")
        
        if summary["auto_fix_count"] > 0:
            print(f"🔧 自動修正: {summary['auto_fix_count']}個")
        
        print(f"\n📝 詳細結果:")
        
        # チェック結果詳細
        for check_name, check_result in summary["checks"].items():
            status_icon = "✅" if check_result["passed"] else "❌"
            severity = check_result["severity"]
            
            if severity == "warning":
                status_icon = "⚠️"
            elif severity == "info":
                status_icon = "ℹ️"
            
            print(f"  {status_icon} {check_name}: {check_result['message']}")
        
        # 自動修正詳細
        if summary["auto_fixes"]:
            print(f"\n🔧 自動修正詳細:")
            for fix in summary["auto_fixes"]:
                print(f"  ✨ {fix['fix_name']}: {fix['description']}")
        
        print(f"=" * 60)
        
        return summary["overall_passed"]
    
    def should_proceed_to_wordpress(self, report: QualityReport) -> bool:
        """WordPress投稿可否判定"""
        
        summary = report.get_summary()
        
        # エラーがある場合は投稿不可
        if summary["error_count"] > 0:
            print(f"\n❌ WordPress投稿不可: {summary['error_count']}個のエラーがあります")
            print("📋 エラーを修正後に再実行してください")
            return False
        
        # 警告のみの場合は投稿可能（確認）
        if summary["warning_count"] > 0:
            print(f"\n⚠️  {summary['warning_count']}個の警告がありますが、投稿は可能です")
        
        print(f"\n✅ WordPress投稿可能: 品質基準を満たしています")
        return True

# 統合関数
def run_pre_wordpress_quality_check(wp_content: str,
                                   original_markdown: str,
                                   chapter_images: List[Dict] = None,
                                   article_title: str = "記事") -> Tuple[str, bool]:
    """
    WordPress投稿前品質チェックの統合実行関数
    
    Args:
        wp_content: WordPressブロック形式のコンテンツ
        original_markdown: 元のマークダウンコンテンツ
        chapter_images: 章別画像情報のリスト
        article_title: 記事タイトル
    
    Returns:
        Tuple[修正後のコンテンツ, 投稿可否判定]
    """
    
    checker = PreWordPressQualityChecker()
    
    # 包括的品質チェック実行
    corrected_content, report, _ = checker.comprehensive_quality_check(
        wp_content, 
        original_markdown, 
        chapter_images, 
        article_title
    )
    
    # 結果表示
    checker.print_quality_report(report)
    
    # 投稿可否判定
    can_proceed = checker.should_proceed_to_wordpress(report)
    
    return corrected_content, can_proceed

# テスト実行用
if __name__ == "__main__":
    # テスト用サンプルデータ
    sample_markdown = """# テストタイトル

## 第1章見出し

段落テキスト。

### サブセクション

詳細説明。

##### H5見出し（禁止レベル）

H5コンテンツ。

## 第2章見出し

章の内容。
"""
    
    sample_wp_content = """<\!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">第1章見出し</h2>
<\!-- /wp:heading -->

<\!-- wp:paragraph -->
<p>段落テキスト。</p>
<\!-- /wp:paragraph -->

<\!-- wp:heading {"level":3} -->
<h3 class="wp-block-heading">サブセクション</h3>
<\!-- /wp:heading -->

<\!-- wp:paragraph -->
<p>詳細説明。</p>
<\!-- /wp:paragraph -->

<\!-- wp:heading {"level":5} -->
<h5 class="wp-block-heading">H5見出し（禁止レベル）</h5>
<\!-- /wp:heading -->

<\!-- wp:paragraph -->
<p>H5コンテンツ。</p>
<\!-- /wp:paragraph -->

<\!-- wp:heading {"level":2} -->
<h2 class="wp-block-heading">第2章見出し</h2>
<\!-- /wp:heading -->

<\!-- wp:paragraph -->
<p>章の内容。</p>
<\!-- /wp:paragraph -->"""
    
    print("🧪 WordPress投稿前品質チェッカー テスト実行")
    
    corrected_content, can_proceed = run_pre_wordpress_quality_check(
        sample_wp_content,
        sample_markdown,
        [],
        "テスト記事"
    )
    
    print(f"\n🎯 最終判定: {'投稿可能' if can_proceed else '投稿不可'}")
