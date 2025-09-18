# Requirements Document

## Introduction

This feature implements a URL parsing module for the coprocessor application. The module provides a unified interface for parsing video sharing URLs from different platforms, starting with Douyin (TikTok China) support. The parser extracts video metadata and download URLs from platform-specific sharing links.

## Requirements

### Requirement 1

**User Story:** As a developer, I want a ShareURLParser class that can identify and route different platform URLs, so that I can extend support for multiple video platforms systematically.

#### Acceptance Criteria

1. WHEN ShareURLParser.parse() receives a share text containing a URL THEN the system SHALL identify the platform based on domain name
2. WHEN the platform is identified THEN the system SHALL route to the appropriate platform-specific parser method
3. WHEN the URL contains douyin.com domain THEN the system SHALL call _parse_douyin method
4. WHEN the URL contains xiaohongshu.com domain THEN the system SHALL call _parse_xiaohongshu method
5. WHEN no URL is found in the text THEN the system SHALL raise URLParserError

### Requirement 2

**User Story:** As a user, I want to parse Douyin sharing links to extract video information, so that I can access the video content programmatically.

#### Acceptance Criteria

1. WHEN _parse_douyin receives a valid Douyin URL THEN the system SHALL extract the video ID from the URL
2. WHEN the video ID is extracted THEN the system SHALL fetch the video page HTML content
3. WHEN the HTML is fetched THEN the system SHALL parse the _ROUTER_DATA JSON object
4. WHEN the JSON is parsed THEN the system SHALL extract video title and download URL
5. WHEN extraction is successful THEN the system SHALL return a VideoInfo object with platform='douyin'

### Requirement 3

**User Story:** As a developer, I want clear error handling for unsupported platforms, so that I can understand what functionality is not yet implemented.

#### Acceptance Criteria

1. WHEN _parse_xiaohongshu is called THEN the system SHALL raise NotImplementedError with descriptive message
2. WHEN HTML parsing fails for Douyin THEN the system SHALL raise URLParserError with clear error message
3. WHEN network requests fail THEN the system SHALL handle exceptions gracefully
4. WHEN invalid URLs are provided THEN the system SHALL raise appropriate URLParserError

### Requirement 4

**User Story:** As a developer, I want comprehensive unit tests for the URL parser, so that I can ensure reliability and catch regressions.

#### Acceptance Criteria

1. WHEN tests are executed THEN the system SHALL have unit tests for successful Douyin parsing with mocked HTTP requests
2. WHEN tests are executed THEN the system SHALL have unit tests for NotImplementedError on Xiaohongshu URLs
3. WHEN tests are executed THEN the system SHALL have unit tests for URLParserError when no URL is found
4. WHEN tests are executed THEN the system SHALL have unit tests for parsing failures with invalid HTML
5. WHEN all tests run THEN they SHALL achieve 100% pass rate

### Requirement 5

**User Story:** As an API user, I want the URL parser integrated into the /api/parse endpoint, so that I can use URL parsing functionality through the REST API.

#### Acceptance Criteria

1. WHEN the /api/parse endpoint receives a JSON request with URL THEN it SHALL use ShareURLParser to process the URL
2. WHEN URL parsing succeeds THEN the endpoint SHALL return VideoParseResponse with parsed video information
3. WHEN URLParserError occurs THEN the endpoint SHALL return 400 status code with error message
4. WHEN NotImplementedError occurs THEN the endpoint SHALL return 501 status code indicating not implemented
5. WHEN the parser is integrated THEN existing API functionality SHALL remain unchanged