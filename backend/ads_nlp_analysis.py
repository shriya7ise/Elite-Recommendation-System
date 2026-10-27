import os
import re
import json
import time
import random
import requests
from collections import Counter
from serpapi import GoogleSearch
from db_ops import DatabaseOperations

# API Configuration
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
HUGGINGFACE_API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
HUGGINGFACE_TOKEN = os.getenv("HF_TOKEN", "")

class FreeNLPAdAnalyzer:
    def __init__(self):
        self.collected_ads = []
        self.db_ops = DatabaseOperations()
        
        # Marketing effectiveness scoring weights
        self.keyword_weights = {
            'free': 3.0, 'certified': 2.8, 'professional': 2.5, 'expert': 2.4,
            'guarantee': 2.2, 'proven': 2.1, 'exclusive': 2.0, 'limited': 1.9,
            'learn': 1.5, 'master': 1.7, 'complete': 1.6, 'comprehensive': 1.5,
            'practical': 1.4, 'hands-on': 1.6, 'project': 1.4, 'career': 1.8,
            'start': 1.3, 'join': 1.4, 'enroll': 1.2, 'register': 1.1,
            'download': 1.2, 'access': 1.1, 'get': 1.0, 'try': 1.3
        }
        
        self.emotional_triggers = {
            'urgency': ['limited time', 'hurry', 'deadline', 'expires', 'today only', 'last chance', 'now'],
            'social_proof': ['trusted', 'popular', 'rated', 'students', 'professionals', 'community'],
            'achievement': ['success', 'transform', 'advance', 'boost', 'improve', 'excel'],
            'fear_of_missing_out': ['exclusive', 'limited', 'special', 'only', 'rare', 'unique'],
            'authority': ['expert', 'certified', 'official', 'accredited', 'university', 'industry']
        }

    def fetch_ads_from_platforms(self):
        """Fetch ads using SerpAPI"""
        print("🔍 Fetching ads from all platforms...")
        
        # Google Ads
        print("\n📌 Fetching Google Ads...")
        google_params = {
            "engine": "google",
            "q": "online python course",
            "location": "India",
            "api_key": SERPAPI_KEY
        }
        
        try:
            google_search = GoogleSearch(google_params)
            google_results = google_search.get_dict()
            
            if "ads" in google_results:
                for ad in google_results.get("ads", []):
                    ad_data = {
                        'platform': 'Google',
                        'type': 'Search Ad',
                        'title': ad.get("title", ""),
                        'description': ad.get("snippet", ""),
                        'link': ad.get("displayed_link", ""),
                        'position': ad.get("position", "N/A"),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.collected_ads.append(ad_data)
                    print(f"✅ Found: {ad.get('title', '')[:50]}...")
            
            if "shopping_results" in google_results:
                for item in google_results.get("shopping_results", [])[:3]:
                    ad_data = {
                        'platform': 'Google',
                        'type': 'Shopping Ad',
                        'title': item.get("title", ""),
                        'description': f"Price: {item.get('price', 'N/A')} | {item.get('snippet', '')}",
                        'link': item.get("link", ""),
                        'position': item.get("position", "N/A"),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.collected_ads.append(ad_data)
                    print(f"🛒 Shopping: {item.get('title', '')[:50]}...")
                    
        except Exception as e:
            print(f"❌ Google error: {e}")
        
        # LinkedIn Content
        print("\n📌 Fetching LinkedIn Content...")
        linkedin_params = {
            "engine": "google",
            "q": "site:linkedin.com data science certification",
            "location": "India",
            "api_key": SERPAPI_KEY
        }
        
        try:
            linkedin_search = GoogleSearch(linkedin_params)
            linkedin_results = linkedin_search.get_dict()
            
            if "organic_results" in linkedin_results:
                for result in linkedin_results.get("organic_results", [])[:5]:
                    if "linkedin.com" in result.get("link", ""):
                        ad_data = {
                            'platform': 'LinkedIn',
                            'type': 'Content Post',
                            'title': result.get("title", ""),
                            'description': result.get("snippet", ""),
                            'link': result.get("link", ""),
                            'position': result.get("position", "N/A"),
                            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                        }
                        self.collected_ads.append(ad_data)
                        print(f"✅ Found: {result.get('title', '')[:50]}...")
                        
        except Exception as e:
            print(f"❌ LinkedIn error: {e}")
        
        # Bing Ads
        print("\n📌 Fetching Bing Ads...")
        bing_params = {
            "engine": "bing",
            "q": "online course programming",
            "location": "India",
            "api_key": SERPAPI_KEY
        }
        
        try:
            bing_search = GoogleSearch(bing_params)
            bing_results = bing_search.get_dict()
            
            if "ads" in bing_results:
                for ad in bing_results.get("ads", []):
                    ad_data = {
                        'platform': 'Bing',
                        'type': 'Search Ad',
                        'title': ad.get("title", ""),
                        'description': ad.get("snippet", ""),
                        'link': ad.get("displayed_link", ""),
                        'position': ad.get("position", "N/A"),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.collected_ads.append(ad_data)
                    print(f"✅ Found: {ad.get('title', '')[:50]}...")
            else:
                for result in bing_results.get("organic_results", [])[:3]:
                    ad_data = {
                        'platform': 'Bing',
                        'type': 'Organic Result',
                        'title': result.get("title", ""),
                        'description': result.get("snippet", ""),
                        'link': result.get("link", ""),
                        'position': result.get("position", "N/A"),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.collected_ads.append(ad_data)
                    print(f"📄 Organic: {result.get('title', '')[:50]}...")
                    
        except Exception as e:
            print(f"❌ Bing error: {e}")
        
        # YouTube Videos
        print("\n📌 Fetching YouTube Videos...")
        youtube_params = {
            "engine": "youtube",
            "search_query": "online python course",
            "api_key": SERPAPI_KEY
        }
        
        try:
            youtube_search = GoogleSearch(youtube_params)
            youtube_results = youtube_search.get_dict()
            
            if "video_results" in youtube_results:
                for video in youtube_results.get("video_results", [])[:5]:
                    channel_info = video.get("channel", {})
                    ad_data = {
                        'platform': 'YouTube',
                        'type': 'Video',
                        'title': video.get("title", ""),
                        'description': video.get("description", ""),
                        'link': video.get("link", ""),
                        'channel': channel_info.get("name", ""),
                        'views': video.get("views", "N/A"),
                        'duration': video.get("duration", "N/A"),
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    self.collected_ads.append(ad_data)
                    print(f"🎥 Found: {video.get('title', '')[:50]}...")
                    
        except Exception as e:
            print(f"❌ YouTube error: {e}")
        
        print(f"\n✅ Total ads collected: {len(self.collected_ads)}")
        return self.collected_ads

    def analyze_sentiment_hf(self, text):
        """Use Hugging Face free API for sentiment analysis"""
        if HUGGINGFACE_TOKEN == "your_hf_token_here":
            return self.analyze_sentiment_local(text)
        
        headers = {"Authorization": f"Bearer {HUGGINGFACE_TOKEN}"}
        
        try:
            response = requests.post(HUGGINGFACE_API_URL, headers=headers, json={"inputs": text})
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    sentiment_data = result[0]
                    return {
                        'label': sentiment_data.get('label', 'NEUTRAL'),
                        'score': sentiment_data.get('score', 0.5)
                    }
        except Exception as e:
            print(f"HF API error: {e}")
        
        return self.analyze_sentiment_local(text)
    
    def analyze_sentiment_local(self, text):
        """Local sentiment analysis using keyword matching"""
        positive_words = ['great', 'excellent', 'amazing', 'best', 'top', 'leading', 'proven', 'success', 'expert', 'professional']
        negative_words = ['difficult', 'hard', 'complex', 'challenging', 'struggle', 'problem']
        
        text_lower = text.lower()
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            return {'label': 'POSITIVE', 'score': 0.7 + (pos_count * 0.1)}
        elif neg_count > pos_count:
            return {'label': 'NEGATIVE', 'score': 0.3 - (neg_count * 0.1)}
        else:
            return {'label': 'NEUTRAL', 'score': 0.5}

    def analyze_ad_comprehensive(self, ad_data):
        """Comprehensive local NLP analysis"""
        title = ad_data.get('title', '')
        description = ad_data.get('description', '')
        full_text = f"{title} {description}".lower()
        
        word_count = len(full_text.split())
        char_count = len(full_text)
        
        sentiment = self.analyze_sentiment_hf(full_text)
        engagement_score = self.calculate_engagement_score(full_text)
        emotional_triggers = self.detect_emotional_triggers(full_text)
        cta_strength = self.analyze_cta_strength(full_text)
        urgency_level = self.detect_urgency(full_text)
        
        predicted_ctr = self.predict_ctr(engagement_score, sentiment['score'], cta_strength)
        estimated_impressions = self.estimate_daily_impressions(engagement_score)
        estimated_cpc = self.estimate_cpc(cta_strength, engagement_score)
        quality_score = self.calculate_quality_score(engagement_score, sentiment['score'], word_count)
        
        keywords = self.extract_keywords(full_text)
        missing_opportunities = self.find_missing_keywords(full_text)
        positioning = self.analyze_positioning(full_text)
        selling_points = self.extract_selling_points(title, description)
        
        return {
            'basic_metrics': {
                'word_count': word_count,
                'char_count': char_count,
                'reading_level': self.calculate_reading_level(full_text)
            },
            'sentiment_analysis': {
                'overall_sentiment': sentiment['label'],
                'confidence_score': round(sentiment['score'], 2),
                'emotional_tone': self.determine_tone(full_text)
            },
            'marketing_effectiveness': {
                'engagement_score': round(engagement_score, 1),
                'cta_strength': cta_strength,
                'urgency_level': urgency_level,
                'emotional_triggers_detected': emotional_triggers,
                'persuasion_elements': len([t for t in emotional_triggers if t in ['authority', 'social_proof']])
            },
            'performance_predictions': {
                'predicted_ctr_percent': round(predicted_ctr, 2),
                'estimated_daily_impressions': estimated_impressions,
                'estimated_cpc_inr': round(estimated_cpc, 2),
                'quality_score_prediction': round(quality_score, 1),
                'engagement_potential': 'high' if engagement_score > 7 else 'medium' if engagement_score > 4 else 'low'
            },
            'competitive_insights': {
                'positioning_strategy': positioning,
                'key_selling_points': selling_points,
                'target_audience': self.identify_target_audience(full_text),
                'competitive_advantages': self.identify_advantages(full_text)
            },
            'keyword_analysis': {
                'primary_keywords': keywords[:5],
                'keyword_density': self.calculate_keyword_density(full_text),
                'missing_opportunities': missing_opportunities,
                'seo_potential': 'high' if len(keywords) > 3 else 'medium'
            },
            'optimization_recommendations': self.generate_recommendations(engagement_score, cta_strength, urgency_level, emotional_triggers)
        }

    def calculate_engagement_score(self, text):
        """Calculate engagement score based on marketing keywords"""
        score = 1.0
        words = text.split()
        
        for word in words:
            if word in self.keyword_weights:
                score += self.keyword_weights[word]
        
        if re.search(r'\d+', text):
            score += 1.0
        if '?' in text:
            score += 0.5
            
        return min(score, 10.0)
    
    def detect_emotional_triggers(self, text):
        """Detect psychological triggers in ad copy"""
        detected_triggers = []
        
        for trigger_type, keywords in self.emotional_triggers.items():
            if any(keyword in text for keyword in keywords):
                detected_triggers.append(trigger_type)
        
        return detected_triggers
    
    def analyze_cta_strength(self, text):
        """Analyze call-to-action strength"""
        strong_ctas = ['join now', 'get started', 'enroll today', 'register now', 'start learning', 'buy now']
        medium_ctas = ['learn more', 'discover', 'explore', 'find out', 'see more', 'view details']
        weak_ctas = ['visit', 'check', 'see', 'view', 'browse']
        
        if any(cta in text for cta in strong_ctas):
            return 'Strong'
        elif any(cta in text for cta in medium_ctas):
            return 'Medium'
        elif any(cta in text for cta in weak_ctas):
            return 'Weak'
        else:
            return 'None'
    
    def detect_urgency(self, text):
        """Detect urgency indicators"""
        high_urgency = ['deadline', 'expires', 'limited time', 'hurry', 'last chance', 'today only']
        medium_urgency = ['now', 'today', 'soon', 'quickly', 'immediate']
        
        if any(term in text for term in high_urgency):
            return 'High'
        elif any(term in text for term in medium_urgency):
            return 'Medium'
        else:
            return 'Low'
    
    def predict_ctr(self, engagement_score, sentiment_score, cta_strength):
        """Predict CTR based on content analysis"""
        base_ctr = 1.5
        engagement_factor = engagement_score / 10.0
        sentiment_factor = sentiment_score if sentiment_score > 0.5 else 0.5
        cta_multipliers = {'Strong': 1.8, 'Medium': 1.3, 'Weak': 1.0, 'None': 0.7}
        cta_factor = cta_multipliers.get(cta_strength, 1.0)
        
        predicted_ctr = base_ctr * engagement_factor * sentiment_factor * cta_factor
        return min(predicted_ctr, 8.0)
    
    def estimate_daily_impressions(self, engagement_score):
        """Estimate daily impressions based on content quality"""
        base_impressions = random.randint(3000, 12000)
        quality_multiplier = 1 + (engagement_score / 15.0)
        return int(base_impressions * quality_multiplier)
    
    def estimate_cpc(self, cta_strength, engagement_score):
        """Estimate cost per click in Indian Rupees"""
        base_cost = random.uniform(20, 50)
        quality_factor = max(0.6, 1.2 - (engagement_score / 20.0))
        cta_factors = {'Strong': 1.3, 'Medium': 1.1, 'Weak': 0.9, 'None': 0.8}
        cta_factor = cta_factors.get(cta_strength, 1.0)
        
        return base_cost * quality_factor * cta_factor
    
    def calculate_quality_score(self, engagement_score, sentiment_score, word_count):
        """Calculate Google Ads style quality score"""
        relevance_score = min(engagement_score, 10)
        expected_ctr_score = sentiment_score * 10
        length_penalty = 1.0 if 5 <= word_count <= 25 else 0.8 if word_count < 5 else 0.9
        
        quality_score = ((relevance_score + expected_ctr_score) / 2) * length_penalty
        return min(quality_score, 10.0)
    
    def extract_keywords(self, text):
        """Extract important keywords"""
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        stop_words = {'the', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'a', 'an', 'this', 'that', 'you', 'your', 'our'}
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        return [kw for kw, count in Counter(keywords).most_common(10)]
    
    def find_missing_keywords(self, text):
        """Find high-value keywords that competitors might be missing"""
        high_value_keywords = [
            'certification', 'job guarantee', 'placement', 'internship',
            'mentor', 'live classes', 'doubt solving', 'project based',
            'industry expert', 'hands on', 'practical', 'real world'
        ]
        return [kw for kw in high_value_keywords if kw.replace(' ', '') not in text.replace(' ', '')][:5]
    
    def analyze_positioning(self, text):
        """Analyze competitive positioning"""
        premium_indicators = ['expert', 'professional', 'certified', 'advanced', 'comprehensive']
        budget_indicators = ['free', 'affordable', 'cheap', 'low cost', 'budget']
        
        premium_count = sum(1 for indicator in premium_indicators if indicator in text)
        budget_count = sum(1 for indicator in budget_indicators if indicator in text)
        
        return 'Premium' if premium_count > budget_count else 'Budget' if budget_count > premium_count else 'Mainstream'
    
    def extract_selling_points(self, title, description):
        """Extract key selling points"""
        text = f"{title} {description}".lower()
        selling_point_patterns = [
            r'(\d+)\s*(hours?|weeks?|months?)',
            r'(\d+)\s*(projects?|assignments?)',
            r'(certificate|certification)',
            r'(job|placement|career)',
            r'(beginner|advanced|intermediate)',
            r'(practical|hands-on|real-world)'
        ]
        
        selling_points = []
        for pattern in selling_point_patterns:
            matches = re.findall(pattern, text)
            if matches:
                selling_points.extend([match if isinstance(match, str) else ' '.join(match) for match in matches])
        
        return selling_points[:5]
    
    def identify_target_audience(self, text):
        """Identify target audience"""
        audiences = {
            'beginners': ['beginner', 'start', 'basic', 'introduction', 'learn from scratch'],
            'professionals': ['professional', 'career', 'advance', 'experienced', 'workplace'],
            'students': ['student', 'college', 'university', 'academic', 'degree'],
            'job_seekers': ['job', 'employment', 'career change', 'placement', 'hiring']
        }
        
        scores = {audience: sum(1 for keyword in keywords if keyword in text) for audience, keywords in audiences.items()}
        return max(scores, key=scores.get) if max(scores.values()) > 0 else 'general'
    
    def identify_advantages(self, text):
        """Identify competitive advantages mentioned"""
        advantage_patterns = {
            'Free Content': ['free', 'no cost', 'without payment'],
            'Certification': ['certificate', 'certified', 'certification'],
            'Expert Instruction': ['expert', 'industry professional', 'experienced'],
            'Practical Learning': ['hands-on', 'practical', 'real-world', 'projects'],
            'Career Support': ['job', 'placement', 'career', 'hiring'],
            'Flexible Learning': ['self-paced', 'flexible', 'anytime', 'anywhere']
        }
        
        return [advantage for advantage, keywords in advantage_patterns.items() if any(keyword in text for keyword in keywords)]
    
    def calculate_keyword_density(self, text):
        """Calculate keyword density for SEO analysis"""
        words = text.split()
        if not words:
            return 0
        education_keywords = ['course', 'learn', 'training', 'certification', 'skill', 'python', 'data', 'science']
        keyword_count = sum(1 for word in words if word in education_keywords)
        return round((keyword_count / len(words)) * 100, 1)
    
    def calculate_reading_level(self, text):
        """Calculate reading difficulty"""
        words = text.split()
        if not words:
            return 'Easy'
        avg_word_length = sum(len(word) for word in words) / len(words)
        return 'Easy' if avg_word_length < 4.5 else 'Medium' if avg_word_length < 6 else 'Difficult'
    
    def determine_tone(self, text):
        """Determine emotional tone of the ad"""
        tones = {
            'Professional': ['professional', 'expert', 'industry', 'certified', 'official'],
            'Friendly': ['help', 'support', 'guide', 'assist', 'welcome'],
            'Urgent': ['now', 'today', 'limited', 'hurry', 'deadline'],
            'Exciting': ['amazing', 'incredible', 'transform', 'breakthrough', 'revolutionize']
        }
        
        tone_scores = {tone: sum(1 for keyword in keywords if keyword in text) for tone, keywords in tones.items()}
        return max(tone_scores, key=tone_scores.get) if max(tone_scores.values()) > 0 else 'Neutral'
    
    def generate_recommendations(self, engagement_score, cta_strength, urgency_level, emotional_triggers):
        """Generate optimization recommendations"""
        recommendations = []
        if engagement_score < 5:
            recommendations.append("Increase engagement by adding power words like 'certified', 'expert', or 'proven'")
        if cta_strength in ['Weak', 'None']:
            recommendations.append("Strengthen call-to-action with action words like 'Start Learning Now' or 'Get Certified Today'")
        if urgency_level == 'Low':
            recommendations.append("Add urgency with phrases like 'Limited Time Offer' or 'Enroll Today'")
        if 'social_proof' not in emotional_triggers:
            recommendations.append("Include social proof like '10,000+ students' or 'Industry-recognized'")
        if 'authority' not in emotional_triggers:
            recommendations.append("Add authority indicators like 'Expert-led' or 'Industry-certified'")
        if not recommendations:
            recommendations.append("Ad copy is well-optimized! Consider A/B testing different variations.")
        return recommendations

def generate_summary_report(analyzed_ads):
    """Generate a summary report of all analyzed ads"""
    print("\n📋 Generating Summary Report...")
    
    total_ads = len(analyzed_ads)
    platforms = Counter(ad['ad_data']['platform'] for ad in analyzed_ads)
    engagement_scores = [ad['analysis']['marketing_effectiveness']['engagement_score'] for ad in analyzed_ads]
    predicted_ctrs = [ad['analysis']['performance_predictions']['predicted_ctr_percent'] for ad in analyzed_ads]
    quality_scores = [ad['analysis']['performance_predictions']['quality_score_prediction'] for ad in analyzed_ads]
    sentiments = Counter(ad['analysis']['sentiment_analysis']['overall_sentiment'] for ad in analyzed_ads)
    cta_strengths = Counter(ad['analysis']['marketing_effectiveness']['cta_strength'] for ad in analyzed_ads)
    urgency_levels = Counter(ad['analysis']['marketing_effectiveness']['urgency_level'] for ad in analyzed_ads)
    
    avg_engagement = sum(engagement_scores) / total_ads if total_ads > 0 else 0
    avg_ctr = sum(predicted_ctrs) / total_ads if total_ads > 0 else 0
    avg_quality = sum(quality_scores) / total_ads if total_ads > 0 else 0
    
    top_ad = max(analyzed_ads, key=lambda x: x['analysis']['marketing_effectiveness']['engagement_score'], default=None)
    
    print("\n📊 Summary Report")
    print("=" * 50)
    print(f"Total Ads Analyzed: {total_ads}")
    print(f"Platforms Analyzed: {', '.join(f'{platform} ({count})' for platform, count in platforms.items())}")
    print(f"Average Engagement Score: {avg_engagement:.1f}/10")
    print(f"Average Predicted CTR: {avg_ctr:.2f}%")
    print(f"Average Quality Score: {avg_quality:.1f}/10")
    
    print("\n🎭 Sentiment Distribution:")
    for sentiment, count in sentiments.items():
        print(f"   • {sentiment}: {count} ({(count/total_ads)*100:.1f}%)")
    
    print("\n👆 CTA Strength Distribution:")
    for strength, count in cta_strengths.items():
        print(f"   • {strength}: {count} ({(count/total_ads)*100:.1f}%)")
    
    print("\n⏰ Urgency Level Distribution:")
    for level, count in urgency_levels.items():
        print(f"   • {level}: {count} ({(count/total_ads)*100:.1f}%)")
    
    if top_ad:
        print("\n🏆 Top Performing Ad:")
        print(f"   • Title: {top_ad['ad_data']['title'][:50]}...")
        print(f"   • Platform: {top_ad['ad_data']['platform']}")
        print(f"   • Database ID: {top_ad['db_id']}")
        print(f"   • Engagement Score: {top_ad['analysis']['marketing_effectiveness']['engagement_score']}/10")
        print(f"   • Predicted CTR: {top_ad['analysis']['performance_predictions']['predicted_ctr_percent']}%")
        print(f"   • Key Selling Points: {', '.join(top_ad['analysis']['competitive_insights']['key_selling_points'][:3])}")
    
    all_keywords = []
    for ad in analyzed_ads:
        all_keywords.extend(ad['analysis']['keyword_analysis']['primary_keywords'])
    common_keywords = Counter(all_keywords).most_common(5)
    
    print("\n🔑 Most Common Keywords:")
    for keyword, count in common_keywords:
        print(f"   • {keyword}: {count} ads")
    
    all_recommendations = []
    for ad in analyzed_ads:
        all_recommendations.extend(ad['analysis']['optimization_recommendations'])
    common_recommendations = Counter(all_recommendations).most_common(3)
    
    print("\n💡 Top Optimization Recommendations:")
    for rec, count in common_recommendations:
        print(f"   • {rec} (suggested for {count} ads)")
    
    summary_data = {
        'total_ads': total_ads,
        'platforms': platforms,
        'avg_engagement': avg_engagement,
        'avg_ctr': avg_ctr,
        'avg_quality': avg_quality,
        'sentiments': sentiments,
        'cta_strengths': cta_strengths,
        'urgency_levels': urgency_levels,
        'common_keywords': [f"{kw}: {count}" for kw, count in common_keywords],
        'top_recommendations': [f"{rec} ({count} ads)" for rec, count in common_recommendations],
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }
    
    print("\n✅ Analysis Complete!")
    return summary_data

def print_database_stats(analyzer):
    """Print database statistics"""
    print("\n🗄️ Database Statistics:")
    print("=" * 30)
    
    ads = analyzer.db_ops.get_ads_from_db()
    print(f"📊 Total Ads in Database: {len(ads)}")
    
    top_ads = analyzer.db_ops.get_top_performing_ads(3)
    print(f"\n🏆 Top 3 Performing Ads (by Engagement Score):")
    for i, (title, platform, engagement, ctr, quality) in enumerate(top_ads, 1):
        print(f"   {i}. {title[:40]}... ({platform})")
        print(f"      Engagement: {engagement:.1f} | CTR: {ctr:.2f}% | Quality: {quality:.1f}")
    
    platform_stats = analyzer.db_ops.get_platform_performance()
    print(f"\n📱 Platform Performance:")
    for platform, count, avg_eng, avg_ctr, avg_qual in platform_stats:
        print(f"   • {platform}: {count} ads")
        print(f"     Avg Engagement: {avg_eng:.1f} | Avg CTR: {avg_ctr:.2f}% | Avg Quality: {avg_qual:.1f}")

def analyze_all_ads():
    """Main function to analyze all collected ads"""
    print("🚀 Starting Free NLP Ad Analysis with SQLite Storage...")
    print("📊 Using advanced local NLP + optional Hugging Face API...")
    
    analyzer = FreeNLPAdAnalyzer()
    collected_ads = analyzer.fetch_ads_from_platforms()
    
    if not collected_ads:
        print("❌ No ads found to analyze")
        return
    
    print(f"\n🤖 Analyzing {len(collected_ads)} ads with Free NLP...")
    analyzed_ads = []
    
    for i, ad in enumerate(collected_ads, 1):
        print(f"\n📊 Analyzing Ad {i}/{len(collected_ads)}: {ad['title'][:40]}...")
        
        ad_id = analyzer.db_ops.save_ad_to_db(ad)
        analysis = analyzer.analyze_ad_comprehensive(ad)
        analyzer.db_ops.save_analysis_to_db(ad_id, analysis, ad['timestamp'])
        
        basic = analysis['basic_metrics']
        sentiment = analysis['sentiment_analysis']
        marketing = analysis['marketing_effectiveness']
        performance = analysis['performance_predictions']
        competitive = analysis['competitive_insights']
        keywords = analysis['keyword_analysis']
        
        print(f"🏆 Platform: {ad['platform']} | Type: {ad['type']} | DB ID: {ad_id}")
        print(f"📝 Content: {basic['word_count']} words | Reading Level: {basic['reading_level']}")
        print(f"🎭 Sentiment: {sentiment['overall_sentiment']} ({sentiment['confidence_score']}) | Tone: {sentiment['emotional_tone']}")
        print(f"📈 Engagement Score: {marketing['engagement_score']}/10")
        print(f"👆 CTA Strength: {marketing['cta_strength']} | Urgency: {marketing['urgency_level']}")
        print(f"🧠 Emotional Triggers: {', '.join(marketing['emotional_triggers_detected']) if marketing['emotional_triggers_detected'] else 'None'}")
        
        print(f"\n💹 Performance Predictions:")
        print(f"   • CTR: {performance['predicted_ctr_percent']}%")
        print(f"   • Daily Impressions: {performance['estimated_daily_impressions']:,}")
        print(f"   • CPC: ₹{performance['estimated_cpc_inr']}")
        print(f"   • Quality Score: {performance['quality_score_prediction']}/10")
        print(f"   • Engagement Potential: {performance['engagement_potential'].title()}")
        
        print(f"\n🎯 Competitive Intelligence:")
        print(f"   • Positioning: {competitive['positioning_strategy']}")
        print(f"   • Target Audience: {competitive['target_audience'].title()}")
        print(f"   • Selling Points: {', '.join(competitive['key_selling_points'][:3])}")
        print(f"   • Advantages: {', '.join(competitive['competitive_advantages'][:3])}")
        
        print(f"\n🔑 Keywords: {', '.join(keywords['primary_keywords'][:5])}")
        print(f"💡 Recommendations: {'; '.join(analysis['optimization_recommendations'][:2])}")
        print(f"🔗 Link: {ad['link'][:60]}...")
        
        analyzed_ads.append({
            'ad_data': ad,
            'analysis': analysis,
            'db_id': ad_id
        })
        
        print("-" * 60)
    
    summary_data = generate_summary_report(analyzed_ads)
    analyzer.db_ops.save_summary_to_db(summary_data)
    
    output_data = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'total_ads_analyzed': len(analyzed_ads),
        'analysis_method': 'Free NLP + Local Processing + SQLite Storage',
        'database_file': analyzer.db_ops.db_name,
        'detailed_results': analyzed_ads
    }
    
    with open('competitor_ad_analysis_free.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n💾 Complete analysis saved to:")
    print(f"   📄 JSON: competitor_ad_analysis_free.json")
    print(f"   🗄️ SQLite: {analyzer.db_ops.db_name}")
    
    print_database_stats(analyzer)
    analyzer.db_ops.query_database_examples()
    analyzer.db_ops.export_to_csv()
    analyzer.db_ops.backup_database()

if __name__ == "__main__":
    analyze_all_ads()