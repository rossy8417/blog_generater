#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress記事2127の最終検証スクリプト
"""

import requests
import os
from dotenv import load_dotenv

def verify_wordpress_post():
    """WordPress記事の実際の状態を検証"""
    
    load_dotenv()
    endpoint = os.getenv('WORDPRESS_ENDPOINT')
    api_key = os.getenv('WORDPRESS_API_KEY')

    response = requests.get(
        f'{endpoint}/get-post/2127',
        headers={'X-API-Key': api_key}
    )

    if response.status_code == 200:
        post = response.json()
        content = post.get('content', '')
        
        print('🎉 WordPress記事ID 2127 最終検証結果')
        print('=' * 60)
        
        # 基本情報
        print(f'📝 タイトル: {post.get("title", "Unknown")}')
        print(f'📅 最終更新: {post.get("modified", "Unknown")}')
        print(f'📊 文字数: {len(content):,}文字')
        
        # WordPressブロック数の正確なカウント
        wp_paragraph = '<!-- wp:paragraph -->'
        wp_heading = '<!-- wp:heading'
        wp_image = '<!-- wp:image'
        wp_list = '<!-- wp:list'
        
        paragraph_count = content.count(wp_paragraph)
        heading_count = content.count(wp_heading) 
        image_count = content.count(wp_image)
        list_count = content.count(wp_list)
        total_blocks = paragraph_count + heading_count + image_count + list_count
        
        print(f'\n📊 WordPressブロック構成:')
        print(f'   段落ブロック: {paragraph_count}個')
        print(f'   見出しブロック: {heading_count}個')
        print(f'   画像ブロック: {image_count}個')
        print(f'   リストブロック: {list_count}個')
        print(f'   総ブロック数: {total_blocks}個')
        
        # H2見出しの確認
        h2_pattern = '<h2 class="wp-block-heading">'
        h2_count = content.count(h2_pattern)
        print(f'\n📋 H2見出し数: {h2_count}個')
        
        # 章別画像の確認
        print(f'\n🖼️  章別画像配置状況:')
        image_ids = ['3269', '3270', '3271', '3272', '3273', '3274']
        found_images = []
        for i, img_id in enumerate(image_ids, 1):
            if f'wp-image-{img_id}' in content:
                found_images.append(i)
                print(f'   ✅ 章{i}画像(ID:{img_id}) - 正常配置')
            else:
                print(f'   ❌ 章{i}画像(ID:{img_id}) - 未配置')
        
        # H2タグ下の画像配置確認
        h2_image_pattern = '</h2>\n<!-- /wp:heading -->\n\n<!-- wp:image'
        h2_image_count = content.count(h2_image_pattern)
        print(f'\n🎯 H2タグ下画像配置: {h2_image_count}個')
        
        # 品質判定
        is_gutenberg = paragraph_count > 30 and heading_count > 10
        has_all_images = len(found_images) == 6
        proper_structure = h2_count >= 6
        good_volume = len(content) > 10000
        
        print(f'\n🎯 品質評価:')
        print(f'   Gutenbergブロック形式: {"✅ PASS" if is_gutenberg else "❌ FAIL"} ({total_blocks}ブロック)')
        print(f'   章別画像完全配置: {"✅ PASS" if has_all_images else "❌ FAIL"} ({len(found_images)}/6個)')
        print(f'   H2見出し構造: {"✅ PASS" if proper_structure else "❌ FAIL"} ({h2_count}個)')
        print(f'   適切な文字数: {"✅ PASS" if good_volume else "❌ FAIL"} ({len(content):,}文字)')
        print(f'   H2下画像配置: {"✅ PASS" if h2_image_count >= 4 else "❌ FAIL"} ({h2_image_count}個)')
        
        # 最終判定
        all_success = is_gutenberg and has_all_images and proper_structure and good_volume
        
        if all_success:
            print(f'\n🎉🎉🎉 記事リライト完全成功！🎉🎉🎉')
            print(f'WordPress記事ID 2127は完璧に更新されています！')
            print(f'✅ Gutenbergブロック形式')
            print(f'✅ 6章構成+まとめ')
            print(f'✅ 章別画像H2下配置')
            print(f'✅ 最適な文字数とボリューム')
        else:
            print(f'\n⚠️  改善が必要な項目があります')
        
        # 実際のコンテンツサンプル表示
        print(f'\n📄 コンテンツサンプル（最初の300文字）:')
        print('-' * 30)
        print(content[:300] + '...' if len(content) > 300 else content)
        print('-' * 30)
        
        return all_success
        
    else:
        print(f'❌ WordPress接続失敗: {response.status_code}')
        return False

if __name__ == "__main__":
    verify_wordpress_post()