import { useNavigate } from 'react-router-dom';
import { Zap, CheckCircle, ArrowRight, Shield, Cpu, BarChart3 } from 'lucide-react';

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Navigation */}
      <nav className="border-b border-white/10 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Cpu className="w-6 h-6 text-orange-500" />
            <span className="text-xl font-bold text-white">AI Detector</span>
          </div>
          <button
            onClick={() => navigate('/upload')}
            className="px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold transition-colors"
          >
            Analyze Now
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <div className="mb-8 animate-fade-in">
          <div className="inline-block mb-4">
            <Zap className="w-16 h-16 text-orange-500 mx-auto animate-pulse" />
          </div>
          <h1 className="text-5xl md:text-7xl font-bold text-white mb-6 leading-tight">
            Detect AI Content <br />
            <span className="bg-gradient-to-r from-orange-400 to-yellow-300 bg-clip-text text-transparent">
              In Any Document
            </span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-2xl mx-auto">
            Instantly identify AI-generated content across all LLMs (Claude, GPT, Llama, Gemini) with precision. Get detailed breakdown by paragraph and confidence scores.
          </p>
        </div>

        <button
          onClick={() => navigate('/upload')}
          className="inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg font-semibold text-lg transition-all transform hover:scale-105 mb-16"
        >
          Upload Document <ArrowRight className="w-5 h-5" />
        </button>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-20">
          <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-md hover:bg-white/10 transition-colors">
            <div className="flex justify-center mb-4">
              <CheckCircle className="w-8 h-8 text-green-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">All LLMs Detected</h3>
            <p className="text-gray-400 text-sm">
              Works with Claude, GPT, Llama, Gemini, and more
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-md hover:bg-white/10 transition-colors">
            <div className="flex justify-center mb-4">
              <BarChart3 className="w-8 h-8 text-blue-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Detailed Breakdown</h3>
            <p className="text-gray-400 text-sm">
              Per-paragraph analysis with confidence scores
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-xl p-6 backdrop-blur-md hover:bg-white/10 transition-colors">
            <div className="flex justify-center mb-4">
              <Shield className="w-8 h-8 text-purple-400" />
            </div>
            <h3 className="text-white font-semibold mb-2">Private & Secure</h3>
            <p className="text-gray-400 text-sm">
              Your documents are never stored or shared
            </p>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <h2 className="text-3xl font-bold text-white mb-12 text-center">How It Works</h2>
        
        <div className="space-y-6">
          <div className="bg-white/5 border border-white/10 rounded-lg p-6 backdrop-blur-md">
            <h3 className="text-white font-semibold mb-2">📤 Upload</h3>
            <p className="text-gray-400">
              Drag & drop or select a PDF, DOCX, or TXT file. Max size: 10MB.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-6 backdrop-blur-md">
            <h3 className="text-white font-semibold mb-2">🔬 Analyze</h3>
            <p className="text-gray-400">
              Our AI detector scans the document using advanced statistical analysis, measuring perplexity, burstiness, and entropy across all LLMs.
            </p>
          </div>

          <div className="bg-white/5 border border-white/10 rounded-lg p-6 backdrop-blur-md">
            <h3 className="text-white font-semibold mb-2">📊 Results</h3>
            <p className="text-gray-400">
              Get your overall AI% score, confidence level, and detailed breakdown showing which paragraphs are AI-generated.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 backdrop-blur-md py-8 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-400 text-sm">
          <p>AI Content Detector • Detect AI across all LLMs • Built with React + FastAPI</p>
        </div>
      </footer>
    </div>
  );
}
