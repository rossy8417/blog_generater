#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress記事更新クライアント - 革新的更新機能
Boss1 & Worker1 共同開発による次世代WordPressクライアント
"""

import os
import requests
import json
import re
from datetime import datetime
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from difflib import SequenceMatcher

# 環境変数読み込み
load_dotenv()

class WordPressUpdateError(Exception):
    """WordPress更新関連エラー"""
    pass

class PostNotFoundError(WordPressUpdateError):
    """記事が見つからない"""
    pass

class InsufficientPermissionError(WordPressUpdateError):
    """更新権限不足"""
    pass

class UpdateConflictError(WordPressUpdateError):
    """更新競合エラー"""
    pass

class WordPressUpdateClient:
    """次世代WordPress記事更新クライアント - Worker3拡張版"""
    
    def __init__(self, integration_mode: bool = False):
        """
        初期化
        
        Args:
            integration_mode: post_blog_universal.pyとの統合モード
        """
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
        
        # 更新履歴管理
        self.update_history = []
        
        # 統合モード設定
        self.integration_mode = integration_mode
        
        # Worker3拡張機能
        self.image_cache = {}
        self.conversion_cache = {}
        self.validation_rules = {
            'title': {'min_length': 5, 'max_length': 200},
            'content': {'min_length': 500, 'max_length': 100000},
            'excerpt': {'max_length': 300}
        }
    
    def update_post(self, 
                   post_id: int,
                   title: Optional[str] = None,
                   content: Optional[str] = None,
                   excerpt: Optional[str] = None,
                   meta_description: Optional[str] = None,
                   status: Optional[str] = None,
                   featured_image_id: Optional[int] = None,
                   backup: bool = True,
                   diff_update: bool = True) -> Dict[str, Any]:
        """
        WordPress記事更新（革新的機能付き）
        
        Args:
            post_id: 更新対象の投稿ID
            title: 新しいタイトル（Noneの場合は更新しない）
            content: 新しい本文（WordPressブロック形式）
            excerpt: 新しい抜粋
            meta_description: SEO用メタディスクリプション
            status: 投稿ステータス (draft, publish, private)
            featured_image_id: アイキャッチ画像ID
            backup: 更新前のバックアップ作成有無
            diff_update: 差分更新の有効化
        
        Returns:
            更新結果とメタデータ
        """
        
        print(f"🚀 WordPress記事更新開始 (ID: {post_id})")
        
        # 1. 入力検証
        if not isinstance(post_id, int) or post_id <= 0:
            raise ValueError("有効な投稿IDを指定してください")
        
        # 2. 既存記事の取得
        current_post = None
        if diff_update or backup:
            try:
                current_post = self.get_post(post_id)
                print(f"📖 既存記事取得完了: {current_post.get('title', 'Unknown')}")
            except Exception as e:
                print(f"⚠️  既存記事取得失敗: {str(e)}")
        
        # 3. バックアップ作成（オプション）
        backup_result = None
        if backup and current_post:
            try:
                backup_result = self._create_backup(post_id, current_post)
                print(f"📋 バックアップ作成完了: ID {backup_result.get('backup_id')}")
            except Exception as e:
                print(f"⚠️  バックアップ作成失敗: {str(e)}")
        
        # 4. 差分更新判定
        update_strategy = "full"
        if diff_update and content and current_post:
            current_content = current_post.get('content', '')
            diff_ratio = self._calculate_diff_ratio(current_content, content)
            if diff_ratio < 0.3:  # 30%未満の変更
                update_strategy = "diff"
                print(f"🔄 差分更新モード: 変更率 {diff_ratio:.1%}")
            else:
                print(f"📝 全体更新モード: 変更率 {diff_ratio:.1%}")
        
        # 5. 更新データ構築
        update_data = self._build_update_data(
            title=title,
            content=content,
            excerpt=excerpt,
            meta_description=meta_description,
            status=status,
            featured_image_id=featured_image_id
        )
        
        if not update_data:
            raise ValueError("更新するデータが指定されていません")
        
        # 6. API呼び出し実行
        try:
            update_data['update_strategy'] = update_strategy
            update_data['timestamp'] = datetime.now().isoformat()
            
            print(f"✏️  記事更新実行中... (戦略: {update_strategy})")
            print(f"   更新項目: {list(update_data.keys())}")
            
            response = requests.put(
                f"{self.endpoint}/update-post/{post_id}",
                headers=self.headers,
                json=update_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                self._record_update_history(post_id, update_data, result, backup_result)
                
                print(f"✅ 記事更新成功!")
                print(f"   投稿ID: {result.get('post_id', post_id)}")
                print(f"   更新時刻: {result.get('modified_time', 'Unknown')}")
                print(f"   更新URL: {result.get('edit_link', 'N/A')}")
                
                return result
            else:
                self._handle_api_error(response)
                
        except requests.exceptions.RequestException as e:
            error_msg = f"接続エラー: {str(e)}"
            print(f"❌ {error_msg}")
            raise WordPressUpdateError(error_msg)
    
    def get_post(self, post_id: int) -> Dict[str, Any]:
        """記事データ取得"""
        try:
            response = requests.get(
                f"{self.endpoint}/get-post/{post_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                raise PostNotFoundError(f"投稿ID {post_id} が見つかりません")
            else:
                raise WordPressUpdateError(f"記事取得エラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise WordPressUpdateError(f"記事取得に失敗: {str(e)}")
    
    def batch_update_posts(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """複数記事の一括更新"""
        print(f"🔄 バッチ更新開始: {len(updates)}件の記事")
        
        results = []
        for i, update_config in enumerate(updates, 1):
            post_id = update_config.pop('post_id')
            print(f"\n📝 [{i}/{len(updates)}] 記事ID {post_id} 更新中...")
            
            try:
                result = self.update_post(post_id, **update_config)
                results.append({"post_id": post_id, "success": True, "result": result})
            except Exception as e:
                error_msg = str(e)
                print(f"❌ 記事ID {post_id} 更新失敗: {error_msg}")
                results.append({"post_id": post_id, "success": False, "error": error_msg})
        
        success_count = sum(1 for r in results if r["success"])
        print(f"\n🎉 バッチ更新完了: {success_count}/{len(updates)} 件成功")
        
        return results
    
    def restore_from_backup(self, post_id: int, backup_id: str) -> Dict[str, Any]:
        """バックアップからの復元"""
        print(f"🔄 記事復元開始: ID {post_id}, バックアップ {backup_id}")
        
        try:
            response = requests.post(
                f"{self.endpoint}/restore-post/{post_id}",
                headers=self.headers,
                json={"backup_id": backup_id},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ 記事復元完了: {result.get('restored_time')}")
                return result
            else:
                raise WordPressUpdateError(f"復元エラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise WordPressUpdateError(f"復元失敗: {str(e)}")
    
    def get_update_history(self, post_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """更新履歴取得"""
        if post_id:
            return [h for h in self.update_history if h.get('post_id') == post_id]
        return self.update_history
    
    def _build_update_data(self, **kwargs) -> Dict[str, Any]:
        """更新データ構築"""
        update_data = {}
        
        for key, value in kwargs.items():
            if value is not None:
                update_data[key] = value
        
        return update_data
    
    def _create_backup(self, post_id: int, current_post: Dict[str, Any]) -> Dict[str, Any]:
        """記事のバックアップ作成"""
        backup_data = {
            "post_id": post_id,
            "content": current_post,
            "created_at": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                f"{self.endpoint}/backup-post/{post_id}",
                headers=self.headers,
                json=backup_data,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise WordPressUpdateError(f"バックアップ作成エラー: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            raise WordPressUpdateError(f"バックアップ作成失敗: {str(e)}")
    
    def _calculate_diff_ratio(self, old_content: str, new_content: str) -> float:
        """変更率計算"""
        if not old_content:
            return 1.0
        
        similarity = SequenceMatcher(None, old_content, new_content).ratio()
        return 1.0 - similarity
    
    def _record_update_history(self, post_id: int, update_data: Dict[str, Any], 
                              result: Dict[str, Any], backup_result: Optional[Dict[str, Any]]):
        """更新履歴記録"""
        history_entry = {
            "post_id": post_id,
            "updated_at": datetime.now().isoformat(),
            "update_data": update_data,
            "result": result,
            "backup_id": backup_result.get('backup_id') if backup_result else None
        }
        
        self.update_history.append(history_entry)
        
        # 履歴の上限管理（最新100件まで）
        if len(self.update_history) > 100:
            self.update_history = self.update_history[-100:]
    
    def _handle_api_error(self, response: requests.Response):
        """APIエラーハンドリング"""
        try:
            error_data = response.json()
            error_code = error_data.get('code', 'unknown')
            error_message = error_data.get('message', 'Unknown error')
        except:
            error_code = 'http_error'
            error_message = response.text
        
        print(f"❌ API エラー: {response.status_code}")
        print(f"   エラーコード: {error_code}")
        print(f"   メッセージ: {error_message}")
        
        if response.status_code == 404:
            raise PostNotFoundError(error_message)
        elif response.status_code == 403:
            raise InsufficientPermissionError(error_message)
        elif response.status_code == 409:
            raise UpdateConflictError(error_message)
        else:
            raise WordPressUpdateError(f"{error_code}: {error_message}")
    
    def update_post_from_markdown(self, post_id: int, markdown_file: str, 
                                 image_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Markdownファイルから記事更新（Worker3統合機能）
        
        Args:
            post_id: 更新対象の投稿ID
            markdown_file: Markdownファイルパス
            image_dir: 画像ディレクトリ
            **kwargs: 追加のupdate_post引数
        """
        print(f"📝 Markdownから記事更新: {markdown_file}")
        
        # Markdown読み込み
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdownファイルが見つかりません: {markdown_file}")
        
        with open(markdown_file, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        
        # タイトル抽出
        title_match = re.search(r'^#\s+(.+)$', markdown_content, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else None
        
        # コンテンツ変換（統合モード対応）
        if self.integration_mode:
            content = self._convert_markdown_integrated(markdown_content, image_dir)
        else:
            content = self._convert_markdown_basic(markdown_content)
        
        # 記事更新実行
        return self.update_post(
            post_id=post_id,
            title=title,
            content=content,
            **kwargs
        )
    
    def validate_content(self, content_type: str, content: str) -> bool:
        """
        コンテンツ検証（Worker3品質管理機能）
        """
        if content_type not in self.validation_rules:
            return True
        
        rules = self.validation_rules[content_type]
        content_length = len(content.strip())
        
        if 'min_length' in rules and content_length < rules['min_length']:
            raise ValueError(f"{content_type} が短すぎます: {content_length} < {rules['min_length']}")
        
        if 'max_length' in rules and content_length > rules['max_length']:
            raise ValueError(f"{content_type} が長すぎます: {content_length} > {rules['max_length']}")
        
        return True
    
    def search_posts_by_title(self, title: str, fuzzy: bool = True) -> List[Dict[str, Any]]:
        """
        タイトルによる記事検索（Worker3検索機能）
        """
        try:
            params = {'title': title, 'fuzzy': fuzzy}
            response = requests.get(
                f"{self.endpoint}/search-posts",
                headers=self.headers,
                params=params,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except requests.exceptions.RequestException:
            return []
    
    def get_post_analytics(self, post_id: int) -> Dict[str, Any]:
        """
        記事分析データ取得（Worker3分析機能）
        """
        try:
            response = requests.get(
                f"{self.endpoint}/analytics/{post_id}",
                headers=self.headers,
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {}
                
        except requests.exceptions.RequestException:
            return {}
    
    def _convert_markdown_integrated(self, markdown_content: str, image_dir: str = None) -> str:
        """
        統合Markdown変換（post_blog_universal.py連携）
        """
        # キャッシュチェック
        cache_key = hash(markdown_content)
        if cache_key in self.conversion_cache:
            print("📋 キャッシュからコンテンツ取得")
            return self.conversion_cache[cache_key]
        
        try:
            # post_blog_universal.pyの変換機能を使用
            sys.path.append('/mnt/c/home/hiroshi/blog_generator/scripts')
            from wordpress_client import convert_markdown_to_gutenberg, insert_chapter_images
            
            # 基本変換
            gutenberg_content = convert_markdown_to_gutenberg(markdown_content)
            
            # 画像挿入
            if image_dir and os.path.exists(image_dir):
                gutenberg_content = insert_chapter_images(gutenberg_content, image_dir)
                print(f"🖼️  章画像挿入完了: {image_dir}")
            
            # キャッシュ保存
            self.conversion_cache[cache_key] = gutenberg_content
            return gutenberg_content
            
        except ImportError as e:
            print(f"⚠️  統合変換失敗、基本変換を使用: {e}")
            return self._convert_markdown_basic(markdown_content)
    
    def _convert_markdown_basic(self, markdown_content: str) -> str:
        """
        基本Markdown変換
        """
        # 簡易的なMarkdown→HTML変換
        content = markdown_content
        
        # 見出し変換
        content = re.sub(r'^### (.+)$', r'<h3>\1</h3>', content, flags=re.MULTILINE)
        content = re.sub(r'^## (.+)$', r'<h2>\1</h2>', content, flags=re.MULTILINE)
        content = re.sub(r'^# (.+)$', r'<h1>\1</h1>', content, flags=re.MULTILINE)
        
        # 段落変換
        paragraphs = content.split('\n\n')
        converted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para and not para.startswith('<'):
                para = f'<p>{para}</p>'
            converted_paragraphs.append(para)
        
        return '\n\n'.join(converted_paragraphs)


def main():
    """メイン実行関数"""
    print("🎉 WordPress記事更新クライアント - 革新的更新機能")
    print("Boss1 & Worker1 共同開発版")
    
    try:
        client = WordPressUpdateClient()
        print("✅ クライアント初期化完了")
        print("📋 利用可能な機能:")
        print("   - update_post(): 記事更新")
        print("   - get_post(): 記事取得")
        print("   - batch_update_posts(): 一括更新")
        print("   - restore_from_backup(): バックアップ復元")
        print("   - get_update_history(): 更新履歴取得")
        
        return client
        
    except Exception as e:
        print(f"❌ 初期化エラー: {str(e)}")
        return None

if __name__ == "__main__":
    main()