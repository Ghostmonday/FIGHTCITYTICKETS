"""
Tests for citation service caching and error handling.
"""
import json
import logging
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add parent directory to path to import src
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.citation import (
    _CITATION_CACHE,
    REDIS_CACHE_TTL,
    _get_cached_citation,
    _get_redis_client,
    _set_cached_citation,
)

class TestCitationCaching(unittest.TestCase):
    """Test Redis caching and error handling in citation service."""

    def setUp(self):
        """Reset state before each test."""
        # Clear in-memory cache
        _CITATION_CACHE.clear()

    def test_get_redis_client_no_redis_module(self):
        """Test _get_redis_client returns None when redis module is missing."""
        # We need to simulate ImportError when 'import redis' is called.
        # We patch builtins.__import__ to raise ImportError for 'redis'.

        original_import = __import__

        def import_mock(name, *args, **kwargs):
            if name == 'redis':
                raise ImportError("No module named 'redis'")
            return original_import(name, *args, **kwargs)

        # We also need to remove 'redis' from sys.modules if it's there
        # to force a new import attempt.
        with patch.dict(sys.modules):
            if 'redis' in sys.modules:
                del sys.modules['redis']

            with patch('builtins.__import__', side_effect=import_mock):
                client = _get_redis_client()
                self.assertIsNone(client)

    def test_get_redis_client_no_url(self):
        """Test _get_redis_client returns None when REDIS_URL is not set."""
        # Mock redis module to be importable
        mock_redis = MagicMock()

        with patch.dict(sys.modules, {'redis': mock_redis}):
            # Patch REDIS_URL in the module to be empty
            with patch('src.services.citation.REDIS_URL', ''):
                client = _get_redis_client()
                self.assertIsNone(client)

    def test_get_redis_client_success(self):
        """Test _get_redis_client returns client when configured correctly."""
        mock_redis = MagicMock()
        mock_redis_client = MagicMock()
        mock_redis.Redis.from_url.return_value = mock_redis_client

        with patch.dict(sys.modules, {'redis': mock_redis}):
            with patch('src.services.citation.REDIS_URL', 'redis://localhost:6379'):
                client = _get_redis_client()
                self.assertIsNotNone(client)
                mock_redis.Redis.from_url.assert_called_with('redis://localhost:6379', decode_responses=True)
                self.assertEqual(client, mock_redis_client)

    def test_get_cached_citation_redis_hit(self):
        """Test cache hit from Redis."""
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.from_url.return_value = mock_client

        citation_number = "123"
        cached_data = {"citation_number": "123", "is_valid": True}
        mock_client.get.return_value = json.dumps(cached_data)

        with patch.dict(sys.modules, {'redis': mock_redis}):
            with patch('src.services.citation.REDIS_URL', 'redis://localhost:6379'):
                result = _get_cached_citation(citation_number)

                self.assertEqual(result, cached_data)
                mock_client.get.assert_called_with(f"citation:{citation_number}")

    def test_get_cached_citation_redis_miss_memory_hit(self):
        """Test Redis miss but memory cache hit."""
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.from_url.return_value = mock_client

        citation_number = "123"
        mock_client.get.return_value = None  # Redis miss

        # Populate memory cache
        import time
        cached_data = {"citation_number": "123", "is_valid": True}
        _CITATION_CACHE[f"citation:{citation_number}"] = (cached_data, time.time())

        with patch.dict(sys.modules, {'redis': mock_redis}):
            with patch('src.services.citation.REDIS_URL', 'redis://localhost:6379'):
                result = _get_cached_citation(citation_number)

                self.assertEqual(result, cached_data)
                mock_client.get.assert_called_with(f"citation:{citation_number}")

    def test_get_cached_citation_redis_error(self):
        """Test Redis error handled gracefully (logs warning)."""
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.from_url.return_value = mock_client

        citation_number = "123"
        mock_client.get.side_effect = Exception("Connection refused")

        with patch.dict(sys.modules, {'redis': mock_redis}):
            with patch('src.services.citation.REDIS_URL', 'redis://localhost:6379'):
                # Patch logger to verify warning
                with patch('src.services.citation.logger') as mock_logger:
                    result = _get_cached_citation(citation_number)

                    self.assertIsNone(result)
                    mock_logger.warning.assert_called()
                    args, _ = mock_logger.warning.call_args
                    self.assertIn("Redis cache lookup failed", args[0])

    def test_set_cached_citation_redis_success(self):
        """Test caching to Redis success."""
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.from_url.return_value = mock_client

        citation_number = "123"
        citation_data = {"citation_number": "123", "is_valid": True}

        with patch.dict(sys.modules, {'redis': mock_redis}):
            with patch('src.services.citation.REDIS_URL', 'redis://localhost:6379'):
                _set_cached_citation(citation_number, citation_data)

                mock_client.setex.assert_called_with(
                    f"citation:{citation_number}",
                    REDIS_CACHE_TTL,
                    json.dumps(citation_data)
                )

    def test_set_cached_citation_redis_error_fallback(self):
        """Test Redis error during set handled gracefully (fallback to memory)."""
        mock_redis = MagicMock()
        mock_client = MagicMock()
        mock_redis.Redis.from_url.return_value = mock_client

        citation_number = "123"
        citation_data = {"citation_number": "123", "is_valid": True}
        mock_client.setex.side_effect = Exception("Connection refused")

        with patch.dict(sys.modules, {'redis': mock_redis}):
            with patch('src.services.citation.REDIS_URL', 'redis://localhost:6379'):
                with patch('src.services.citation.logger') as mock_logger:
                    _set_cached_citation(citation_number, citation_data)

                    mock_logger.warning.assert_called()
                    args, _ = mock_logger.warning.call_args
                    self.assertIn("Redis cache set failed", args[0])

                    # Verify fallback to memory cache
                    cache_key = f"citation:{citation_number}"
                    self.assertIn(cache_key, _CITATION_CACHE)
                    self.assertEqual(_CITATION_CACHE[cache_key][0], citation_data)

if __name__ == "__main__":
    unittest.main()
