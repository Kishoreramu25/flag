import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, ArrowLeft, FileText, AlertCircle } from 'lucide-react';
import axios from 'axios';

export default function UploadPage() {
  const navigate = useNavigate();
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const droppedFile = e.dataTransfer.files[0];
    if (validateFile(droppedFile)) {
      setFile(droppedFile);
      setError(null);
    }
  };

  const validateFile = (selectedFile) => {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];

    if (!allowedTypes.includes(selectedFile.type)) {
      setError('Only PDF, DOCX, and TXT files are supported');
      return false;
    }
    if (selectedFile.size > maxSize) {
      setError('File size must be less than 10MB');
      return false;
    }
    return true;
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && validateFile(selectedFile)) {
      setFile(selectedFile);
      setError(null);
    }
  };

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      // Call backend API
      const response = await axios.post(
        `${import.meta.env.VITE_BACKEND_URL}/api/analyze`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      // Navigate to results page with data
      navigate(`/results/${response.data.analysis_id}`, {
        state: { analysis: response.data },
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Please try again.');
      console.error('Analysis error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Header */}
      <div className="border-b border-white/10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h1 className="text-4xl font-bold text-white mb-2 text-center">
          Upload Your Document
        </h1>
        <p className="text-gray-400 text-center mb-12">
          Select a PDF, DOCX, or TXT file to analyze for AI-generated content
        </p>

        {/* Upload Area */}
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative border-2 border-dashed rounded-2xl p-12 text-center transition-all cursor-pointer ${
            dragActive
              ? 'border-orange-500 bg-orange-500/10'
              : 'border-white/20 bg-white/5 hover:bg-white/10'
          }`}
        >
          <input
            type="file"
            onChange={handleFileChange}
            accept=".pdf,.docx,.txt"
            className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          />

          <Upload className="w-12 h-12 text-orange-500 mx-auto mb-4" />
          <p className="text-white font-semibold mb-2">
            Drag & drop your file here
          </p>
          <p className="text-gray-400 text-sm mb-4">
            or click to browse from your computer
          </p>
          <p className="text-gray-500 text-xs">
            PDF, DOCX, or TXT • Max 10MB
          </p>
        </div>

        {/* File Selected */}
        {file && (
          <div className="mt-8 bg-white/5 border border-white/10 rounded-lg p-4 backdrop-blur-md flex items-center gap-4">
            <FileText className="w-8 h-8 text-blue-400 flex-shrink-0" />
            <div className="flex-grow">
              <p className="text-white font-semibold">{file.name}</p>
              <p className="text-gray-400 text-sm">
                {(file.size / 1024 / 1024).toFixed(2)} MB
              </p>
            </div>
            <button
              onClick={() => setFile(null)}
              className="text-gray-400 hover:text-white transition-colors"
            >
              ✕
            </button>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mt-6 bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Action Buttons */}
        <div className="mt-12 flex gap-4 justify-center">
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 border border-white/20 text-white rounded-lg font-semibold hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleAnalyze}
            disabled={!file || loading}
            className={`px-8 py-3 rounded-lg font-semibold transition-all flex items-center gap-2 ${
              file && !loading
                ? 'bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white'
                : 'bg-gray-600 text-gray-300 cursor-not-allowed'
            }`}
          >
            {loading ? (
              <>
                <span className="animate-spin">⏳</span>
                Analyzing...
              </>
            ) : (
              'Analyze Document'
            )}
          </button>
        </div>

        {/* Info Box */}
        <div className="mt-12 bg-blue-500/10 border border-blue-500/20 rounded-lg p-6">
          <h3 className="text-blue-300 font-semibold mb-2">💡 How it works</h3>
          <ul className="text-gray-400 text-sm space-y-2">
            <li>✓ Upload your document (PDF, DOCX, or TXT)</li>
            <li>✓ Our AI detector analyzes the content</li>
            <li>✓ Get instant results showing % AI content</li>
            <li>✓ See detailed breakdown by paragraph</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
