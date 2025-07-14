#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress標準REST APIで記事確認
"""

import requests

def check_wordpress_standard_api():
    """WordPress標準REST APIで記事2127を確認"""
    
    # WordPressの標準REST APIを使用
    wordpress_url = 'https://www.ht-sw.tech'
    api_endpoint = f'{wordpress_url}/wp-json/wp/v2/posts/2127'

    print('🔍 WordPress標準REST API確認')
    print(f'URL: {api_endpoint}')
    print('=' * 50)

    try:
        response = requests.get(api_endpoint, timeout=10)
        
        print(f'ステータスコード: {response.status_code}')
        
        if response.status_code == 200:
            data = response.json()
            
            print(f'\n記事情報:')
            print(f'ID: {data.get("id")}')
            print(f'タイトル: {data.get("title", {}).get("rendered", "Unknown")}')
            print(f'ステータス: {data.get("status")}')
            print(f'最終更新: {data.get("modified")}')
            
            # コンテンツ確認
            content = data.get('content', {}).get('rendered', '')
            print(f'\nコンテンツ情報:')
            print(f'文字数: {len(content):,}文字')
            
            # 実際のコンテンツ形式確認
            print(f'\nコンテンツ形式確認:')
            print(f'開始文字（200文字）: {repr(content[:200])}')
            
            # Gutenbergブロック確認
            wp_block_marker = '<!-- wp:'
            if wp_block_marker in content:
                wp_blocks = content.count(wp_block_marker)
                print(f'\n✅ Gutenbergブロック形式')
                print(f'ブロック数: {wp_blocks}個')
                
                # 詳細なブロック分析
                paragraph_blocks = content.count('<!-- wp:paragraph -->')
                heading_blocks = content.count('<!-- wp:heading')
                image_blocks = content.count('<!-- wp:image')
                list_blocks = content.count('<!-- wp:list')
                
                print(f'   段落ブロック: {paragraph_blocks}個')
                print(f'   見出しブロック: {heading_blocks}個')
                print(f'   画像ブロック: {image_blocks}個')
                print(f'   リストブロック: {list_blocks}個')
            else:
                print(f'\n❌ Gutenbergブロック形式ではない')
                
            # 画像確認
            image_count = content.count('<img')
            print(f'\n🖼️ 画像情報:')
            print(f'総画像数: {image_count}個')
            
            # 章別画像ID確認
            print(f'\n📋 章別画像確認:')
            image_ids = ['3269', '3270', '3271', '3272', '3273', '3274']
            found_images = 0
            for i, img_id in enumerate(image_ids, 1):
                if f'wp-image-{img_id}' in content:
                    print(f'   ✅ 章{i}画像(ID:{img_id})')
                    found_images += 1
                else:
                    print(f'   ❌ 章{i}画像(ID:{img_id})')
            
            # H2見出し確認
            h2_count = content.count('<h2')
            print(f'\n📋 見出し構造:')
            print(f'H2見出し数: {h2_count}個')
            
            # 最終判定
            is_gutenberg = wp_block_marker in content
            has_all_images = found_images == 6
            good_structure = h2_count >= 6
            
            print(f'\n🎯 最終判定:')
            print(f'   記事ステータス: {data.get("status")}')
            print(f'   Gutenbergブロック: {"✅ YES" if is_gutenberg else "❌ NO"}')
            print(f'   章別画像完備: {"✅ YES" if has_all_images else "❌ NO"} ({found_images}/6個)')
            print(f'   見出し構造: {"✅ YES" if good_structure else "❌ NO"} ({h2_count}個)')
            
            if is_gutenberg and has_all_images and good_structure:
                print(f'\n🎉 WordPress標準API確認: 完全成功!')
                print(f'記事は正常にGutenbergブロック形式で更新されています')
            else:
                print(f'\n⚠️  改善が必要な項目があります')
                
            return True
            
        elif response.status_code == 404:
            print(f'❌ 記事が見つかりません')
            return False
        else:
            print(f'❌ エラー: {response.status_code}')
            print(f'レスポンス: {response.text[:300]}')
            return False
            
    except Exception as e:
        print(f'❌ 接続エラー: {e}')
        return False

if __name__ == "__main__":
    check_wordpress_standard_api()