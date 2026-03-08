# OpenTelemetry Instrumentation Guide

This project now includes OpenTelemetry instrumentation for both the frontend (React) and backend (FastAPI) applications.

## Frontend (React + Vite)

### What's Instrumented
- HTTP requests (Fetch API and XMLHttpRequest)
- Page performance metrics
- Frontend errors

### Setup

1. **Install Dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Configure Environment Variables**
   Copy `.env.example` to `.env.local` (or add to your deployment environment):
   ```bash
   REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.kubiks.app/v1/traces
   REACT_APP_OTEL_EXPORTER_OTLP_HEADERS=your-api-key-here
   ```
   
   Replace `your-api-key-here` with your actual Kubiks API key from `x-kubiks-key=kubiks_546affc804de9e2255f0311c59031e0a9c7377b25d53e1d6a43c9353a6afbd3b`

3. **Build**
   ```bash
   npm run build
   ```

## Backend (FastAPI + Python)

### What's Instrumented
- HTTP requests to FastAPI endpoints
- HTTP requests made by the application (httpx, requests)
- All FastAPI route handlers

### Setup

1. **Install Dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables**
   Create a `.env` file (or add to your deployment environment):
   ```bash
   OTEL_EXPORTER_OTLP_ENDPOINT=https://ingest.kubiks.app
   OTEL_EXPORTER_OTLP_HEADERS=x-kubiks-key=your-api-key-here
   OTEL_SERVICE_NAME=foreign-stock-tax-calculator-backend
   ENVIRONMENT=production
   ```
   
   Replace `your-api-key-here` with your actual Kubiks API key.

3. **Run**
   ```bash
   uvicorn backend.main:app --reload
   ```

## Environment Variables Reference

### Frontend (React)
- `REACT_APP_OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry endpoint (default: `https://ingest.kubiks.app/v1/traces`)
- `REACT_APP_OTEL_EXPORTER_OTLP_HEADERS` - Authentication header with your API key

### Backend (FastAPI)
- `OTEL_EXPORTER_OTLP_ENDPOINT` - OpenTelemetry endpoint (default: `https://ingest.kubiks.app`)
- `OTEL_EXPORTER_OTLP_HEADERS` - Authentication header with your API key
- `OTEL_SERVICE_NAME` - Service name (default: `foreign-stock-tax-calculator-backend`)
- `ENVIRONMENT` - Environment name (e.g., `production`, `staging`, `development`)

## Getting Your API Key

Your Kubiks API key is: `kubiks_546affc804de9e2255f0311c59031e0a9c7377b25d53e1d6a43c9353a6afbd3b`

Use it in the format:
```
x-kubiks-key=kubiks_546affc804de9e2255f0311c59031e0a9c7377b25d53e1d6a43c9353a6afbd3b
```

## Verifying the Setup

Once configured and deployed:

1. **Generate some traffic** by using your application (upload files, calculate taxes, etc.)
2. **Check Kubiks Dashboard** to see traces appearing from both frontend and backend
3. **View trace details** to see the spans for HTTP requests and calculations

## Files Added/Modified

### Frontend
- `frontend/src/otel.ts` - OpenTelemetry initialization and instrumentation
- `frontend/src/main.tsx` - Updated to import otel initialization
- `frontend/.env.example` - Environment variable template

### Backend
- `backend/otel.py` - OpenTelemetry initialization and instrumentation
- `backend/main.py` - Updated to initialize OpenTelemetry on startup
- `backend/requirements.txt` - Added OpenTelemetry dependencies
- `backend/.env.example` - Environment variable template

## Next Steps

1. Copy the environment variable examples to your actual `.env` files
2. Add your Kubiks API key to the environment variables
3. Deploy both frontend and backend
4. Start monitoring your application in Kubiks dashboard
