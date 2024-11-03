export interface SEOResult {
  score: number;
  recommendations: Recommendation[];
  metrics: Metric[];
}

export interface Recommendation {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: 'performance' | 'accessibility' | 'seo' | 'best-practices';
}

export interface Metric {
  name: string;
  value: string | number;
  status: 'good' | 'warning' | 'error';
}