"""
Supabase Analytics Module for Beige AI
Production-ready analytics and monitoring for feedback logging system.

Usage:
    from backend.integrations.supabase_analytics import Analytics
    
    analytics = Analytics()
    
    # Get recent logs
    recent = analytics.get_recent_logs()
    
    # Analyze model performance
    performance = analytics.get_model_performance()
    
    # Analyze popular cakes
    popular = analytics.get_popular_cakes()
    
    # Analyze latency
    latency = analytics.get_latency_analysis()
    
    # Analyze A/B tests
    ab_tests = analytics.get_ab_test_results()
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()


class Analytics:
    """Production analytics module for Beige AI feedback system."""
    
    def __init__(self):
        """Initialize Supabase client."""
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_KEY")
        
        if not self.url or not self.key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")
        
        self.client = create_client(self.url, self.key)
    
    # ========================================================================
    # QUERY 1: RECENT LOGS
    # ========================================================================
    
    def get_recent_logs(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent feedback logs for monitoring.
        
        Returns latest N records with key fields:
        - created_at: Timestamp of recommendation
        - session_id: User session identifier
        - recommended_cake: Primary recommendation
        - user_feedback: User rating (1-5, or None if not rated)
        - model_version: ML model that made recommendation
        - latency_ms: Inference time in milliseconds
        
        Args:
            limit: Number of recent logs to retrieve (default: 10)
        
        Returns:
            List of dicts with log records, newest first
        """
        try:
            response = self.client.table('feedback_logs').select(
                'created_at, session_id, recommended_cake, user_feedback, model_version, latency_ms'
            ).order('created_at', desc=True).limit(limit).execute()
            
            return response.data if response.data else []
        except Exception as e:
            print(f"Error fetching recent logs: {str(e)}")
            return []
    
    # ========================================================================
    # QUERY 2: MODEL PERFORMANCE
    # ========================================================================
    
    def get_model_performance(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Compare model performance metrics over time.
        
        Metrics:
        - model_version: Unique model identifier
        - recommendations: Total number of recommendations
        - avg_rating: Average user feedback score (1-5)
        - avg_latency_ms: Average inference time
        - satisfaction_rate: % of recommendations with feedback >= 4
        
        Filters:
        - Last N hours (default: 24)
        - Only records with user feedback
        
        Args:
            hours: Look-back window in hours (default: 24)
        
        Returns:
            List of dicts with model performance metrics
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            since_str = since.isoformat()
            
            # Use raw SQL for aggregation
            query = f"""
            SELECT 
              model_version,
              COUNT(*) as recommendations,
              ROUND(AVG(CAST(user_feedback AS NUMERIC)), 2) as avg_rating,
              ROUND(AVG(CAST(latency_ms AS NUMERIC)), 0) as avg_latency_ms,
              ROUND(
                COUNT(CASE WHEN user_feedback >= 4 THEN 1 END)::float / 
                NULLIF(COUNT(CASE WHEN user_feedback IS NOT NULL THEN 1 END), 0),
                3
              ) as satisfaction_rate
            FROM feedback_logs
            WHERE created_at > '{since_str}'
              AND user_feedback IS NOT NULL
            GROUP BY model_version
            ORDER BY avg_rating DESC
            """
            
            response = self.client.rpc('query_result', {'sql': query}).execute()
            return response.data if response.data else []
        except:
            # Fallback: Return empty if direct SQL not available
            return self._fallback_get_model_performance(hours)
    
    def _fallback_get_model_performance(self, hours: int) -> List[Dict[str, Any]]:
        """Fallback aggregation using client-side processing."""
        since = datetime.utcnow() - timedelta(hours=hours)
        
        response = self.client.table('feedback_logs').select('*').gte(
            'created_at', since.isoformat()
        ).is_('user_feedback', 'not.is.null').execute()
        
        if not response.data:
            return []
        
        # Group by model_version
        models = {}
        for record in response.data:
            version = record.get('model_version', 'unknown')
            if version not in models:
                models[version] = {
                    'model_version': version,
                    'recommendations': 0,
                    'ratings': [],
                    'latencies': []
                }
            
            models[version]['recommendations'] += 1
            if record.get('user_feedback'):
                models[version]['ratings'].append(record['user_feedback'])
            if record.get('latency_ms'):
                models[version]['latencies'].append(record['latency_ms'])
        
        # Calculate metrics
        results = []
        for version, data in models.items():
            avg_rating = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else None
            avg_latency = sum(data['latencies']) / len(data['latencies']) if data['latencies'] else None
            satisfaction = len([r for r in data['ratings'] if r >= 4]) / len(data['ratings']) if data['ratings'] else 0
            
            results.append({
                'model_version': version,
                'recommendations': data['recommendations'],
                'avg_rating': round(avg_rating, 2) if avg_rating else None,
                'avg_latency_ms': round(avg_latency, 0) if avg_latency else None,
                'satisfaction_rate': round(satisfaction, 3)
            })
        
        return sorted(results, key=lambda x: x.get('avg_rating') or 0, reverse=True)
    
    # ========================================================================
    # QUERY 3: POPULAR CAKES
    # ========================================================================
    
    def get_popular_cakes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Identify most successful cake recommendations.
        
        Metrics:
        - recommended_cake: Cake name
        - times_recommended: Total recommendations
        - avg_feedback: Average user rating
        - success_rate: % of recommendations with feedback >= 4
        
        Returns:
            Top N cakes by success rate
        
        Args:
            limit: Number of top cakes to return (default: 5)
        """
        try:
            response = self.client.table('feedback_logs').select('*').is_(
                'user_feedback', 'not.is.null'
            ).execute()
            
            if not response.data:
                return []
            
            # Group by cake
            cakes = {}
            for record in response.data:
                cake = record.get('recommended_cake', 'unknown')
                if cake not in cakes:
                    cakes[cake] = {
                        'recommended_cake': cake,
                        'times_recommended': 0,
                        'ratings': []
                    }
                
                cakes[cake]['times_recommended'] += 1
                if record.get('user_feedback'):
                    cakes[cake]['ratings'].append(record['user_feedback'])
            
            # Calculate metrics
            results = []
            for cake, data in cakes.items():
                avg_feedback = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
                success_rate = len([r for r in data['ratings'] if r >= 4]) / len(data['ratings']) if data['ratings'] else 0
                
                results.append({
                    'recommended_cake': cake,
                    'times_recommended': data['times_recommended'],
                    'avg_feedback': round(avg_feedback, 2),
                    'success_rate': round(success_rate, 3)
                })
            
            return sorted(results, key=lambda x: x['success_rate'], reverse=True)[:limit]
        except Exception as e:
            print(f"Error fetching popular cakes: {str(e)}")
            return []
    
    # ========================================================================
    # QUERY 4: LATENCY ANALYSIS
    # ========================================================================
    
    def get_latency_analysis(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Analyze inference latency distribution by model.
        
        Metrics (percentiles):
        - p25: 25th percentile
        - p50: Median (50th percentile)
        - p75: 75th percentile
        - p95: 95th percentile
        - max_latency: Maximum recorded latency
        
        Use cases:
        - Identify slow models
        - Set performance thresholds
        - Detect degradation over time
        
        Args:
            hours: Look-back window in hours (default: 24)
        
        Returns:
            List of dicts with latency percentiles by model
        """
        try:
            since = datetime.utcnow() - timedelta(hours=hours)
            
            response = self.client.table('feedback_logs').select(
                'model_version, latency_ms'
            ).gte('created_at', since.isoformat()).execute()
            
            if not response.data:
                return []
            
            # Group by model
            models = {}
            for record in response.data:
                version = record.get('model_version', 'unknown')
                latency = record.get('latency_ms')
                
                if latency is None:
                    continue
                
                if version not in models:
                    models[version] = []
                
                models[version].append(latency)
            
            # Calculate percentiles
            results = []
            for version, latencies in models.items():
                latencies.sort()
                n = len(latencies)
                
                results.append({
                    'model_version': version,
                    'p25': round(latencies[int(n * 0.25)], 2),
                    'p50': round(latencies[int(n * 0.50)], 2),  # Median
                    'p75': round(latencies[int(n * 0.75)], 2),
                    'p95': round(latencies[int(n * 0.95)], 2),
                    'max_latency': max(latencies)
                })
            
            return results
        except Exception as e:
            print(f"Error fetching latency analysis: {str(e)}")
            return []
    
    # ========================================================================
    # QUERY 5: A/B TEST ANALYSIS
    # ========================================================================
    
    def get_ab_test_results(self) -> List[Dict[str, Any]]:
        """
        Analyze A/B test experiment results.
        
        Metrics:
        - experiment_id: Experiment identifier
        - model_version: Model being tested
        - sample_size: Number of recommendations in test
        - avg_feedback: Average user rating for variant
        - avg_latency: Average inference time
        
        Use cases:
        - Compare model variants
        - Validate improvements before deployment
        - Track experiment outcomes
        
        Returns:
            List of dicts with A/B test metrics
        """
        try:
            response = self.client.table('feedback_logs').select(
                'experiment_id, model_version, user_feedback, latency_ms'
            ).is_('experiment_id', 'not.is.null').is_(
                'user_feedback', 'not.is.null'
            ).execute()
            
            if not response.data:
                return []
            
            # Group by experiment_id and model_version
            experiments = {}
            for record in response.data:
                exp_id = record.get('experiment_id')
                version = record.get('model_version')
                key = (exp_id, version)
                
                if key not in experiments:
                    experiments[key] = {
                        'experiment_id': exp_id,
                        'model_version': version,
                        'sample_size': 0,
                        'ratings': [],
                        'latencies': []
                    }
                
                experiments[key]['sample_size'] += 1
                if record.get('user_feedback'):
                    experiments[key]['ratings'].append(record['user_feedback'])
                if record.get('latency_ms'):
                    experiments[key]['latencies'].append(record['latency_ms'])
            
            # Calculate metrics
            results = []
            for (exp_id, version), data in experiments.items():
                avg_feedback = sum(data['ratings']) / len(data['ratings']) if data['ratings'] else 0
                avg_latency = sum(data['latencies']) / len(data['latencies']) if data['latencies'] else 0
                
                results.append({
                    'experiment_id': exp_id,
                    'model_version': version,
                    'sample_size': data['sample_size'],
                    'avg_feedback': round(avg_feedback, 2),
                    'avg_latency': round(avg_latency, 0)
                })
            
            return sorted(results, key=lambda x: x['experiment_id'])
        except Exception as e:
            print(f"Error fetching A/B test results: {str(e)}")
            return []
    
    # ========================================================================
    # UTILITY: PRINT FORMATTED RESULTS
    # ========================================================================
    
    def print_recent_logs(self, limit: int = 10):
        """Print recent logs in formatted table."""
        logs = self.get_recent_logs(limit)
        
        if not logs:
            print("No recent logs found.")
            return
        
        print(f"\n📋 RECENT LOGS (Last {limit} records)\n")
        print(f"{'Timestamp':<20} {'Session':<10} {'Cake':<25} {'Rating':<7} {'Model':<15} {'Latency':<8}")
        print("-" * 95)
        
        for log in logs:
            timestamp = log.get('created_at', '')[:19]
            session = log.get('session_id', '')[:8]
            cake = (log.get('recommended_cake', '')[:23])
            rating = str(log.get('user_feedback') or '-')
            model = log.get('model_version', '')[:13]
            latency = f"{log.get('latency_ms', 0)}ms"
            
            print(f"{timestamp:<20} {session:<10} {cake:<25} {rating:<7} {model:<15} {latency:<8}")
    
    def print_model_performance(self, hours: int = 24):
        """Print model performance metrics."""
        perf = self.get_model_performance(hours)
        
        if not perf:
            print(f"No data for last {hours} hours.")
            return
        
        print(f"\n📊 MODEL PERFORMANCE (Last {hours}h)\n")
        print(f"{'Model':<20} {'Recs':<8} {'Avg Rating':<12} {'Avg Latency':<12} {'Satisfaction':<13}")
        print("-" * 65)
        
        for row in perf:
            model = row.get('model_version', '')[0:18]
            recs = row.get('recommendations', 0)
            rating = f"{row.get('avg_rating') or 'N/A'}"
            latency = f"{row.get('avg_latency_ms') or 'N/A'}ms"
            satisfaction = f"{(row.get('satisfaction_rate') or 0) * 100:.1f}%"
            
            print(f"{model:<20} {recs:<8} {rating:<12} {latency:<12} {satisfaction:<13}")
    
    def print_popular_cakes(self, limit: int = 5):
        """Print popular cakes."""
        cakes = self.get_popular_cakes(limit)
        
        if not cakes:
            print("No cake data found.")
            return
        
        print(f"\n🍰 TOP {limit} CAKES BY SUCCESS RATE\n")
        print(f"{'Cake':<30} {'Recommended':<12} {'Avg Rating':<12} {'Success Rate':<13}")
        print("-" * 67)
        
        for cake in cakes:
            name = cake.get('recommended_cake', '')[0:28]
            recs = cake.get('times_recommended', 0)
            rating = f"{cake.get('avg_feedback', 0)}"
            success = f"{(cake.get('success_rate', 0) * 100):.1f}%"
            
            print(f"{name:<30} {recs:<12} {rating:<12} {success:<13}")
    
    def print_latency_analysis(self, hours: int = 24):
        """Print latency analysis."""
        latency = self.get_latency_analysis(hours)
        
        if not latency:
            print(f"No latency data for last {hours} hours.")
            return
        
        print(f"\n⏱️  LATENCY ANALYSIS (Last {hours}h)\n")
        print(f"{'Model':<20} {'p25':<8} {'p50':<8} {'p75':<8} {'p95':<8} {'Max':<8}")
        print("-" * 60)
        
        for row in latency:
            model = row.get('model_version', '')[0:18]
            p25 = f"{row.get('p25', 0)}ms"
            p50 = f"{row.get('p50', 0)}ms"
            p75 = f"{row.get('p75', 0)}ms"
            p95 = f"{row.get('p95', 0)}ms"
            max_l = f"{row.get('max_latency', 0)}ms"
            
            print(f"{model:<20} {p25:<8} {p50:<8} {p75:<8} {p95:<8} {max_l:<8}")
    
    def print_ab_tests(self):
        """Print A/B test results."""
        tests = self.get_ab_test_results()
        
        if not tests:
            print("No A/B test experiments found.")
            return
        
        print(f"\n🧪 A/B TEST RESULTS\n")
        print(f"{'Experiment':<25} {'Model':<20} {'Sample':<8} {'Avg Rating':<12} {'Avg Latency':<12}")
        print("-" * 77)
        
        for test in tests:
            exp = test.get('experiment_id', '')[0:23]
            model = test.get('model_version', '')[0:18]
            sample = test.get('sample_size', 0)
            rating = f"{test.get('avg_feedback', 0)}"
            latency = f"{test.get('avg_latency', 0)}ms"
            
            print(f"{exp:<25} {model:<20} {sample:<8} {rating:<12} {latency:<12}")


# ============================================================================
# CLI: PRINT ALL ANALYTICS
# ============================================================================

def print_all_analytics(hours: int = 24):
    """Print comprehensive analytics dashboard."""
    try:
        analytics = Analytics()
        
        print("\n" + "="*70)
        print("  Beige AI - Analytics Dashboard")
        print("="*70)
        
        analytics.print_recent_logs(limit=10)
        analytics.print_model_performance(hours=hours)
        analytics.print_popular_cakes(limit=5)
        analytics.print_latency_analysis(hours=hours)
        analytics.print_ab_tests()
        
        print("\n" + "="*70)
        print("  Dashboard generated successfully")
        print("="*70 + "\n")
    except Exception as e:
        print(f"Error generating analytics: {str(e)}")


if __name__ == "__main__":
    # Run analytics dashboard
    print_all_analytics(hours=24)
