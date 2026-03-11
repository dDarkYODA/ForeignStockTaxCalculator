# Multi-Agent AI Code Review & Auto-Fix System

This repository implements an automated pipeline where AI agents collaborate to review PRs, resolve comments from CodeRabbit, and maintain code quality.

## System Architecture

The system consists of three specialized AI agents, whose instructions are defined in the `.ai/` directory:

1.  **Review-Fix Agent** (`.ai/review-fix-agent.md`): Automatically resolves CodeRabbit review comments by generating and applying code patches.
2.  **Test Agent** (`.ai/test-agent.md`): Ensures test coverage for modified code and validates fixes.
3.  **Architecture Agent** (`.ai/architecture-agent.md`): Maintains system design quality by analyzing cross-module impacts and preferring structural refactors.

## How It Works

1.  **Trigger**: The system is triggered by GitHub Actions on PR creation, updates, or when CodeRabbit submits a review/comment.
2.  **Agent Runner**: A Python script (`scripts/agent_runner.py`) executes the agent loop:
    *   Fetches unresolved CodeRabbit comments via the GitHub API.
    *   Uses OpenAI (GPT-4o) to generate fixes based on the instructions and code context.
    *   Applies fixes to the PR branch.
    *   Runs the project's test suite to verify the changes.
    *   Commits and pushes the improvements back to the repository.
3.  **Loop**: The process repeats until no unresolved CodeRabbit comments remain, or until a maximum number of iterations is reached.

## Configuration

*   **GitHub Workflow**: `.github/workflows/ai-agent-loop.yml` defines the automation triggers and environment.
*   **Secrets Required**:
    *   `GITHUB_TOKEN`: Provided by GitHub Actions automatically.
    *   `OPENAI_API_KEY`: Must be configured in the repository secrets for the agents to use LLMs.

## Maintenance

To update agent behavior, modify the instruction files in `.ai/`. For changes to the integration logic (e.g., how comments are fetched or how tests are run), update `scripts/agent_runner.py`.
