"""
Performance monitoring utilities and decorators for service call tracking.
"""

import functools
import time
from collections.abc import Callable
from typing import Any

from .config import MonitoringConfig, TimeoutConfig
from .logging_config import PerformanceLogger


def track_service_call(service_name: str, operation: str | None = None):
    """
    Decorator to track service call performance and results.

    Args:
        service_name: Name of the service being called
        operation: Optional operation name (defaults to function name)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            perf_logger = PerformanceLogger(f"service.{service_name}")
            op_name = operation or func.__name__
            start_time = time.time()
            success = False

            try:
                result = await func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                perf_logger.log_error(
                    f"Service call {service_name}.{op_name} failed",
                    e,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                )
                raise
            finally:
                duration = time.time() - start_time
                perf_logger.log_service_call(
                    service_name=service_name,
                    operation=op_name,
                    duration=duration,
                    success=success,
                )

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            perf_logger = PerformanceLogger(f"service.{service_name}")
            op_name = operation or func.__name__
            start_time = time.time()
            success = False

            try:
                result = func(*args, **kwargs)
                success = True
                return result
            except Exception as e:
                perf_logger.log_error(
                    f"Service call {service_name}.{op_name} failed",
                    e,
                    args_count=len(args),
                    kwargs_keys=list(kwargs.keys()),
                )
                raise
            finally:
                duration = time.time() - start_time
                perf_logger.log_service_call(
                    service_name=service_name,
                    operation=op_name,
                    duration=duration,
                    success=success,
                )

        # Return appropriate wrapper based on whether function is async
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class ServiceCallTracker:
    """Context manager for tracking service calls with detailed metrics"""

    def __init__(
        self, service_name: str, operation: str, perf_logger: PerformanceLogger
    ):
        self.service_name = service_name
        self.operation = operation
        self.perf_logger = perf_logger
        self.start_time = None
        self.success = False

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.success = exc_type is None

            if not self.success and exc_val:
                self.perf_logger.log_error(
                    f"Service call {self.service_name}.{self.operation} failed", exc_val
                )

            self.perf_logger.log_service_call(
                service_name=self.service_name,
                operation=self.operation,
                duration=duration,
                success=self.success,
            )

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration = time.time() - self.start_time
            self.success = exc_type is None

            if not self.success and exc_val:
                self.perf_logger.log_error(
                    f"Service call {self.service_name}.{self.operation} failed", exc_val
                )

            self.perf_logger.log_service_call(
                service_name=self.service_name,
                operation=self.operation,
                duration=duration,
                success=self.success,
            )


def create_service_tracker(
    service_name: str, operation: str, perf_logger: PerformanceLogger
) -> ServiceCallTracker:
    """Create a service call tracker context manager"""
    return ServiceCallTracker(service_name, operation, perf_logger)


class ProcessingTimeMonitor:
    """Monitor processing time against performance targets"""

    def __init__(self, perf_logger: PerformanceLogger):
        self.perf_logger = perf_logger
        self.start_time = time.time()
        self.checkpoints = {}

    def checkpoint(self, name: str) -> float:
        """Record a checkpoint and return elapsed time"""
        current_time = time.time()
        elapsed = current_time - self.start_time
        self.checkpoints[name] = elapsed

        # Check against thresholds
        if name == "asr_complete" and elapsed > MonitoringConfig.ASR_SLOW_THRESHOLD:
            self.perf_logger.logger.warning(
                f"ASR processing is slow: {elapsed:.2f}s (threshold: {MonitoringConfig.ASR_SLOW_THRESHOLD}s)"
            )
        elif name == "llm_complete" and elapsed > MonitoringConfig.LLM_SLOW_THRESHOLD:
            self.perf_logger.logger.warning(
                f"LLM processing is slow: {elapsed:.2f}s (threshold: {MonitoringConfig.LLM_SLOW_THRESHOLD}s)"
            )

        return elapsed

    def get_total_time(self) -> float:
        """Get total processing time"""
        return time.time() - self.start_time

    def check_target_compliance(self) -> bool:
        """Check if processing is within the 50-second target"""
        total_time = self.get_total_time()
        target = TimeoutConfig.TOTAL_PROCESSING_TARGET

        if total_time > target:
            self.perf_logger.logger.warning(
                f"Processing time {total_time:.2f}s exceeds target of {target}s"
            )
            return False

        return True

    def get_performance_summary(self) -> dict:
        """Get a summary of performance metrics"""
        total_time = self.get_total_time()
        return {
            "total_time": total_time,
            "target_time": TimeoutConfig.TOTAL_PROCESSING_TARGET,
            "within_target": total_time <= TimeoutConfig.TOTAL_PROCESSING_TARGET,
            "checkpoints": self.checkpoints.copy(),
        }
