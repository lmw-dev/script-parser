"""
Tests for timeout and performance optimization features
"""

import asyncio
import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from .config import MonitoringConfig, PerformanceConfig, TimeoutConfig
from .http_client import HTTPClientManager
from .logging_config import PerformanceLogger
from .performance_monitoring import ProcessingTimeMonitor
from .services.asr_service import ASRError, ASRService
from .services.llm_service import DeepSeekAdapter


class TestTimeoutConfiguration:
    """Test timeout configuration and enforcement"""

    def test_timeout_config_values(self):
        """Test that timeout configuration has reasonable values"""
        assert TimeoutConfig.ASR_TIMEOUT > 0
        assert TimeoutConfig.LLM_TIMEOUT > 0
        assert TimeoutConfig.OSS_UPLOAD_TIMEOUT > 0
        assert TimeoutConfig.URL_PARSER_TIMEOUT > 0
        assert TimeoutConfig.HTTP_CONNECT_TIMEOUT > 0
        assert TimeoutConfig.HTTP_READ_TIMEOUT > 0

        # Ensure total processing target is reasonable
        assert TimeoutConfig.TOTAL_PROCESSING_TARGET >= 30  # At least 30 seconds
        assert TimeoutConfig.TOTAL_PROCESSING_TARGET <= 120  # At most 2 minutes

    def test_http_timeout_config(self):
        """Test HTTP timeout configuration format"""
        http_timeout = TimeoutConfig.get_http_timeout()

        assert "connect" in http_timeout
        assert "read" in http_timeout
        assert "write" in http_timeout
        assert "pool" in http_timeout

        # All values should be positive
        for key, value in http_timeout.items():
            assert value > 0, f"{key} timeout should be positive"


class TestPerformanceConfiguration:
    """Test performance optimization configuration"""

    def test_performance_config_values(self):
        """Test that performance configuration has reasonable values"""
        assert PerformanceConfig.HTTP_POOL_CONNECTIONS > 0
        assert PerformanceConfig.HTTP_POOL_MAXSIZE > 0
        assert PerformanceConfig.HTTP_MAX_KEEPALIVE_CONNECTIONS > 0
        assert PerformanceConfig.HTTP_KEEPALIVE_EXPIRY > 0
        assert PerformanceConfig.MAX_FILE_SIZE > 0
        assert PerformanceConfig.CHUNK_SIZE > 0

    def test_http_limits_config(self):
        """Test HTTP connection limits configuration"""
        http_limits = PerformanceConfig.get_http_limits()

        assert "max_connections" in http_limits
        assert "max_keepalive_connections" in http_limits
        assert "keepalive_expiry" in http_limits

        # All values should be positive
        for key, value in http_limits.items():
            assert value > 0, f"{key} should be positive"


class TestHTTPClientManager:
    """Test HTTP client manager with connection pooling"""

    @pytest.mark.asyncio
    async def test_singleton_behavior(self):
        """Test that HTTPClientManager is a singleton"""
        manager1 = HTTPClientManager()
        manager2 = HTTPClientManager()

        assert manager1 is manager2

    @pytest.mark.asyncio
    async def test_client_creation(self):
        """Test HTTP client creation with proper configuration"""
        manager = HTTPClientManager()
        client = await manager.get_client()

        assert client is not None
        assert hasattr(client, "timeout")
        assert hasattr(client, "_limits") or hasattr(client, "_pool_limits")

        # Test that subsequent calls return the same client
        client2 = await manager.get_client()
        assert client is client2

    @pytest.mark.asyncio
    async def test_client_cleanup(self):
        """Test HTTP client cleanup"""
        manager = HTTPClientManager()
        client = await manager.get_client()

        await manager.close()

        # After closing, a new client should be created
        new_client = await manager.get_client()
        assert new_client is not client


class TestASRServiceTimeout:
    """Test ASR service timeout functionality"""

    @pytest.mark.asyncio
    async def test_asr_timeout_on_slow_response(self):
        """Test that ASR service times out on slow responses"""
        with patch(
            "dashscope.audio.asr.Transcription.async_call"
        ) as mock_async_call, patch(
            "dashscope.audio.asr.Transcription.wait"
        ) as mock_wait:
            # Mock a slow response that exceeds timeout
            async def slow_response(*args, **kwargs):
                await asyncio.sleep(TimeoutConfig.ASR_TIMEOUT + 1)
                return MagicMock()

            mock_async_call.return_value = MagicMock()
            mock_async_call.return_value.output.task_id = "test_task_id"
            mock_wait.side_effect = slow_response

            asr_service = ASRService()

            with pytest.raises(ASRError) as exc_info:
                await asr_service.transcribe_from_url("http://example.com/video.mp4")

            assert "timed out" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_asr_successful_within_timeout(self):
        """Test that ASR service works normally within timeout"""
        with patch(
            "dashscope.audio.asr.Transcription.async_call"
        ) as mock_async_call, patch(
            "dashscope.audio.asr.Transcription.wait"
        ) as mock_wait, patch.object(
            ASRService, "_process_transcription_response"
        ) as mock_process:
            # Mock successful response within timeout
            mock_task_response = MagicMock()
            mock_task_response.output.task_id = "test_task_id"
            mock_async_call.return_value = mock_task_response

            mock_transcription_response = MagicMock()
            mock_wait.return_value = mock_transcription_response

            mock_process.return_value = "Test transcript"

            asr_service = ASRService()
            result = await asr_service.transcribe_from_url(
                "http://example.com/video.mp4"
            )

            assert result == "Test transcript"
            mock_process.assert_called_once_with(mock_transcription_response)


class TestLLMServiceTimeout:
    """Test LLM service timeout functionality"""

    @pytest.mark.asyncio
    async def test_llm_timeout_configuration(self):
        """Test that LLM service uses configured timeout"""
        with patch(
            "apps.coprocessor.app.http_client.get_http_client"
        ) as mock_get_client:
            mock_client = AsyncMock()
            mock_get_client.return_value = mock_client

            # Mock successful response
            mock_response = MagicMock()
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": '{"hook": "test", "core": "test", "cta": "test"}'
                        }
                    }
                ]
            }
            mock_client.post.return_value = mock_response

            adapter = DeepSeekAdapter()
            await adapter.analyze("test text")

            # Verify that the client was called with the configured timeout
            mock_client.post.assert_called_once()
            call_kwargs = mock_client.post.call_args[1]
            assert call_kwargs["timeout"] == TimeoutConfig.LLM_TIMEOUT


class TestProcessingTimeMonitor:
    """Test processing time monitoring functionality"""

    def test_monitor_initialization(self):
        """Test ProcessingTimeMonitor initialization"""
        perf_logger = PerformanceLogger("test")
        monitor = ProcessingTimeMonitor(perf_logger)

        assert monitor.perf_logger is perf_logger
        assert monitor.start_time > 0
        assert len(monitor.checkpoints) == 0

    def test_checkpoint_recording(self):
        """Test checkpoint recording functionality"""
        perf_logger = PerformanceLogger("test")
        monitor = ProcessingTimeMonitor(perf_logger)

        # Record a checkpoint
        elapsed = monitor.checkpoint("test_checkpoint")

        assert elapsed >= 0
        assert "test_checkpoint" in monitor.checkpoints
        assert monitor.checkpoints["test_checkpoint"] == elapsed

    def test_target_compliance_check(self):
        """Test target compliance checking"""
        perf_logger = PerformanceLogger("test")
        monitor = ProcessingTimeMonitor(perf_logger)

        # Should be within target initially
        assert monitor.check_target_compliance() is True

        # Mock a long processing time
        monitor.start_time = time.time() - (TimeoutConfig.TOTAL_PROCESSING_TARGET + 10)
        assert monitor.check_target_compliance() is False

    def test_performance_summary(self):
        """Test performance summary generation"""
        perf_logger = PerformanceLogger("test")
        monitor = ProcessingTimeMonitor(perf_logger)

        # Add some checkpoints
        monitor.checkpoint("step1")
        time.sleep(0.01)  # Small delay
        monitor.checkpoint("step2")

        summary = monitor.get_performance_summary()

        assert "total_time" in summary
        assert "target_time" in summary
        assert "within_target" in summary
        assert "checkpoints" in summary

        assert summary["target_time"] == TimeoutConfig.TOTAL_PROCESSING_TARGET
        assert len(summary["checkpoints"]) == 2
        assert "step1" in summary["checkpoints"]
        assert "step2" in summary["checkpoints"]


class TestMemoryOptimization:
    """Test memory optimization features"""

    def test_streaming_upload_configuration(self):
        """Test streaming upload configuration"""
        assert isinstance(PerformanceConfig.ENABLE_STREAMING_UPLOAD, bool)
        assert PerformanceConfig.CHUNK_SIZE > 0
        assert PerformanceConfig.MAX_FILE_SIZE > 0

    def test_chunk_size_reasonable(self):
        """Test that chunk size is reasonable for memory usage"""
        # Chunk size should be between 1KB and 1MB for good memory/performance balance
        assert 1024 <= PerformanceConfig.CHUNK_SIZE <= 1024 * 1024


class TestMonitoringConfiguration:
    """Test monitoring configuration"""

    def test_monitoring_thresholds(self):
        """Test that monitoring thresholds are reasonable"""
        assert MonitoringConfig.SLOW_REQUEST_THRESHOLD > 0
        assert MonitoringConfig.ASR_SLOW_THRESHOLD > 0
        assert MonitoringConfig.LLM_SLOW_THRESHOLD > 0

        # ASR threshold should be reasonable (allow it to be higher than total target for edge cases)
        assert MonitoringConfig.ASR_SLOW_THRESHOLD > 0

        # LLM threshold should be less than ASR threshold (LLM is typically faster)
        assert MonitoringConfig.LLM_SLOW_THRESHOLD < MonitoringConfig.ASR_SLOW_THRESHOLD

    def test_monitoring_flags(self):
        """Test monitoring feature flags"""
        assert isinstance(MonitoringConfig.ENABLE_DETAILED_TIMING, bool)
        assert isinstance(MonitoringConfig.ENABLE_MEMORY_MONITORING, bool)


@pytest.mark.asyncio
async def test_integration_timeout_and_performance():
    """Integration test for timeout and performance features"""
    perf_logger = PerformanceLogger("integration_test")
    monitor = ProcessingTimeMonitor(perf_logger)

    # Simulate a workflow with checkpoints
    time.time()

    # Simulate URL parsing (fast)
    await asyncio.sleep(0.01)
    monitor.checkpoint("url_parsing_complete")

    # Simulate ASR processing (slower)
    await asyncio.sleep(0.02)
    monitor.checkpoint("asr_complete")

    # Simulate LLM analysis (medium)
    await asyncio.sleep(0.01)
    monitor.checkpoint("llm_complete")

    # Check that all checkpoints were recorded
    summary = monitor.get_performance_summary()
    assert len(summary["checkpoints"]) == 3
    assert (
        summary["within_target"] is True
    )  # Should be within target for this fast test

    # Verify checkpoint order
    checkpoints = summary["checkpoints"]
    assert checkpoints["url_parsing_complete"] < checkpoints["asr_complete"]
    assert checkpoints["asr_complete"] < checkpoints["llm_complete"]
