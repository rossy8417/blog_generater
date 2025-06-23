#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
汎用記事更新マネージャー
再現性と汎用性を重視した記事更新システム
"""

import os
import sys
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 環境変数読み込み
load_dotenv()

class ArticleUpdateManager:
    """汎用記事更新マネージャー"""
    
    def __init__(self, config_path: Optional[str] = None):
        """初期化"""
        self.project_root = Path(__file__).parent.parent
        self.config_path = config_path or self.project_root / "config" / "article_update_config.json"
        self.config = self._load_config()
        self.setup_directories()
        self.setup_logging()
        
        # WordPress認証設定
        self.api_key = os.getenv('WORDPRESS_API_KEY')
        if not self.api_key:
            raise ValueError("WORDPRESS_API_KEY が .env ファイルに設定されていません")
            
        self.headers = {
            'Content-Type': 'application/json',
            self.config['security']['auth_header']: self.api_key
        }
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"設定ファイルが見つかりません: {self.config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"設定ファイルの形式が不正です: {e}")
    
    def setup_directories(self):
        """必要ディレクトリの作成"""
        dirs = [
            self.config['file_management']['output_directory'],
            self.config['file_management']['backup_directory'], 
            self.config['file_management']['temp_directory'],
            self.config['file_management']['log_directory']
        ]
        
        for dir_path in dirs:
            full_path = self.project_root / dir_path
            full_path.mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """ログ設定"""
        log_dir = self.project_root / self.config['file_management']['log_directory']
        log_file = log_dir / f"article_update_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def update_article(self, 
                      post_id: int,
                      content_file: str,
                      strategy: str = "proven_method") -> Dict[str, Any]:
        """
        記事更新メイン処理
        
        Args:
            post_id: 更新対象記事ID
            content_file: コンテンツファイルパス（プロジェクトルートからの相対パス）
            strategy: 更新戦略 (new_post, direct_update, proven_method)
        
        Returns:
            更新結果辞書
        """
        self.logger.info(f"🚀 記事更新開始: ID {post_id}, 戦略: {strategy}")
        
        try:
            # 1. コンテンツファイル読み込み
            content = self._load_content_file(content_file)
            
            # 2. 更新実行
            update_result = self._execute_update(post_id, content, strategy)
            
            # 3. 結果レポート作成
            final_result = self._create_update_report(post_id, strategy, update_result)
            
            self.logger.info(f"✅ 記事更新完了: ID {post_id}")
            return final_result
            
        except Exception as e:
            error_msg = f"記事更新失敗: {str(e)}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "post_id": post_id,
                "strategy": strategy,
                "timestamp": datetime.now().isoformat()
            }
    
    def _load_content_file(self, content_file: str) -> str:
        """コンテンツファイル読み込み"""
        file_path = self.project_root / content_file
        
        if not file_path.exists():
            raise FileNotFoundError(f"コンテンツファイルが見つかりません: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        self.logger.info(f"📖 コンテンツ読み込み完了: {len(content)}文字")
        return content
    
    def _execute_update(self, post_id: int, content: str, strategy: str) -> Dict[str, Any]:
        """更新実行"""
        strategy_config = self.config['update_strategies'][strategy]
        endpoint = self.config['wordpress_settings']['endpoint_base'] + strategy_config['endpoint'].format(post_id=post_id)
        method = strategy_config['method']
        
        # 更新データ構築
        update_data = {
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info(f"✏️  更新実行: {method} {endpoint}")
        
        # API呼び出し
        try:
            response = requests.post(endpoint, headers=self.headers, json=update_data, 
                                   timeout=self.config['wordpress_settings']['timeout'])
            
            self.logger.info(f"📡 API レスポンス: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json() if response.content else {}
                result['api_status_code'] = response.status_code
                return result
            else:
                raise requests.exceptions.HTTPError(f"HTTP {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API呼び出し失敗: {str(e)}")
    
    def _create_update_report(self, post_id: int, strategy: str, update_result: Dict[str, Any]) -> Dict[str, Any]:
        """更新結果レポート作成"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        report = {
            "post_id": post_id,
            "strategy": strategy,
            "timestamp": timestamp,
            "success": update_result.get('success', True),
            "update_result": update_result
        }
        
        # レポートファイル保存
        report_filename = f"update_report_{post_id}_{timestamp}.json"
        report_path = self.project_root / self.config['file_management']['output_directory'] / report_filename
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        report['report_file'] = str(report_path)
        return report


def main():
    """コマンドライン実行用メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='汎用記事更新マネージャー')
    parser.add_argument('post_id', type=int, help='更新対象記事ID')
    parser.add_argument('content_file', help='コンテンツファイルパス')
    parser.add_argument('--strategy', default='proven_method', help='更新戦略')
    
    args = parser.parse_args()
    
    try:
        manager = ArticleUpdateManager()
        
        result = manager.update_article(
            post_id=args.post_id,
            content_file=args.content_file,
            strategy=args.strategy
        )
        
        if result['success']:
            print(f"✅ 記事更新成功: ID {args.post_id}")
            return 0
        else:
            print(f"❌ 記事更新失敗: {result.get('error')}")
            return 1
            
    except Exception as e:
        print(f"❌ エラー: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())