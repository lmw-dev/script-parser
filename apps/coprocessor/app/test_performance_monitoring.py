"""
Tests for performance monitoring and logging functionality.
"""

import asyncio
import logging
import time

import pytest

from .logging_config import (
    PerformanceLogger,
    generate_request_id,
    set_request_context,
)
from .performance_monitoring import (
    create_service_tracker,
    track_service_call,
)


class TestPerformanceLogger:
    """Test performance logging functionality"""

    def test_generate_request_id(self):
        """Test request ID generation"""
        request_id = generate_request_id()
        assert isinstance(request_id, str)
        assert len(request_id) == 8

        # Test uniqueness
        request_id2 = generate_request_id()
        assert request_id != request_id2

    def test_set_request_context(self, caplog):
        """Test setting request context"""
        request_id = "test-123"
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id(request_id)

        with caplog.at_level(logging.INFO):
            perf_logger.start_request("test_request")

        # Check that request ID appears in log
        assert request_id in caplog.text

    def test_performance_logger_initialization(self):
        """Test PerformanceLogger initialization"""
        perf_logger = PerformanceLogger("test.module")
        assert perf_logger.logger.name == "test.module"
        assert perf_logger.request_id is None
        assert perf_logger.start_time is None
        assert perf_logger.step_times == {}

    def test_set_request_id(self):
        """Test setting request ID on performance logger"""
        perf_logger = PerformanceLogger("test.module")
        request_id = "test-456"

        perf_logger.set_request_id(request_id)
        assert perf_logger.request_id == request_id

    def test_start_request(self, caplog):
        """Test starting request tracking"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-789")

        with caplog.at_level(logging.INFO):
            perf_logger.start_request("test_request", param1="value1", param2="value2")

        assert perf_logger.start_time is not None
        assert "Starting test_request request" in caplog.text
        assert "test-789" in caplog.text

    def test_log_step_timing(self, caplog):
        """Test step timing functionality"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-step")

        with caplog.at_level(logging.INFO):
            # Start step
            start_time = perf_logger.log_step_start("test_step", param="value")
            assert isinstance(start_time, float)

            # Simulate some work
            time.sleep(0.01)

            # End step
            perf_logger.log_step_end("test_step", success=True)

        assert "Starting step: test_step" in caplog.text
        assert "Step test_step completed" in caplog.text
        assert "test_step_duration" in perf_logger.step_times

    def test_log_step_context_manager(self, caplog):
        """Test step logging context manager"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-context")

        with caplog.at_level(logging.INFO):
            with perf_logger.log_step("context_step", param="value"):
                time.sleep(0.01)

        assert "Starting step: context_step" in caplog.text
        assert "Step context_step completed" in caplog.text

    def test_log_step_context_manager_with_exception(self, caplog):
        """Test step logging context manager with exception"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-error")

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError):
                with perf_logger.log_step("error_step"):
                    raise ValueError("Test error")

        assert "Starting step: error_step" in caplog.text
        assert "Step error_step failed" in caplog.text

    def test_log_service_call(self, caplog):
        """Test service call logging"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-service")

        with caplog.at_level(logging.INFO):
            perf_logger.log_service_call(
                service_name="TestService",
                operation="test_operation",
                duration=0.123,
                success=True,
                param="value",
            )

        assert (
            "Service call: TestService.test_operation success in 0.123s" in caplog.text
        )

    def test_log_error(self, caplog):
        """Test error logging with stack trace"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-error-log")

        test_error = ValueError("Test error message")

        with caplog.at_level(logging.ERROR):
            perf_logger.log_error("Test operation failed", test_error, param="value")

        assert "Test operation failed: Test error message" in caplog.text
        assert "ValueError" in caplog.text

    def test_log_request_complete(self, caplog):
        """Test request completion logging"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-complete")
        perf_logger.start_request("test_request")

        # Add some step timings
        perf_logger.log_step_start("step1")
        time.sleep(0.01)
        perf_logger.log_step_end("step1", success=True)

        with caplog.at_level(logging.INFO):
            perf_logger.log_request_complete(success=True, result="success")

        assert "Request completed" in caplog.text
        assert "step1" in caplog.text

    def test_filter_sensitive_info(self):
        """Test sensitive information filtering"""
        perf_logger = PerformanceLogger("test.module")

        sensitive_data = {
            "password": "secret123",
            "api_key": "key123",
            "token": "token123",
            "normal_field": "normal_value",
            "long_text": "a" * 150,  # Long text that should be truncated
        }

        filtered = perf_logger._filter_sensitive_info(sensitive_data)

        assert filtered["password"] == "[REDACTED]"
        assert filtered["api_key"] == "[REDACTED]"
        assert filtered["token"] == "[REDACTED]"
        assert filtered["normal_field"] == "normal_value"
        assert "[TRUNCATED]" in filtered["long_text"]
        assert len(filtered["long_text"]) < 150


class TestServiceCallTracker:
    """Test service call tracking functionality"""

    def test_service_call_tracker_success(self, caplog):
        """Test successful service call tracking"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-tracker")

        with caplog.at_level(logging.INFO):
            with create_service_tracker("TestService", "test_op", perf_logger):
                time.sleep(0.01)

        assert "Service call: TestService.test_op success" in caplog.text

    def test_service_call_tracker_failure(self, caplog):
        """Test failed service call tracking"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-tracker-fail")

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError):
                with create_service_tracker("TestService", "test_op", perf_logger):
                    raise ValueError("Service failed")

        assert "Service call: TestService.test_op failure" in caplog.text

    @pytest.mark.asyncio
    async def test_async_service_call_tracker(self, caplog):
        """Test async service call tracking"""
        perf_logger = PerformanceLogger("test.module")
        perf_logger.set_request_id("test-async-tracker")

        with caplog.at_level(logging.INFO):
            async with create_service_tracker("AsyncService", "async_op", perf_logger):
                await asyncio.sleep(0.01)

        assert "Service call: AsyncService.async_op success" in caplog.text


class TestTrackServiceCallDecorator:
    """Test service call tracking decorator"""

    @pytest.mark.asyncio
    async def test_async_decorator_success(self, caplog):
        """Test async decorator for successful calls"""

        @track_service_call("TestService", "decorated_operation")
        async def test_async_function(param1, param2="default"):
            await asyncio.sleep(0.01)
            return f"result: {param1}, {param2}"

        with caplog.at_level(logging.INFO):
            result = await test_async_function("value1", param2="value2")

        assert result == "result: value1, value2"
        assert "Service call: TestService.decorated_operation success" in caplog.text

    @pytest.mark.asyncio
    async def test_async_decorator_failure(self, caplog):
        """Test async decorator for failed calls"""

        @track_service_call("TestService", "failing_operation")
        async def test_failing_function():
            raise ValueError("Decorated function failed")

        with caplog.at_level(logging.INFO):
            with pytest.raises(ValueError):
                await test_failing_function()

        assert "Service call: TestService.failing_operation failure" in caplog.text

    def test_sync_decorator_success(self, caplog):
        """Test sync decorator for successful calls"""

        @track_service_call("SyncService", "sync_operation")
        def test_sync_function(param1):
            time.sleep(0.01)
            return f"sync result: {param1}"

        with caplog.at_level(logging.INFO):
            result = test_sync_function("value1")

        assert result == "sync result: value1"
        assert "Service call: SyncService.sync_operation success" in caplog.text

    def test_sync_decorator_failure(self, caplog):
        """Test sync decorator for failed calls"""

        @track_service_call("SyncService", "failing_sync_operation")
        def test_failing_sync_function():
            raise RuntimeError("Sync function failed")

        with caplog.at_level(logging.INFO):
            with pytest.raises(RuntimeError):
                test_failing_sync_function()

        assert "Service call: SyncService.failing_sync_operation failure" in caplog.text

    def test_decorator_without_operation_name(self, caplog):
        """Test decorator using function name as operation"""

        @track_service_call("AutoNameService")
        def auto_named_function():
            return "auto named result"

        with caplog.at_level(logging.INFO):
            result = auto_named_function()

        assert result == "auto named result"
        assert (
            "Service call: AutoNameService.auto_named_function success" in caplog.text
        )


class TestIntegrationScenarios:
    """Test integration scenarios combining multiple features"""

    @pytest.mark.asyncio
    async def test_complete_workflow_logging(self, caplog):
        """Test complete workflow with all logging features"""
        request_id = generate_request_id()
        set_request_context(request_id)

        perf_logger = PerformanceLogger("integration.test")
        perf_logger.set_request_id(request_id)

        with caplog.at_level(logging.INFO):
            perf_logger.start_request("integration_test", workflow="complete")

            # Simulate multiple steps
            with perf_logger.log_step("step1", operation="parse"):
                time.sleep(0.01)

            with perf_logger.log_step("step2", operation="process"):
                async with create_service_tracker(
                    "ProcessingService", "process", perf_logger
                ):
                    await asyncio.sleep(0.01)

            # Simulate an error in step3
            try:
                with perf_logger.log_step("step3", operation="analyze"):
                    raise ValueError("Analysis failed")
            except ValueError as e:
                perf_logger.log_error("Step 3 failed", e)

            perf_logger.log_request_complete(success=False, error="analysis_failed")

        # Verify all logging occurred
        log_text = caplog.text
        assert request_id in log_text
        assert "Starting integration_test request" in log_text
        assert "Starting step: step1" in log_text
        assert "Step step1 completed" in log_text
        assert "Service call: ProcessingService.process success" in log_text
        assert "Step 3 failed: Analysis failed" in log_text
        assert "Request failed" in log_text

    def test_sensitive_data_filtering_in_workflow(self, caplog):
        """Test that sensitive data is properly filtered throughout workflow"""
        perf_logger = PerformanceLogger("security.test")
        perf_logger.set_request_id("security-test")

        with caplog.at_level(logging.INFO):
            perf_logger.start_request(
                "security_test",
                password="secret123",
                api_key="key456",
                normal_data="visible",
            )

            perf_logger.log_service_call(
                "SecureService",
                "authenticate",
                0.1,
                True,
                token="bearer_token_123",
                user_id="user123",
            )

            perf_logger.log_request_complete(
                success=True, access_token="final_token_456", result="success"
            )

        log_text = caplog.text
        # Sensitive data should be redacted
        assert "secret123" not in log_text
        assert "key456" not in log_text
        assert "bearer_token_123" not in log_text
        assert "final_token_456" not in log_text

        # Non-sensitive data should be visible
        assert "visible" in log_text
        assert "user123" in log_text
        assert "success" in log_text
        assert "[REDACTED]" in log_text
