import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { confirmMapping } from '../services/api';
import { AlertCircle, ArrowRight } from 'lucide-react';

const PreviewPage: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const { inferredMapping = {}, filename = '' } = location.state || {};

  const [mapping, setMapping] = useState<Record<string, string>>(inferredMapping);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const requiredFields = [
    { key: 'date', label: 'Transaction Date' },
    { key: 'transaction_type', label: 'Transaction Type' },
    { key: 'symbol', label: 'Symbol / Ticker' },
    { key: 'shares', label: 'Shares / Quantity' },
    { key: 'price', label: 'Price' },
    { key: 'currency', label: 'Currency (Optional)' }
  ];

  const handleMappingChange = (fieldKey: string, value: string) => {
    setMapping({ ...mapping, [fieldKey]: value });
  };

  const handleConfirm = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await confirmMapping(filename, mapping);
      navigate('/results');
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Error processing mappings');
      setIsSubmitting(false);
    }
  };

  if (!filename) {
    return (
      <div className="max-w-2xl mx-auto p-6 mt-10 text-center">
        <p>No file context found. Please start from upload.</p>
        <button onClick={() => navigate('/')} className="mt-4 text-blue-600 underline">Go Back</button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-6 bg-white rounded-xl shadow-md mt-10">
      <div className="flex items-center mb-6">
        <div className="bg-yellow-100 p-2 rounded-full mr-3">
          <AlertCircle className="w-6 h-6 text-yellow-600" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-gray-800">Confirm Column Mappings</h1>
          <p className="text-sm text-gray-500">Our AI has inferred these mappings. Please review and edit if necessary.</p>
        </div>
      </div>

      <div className="bg-gray-50 p-6 rounded-lg mb-6 border border-gray-200">
        <div className="grid grid-cols-2 gap-y-4 gap-x-8">
          {requiredFields.map((field) => (
            <div key={field.key} className="flex flex-col">
              <label className="text-sm font-semibold text-gray-700 mb-1">{field.label}</label>
              <input
                type="text"
                value={mapping[field.key] || ''}
                onChange={(e) => handleMappingChange(field.key, e.target.value)}
                placeholder="Column header name..."
                className="p-2 border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500 outline-none text-sm"
              />
            </div>
          ))}
        </div>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={handleConfirm}
          disabled={isSubmitting}
          className={`py-2 px-6 rounded-lg font-medium text-white transition-colors flex items-center ${
            isSubmitting ? 'bg-blue-300 cursor-not-allowed' : 'bg-blue-600 hover:bg-blue-700'
          }`}
        >
          {isSubmitting ? 'Processing...' : 'Confirm & Process'}
          {!isSubmitting && <ArrowRight className="ml-2 w-4 h-4" />}
        </button>
      </div>
    </div>
  );
};

export default PreviewPage;
