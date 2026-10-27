import sqlite3
import csv
import shutil
import datetime
import json
from collections import Counter

class DatabaseOperations:
    def __init__(self, db_name="ad_analysis.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Initialize SQLite database with required tables"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                platform TEXT,
                ad_type TEXT,
                title TEXT,
                description TEXT,
                link TEXT,
                position TEXT,
                channel TEXT,
                views TEXT,
                duration TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad_id INTEGER,
                timestamp TEXT,
                word_count INTEGER,
                char_count INTEGER,
                reading_level TEXT,
                overall_sentiment TEXT,
                sentiment_confidence REAL,
                emotional_tone TEXT,
                engagement_score REAL,
                cta_strength TEXT,
                urgency_level TEXT,
                emotional_triggers TEXT,
                predicted_ctr REAL,
                estimated_daily_impressions INTEGER,
                estimated_cpc REAL,
                quality_score REAL,
                engagement_potential TEXT,
                positioning_strategy TEXT,
                target_audience TEXT,
                key_selling_points TEXT,
                competitive_advantages TEXT,
                primary_keywords TEXT,
                keyword_density REAL,
                missing_opportunities TEXT,
                optimization_recommendations TEXT,
                FOREIGN KEY (ad_id) REFERENCES ads (id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS summary_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                total_ads_analyzed INTEGER,
                avg_engagement_score REAL,
                avg_predicted_ctr REAL,
                avg_quality_score REAL,
                platform_distribution TEXT,
                sentiment_distribution TEXT,
                cta_distribution TEXT,
                urgency_distribution TEXT,
                common_keywords TEXT,
                top_recommendations TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"✅ Database initialized: {self.db_name}")

    def save_ad_to_db(self, ad_data):
        """Save ad data to SQLite database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO ads (timestamp, platform, ad_type, title, description, link, position, channel, views, duration)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ad_data['timestamp'],
            ad_data.get('platform', ''),
            ad_data.get('type', ''),
            ad_data.get('title', ''),
            ad_data.get('description', ''),
            ad_data.get('link', ''),
            str(ad_data.get('position', '')),
            ad_data.get('channel', ''),
            ad_data.get('views', ''),
            ad_data.get('duration', '')
        ))
        
        ad_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return ad_id

    def save_analysis_to_db(self, ad_id, analysis, timestamp):
        """Save analysis results to SQLite database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        basic = analysis['basic_metrics']
        sentiment = analysis['sentiment_analysis']
        marketing = analysis['marketing_effectiveness']
        performance = analysis['performance_predictions']
        competitive = analysis['competitive_insights']
        keywords = analysis['keyword_analysis']
        
        cursor.execute('''
            INSERT INTO analysis_results (
                ad_id, timestamp, word_count, char_count, reading_level,
                overall_sentiment, sentiment_confidence, emotional_tone,
                engagement_score, cta_strength, urgency_level, emotional_triggers,
                predicted_ctr, estimated_daily_impressions, estimated_cpc, quality_score, engagement_potential,
                positioning_strategy, target_audience, key_selling_points, competitive_advantages,
                primary_keywords, keyword_density, missing_opportunities, optimization_recommendations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            ad_id,
            timestamp,
            basic['word_count'],
            basic['char_count'],
            basic['reading_level'],
            sentiment['overall_sentiment'],
            sentiment['confidence_score'],
            sentiment['emotional_tone'],
            marketing['engagement_score'],
            marketing['cta_strength'],
            marketing['urgency_level'],
            json.dumps(marketing['emotional_triggers_detected']),
            performance['predicted_ctr_percent'],
            performance['estimated_daily_impressions'],
            performance['estimated_cpc_inr'],
            performance['quality_score_prediction'],
            performance['engagement_potential'],
            competitive['positioning_strategy'],
            competitive['target_audience'],
            json.dumps(competitive['key_selling_points']),
            json.dumps(competitive['competitive_advantages']),
            json.dumps(keywords['primary_keywords']),
            keywords['keyword_density'],
            json.dumps(keywords['missing_opportunities']),
            json.dumps(analysis['optimization_recommendations'])
        ))
        
        conn.commit()
        conn.close()

    def save_summary_to_db(self, summary_data):
        """Save summary report to SQLite database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO summary_reports (
                timestamp, total_ads_analyzed, avg_engagement_score, avg_predicted_ctr, avg_quality_score,
                platform_distribution, sentiment_distribution, cta_distribution, urgency_distribution,
                common_keywords, top_recommendations
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            summary_data['timestamp'],
            summary_data['total_ads'],
            summary_data['avg_engagement'],
            summary_data['avg_ctr'],
            summary_data['avg_quality'],
            json.dumps(dict(summary_data['platforms'])),
            json.dumps(dict(summary_data['sentiments'])),
            json.dumps(dict(summary_data['cta_strengths'])),
            json.dumps(dict(summary_data['urgency_levels'])),
            json.dumps(summary_data['common_keywords']),
            json.dumps(summary_data['top_recommendations'])
        ))
        
        conn.commit()
        conn.close()
        print(f"✅ Summary report saved to database")

    def get_ads_from_db(self, limit=None):
        """Retrieve ads from database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        query = '''
            SELECT a.*, ar.engagement_score, ar.predicted_ctr, ar.quality_score
            FROM ads a
            LEFT JOIN analysis_results ar ON a.id = ar.ad_id
            ORDER BY a.timestamp DESC
        '''
        
        if limit:
            query += f' LIMIT {limit}'
        
        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()
        
        return results

    def get_top_performing_ads(self, limit=5):
        """Get top performing ads from database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.title, a.platform, ar.engagement_score, ar.predicted_ctr, ar.quality_score
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            ORDER BY ar.engagement_score DESC
            LIMIT ?
        ''', (limit,))
        
        results = cursor.fetchall()
        conn.close()
        
        return results

    def get_platform_performance(self):
        """Get performance metrics by platform"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                a.platform,
                COUNT(*) as ad_count,
                AVG(ar.engagement_score) as avg_engagement,
                AVG(ar.predicted_ctr) as avg_ctr,
                AVG(ar.quality_score) as avg_quality
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            GROUP BY a.platform
            ORDER BY avg_engagement DESC
        ''')
        
        results = cursor.fetchall()
        conn.close()
        
        return results

    def export_to_csv(self):
        """Export all database data to CSV file"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                a.id, a.timestamp, a.platform, a.ad_type, a.title, a.description, a.link, a.position, 
                a.channel, a.views, a.duration,
                ar.word_count, ar.char_count, ar.reading_level, ar.overall_sentiment, ar.sentiment_confidence, 
                ar.emotional_tone, ar.engagement_score, ar.cta_strength, ar.urgency_level, ar.emotional_triggers, 
                ar.predicted_ctr, ar.estimated_daily_impressions, ar.estimated_cpc, ar.quality_score, 
                ar.engagement_potential, ar.positioning_strategy, ar.target_audience, ar.key_selling_points, 
                ar.competitive_advantages, ar.primary_keywords, ar.keyword_density, ar.missing_opportunities, 
                ar.optimization_recommendations
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            ORDER BY ar.engagement_score DESC
        ''')
        
        results = cursor.fetchall()
        
        with open('ad_analysis_results.csv', 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'ID', 'Timestamp', 'Platform', 'Ad Type', 'Title', 'Description', 'Link', 'Position', 
                'Channel', 'Views', 'Duration', 'Word Count', 'Char Count', 'Reading Level', 
                'Sentiment', 'Sentiment Confidence', 'Emotional Tone', 'Engagement Score', 
                'CTA Strength', 'Urgency Level', 'Emotional Triggers', 'Predicted CTR', 
                'Estimated Daily Impressions', 'Estimated CPC', 'Quality Score', 'Engagement Potential', 
                'Positioning Strategy', 'Target Audience', 'Key Selling Points', 'Competitive Advantages', 
                'Primary Keywords', 'Keyword Density', 'Missing Opportunities', 'Optimization Recommendations'
            ])
            
            for row in results:
                writer.writerow(row)
        
        print(f"📊 Exported {len(results)} records to ad_analysis_results.csv")
        conn.close()

    def backup_database(self):
        """Create a backup of the database"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"ad_analysis_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_name, backup_name)
            print(f"✅ Database backed up to: {backup_name}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")

    def clean_old_data(self, days_old=30):
        """Clean data older than specified days"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM analysis_results 
            WHERE ad_id IN (
                SELECT id FROM ads 
                WHERE datetime(timestamp) < datetime('now', '-{} days')
            )
        '''.format(days_old))
        
        cursor.execute('''
            DELETE FROM ads 
            WHERE datetime(timestamp) < datetime('now', '-{} days')
        '''.format(days_old))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"🧹 Cleaned {deleted_count} old records (older than {days_old} days)")

    def query_database_examples(self):
        """Example function showing how to query the database"""
        print("\n🔍 Database Query Examples:")
        print("=" * 40)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.title, a.platform, ar.engagement_score, ar.predicted_ctr
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            WHERE a.platform = ?
            ORDER BY ar.engagement_score DESC
        ''', ('Google',))
        
        google_ads = cursor.fetchall()
        print(f"\n📌 Google Ads (Top 3 by Engagement):")
        for title, platform, engagement, ctr in google_ads[:3]:
            print(f"   • {title[:40]}... | Engagement: {engagement:.1f} | CTR: {ctr:.2f}%")
        
        cursor.execute('''
            SELECT a.title, a.platform, ar.urgency_level, ar.engagement_score
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            WHERE ar.urgency_level = 'High'
            ORDER BY ar.engagement_score DESC
        ''')
        
        high_urgency_ads = cursor.fetchall()
        print(f"\n⏰ High Urgency Ads:")
        for title, platform, urgency, engagement in high_urgency_ads:
            print(f"   • {title[:40]}... ({platform}) | Engagement: {engagement:.1f}")
        
        cursor.execute('''
            SELECT a.title, ar.overall_sentiment, ar.sentiment_confidence, ar.engagement_score
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            WHERE ar.overall_sentiment = 'POSITIVE'
            ORDER BY ar.sentiment_confidence DESC
            LIMIT 3
        ''')
        
        positive_ads = cursor.fetchall()
        print(f"\n😊 Most Positive Ads:")
        for title, sentiment, confidence, engagement in positive_ads:
            print(f"   • {title[:40]}...")
            print(f"     Sentiment: {sentiment} ({confidence:.2f}) | Engagement: {engagement:.1f}")
        
        cursor.execute('''
            SELECT 
                ar.cta_strength,
                COUNT(*) as ad_count,
                AVG(ar.engagement_score) as avg_engagement,
                AVG(ar.predicted_ctr) as avg_ctr
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            GROUP BY ar.cta_strength
            ORDER BY avg_engagement DESC
        ''')
        
        cta_performance = cursor.fetchall()
        print(f"\n👆 Performance by CTA Strength:")
        for cta_strength, count, avg_eng, avg_ctr in cta_performance:
            print(f"   • {cta_strength}: {count} ads")
            print(f"     Avg Engagement: {avg_eng:.1f} | Avg CTR: {avg_ctr:.2f}%")
        
        cursor.execute('''
            SELECT a.title, ar.primary_keywords, ar.keyword_density, ar.engagement_score
            FROM ads a
            JOIN analysis_results ar ON a.id = ar.ad_id
            ORDER BY ar.keyword_density DESC
            LIMIT 5
        ''')
        
        keyword_rich_ads = cursor.fetchall()
        print(f"\n🔑 Top 5 Keyword-Rich Ads:")
        for title, keywords_json, density, engagement in keyword_rich_ads:
            keywords = json.loads(keywords_json) if keywords_json else []
            print(f"   • {title[:40]}...")
            print(f"     Keywords: {', '.join(keywords[:3])} | Density: {density}% | Engagement: {engagement:.1f}")
        
        conn.close()