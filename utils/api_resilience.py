#!/usr/bin/env python3
"""
API通信の信頼性強化システム
サーキットブレーカー、指数バックオフ、リトライ機構を提供
"""

import time
import random
import logging
import functools
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime, timedelta
from enum import Enum
import requests
from dataclasses import dataclass

class CircuitState(Enum):
    """サーキットブレーカーの状態"""
    CLOSED = "closed"      # 正常
    OPEN = "open"          # 障害中
    HALF_OPEN = "half_open"  # 回復テスト中

@dataclass
class RetryConfig:
    """リトライ設定"""
    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True

@dataclass 
class CircuitBreakerConfig:
    """サーキットブレーカー設定"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    success_threshold: int = 3  # HALF_OPEN状態での成功回数

class APICircuitBreaker:
    """APIコール用サーキットブレーカー"""
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.logger = logging.getLogger(f"{__name__}.{name}")
    
    def can_execute(self) -> bool:
        """実行可能かチェック"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # 回復タイムアウトチェック
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.config.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.logger.info(f"Circuit breaker {self.name}: OPEN -> HALF_OPEN")
                return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return True
        
        return False
    
    def record_success(self):
        """成功記録"""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.config.success_threshold:
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.logger.info(f"Circuit breaker {self.name}: HALF_OPEN -> CLOSED (recovered)")
        elif self.state == CircuitState.CLOSED:
            self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """失敗記録"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.CLOSED and self.failure_count >= self.config.failure_threshold:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit breaker {self.name}: CLOSED -> OPEN (threshold exceeded)")
        elif self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self.logger.warning(f"Circuit breaker {self.name}: HALF_OPEN -> OPEN (recovery failed)")

class APIResilienceManager:
    """API通信の信頼性管理"""
    
    def __init__(self):
        self.circuit_breakers: Dict[str, APICircuitBreaker] = {}
        self.retry_configs: Dict[str, RetryConfig] = {}
        self.logger = logging.getLogger(__name__)
        
        # デフォルト設定
        self._setup_default_configs()
    
    def _setup_default_configs(self):
        """デフォルト設定セットアップ"""
        # OpenAI API用設定
        self.register_api("openai", 
                         CircuitBreakerConfig(failure_threshold=3, recovery_timeout=60),
                         RetryConfig(max_retries=3, base_delay=2.0, max_delay=120.0))
        
        # Google API用設定
        self.register_api("google", 
                         CircuitBreakerConfig(failure_threshold=3, recovery_timeout=45),
                         RetryConfig(max_retries=3, base_delay=1.5, max_delay=90.0))
        
        # WordPress API用設定
        self.register_api("wordpress",
                         CircuitBreakerConfig(failure_threshold=5, recovery_timeout=30),
                         RetryConfig(max_retries=5, base_delay=1.0, max_delay=60.0))
    
    def register_api(self, api_name: str, 
                    circuit_config: CircuitBreakerConfig,
                    retry_config: RetryConfig):
        """API設定登録"""
        self.circuit_breakers[api_name] = APICircuitBreaker(api_name, circuit_config)
        self.retry_configs[api_name] = retry_config
        self.logger.info(f"API registered: {api_name}")
    
    def with_resilience(self, api_name: str):
        """信頼性機能付きデコレータ"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                return self.execute_with_resilience(api_name, func, *args, **kwargs)
            return wrapper
        return decorator
    
    def execute_with_resilience(self, api_name: str, func: Callable, *args, **kwargs) -> Any:
        """信頼性機能付きで関数実行"""
        circuit_breaker = self.circuit_breakers.get(api_name)
        retry_config = self.retry_configs.get(api_name, RetryConfig())
        
        if not circuit_breaker:
            self.logger.warning(f"Unknown API: {api_name}, executing without circuit breaker")
            return self._execute_with_retry(func, retry_config, *args, **kwargs)
        
        # サーキットブレーカーチェック
        if not circuit_breaker.can_execute():
            raise APICircuitOpenError(f"Circuit breaker open for {api_name}")
        
        try:
            result = self._execute_with_retry(func, retry_config, *args, **kwargs)
            circuit_breaker.record_success()
            return result
        except Exception as e:
            circuit_breaker.record_failure()
            raise
    
    def _execute_with_retry(self, func: Callable, config: RetryConfig, *args, **kwargs) -> Any:
        """指数バックオフ付きリトライ実行"""
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                result = func(*args, **kwargs)
                if attempt > 0:
                    self.logger.info(f"Function succeeded on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                last_exception = e
                
                # 最終試行の場合はエラーを再発生
                if attempt == config.max_retries:
                    break
                
                # リトライ可能エラーかチェック
                if not self._is_retryable_error(e):
                    self.logger.info(f"Non-retryable error: {e}")
                    break
                
                # 指数バックオフ計算
                delay = min(
                    config.base_delay * (config.exponential_base ** attempt),
                    config.max_delay
                )
                
                # ジッター追加
                if config.jitter:
                    delay *= (0.5 + random.random() * 0.5)
                
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay:.2f}s")
                time.sleep(delay)
        
        # 全試行失敗
        self.logger.error(f"All {config.max_retries + 1} attempts failed")
        raise last_exception
    
    def _is_retryable_error(self, error: Exception) -> bool:
        """リトライ可能エラーかチェック"""
        if isinstance(error, requests.exceptions.RequestException):
            # ネットワーク関連エラーはリトライ可能
            if isinstance(error, (
                requests.exceptions.ConnectionError,
                requests.exceptions.Timeout,
                requests.exceptions.HTTPError
            )):
                # HTTPエラーの場合はステータスコードをチェック
                if hasattr(error, 'response') and error.response is not None:
                    status_code = error.response.status_code
                    # 4xx系エラー（クライアントエラー）は基本的にリトライしない
                    if 400 <= status_code < 500:
                        # ただし429(Rate Limit)と408(Timeout)はリトライ
                        return status_code in [408, 429]
                    # 5xx系エラー（サーバーエラー）はリトライ
                    return status_code >= 500
                return True
        
        # API固有のエラーチェック
        error_message = str(error).lower()
        retryable_patterns = [
            "rate limit",
            "timeout",
            "connection",
            "server error",
            "service unavailable",
            "too many requests"
        ]
        
        return any(pattern in error_message for pattern in retryable_patterns)
    
    def get_circuit_status(self) -> Dict[str, Dict[str, Any]]:
        """全サーキットブレーカー状態取得"""
        status = {}
        for name, breaker in self.circuit_breakers.items():
            status[name] = {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
                "last_failure": breaker.last_failure_time.isoformat() if breaker.last_failure_time else None
            }
        return status

class APICircuitOpenError(Exception):
    """サーキットブレーカーが開いている時のエラー"""
    pass

# グローバルインスタンス
resilience_manager = APIResilienceManager()

# 便利なデコレータ関数
def with_openai_resilience(func: Callable):
    """OpenAI API用信頼性デコレータ"""
    return resilience_manager.with_resilience("openai")(func)

def with_google_resilience(func: Callable):
    """Google API用信頼性デコレータ"""
    return resilience_manager.with_resilience("google")(func)

def with_wordpress_resilience(func: Callable):
    """WordPress API用信頼性デコレータ"""
    return resilience_manager.with_resilience("wordpress")(func)

# 使用例
if __name__ == "__main__":
    import requests
    
    # 使用例1: デコレータ使用
    @with_openai_resilience
    def call_openai_api():
        # OpenAI API呼び出し（模擬）
        response = requests.get("https://api.openai.com/v1/models", timeout=10)
        response.raise_for_status()
        return response.json()
    
    # 使用例2: 直接実行
    def call_wordpress_api():
        response = requests.post("https://example.com/wp-json/api", timeout=10)
        response.raise_for_status()
        return response.json()
    
    try:
        # API呼び出し
        result1 = call_openai_api()
        result2 = resilience_manager.execute_with_resilience("wordpress", call_wordpress_api)
        
        # 状態確認
        print("Circuit Breaker Status:")
        for api, status in resilience_manager.get_circuit_status().items():
            print(f"  {api}: {status}")
            
    except Exception as e:
        print(f"API call failed: {e}")