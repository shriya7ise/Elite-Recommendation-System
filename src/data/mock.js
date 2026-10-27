export const campaigns = [
  { id: 1, name: "DS Bootcamp Q3", platform: "LinkedIn", status: "Running", budget: 12000, roi: 132, score: 7.8 },
  { id: 2, name: "AI Crash Course", platform: "Meta", status: "Paused", budget: 8000, roi: 96, score: 6.1 },
  { id: 3, name: "ML Pro Cert", platform: "Google", status: "Running", budget: 20000, roi: 148, score: 8.4 },
];

export const monthlySpend = [
  { month: "Apr", spend: 18 },
  { month: "May", spend: 22 },
  { month: "Jun", spend: 25 },
  { month: "Jul", spend: 29 },
  { month: "Aug", spend: 31 },
];

export const platformRevenue = [
  { name: "Meta", value: 38000 },
  { name: "Google", value: 52000 },
  { name: "LinkedIn", value: 26000 },
];

export const platformMetrics = [
  { name: "Meta", CTR: 1.2, CPC: 1.8, CVR: 3.3 },
  { name: "Google", CTR: 2.1, CPC: 2.6, CVR: 4.1 },
  { name: "LinkedIn", CTR: 0.9, CPC: 3.2, CVR: 2.4 },
];

export const competitorList = [
  { id: "A", name: "Competitor A", logo: "A", tracked: true },
  { id: "B", name: "Competitor B", logo: "B", tracked: true },
  { id: "C", name: "Competitor C", logo: "C", tracked: false },
];

export const competitorAds = [
  {
    id: "ad1",
    competitor: "Competitor A",
    platform: "LinkedIn",
    type: "Content Post",
    title: "Become a Data Scientist",
    desc: "Industry-recognized program. Learn ML, AI, and more.",
    timestamp: "2025-08-15 10:32",
    metrics: { ctr: 0.4, quality: 4.6, engagement: 5.3, cta: "Weak" },
    analysis: {
      sentiment: "Neutral", confidence: 0.5, tone: "Professional", readingLevel: "Medium",
      words: 30, chars: 202, dailyImpressions: 12182, cpc: 28.36, urgency: "Low",
      triggers: ["authority"], persuasion: 1
    }
  },
  {
    id: "ad2",
    competitor: "Competitor B",
    platform: "Meta",
    type: "Image Ad",
    title: "AI Career Fast-Track",
    desc: "Limited seats. Hands-on projects with mentors.",
    timestamp: "2025-08-18 14:05",
    metrics: { ctr: 0.6, quality: 5.1, engagement: 6.2, cta: "Medium" },
    analysis: {
      sentiment: "Positive", confidence: 0.63, tone: "Professional", readingLevel: "Medium",
      words: 26, chars: 165, dailyImpressions: 15440, cpc: 24.10, urgency: "Medium",
      triggers: ["authority","scarcity"], persuasion: 2
    }
  }
];

export const successRadar = [
  { factor: "Urgency+Job Guarantee", score: 85 },
  { factor: "Authority+Social Proof", score: 78 },
  { factor: "Casual+Strong CTA", score: 72 },
  { factor: "Mentor+Career Outcomes", score: 80 },
];

export const qualityVsReading = [
  { level: "Easy", quality: 3.9 },
  { level: "Medium", quality: 4.7 },
  { level: "Hard", quality: 4.2 },
];
