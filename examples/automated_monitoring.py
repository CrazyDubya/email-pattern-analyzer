#!/usr/bin/env python3
"""Automated monitoring example.

This script demonstrates how to set up continuous email monitoring:
1. Check for new emails periodically
2. Analyze patterns
3. Detect anomalies
4. Send alerts
"""

import sys
import yaml
import time
import json
import schedule
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector
from src.pattern_detector import PatternDetector
from src.filter_suggester import FilterSuggester

# State file to track last analysis
STATE_FILE = 'data/monitor_state.json'

def load_state():
    """Load monitoring state."""
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {
            'last_analysis': None,
            'last_email_count': 0,
            'baseline_avg_per_day': 0
        }

def save_state(state):
    """Save monitoring state."""
    Path(STATE_FILE).parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def detect_anomalies(current_results, baseline):
    """Detect anomalies in email patterns."""
    anomalies = []
    
    # Check for email volume spike
    current_avg = current_results['basic_stats']['avg_per_day']
    baseline_avg = baseline.get('baseline_avg_per_day', current_avg)
    
    if baseline_avg > 0:
        volume_increase = ((current_avg - baseline_avg) / baseline_avg) * 100
        
        if volume_increase > 50:  # 50% increase
            anomalies.append({
                'type': 'volume_spike',
                'severity': 'high',
                'message': f"Email volume increased by {volume_increase:.0f}%",
                'details': f"From {baseline_avg:.1f} to {current_avg:.1f} emails/day"
            })
    
    # Check for unusual top sender
    top_sender = current_results['sender_stats']['top_sender']
    if top_sender and top_sender['percentage'] > 30:
        anomalies.append({
            'type': 'sender_dominance',
            'severity': 'medium',
            'message': f"One sender dominates: {top_sender['email']}",
            'details': f"{top_sender['percentage']:.1f}% of all emails"
        })
    
    # Check for high weekend activity
    weekend_pct = current_results['temporal_patterns']['weekend_percentage']
    if weekend_pct > 40:
        anomalies.append({
            'type': 'weekend_overload',
            'severity': 'medium',
            'message': f"High weekend email activity: {weekend_pct:.1f}%",
            'details': "Consider adjusting notification settings"
        })
    
    # Check for late night emails
    patterns = current_results.get('patterns', {}).get('temporal', {})
    night_pct = patterns.get('time_of_day', {}).get('night', {}).get('percentage', 0)
    
    if night_pct > 25:
        anomalies.append({
            'type': 'night_activity',
            'severity': 'low',
            'message': f"High late-night email activity: {night_pct:.1f}%",
            'details': "Consider do-not-disturb settings"
        })
    
    return anomalies

def send_alert(anomalies, results):
    """Send alert about detected anomalies."""
    print("\n" + "⚠️ " * 20)
    print("  ANOMALY ALERT")
    print("⚠️ " * 20)
    print(f"\nDetected at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for anomaly in anomalies:
        severity_emoji = {'
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }
        
        print(f"{severity_emoji.get(anomaly['severity'], '⚪')} {anomaly['severity'].upper()}: {anomaly['message']}")
        print(f"   {anomaly['details']}")
        print()
    
    print("-" * 60)
    print("\nCurrent Stats:")
    print(f"  Total emails: {results['total_emails']:,}")
    print(f"  Emails/day: {results['basic_stats']['avg_per_day']:.1f}")
    print(f"  Top sender: {results['sender_stats']['top_sender']['email']}")
    print()

def monitor_once(config):
    """Run one monitoring cycle."""
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running email monitoring...")
    
    # Load previous state
    state = load_state()
    
    # Connect and fetch recent emails
    connector = GmailConnector(config=config)
    if not connector.authenticate():
        print("❌ Authentication failed")
        return
    
    # Fetch emails from last 7 days
    after_date = datetime.now() - timedelta(days=7)
    emails = connector.fetch_emails(
        max_results=500,
        after_date=after_date
    )
    
    if not emails:
        print("ℹ️  No emails found")
        return
    
    print(f"✅ Fetched {len(emails)} emails")
    
    # Analyze
    analyzer = EmailAnalyzer(config)
    results = analyzer.analyze(emails)
    
    # Detect anomalies
    anomalies = detect_anomalies(results, state)
    
    if anomalies:
        send_alert(anomalies, results)
    else:
        print("✅ No anomalies detected")
        print(f"   Total emails: {results['total_emails']:,}")
        print(f"   Avg per day: {results['basic_stats']['avg_per_day']:.1f}")
    
    # Update state
    state['last_analysis'] = datetime.now().isoformat()
    state['last_email_count'] = results['total_emails']
    state['baseline_avg_per_day'] = results['basic_stats']['avg_per_day']
    save_state(state)

def main():
    print("\n" + "="*60)
    print("  EMAIL PATTERN ANALYZER - Automated Monitoring")
    print("="*60 + "\n")
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ Error: config.yaml not found!")
        sys.exit(1)
    
    print("🔄 Starting continuous monitoring...")
    print("   Checking every hour")
    print("   Press Ctrl+C to stop\n")
    print("-" * 60)
    
    # Schedule monitoring
    schedule.every().hour.do(monitor_once, config=config)
    
    # Run once immediately
    monitor_once(config)
    
    # Then run on schedule
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("\n\n🛑 Monitoring stopped by user")
        print("\nMonitoring summary:")
        state = load_state()
        if state['last_analysis']:
            print(f"  Last analysis: {state['last_analysis']}")
            print(f"  Last email count: {state['last_email_count']:,}")
            print(f"  Baseline avg: {state['baseline_avg_per_day']:.1f} emails/day")
        print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
