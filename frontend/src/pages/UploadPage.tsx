import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { UploadCloud, CheckCircle } from 'lucide-react';
import { uploadStatement } from '../services/api';

const UploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [broker, setBroker] = useState<string>('generic');
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      setFile(e.target.files[0]);
      setError(null);
    }
  };

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first.');
      return;
    }

    setIsUploading(true);
    setError(null);

    try {
      const response = await uploadStatement(file, broker);

      if (response.status === 'requires_mapping') {
        navigate('/preview', {
          state: {
            inferredMapping: response.inferred_mapping,
            filename: response.filename
          }
        });
      } else {
        navigate('/results');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'An error occurred during upload.');
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-xl shadow-md mt-10">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Upload Foreign Stock Statement</h1>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">Select Broker Format</label>
        <select
          value={broker}
          onChange={(e) => setBroker(e.target.value)}
          className="w-full p-3 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 outline-none"
        >
          <option value="shareworks">Morgan Stanley Shareworks</option>
          <option value="fidelity">Fidelity</option>
          <option value="generic">Generic / Other (Auto-detect schema via AI)</option>
        </select>
      </div>

      <div className="mb-6 border-2 border-dashed border-gray-300 rounded-xl p-8 text-center hover:bg-gray-50 transition-colors">
        <input
          type="file"
          id="file-upload"
          className="hidden"
          accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel"
          onChange={handleFileChange}
        />
        <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
          <UploadCloud className="h-12 w-12 text-gray-400 mb-3" />
          <span className="text-sm font-medium text-gray-900">
            {file ? file.name : "Click to select a CSV or Excel file"}
          </span>
          {!file && <span className="text-xs text-gray-500 mt-1">or drag and drop here</span>}
        </label>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 text-red-700 rounded-lg text-sm">
          {error}
        </div>
      )}

      <button
        onClick={handleUpload}
        disabled={!file || isUploading}
        className={`w-full py-3 px-4 rounded-lg font-medium text-white transition-colors flex justify-center items-center ${
          !file || isUploading
            ? 'bg-blue-300 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {isUploading ? (
          <span>Processing...</span>
        ) : (
          <>
            <CheckCircle className="w-5 h-5 mr-2" />
            Upload and Process
          </>
        )}
      </button>
    </div>
  );
};

export default UploadPage;
