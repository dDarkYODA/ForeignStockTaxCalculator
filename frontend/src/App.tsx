import { useState } from 'react';
import './index.css';

interface Transaction {
  date: string;
  transaction_type: string;
  symbol: string;
  shares: number;
  price: number;
  currency: string;
  broker: string;
  reference_id?: string;
}

interface TaxResult {
  date: string;
  symbol: string;
  shares: number;
  cost_inr: number;
  sale_inr: number;
  gain_inr: number;
  holding_type: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [broker, setBroker] = useState<string>('shareworks');
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [taxResults, setTaxResults] = useState<TaxResult[]>([]);
  const [loading, setLoading] = useState(false);

  const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    const formData = new FormData();
    formData.append('file', file);
    formData.append('broker', broker);

    try {
      const res = await fetch(`${API_URL}/upload?broker=${broker}`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      setTransactions(data);
    } catch (err) {
      console.error(err);
      alert('Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculate = async () => {
    if (transactions.length === 0) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/calculate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transactions),
      });
      const data = await res.json();
      setTaxResults(data);
    } catch (err) {
      console.error(err);
      alert('Calculation failed');
    } finally {
      setLoading(false);
    }
  };

  const exportCSV = () => {
    const headers = ['date', 'symbol', 'shares', 'cost_inr', 'sale_inr', 'gain_inr', 'holding_type'];
    const csvContent = [
      headers.join(','),
      ...taxResults.map(row => 
        [row.date, row.symbol, row.shares, row.cost_inr, row.sale_inr, row.gain_inr, row.holding_type].join(',')
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = 'tax_results.csv';
    link.click();
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        <h1 className="text-3xl font-bold text-gray-900">Foreign Stock Tax Calculator</h1>
        
        {/* Upload Section */}
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">1. Upload Transactions</h2>
          <div className="flex items-center space-x-4">
            <select 
              value={broker} 
              onChange={e => setBroker(e.target.value)}
              className="border p-2 rounded"
            >
              <option value="shareworks">Morgan Stanley Shareworks</option>
              <option value="fidelity">Fidelity</option>
              <option value="unknown">Unknown (AI Infer Schema)</option>
            </select>
            <input 
              type="file" 
              accept=".csv" 
              onChange={e => setFile(e.target.files?.[0] || null)}
              className="border p-2 rounded"
            />
            <button 
              onClick={handleUpload}
              disabled={!file || loading}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Processing...' : 'Upload & Parse'}
            </button>
          </div>
        </div>

        {/* Transactions Preview */}
        {transactions.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">2. Transaction Preview</h2>
              <button 
                onClick={handleCalculate}
                disabled={loading}
                className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 disabled:opacity-50"
              >
                Calculate Capital Gains
              </button>
            </div>
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-2">Date</th>
                  <th className="p-2">Type</th>
                  <th className="p-2">Symbol</th>
                  <th className="p-2">Shares</th>
                  <th className="p-2">Price</th>
                  <th className="p-2">Currency</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map((t, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{t.date}</td>
                    <td className="p-2">{t.transaction_type}</td>
                    <td className="p-2">{t.symbol}</td>
                    <td className="p-2">{t.shares}</td>
                    <td className="p-2">{t.price}</td>
                    <td className="p-2">{t.currency}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Results */}
        {taxResults.length > 0 && (
          <div className="bg-white p-6 rounded-lg shadow overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold">3. Capital Gains Results</h2>
              <button 
                onClick={exportCSV}
                className="bg-purple-600 text-white px-4 py-2 rounded hover:bg-purple-700"
              >
                Export CSV
              </button>
            </div>
            <table className="w-full text-left text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="p-2">Sell Date</th>
                  <th className="p-2">Symbol</th>
                  <th className="p-2">Shares</th>
                  <th className="p-2">Cost (INR)</th>
                  <th className="p-2">Sale (INR)</th>
                  <th className="p-2">Gain (INR)</th>
                  <th className="p-2">Type</th>
                </tr>
              </thead>
              <tbody>
                {taxResults.map((r, i) => (
                  <tr key={i} className="border-b">
                    <td className="p-2">{r.date}</td>
                    <td className="p-2">{r.symbol}</td>
                    <td className="p-2">{r.shares}</td>
                    <td className="p-2">₹{r.cost_inr.toFixed(2)}</td>
                    <td className="p-2">₹{r.sale_inr.toFixed(2)}</td>
                    <td className="p-2 font-semibold text-gray-900">₹{r.gain_inr.toFixed(2)}</td>
                    <td className="p-2">
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${r.holding_type === 'LTCG' ? 'bg-blue-100 text-blue-800' : 'bg-orange-100 text-orange-800'}`}>
                        {r.holding_type}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
