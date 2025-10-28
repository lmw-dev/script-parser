# GEMINI.md

## Project Overview

This is a monorepo for the "ScriptParser" application, an intelligent script analysis tool based on AI. The project follows a separated architecture with a "Web application + AI coprocessor" model.

-   **Web Application**: A full-stack web application built with Next.js 14, responsible for the user interface and business logic. It uses TypeScript, Tailwind CSS, and shadcn/ui for the frontend.
-   **AI Coprocessor**: A dedicated AI service built with FastAPI, which handles audio-to-text transcription and intelligent analysis. It integrates with Alibaba Cloud ASR and DeepSeek/Kimi LLM.

The project is containerized using Docker and uses pnpm for monorepo package management.

## Building and Running

### Docker (Recommended)

1.  **Configure environment variables**:
    ```bash
    cp apps/coprocessor/.env.example apps/coprocessor/.env
    # Edit apps/coprocessor/.env to add your API keys
    ```

2.  **Start services**:
    ```bash
    docker-compose up --build -d
    ```

### Local Development

1.  **Install dependencies**:
    ```bash
    pnpm install
    ```

2.  **Run the Web App**:
    ```bash
    pnpm --filter web dev
    ```

3.  **Run the AI Coprocessor**:
    ```bash
    cd apps/coprocessor
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --port 8000
    ```

## Development Conventions

-   **Code Formatting**: The project uses Prettier for the web app and Ruff for the Python coprocessor. A formatting script is available at `./scripts/format.sh`.
-   **Linting**: ESLint is used for the web app, and Ruff is used for the coprocessor.
-   **Commit Messages**: The project follows the Conventional Commits specification. Commitlint and Husky are used to enforce this standard.
-   **Testing**: The web app uses Jest and React Testing Library for unit and integration tests. The AI coprocessor uses pytest.
