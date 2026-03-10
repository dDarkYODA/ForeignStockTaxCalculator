import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { simulateTrade, getPortfolio } from '../services/api';

import { IndianRupee, PieChart, Activity } from 'lucide-react';

const SimulatorPage: React.FC = () => {
  const [symbol, setSymbol] = useState('');
  const [shares, setShares] = useState<number | ''>('');
  const [price, setPrice] = useState<number | ''>('');
  const [currency, setCurrency] = useState('USD');
  const [date, setDate] = useState(() => new Date().toISOString().split('T')[0]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<any>(null);

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

  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!symbol || !shares || !price || !date || !currency) {
      setError('Please fill in all fields.');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await simulateTrade(symbol.toUpperCase(), Number(shares), Number(price), currency, date);
      setResult(res);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error simulating trade');
    } finally {
      setLoading(false);
    }
  };

  if (hasData === false) {
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

  return (
    <div className="max-w-6xl mx-auto p-6 grid grid-cols-1 md:grid-cols-2 gap-8 mt-10">
      <div className="bg-white p-6 rounded-xl shadow-md border border-gray-100">
        <h2 className="text-2xl font-bold text-gray-800 mb-6 flex items-center">
          <Activity className="mr-3 text-blue-600" /> Trade Simulator
        </h2>

        <form onSubmit={handleSimulate} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Symbol</label>
            <input
              type="text"
              value={symbol}
              onChange={(e) => setSymbol(e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 outline-none uppercase"
              placeholder="e.g., AAPL"
              required
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Shares to Sell</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={shares}
                onChange={(e) => setShares(Number(e.target.value) || '')}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="10"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sale Price</label>
              <input
                type="number"
                step="0.01"
                min="0.01"
                value={price}
                onChange={(e) => setPrice(Number(e.target.value) || '')}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 outline-none"
                placeholder="150.00"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Currency</label>
              <select
                value={currency}
                onChange={(e) => setCurrency(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 outline-none"
              >
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="CHF">CHF</option>
                <option value="INR">INR</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Sale Date</label>
              <input
                type="date"
                value={date}
                onChange={(e) => setDate(e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-blue-500 focus:border-blue-500 outline-none"
                required
              />
            </div>
          </div>

          {error && <div className="p-4 bg-red-50 text-red-700 rounded-lg text-sm">{error}</div>}

          <button
            type="submit"
            disabled={loading}
            className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors flex justify-center items-center ${
              loading ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
            }`}
          >
            {loading ? 'Simulating...' : 'Simulate Trade'}
          </button>
        </form>
      </div>

      <div>
        {result ? (
          <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 h-full">
            <h3 className="text-xl font-bold text-gray-800 mb-6 flex items-center border-b pb-4">
              <PieChart className="mr-3 text-green-600" /> Simulation Results
            </h3>

            <div className="space-y-4">
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <span className="text-gray-600 font-medium">Sale Value (INR)</span>
                <span className="text-xl font-bold text-gray-900">
                  ₹{result.sale_value.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </span>
              </div>

              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-lg">
                <span className="text-gray-600 font-medium">Cost Basis (INR)</span>
                <span className="text-xl font-bold text-gray-900">
                  ₹{result.cost_basis.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </span>
              </div>

              <div className={`flex justify-between items-center p-4 rounded-lg border ${
                result.capital_gain >= 0 ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'
              }`}>
                <span className={`font-medium ${result.capital_gain >= 0 ? 'text-green-800' : 'text-red-800'}`}>
                  Capital Gain (INR)
                </span>
                <span className={`text-xl font-bold ${result.capital_gain >= 0 ? 'text-green-900' : 'text-red-900'}`}>
                  {result.capital_gain > 0 ? '+' : ''}₹{result.capital_gain.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </span>
              </div>

              <div className="flex justify-between items-center p-4 bg-orange-50 rounded-lg border border-orange-100">
                <span className="text-orange-800 font-medium">Estimated Tax (INR)</span>
                <span className="text-xl font-bold text-orange-900">
                  ₹{result.tax.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </span>
              </div>

              <div className="flex justify-between items-center p-4 bg-blue-50 rounded-lg border border-blue-100 mt-6 shadow-sm">
                <span className="text-blue-800 font-bold text-lg">Net After Tax</span>
                <span className="text-2xl font-bold text-blue-900 flex items-center">
                  <IndianRupee className="w-5 h-5 mr-1" />
                  {result.net_after_tax.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </span>
              </div>
            </div>

            <div className="mt-6 pt-4 border-t border-gray-100">
              <p className="text-xs text-gray-500 text-center">
                * Based on FIFO matching. STCG assumed at 30%, LTCG at 12.5%. Not financial advice.
              </p>
            </div>
          </div>
        ) : (
          <div className="bg-gray-50 rounded-xl border border-gray-200 border-dashed h-full flex flex-col items-center justify-center p-12 text-center">
            <Activity className="w-16 h-16 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-700 mb-2">No Simulation Run</h3>
            <p className="text-gray-500 text-sm">
              Enter your trade details and click "Simulate Trade" to estimate your capital gains and tax liability.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default SimulatorPage;
