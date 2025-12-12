# Automation Guide

Set up automated email analysis and monitoring.

## Scheduled Analysis

### Using cron (Linux/macOS)

1. **Create analysis script** (`scripts/auto_analyze.sh`):

```bash
#!/bin/bash
cd /path/to/email-pattern-analyzer
source venv/bin/activate
python scripts/scheduled_analysis.py
```

2. **Make it executable**:

```bash
chmod +x scripts/auto_analyze.sh
```

3. **Add to crontab**:

```bash
crontab -e
```

Add one of these lines:

```bash
# Daily at 6 AM
0 6 * * * /path/to/scripts/auto_analyze.sh

# Weekly on Monday at 8 AM
0 8 * * 1 /path/to/scripts/auto_analyze.sh

# First day of month at 9 AM
0 9 1 * * /path/to/scripts/auto_analyze.sh
```

### Using Task Scheduler (Windows)

1. **Create batch file** (`scripts/auto_analyze.bat`):

```batch
@echo off
cd C:\path\to\email-pattern-analyzer
call venv\Scripts\activate.bat
python scripts\scheduled_analysis.py
```

2. **Open Task Scheduler**
   - Search for "Task Scheduler" in Start Menu
   - Click "Create Basic Task"
   - Name: "Email Pattern Analysis"
   - Trigger: Choose frequency (Daily, Weekly, Monthly)
   - Action: "Start a program"
   - Program: Browse to `auto_analyze.bat`

### Python Scheduling

Create `scripts/scheduled_analysis.py`:

```python
import schedule
import time
import yaml
from datetime import datetime
from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector
from src.stats_generator import StatsGenerator
from src.filter_suggester import FilterSuggester
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/analysis.log'),
        logging.StreamHandler()
    ]
)

def run_analysis():
    """Run scheduled email analysis."""
    try:
        logging.info("Starting scheduled analysis")
        
        # Load config
        with open('config.yaml') as f:
            config = yaml.safe_load(f)
        
        # Connect and fetch
        connector = GmailConnector(config=config)
        connector.authenticate()
        emails = connector.fetch_emails(max_results=1000)
        
        # Analyze
        analyzer = EmailAnalyzer(config)
        results = analyzer.analyze(emails)
        
        # Generate reports
        stats_gen = StatsGenerator(config)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_dir = f'data/reports/{timestamp}'
        reports = stats_gen.generate_all_reports(results, output_dir)
        
        # Get suggestions
        suggester = FilterSuggester(config)
        suggestions = suggester.generate_suggestions(results)
        
        # Log summary
        logging.info(f"Analysis complete:")
        logging.info(f"  Total emails: {results['total_emails']}")
        logging.info(f"  Top sender: {results['sender_stats']['top_sender']['email']}")
        logging.info(f"  Suggestions: {len(suggestions)}")
        logging.info(f"  Reports: {output_dir}")
        
        # Send notifications if configured
        if config.get('notifications', {}).get('enabled'):
            send_notification(results, suggestions, reports)
        
    except Exception as e:
        logging.error(f"Analysis failed: {e}", exc_info=True)

def send_notification(results, suggestions, reports):
    """Send notification with results."""
    # Implementation depends on notification method
    pass

# Schedule jobs
schedule.every().day.at("06:00").do(run_analysis)
# schedule.every().monday.at("08:00").do(run_analysis)
# schedule.every().hour.do(run_analysis)

if __name__ == "__main__":
    logging.info("Scheduler started")
    
    # Run once immediately
    run_analysis()
    
    # Then run on schedule
    while True:
        schedule.run_pending()
        time.sleep(60)
```

Run it:
```bash
python scripts/scheduled_analysis.py
```

## Email Notifications

### Configure Email Alerts

In `config.yaml`:

```yaml
notifications:
  enabled: true
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    sender: analyzer@gmail.com
    password: YOUR_APP_PASSWORD  # Use App Password, not regular password
    recipients:
      - your-email@gmail.com
```

### Email Notification Script

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

def send_email_report(results, suggestions, reports, config):
    """Send email with analysis results."""
    email_config = config['notifications']['email']
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = email_config['sender']
    msg['To'] = ', '.join(email_config['recipients'])
    msg['Subject'] = f"Email Analysis Report - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Email body
    body = f"""
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; }}
            .stat {{ background: #f0f0f0; padding: 10px; margin: 10px 0; border-radius: 5px; }}
            .stat-label {{ font-weight: bold; color: #333; }}
            .stat-value {{ font-size: 20px; color: #007bff; }}
            .suggestion {{ background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; }}
        </style>
    </head>
    <body>
        <h2>Email Analysis Report</h2>
        
        <div class="stat">
            <div class="stat-label">Total Emails Analyzed</div>
            <div class="stat-value">{results['total_emails']}</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">Top Sender</div>
            <div class="stat-value">{results['sender_stats']['top_sender']['email']}</div>
            <div>{results['sender_stats']['top_sender']['percentage']:.1f}% of emails</div>
        </div>
        
        <div class="stat">
            <div class="stat-label">Peak Email Time</div>
            <div class="stat-value">{results['temporal_patterns']['peak_hour']}:00</div>
        </div>
        
        <h3>Top Suggestions</h3>
    """
    
    # Add top 3 suggestions
    for suggestion in suggestions[:3]:
        body += f"""
        <div class="suggestion">
            <strong>{suggestion['rule']}</strong><br>
            {suggestion['reason']}<br>
            <small>Confidence: {suggestion['confidence']:.0f}% | Impact: {suggestion['impact']}</small>
        </div>
        """
    
    body += """
        <p>Full reports attached.</p>
        <p><small>This is an automated email from Email Pattern Analyzer.</small></p>
    </body>
    </html>
    """
    
    msg.attach(MIMEText(body, 'html'))
    
    # Attach JSON report
    if 'json' in reports:
        with open(reports['json'], 'rb') as f:
            attachment = MIMEBase('application', 'json')
            attachment.set_payload(f.read())
            encoders.encode_base64(attachment)
            attachment.add_header('Content-Disposition', f'attachment; filename=analysis.json')
            msg.attach(attachment)
    
    # Send email
    try:
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        server.starttls()
        server.login(email_config['sender'], email_config['password'])
        server.send_message(msg)
        server.quit()
        logging.info("Email notification sent")
        return True
    except Exception as e:
        logging.error(f"Failed to send email: {e}")
        return False
```

## Webhook Notifications

### Slack Integration

```python
import requests
import json

def send_slack_notification(results, suggestions, webhook_url):
    """Send analysis results to Slack."""
    
    # Build message blocks
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "📧 Email Analysis Complete"
            }
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Total Emails:*\n{results['total_emails']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Emails/Day:*\n{results['basic_stats']['avg_per_day']:.1f}"
                }
            ]
        },
        {
            "type": "section",
            "fields": [
                {
                    "type": "mrkdwn",
                    "text": f"*Top Sender:*\n{results['sender_stats']['top_sender']['email']}"
                },
                {
                    "type": "mrkdwn",
                    "text": f"*Peak Hour:*\n{results['temporal_patterns']['peak_hour']}:00"
                }
            ]
        },
        {
            "type": "divider"
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Top Suggestions:*"
            }
        }
    ]
    
    # Add suggestions
    for i, suggestion in enumerate(suggestions[:3], 1):
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{i}. *{suggestion['rule']}*\n{suggestion['reason']}\n_Confidence: {suggestion['confidence']:.0f}%_"
            }
        })
    
    payload = {
        "blocks": blocks
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200
```

### Microsoft Teams Integration

```python
def send_teams_notification(results, suggestions, webhook_url):
    """Send analysis results to Microsoft Teams."""
    
    payload = {
        "@type": "MessageCard",
        "@context": "https://schema.org/extensions",
        "summary": "Email Analysis Complete",
        "themeColor": "0078D7",
        "title": "📧 Email Analysis Report",
        "sections": [
            {
                "activityTitle": "Analysis Summary",
                "facts": [
                    {
                        "name": "Total Emails",
                        "value": str(results['total_emails'])
                    },
                    {
                        "name": "Emails per Day",
                        "value": f"{results['basic_stats']['avg_per_day']:.1f}"
                    },
                    {
                        "name": "Top Sender",
                        "value": results['sender_stats']['top_sender']['email']
                    }
                ]
            },
            {
                "activityTitle": "Top Suggestions",
                "text": "\n\n".join([
                    f"**{s['rule']}**  \n{s['reason']}"
                    for s in suggestions[:3]
                ])
            }
        ]
    }
    
    response = requests.post(webhook_url, json=payload)
    return response.status_code == 200
```

## Auto-Apply Filters

### Safe Auto-Application

```python
def auto_apply_filters(suggestions, connector, dry_run=True):
    """Automatically apply high-confidence filter suggestions."""
    
    applied = []
    skipped = []
    
    for suggestion in suggestions:
        # Only auto-apply if:
        # 1. High confidence (>90%)
        # 2. Low risk (auto_label or auto_archive only)
        # 3. Low impact to start
        
        should_apply = (
            suggestion['confidence'] > 90 and
            suggestion['type'] in ['auto_label', 'auto_archive'] and
            suggestion['impact'] == 'low'
        )
        
        if should_apply:
            if dry_run:
                logging.info(f"[DRY RUN] Would apply: {suggestion['rule']}")
                applied.append(suggestion)
            else:
                try:
                    if isinstance(connector, GmailConnector):
                        filter_config = format_suggestion_for_gmail(suggestion)
                        connector.apply_filter(filter_config)
                    else:
                        rule_config = format_suggestion_for_outlook(suggestion)
                        connector.create_rule(rule_config)
                    
                    logging.info(f"Applied: {suggestion['rule']}")
                    applied.append(suggestion)
                    
                except Exception as e:
                    logging.error(f"Failed to apply {suggestion['rule']}: {e}")
                    skipped.append(suggestion)
        else:
            skipped.append(suggestion)
    
    return applied, skipped

# Usage
applied, skipped = auto_apply_filters(suggestions, connector, dry_run=False)
logging.info(f"Applied {len(applied)} filters, skipped {len(skipped)}")
```

## Docker Automation

### Dockerfile for Automation

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Install package
RUN pip install -e .

# Run scheduler
CMD ["python", "scripts/scheduled_analysis.py"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  analyzer:
    build: .
    volumes:
      - ./data:/app/data
      - ./config.yaml:/app/config.yaml:ro
      - ./credentials.json:/app/credentials.json:ro
      - ./logs:/app/logs
    restart: unless-stopped
    environment:
      - TZ=America/New_York
```

Run:
```bash
docker-compose up -d
```

## Monitoring

### Health Check Script

```python
# scripts/health_check.py
import os
import sys
from datetime import datetime, timedelta

def check_health():
    """Check if analysis is running properly."""
    issues = []
    
    # Check if reports are being generated
    report_dir = 'data/reports'
    if os.path.exists(report_dir):
        latest_reports = sorted(os.listdir(report_dir))
        if latest_reports:
            latest = latest_reports[-1]
            # Check if report is recent (within 25 hours for daily)
            # Add logic to parse timestamp and check
            pass
        else:
            issues.append("No reports found")
    else:
        issues.append("Report directory doesn't exist")
    
    # Check log file
    log_file = 'logs/analysis.log'
    if os.path.exists(log_file):
        # Check for recent errors
        with open(log_file, 'r') as f:
            recent_lines = f.readlines()[-100:]
            errors = [l for l in recent_lines if 'ERROR' in l]
            if errors:
                issues.append(f"{len(errors)} errors in recent logs")
    else:
        issues.append("Log file not found")
    
    # Report status
    if issues:
        print("❌ Health Check Failed:")
        for issue in issues:
            print(f"  - {issue}")
        sys.exit(1)
    else:
        print("✅ Health Check Passed")
        sys.exit(0)

if __name__ == "__main__":
    check_health()
```

## Best Practices

1. **Start with dry runs**
   - Test automation without actually applying filters
   - Review suggestions manually first

2. **Gradual rollout**
   - Begin with high-confidence, low-impact suggestions
   - Monitor results before expanding

3. **Keep logs**
   - Log all automated actions
   - Review logs regularly

4. **Set up alerts**
   - Get notified of failures
   - Monitor unusual patterns

5. **Regular reviews**
   - Weekly review of applied filters
   - Monthly review of automation effectiveness

6. **Backup before automation**
   - Export current filter rules
   - Keep copies of important emails

## Troubleshooting Automation

### Common Issues

1. **Authentication expires**
   - Refresh OAuth tokens automatically
   - Set up service account for Gmail

2. **Cron job not running**
   - Check cron logs: `grep CRON /var/log/syslog`
   - Verify script permissions
   - Use absolute paths

3. **Rate limiting**
   - Add delays between API calls
   - Reduce analysis frequency

4. **Memory issues**
   - Process in smaller batches
   - Clear cache between runs
   - Limit email fetching

## Next Steps

- Review [Usage Guide](usage.md) for analysis techniques
- Check [Output Guide](output_guide.md) to understand results
- Read [Customization Guide](customization.md) for advanced features
