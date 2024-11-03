import React, { useState } from 'react';
import { Hero } from './components/Hero';
import { URLForm } from './components/URLForm';
import { SEOResults } from './components/SEOResults';
import { DetailedAnalysis } from './components/DetailedAnalysis';
import { analyzeSEO } from './utils/seoAnalyzer';
import { generatePDF, downloadPDF } from './utils/pdfGenerator';
import { backupWebpage } from './utils/webpageBackup';
import type { SEOResult } from './types/seo';

function App() {
  const [url, setUrl] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isBackingUp, setIsBackingUp] = useState(false);
  const [results, setResults] = useState<SEOResult | null>(null);
  const [isGeneratingPDF, setIsGeneratingPDF] = useState(false);
  const [showDetailedAnalysis, setShowDetailedAnalysis] = useState(false);

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsAnalyzing(true);
    try {
      const seoResults = await analyzeSEO(url);
      setResults(seoResults);
    } catch (error) {
      console.error('Error analyzing SEO:', error);
      alert('Failed to analyze SEO. Please try again.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleBackup = async () => {
    if (!url) return;
    
    setIsBackingUp(true);
    try {
      await backupWebpage(url);
    } catch (error) {
      console.error('Error creating backup:', error);
      alert('Failed to create backup. Please try again.');
    } finally {
      setIsBackingUp(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!results) return;
    
    setIsGeneratingPDF(true);
    try {
      const pdf = await generatePDF(results);
      downloadPDF(pdf, 'seo-report.pdf');
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('Failed to generate PDF. Please try again.');
    } finally {
      setIsGeneratingPDF(false);
    }
  };

  const handleViewDetails = () => {
    if (!results) return;
    setShowDetailedAnalysis(true);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-white to-purple-50">
      <div className="container mx-auto px-4 py-12">
        <Hero />
        <URLForm
          url={url}
          isAnalyzing={isAnalyzing}
          isBackingUp={isBackingUp}
          onUrlChange={setUrl}
          onAnalyze={handleAnalyze}
          onBackup={handleBackup}
        />
        {results && (
          <SEOResults
            results={results}
            onDownloadPDF={handleDownloadPDF}
            onViewDetails={handleViewDetails}
          />
        )}
        {showDetailedAnalysis && results && (
          <DetailedAnalysis
            results={results}
            onClose={() => setShowDetailedAnalysis(false)}
          />
        )}
      </div>
    </div>
  );
}

export default App;