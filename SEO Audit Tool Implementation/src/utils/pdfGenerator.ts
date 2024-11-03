import jsPDF from 'jspdf';
import type { SEOResult } from '../types/seo';

export async function generatePDF(results: SEOResult): Promise<Blob> {
  const pdf = new jsPDF();
  let yPos = 20;

  // Title
  pdf.setFontSize(24);
  pdf.text('SEO Analysis Report', 20, yPos);
  yPos += 20;

  // Score
  pdf.setFontSize(16);
  pdf.text(`Overall Score: ${results.score}/100`, 20, yPos);
  yPos += 20;

  // Metrics
  pdf.setFontSize(16);
  pdf.text('Key Metrics', 20, yPos);
  yPos += 10;

  pdf.setFontSize(12);
  results.metrics.forEach(metric => {
    pdf.text(`${metric.name}: ${metric.value} (${metric.status})`, 30, yPos);
    yPos += 10;
  });
  yPos += 10;

  // Recommendations
  pdf.setFontSize(16);
  pdf.text('Recommendations', 20, yPos);
  yPos += 10;

  pdf.setFontSize(12);
  results.recommendations.forEach(rec => {
    // Check if we need a new page
    if (yPos > 270) {
      pdf.addPage();
      yPos = 20;
    }

    pdf.text(`${rec.title} (${rec.priority.toUpperCase()})`, 30, yPos);
    yPos += 7;
    
    // Split long descriptions into multiple lines
    const lines = pdf.splitTextToSize(rec.description, 150);
    lines.forEach(line => {
      if (yPos > 270) {
        pdf.addPage();
        yPos = 20;
      }
      pdf.text(line, 30, yPos);
      yPos += 7;
    });
    yPos += 5;
  });

  return pdf.output('blob');
}

export function downloadPDF(blob: Blob, filename: string) {
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(url);
}