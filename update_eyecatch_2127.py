#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
記事2127のアイキャッチ画像を人間らしさを強調した新画像に更新
"""

import sys
import os
from PIL import Image
import requests
from dotenv import load_dotenv

# スクリプトディレクトリを追加
sys.path.append('/mnt/c/home/hiroshi/blog_generator/scripts')
from wordpress_client import WordPressClient

load_dotenv()

def optimize_and_upload_eyecatch():
    """アイキャッチ画像を最適化してWordPressにアップロード・設定"""
    
    # 画像パスを確認
    image_path = "/mnt/c/home/hiroshi/blog_generator/outputs/AI時代を制する記事リライト企画-INT-01/outputs/AI時代を制する記事リライト企画-INT-01/20250714_human_warmth_eyecatch.jpg"
    
    if not os.path.exists(image_path):
        print(f"❌ 画像ファイルが見つかりません: {image_path}")
        return False
    
    print(f"🖼️ 画像を最適化中...")
    
    # PIL画像処理でサイズ最適化
    with Image.open(image_path) as img:
        # RGBモードに変換（透明度対応）
        if img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'P':
                img = img.convert('RGBA')
            rgb_img.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
            img = rgb_img
        
        # サイズ調整（幅1200px、高さ比例）
        if img.width > 1200:
            ratio = 1200 / img.width
            new_height = int(img.height * ratio)
            img = img.resize((1200, new_height), Image.Resampling.LANCZOS)
        
        # 最適化された画像として保存
        optimized_path = "/mnt/c/home/hiroshi/blog_generator/20250714_human_warmth_optimized.jpg"
        img.save(optimized_path, 'JPEG', quality=85, optimize=True, progressive=True)
    
    file_size = os.path.getsize(optimized_path)
    print(f"✅ 画像最適化完了: {file_size/1024:.1f}KB")
    
    # WordPressクライアント初期化
    client = WordPressClient()
    
    print(f"📤 WordPressにアップロード中...")
    
    # 画像をアップロード
    upload_result = client.upload_image(
        image_path=optimized_path,
        alt_text="AI時代における人間らしさとつながり - アイキャッチ画像"
    )
    
    if not upload_result:
        print(f"❌ 画像アップロードに失敗")
        return False
    
    # IDの取得を修正
    media_id = upload_result.get('id') or upload_result.get('attachment_id')
    if not media_id:
        print(f"❌ アップロード結果からIDを取得できませんでした: {upload_result}")
        return False
    print(f"✅ 画像アップロード成功: ID {media_id}")
    
    # 記事2127のアイキャッチに設定
    print(f"🎯 記事2127のアイキャッチ画像を更新中...")
    
    try:
        # カスタムAPIエンドポイントでアイキャッチ更新
        api_url = f"{os.getenv('WORDPRESS_ENDPOINT')}/wp-json/blog-generator/v1/update-post"
        headers = {
            'X-API-Key': os.getenv('WORDPRESS_API_KEY'),
            'Content-Type': 'application/json'
        }
        
        update_data = {
            'post_id': 2127,
            'featured_media': media_id
        }
        
        response = requests.post(api_url, json=update_data, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ アイキャッチ画像更新成功")
            print(f"   記事ID: {result.get('id')}")
            print(f"   アイキャッチID: {result.get('featured_media')}")
            print(f"   更新時刻: {result.get('modified')}")
            
            # クリーンアップ
            if os.path.exists(optimized_path):
                os.remove(optimized_path)
            
            return True
        else:
            print(f"❌ アイキャッチ更新失敗: {response.status_code}")
            print(f"エラー: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ アイキャッチ更新エラー: {e}")
        return False

if __name__ == "__main__":
    success = optimize_and_upload_eyecatch()
    if success:
        print(f"\n🎉 記事2127のアイキャッチ画像更新完了!")
        print(f"新しいアイキャッチ画像は「AI時代における人間らしさとつながり」をテーマにした")
        print(f"温かみのあるビジュアルに更新されました。")
    else:
        print(f"\n❌ アイキャッチ画像更新に失敗しました。")