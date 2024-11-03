import type { SEOResult, Recommendation, Metric } from '../types/seo';

export async function analyzeSEO(url: string): Promise<SEOResult> {
  // Simulate API call to analyze SEO
  await new Promise(resolve => setTimeout(resolve, 2000));

  const recommendations: Recommendation[] = [
    {
      id: '1',
      title: 'Optimize Meta Descriptions',
      description: 'Your meta descriptions are too short. Add compelling descriptions to improve CTR.',
      priority: 'high',
      category: 'seo'
    },
    {
      id: '2',
      title: 'Improve Page Load Speed',
      description: 'Large images are slowing down your page. Compress images to improve performance.',
      priority: 'high',
      category: 'performance'
    },
    {
      id: '3',
      title: 'Add Alt Text to Images',
      description: '12 images are missing alt text. Add descriptive alt text for better accessibility.',
      priority: 'medium',
      category: 'accessibility'
    },
    {
      id: '4',
      title: 'Fix Header Hierarchy',
      description: 'Proper header hierarchy (h1-h6) is missing. Implement correct header structure.',
      priority: 'medium',
      category: 'best-practices'
    }
  ];

  const metrics: Metric[] = [
    { name: 'Page Load Time', value: '2.5s', status: 'warning' },
    { name: 'Mobile Friendly', value: 'Yes', status: 'good' },
    { name: 'SSL Certificate', value: 'Valid', status: 'good' },
    { name: 'Broken Links', value: 3, status: 'error' }
  ];

  return {
    score: 85,
    recommendations,
    metrics
  };
}