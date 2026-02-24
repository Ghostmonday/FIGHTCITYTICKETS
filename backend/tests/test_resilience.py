import asyncio
import time
from unittest.mock import AsyncMock, Mock, patch

import pytest
from src.middleware.resilience import (
    CircuitBreaker,
    CircuitBreakerConfig,
    CircuitState,
    CircuitOpenError,
    retry_async,
    retry_sync,
)

# --- Circuit Breaker Tests ---

@pytest.fixture
def cb_config():
    return CircuitBreakerConfig(
        failure_threshold=2,
        success_threshold=2,
        timeout_seconds=1,  # Short timeout for testing
    )

@pytest.fixture
def circuit_breaker(cb_config):
    return CircuitBreaker("test-circuit", config=cb_config)

@pytest.mark.asyncio
async def test_initial_state(circuit_breaker):
    """Verify initial state is CLOSED with zero metrics."""
    assert circuit_breaker.metrics.state == CircuitState.CLOSED
    assert circuit_breaker.metrics.failure_count == 0
    assert circuit_breaker.metrics.success_count == 0
    assert circuit_breaker.metrics.total_calls == 0

@pytest.mark.asyncio
async def test_success_call(circuit_breaker):
    """Verify successful calls update metrics correctly."""
    async def success_func():
        return "success"

    result = await circuit_breaker.call(success_func)

    assert result == "success"
    assert circuit_breaker.metrics.state == CircuitState.CLOSED
    assert circuit_breaker.metrics.success_count == 1
    assert circuit_breaker.metrics.failure_count == 0
    assert circuit_breaker.metrics.total_calls == 1

@pytest.mark.asyncio
async def test_failure_call(circuit_breaker):
    """Verify failed calls update metrics and trigger state change."""
    async def fail_func():
        raise ValueError("failure")

    with pytest.raises(ValueError):
        await circuit_breaker.call(fail_func)

    assert circuit_breaker.metrics.failure_count == 1
    assert circuit_breaker.metrics.state == CircuitState.CLOSED  # Threshold is 2

    # Second failure should trigger OPEN
    with pytest.raises(ValueError):
        await circuit_breaker.call(fail_func)

    assert circuit_breaker.metrics.failure_count == 2
    assert circuit_breaker.metrics.state == CircuitState.OPEN

@pytest.mark.asyncio
async def test_circuit_open_behavior(circuit_breaker):
    """Verify circuit rejects calls when OPEN."""
    # Force OPEN state
    circuit_breaker.metrics.state = CircuitState.OPEN
    circuit_breaker.metrics.last_failure_time = time.time()

    async def success_func():
        return "should not run"

    with pytest.raises(CircuitOpenError):
        await circuit_breaker.call(success_func)

@pytest.mark.asyncio
async def test_half_open_transition(circuit_breaker):
    """Verify transition to HALF_OPEN after timeout."""
    # Force OPEN state with old timestamp
    circuit_breaker.metrics.state = CircuitState.OPEN
    circuit_breaker.metrics.last_failure_time = time.time() - 2  # 2 seconds ago (timeout is 1s)

    async def success_func():
        return "recovery"

    # First call should transition to HALF_OPEN and succeed
    result = await circuit_breaker.call(success_func)

    assert result == "recovery"
    assert circuit_breaker.metrics.state == CircuitState.HALF_OPEN
    assert circuit_breaker.metrics.success_count == 1

@pytest.mark.asyncio
async def test_recovery_to_closed(circuit_breaker):
    """Verify transition from HALF_OPEN to CLOSED after success threshold."""
    circuit_breaker.metrics.state = CircuitState.HALF_OPEN

    async def success_func():
        return "ok"

    # Need 2 successes to close (config.success_threshold=2)
    await circuit_breaker.call(success_func)
    assert circuit_breaker.metrics.state == CircuitState.HALF_OPEN
    assert circuit_breaker.metrics.success_count == 1

    await circuit_breaker.call(success_func)
    assert circuit_breaker.metrics.state == CircuitState.CLOSED
    assert circuit_breaker.metrics.success_count == 0  # Resets on close
    assert circuit_breaker.metrics.failure_count == 0

@pytest.mark.asyncio
async def test_half_open_failure(circuit_breaker):
    """Verify failure in HALF_OPEN trips back to OPEN."""
    circuit_breaker.metrics.state = CircuitState.HALF_OPEN

    async def fail_func():
        raise ValueError("oops")

    with pytest.raises(ValueError):
        await circuit_breaker.call(fail_func)

    assert circuit_breaker.metrics.state == CircuitState.OPEN
    assert circuit_breaker.metrics.success_count == 0

@pytest.mark.asyncio
async def test_fallback(cb_config):
    """Verify fallback is called when circuit is OPEN."""
    fallback_mock = Mock(return_value="fallback_result")
    cb = CircuitBreaker("fallback-test", config=cb_config, fallback=fallback_mock)

    # Force OPEN
    cb.metrics.state = CircuitState.OPEN
    cb.metrics.last_failure_time = time.time()

    async def target_func():
        return "target"

    result = await cb.call(target_func)

    assert result == "fallback_result"
    fallback_mock.assert_called_once()

@pytest.mark.asyncio
async def test_call_sync(circuit_breaker):
    """Verify sync call wrapper works."""
    def sync_func():
        return "sync_result"

    result = await circuit_breaker.call_sync(sync_func)

    assert result == "sync_result"
    assert circuit_breaker.metrics.total_calls == 1

# --- Retry Tests ---

@pytest.mark.asyncio
async def test_retry_async():
    """Verify async retry decorator."""
    mock_func = AsyncMock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])

    @retry_async(max_attempts=3, base_delay=0.01)
    async def decorated_func():
        return await mock_func()

    result = await decorated_func()

    assert result == "success"
    assert mock_func.call_count == 3

@pytest.mark.asyncio
async def test_retry_async_exhausted():
    """Verify async retry fails after max attempts."""
    mock_func = AsyncMock(side_effect=ValueError("fail"))

    @retry_async(max_attempts=2, base_delay=0.01)
    async def decorated_func():
        await mock_func()

    with pytest.raises(ValueError):
        await decorated_func()

    assert mock_func.call_count == 2

def test_retry_sync():
    """Verify sync retry decorator."""
    mock_func = Mock(side_effect=[ValueError("fail"), "success"])

    @retry_sync(max_attempts=3, base_delay=0.01)
    def decorated_func():
        return mock_func()

    result = decorated_func()

    assert result == "success"
    assert mock_func.call_count == 2
