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
