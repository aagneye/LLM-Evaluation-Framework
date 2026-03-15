import pytest
from unittest.mock import Mock, patch
from app.core.cache import CacheManager


@pytest.fixture
def mock_redis():
    """Mock Redis client."""
    with patch('app.core.cache.Redis') as mock:
        redis_instance = Mock()
        mock.from_url.return_value = redis_instance
        yield redis_instance


def test_cache_set_get(mock_redis):
    """Test setting and getting cache values."""
    cache = CacheManager(mock_redis)
    
    mock_redis.get.return_value = '{"test": "value"}'
    
    result = cache.get("test_key")
    
    assert result == {"test": "value"}
    mock_redis.get.assert_called_once_with("test_key")


def test_cache_miss(mock_redis):
    """Test cache miss."""
    cache = CacheManager(mock_redis)
    
    mock_redis.get.return_value = None
    
    result = cache.get("nonexistent_key")
    
    assert result is None


def test_model_response_caching(mock_redis):
    """Test model response caching."""
    cache = CacheManager(mock_redis)
    
    response_data = {
        "text": "Test response",
        "latency": 0.5,
        "success": True
    }
    
    cache.set_model_response("gpt-4", "test prompt", response_data)
    
    mock_redis.setex.assert_called_once()


def test_cache_health_check(mock_redis):
    """Test cache health check."""
    cache = CacheManager(mock_redis)
    
    mock_redis.ping.return_value = True
    
    assert cache.health_check() is True
    
    mock_redis.ping.side_effect = Exception("Connection failed")
    
    assert cache.health_check() is False
