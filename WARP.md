# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

ScriptParser (脚本快拆) is an AI-powered intelligent script analysis tool that uses a **"Web Application + AI Coprocessor"** separated architecture:

- **Web Application**: Full-stack Next.js 14 application handling UI and business logic
- **AI Coprocessor**: FastAPI-based dedicated AI service for audio transcription and intelligent analysis
- **AI Capabilities**: Integrates Aliyun ASR and DeepSeek/Kimi LLM services

## Development Commands

### Quick Setup

```bash
# Install dependencies
pnpm install

# Start development (both services)
pnpm dev:web                    # Web application only
pnpm --filter web dev          # Alternative web dev command

# Build
pnpm build:web                 # Build web application
pnpm --filter web build       # Alternative build command

# Docker development
pnpm docker:up                 # Start all services with Docker
pnpm docker:down               # Stop all services
pnpm docker:build              # Build and push Docker images
```

### Web Application (Next.js)

```bash
cd apps/web

# Development
pnpm dev                       # Start dev server with Turbopack
pnpm build                     # Build for production
pnpm start                     # Start production server
pnpm lint                      # Run ESLint
pnpm format                    # Format code with Prettier
pnpm format:check              # Check code formatting

# Testing
pnpm test                      # Run tests
pnpm test:watch                # Run tests in watch mode
pnpm test:coverage             # Run tests with coverage
```

### AI Coprocessor (FastAPI)

```bash
cd apps/coprocessor

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Development
python -m uvicorn app.main:app --reload --port 8000

# Code quality
ruff check --fix .             # Lint and fix Python code
ruff format .                  # Format Python code

# Testing
pytest                         # Run tests
pytest --asyncio-mode=auto     # Run async tests
```

### Build and Deployment

```bash
# Format all code
./scripts/format.sh            # Format both web and coprocessor code

# Docker build and deploy
./scripts/build-push.sh        # Build Docker images
REGISTRY=your-registry.com TAG=v1.0.0 ./scripts/build-push.sh  # Build and push

# Docker Compose operations
docker-compose up --build -d   # Build and start all services
docker-compose ps              # Check service status
docker-compose logs -f         # View logs (all services)
docker-compose logs -f web     # View specific service logs
docker-compose restart         # Restart services
docker-compose down            # Stop all services
```

### Single Test Execution

```bash
# Web application tests
cd apps/web
npx jest src/app/page.test.tsx                    # Run specific test file
npx jest --testNamePattern="specific test name"   # Run specific test

# Python tests
cd apps/coprocessor
pytest tests/test_specific_module.py              # Run specific test file
pytest -k "test_specific_function"                # Run specific test function
```

## Architecture Overview

### Monorepo Structure

- **`apps/web/`**: Next.js 15 application with App Router
  - Uses shadcn/ui components with Tailwind CSS
  - Zustand for state management  
  - TypeScript with strict type checking
- **`apps/coprocessor/`**: FastAPI Python service
  - Handles audio transcription (Aliyun ASR)
  - LLM analysis (DeepSeek/Kimi integration)
  - Modular service architecture with error handling
- **`scripts/`**: Build and deployment scripts
- **`nginx/`**: Reverse proxy configuration for unified API gateway

### Service Communication

```
User Browser → Nginx (Port 80)
├── "/" → Web App (Next.js:3000)
└── "/api/*" → AI Coprocessor (FastAPI:8000)
```

### Key Architecture Patterns

**Web Application (Next.js)**:
- App Router with server and client components
- Form validation with URL extraction and file validation
- State management via Zustand store
- Components organized in feature-based structure
- API integration with typed request/response interfaces

**AI Coprocessor (FastAPI)**:
- **WorkflowOrchestrator**: Central coordinator for processing pipelines
- **Service Layer**: Modular services (ASR, LLM, File Handler, OSS Uploader)
- **Error Handling**: Structured exception hierarchy with centralized handling
- **Performance Monitoring**: Built-in logging and time tracking
- **Lazy Initialization**: Services initialized on-demand for better startup performance

### State Management

The web application uses Zustand for client state with the following pattern:

```typescript
// Key store: apps/web/src/stores/app-store.ts
interface AppState {
  processingRequest: VideoParseRequest | null
  processingResult: ProcessingResult | null
  startProcessing: (request: VideoParseRequest) => void
}
```

### API Design Standards

All APIs follow a unified response format:
```typescript
interface ApiResponse<T> {
  code: number;        // Business status code (0 = success)
  success: bool;       // Operation success flag
  data: T | null;      // Response data
  message: string;     // Response message
}
```

## Development Guidelines

### Code Standards

**General Principles** (from .cursor/rules/):
- Clarity over cleverness - write explicit, readable code
- Single Responsibility Principle - functions do one thing well
- DRY principle - extract reusable components and utilities
- Comment the "why", not the "what"
- Never ignore errors silently

**TypeScript/Next.js**:
- Use descriptive, unambiguous naming (camelCase for variables/functions)
- Prefer immutable data patterns
- Server/Client component separation in App Router
- Type-safe API communication

**Python/FastAPI**:
- Follow PEP standards with Ruff formatting
- Use type hints throughout
- Custom exception classes for structured error handling  
- Async/await patterns for I/O operations
- Service-oriented architecture with dependency injection

### Error Handling

**Frontend**: Graceful error states with toast notifications and fallback UI

**Backend**: Structured exception hierarchy:
```python
class APIException(Exception):
    def __init__(self, code: int, message: str = None)

class InvalidParameterError(APIException): # 2001
class NotAuthenticatedError(APIException): # 4001  
```

### Testing Strategy

- **Unit Tests**: Jest for React components, pytest for Python services
- **Integration Tests**: API endpoint testing with realistic payloads
- **Error Scenarios**: Test both happy path and error conditions
- **Async Testing**: Use proper async test patterns for FastAPI endpoints

## Environment Configuration

### Required Environment Variables

**AI Coprocessor** (`apps/coprocessor/.env`):
```bash
# Aliyun ASR API
ALIYUN_ASR_API_KEY=your_api_key
ALIYUN_ASR_API_SECRET=your_api_secret

# DeepSeek/Kimi LLM
DEEPSEEK_API_KEY=your_deepseek_key

# Service Configuration  
HOST=0.0.0.0
PORT=8000
DEBUG=false
```

**Web Application**:
```bash
NODE_ENV=production
NEXT_PUBLIC_API_URL=http://localhost/api  # Points to coprocessor via nginx
```

## Production Deployment

The application is designed for containerized deployment with Docker Compose providing:

- **Nginx**: Reverse proxy and load balancer (Port 80)
- **Web App**: Next.js application in production mode  
- **Coprocessor**: FastAPI service with Python 3.12
- **Networking**: Bridge network for inter-service communication
- **Health Checks**: Available at `/api/health`

Services communicate internally through Docker networking while Nginx provides the unified external interface.