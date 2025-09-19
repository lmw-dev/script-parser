#!/usr/bin/env python3
"""
Demonstration script for performance monitoring and logging functionality.
"""

import asyncio

from .logging_config import PerformanceLogger, generate_request_id
from .performance_monitoring import create_service_tracker


async def demo_performance_monitoring():
    """Demonstrate the performance monitoring capabilities"""

    print("=== Performance Monitoring Demo ===\n")

    # Generate a request ID
    request_id = generate_request_id()
    print(f"Generated Request ID: {request_id}")

    # Create performance logger
    perf_logger = PerformanceLogger("demo.workflow")
    perf_logger.set_request_id(request_id)

    # Start a request
    perf_logger.start_request(
        "demo_workflow", workflow_type="demonstration", user_id="demo_user"
    )

    # Simulate workflow steps
    with perf_logger.log_step("initialization", component="demo"):
        await asyncio.sleep(0.1)  # Simulate initialization time

    # Simulate service calls with tracking
    with perf_logger.log_step("external_service_calls"):
        # Mock service call 1
        async with create_service_tracker("DemoService", "fetch_data", perf_logger):
            await asyncio.sleep(0.2)  # Simulate service call

        # Mock service call 2 with failure
        try:
            async with create_service_tracker(
                "DemoService", "process_data", perf_logger
            ):
                await asyncio.sleep(0.1)
                raise ValueError("Simulated service failure")
        except ValueError as e:
            perf_logger.log_error(
                "Service processing failed",
                e,
                service="DemoService",
                operation="process_data",
            )

    # Simulate data processing
    with perf_logger.log_step(
        "data_processing", records_count=1000, processing_mode="batch"
    ):
        await asyncio.sleep(0.15)

    # Simulate response preparation
    with perf_logger.log_step("response_preparation"):
        await asyncio.sleep(0.05)

    # Complete the request
    perf_logger.log_request_complete(
        success=True, records_processed=1000, response_size="2.5KB"
    )

    print(f"\n=== Demo completed for request {request_id} ===")


def demo_sensitive_data_filtering():
    """Demonstrate sensitive data filtering"""

    print("\n=== Sensitive Data Filtering Demo ===\n")

    perf_logger = PerformanceLogger("demo.security")
    perf_logger.set_request_id("security-demo")

    # Test with sensitive data
    perf_logger.start_request(
        "security_test",
        api_key="secret_key_123",  # Should be redacted
        password="user_password",  # Should be redacted
        user_name="demo_user",  # Should be visible
        token="bearer_token_456",
    )  # Should be redacted

    # Test URL filtering
    perf_logger.log_step_start(
        "url_processing",
        url="https://api.example.com/data?api_key=secret123&token=abc456&user_id=12345",
    )

    perf_logger.log_step_end(
        "url_processing",
        success=True,
        result_url="https://result.example.com/output?access_token=xyz789&data=processed",
    )

    # Test service call with sensitive data
    perf_logger.log_service_call(
        "AuthService",
        "authenticate",
        0.1,
        True,
        username="demo_user",  # Should be visible
        password="secret_pass",  # Should be redacted
        api_key="key_123",  # Should be redacted
        session_id="sess_456",
    )  # Should be visible

    perf_logger.log_request_complete(
        success=True,
        access_token="final_token_789",  # Should be redacted
        user_id="12345",  # Should be visible
        session_duration=120,
    )  # Should be visible

    print("=== Sensitive data filtering demo completed ===")


def demo_error_logging():
    """Demonstrate error logging with stack traces"""

    print("\n=== Error Logging Demo ===\n")

    perf_logger = PerformanceLogger("demo.errors")
    perf_logger.set_request_id("error-demo")

    perf_logger.start_request("error_handling_demo")

    # Simulate different types of errors
    try:
        with perf_logger.log_step("validation_step"):
            raise ValueError("Invalid input data: missing required field 'user_id'")
    except ValueError as e:
        perf_logger.log_error(
            "Validation failed",
            e,
            input_data="[SAMPLE_DATA]",
            validation_rule="required_fields",
        )

    try:
        with perf_logger.log_step("network_step"):
            raise ConnectionError("Failed to connect to external service")
    except ConnectionError as e:
        perf_logger.log_error(
            "Network operation failed",
            e,
            service_url="https://api.example.com",
            timeout=30,
            retry_count=3,
        )

    try:
        with perf_logger.log_step("processing_step"):
            raise RuntimeError("Unexpected processing error in data transformation")
    except RuntimeError as e:
        perf_logger.log_error(
            "Processing failed", e, batch_size=100, processing_stage="transformation"
        )

    perf_logger.log_request_complete(success=False, error_count=3, partial_results=True)

    print("=== Error logging demo completed ===")


async def main():
    """Run all demonstrations"""
    print("Starting Performance Monitoring Demonstrations...\n")

    # Run the async demo
    await demo_performance_monitoring()

    # Run sync demos
    demo_sensitive_data_filtering()
    demo_error_logging()

    print("\n=== All demonstrations completed ===")
    print("\nKey features demonstrated:")
    print("✓ Request ID generation and tracking")
    print("✓ Step-by-step performance monitoring")
    print("✓ Service call tracking with success/failure")
    print("✓ Automatic timing measurements")
    print("✓ Sensitive data filtering in logs")
    print("✓ URL parameter filtering")
    print("✓ Error logging with stack traces")
    print("✓ Request completion summaries")


if __name__ == "__main__":
    asyncio.run(main())
