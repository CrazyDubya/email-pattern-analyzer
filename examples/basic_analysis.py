#!/usr/bin/env python3
"""Basic email analysis example.

This script demonstrates the simplest way to analyze your emails:
1. Connect to Gmail or Outlook
2. Fetch recent emails
3. Analyze patterns
4. Display results
"""

import sys
import yaml
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector
from src.outlook_connector import OutlookConnector
from src.stats_generator import StatsGenerator
from src.filter_suggester import FilterSuggester

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    """Run basic email analysis."""
    print("\n" + "="*60)
    print("  EMAIL PATTERN ANALYZER - Basic Analysis")
    print("="*60 + "\n")
    
    # Load configuration
    try:
        with open('config.yaml', 'r') as f:
            config = yaml.safe_load(f)
    except FileNotFoundError:
        print("❌ Error: config.yaml not found!")
        print("Please copy config.yaml.example to config.yaml and configure it.")
        sys.exit(1)
    
    # Choose email service
    use_gmail = config.get('gmail', {}).get('enabled', True)
    use_outlook = config.get('outlook', {}).get('enabled', False)
    
    # Connect to email service
    print("\n🔌 Connecting to email service...")
    
    if use_gmail:
        print("Using Gmail...")
        connector = GmailConnector(config=config)
        if not connector.authenticate():
            print("❌ Authentication failed!")
            sys.exit(1)
    elif use_outlook:
        print("Using Outlook...")
        outlook_config = config['outlook']
        connector = OutlookConnector(
            client_id=outlook_config['client_id'],
            client_secret=outlook_config['client_secret'],
            tenant_id=outlook_config['tenant_id'],
            config=config
        )
        if not connector.authenticate():
            print("❌ Authentication failed!")
            sys.exit(1)
    else:
        print("❌ No email service enabled in config!")
        sys.exit(1)
    
    print("✅ Connected successfully!\n")
    
    # Fetch emails
    print("📥 Fetching emails...")
    max_emails = 500  # Fetch last 500 emails for quick analysis
    emails = connector.fetch_emails(max_results=max_emails)
    
    if not emails:
        print("❌ No emails found!")
        sys.exit(1)
    
    print(f"✅ Fetched {len(emails)} emails\n")
    
    # Analyze emails
    print("🔍 Analyzing email patterns...")
    analyzer = EmailAnalyzer(config)
    results = analyzer.analyze(emails)
    
    # Display results
    print("\n" + "="*60)
    print("  ANALYSIS RESULTS")
    print("="*60 + "\n")
    
    # Summary Statistics
    print("📊 SUMMARY STATISTICS")
    print("-" * 40)
    print(f"Total emails analyzed:  {results['total_emails']:,}")
    print(f"Date range:            {results['date_range']['start'][:10]} to {results['date_range']['end'][:10]}")
    print(f"Emails per day:        {results['basic_stats']['avg_per_day']:.1f}")
    print(f"Unique senders:        {results['basic_stats']['unique_senders']:,}")
    print(f"Total size:            {results['basic_stats']['total_size_mb']:.1f} MB")
    
    # Top Senders
    print("\n\n👥 TOP 5 SENDERS")
    print("-" * 40)
    for i, sender in enumerate(results['sender_stats']['top_senders'][:5], 1):
        print(f"{i}. {sender['email'][:50]}")
        print(f"   {sender['count']:,} emails ({sender['percentage']:.1f}%)")
    
    # Temporal Patterns
    print("\n\n⏰ TEMPORAL PATTERNS")
    print("-" * 40)
    print(f"Peak hour:            {results['temporal_patterns']['peak_hour']}:00")
    print(f"Peak day:             {results['temporal_patterns']['peak_day']}")
    print(f"Weekend emails:       {results['temporal_patterns']['weekend_percentage']:.1f}%")
    
    # Categories
    print("\n\n🏷️  EMAIL CATEGORIES")
    print("-" * 40)
    categories = results['categories']['distribution']
    for category, info in sorted(categories.items(), key=lambda x: x[1]['count'], reverse=True):
        bar = '█' * int(info['percentage'] / 2)
        print(f"{category:15} {bar} {info['percentage']:5.1f}% ({info['count']:,})")
    
    # Generate filter suggestions
    print("\n\n🔧 FILTER SUGGESTIONS")
    print("-" * 40)
    suggester = FilterSuggester(config)
    suggestions = suggester.generate_suggestions(results)
    
    if suggestions:
        for i, suggestion in enumerate(suggestions[:5], 1):
            print(f"\n{i}. {suggestion['rule']}")
            print(f"   💬 {suggestion['reason']}")
            print(f"   🎯 Confidence: {suggestion['confidence']:.0f}%")
            print(f"   📦 Impact: {suggestion['impact']}")
    else:
        print("No suggestions at this time.")
    
    # Generate detailed reports
    print("\n\n📄 Generating detailed reports...")
    stats_gen = StatsGenerator(config)
    reports = stats_gen.generate_all_reports(results, output_dir='data/reports')
    
    print("\nReports saved to:")
    for format_type, path in reports.items():
        if format_type != 'charts':
            print(f"  • {format_type.upper()}: {path}")
        else:
            print(f"  • CHARTS: {len(path)} files")
    
    # Summary
    print("\n" + "="*60)
    print("  ANALYSIS COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("  1. Review the generated reports in data/reports/")
    print("  2. Check the filter suggestions above")
    print("  3. Run 'python examples/category_customization.py' to customize categories")
    print("  4. See docs/usage.md for more advanced usage")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAnalysis interrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
