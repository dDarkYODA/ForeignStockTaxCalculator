# Foreign Stock Tax Calculator

An AI-driven software repository for an Indian tax rules calculator on foreign stock transactions.

## Purpose

The application allows users to upload stock transaction files from foreign brokers and compute capital gains according to Indian tax rules.

Initially supported brokers:
- Morgan Stanley Shareworks
- Fidelity

If a broker is unsupported, the system uses AI to infer the transaction schema.

## Run Locally

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate`
4. `pip install -r backend/requirements.txt`
5. `cd backend && uvicorn main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

## Rules
- AI agents must not push directly to main.
- Changes must go through Pull Requests.
- Never embed API keys or tokens in code.

## Braintrust Integration

This project uses **Braintrust** to evaluate, monitor, and improve AI-driven schema inference for unsupported broker CSV files.

### What Braintrust Does Here
- **Monitoring**: It logs every AI schema inference call, capturing the CSV snippet, the generated prompt, the inferred mapping, and relevant metadata.
- **Evaluation**: The project includes a framework to test the schema inference against known expected outputs to prevent regressions and improve accuracy over time.

**Safety Rule**: Braintrust *only* monitors the AI-based schema inference. It does **NOT** influence or interact with the core tax calculations, FIFO matching, or FX conversions, which remain strictly deterministic.

### Running Evaluations Locally
To evaluate schema inference locally against the dataset:
1. Ensure `braintrust` is installed (included in `backend/requirements.txt`).
2. Set your API key: `export BRAINTRUST_API_KEY=your_key_here`
3. Run the evaluation script:
   ```bash
   cd backend
   python -m evals.schema_eval
   ```

### CI/CD Integration
Braintrust evaluations run automatically via GitHub Actions (`.github/workflows/ci.yml`) on every push and pull request to `main`. This ensures AI parsing quality does not regress.
