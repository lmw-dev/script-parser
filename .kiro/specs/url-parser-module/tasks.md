# Implementation Plan

- [x] 1. Create unit test infrastructure for URL parser module
  - Create test_url_parser.py file in the services directory
  - Set up pytest fixtures for mocking HTTP requests
  - Write comprehensive unit tests covering all scenarios (success, errors, edge cases)
  - Ensure all tests fail initially (test-first approach)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [x] 2. Implement core data models and exceptions
  - Create VideoInfo Pydantic model with required fields
  - Create URLParserError custom exception class
  - Ensure models follow the API contract from the design
  - _Requirements: 5.1, 3.3_

- [x] 3. Implement ShareURLParser class with platform routing
  - Create ShareURLParser class with parse method
  - Implement URL extraction from text using regex
  - Implement platform identification based on domain
  - Add routing logic to call appropriate platform-specific parsers
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [x] 4. Implement Douyin parsing logic
  - Create _parse_douyin method with full implementation
  - Implement HTTP request handling with httpx
  - Implement HTML parsing to extract _ROUTER_DATA JSON
  - Extract video metadata (ID, title, download URL) from JSON
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 5. Implement placeholder for Xiaohongshu and error handling
  - Create _parse_xiaohongshu method that raises NotImplementedError
  - Implement comprehensive error handling for all failure scenarios
  - Ensure proper exception propagation with clear error messages
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [x] 6. Integrate URL parser into /api/parse endpoint
  - Import ShareURLParser in main.py
  - Modify /api/parse endpoint to use URL parser for JSON requests
  - Add proper error handling with appropriate HTTP status codes
  - Ensure existing functionality remains unchanged
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 7. Verify implementation and run comprehensive tests
  - Run unit tests to ensure 100% pass rate
  - Test integration with API endpoint
  - Verify error handling and status codes
  - Run code quality checks (ruff)
  - _Requirements: 4.5, 5.5_