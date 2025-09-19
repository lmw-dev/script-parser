"""
Configuration module for timeout and performance settings
"""

import os
from typing import Any


class TimeoutConfig:
    """Timeout configuration for various services"""

    # Service-specific timeouts (in seconds)
    ASR_TIMEOUT = float(os.getenv("ASR_TIMEOUT", "120"))  # 2 minutes for ASR processing
    LLM_TIMEOUT = float(os.getenv("LLM_TIMEOUT", "30"))  # 30 seconds for LLM analysis
    OSS_UPLOAD_TIMEOUT = float(
        os.getenv("OSS_UPLOAD_TIMEOUT", "60")
    )  # 1 minute for OSS upload
    URL_PARSER_TIMEOUT = float(
        os.getenv("URL_PARSER_TIMEOUT", "10")
    )  # 10 seconds for URL parsing

    # HTTP client timeouts
    HTTP_CONNECT_TIMEOUT = float(
        os.getenv("HTTP_CONNECT_TIMEOUT", "5")
    )  # 5 seconds to connect
    HTTP_READ_TIMEOUT = float(
        os.getenv("HTTP_READ_TIMEOUT", "30")
    )  # 30 seconds to read response
    HTTP_WRITE_TIMEOUT = float(
        os.getenv("HTTP_WRITE_TIMEOUT", "10")
    )  # 10 seconds to write request
    HTTP_POOL_TIMEOUT = float(
        os.getenv("HTTP_POOL_TIMEOUT", "5")
    )  # 5 seconds to get connection from pool

    # Performance targets
    TOTAL_PROCESSING_TARGET = float(
        os.getenv("TOTAL_PROCESSING_TARGET", "50")
    )  # 50 seconds total target

    @classmethod
    def get_http_timeout(cls) -> dict[str, float]:
        """Get HTTP timeout configuration for httpx"""
        return {
            "connect": cls.HTTP_CONNECT_TIMEOUT,
            "read": cls.HTTP_READ_TIMEOUT,
            "write": cls.HTTP_WRITE_TIMEOUT,
            "pool": cls.HTTP_POOL_TIMEOUT,
        }


class PerformanceConfig:
    """Performance optimization configuration"""

    # HTTP connection pool settings
    HTTP_POOL_CONNECTIONS = int(os.getenv("HTTP_POOL_CONNECTIONS", "10"))
    HTTP_POOL_MAXSIZE = int(os.getenv("HTTP_POOL_MAXSIZE", "10"))
    HTTP_MAX_KEEPALIVE_CONNECTIONS = int(
        os.getenv("HTTP_MAX_KEEPALIVE_CONNECTIONS", "5")
    )
    HTTP_KEEPALIVE_EXPIRY = float(os.getenv("HTTP_KEEPALIVE_EXPIRY", "5"))

    # File processing settings
    MAX_FILE_SIZE = int(
        os.getenv("MAX_FILE_SIZE", str(100 * 1024 * 1024))
    )  # 100MB default
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "8192"))  # 8KB chunks for file processing

    # Memory optimization settings
    ENABLE_STREAMING_UPLOAD = (
        os.getenv("ENABLE_STREAMING_UPLOAD", "true").lower() == "true"
    )
    TEMP_FILE_CLEANUP_DELAY = float(
        os.getenv("TEMP_FILE_CLEANUP_DELAY", "0")
    )  # Immediate cleanup

    @classmethod
    def get_http_limits(cls) -> dict[str, Any]:
        """Get HTTP connection limits for httpx"""
        return {
            "max_connections": cls.HTTP_POOL_CONNECTIONS,
            "max_keepalive_connections": cls.HTTP_MAX_KEEPALIVE_CONNECTIONS,
            "keepalive_expiry": cls.HTTP_KEEPALIVE_EXPIRY,
        }


class MonitoringConfig:
    """Monitoring and alerting configuration"""

    # Performance thresholds for alerting
    SLOW_REQUEST_THRESHOLD = float(
        os.getenv("SLOW_REQUEST_THRESHOLD", "30")
    )  # 30 seconds
    ASR_SLOW_THRESHOLD = float(os.getenv("ASR_SLOW_THRESHOLD", "90"))  # 90 seconds
    LLM_SLOW_THRESHOLD = float(os.getenv("LLM_SLOW_THRESHOLD", "20"))  # 20 seconds

    # Monitoring intervals
    PERFORMANCE_LOG_INTERVAL = float(
        os.getenv("PERFORMANCE_LOG_INTERVAL", "10")
    )  # Log every 10 seconds

    # Enable/disable monitoring features
    ENABLE_DETAILED_TIMING = (
        os.getenv("ENABLE_DETAILED_TIMING", "true").lower() == "true"
    )
    ENABLE_MEMORY_MONITORING = (
        os.getenv("ENABLE_MEMORY_MONITORING", "true").lower() == "true"
    )
