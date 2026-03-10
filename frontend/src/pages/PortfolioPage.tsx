import { useEffect, useState } from 'react';
import { getPortfolio } from '../services/api';
import { Link } from 'react-router-dom';

const PortfolioPage: React.FC = () => {
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [manualPrices, setManualPrices] = useState<Record<string, number>>({});

  const fetchPortfolio = async (prices?: Record<string, number>) => {
    try {
      setLoading(true);
      const res = await getPortfolio(prices || manualPrices);
      setData(res);
    } catch (err: any) {
      setError(err.message || 'Error fetching portfolio');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const handlePriceChange = (symbol: string, price: string) => {
    const numPrice = parseFloat(price);
    if (!isNaN(numPrice)) {
      setManualPrices(prev => ({ ...prev, [symbol]: numPrice }));
    }
  };

  const handleApplyPrices = () => {
    fetchPortfolio(manualPrices);
  };

  if (loading && !data) return <div className="text-center mt-20 text-gray-500">Loading portfolio...</div>;
  if (error) return <div className="text-center mt-20 text-red-500">{error}</div>;

  if (!data || data.holdings.length === 0) {
    return (
      <div className="max-w-2xl mx-auto p-12 bg-white rounded-xl shadow-sm border border-gray-100 mt-10 text-center">
        <h2 className="text-2xl font-bold text-gray-800 mb-4">No Portfolio Data Found</h2>
        <p className="text-gray-600 mb-6">Upload a broker CSV file to view your portfolio.</p>
        <Link to="/" className="inline-block px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition">
          Upload Data
        </Link>
      </div>
    );
  }

  const { summary, holdings } = data;

  return (
    <div className="bg-white rounded-xl shadow-md p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Portfolio Dashboard</h1>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-gray-50 p-6 rounded-xl border border-gray-100">
          <p className="text-sm font-semibold text-gray-500 mb-1">Total Cost (INR)</p>
          <p className="text-3xl font-bold text-gray-900">₹{summary.total_cost_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
        </div>
        <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
          <p className="text-sm font-semibold text-blue-800 mb-1">Total Value (INR)</p>
          <p className="text-3xl font-bold text-blue-900">₹{summary.total_value_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</p>
        </div>
        <div className={`p-6 rounded-xl border ${summary.total_unrealized_gain >= 0 ? 'bg-green-50 border-green-100' : 'bg-red-50 border-red-100'}`}>
          <p className={`text-sm font-semibold mb-1 ${summary.total_unrealized_gain >= 0 ? 'text-green-800' : 'text-red-800'}`}>Unrealized Gain</p>
          <p className={`text-3xl font-bold ${summary.total_unrealized_gain >= 0 ? 'text-green-900' : 'text-red-900'}`}>
            {summary.total_unrealized_gain >= 0 ? '+' : ''}₹{summary.total_unrealized_gain.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </p>
        </div>
      </div>

      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-bold text-gray-800">Holdings</h2>
        <button
          onClick={handleApplyPrices}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm font-medium"
        >
          Recalculate with Custom Prices
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-600 text-sm uppercase tracking-wider border-b">
              <th className="p-4 font-semibold">Symbol</th>
              <th className="p-4 font-semibold text-right">Shares</th>
              <th className="p-4 font-semibold text-right">Avg Cost</th>
              <th className="p-4 font-semibold text-right">Cost (INR)</th>
              <th className="p-4 font-semibold text-right">Current Price</th>
              <th className="p-4 font-semibold text-right">Value (INR)</th>
              <th className="p-4 font-semibold text-right">Unrealized Gain</th>
              <th className="p-4 font-semibold text-right">Gain %</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-gray-100">
            {holdings.map((h: any, idx: number) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                <td className="p-4 text-gray-800 font-bold">{h.symbol}</td>
                <td className="p-4 text-right text-gray-600">{h.shares.toFixed(4)}</td>
                <td className="p-4 text-right text-gray-600">{h.avg_cost_local.toFixed(2)}</td>
                <td className="p-4 text-right text-gray-600">₹{h.cost_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                <td className="p-4 text-right">
                  <input
                    type="number"
                    step="0.01"
                    className="w-24 px-2 py-1 border border-gray-300 rounded text-right focus:outline-none focus:ring-1 focus:ring-blue-500"
                    placeholder={h.current_price.toFixed(2)}
                    onChange={(e) => handlePriceChange(h.symbol, e.target.value)}
                  />
                </td>
                <td className="p-4 text-right text-gray-600">₹{h.value_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                <td className={`p-4 text-right font-medium ${h.unrealized_gain >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {h.unrealized_gain > 0 ? '+' : ''}₹{h.unrealized_gain.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </td>
                <td className={`p-4 text-right font-medium ${h.gain_percent >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {h.gain_percent > 0 ? '+' : ''}{h.gain_percent.toFixed(2)}%
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default PortfolioPage;
