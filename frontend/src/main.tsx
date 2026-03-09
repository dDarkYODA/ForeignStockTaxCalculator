import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

// Initialize OpenTelemetry
import { initializeOTel } from './services/otel'
initializeOTel()

import App from './App.tsx'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)
