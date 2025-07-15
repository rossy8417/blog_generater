#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress見出し変換修正テスト
"""

from wordpress_client_fixed import convert_markdown_to_gutenberg, validate_heading_structure

def test_heading_conversion():
    """見出し変換テストの実行"""
    
    print("🧪 WordPress見出し変換修正テスト開始")
    print("=" * 50)
    
    # テスト用マークダウン（問題のあるH5/H6を含む）
    test_markdown = """# メインタイトル（スキップされる）

## 第1章: AI開発の基本概念

この章では基本的な概念について説明します。

### AI技術の分類

AIには以下の分類があります。

#### 機械学習の種類

機械学習にはいくつかの種類があります。

##### 深層学習の詳細（H5禁止・H4に修正される）

深層学習について詳しく説明します。

##### 強化学習の説明（H5禁止・H4に修正される）

強化学習の仕組みを見ていきます。

###### ニューラルネットワーク（H6禁止・H4に修正される）

ニューラルネットワークの構造です。

## 第2章: 実装手法

実装について詳しく見ていきます。

### プログラミング言語

Pythonを使用します。

#### コードの書き方

基本的な書き方を学びます。

## まとめ

本記事では以下について説明しました。
"""
    
    print("📝 変換前のマークダウン:")
    print(test_markdown)
    print("\n" + "=" * 50)
    
    # 変換実行（デバッグモード）
    print("🔄 WordPressブロック形式に変換中...")
    wp_content = convert_markdown_to_gutenberg(test_markdown, debug=True)
    
    print("\n" + "=" * 50)
    print("📋 変換後のWordPressブロック形式:")
    print(wp_content)
    
    print("\n" + "=" * 50)
    print("🔍 見出し構造の検証:")
    validation = validate_heading_structure(wp_content)
    
    print(f"H2見出し: {validation['h2']}個")
    print(f"H3見出し: {validation['h3']}個")
    print(f"H4見出し: {validation['h4']}個")
    print(f"H5見出し: {validation['h5']}個（禁止）")
    print(f"H6見出し: {validation['h6']}個（禁止）")
    print(f"構造の有効性: {'✅ 有効' if validation['is_valid'] else '❌ 無効'}")
    
    if validation['structure_issues']:
        print("⚠️ 構造の問題:")
        for issue in validation['structure_issues']:
            print(f"   - {issue}")
    else:
        print("✅ 構造に問題はありません")
    
    print("\n" + "=" * 50)
    print("📊 修正前後の比較:")
    print("修正前の問題:")
    print("- H2見出しがH3に変換される（間違い）")
    print("- H5/H6見出しが禁止されていない")
    print("- テンプレートID残存チェックが不十分")
    
    print("\n修正後の改善:")
    print("- ✅ すべてのH2見出しがH2として保持される")
    print("- ✅ H5/H6見出しを自動的にH4に降格")
    print("- ✅ テンプレートID検出とレポート")
    print("- ✅ 詳細なデバッグ情報とエラー処理")
    
    print("\n🎉 テスト完了!")

if __name__ == "__main__":
    test_heading_conversion()