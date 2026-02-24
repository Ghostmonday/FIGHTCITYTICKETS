"""
Resilience patterns for Fight City Tickets - Production Hardening

Provides:
- Circuit Breaker pattern for external service resilience
- Retry decorator with exponential backoff and jitter
- Fallback handlers for graceful degradation
"""

import asyncio
import functools
import logging
import random
import time
from dataclasses import dataclass, field
from enum import Enum
from types import TracebackType
from typing import Any, Awaitable, Callable, Optional, TypeVar, Union

logger = logging.getLogger(__name__)

T = TypeVar("T")
ExcInfo = tuple[type[BaseException], BaseException, TracebackType] | tuple[None, None, None]


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker."""
    failure_threshold: int = 5  # Failures before opening
    success_threshold: int = 3  # Successes in half-open to close
    timeout_seconds: int = 300  # 5 minutes cooldown
    expected_exception: type[Exception] = Exception


@dataclass
class CircuitBreakerMetrics:
    """Metrics for circuit breaker monitoring."""
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    last_failure_reason: Optional[str] = None
    total_calls: int = 0
    total_failures: int = 0
    total_successes: int = 0


class CircuitBreaker:
    """
    Circuit Breaker implementation for external service protection.
    
    Prevents cascading failures by stopping requests to a failing service.
    After configured number of failures, opens the circuit for a timeout period.
    Then enters half-open state to test recovery.
    """
    
    _instances: dict[str, "CircuitBreaker"] = {}
    
    def __init__(
        self,
        name: str,
        config: Optional[CircuitBreakerConfig] = None,
        fallback: Optional[Callable[[], T]] = None,
    ):
        """
        Initialize circuit breaker.
        
        Args:
            name: Unique identifier for this circuit breaker
            config: Circuit breaker configuration
            fallback: Fallback function to call when circuit is open
        """
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.fallback = fallback
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()
        CircuitBreaker._instances[name] = self
    
    @classmethod
    def get_instance(cls, name: str) -> Optional["CircuitBreaker"]:
        """Get circuit breaker instance by name."""
        return cls._instances.get(name)
    
    @classmethod
    def get_all_instances(cls) -> dict[str, "CircuitBreaker"]:
        """Get all circuit breaker instances."""
        return cls._instances.copy()
    
    async def __aenter__(self) -> "CircuitBreaker":
        """Async context manager entry."""
        await self._before_call()
        return self
    
    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> bool:
        """Async context manager exit."""
        if exc_type is None:
            await self._on_success()
        elif exc_val is not None:
            await self._on_failure(exc_val) if isinstance(exc_val, Exception) else None
        return False
    
    async def _before_call(self) -> None:
        """Check circuit state before making a call."""
        if self.metrics.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.metrics.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit {self.name}: OPEN → HALF_OPEN")
            else:
                reason = f"Circuit {self.name} is OPEN. Retry after {self.config.timeout_seconds}s"
                logger.warning(reason)
                raise CircuitOpenError(reason)
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.metrics.last_failure_time is None:
            return True
        elapsed = time.time() - self.metrics.last_failure_time
        return elapsed >= self.config.timeout_seconds
    
    async def call(self, func: Callable[..., Awaitable[T]], *args: Any, **kwargs: Any) -> T:
        """
        Execute an async function with circuit breaker protection.
        
        Args:
            func: Async function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result or fallback
            
        Raises:
            Original exception if circuit is closed
            CircuitOpenError if circuit is open
        """
        try:
            await self._before_call()
        except CircuitOpenError:
            if self.fallback:
                return self.fallback()  # type: ignore
            raise
        
        try:
            result = await func(*args, **kwargs)
            await self._on_success()
            return result
        except self.config.expected_exception as e:
            await self._on_failure(e)
            raise
    
    async def call_sync(self, func: Callable[[], T], *args: Any, **kwargs: Any) -> T:
        """
        Execute a sync function with circuit breaker protection.
        
        Args:
            func: Sync function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result or fallback
            
        Raises:
            Original exception if circuit is closed
            CircuitOpenError if circuit is open
        """
        try:
            await self._before_call()
        except CircuitOpenError:
            if self.fallback:
                return self.fallback()  # type: ignore
            raise
        
        try:
            result = func(*args, **kwargs)
            await self._on_success()
            return result
        except self.config.expected_exception as e:
            await self._on_failure(e)
            raise
    
    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            self.metrics.total_calls += 1
            self.metrics.total_successes += 1
            self.metrics.success_count += 1
            
            if self.metrics.state == CircuitState.HALF_OPEN:
                if self.metrics.success_count >= self.config.success_threshold:
                    self.metrics.state = CircuitState.CLOSED
                    self.metrics.failure_count = 0
                    self.metrics.success_count = 0
                    logger.info(f"Circuit {self.name}: HALF_OPEN → CLOSED")
    
    async def _on_failure(self, error: Exception) -> None:
        """Handle failed call."""
        async with self._lock:
            self.metrics.total_calls += 1
            self.metrics.total_failures += 1
            self.metrics.failure_count += 1
            self.metrics.last_failure_time = time.time()
            self.metrics.last_failure_reason = str(error)
            
            if self.metrics.state == CircuitState.HALF_OPEN:
                self.metrics.state = CircuitState.OPEN
                self.metrics.success_count = 0
                logger.warning(f"Circuit {self.name}: HALF_OPEN → OPEN (failure {self.metrics.failure_count})")
            elif self.metrics.failure_count >= self.config.failure_threshold:
                self.metrics.state = CircuitState.OPEN
                logger.warning(
                    f"Circuit {self.name}: OPEN (threshold reached: {self.config.failure_threshold})"
                )
    
    def reset(self) -> None:
        """Reset circuit breaker to closed state."""
        self.metrics = CircuitBreakerMetrics()
        logger.info(f"Circuit {self.name}: Reset to CLOSED")
    
    def get_status(self) -> dict[str, Any]:
        """Get circuit breaker status for health checks."""
        return {
            "name": self.name,
            "state": self.metrics.state.value,
            "failure_count": self.metrics.failure_count,
            "success_count": self.metrics.success_count,
            "total_calls": self.metrics.total_calls,
            "total_failures": self.metrics.total_failures,
            "total_successes": self.metrics.total_successes,
            "last_failure_time": self.metrics.last_failure_time,
            "last_failure_reason": self.metrics.last_failure_reason,
            "config": {
                "failure_threshold": self.config.failure_threshold,
                "timeout_seconds": self.config.timeout_seconds,
            },
        }


class CircuitOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


def retry_async(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    jitter: float = 0.25,
    expected_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Callable[[Callable[..., Awaitable[T]]], Callable[..., Awaitable[T]]]:
    """
    Async retry decorator with exponential backoff and jitter.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff
        jitter: Random jitter factor (±percentage)
        expected_exceptions: Tuple of exception types to retry
        on_retry: Callback called on each retry (attempt, error, delay)
    
    Returns:
        Decorated async function
    """
    def decorator(func: Callable[..., Awaitable[T]]) -> Callable[..., Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: BaseException | None = None
            
            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except expected_exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        # Calculate delay with exponential backoff and jitter
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                        jitter_range = delay * jitter
                        actual_delay = delay + random.uniform(-jitter_range, jitter_range)
                        
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts - 1} for {func.__name__}: "
                            f"{type(e).__name__} after {actual_delay:.2f}s"
                        )
                        
                        if on_retry:
                            on_retry(attempt, e, actual_delay)
                        
                        await asyncio.sleep(actual_delay)
            
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected state in retry decorator")
        
        return wrapper
    return decorator


def retry_sync(
    max_attempts: int = 3,
    base_delay: float = 0.1,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    jitter: float = 0.25,
    expected_exceptions: tuple[type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable[[int, Exception, float], None]] = None,
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Sync retry decorator with exponential backoff and jitter.
    
    Args:
        max_attempts: Maximum number of attempts
        base_delay: Initial delay between retries (seconds)
        max_delay: Maximum delay between retries (seconds)
        exponential_base: Base for exponential backoff
        jitter: Random jitter factor (±percentage)
        expected_exceptions: Tuple of exception types to retry
        on_retry: Callback called on each retry (attempt, error, delay)
    
    Returns:
        Decorated sync function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception: BaseException | None = None
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except expected_exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        delay = min(base_delay * (exponential_base ** attempt), max_delay)
                        jitter_range = delay * jitter
                        actual_delay = delay + random.uniform(-jitter_range, jitter_range)
                        
                        logger.warning(
                            f"Retry {attempt + 1}/{max_attempts - 1} for {func.__name__}: "
                            f"{type(e).__name__} after {actual_delay:.2f}s"
                        )
                        
                        if on_retry:
                            on_retry(attempt, e, actual_delay)
                        
                        time.sleep(actual_delay)
            
            if last_exception is not None:
                raise last_exception
            raise RuntimeError("Unexpected state in retry decorator")
        
        return wrapper
    return decorator


# Pre-configured circuit breakers for common services
def create_stripe_circuit(fallback: Optional[Callable[[], T]] = None) -> CircuitBreaker:
    """Create circuit breaker for Stripe API."""
    return CircuitBreaker(
        name="stripe",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=300,  # 5 minutes
            expected_exception=Exception,  # type: ignore
        ),
        fallback=fallback,
    )


def create_email_circuit(fallback: Optional[Callable[[], T]] = None) -> CircuitBreaker:
    """Create circuit breaker for Email service."""
    return CircuitBreaker(
        name="email",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=300,
            expected_exception=Exception,  # type: ignore
        ),
        fallback=fallback,
    )


def create_deepseek_circuit(fallback: Optional[Callable[[], T]] = None) -> CircuitBreaker:
    """Create circuit breaker for DeepSeek AI API."""
    return CircuitBreaker(
        name="deepseek",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=300,
            expected_exception=Exception,  # type: ignore
        ),
        fallback=fallback,
    )


def create_database_circuit(fallback: Optional[Callable[[], T]] = None) -> CircuitBreaker:
    """Create circuit breaker for Database connections."""
    return CircuitBreaker(
        name="database",
        config=CircuitBreakerConfig(
            failure_threshold=5,
            timeout_seconds=300,
            expected_exception=Exception,  # type: ignore
        ),
        fallback=fallback,
    )


__all__ = [
    "CircuitBreaker",
    "CircuitBreakerConfig",
    "CircuitBreakerMetrics",
    "CircuitState",
    "CircuitOpenError",
    "retry_async",
    "retry_sync",
    "create_stripe_circuit",
    "create_email_circuit",
    "create_deepseek_circuit",
    "create_database_circuit",
]
