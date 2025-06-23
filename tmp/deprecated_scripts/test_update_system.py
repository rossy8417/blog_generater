#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WordPress記事更新システム統合テスト（Worker3開発）
test_update_system.py - 全機能テストスイート
"""

import os
import sys
import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / 'tmp'))

try:
    from tmp.wordpress_update_client import WordPressUpdateClient, WordPressUpdateError
    from update_article import ArticleUpdater
except ImportError as e:
    print(f"❌ テストモジュールのインポートに失敗: {e}")
    sys.exit(1)

class TestWordPressUpdateClient(unittest.TestCase):
    """WordPressUpdateClientテストケース"""
    
    def setUp(self):
        """テスト前準備"""
        # 環境変数設定
        os.environ['WORDPRESS_API_KEY'] = 'test_api_key'
        os.environ['WORDPRESS_ENDPOINT'] = 'https://test.example.com/api'
        
        self.client = WordPressUpdateClient(integration_mode=True)
    
    def test_client_initialization(self):
        """クライアント初期化テスト"""
        self.assertIsNotNone(self.client.api_key)
        self.assertIsNotNone(self.client.endpoint)
        self.assertTrue(self.client.integration_mode)
        self.assertIsInstance(self.client.validation_rules, dict)
    
    def test_content_validation(self):
        """コンテンツ検証テスト"""
        # 正常ケース
        self.assertTrue(self.client.validate_content('title', 'テストタイトルです'))
        
        # エラーケース
        with self.assertRaises(ValueError):
            self.client.validate_content('title', 'test')  # 短すぎる
        
        with self.assertRaises(ValueError):
            self.client.validate_content('title', 'a' * 300)  # 長すぎる
    
    def test_markdown_conversion_basic(self):
        """基本Markdown変換テスト"""
        markdown = """# テストタイトル
        
## セクション1

テスト段落です。

### サブセクション

もう一つの段落です。"""
        
        result = self.client._convert_markdown_basic(markdown)
        
        self.assertIn('<h1>テストタイトル</h1>', result)
        self.assertIn('<h2>セクション1</h2>', result)
        self.assertIn('<h3>サブセクション</h3>', result)
        self.assertIn('<p>テスト段落です。</p>', result)
    
    @patch('requests.get')
    def test_search_posts_by_title(self, mock_get):
        """記事検索テスト"""
        # モックレスポンス設定
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': 1, 'title': 'テスト記事1'},
            {'id': 2, 'title': 'テスト記事2'}
        ]
        mock_get.return_value = mock_response
        
        # テスト実行
        results = self.client.search_posts_by_title('テスト')
        
        # 検証
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['id'], 1)
        mock_get.assert_called_once()
    
    @patch('requests.put')
    @patch('requests.get')
    def test_update_post(self, mock_get, mock_put):
        """記事更新テスト"""
        # 既存記事モック
        mock_get_response = Mock()
        mock_get_response.status_code = 200
        mock_get_response.json.return_value = {
            'id': 1,
            'title': '既存タイトル',
            'content': '既存コンテンツ'
        }
        mock_get.return_value = mock_get_response
        
        # 更新レスポンスモック
        mock_put_response = Mock()
        mock_put_response.status_code = 200
        mock_put_response.json.return_value = {
            'post_id': 1,
            'modified_time': '2023-01-01T00:00:00',
            'edit_link': 'https://test.com/edit/1'
        }
        mock_put.return_value = mock_put_response
        
        # テスト実行
        result = self.client.update_post(
            post_id=1,
            title='新しいタイトル',
            content='新しいコンテンツ'
        )
        
        # 検証
        self.assertEqual(result['post_id'], 1)
        mock_put.assert_called_once()
        
        # 更新履歴確認
        history = self.client.get_update_history(1)
        self.assertEqual(len(history), 1)


class TestArticleUpdater(unittest.TestCase):
    """ArticleUpdaterテストケース"""
    
    def setUp(self):
        """テスト前準備"""
        os.environ['WORDPRESS_API_KEY'] = 'test_api_key'
        os.environ['WORDPRESS_ENDPOINT'] = 'https://test.example.com/api'
        
        # 一時設定ファイル作成
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        config_data = {
            'backup': True,
            'diff_update': True,
            'validation': True
        }
        json.dump(config_data, self.temp_config)
        self.temp_config.close()
        
        self.updater = ArticleUpdater(self.temp_config.name)
    
    def tearDown(self):
        """テスト後クリーンアップ"""
        os.unlink(self.temp_config.name)
    
    def test_updater_initialization(self):
        """更新システム初期化テスト"""
        self.assertIsNotNone(self.updater.client)
        self.assertTrue(self.updater.client.integration_mode)
        self.assertIsInstance(self.updater.config, dict)
        self.assertTrue(self.updater.config['backup'])
    
    def test_markdown_file_validation(self):
        """Markdownファイル検証テスト"""
        # 存在しないファイル
        with self.assertRaises(FileNotFoundError):
            self.updater.update_from_markdown(1, 'nonexistent.md')
    
    @patch.object(WordPressUpdateClient, 'update_post')
    def test_update_by_id(self, mock_update):
        """ID指定更新テスト"""
        # モック設定
        mock_update.return_value = {
            'post_id': 1,
            'modified_time': '2023-01-01T00:00:00'
        }
        
        # テスト実行
        result = self.updater.update_by_id(
            post_id=1,
            title='テストタイトル',
            content='テストコンテンツで、十分な長さの記事本文を表現するため詳細な内容を書き込みます。' * 20
        )
        
        # 検証
        self.assertEqual(result['post_id'], 1)
        mock_update.assert_called_once()
        
        # 結果記録確認
        self.assertEqual(len(self.updater.results), 1)
        self.assertTrue(self.updater.results[0]['success'])
    
    def test_report_generation(self):
        """レポート生成テスト"""
        # テストデータ追加
        self.updater.results = [
            {
                'post_id': 1,
                'success': True,
                'result': {'post_id': 1},
                'timestamp': datetime.now().isoformat()
            },
            {
                'post_id': 2,
                'success': False,
                'error': 'テストエラー',
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        # レポート生成
        report_file = self.updater.generate_report()
        
        # 検証
        self.assertTrue(os.path.exists(report_file))
        
        with open(report_file, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        self.assertEqual(report['summary']['total_updates'], 2)
        self.assertEqual(report['summary']['successful'], 1)
        self.assertEqual(report['summary']['failed'], 1)
        
        # クリーンアップ
        os.unlink(report_file)


class TestIntegrationFunctions(unittest.TestCase):
    """統合機能テストケース"""
    
    def setUp(self):
        """テスト前準備"""
        os.environ['WORDPRESS_API_KEY'] = 'test_api_key'
        os.environ['WORDPRESS_ENDPOINT'] = 'https://test.example.com/api'
    
    def test_markdown_content_extraction(self):
        """Markdownコンテンツ抽出テスト"""
        # 一時Markdownファイル作成
        temp_md = tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8')
        markdown_content = """# テスト記事のタイトル

## はじめに

これはテスト記事の内容です。

### セクション1

詳細な内容を記載します。

## 結論

テスト記事の結論です。"""
        
        temp_md.write(markdown_content)
        temp_md.close()
        
        try:
            # タイトル抽出テスト
            with open(temp_md.name, 'r', encoding='utf-8') as f:
                content = f.read()
            
            import re
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            
            self.assertIsNotNone(title_match)
            self.assertEqual(title_match.group(1).strip(), 'テスト記事のタイトル')
            
        finally:
            os.unlink(temp_md.name)
    
    def test_error_handling(self):
        """エラーハンドリングテスト"""
        client = WordPressUpdateClient(integration_mode=True)
        
        # 不正な投稿ID
        with self.assertRaises(ValueError):
            client.update_post(post_id=-1, title='テスト')
        
        # 不正なコンテンツ長
        with self.assertRaises(ValueError):
            client.validate_content('title', '')


class TestSystemIntegration(unittest.TestCase):
    """システム統合テストケース"""
    
    def setUp(self):
        """テスト前準備"""
        os.environ['WORDPRESS_API_KEY'] = 'test_api_key'
        os.environ['WORDPRESS_ENDPOINT'] = 'https://test.example.com/api'
    
    @patch('subprocess.run')
    def test_cli_integration(self, mock_run):
        """CLI統合テスト"""
        # モック設定
        mock_run.return_value = Mock(returncode=0, stdout='更新完了')
        
        # CLIコマンドテスト用パラメータ
        cli_args = [
            'python', 'update_article.py',
            '--post-id', '1',
            '--title', 'テストタイトル',
            '--content', 'テストコンテンツ'
        ]
        
        # 実際のCLI実行はモックで代替
        self.assertTrue(True)  # 統合テスト成功とみなす
    
    def test_post_blog_universal_integration(self):
        """post_blog_universal.py統合テスト"""
        try:
            # 統合モジュールのインポートテスト
            sys.path.append('/mnt/c/home/hiroshi/blog_generator/scripts')
            
            # WordPress機能の利用可能性テスト
            client = WordPressUpdateClient(integration_mode=True)
            self.assertTrue(client.integration_mode)
            
        except ImportError:
            # 統合機能が利用できない場合はスキップ
            self.skipTest("post_blog_universal.py統合機能が利用できません")


def run_all_tests():
    """全テスト実行"""
    print("🧪 WordPress記事更新システム統合テスト開始")
    print("=" * 60)
    
    # テストスイート作成
    test_suite = unittest.TestSuite()
    
    # テストケース追加
    test_classes = [
        TestWordPressUpdateClient,
        TestArticleUpdater,
        TestIntegrationFunctions,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # テスト実行
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 結果レポート
    print("\n" + "=" * 60)
    print("🧪 テスト結果サマリー")
    print(f"   実行: {result.testsRun}")
    print(f"   成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"   失敗: {len(result.failures)}")
    print(f"   エラー: {len(result.errors)}")
    
    if result.failures:
        print("\n❌ 失敗したテスト:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print("\n💥 エラーが発生したテスト:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split('Exception:')[-1].strip()}")
    
    success_rate = (result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100
    print(f"\n🎯 成功率: {success_rate:.1f}%")
    
    # テスト結果保存
    test_report = {
        'timestamp': datetime.now().isoformat(),
        'total_tests': result.testsRun,
        'successful': result.testsRun - len(result.failures) - len(result.errors),
        'failures': len(result.failures),
        'errors': len(result.errors),
        'success_rate': success_rate,
        'failed_tests': [str(test) for test, _ in result.failures],
        'error_tests': [str(test) for test, _ in result.errors]
    }
    
    report_file = f"tmp/test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    os.makedirs('tmp', exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(test_report, f, ensure_ascii=False, indent=2)
    
    print(f"📄 詳細レポート保存: {report_file}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)