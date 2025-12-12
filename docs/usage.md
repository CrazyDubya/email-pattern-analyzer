# Usage Guide

This guide provides comprehensive examples of using the Email Pattern Analyzer.

## Basic Usage

### 1. Simple Analysis

```python
from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector
import yaml

# Load configuration
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Connect to Gmail
connector = GmailConnector(config=config)
connector.authenticate()

# Fetch emails
emails = connector.fetch_emails(max_results=500)

# Analyze
analyzer = EmailAnalyzer(config)
results = analyzer.analyze(emails)

# Print summary
print(f"Total emails: {results['total_emails']}")
print(f"Date range: {results['date_range']['start']} to {results['date_range']['end']}")
print(f"Top sender: {results['sender_stats']['top_sender']['email']}")
print(f"Peak hour: {results['temporal_patterns']['peak_hour']}")
```

### 2. Generate Statistics

```python
from src.stats_generator import StatsGenerator

# Generate comprehensive stats
stats_gen = StatsGenerator(config)
reports = stats_gen.generate_all_reports(results, output_dir='./data/reports')

print(f"Reports saved to:")
for format_type, path in reports.items():
    print(f"  {format_type}: {path}")
```

### 3. Get Filter Suggestions

```python
from src.filter_suggester import FilterSuggester

# Generate suggestions
suggester = FilterSuggester(config)
suggestions = suggester.generate_suggestions(results)

# Print top suggestions
for suggestion in suggestions[:5]:
    print(f"\n{suggestion['rule']}")
    print(f"  Reason: {suggestion['reason']}")
    print(f"  Confidence: {suggestion['confidence']:.0f}%")
    print(f"  Impact: {suggestion['impact']}")
```

## Advanced Usage

### Analyzing Specific Time Periods

```python
from datetime import datetime, timedelta

# Analyze only recent emails
after_date = datetime.now() - timedelta(days=30)
emails = connector.fetch_emails(
    max_results=1000,
    after_date=after_date
)

results = analyzer.analyze(emails)
print(f"Analyzed {len(emails)} emails from the last 30 days")
```

### Using Query Filters

```python
# Gmail query syntax
emails = connector.fetch_emails(
    query='from:newsletter@company.com OR from:updates@service.com',
    max_results=500
)

# Filter by label
emails = connector.fetch_emails(
    label_ids=['INBOX', 'UNREAD'],
    max_results=200
)

# Complex query
emails = connector.fetch_emails(
    query='subject:meeting has:attachment -label:processed',
    max_results=300
)
```

### Batch Processing Large Mailboxes

```python
def analyze_in_batches(connector, analyzer, batch_size=1000, total_emails=10000):
    """Analyze large mailboxes in batches."""
    all_results = []
    
    for offset in range(0, total_emails, batch_size):
        print(f"Processing batch {offset}-{offset+batch_size}...")
        
        emails = connector.fetch_emails(max_results=batch_size)
        results = analyzer.analyze(emails)
        all_results.append(results)
        
        # Save intermediate results
        with open(f'data/batch_{offset}.json', 'w') as f:
            json.dump(results, f)
    
    return all_results

results = analyze_in_batches(connector, analyzer)
```

### Custom Categorization

```python
from src.categorizer import Categorizer

# Create categorizer with custom categories
categorizer = Categorizer(config)

# Add custom category at runtime
categorizer.add_custom_category(
    name='Project Alpha',
    keywords=['project alpha', 'alpha milestone', 'alpha sprint'],
    senders=['alpha-team@company.com'],
    priority='high'
)

# Categorize emails
for email in emails:
    category = categorizer.categorize(email)
    print(f"{email['subject']}: {category}")
```

### Working with Patterns

```python
from src.pattern_detector import PatternDetector

pattern_detector = PatternDetector(config)
patterns = pattern_detector.detect_patterns(emails)

# Check temporal patterns
temporal = patterns['temporal']
print(f"Morning emails: {temporal['time_of_day']['morning']['percentage']:.1f}%")
print(f"Has daily routine: {temporal['has_daily_routine']}")

# Check sender patterns
for sender in patterns['sender']['frequent_senders']:
    print(f"{sender['sender']}: {sender['emails_per_month']:.1f} emails/month")

# Check content patterns
for keyword, count in patterns['content']['common_keywords'].items():
    print(f"{keyword}: {count} occurrences")
```

## Outlook Usage

### Connecting to Outlook

```python
from src.outlook_connector import OutlookConnector

# Initialize with credentials from config
outlook_config = config['outlook']
connector = OutlookConnector(
    client_id=outlook_config['client_id'],
    client_secret=outlook_config['client_secret'],
    tenant_id=outlook_config['tenant_id'],
    config=config
)

# Authenticate
if connector.authenticate():
    # Fetch emails
    emails = connector.fetch_emails(max_results=500)
    
    # Analyze (same as Gmail)
    results = analyzer.analyze(emails)
```

### Outlook-Specific Features

```python
# Get folders
folders = connector.get_folders()
for folder in folders:
    print(f"{folder['displayName']}: {folder['totalItemCount']} items")

# Create a new folder
folder_id = connector.create_folder('Analyzed Emails')

# Move email to folder
connector.move_message(email['id'], folder_id)

# Apply category
connector.apply_category(email['id'], 'Important')
```

## Applying Filters

### Gmail Filters

```python
# Convert suggestion to Gmail filter
suggestion = suggestions[0]
gmail_filter = suggester.format_suggestion_for_gmail(suggestion)

# Apply the filter
connector.apply_filter(gmail_filter)
print(f"Filter applied: {suggestion['rule']}")
```

### Outlook Rules

```python
# Convert suggestion to Outlook rule
suggestion = suggestions[0]
outlook_rule = suggester.format_suggestion_for_outlook(suggestion)

# Create the rule
connector.create_rule(outlook_rule)
print(f"Rule created: {suggestion['rule']}")
```

## Exporting Results

### JSON Export

```python
import json

# Save full results
with open('data/analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2, default=str)
```

### CSV Export

```python
import csv
import pandas as pd

# Export sender stats to CSV
senders_df = pd.DataFrame(results['sender_stats']['top_senders'])
senders_df.to_csv('data/top_senders.csv', index=False)

# Export category distribution
categories = []
for cat, info in results['categories']['distribution'].items():
    categories.append({
        'category': cat,
        'count': info['count'],
        'percentage': info['percentage']
    })

cat_df = pd.DataFrame(categories)
cat_df.to_csv('data/categories.csv', index=False)
```

### HTML Report

```python
from src.stats_generator import StatsGenerator

stats_gen = StatsGenerator(config)
stats = stats_gen.generate_statistics(results)

# Generate HTML report
report_path = stats_gen._export_html(stats, results, 'data/report.html')
print(f"HTML report: {report_path}")
```

## Visualization

### Generate Charts

```python
import matplotlib.pyplot as plt
import seaborn as sns

# Hourly distribution
hourly_dist = results['temporal_patterns']['hourly_distribution']
plt.figure(figsize=(12, 6))
plt.bar(hourly_dist.keys(), hourly_dist.values())
plt.xlabel('Hour of Day')
plt.ylabel('Number of Emails')
plt.title('Email Distribution by Hour')
plt.savefig('data/hourly_distribution.png')

# Category pie chart
categories = results['categories']['distribution']
labels = list(categories.keys())
sizes = [info['count'] for info in categories.values()]

plt.figure(figsize=(10, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.title('Email Distribution by Category')
plt.savefig('data/category_distribution.png')
```

## Command-Line Usage

### Using the CLI

Create a simple CLI script:

```python
# cli.py
import click
import yaml
from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector

@click.command()
@click.option('--config', default='config.yaml', help='Config file path')
@click.option('--max-emails', default=1000, help='Maximum emails to analyze')
@click.option('--output', default='data', help='Output directory')
def analyze(config, max_emails, output):
    """Analyze email patterns."""
    with open(config) as f:
        cfg = yaml.safe_load(f)
    
    connector = GmailConnector(config=cfg)
    connector.authenticate()
    
    emails = connector.fetch_emails(max_results=max_emails)
    
    analyzer = EmailAnalyzer(cfg)
    results = analyzer.analyze(emails)
    
    click.echo(f"Analyzed {results['total_emails']} emails")
    click.echo(f"Top sender: {results['sender_stats']['top_sender']['email']}")

if __name__ == '__main__':
    analyze()
```

Run it:
```bash
python cli.py --max-emails 500 --output ./results
```

## Integration Examples

### Slack Notifications

```python
import requests

def send_slack_notification(results, webhook_url):
    """Send analysis summary to Slack."""
    message = {
        "text": f"Email Analysis Complete",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Email Analysis Results*\n"
                           f"Total: {results['total_emails']}\n"
                           f"Top Sender: {results['sender_stats']['top_sender']['email']}\n"
                           f"Peak Hour: {results['temporal_patterns']['peak_hour']}:00"
                }
            }
        ]
    }
    
    response = requests.post(webhook_url, json=message)
    return response.status_code == 200

# Usage
send_slack_notification(results, 'https://hooks.slack.com/services/YOUR/WEBHOOK')
```

### Database Storage

```python
import sqlite3
import json

def save_to_database(results, db_path='email_analysis.db'):
    """Save results to SQLite database."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            total_emails INTEGER,
            date_range_start TEXT,
            date_range_end TEXT,
            results TEXT
        )
    ''')
    
    # Insert results
    cursor.execute('''
        INSERT INTO analyses (timestamp, total_emails, date_range_start, date_range_end, results)
        VALUES (?, ?, ?, ?, ?)
    ''', (
        results['analysis_timestamp'],
        results['total_emails'],
        results['date_range']['start'],
        results['date_range']['end'],
        json.dumps(results)
    ))
    
    conn.commit()
    conn.close()

# Usage
save_to_database(results)
```

## Error Handling

```python
try:
    connector = GmailConnector(config=config)
    
    if not connector.authenticate():
        raise Exception("Authentication failed")
    
    emails = connector.fetch_emails(max_results=1000)
    
    if not emails:
        print("No emails found")
        exit(1)
    
    results = analyzer.analyze(emails)
    
except FileNotFoundError as e:
    print(f"Config or credentials file not found: {e}")
except Exception as e:
    print(f"Error during analysis: {e}")
    import traceback
    traceback.print_exc()
```

## Performance Tips

1. **Use caching** for repeated analyses:
   ```python
   analyzer = EmailAnalyzer(config)
   results = analyzer.analyze(emails, use_cache=True)
   ```

2. **Limit email fetching**:
   ```python
   emails = connector.fetch_emails(
       max_results=500,
       after_date=datetime.now() - timedelta(days=90)
   )
   ```

3. **Process in parallel**:
   ```python
   config['performance']['enable_parallel'] = True
   config['performance']['num_workers'] = 8
   ```

4. **Disable expensive features**:
   ```python
   config['statistics']['generate_charts'] = False
   config['analysis']['enable_sentiment_analysis'] = False
   ```

## Next Steps

- [Customization Guide](customization.md) - Learn how to customize
- [Output Guide](output_guide.md) - Understand the results
- [Automation Guide](automation.md) - Automate your analysis
