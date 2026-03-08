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
