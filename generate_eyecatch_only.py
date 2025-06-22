#!/usr/bin/env python3
"""
アイキャッチ画像のみを生成する簡単なスクリプト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from scripts.image_generator import BlogImageGenerator

def generate_eyecatch_simple():
    """簡単なアイキャッチ生成"""
    
    # 画像ジェネレーター初期化
    generator = BlogImageGenerator()
    
    # アイキャッチ用のプロンプト（日本語テキスト付き）
    eyecatch_prompt = """
Professional blog header image with Japanese text overlay. 
Main title: "生成AI定型業務自動化完全ガイド" 
Subtitle: "効率化・生産性向上の実践手法"
Modern office setting with AI automation elements, 
blue and orange color scheme, clean professional design, 
business automation icons, digital transformation theme,
high quality, engaging composition, 16:9 aspect ratio
"""
    
    print("🎨 Generating optimized eyecatch image...")
    
    # OpenAI gpt-image-1でアイキャッチ生成
    image_data = generator.generate_image_openai(eyecatch_prompt)
    if not image_data:
        print("❌ Failed to generate image")
        return None
    
    # 最適化
    print("📦 Optimizing image...")
    original_size_kb = len(image_data) / 1024
    print(f"   Original size: {original_size_kb:.1f}KB")
    
    optimized_data = generator.optimize_image(image_data, 'eyecatch')
    optimized_size_kb = len(optimized_data) / 1024
    print(f"   Optimized size: {optimized_size_kb:.1f}KB ({(1-optimized_size_kb/original_size_kb)*100:.1f}% reduction)")
    
    # 保存先のディレクトリ
    output_dir = Path("outputs/生成AI定型業務自動化完全ガイド-INT-01")
    
    # ファイル名生成（最適化された拡張子で）
    from datetime import datetime
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_eyecatch_optimized.jpg"
    filepath = output_dir / filename
    
    # 保存
    with open(filepath, 'wb') as f:
        f.write(optimized_data)
    
    print(f"✅ Optimized eyecatch saved: {filepath}")
    print(f"📊 Final size: {optimized_size_kb:.1f}KB")
    return str(filepath)

if __name__ == "__main__":
    generate_eyecatch_simple()