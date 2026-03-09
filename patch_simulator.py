import sys

def main():
    content = ""
    with open("frontend/src/pages/SimulatorPage.tsx", "r") as f:
        content = f.read()

    new_imports = """import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { simulateTrade, getPortfolio } from '../services/api';
"""
    content = content.replace("import { useState } from 'react';\nimport { simulateTrade } from '../services/api';", new_imports)

    state_setup = """  const [result, setResult] = useState<any>(null);

  const [hasData, setHasData] = useState<boolean | null>(null);

  useEffect(() => {
    const checkData = async () => {
      try {
        const portfolio = await getPortfolio();
        setHasData(portfolio.holdings && portfolio.holdings.length > 0);
      } catch (err) {
        setHasData(false);
      }
    };
    checkData();
  }, []);

  const handleSimulate = async (e: React.FormEvent) => {"""
    content = content.replace("  const [result, setResult] = useState<any>(null);\n\n  const handleSimulate = async (e: React.FormEvent) => {", state_setup)

    empty_state = """  if (hasData === false) {
    return (
      <div className="max-w-2xl mx-auto p-12 bg-white rounded-xl shadow-sm border border-gray-100 mt-10 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">No Portfolio Data Found</h2>
        <p className="text-gray-600 mb-6">Upload a broker CSV file to view your portfolio and simulate trades.</p>
        <Link to="/" className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
          Upload Data
        </Link>
      </div>
    );
  }

  return ("""
    content = content.replace("  return (", empty_state)

    with open("frontend/src/pages/SimulatorPage.tsx", "w") as f:
        f.write(content)

if __name__ == "__main__":
    main()
