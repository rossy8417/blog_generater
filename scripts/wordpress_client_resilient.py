#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress Blog Generator Client (Resilient Version)
信頼性機能強化版WordPressクライアント
"""

import os
import requests
import json
import re
import sys
from dotenv import load_dotenv
from typing import Dict, Any, Optional
import logging

# 相対パスでutilsモジュールを追加
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.api_resilience import with_wordpress_resilience, APICircuitOpenError, resilience_manager

# 環境変数読み込み
load_dotenv()

class ResilientWordPressClient:
    """信頼性機能強化版WordPressクライアント"""
    
    def __init__(self):
        self.api_key = os.getenv('WORDPRESS_API_KEY')
        self.endpoint = os.getenv('WORDPRESS_ENDPOINT')
        
        if not self.api_key:
            raise ValueError("WORDPRESS_API_KEY が .env ファイルに設定されていません")
        if not self.endpoint:
            raise ValueError("WORDPRESS_ENDPOINT が .env ファイルに設定されていません")
        
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': self.api_key
        }
        
        # ログ設定
        self.logger = logging.getLogger(__name__)
    
    @with_wordpress_resilience
    def create_post(self, 
                   title: str, 
                   content: str, 
                   excerpt: str = "", 
                   meta_description: str = "",
                   status: str = "draft",
                   featured_image_id: Optional[int] = None) -> Dict[str, Any]:
        """
        信頼性機能付きWordPress記事作成
        
        Args:
            title: 記事タイトル
            content: 記事本文（WordPressブロック形式）
            excerpt: 記事の抜粋
            meta_description: SEO用メタディスクリプション
            status: 投稿ステータス (draft, publish, private)
            featured_image_id: アイキャッチ画像のID
            
        Returns:
            作成された記事の情報を含む辞書
            
        Raises:
            APICircuitOpenError: サーキットブレーカーが開いている場合
            requests.exceptions.RequestException: API通信エラー
        """
        try:
            data = {
                'title': title,
                'content': content,
                'excerpt': excerpt,
                'meta_description': meta_description,
                'status': status
            }
            
            if featured_image_id:
                data['featured_media'] = featured_image_id
            
            self.logger.info(f"Creating WordPress post: {title[:50]}...")
            
            response = requests.post(
                f"{self.endpoint}/create-post",
                headers=self.headers,
                json=data,
                timeout=120  # WordPress投稿は時間がかかる可能性
            )
            
            # ステータスコードチェック
            if response.status_code == 429:
                # レート制限の場合、より具体的なエラー
                raise requests.exceptions.HTTPError(f"Rate limit exceeded for WordPress API", response=response)
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"WordPress post created successfully: ID {result.get('post_id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"WordPress API request failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in create_post: {e}")
            raise
    
    @with_wordpress_resilience
    def upload_image(self, image_path: str, alt_text: str = "") -> Dict[str, Any]:
        """
        信頼性機能付き画像アップロード
        
        Args:
            image_path: アップロードする画像ファイルのパス
            alt_text: 画像のalt属性
            
        Returns:
            アップロードされた画像の情報を含む辞書
        """
        try:
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            
            self.logger.info(f"Uploading image: {os.path.basename(image_path)}")
            
            with open(image_path, 'rb') as f:
                files = {'file': f}
                data = {'alt_text': alt_text}
                
                response = requests.post(
                    f"{self.endpoint}/upload-image",
                    headers={'X-API-Key': self.api_key},  # Content-Typeを除外
                    files=files,
                    data=data,
                    timeout=180  # 画像アップロードは時間がかかる
                )
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"Image uploaded successfully: ID {result.get('attachment_id')}")
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Image upload failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in upload_image: {e}")
            raise
    
    @with_wordpress_resilience
    def update_post(self, post_id: int, **kwargs) -> Dict[str, Any]:
        """
        信頼性機能付き記事更新
        
        Args:
            post_id: 更新する記事のID
            **kwargs: 更新するフィールド
            
        Returns:
            更新された記事の情報
        """
        try:
            self.logger.info(f"Updating WordPress post: {post_id}")
            
            response = requests.post(
                f"{self.endpoint}/update-post/{post_id}",
                headers=self.headers,
                json=kwargs,
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"WordPress post updated successfully: {post_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"WordPress post update failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in update_post: {e}")
            raise
    
    @with_wordpress_resilience
    def get_post(self, post_id: int) -> Dict[str, Any]:
        """
        信頼性機能付き記事取得
        
        Args:
            post_id: 取得する記事のID
            
        Returns:
            記事の情報
        """
        try:
            self.logger.info(f"Getting WordPress post: {post_id}")
            
            response = requests.get(
                f"{self.endpoint}/get-post/{post_id}",
                headers=self.headers,
                timeout=60
            )
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.info(f"WordPress post retrieved successfully: {post_id}")
            return result
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"WordPress post retrieval failed: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error in get_post: {e}")
            raise
    
    def get_circuit_status(self) -> Dict[str, Any]:
        """WordPress APIのサーキットブレーカー状態取得"""
        return resilience_manager.get_circuit_status().get("wordpress", {})
    
    def convert_markdown_to_gutenberg(self, markdown_content: str) -> str:
        """
        マークダウンをWordPress Gutenbergブロック形式に変換
        （既存機能を維持）
        """
        # ローカルメタディスクリプション除去
        content = re.sub(r'\*\*メタディスクリプション\*\*.*?(?=\n\n|\n#|\Z)', '', markdown_content, flags=re.DOTALL)
        
        # ローカル画像パス除去
        content = re.sub(r'!\[.*?\]\((?:outputs/|\.\.\/outputs/|/mnt/c/home/hiroshi/blog_generator/outputs/).*?\)', '', content)
        
        # Gutenbergブロック形式に変換
        lines = content.split('\n')
        gutenberg_blocks = []
        current_paragraph = []
        
        for line in lines:
            line = line.strip()
            
            if not line:
                if current_paragraph:
                    gutenberg_blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
                    current_paragraph = []
                continue
            
            # 見出しブロック
            if line.startswith('#'):
                if current_paragraph:
                    gutenberg_blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
                    current_paragraph = []
                
                level = len(line) - len(line.lstrip('#'))
                text = line.lstrip('#').strip()
                gutenberg_blocks.append(self._create_heading_block(text, level))
            
            # リストブロック
            elif line.startswith('- ') or line.startswith('* '):
                if current_paragraph:
                    gutenberg_blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
                    current_paragraph = []
                
                list_items = [line.lstrip('- *').strip()]
                gutenberg_blocks.append(self._create_list_block(list_items))
            
            # その他は段落として処理
            else:
                current_paragraph.append(line)
        
        # 最後の段落処理
        if current_paragraph:
            gutenberg_blocks.append(self._create_paragraph_block('\n'.join(current_paragraph)))
        
        return ''.join(gutenberg_blocks)
    
    def _create_paragraph_block(self, content: str) -> str:
        """段落ブロック作成"""
        return f'<!-- wp:paragraph -->\n<p>{content}</p>\n<!-- /wp:paragraph -->\n\n'
    
    def _create_heading_block(self, content: str, level: int) -> str:
        """見出しブロック作成"""
        return f'<!-- wp:heading {{"level":{level}}} -->\n<h{level}>{content}</h{level}>\n<!-- /wp:heading -->\n\n'
    
    def _create_list_block(self, items: list) -> str:
        """リストブロック作成"""
        list_html = '\n'.join(f'<li>{item}</li>' for item in items)
        return f'<!-- wp:list -->\n<ul>\n{list_html}\n</ul>\n<!-- /wp:list -->\n\n'

# 便利な関数
def create_resilient_wordpress_client() -> ResilientWordPressClient:
    """信頼性機能付きWordPressクライアント作成"""
    return ResilientWordPressClient()

def check_wordpress_api_health() -> Dict[str, Any]:
    """WordPress API健全性チェック"""
    client = ResilientWordPressClient()
    circuit_status = client.get_circuit_status()
    
    health_info = {
        "timestamp": "2025-01-14T10:30:00Z",
        "circuit_breaker": circuit_status,
        "status": "healthy" if circuit_status.get("state") == "closed" else "degraded"
    }
    
    return health_info

if __name__ == "__main__":
    # 使用例
    try:
        client = ResilientWordPressClient()
        
        # 記事作成テスト
        test_content = "# テスト記事\n\nこれはテスト記事です。"
        result = client.create_post(
            title="API信頼性テスト記事",
            content=client.convert_markdown_to_gutenberg(test_content),
            status="draft"
        )
        
        print(f"記事作成成功: {result}")
        
        # 健全性チェック
        health = check_wordpress_api_health()
        print(f"API健全性: {health}")
        
    except APICircuitOpenError as e:
        print(f"API回路が開いています: {e}")
    except Exception as e:
        print(f"API呼び出しエラー: {e}")