#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ユーザー要求を反映したアイキャッチ生成
既存テンプレート + ユーザー指定テーマでカスタマイズ
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.append('/mnt/c/home/hiroshi/blog_generator/scripts')
from image_generator import BlogImageGenerator

def generate_custom_eyecatch():
    """ユーザー要求「AI時代に大切な人間らしさ」を反映したアイキャッチ生成"""
    
    # アウトラインデータ読み込み
    outline_path = "/mnt/c/home/hiroshi/blog_generator/outputs/AI時代を制する記事リライト企画-INT-01/outline_content.md"
    
    with open(outline_path, 'r', encoding='utf-8') as f:
        outline_content = f.read()
    
    # アウトラインデータを辞書形式に変換
    outline_data = {
        'title': 'AI時代を制する記事リライト企画｜人間らしさで勝つ6つの必須スキル',
        'meta_description': 'AI時代だからこそ必要な人間力とは？共感力・感情管理・コミュニケーション・適応力・勇気・働き方設計の6つのスキルで、技術に負けない価値を身につけましょう。',
        'outline_id': 'INT-01',
        'timestamp': datetime.now().strftime('%Y%m%d_%H%M%S'),
        'date': datetime.now().strftime('%Y-%m-%d'),
        'user_request': 'AI時代に大切な人間らしさ - 温かい感情的つながりと共感を重視した、親しみやすくて心に響くデザイン',
        'content': outline_content
    }
    
    print(f"🎨 ユーザー要求に基づくアイキャッチ生成開始")
    print(f"   記事タイトル: {outline_data['title']}")
    print(f"   ユーザー要求: {outline_data['user_request']}")
    
    # 画像生成器初期化
    generator = BlogImageGenerator()
    
    # カスタムプロンプト生成（テンプレート + ユーザー要求）
    custom_prompt = f"""
テンプレートガイドライン: {open('/mnt/c/home/hiroshi/blog_generator/templates/eyecatch.md', 'r', encoding='utf-8').read()}

記事情報:
- タイトル: {outline_data['title']}  
- メタ説明: {outline_data['meta_description']}
- ユーザー特別要求: {outline_data['user_request']}

上記テンプレートを基に、ユーザーの特別要求「{outline_data['user_request']}」を重視したアイキャッチ画像のYAML設定を作成してください。

特に以下を強調:
- 人間らしい温かさと感情的つながり
- AI時代における人間の価値
- 親しみやすくて心に響くビジュアル
- フォーマル過ぎない、人間味のあるデザイン
- 共感と理解を促すカラーパレット
"""
    
    # ユーザー要求に基づくカスタム画像プロンプト直接生成
    print(f"🎨 カスタム画像プロンプト生成中...")
    
    # 人間らしさと温かさを重視したプロンプト
    image_prompt = """
A warm and heartfelt digital illustration showing human connection and empathy in the AI era. 
The image features diverse people of different ages connecting emotionally - a gentle elderly person talking with young professionals, families sharing moments, friends supporting each other. 
The background has soft, warm colors like amber, cream, and gentle blues with subtle AI elements (floating gentle lights, soft digital patterns) that enhance rather than dominate the human elements.
The overall mood is approachable, warm, and emphasizes human qualities that matter in the digital age: empathy, understanding, emotional intelligence, and genuine human connection.
Include Japanese text overlay: "AI時代を制する" in elegant, readable font at the top, and "人間らしさで勝つ6つの必須スキル" as subtitle at the bottom.
Professional quality, 16:9 aspect ratio, modern but warm design aesthetic.
"""
    print(f"🖼️ 画像生成プロンプト: {image_prompt[:200]}...")
    
    # OpenAI gpt-image-1でアイキャッチ画像生成
    print(f"🎨 OpenAI gpt-image-1で画像生成中...")
    image_data = generator.generate_image_openai(image_prompt)
    
    if not image_data:
        print(f"❌ 画像生成に失敗")
        return None
    
    # 画像最適化
    print(f"📦 画像最適化中...")
    original_size_kb = len(image_data) / 1024
    print(f"   元サイズ: {original_size_kb:.1f}KB")
    
    optimized_data = generator.optimize_image(image_data, 'eyecatch')
    optimized_size_kb = len(optimized_data) / 1024
    reduction = (1 - optimized_size_kb/original_size_kb) * 100
    print(f"   最適化後: {optimized_size_kb:.1f}KB ({reduction:.1f}% 削減)")
    
    # 画像保存
    metadata = {
        'title': outline_data['title'],
        'date': outline_data['date'],
        'int_number': outline_data['outline_id'],
        'timestamp': outline_data['timestamp'],
        'user_request': outline_data['user_request']
    }
    
    saved_path = generator.save_image(optimized_data, '', metadata, 'eyecatch')
    
    if saved_path:
        print(f"✅ カスタムアイキャッチ生成完了!")
        print(f"   保存先: {saved_path}")
        print(f"   ファイルサイズ: {optimized_size_kb:.1f}KB")
        return saved_path
    else:
        print(f"❌ 画像保存に失敗")
        return None

if __name__ == "__main__":
    result = generate_custom_eyecatch()
    if result:
        print(f"\n🎉 ユーザー要求「AI時代に大切な人間らしさ」を反映した")
        print(f"   温かみのあるアイキャッチ画像が生成されました！")
        print(f"   次のステップ: WordPressアップロード & 記事2127への設定")
    else:
        print(f"\n❌ カスタムアイキャッチ生成に失敗しました")