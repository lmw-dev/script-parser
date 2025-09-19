"""
Logging configuration and utilities for performance monitoring and request tracking.
"""

import logging
import time
import uuid
from contextlib import contextmanager
from typing import Any

# Configure logging format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"


class RequestContextFilter(logging.Filter):
    """Filter to add request ID to log records"""

    def __init__(self):
        super().__init__()
        self.request_id = "no-request-id"

    def set_request_id(self, request_id: str):
        """Set the current request ID"""
        self.request_id = request_id

    def filter(self, record):
        """Add request_id to the log record"""
        record.request_id = self.request_id
        return True


# Global request context filter
request_filter = RequestContextFilter()


def setup_logging():
    """Setup logging configuration for the application"""
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(),
        ],
    )

    # Add request context filter to all handlers
    root_logger = logging.getLogger()
    for handler in root_logger.handlers:
        handler.addFilter(request_filter)

    # Set specific log levels for different modules
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.INFO)


def generate_request_id() -> str:
    """Generate a unique request ID for tracking"""
    return str(uuid.uuid4())[:8]


def set_request_context(request_id: str):
    """Set the request context for logging"""
    request_filter.set_request_id(request_id)


class PerformanceLogger:
    """Logger for performance monitoring and service call tracking"""

    def __init__(self, logger_name: str = __name__):
        self.logger = logging.getLogger(logger_name)
        self.request_id = None
        self.start_time = None
        self.step_times: dict[str, float] = {}

    def set_request_id(self, request_id: str):
        """Set request ID for this performance logger instance"""
        self.request_id = request_id
        set_request_context(request_id)

    def start_request(self, request_type: str, **kwargs):
        """Start tracking a request"""
        self.start_time = time.time()
        # Filter out sensitive information from kwargs
        safe_kwargs = self._filter_sensitive_info(kwargs)
        request_prefix = f"[{self.request_id}]" if self.request_id else ""
        if safe_kwargs:
            self.logger.info(
                f"{request_prefix} Starting {request_type} request with params: {safe_kwargs}"
            )
        else:
            self.logger.info(f"{request_prefix} Starting {request_type} request")

    def log_step_start(self, step_name: str, **kwargs):
        """Log the start of a processing step"""
        step_start_time = time.time()
        self.step_times[f"{step_name}_start"] = step_start_time
        # Filter out sensitive information
        safe_kwargs = self._filter_sensitive_info(kwargs)
        request_prefix = f"[{self.request_id}]" if self.request_id else ""
        if safe_kwargs:
            self.logger.info(
                f"{request_prefix} Starting step: {step_name} with params: {safe_kwargs}"
            )
        else:
            self.logger.info(f"{request_prefix} Starting step: {step_name}")
        return step_start_time

    def log_step_end(self, step_name: str, success: bool = True, **kwargs):
        """Log the end of a processing step with timing"""
        end_time = time.time()
        start_key = f"{step_name}_start"

        if start_key in self.step_times:
            duration = end_time - self.step_times[start_key]
            self.step_times[f"{step_name}_duration"] = duration

            status = "completed" if success else "failed"
            # Filter out sensitive information
            safe_kwargs = self._filter_sensitive_info(kwargs)
            request_prefix = f"[{self.request_id}]" if self.request_id else ""

            if safe_kwargs:
                self.logger.info(
                    f"{request_prefix} Step {step_name} {status} in {duration:.3f}s with results: {safe_kwargs}"
                )
            else:
                self.logger.info(
                    f"{request_prefix} Step {step_name} {status} in {duration:.3f}s"
                )
        else:
            request_prefix = f"[{self.request_id}]" if self.request_id else ""
            self.logger.warning(
                f"{request_prefix} No start time recorded for step: {step_name}"
            )

    @contextmanager
    def log_step(self, step_name: str, **kwargs):
        """Context manager for logging a step with automatic timing"""
        self.log_step_start(step_name, **kwargs)
        success = False
        try:
            yield
            success = True
        except Exception as e:
            self.log_error(f"Step {step_name} failed", e, **kwargs)
            raise
        finally:
            self.log_step_end(step_name, success=success)

    def log_service_call(
        self,
        service_name: str,
        operation: str,
        duration: float,
        success: bool,
        **kwargs,
    ):
        """Log service call results with timing"""
        status = "success" if success else "failure"
        # Filter out sensitive information
        safe_kwargs = self._filter_sensitive_info(kwargs)
        request_prefix = f"[{self.request_id}]" if self.request_id else ""

        if safe_kwargs:
            self.logger.info(
                f"{request_prefix} Service call: {service_name}.{operation} {status} in {duration:.3f}s with data: {safe_kwargs}"
            )
        else:
            self.logger.info(
                f"{request_prefix} Service call: {service_name}.{operation} {status} in {duration:.3f}s"
            )

    def log_error(self, message: str, error: Exception, **kwargs):
        """Log error with stack trace and context"""
        # Filter out sensitive information
        safe_kwargs = self._filter_sensitive_info(kwargs)
        request_prefix = f"[{self.request_id}]" if self.request_id else ""

        error_msg = (
            f"{request_prefix} {message}: {str(error)} [Type: {type(error).__name__}]"
        )
        if safe_kwargs:
            error_msg += f" with context: {safe_kwargs}"

        self.logger.error(error_msg, exc_info=error)

    def log_request_complete(self, success: bool, **kwargs):
        """Log request completion with total timing"""
        if self.start_time:
            total_duration = time.time() - self.start_time
            status = "completed" if success else "failed"

            # Filter out sensitive information
            safe_kwargs = self._filter_sensitive_info(kwargs)
            step_durations = self._get_step_durations()
            request_prefix = f"[{self.request_id}]" if self.request_id else ""

            log_parts = [f"{request_prefix} Request {status} in {total_duration:.3f}s"]
            if step_durations:
                log_parts.append(f"step_timings: {step_durations}")
            if safe_kwargs:
                log_parts.append(f"results: {safe_kwargs}")

            self.logger.info(" | ".join(log_parts))
        else:
            request_prefix = f"[{self.request_id}]" if self.request_id else ""
            self.logger.warning(
                f"{request_prefix} No start time recorded for request completion"
            )

    def _get_step_durations(self) -> dict[str, float]:
        """Get all step durations"""
        return {
            key.replace("_duration", ""): value
            for key, value in self.step_times.items()
            if key.endswith("_duration")
        }

    def _filter_sensitive_info(self, data: dict[str, Any]) -> dict[str, Any]:
        """Filter out sensitive information from log data"""
        if not isinstance(data, dict):
            return {}

        # List of sensitive keys to filter out
        sensitive_keys = {
            "password",
            "token",
            "key",
            "secret",
            "auth",
            "authorization",
            "api_key",
            "access_token",
            "refresh_token",
            "private_key",
            "credential",
            "credentials",
        }

        # List of sensitive query parameters
        sensitive_params = {
            "token",
            "api_key",
            "key",
            "secret",
            "auth",
            "authorization",
            "access_token",
            "refresh_token",
            "password",
            "credential",
        }

        filtered_data = {}
        for key, value in data.items():
            key_lower = key.lower()

            # Check if key contains sensitive information
            if any(sensitive_key in key_lower for sensitive_key in sensitive_keys):
                filtered_data[key] = "[REDACTED]"
            elif isinstance(value, str):
                # Check if this is a URL that might contain sensitive query parameters
                if key_lower == "url" and ("?" in value or "&" in value):
                    filtered_data[key] = self._filter_url_params(
                        value, sensitive_params
                    )
                elif len(value) > 100:
                    # Truncate very long strings to prevent log bloat
                    filtered_data[key] = value[:100] + "...[TRUNCATED]"
                else:
                    filtered_data[key] = value
            else:
                filtered_data[key] = value

        return filtered_data

    def _filter_url_params(self, url: str, sensitive_params: set) -> str:
        """Filter sensitive parameters from URL query string"""
        try:
            from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

            parsed = urlparse(url)
            if not parsed.query:
                return url

            # Parse query parameters
            query_params = parse_qs(parsed.query, keep_blank_values=True)

            # Filter sensitive parameters
            filtered_params = {}
            for param_name, param_values in query_params.items():
                if any(
                    sensitive_param in param_name.lower()
                    for sensitive_param in sensitive_params
                ):
                    filtered_params[param_name] = ["[REDACTED]"]
                else:
                    filtered_params[param_name] = param_values

            # Reconstruct URL
            filtered_query = urlencode(filtered_params, doseq=True)
            filtered_parsed = parsed._replace(query=filtered_query)
            return urlunparse(filtered_parsed)

        except Exception:
            # If URL parsing fails, just truncate the URL after the first ?
            if "?" in url:
                return url.split("?")[0] + "?[FILTERED_PARAMS]"
            return url


# Initialize logging when module is imported
setup_logging()
