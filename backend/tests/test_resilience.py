import asyncio
import pytest
import time
from unittest.mock import Mock, patch, AsyncMock
from src.middleware.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitOpenError,
)

@pytest.fixture
def circuit_breaker():
    """Create a circuit breaker for testing."""
    config = CircuitBreakerConfig(
        failure_threshold=2,
        success_threshold=2,
        timeout_seconds=60,
    )
    # Use a unique name for each test to avoid singleton collision
    return CircuitBreaker(f"test_circuit_{time.time()}", config=config)

@pytest.mark.asyncio
async def test_circuit_breaker_initial_state(circuit_breaker):
    """Test initial state of circuit breaker."""
    assert circuit_breaker.metrics.state == CircuitState.CLOSED
    assert circuit_breaker.metrics.failure_count == 0
    assert circuit_breaker.metrics.success_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_success(circuit_breaker):
    """Test successful execution."""
    async def success_func():
        return "success"

    result = await circuit_breaker.call(success_func)
    assert result == "success"
    assert circuit_breaker.metrics.total_calls == 1
    assert circuit_breaker.metrics.total_successes == 1
    assert circuit_breaker.metrics.state == CircuitState.CLOSED

@pytest.mark.asyncio
async def test_circuit_breaker_failure_counts(circuit_breaker):
    """Test that failures are counted correctly."""
    async def failing_func():
        raise ValueError("error")

    # First failure
    with pytest.raises(ValueError):
        await circuit_breaker.call(failing_func)

    assert circuit_breaker.metrics.failure_count == 1
    assert circuit_breaker.metrics.state == CircuitState.CLOSED

    # Second failure (threshold reached)
    with pytest.raises(ValueError):
        await circuit_breaker.call(failing_func)

    assert circuit_breaker.metrics.failure_count == 2
    assert circuit_breaker.metrics.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_circuit_breaker_open_state(circuit_breaker):
    """Test that open circuit rejects requests."""
    # Force open state
    circuit_breaker.metrics.state = CircuitState.OPEN
    circuit_breaker.metrics.last_failure_time = time.time()

    async def success_func():
        return "success"

    # Should raise CircuitOpenError immediately
    with pytest.raises(CircuitOpenError):
        await circuit_breaker.call(success_func)

@pytest.mark.asyncio
async def test_circuit_breaker_timeout_recovery(circuit_breaker):
    """Test recovery from OPEN to HALF_OPEN after timeout."""
    # Set to OPEN state with old failure time
    circuit_breaker.metrics.state = CircuitState.OPEN
    circuit_breaker.metrics.last_failure_time = time.time() - 61  # Past timeout (60s)

    async def success_func():
        return "success"

    # Should attempt reset and succeed
    result = await circuit_breaker.call(success_func)

    assert result == "success"
    assert circuit_breaker.metrics.state == CircuitState.HALF_OPEN

@pytest.mark.asyncio
async def test_circuit_breaker_half_open_success(circuit_breaker):
    """Test successful recovery sequence in HALF_OPEN state."""
    # Set to HALF_OPEN
    circuit_breaker.metrics.state = CircuitState.HALF_OPEN
    circuit_breaker.metrics.success_count = 0

    async def success_func():
        return "success"

    # First success
    await circuit_breaker.call(success_func)
    assert circuit_breaker.metrics.state == CircuitState.HALF_OPEN
    assert circuit_breaker.metrics.success_count == 1

    # Second success (threshold reached)
    await circuit_breaker.call(success_func)
    assert circuit_breaker.metrics.state == CircuitState.CLOSED
    assert circuit_breaker.metrics.success_count == 0
    assert circuit_breaker.metrics.failure_count == 0

@pytest.mark.asyncio
async def test_circuit_breaker_half_open_failure(circuit_breaker):
    """Test failure in HALF_OPEN state re-opens circuit."""
    circuit_breaker.metrics.state = CircuitState.HALF_OPEN

    async def failing_func():
        raise ValueError("error")

    with pytest.raises(ValueError):
        await circuit_breaker.call(failing_func)

    assert circuit_breaker.metrics.state == CircuitState.OPEN
    assert circuit_breaker.metrics.success_count == 0

@pytest.mark.asyncio
async def test_fallback_execution(circuit_breaker):
    """Test fallback is executed when circuit is OPEN."""
    circuit_breaker.metrics.state = CircuitState.OPEN
    circuit_breaker.metrics.last_failure_time = time.time()

    fallback_mock = Mock(return_value="fallback")
    circuit_breaker.fallback = fallback_mock

    target_mock = AsyncMock(return_value="target")

    result = await circuit_breaker.call(target_mock)

    assert result == "fallback"
    fallback_mock.assert_called_once()
    target_mock.assert_not_called()

@pytest.mark.asyncio
async def test_sync_call(circuit_breaker):
    """Test synchronous call support."""
    def sync_func():
        return "sync_success"

    result = await circuit_breaker.call_sync(sync_func)
    assert result == "sync_success"
    assert circuit_breaker.metrics.total_successes == 1

@pytest.mark.asyncio
async def test_sync_call_failure(circuit_breaker):
    """Test synchronous call failure."""
    def failing_func():
        raise ValueError("error")

    with pytest.raises(ValueError):
        await circuit_breaker.call_sync(failing_func)

    assert circuit_breaker.metrics.failure_count == 1
