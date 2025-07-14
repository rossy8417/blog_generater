#\!/usr/bin/env python3
"""
設定一元管理システム
ハードコーディングされた設定値を環境変数から動的に生成
"""

import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

class ConfigManager:
    """設定の一元管理"""
    
    def __init__(self, env_path: str = ".env"):
        load_dotenv(env_path)
        self._validate_required_vars()
    
    def _validate_required_vars(self):
        """必須環境変数のチェック"""
        required_vars = ['WORDPRESS_API_KEY', 'WORDPRESS_ENDPOINT']
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var) or os.getenv(var).startswith('your_'):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"必須環境変数が未設定です: {', '.join(missing_vars)}")
    
    def get_wordpress_config(self) -> Dict[str, Any]:
        """WordPress設定を環境変数から動的生成"""
        endpoint = os.getenv('WORDPRESS_ENDPOINT')
        base_url = os.getenv('WORDPRESS_BASE_URL')
        
        if not base_url and endpoint:
            base_url = endpoint.split('/wp-json')[0]
        
        wp_api_base = os.getenv('WORDPRESS_WP_API_BASE') or f"{base_url}/wp-json/wp/v2"
        
        return {
            "wordpress_settings": {
                "endpoint_base": endpoint,
                "timeout": int(os.getenv('API_TIMEOUT', '30')),
                "retry_attempts": int(os.getenv('API_RETRY_ATTEMPTS', '3')),
                "retry_delay": int(os.getenv('API_RETRY_DELAY', '2'))
            },
            "update_strategies": {
                "proven_method": {
                    "endpoint": "/update-post/{post_id}",
                    "method": "POST",
                    "backup_required": True,
                    "verify_endpoint": f"{wp_api_base}/posts/{{post_id}}"
                }
            }
        }

def get_wordpress_config() -> Dict[str, Any]:
    """WordPress設定取得（便利関数）"""
    config_manager = ConfigManager()
    return config_manager.get_wordpress_config()

if __name__ == "__main__":
    try:
        config = get_wordpress_config()
        print("✅ WordPress設定生成成功")
        print(f"エンドポイント: {config['wordpress_settings']['endpoint_base']}")
    except Exception as e:
        print(f"❌ エラー: {e}")
EOF < /dev/null
