import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { ArrowLeft, Download, RotateCcw, ChevronDown, ChevronUp } from 'lucide-react';

export default function Results() {
  const { analysisId } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [analysis, setAnalysis] = useState(location.state?.analysis || null);
  const [expandedParagraph, setExpandedParagraph] = useState(null);

  const getScoreBadge = (score) => {
    if (score >= 80) return { bg: 'bg-red-500/20', border: 'border-red-500/30', text: 'text-red-300', label: 'Very High' };
    if (score >= 60) return { bg: 'bg-orange-500/20', border: 'border-orange-500/30', text: 'text-orange-300', label: 'High' };
    if (score >= 40) return { bg: 'bg-yellow-500/20', border: 'border-yellow-500/30', text: 'text-yellow-300', label: 'Medium' };
    if (score >= 20) return { bg: 'bg-blue-500/20', border: 'border-blue-500/30', text: 'text-blue-300', label: 'Low' };
    return { bg: 'bg-green-500/20', border: 'border-green-500/30', text: 'text-green-300', label: 'Very Low' };
  };

  const getProgressBarColor = (score) => {
    if (score >= 80) return 'bg-red-500';
    if (score >= 60) return 'bg-orange-500';
    if (score >= 40) return 'bg-yellow-500';
    if (score >= 20) return 'bg-blue-500';
    return 'bg-green-500';
  };

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-400 mb-6">Loading results...</p>
          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const overallScore = Math.round(analysis.overall_ai_percentage || 0);
  const confidence = Math.round(analysis.confidence_score || 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-slate-900">
      {/* Header */}
      <div className="border-b border-white/10 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4 flex justify-between items-center">
          <button
            onClick={() => navigate('/')}
            className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Back
          </button>
          <h1 className="text-2xl font-bold text-white">Analysis Results</h1>
          <div className="w-12"></div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Overall Score Card */}
        <div className="bg-gradient-to-br from-white/10 to-white/5 border border-white/20 rounded-2xl p-8 backdrop-blur-md mb-8">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Main Score */}
            <div className="md:col-span-1 flex flex-col justify-center items-center">
              <p className="text-gray-400 text-sm mb-2 uppercase tracking-wide">AI Content Score</p>
              <div className="relative w-32 h-32 mb-4">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 120 120">
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    stroke="rgba(255,255,255,0.1)"
                    strokeWidth="8"
                    fill="none"
                  />
                  <circle
                    cx="60"
                    cy="60"
                    r="54"
                    stroke={getProgressBarColor(overallScore).replace('bg-', '')}
                    strokeWidth="8"
                    fill="none"
                    strokeDasharray={`${(overallScore / 100) * 339.3} 339.3`}
                    className="transition-all duration-1000"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-4xl font-bold text-white">{overallScore}%</span>
                </div>
              </div>
              <p className="text-gray-400 text-sm text-center">
                of document is AI-generated
              </p>
            </div>

            {/* Stats */}
            <div className="md:col-span-2 space-y-4">
              <div>
                <div className="flex justify-between items-center mb-2">
                  <p className="text-gray-300 font-semibold">Confidence Level</p>
                  <span className="text-white font-bold">{confidence}%</span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div
                    className="bg-gradient-to-r from-blue-500 to-blue-400 h-2 rounded-full transition-all duration-1000"
                    style={{ width: `${confidence}%` }}
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Words Analyzed</p>
                  <p className="text-2xl font-bold text-white">
                    {analysis.total_words?.toLocaleString() || 0}
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">AI Words Detected</p>
                  <p className="text-2xl font-bold text-orange-400">
                    {analysis.ai_words?.toLocaleString() || 0}
                  </p>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/10">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Processing Time</p>
                  <p className="text-white font-semibold">
                    {analysis.processing_time?.toFixed(2)}s
                  </p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Paragraphs Scanned</p>
                  <p className="text-white font-semibold">
                    {analysis.paragraph_results?.length || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Paragraph Breakdown */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">Paragraph Breakdown</h2>

          <div className="space-y-3">
            {analysis.paragraph_results?.map((para, index) => {
              const badge = getScoreBadge(para.ai_score);
              const isExpanded = expandedParagraph === index;

              return (
                <div
                  key={index}
                  className="bg-white/5 border border-white/10 rounded-lg overflow-hidden backdrop-blur-md hover:bg-white/10 transition-colors"
                >
                  {/* Paragraph Header */}
                  <button
                    onClick={() => setExpandedParagraph(isExpanded ? null : index)}
                    className="w-full p-4 flex items-start gap-4 hover:bg-white/5 transition-colors"
                  >
                    <div className="flex-grow text-left">
                      <p className="text-gray-300 line-clamp-2 mb-2">
                        {para.text.substring(0, 150)}...
                      </p>
                      <div className="flex items-center gap-3">
                        <div className="flex-grow">
                          <div className="w-32 h-1.5 bg-white/10 rounded-full overflow-hidden">
                            <div
                              className={`${getProgressBarColor(para.ai_score)} h-full transition-all`}
                              style={{ width: `${para.ai_score}%` }}
                            />
                          </div>
                        </div>
                        <span className="text-sm font-bold text-white min-w-fit">
                          {Math.round(para.ai_score)}%
                        </span>
                        <div
                          className={`px-2 py-1 rounded text-xs font-semibold ${badge.bg} ${badge.border} border ${badge.text}`}
                        >
                          {badge.label}
                        </div>
                      </div>
                    </div>
                    {isExpanded ? (
                      <ChevronUp className="w-5 h-5 text-gray-400 flex-shrink-0 mt-1" />
                    ) : (
                      <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0 mt-1" />
                    )}
                  </button>

                  {/* Expanded Content */}
                  {isExpanded && (
                    <div className="border-t border-white/10 p-4 bg-white/5">
                      <p className="text-gray-300 mb-4 leading-relaxed">
                        {para.text}
                      </p>
                      <div className="grid grid-cols-3 gap-4 text-sm">
                        <div>
                          <p className="text-gray-400 text-xs mb-1 uppercase">Perplexity</p>
                          <p className="text-white font-semibold">
                            {para.metrics?.perplexity?.toFixed(2) || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400 text-xs mb-1 uppercase">Burstiness</p>
                          <p className="text-white font-semibold">
                            {para.metrics?.burstiness?.toFixed(2) || 'N/A'}
                          </p>
                        </div>
                        <div>
                          <p className="text-gray-400 text-xs mb-1 uppercase">Entropy</p>
                          <p className="text-white font-semibold">
                            {para.metrics?.entropy?.toFixed(2) || 'N/A'}
                          </p>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex gap-4 justify-center pt-8 border-t border-white/10">
          <button
            onClick={() => navigate('/upload')}
            className="inline-flex items-center gap-2 px-8 py-3 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-semibold transition-colors"
          >
            <RotateCcw className="w-5 h-5" />
            Analyze Another
          </button>
          <button
            onClick={() => {
              const element = document.createElement('a');
              element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(JSON.stringify(analysis, null, 2)));
              element.setAttribute('download', `analysis_${analysisId}.json`);
              element.style.display = 'none';
              document.body.appendChild(element);
              element.click();
              document.body.removeChild(element);
            }}
            className="inline-flex items-center gap-2 px-8 py-3 border border-white/20 text-white rounded-lg font-semibold hover:bg-white/5 transition-colors"
          >
            <Download className="w-5 h-5" />
            Download Report
          </button>
        </div>
      </div>
    </div>
  );
}
