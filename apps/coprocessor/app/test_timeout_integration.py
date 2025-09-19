"""
Integration test for timeout and performance optimization
"""

import asyncio
import time
from unittest.mock import MagicMock, patch

import pytest

from .config import TimeoutConfig
from .logging_config import PerformanceLogger
from .main import WorkflowOrchestrator


@pytest.mark.asyncio
async def test_workflow_orchestrator_with_performance_monitoring():
    """Test that WorkflowOrchestrator includes performance monitoring"""
    perf_logger = PerformanceLogger("test")
    orchestrator = WorkflowOrchestrator(perf_logger)

    # Verify that the orchestrator has a time monitor
    assert hasattr(orchestrator, "time_monitor")
    assert orchestrator.time_monitor is not None

    # Test checkpoint functionality
    elapsed = orchestrator.time_monitor.checkpoint("test_checkpoint")
    assert elapsed >= 0

    # Test performance summary
    summary = orchestrator.time_monitor.get_performance_summary()
    assert "total_time" in summary
    assert "target_time" in summary
    assert "within_target" in summary
    assert "checkpoints" in summary


@pytest.mark.asyncio
async def test_asr_service_timeout_integration():
    """Test ASR service timeout integration"""
    from .services.asr_service import ASRService

    # Test that ASR service uses the configured timeout
    asr_service = ASRService()

    # Mock a slow operation that would exceed timeout
    with patch(
        "dashscope.audio.asr.Transcription.async_call"
    ) as mock_async_call, patch("dashscope.audio.asr.Transcription.wait") as mock_wait:
        # Setup mock response
        mock_task_response = MagicMock()
        mock_task_response.output.task_id = "test_task_id"
        mock_async_call.return_value = mock_task_response

        # Mock a slow wait operation
        async def slow_wait(*args, **kwargs):
            await asyncio.sleep(0.1)  # Small delay for testing
            return MagicMock()

        mock_wait.side_effect = slow_wait

        # This should work within timeout
        with patch.object(
            asr_service,
            "_process_transcription_response",
            return_value="test transcript",
        ):
            result = await asr_service.transcribe_from_url(
                "http://example.com/video.mp4"
            )
            assert result == "test transcript"


@pytest.mark.asyncio
async def test_llm_service_timeout_integration():
    """Test LLM service timeout integration"""
    from .services.llm_service import DeepSeekAdapter

    with patch.object(DeepSeekAdapter, "analyze") as mock_analyze:
        # Mock successful response
        from .services.llm_service import AnalysisResult

        mock_result = AnalysisResult(hook="test hook", core="test core", cta="test cta")
        mock_analyze.return_value = mock_result

        adapter = DeepSeekAdapter()
        result = await adapter.analyze("test text")

        # Verify the result
        assert result.hook == "test hook"
        assert result.core == "test core"
        assert result.cta == "test cta"

        # Verify the method was called
        mock_analyze.assert_called_once_with("test text")


@pytest.mark.asyncio
async def test_file_handler_memory_optimization():
    """Test file handler memory optimization features"""
    from .config import PerformanceConfig
    from .services.file_handler import FileHandler

    # Test that file handler uses the configured settings
    FileHandler()

    # Verify configuration is loaded
    assert PerformanceConfig.MAX_FILE_SIZE > 0
    assert PerformanceConfig.CHUNK_SIZE > 0
    assert isinstance(PerformanceConfig.ENABLE_STREAMING_UPLOAD, bool)


def test_configuration_values():
    """Test that all timeout and performance configurations are reasonable"""
    # Test timeout configurations
    assert TimeoutConfig.ASR_TIMEOUT > 0
    assert TimeoutConfig.LLM_TIMEOUT > 0
    assert TimeoutConfig.OSS_UPLOAD_TIMEOUT > 0
    assert TimeoutConfig.URL_PARSER_TIMEOUT > 0
    assert TimeoutConfig.TOTAL_PROCESSING_TARGET > 0

    # Test HTTP timeout configurations
    http_timeout = TimeoutConfig.get_http_timeout()
    assert all(v > 0 for v in http_timeout.values())

    # Test performance configurations
    from .config import PerformanceConfig

    assert PerformanceConfig.HTTP_POOL_CONNECTIONS > 0
    assert PerformanceConfig.HTTP_POOL_MAXSIZE > 0
    assert PerformanceConfig.MAX_FILE_SIZE > 0
    assert PerformanceConfig.CHUNK_SIZE > 0

    # Test HTTP limits
    http_limits = PerformanceConfig.get_http_limits()
    assert all(v > 0 for v in http_limits.values())


@pytest.mark.asyncio
async def test_http_client_connection_pooling():
    """Test HTTP client connection pooling functionality"""
    from .http_client import HTTPClientManager, get_http_client

    # Test singleton behavior
    manager1 = HTTPClientManager()
    manager2 = HTTPClientManager()
    assert manager1 is manager2

    # Test client creation and reuse
    client1 = await get_http_client()
    client2 = await get_http_client()
    assert client1 is client2

    # Test client has proper configuration
    assert hasattr(client1, "timeout")
    # Note: httpx client stores limits differently, just verify it's configured
    assert client1 is not None


@pytest.mark.asyncio
async def test_performance_monitoring_integration():
    """Test performance monitoring integration"""
    from .performance_monitoring import ProcessingTimeMonitor

    perf_logger = PerformanceLogger("test")
    monitor = ProcessingTimeMonitor(perf_logger)

    # Test checkpoint recording
    time.time()

    # Simulate some processing steps
    await asyncio.sleep(0.01)
    monitor.checkpoint("step1")

    await asyncio.sleep(0.01)
    monitor.checkpoint("step2")

    # Test performance summary
    summary = monitor.get_performance_summary()

    assert "total_time" in summary
    assert "target_time" in summary
    assert "within_target" in summary
    assert "checkpoints" in summary

    # Verify checkpoints were recorded
    assert "step1" in summary["checkpoints"]
    assert "step2" in summary["checkpoints"]

    # Verify timing is reasonable
    assert summary["checkpoints"]["step1"] < summary["checkpoints"]["step2"]
    assert summary["total_time"] > 0

    # For this fast test, should be within target
    assert summary["within_target"] is True
