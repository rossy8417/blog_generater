#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
見出し構造検証ツール
投稿前にMarkdownとWordPress出力の見出し構造をチェックし、問題を事前に検出
"""

import re
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass

@dataclass
class HeadingIssue:
    """見出し構造の問題"""
    line_number: int
    issue_type: str
    heading_text: str
    suggestion: str

class HeadingValidator:
    """見出し構造検証クラス"""
    
    def __init__(self):
        self.forbidden_levels = [5, 6]  # H5, H6は禁止
        self.max_allowed_level = 4
        
    def validate_markdown_file(self, file_path: str) -> Tuple[bool, List[HeadingIssue]]:
        """
        Markdownファイルの見出し構造を検証
        
        Args:
            file_path: 検証するMarkdownファイルのパス
            
        Returns:
            (is_valid, issues): 検証結果と問題のリスト
        """
        issues = []
        
        if not os.path.exists(file_path):
            issues.append(HeadingIssue(0, "FILE_NOT_FOUND", "", f"ファイルが見つかりません: {file_path}"))
            return False, issues
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if line.startswith('#'):
                    level = len(line) - len(line.lstrip('#'))
                    heading_text = line.lstrip('# ').strip()
                    
                    # H5以上の禁止チェック
                    if level >= 5:
                        issues.append(HeadingIssue(
                            i, 
                            "FORBIDDEN_LEVEL",
                            heading_text,
                            f"H{level}は禁止されています。H4以下または装飾（**太字**等）を使用してください"
                        ))
                    
                    # テンプレート識別子の残存チェック
                    if re.search(r'H\d+-\d+(-\d+)?', heading_text):
                        issues.append(HeadingIssue(
                            i,
                            "TEMPLATE_ID_FOUND",
                            heading_text,
                            "テンプレート識別子（H3-1等）が残存しています。削除してください"
                        ))
                    
                    # 見出し階層の飛びチェック
                    if level > 4:
                        issues.append(HeadingIssue(
                            i,
                            "LEVEL_TOO_DEEP",
                            heading_text,
                            f"見出しレベルが深すぎます（H{level}）。H4以下に調整してください"
                        ))
                        
        except Exception as e:
            issues.append(HeadingIssue(0, "READ_ERROR", "", f"ファイル読み込みエラー: {str(e)}"))
            return False, issues
            
        return len(issues) == 0, issues
    
    def validate_wordpress_content(self, wp_content: str) -> Tuple[bool, List[HeadingIssue]]:
        """
        WordPress Gutenbergコンテンツの見出し構造を検証
        
        Args:
            wp_content: WordPressブロック形式のコンテンツ
            
        Returns:
            (is_valid, issues): 検証結果と問題のリスト
        """
        issues = []
        lines = wp_content.split('\n')
        
        # 見出しレベル別カウント
        heading_counts = {2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        
        for i, line in enumerate(lines, 1):
            # WordPress見出しブロックの検出
            heading_match = re.search(r'<!-- wp:heading \{"level":(\d+)\} -->', line)
            if heading_match:
                level = int(heading_match.group(1))
                heading_counts[level] += 1
                
                # 次の行でH要素を取得
                if i < len(lines):
                    h_tag_line = lines[i].strip()
                    h_tag_match = re.search(r'<h(\d+)[^>]*>([^<]+)</h\d+>', h_tag_line)
                    if h_tag_match:
                        heading_text = h_tag_match.group(2)
                        
                        # H5以上の禁止チェック
                        if level >= 5:
                            issues.append(HeadingIssue(
                                i,
                                "FORBIDDEN_WP_LEVEL",
                                heading_text,
                                f"WordPress H{level}タグが生成されています。変換処理を確認してください"
                            ))
        
        # 統計情報の追加
        stats_issue = HeadingIssue(
            0,
            "STATISTICS",
            "",
            f"見出し統計: H2={heading_counts[2]}, H3={heading_counts[3]}, H4={heading_counts[4]}, H5={heading_counts[5]}, H6={heading_counts[6]}"
        )
        issues.append(stats_issue)
        
        # H5/H6が存在する場合は無効
        forbidden_count = heading_counts[5] + heading_counts[6]
        is_valid = forbidden_count == 0
        
        return is_valid, issues
    
    def generate_report(self, issues: List[HeadingIssue], file_path: str = "") -> str:
        """
        検証結果レポートを生成
        
        Args:
            issues: 問題のリスト
            file_path: 検証したファイルパス
            
        Returns:
            レポート文字列
        """
        report = []
        report.append("🔍 見出し構造検証レポート")
        report.append("=" * 50)
        
        if file_path:
            report.append(f"📁 ファイル: {file_path}")
            report.append("")
        
        if not issues:
            report.append("✅ 問題は検出されませんでした")
            return "\n".join(report)
        
        # 問題別に分類
        critical_issues = [i for i in issues if i.issue_type in ["FORBIDDEN_LEVEL", "FORBIDDEN_WP_LEVEL"]]
        warning_issues = [i for i in issues if i.issue_type in ["TEMPLATE_ID_FOUND", "LEVEL_TOO_DEEP"]]
        info_issues = [i for i in issues if i.issue_type in ["STATISTICS"]]
        
        if critical_issues:
            report.append("❌ 重大な問題:")
            for issue in critical_issues:
                report.append(f"  行 {issue.line_number}: {issue.heading_text}")
                report.append(f"    → {issue.suggestion}")
                report.append("")
        
        if warning_issues:
            report.append("⚠️ 警告:")
            for issue in warning_issues:
                report.append(f"  行 {issue.line_number}: {issue.heading_text}")
                report.append(f"    → {issue.suggestion}")
                report.append("")
        
        if info_issues:
            report.append("📊 統計情報:")
            for issue in info_issues:
                report.append(f"  {issue.suggestion}")
                report.append("")
        
        return "\n".join(report)

def validate_article_file(file_path: str) -> bool:
    """
    記事ファイルの簡易検証（外部から呼び出し用）
    
    Args:
        file_path: 検証するファイルパス
        
    Returns:
        検証成功可否
    """
    validator = HeadingValidator()
    is_valid, issues = validator.validate_markdown_file(file_path)
    
    if not is_valid:
        print(validator.generate_report(issues, file_path))
        return False
    
    print(f"✅ {os.path.basename(file_path)}: 見出し構造は正常です")
    return True

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) != 2:
        print("使用方法: python heading_validator.py <markdown_file>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = validate_article_file(file_path)
    sys.exit(0 if success else 1)
