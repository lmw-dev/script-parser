---
inclusion: fileMatch
fileMatchPattern: ['**/*.test.ts', '**/*.test.tsx', '**/test_*.py']
---
# Rule: Testing Guide and Strategy (v2.1)

*Note: This guide defines **how** to write tests. Our core development workflow, `[[SOP - Vibe Coding 端到端开发工作流 V3.0]]`, defines **when** to write them (Test-First).*

## 1. General Testing Principles
- **Test Behavior, Not Implementation:** Tests should verify the public-facing behavior of a function or component, not its internal implementation details. 
- **Clear Descriptions:** Each test case should have a clear, human-readable description of the behavior it is testing. 
- **AAA Pattern:** Structure tests using the Arrange-Act-Assert pattern. 

## 2. Frontend Testing (web - Next.js)
- **Tools:** Use **Vitest** and **React Testing Library (RTL)**. 
- **Focus:** Unit test complex hooks and utilities; integration test user flows. 
- **File Location:** Test files **must** be co-located with the source file they are testing.
  - **Good:** `/components/ui/Button.tsx` and `/components/ui/Button.test.tsx`
- **Querying:** Always prefer user-facing queries like `getByRole` and `getByLabelText`.  Avoid implementation-detail queries like `getByTestId`. 

## 3. Backend Testing (ai - FastAPI)
- **Tools:** Use **Pytest**. 
- **Focus:** The primary focus is **integration testing API endpoints** using FastAPI's `TestClient`.  Unit tests are for complex, isolated business logic. 
- **File Location:** All test files **must** be placed in a top-level `tests/` directory, which mirrors the structure of the `app/` directory.
  - **Good:** Test for `apps/coprocessor/app/services/factory.py` should be at `apps/coprocessor/tests/services/test_factory.py`
- **Dependencies:** Tests should **not** interact with the real database or external APIs. Use mocking/patching to simulate their responses. 