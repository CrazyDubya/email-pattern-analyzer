"""Pattern detection module.

Detects various patterns in email data including temporal patterns,
sender patterns, content patterns, and behavioral patterns.
"""

import logging
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import re

logger = logging.getLogger(__name__)


class PatternDetector:
    """Detects patterns in email data.
    
    Identifies:
    - Temporal patterns (time of day, day of week, seasonal)
    - Sender patterns (frequent senders, response times)
    - Content patterns (recurring keywords, subjects)
    - Volume patterns (trends, anomalies)
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the pattern detector.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.min_occurrences = self.config.get('analysis', {}).get('min_pattern_occurrences', 5)
        self.pattern_thresholds = self.config.get('analysis', {}).get('pattern_thresholds', {})
        
        logger.info("PatternDetector initialized")
    
    def detect_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect all patterns in email data.
        
        Args:
            emails: List of normalized email dictionaries
        
        Returns:
            Dictionary containing detected patterns
        """
        if not emails:
            return {}
        
        logger.info(f"Detecting patterns in {len(emails)} emails")
        
        patterns = {
            'temporal': self._detect_temporal_patterns(emails),
            'sender': self._detect_sender_patterns(emails),
            'content': self._detect_content_patterns(emails),
            'volume': self._detect_volume_patterns(emails),
            'thread': self._detect_thread_patterns(emails),
            'behavioral': self._detect_behavioral_patterns(emails)
        }
        
        logger.info("Pattern detection completed")
        return patterns
    
    def _detect_temporal_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect time-based patterns."""
        patterns = {}
        
        # Time of day patterns
        hours = [e['date'].hour for e in emails]
        hour_counts = Counter(hours)
        
        # Define time periods
        morning = sum(hour_counts[h] for h in range(6, 12))
        afternoon = sum(hour_counts[h] for h in range(12, 18))
        evening = sum(hour_counts[h] for h in range(18, 24))
        night = sum(hour_counts[h] for h in range(0, 6))
        
        total = len(emails)
        patterns['time_of_day'] = {
            'morning': {'count': morning, 'percentage': (morning/total)*100},
            'afternoon': {'count': afternoon, 'percentage': (afternoon/total)*100},
            'evening': {'count': evening, 'percentage': (evening/total)*100},
            'night': {'count': night, 'percentage': (night/total)*100}
        }
        
        # Day of week patterns
        weekdays = [e['date'].weekday() for e in emails]
        workday_count = sum(1 for d in weekdays if d < 5)
        weekend_count = sum(1 for d in weekdays if d >= 5)
        
        patterns['workweek_vs_weekend'] = {
            'workdays': {'count': workday_count, 'percentage': (workday_count/total)*100},
            'weekends': {'count': weekend_count, 'percentage': (weekend_count/total)*100}
        }
        
        # Detect if there's a consistent daily pattern
        patterns['has_daily_routine'] = self._detect_daily_routine(hours)
        
        # Monthly seasonality
        patterns['monthly_seasonality'] = self._detect_monthly_seasonality(emails)
        
        return patterns
    
    def _detect_daily_routine(self, hours: List[int]) -> bool:
        """Detect if there's a consistent daily email routine."""
        hour_counts = Counter(hours)
        
        # Check if 80% of emails fall within a 4-hour window
        sorted_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)
        top_hours = sorted_hours[:4]
        top_count = sum(count for _, count in top_hours)
        
        return (top_count / len(hours)) > 0.8 if hours else False
    
    def _detect_monthly_seasonality(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect monthly patterns and seasonality."""
        monthly_counts = defaultdict(int)
        
        for email in emails:
            month = email['date'].month
            monthly_counts[month] += 1
        
        if len(monthly_counts) < 3:
            return {'detected': False}
        
        counts = list(monthly_counts.values())
        avg = np.mean(counts)
        std = np.std(counts)
        
        # Check for significant variation
        has_seasonality = std > (avg * 0.3)
        
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        return {
            'detected': has_seasonality,
            'monthly_distribution': {month_names[m-1]: c for m, c in monthly_counts.items()},
            'peak_month': month_names[max(monthly_counts.items(), key=lambda x: x[1])[0] - 1] if monthly_counts else None
        }
    
    def _detect_sender_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in sender behavior."""
        sender_emails = defaultdict(list)
        
        for email in emails:
            sender_emails[email['sender']].append(email)
        
        patterns = {
            'frequent_senders': [],
            'burst_senders': [],
            'regular_senders': []
        }
        
        for sender, sender_mails in sender_emails.items():
            if len(sender_mails) < self.min_occurrences:
                continue
            
            # Frequent senders (high volume)
            if len(sender_mails) > self.pattern_thresholds.get('frequent_sender', 20):
                patterns['frequent_senders'].append({
                    'sender': sender,
                    'count': len(sender_mails),
                    'emails_per_month': len(sender_mails) / max(1, 
                        (max(e['date'] for e in sender_mails) - 
                         min(e['date'] for e in sender_mails)).days / 30)
                })
            
            # Check for burst patterns (many emails in short time)
            burst_score = self._calculate_burst_score(sender_mails)
            if burst_score > 0.7:
                patterns['burst_senders'].append({
                    'sender': sender,
                    'burst_score': burst_score
                })
            
            # Regular senders (consistent frequency)
            regularity = self._calculate_regularity(sender_mails)
            if regularity > 0.7:
                patterns['regular_senders'].append({
                    'sender': sender,
                    'regularity_score': regularity
                })
        
        return patterns
    
    def _calculate_burst_score(self, emails: List[Dict[str, Any]]) -> float:
        """Calculate burst score for a sender."""
        if len(emails) < 2:
            return 0.0
        
        dates = sorted([e['date'] for e in emails])
        intervals = [(dates[i+1] - dates[i]).total_seconds() / 3600 
                    for i in range(len(dates)-1)]
        
        # Burst if many emails sent within short intervals
        short_intervals = sum(1 for i in intervals if i < 24)  # Within 24 hours
        return short_intervals / len(intervals) if intervals else 0.0
    
    def _calculate_regularity(self, emails: List[Dict[str, Any]]) -> float:
        """Calculate regularity score for a sender."""
        if len(emails) < 3:
            return 0.0
        
        dates = sorted([e['date'] for e in emails])
        intervals = [(dates[i+1] - dates[i]).days 
                    for i in range(len(dates)-1)]
        
        if not intervals:
            return 0.0
        
        # High regularity if intervals have low standard deviation
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if avg_interval == 0:
            return 0.0
        
        regularity = 1.0 / (1.0 + (std_interval / avg_interval))
        return regularity
    
    def _detect_content_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in email content."""
        # Extract common keywords from subjects
        all_subjects = ' '.join([e['subject'].lower() for e in emails])
        words = re.findall(r'\b[a-z]{4,}\b', all_subjects)
        word_counts = Counter(words)
        
        # Remove common stop words
        stop_words = {'from', 'with', 'your', 'this', 'that', 'have', 'will', 'would', 'could'}
        filtered_words = {w: c for w, c in word_counts.items() 
                         if w not in stop_words and c >= self.min_occurrences}
        
        # Detect recurring subject patterns
        subject_patterns = self._detect_subject_patterns(emails)
        
        # Detect newsletter patterns
        newsletter_indicators = sum(1 for e in emails if 'unsubscribe' in e.get('body', '').lower())
        
        return {
            'common_keywords': dict(sorted(filtered_words.items(), 
                                         key=lambda x: x[1], reverse=True)[:20]),
            'subject_patterns': subject_patterns,
            'newsletter_percentage': (newsletter_indicators / len(emails)) * 100 if emails else 0
        }
    
    def _detect_subject_patterns(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect recurring patterns in subject lines."""
        subjects = [e['subject'] for e in emails]
        
        # Look for subjects with similar prefixes
        prefix_counts = defaultdict(int)
        
        for subject in subjects:
            # Extract prefix (first few words)
            words = subject.split()[:3]
            if words:
                prefix = ' '.join(words).lower()
                prefix_counts[prefix] += 1
        
        patterns = []
        for prefix, count in prefix_counts.items():
            if count >= self.min_occurrences:
                patterns.append({
                    'pattern': prefix,
                    'occurrences': count,
                    'percentage': (count / len(emails)) * 100
                })
        
        return sorted(patterns, key=lambda x: x['occurrences'], reverse=True)[:10]
    
    def _detect_volume_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect volume trends and anomalies."""
        if not emails:
            return {}
        
        # Group emails by day
        daily_counts = defaultdict(int)
        for email in emails:
            date_key = email['date'].date()
            daily_counts[date_key] += 1
        
        counts = list(daily_counts.values())
        
        if not counts:
            return {}
        
        avg_daily = np.mean(counts)
        std_daily = np.std(counts)
        
        # Detect anomalies (days with unusually high/low volume)
        anomalies = []
        for date, count in daily_counts.items():
            z_score = (count - avg_daily) / std_daily if std_daily > 0 else 0
            if abs(z_score) > 2:  # More than 2 standard deviations
                anomalies.append({
                    'date': date.isoformat(),
                    'count': count,
                    'deviation': z_score,
                    'type': 'spike' if z_score > 0 else 'drop'
                })
        
        # Detect trend (increasing/decreasing)
        sorted_dates = sorted(daily_counts.keys())
        if len(sorted_dates) > 7:
            recent_avg = np.mean([daily_counts[d] for d in sorted_dates[-7:]])
            older_avg = np.mean([daily_counts[d] for d in sorted_dates[:7]])
            trend = 'increasing' if recent_avg > older_avg * 1.2 else \
                   ('decreasing' if recent_avg < older_avg * 0.8 else 'stable')
        else:
            trend = 'insufficient_data'
        
        return {
            'average_daily': float(avg_daily),
            'std_deviation': float(std_daily),
            'trend': trend,
            'anomalies': sorted(anomalies, key=lambda x: abs(x['deviation']), reverse=True)[:10]
        }
    
    def _detect_thread_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect patterns in email threads."""
        threads = defaultdict(list)
        
        for email in emails:
            thread_id = email.get('thread_id')
            if thread_id:
                threads[thread_id].append(email)
        
        if not threads:
            return {'thread_analysis_available': False}
        
        thread_lengths = [len(emails) for emails in threads.values()]
        
        long_threads = [tid for tid, emails in threads.items() if len(emails) > 10]
        
        return {
            'thread_analysis_available': True,
            'total_threads': len(threads),
            'average_thread_length': float(np.mean(thread_lengths)),
            'max_thread_length': max(thread_lengths),
            'long_threads_count': len(long_threads),
            'emails_in_threads_percentage': (sum(thread_lengths) / len(emails)) * 100 if emails else 0
        }
    
    def _detect_behavioral_patterns(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Detect behavioral patterns in email usage."""
        patterns = {}
        
        # Detect if user is an email hoarder (rarely deletes)
        patterns['email_hoarder_score'] = min(len(emails) / 10000, 1.0)  # Score 0-1
        
        # Detect organizational habits based on labels
        labels_used = set()
        for email in emails:
            labels_used.update(email.get('labels', []))
        
        patterns['organizational_score'] = min(len(labels_used) / 20, 1.0)  # Score 0-1
        
        # Detect response time patterns (would need sent emails data)
        patterns['response_analysis'] = 'requires_sent_emails_data'
        
        return patterns
