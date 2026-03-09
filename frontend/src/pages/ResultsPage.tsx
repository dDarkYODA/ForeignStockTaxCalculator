import { useEffect, useState } from 'react';
import { getResults } from '../services/api';
import { Download, IndianRupee, PieChart, Info } from 'lucide-react';

const ResultsPage: React.FC = () => {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchResults = async () => {
      try {
        const data = await getResults();
        setResults(data);
      } catch (err: any) {
        setError(err.message || 'Error fetching results');
      } finally {
        setLoading(false);
      }
    };
    fetchResults();
  }, []);

  const handleExportCSV = () => {
    if (results.length === 0) return;

    const headers = ['Date', 'Symbol', 'Shares', 'Cost (INR)', 'Sale (INR)', 'Gain (INR)', 'Holding Type'];
    const csvContent = [
      headers.join(','),
      ...results.map(row =>
        `${row.date},${row.symbol},${row.shares},${row.cost_inr.toFixed(2)},${row.sale_inr.toFixed(2)},${row.gain_inr.toFixed(2)},${row.holding_type}`
      )
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', 'capital_gains_report.csv');
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (loading) return <div className="text-center mt-20 text-gray-500">Loading results...</div>;
  if (error) return <div className="text-center mt-20 text-red-500">{error}</div>;

  const totalGain = results.reduce((acc, r) => acc + r.gain_inr, 0);

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white rounded-xl shadow-md mt-10">
      <div className="flex justify-between items-center mb-6 border-b pb-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-800 flex items-center">
            <PieChart className="mr-3 text-blue-600" /> Capital Gains Report
          </h1>
          <p className="text-sm text-gray-500 mt-1 flex items-center">
            <Info className="w-4 h-4 mr-1" /> FIFO method applied. Foreign exchange based on SBI TT Buying Rates.
          </p>
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
        >
          <Download className="w-4 h-4 mr-2" /> Export CSV
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-blue-50 p-6 rounded-xl border border-blue-100">
          <p className="text-sm font-semibold text-blue-800 mb-1">Total Transactions</p>
          <p className="text-3xl font-bold text-blue-900">{results.length}</p>
        </div>
        <div className="bg-green-50 p-6 rounded-xl border border-green-100">
          <p className="text-sm font-semibold text-green-800 mb-1">Total Gain (INR)</p>
          <p className="text-3xl font-bold text-green-900 flex items-center">
            <IndianRupee className="w-6 h-6 mr-1" />
            {totalGain.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
          </p>
        </div>
        <div className="bg-purple-50 p-6 rounded-xl border border-purple-100">
          <p className="text-sm font-semibold text-purple-800 mb-1">LTCG / STCG Split</p>
          <div className="flex gap-4 mt-2">
            <div>
              <span className="text-xs text-purple-600 block">LTCG</span>
              <span className="font-bold text-purple-900">
                {results.filter(r => r.holding_type === 'LTCG').length} lots
              </span>
            </div>
            <div>
              <span className="text-xs text-purple-600 block">STCG</span>
              <span className="font-bold text-purple-900">
                {results.filter(r => r.holding_type === 'STCG').length} lots
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-gray-50 text-gray-600 text-sm uppercase tracking-wider border-b">
              <th className="p-4 font-semibold">Date</th>
              <th className="p-4 font-semibold">Symbol</th>
              <th className="p-4 font-semibold text-right">Shares</th>
              <th className="p-4 font-semibold text-right">Cost (INR)</th>
              <th className="p-4 font-semibold text-right">Sale (INR)</th>
              <th className="p-4 font-semibold text-right">Gain (INR)</th>
              <th className="p-4 font-semibold text-center">Type</th>
            </tr>
          </thead>
          <tbody className="text-sm divide-y divide-gray-100">
            {results.map((row, idx) => (
              <tr key={idx} className="hover:bg-gray-50 transition-colors">
                <td className="p-4 text-gray-800 font-medium">{row.date}</td>
                <td className="p-4 text-gray-600">{row.symbol}</td>
                <td className="p-4 text-right text-gray-600">{row.shares}</td>
                <td className="p-4 text-right text-gray-600">{row.cost_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                <td className="p-4 text-right text-gray-600">{row.sale_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}</td>
                <td className={`p-4 text-right font-medium ${row.gain_inr >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {row.gain_inr > 0 ? '+' : ''}{row.gain_inr.toLocaleString('en-IN', { maximumFractionDigits: 2 })}
                </td>
                <td className="p-4 text-center">
                  <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                    row.holding_type === 'LTCG' ? 'bg-indigo-100 text-indigo-800' : 'bg-orange-100 text-orange-800'
                  }`}>
                    {row.holding_type}
                  </span>
                </td>
              </tr>
            ))}

            {results.length === 0 && (
              <tr>
                <td colSpan={7} className="p-8 text-center text-gray-500">
                  <div className="flex flex-col items-center justify-center">
                    <Info className="w-8 h-8 text-blue-400 mb-2" />
                    <p className="text-lg font-medium text-gray-800">No sale transactions found</p>
                    <p className="text-sm mt-1">Capital gains can only be calculated when there are matching SELL transactions.</p>
                    <p className="text-sm">The uploaded file appears to only contain purchases or vests.</p>
                  </div>
                </td>
              </tr>
            )}

          </tbody>
        </table>
      </div>
    </div>
  );
};

export default ResultsPage;
