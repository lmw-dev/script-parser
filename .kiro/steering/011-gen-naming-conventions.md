---
inclusion: fileMatch
fileMatchPattern: ['**/*.tsx', '**/*.ts', '**/*.py']
---

# Rule: Unified Naming Conventions (V2.1)

## Description
This document defines the strict naming conventions for all code across all projects. The AI must adhere to these rules at all times. These rules are based on official framework conventions (Next.js) and authoritative industry style guides (PEP 8, Google, Airbnb).

---

## 1. TypeScript / JavaScript Naming Conventions (web project)

### 1.1 Code Identifiers (Variables, Functions, etc.)
- **Variables, Functions, Props, & Methods:** Use `camelCase`.
- **Classes, Interfaces, Type Aliases, Enums:** Use `PascalCase`.
- **Constants (reused, hardcoded values):** Use `UPPER_CASE_SNAKE_CASE`.

### 1.2 File Names
- **Next.js Special Files:** Use `lowercase`.
  - **Required:** `page.tsx`, `layout.tsx`, `loading.tsx`, `error.tsx`, `route.ts`
- **React Component Files:** Use `PascalCase.tsx`.
  - **Definition:** A file is considered a Component File if its **primary default export** is a React component.
- **Type Definition Files:** `kebab-case.types.ts`.
  - **Definition:** Files containing **only** `type` or `interface` exports.
- **All Other Code Files (hooks, utils, services):** Use `kebab-case.ts`.

### 1.3 API Route Files
- **Next.js App Router API Routes:** Must be named `route.ts` and placed within a descriptive API path folder.

---

## 2. Python Naming Conventions (ai project)
*Based on PEP 8 Style Guide.*

- **Variables, Functions, Methods, and Modules (Files):** Use `snake_case`.
- **Classes:** Use `PascalCase` (CapWords).
- **Constants:** Use `UPPER_CASE_SNAKE_CASE`.
- **Private Attributes:** Use a single leading underscore: `self._internal_state`.

---

## 3. Database Naming Conventions (PostgreSQL)
*Applies to all database objects.*

- **Tables, Columns, Views, Functions:** Use `snake_case`.