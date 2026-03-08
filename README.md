<<<<<<< HEAD
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
=======
# Foreign Stock Tax Calculator (India)

A web application to calculate Indian capital gains tax (LTCG / STCG) on foreign stock transactions.

It supports:
- **Morgan Stanley Shareworks** statement parsing
- **Fidelity** statement parsing
- **Generic Uploads** with an AI-assisted column mapping inference (OpenAI)
- **FIFO (First-In-First-Out)** lot matching
- Automatic foreign exchange conversion using mock SBI TT Buying Rates.

## Tech Stack
- **Frontend**: React, TypeScript, Vite, Tailwind CSS, Lucide React
- **Backend**: Python, FastAPI, SQLAlchemy, Pandas, OpenAI
- **Database**: PostgreSQL (Supabase recommended)

---

## Project Structure

```
foreign-stock-tax-calculator/
├── backend/                  # FastAPI Application
│   ├── api/                  # Endpoints
│   ├── models/               # Database Schemas
│   ├── parsers/              # Broker statement parsers & AI logic
│   ├── services/             # Tax calculation & FX engines
│   ├── main.py               # Application entrypoint
│   └── requirements.txt      # Python dependencies
├── frontend/                 # React UI
│   ├── src/
│   │   ├── components/
│   │   ├── pages/            # Upload, Preview, Results pages
│   │   └── services/         # API integration
│   └── vite.config.ts
├── examples/                 # Sample CSV files for testing
└── README.md
```

---

## Local Development Setup

### 1. Database Setup

1. Create a PostgreSQL database (e.g., via Supabase).
2. The provided code will auto-create the tables using `Base.metadata.create_all()` on startup if they don't exist.

### 2. Backend Setup

1. Navigate to the backend directory: `cd backend`
2. Create a virtual environment and activate it.
3. Install dependencies: `pip install -r requirements.txt`
4. Create a `.env` file in the `backend/` directory:
   ```env
   # Example .env file
   DATABASE_URL=postgresql://postgres.xxxxx:YOUR_PASSWORD@aws-0-us-east-1.pooler.supabase.com:6543/postgres
   OPENAI_API_KEY=your_openai_api_key_here
   ```
5. Start the FastAPI development server: `uvicorn main:app --reload`
   The backend will run on `http://localhost:8000`.

### 3. Frontend Setup

1. Navigate to the frontend directory: `cd frontend`
2. Install dependencies: `npm install`
3. Create a `.env` file in the `frontend/` directory if you need to override the backend URL:
   ```env
   VITE_API_URL=http://localhost:8000/api
   ```
4. Start the Vite development server in development mode.
   The frontend will run on `http://localhost:5173`.

---

## How to Use

1. **Upload Statement**: Go to the homepage and select the broker type (Shareworks, Fidelity, or Generic). Upload one of the sample CSVs from the `examples/` folder.
2. **AI Mapping Confirmation (Generic)**: If you upload a generic file, the backend will call OpenAI to infer the column mappings. Review and confirm the mappings.
3. **View Results**: The engine will parse the transactions, match lots using FIFO, apply FX rates, and compute the gain/loss in INR, classifying it as STCG or LTCG. You can export the results to a CSV file.
>>>>>>> origin/main
