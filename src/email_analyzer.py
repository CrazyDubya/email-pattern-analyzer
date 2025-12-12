"""Main email analysis engine.

This module provides the core functionality for analyzing email patterns,
including frequency analysis, timing patterns, and sender behaviors.
"""

import logging
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import pandas as pd
import numpy as np
from dateutil import parser as date_parser

from .pattern_detector import PatternDetector
from .categorizer import Categorizer

logger = logging.getLogger(__name__)


class EmailAnalyzer:
    """Main email analysis engine.
    
    This class coordinates the analysis of email data, including pattern detection,
    categorization, and statistical analysis.
    
    Attributes:
        pattern_detector: Pattern detection engine
        categorizer: Email categorization engine
        config: Configuration dictionary
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the email analyzer.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.pattern_detector = PatternDetector(config)
        self.categorizer = Categorizer(config)
        self.analysis_cache = {}
        
        logger.info("EmailAnalyzer initialized")
    
    def analyze(self, emails: List[Dict[str, Any]], 
                use_cache: bool = True) -> Dict[str, Any]:
        """Perform comprehensive email analysis.
        
        Args:
            emails: List of email dictionaries with fields:
                - sender: Email address of sender
                - subject: Email subject
                - date: Email date (string or datetime)
                - body: Email body text (optional)
                - labels: List of labels (optional)
            use_cache: Whether to use cached results
        
        Returns:
            Dictionary containing analysis results:
                - total_emails: Total number of emails analyzed
                - date_range: Start and end dates
                - sender_stats: Statistics about senders
                - temporal_patterns: Time-based patterns
                - categories: Distribution of categories
                - patterns: Detected patterns
                - recommendations: Action recommendations
        """
        logger.info(f"Starting analysis of {len(emails)} emails")
        
        if not emails:
            logger.warning("No emails to analyze")
            return self._empty_analysis()
        
        # Parse and normalize email data
        normalized_emails = self._normalize_emails(emails)
        
        # Basic statistics
        basic_stats = self._calculate_basic_stats(normalized_emails)
        
        # Sender analysis
        sender_stats = self._analyze_senders(normalized_emails)
        
        # Temporal analysis
        temporal_patterns = self._analyze_temporal_patterns(normalized_emails)
        
        # Categorize emails
        categories = self._categorize_emails(normalized_emails)
        
        # Detect advanced patterns
        patterns = self.pattern_detector.detect_patterns(normalized_emails)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            normalized_emails, sender_stats, patterns, categories
        )
        
        results = {
            "total_emails": len(normalized_emails),
            "date_range": basic_stats["date_range"],
            "basic_stats": basic_stats,
            "sender_stats": sender_stats,
            "temporal_patterns": temporal_patterns,
            "categories": categories,
            "patterns": patterns,
            "recommendations": recommendations,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
        logger.info("Analysis completed successfully")
        return results
    
    def _normalize_emails(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize email data to consistent format."""
        normalized = []
        
        for email in emails:
            try:
                # Parse date
                if isinstance(email.get('date'), str):
                    date = date_parser.parse(email['date'])
                elif isinstance(email.get('date'), datetime):
                    date = email['date']
                else:
                    date = datetime.now()
                
                normalized.append({
                    'sender': email.get('sender', 'unknown@unknown.com').lower(),
                    'subject': email.get('subject', ''),
                    'date': date,
                    'body': email.get('body', ''),
                    'labels': email.get('labels', []),
                    'thread_id': email.get('thread_id', None),
                    'size': email.get('size', 0)
                })
            except Exception as e:
                logger.warning(f"Error normalizing email: {e}")
                continue
        
        return normalized
    
    def _calculate_basic_stats(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate basic email statistics."""
        dates = [e['date'] for e in emails]
        
        return {
            "date_range": {
                "start": min(dates).isoformat(),
                "end": max(dates).isoformat()
            },
            "total_size_mb": sum(e['size'] for e in emails) / (1024 * 1024),
            "avg_per_day": len(emails) / max((max(dates) - min(dates)).days, 1),
            "unique_senders": len(set(e['sender'] for e in emails)),
            "unique_threads": len(set(e['thread_id'] for e in emails if e['thread_id']))
        }
    
    def _analyze_senders(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze sender patterns and statistics."""
        sender_counts = Counter(e['sender'] for e in emails)
        sender_dates = defaultdict(list)
        
        for email in emails:
            sender_dates[email['sender']].append(email['date'])
        
        # Top senders
        top_senders = [
            {
                "email": sender,
                "count": count,
                "percentage": (count / len(emails)) * 100
            }
            for sender, count in sender_counts.most_common(20)
        ]
        
        # Calculate sender frequency
        sender_frequency = {}
        for sender, dates in sender_dates.items():
            if len(dates) > 1:
                sorted_dates = sorted(dates)
                intervals = [(sorted_dates[i+1] - sorted_dates[i]).days 
                           for i in range(len(sorted_dates)-1)]
                avg_interval = np.mean(intervals) if intervals else 0
                sender_frequency[sender] = {
                    "avg_days_between": avg_interval,
                    "regularity_score": 1 / (1 + np.std(intervals)) if intervals else 0
                }
        
        return {
            "top_senders": top_senders,
            "total_senders": len(sender_counts),
            "top_sender": top_senders[0] if top_senders else None,
            "sender_frequency": sender_frequency
        }
    
    def _analyze_temporal_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze time-based patterns in email activity."""
        # Hour of day distribution
        hours = [e['date'].hour for e in emails]
        hour_dist = Counter(hours)
        
        # Day of week distribution
        days = [e['date'].weekday() for e in emails]  # 0 = Monday
        day_dist = Counter(days)
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        # Monthly trends
        monthly = defaultdict(int)
        for email in emails:
            month_key = email['date'].strftime('%Y-%m')
            monthly[month_key] += 1
        
        return {
            "peak_hour": max(hour_dist.items(), key=lambda x: x[1])[0] if hour_dist else None,
            "hourly_distribution": dict(hour_dist),
            "peak_day": day_names[max(day_dist.items(), key=lambda x: x[1])[0]] if day_dist else None,
            "daily_distribution": {day_names[k]: v for k, v in day_dist.items()},
            "monthly_trends": dict(sorted(monthly.items())),
            "weekend_percentage": sum(1 for d in days if d >= 5) / len(days) * 100 if days else 0
        }
    
    def _categorize_emails(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Categorize all emails and generate distribution."""
        categories = defaultdict(int)
        categorized_emails = []
        
        for email in emails:
            category = self.categorizer.categorize(email)
            categories[category] += 1
            categorized_emails.append({
                'email': email,
                'category': category
            })
        
        total = len(emails)
        return {
            "distribution": {
                cat: {
                    "count": count,
                    "percentage": (count / total) * 100
                }
                for cat, count in categories.items()
            },
            "dominant_category": max(categories.items(), key=lambda x: x[1])[0] if categories else None
        }
    
    def _generate_recommendations(self, emails: List[Dict[str, Any]], 
                                 sender_stats: Dict[str, Any],
                                 patterns: Dict[str, Any],
                                 categories: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # High-volume sender recommendations
        for sender_info in sender_stats['top_senders'][:5]:
            if sender_info['percentage'] > 10:
                recommendations.append({
                    "type": "filter",
                    "priority": "high",
                    "title": f"Create filter for high-volume sender",
                    "description": f"{sender_info['email']} accounts for {sender_info['percentage']:.1f}% of your emails",
                    "action": f"Consider auto-labeling or archiving emails from {sender_info['email']}"
                })
        
        # Category-based recommendations
        for cat, info in categories['distribution'].items():
            if cat == 'promotional' and info['percentage'] > 20:
                recommendations.append({
                    "type": "organization",
                    "priority": "medium",
                    "title": "High promotional email volume",
                    "description": f"Promotional emails make up {info['percentage']:.1f}% of your inbox",
                    "action": "Consider unsubscribing or auto-archiving promotional emails"
                })
        
        return recommendations
    
    def _empty_analysis(self) -> Dict[str, Any]:
        """Return empty analysis results."""
        return {
            "total_emails": 0,
            "date_range": None,
            "basic_stats": {},
            "sender_stats": {},
            "temporal_patterns": {},
            "categories": {},
            "patterns": {},
            "recommendations": [],
            "analysis_timestamp": datetime.now().isoformat()
        }


def main():
    """Command-line interface for email analyzer."""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: python email_analyzer.py <emails.json>")
        sys.exit(1)
    
    with open(sys.argv[1], 'r') as f:
        emails = json.load(f)
    
    analyzer = EmailAnalyzer()
    results = analyzer.analyze(emails)
    
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
