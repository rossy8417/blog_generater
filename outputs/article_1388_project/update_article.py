#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress記事更新統合スクリプト（Worker3開発）
update_article.py - CLI対応の統合更新システム
"""

import os
import sys
import argparse
import json
import glob
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'tmp'))

try:
    from tmp.wordpress_update_client import WordPressUpdateClient
    from scripts.post_blog_universal import find_latest_article_files
except ImportError as e:
    print(f"❌ 必要なモジュールのインポートに失敗: {e}")
    sys.exit(1)

class ArticleUpdater:
    """統合記事更新システム（Worker3開発）"""
    
    def __init__(self, config_file: str = None):
        """
        初期化
        
        Args:
            config_file: 設定ファイルパス
        """
        self.config = self._load_config(config_file)
        self.client = WordPressUpdateClient(integration_mode=True)
        self.results = []
        
        print("🚀 WordPress記事更新統合システム初期化完了")
        print(f"   設定ファイル: {config_file or 'デフォルト'}")
        print(f"   統合モード: 有効")
    
    def update_by_id(self, post_id: int, **kwargs) -> Dict[str, Any]:
        """
        投稿IDによる記事更新
        
        Args:
            post_id: 更新対象の投稿ID
            **kwargs: 更新パラメータ
        """
        print(f"\n📝 記事更新開始: ID {post_id}")
        
        try:
            # バリデーション
            if kwargs.get('title'):
                self.client.validate_content('title', kwargs['title'])
            if kwargs.get('content'):
                self.client.validate_content('content', kwargs['content'])
            if kwargs.get('excerpt'):
                self.client.validate_content('excerpt', kwargs['excerpt'])
            
            # 更新実行
            result = self.client.update_post(post_id, **kwargs)
            
            self.results.append({
                'post_id': post_id,
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ 記事更新成功: {result.get('post_id', post_id)}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ 記事更新失敗: {error_msg}")
            
            self.results.append({
                'post_id': post_id,
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
            
            raise
    
    def update_from_markdown(self, post_id: int, markdown_file: str, 
                           image_dir: str = None, **kwargs) -> Dict[str, Any]:
        """
        Markdownファイルからの記事更新
        
        Args:
            post_id: 更新対象の投稿ID
            markdown_file: Markdownファイルパス
            image_dir: 画像ディレクトリパス
            **kwargs: 追加更新パラメータ
        """
        print(f"\n📖 Markdownファイルから更新: {markdown_file}")
        
        if not os.path.exists(markdown_file):
            raise FileNotFoundError(f"Markdownファイルが見つかりません: {markdown_file}")
        
        try:
            result = self.client.update_post_from_markdown(
                post_id=post_id,
                markdown_file=markdown_file,
                image_dir=image_dir,
                **kwargs
            )
            
            self.results.append({
                'post_id': post_id,
                'source': 'markdown',
                'file': markdown_file,
                'success': True,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            print(f"✅ Markdown更新成功: {result.get('post_id', post_id)}")
            return result
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Markdown更新失敗: {error_msg}")
            
            self.results.append({
                'post_id': post_id,
                'source': 'markdown',
                'file': markdown_file,
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
            
            raise
    
    def update_latest_article(self, post_id: int, outputs_dir: str = None) -> Dict[str, Any]:
        """
        最新記事ファイルからの更新（post_blog_universal.py連携）
        
        Args:
            post_id: 更新対象の投稿ID
            outputs_dir: 出力ディレクトリ
        """
        print(f"\n🔍 最新記事ファイルから更新開始")
        
        if not outputs_dir:
            outputs_dir = os.path.join(project_root, 'outputs')
        
        # 最新記事ファイル検索
        try:
            article_file, thumbnail_files, eyecatch_file = find_latest_article_files(outputs_dir)
            
            if not article_file:
                raise FileNotFoundError("最新記事ファイルが見つかりません")
            
            image_dir = os.path.dirname(article_file)
            
            print(f"📄 記事ファイル: {os.path.basename(article_file)}")
            print(f"📁 画像ディレクトリ: {image_dir}")
            
            # Markdown更新実行
            return self.update_from_markdown(
                post_id=post_id,
                markdown_file=article_file,
                image_dir=image_dir
            )
            
        except Exception as e:
            error_msg = f"最新記事更新失敗: {str(e)}"
            print(f"❌ {error_msg}")
            
            self.results.append({
                'post_id': post_id,
                'source': 'latest_article',
                'success': False,
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            })
            
            raise
    
    def search_and_update(self, title: str, **kwargs) -> List[Dict[str, Any]]:
        """
        タイトル検索による記事更新
        
        Args:
            title: 検索タイトル
            **kwargs: 更新パラメータ
        """
        print(f"\n🔍 タイトル検索更新: {title}")
        
        # 記事検索
        posts = self.client.search_posts_by_title(title)
        
        if not posts:
            print(f"❌ タイトル '{title}' の記事が見つかりません")
            return []
        
        print(f"📝 {len(posts)}件の記事が見つかりました")
        
        results = []
        for post in posts:
            post_id = post.get('id')
            post_title = post.get('title', 'Unknown')
            
            try:
                print(f"\n更新中: {post_title} (ID: {post_id})")
                result = self.update_by_id(post_id, **kwargs)
                results.append(result)
                
            except Exception as e:
                print(f"❌ 記事ID {post_id} 更新失敗: {str(e)}")
                continue
        
        return results
    
    def batch_update(self, updates: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        バッチ更新（統合版）
        
        Args:
            updates: 更新設定リスト
        """
        print(f"\n🔄 バッチ更新開始: {len(updates)}件")
        
        results = []
        for i, update_config in enumerate(updates, 1):
            print(f"\n[{i}/{len(updates)}] バッチ更新中...")
            
            try:
                if 'markdown_file' in update_config:
                    # Markdown更新
                    result = self.update_from_markdown(**update_config)
                else:
                    # 通常更新
                    result = self.update_by_id(**update_config)
                
                results.append(result)
                
            except Exception as e:
                print(f"❌ バッチ項目 {i} 更新失敗: {str(e)}")
                continue
        
        success_count = len(results)
        print(f"\n🎉 バッチ更新完了: {success_count}/{len(updates)} 件成功")
        
        return results
    
    def get_analytics(self, post_id: int) -> Dict[str, Any]:
        """
        記事分析データ取得
        
        Args:
            post_id: 記事ID
        """
        print(f"\n📊 記事分析データ取得: ID {post_id}")
        
        analytics = self.client.get_post_analytics(post_id)
        
        if analytics:
            print(f"✅ 分析データ取得完了")
            print(f"   PV: {analytics.get('page_views', 'N/A')}")
            print(f"   シェア数: {analytics.get('shares', 'N/A')}")
            print(f"   滞在時間: {analytics.get('avg_time', 'N/A')}")
        else:
            print(f"⚠️  分析データが取得できませんでした")
        
        return analytics
    
    def generate_report(self, output_file: str = None) -> str:
        """
        更新結果レポート生成
        
        Args:
            output_file: 出力ファイルパス
        """
        if not output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = f"tmp/update_report_{timestamp}.json"
        
        report = {
            'summary': {
                'total_updates': len(self.results),
                'successful': sum(1 for r in self.results if r.get('success')),
                'failed': sum(1 for r in self.results if not r.get('success')),
                'generated_at': datetime.now().isoformat()
            },
            'results': self.results,
            'config': self.config
        }
        
        # レポート保存
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"📄 更新レポート生成: {output_file}")
        print(f"   成功: {report['summary']['successful']} 件")
        print(f"   失敗: {report['summary']['failed']} 件")
        
        return output_file
    
    def _load_config(self, config_file: str = None) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        default_config = {
            'backup': True,
            'diff_update': True,
            'validation': True,
            'max_retries': 3,
            'timeout': 30
        }
        
        if not config_file or not os.path.exists(config_file):
            return default_config
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
            
            # デフォルト設定と統合
            config = {**default_config, **user_config}
            print(f"📋 設定ファイル読み込み完了: {config_file}")
            return config
            
        except Exception as e:
            print(f"⚠️  設定ファイル読み込み失敗、デフォルト設定を使用: {e}")
            return default_config


def main():
    """メイン実行関数"""
    parser = argparse.ArgumentParser(description='WordPress記事更新統合システム')
    
    # 基本オプション
    parser.add_argument('--post-id', type=int, help='更新対象の投稿ID')
    parser.add_argument('--title', help='新しいタイトル')
    parser.add_argument('--content', help='新しいコンテンツ')
    parser.add_argument('--excerpt', help='新しい抜粋')
    parser.add_argument('--status', help='投稿ステータス')
    
    # ファイル指定オプション
    parser.add_argument('--markdown', help='Markdownファイルパス')
    parser.add_argument('--image-dir', help='画像ディレクトリパス')
    parser.add_argument('--config', help='設定ファイルパス')
    
    # 特殊モード
    parser.add_argument('--latest', action='store_true', help='最新記事ファイルから更新')
    parser.add_argument('--search-title', help='タイトル検索による更新')
    parser.add_argument('--batch', help='バッチ更新設定ファイル')
    parser.add_argument('--analytics', action='store_true', help='分析データ取得')
    
    # 出力オプション
    parser.add_argument('--outputs-dir', default='outputs', help='出力ディレクトリ')
    parser.add_argument('--report', help='レポート出力ファイル')
    
    args = parser.parse_args()
    
    # バリデーション
    if not args.post_id and not args.search_title and not args.batch:
        print("❌ --post-id, --search-title, または --batch のいずれかを指定してください")
        return 1
    
    try:
        # 更新システム初期化
        updater = ArticleUpdater(args.config)
        
        # 実行モード判定
        if args.batch:
            # バッチ更新
            if not os.path.exists(args.batch):
                print(f"❌ バッチ設定ファイルが見つかりません: {args.batch}")
                return 1
            
            with open(args.batch, 'r', encoding='utf-8') as f:
                batch_config = json.load(f)
            
            updater.batch_update(batch_config)
            
        elif args.search_title:
            # タイトル検索更新
            update_params = {}
            if args.title: update_params['title'] = args.title
            if args.content: update_params['content'] = args.content
            if args.excerpt: update_params['excerpt'] = args.excerpt
            if args.status: update_params['status'] = args.status
            
            updater.search_and_update(args.search_title, **update_params)
            
        else:
            # 単一記事更新
            if args.latest:
                # 最新記事更新
                updater.update_latest_article(args.post_id, args.outputs_dir)
                
            elif args.markdown:
                # Markdown更新
                update_params = {}
                if args.title: update_params['title'] = args.title
                if args.excerpt: update_params['excerpt'] = args.excerpt
                if args.status: update_params['status'] = args.status
                
                updater.update_from_markdown(
                    args.post_id, 
                    args.markdown, 
                    args.image_dir,
                    **update_params
                )
                
            else:
                # 通常更新
                update_params = {}
                if args.title: update_params['title'] = args.title
                if args.content: update_params['content'] = args.content
                if args.excerpt: update_params['excerpt'] = args.excerpt
                if args.status: update_params['status'] = args.status
                
                if not update_params:
                    print("❌ 更新するデータを指定してください")
                    return 1
                
                updater.update_by_id(args.post_id, **update_params)
            
            # 分析データ取得
            if args.analytics:
                updater.get_analytics(args.post_id)
        
        # レポート生成
        updater.generate_report(args.report)
        
        print("\n🎉 更新処理完了!")
        return 0
        
    except Exception as e:
        print(f"\n❌ 更新処理失敗: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())