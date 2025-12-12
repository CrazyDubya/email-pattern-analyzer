# Customization Guide

Learn how to customize the Email Pattern Analyzer to fit your specific needs.

## Custom Categories

### Adding Categories via Configuration

Edit `config.yaml`:

```yaml
categorization:
  custom_categories:
    - name: Client Emails
      keywords: ["proposal", "contract", "client meeting", "deliverable"]
      senders: ["client@company.com", "@clientdomain.com"]
      priority: high
    
    - name: Team Standup
      keywords: ["standup", "daily update", "team sync"]
      senders: ["team@company.com"]
      priority: medium
```

### Adding Categories Programmatically

```python
from src.categorizer import Categorizer

categorizer = Categorizer(config)

# Add a new category
categorizer.add_custom_category(
    name='Bug Reports',
    keywords=['bug', 'error', 'crash', 'issue', 'broken'],
    senders=['bugs@tracker.com', 'jira@company.com'],
    priority='high'
)

# Add multiple categories
for category_def in my_custom_categories:
    categorizer.add_custom_category(**category_def)
```

### Creating Category Rules

```python
class CustomCategorizer(Categorizer):
    """Extended categorizer with custom logic."""
    
    def categorize(self, email):
        # Check custom rules first
        if self._is_urgent(email):
            return 'urgent'
        
        if self._is_from_vip(email):
            return 'vip'
        
        # Fall back to default categorization
        return super().categorize(email)
    
    def _is_urgent(self, email):
        """Check if email is urgent."""
        subject = email.get('subject', '').lower()
        urgent_keywords = ['urgent', 'asap', 'critical', 'emergency']
        return any(kw in subject for kw in urgent_keywords)
    
    def _is_from_vip(self, email):
        """Check if email is from VIP sender."""
        vip_senders = ['ceo@company.com', 'board@company.com']
        sender = email.get('sender', '').lower()
        return any(vip in sender for vip in vip_senders)

# Use custom categorizer
categorizer = CustomCategorizer(config)
```

## Custom Pattern Detection

### Extending Pattern Detector

```python
from src.pattern_detector import PatternDetector

class CustomPatternDetector(PatternDetector):
    """Extended pattern detector with custom patterns."""
    
    def detect_patterns(self, emails):
        # Get default patterns
        patterns = super().detect_patterns(emails)
        
        # Add custom patterns
        patterns['custom'] = {
            'weekend_worker': self._detect_weekend_worker(emails),
            'night_owl': self._detect_night_owl(emails),
            'email_hoarder': self._detect_email_hoarder(emails)
        }
        
        return patterns
    
    def _detect_weekend_worker(self, emails):
        """Detect if user works on weekends."""
        weekend_emails = sum(1 for e in emails if e['date'].weekday() >= 5)
        total = len(emails)
        weekend_pct = (weekend_emails / total) * 100 if total > 0 else 0
        
        return {
            'detected': weekend_pct > 20,
            'percentage': weekend_pct,
            'count': weekend_emails
        }
    
    def _detect_night_owl(self, emails):
        """Detect late-night email activity."""
        night_emails = sum(1 for e in emails if e['date'].hour >= 22 or e['date'].hour < 6)
        total = len(emails)
        night_pct = (night_emails / total) * 100 if total > 0 else 0
        
        return {
            'detected': night_pct > 15,
            'percentage': night_pct,
            'peak_hours': [e['date'].hour for e in emails if e['date'].hour >= 22 or e['date'].hour < 6]
        }
```

## Custom Filter Suggestions

### Creating Custom Suggestion Rules

```python
from src.filter_suggester import FilterSuggester

class CustomFilterSuggester(FilterSuggester):
    """Extended filter suggester with custom rules."""
    
    def generate_suggestions(self, analysis_results):
        # Get default suggestions
        suggestions = super().generate_suggestions(analysis_results)
        
        # Add custom suggestions
        suggestions.extend(self._suggest_meeting_filters(analysis_results))
        suggestions.extend(self._suggest_time_based_filters(analysis_results))
        
        return suggestions
    
    def _suggest_meeting_filters(self, results):
        """Suggest filters for meeting-related emails."""
        suggestions = []
        
        # Check for high volume of meeting invites
        patterns = results.get('patterns', {}).get('content', {})
        keywords = patterns.get('common_keywords', {})
        
        if keywords.get('meeting', 0) > 50:
            suggestions.append({
                'type': 'auto_label',
                'rule': 'Label meeting invites',
                'filter_criteria': {
                    'subject_contains': 'meeting invitation'
                },
                'action': 'add_label',
                'label': 'Meetings',
                'reason': 'High volume of meeting-related emails',
                'confidence': 85,
                'priority': 2
            })
        
        return suggestions
```

## Custom Statistics

### Adding Custom Metrics

```python
from src.stats_generator import StatsGenerator

class CustomStatsGenerator(StatsGenerator):
    """Extended stats generator with custom metrics."""
    
    def generate_statistics(self, analysis_results):
        # Get default stats
        stats = super().generate_statistics(analysis_results)
        
        # Add custom stats
        stats['custom_metrics'] = {
            'response_time': self._calculate_response_time(analysis_results),
            'engagement_score': self._calculate_engagement_score(analysis_results),
            'productivity_index': self._calculate_productivity_index(analysis_results)
        }
        
        return stats
    
    def _calculate_engagement_score(self, results):
        """Calculate email engagement score."""
        # Example: Based on variety of senders and reply rate
        sender_stats = results.get('sender_stats', {})
        diversity = sender_stats.get('sender_diversity', 'medium')
        
        diversity_scores = {'high': 100, 'medium': 70, 'low': 40}
        return diversity_scores.get(diversity, 50)
```

## Custom Visualizations

### Creating Custom Charts

```python
import matplotlib.pyplot as plt
import seaborn as sns

def create_sender_network_chart(results, output_path='sender_network.png'):
    """Create a network visualization of top senders."""
    import networkx as nx
    
    G = nx.Graph()
    
    # Add nodes for top senders
    top_senders = results['sender_stats']['top_senders'][:10]
    for sender in top_senders:
        G.add_node(sender['email'], weight=sender['count'])
    
    # Draw
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G)
    
    # Node sizes based on email count
    node_sizes = [G.nodes[node]['weight'] * 10 for node in G.nodes()]
    
    nx.draw(G, pos, with_labels=True, node_size=node_sizes, 
            node_color='lightblue', font_size=8, font_weight='bold')
    
    plt.title('Top Email Senders Network')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()

def create_heatmap(results, output_path='email_heatmap.png'):
    """Create a heatmap of email activity by day and hour."""
    import pandas as pd
    
    # Create day/hour matrix
    data = []
    for email in results.get('emails', []):
        data.append({
            'day': email['date'].strftime('%A'),
            'hour': email['date'].hour
        })
    
    df = pd.DataFrame(data)
    heatmap_data = df.groupby(['day', 'hour']).size().unstack(fill_value=0)
    
    # Reorder days
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_data = heatmap_data.reindex(days_order)
    
    # Plot
    plt.figure(figsize=(14, 6))
    sns.heatmap(heatmap_data, cmap='YlOrRd', annot=True, fmt='d')
    plt.title('Email Activity Heatmap')
    plt.xlabel('Hour of Day')
    plt.ylabel('Day of Week')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
```

## Custom API Connectors

### Creating a Yahoo Mail Connector

```python
class YahooConnector:
    """Custom connector for Yahoo Mail (example)."""
    
    def __init__(self, username, password, config=None):
        self.username = username
        self.password = password
        self.config = config or {}
    
    def authenticate(self):
        """Authenticate with Yahoo Mail."""
        # Implementation would use Yahoo API or IMAP
        pass
    
    def fetch_emails(self, max_results=1000):
        """Fetch emails from Yahoo Mail."""
        # Implementation
        pass
```

## Custom Workflows

### Automated Weekly Digest

```python
import schedule
import time
from datetime import datetime, timedelta

def weekly_digest():
    """Generate and email weekly digest."""
    # Fetch last week's emails
    after_date = datetime.now() - timedelta(days=7)
    emails = connector.fetch_emails(after_date=after_date)
    
    # Analyze
    results = analyzer.analyze(emails)
    
    # Generate report
    stats_gen = StatsGenerator(config)
    reports = stats_gen.generate_all_reports(results)
    
    # Send via email
    send_email_report(reports, to='your-email@example.com')
    
    print(f"Weekly digest sent: {datetime.now()}")

# Schedule
schedule.every().monday.at("09:00").do(weekly_digest)

while True:
    schedule.run_pending()
    time.sleep(60)
```

### Custom Alert System

```python
def check_for_urgent_patterns(results):
    """Check for concerning email patterns."""
    alerts = []
    
    # Check for email overload
    if results['basic_stats']['avg_per_day'] > 200:
        alerts.append({
            'level': 'warning',
            'message': f"High email volume: {results['basic_stats']['avg_per_day']:.0f} per day",
            'suggestion': 'Consider aggressive filtering'
        })
    
    # Check for late-night emails
    patterns = results['patterns']['temporal']
    night_pct = patterns.get('time_of_day', {}).get('night', {}).get('percentage', 0)
    
    if night_pct > 20:
        alerts.append({
            'level': 'info',
            'message': f"{night_pct:.1f}% of emails received at night",
            'suggestion': 'Consider adjusting notification settings'
        })
    
    return alerts

# Usage
alerts = check_for_urgent_patterns(results)
for alert in alerts:
    print(f"[{alert['level'].upper()}] {alert['message']}")
    print(f"  Suggestion: {alert['suggestion']}")
```

## Configuration Templates

### Work Email Configuration

```yaml
# config_work.yaml
analysis:
  time_range_days: 30
  enable_ml_categorization: true

categorization:
  custom_categories:
    - name: Management
      senders: ["manager@company.com", "director@company.com"]
      priority: high
    
    - name: Team
      senders: ["@team.company.com"]
      priority: medium

filter_suggestions:
  aggressive_mode: false
  suggestion_types:
    - auto_label
    - priority_inbox
```

### Personal Email Configuration

```yaml
# config_personal.yaml
analysis:
  time_range_days: 180
  enable_ml_categorization: true

categorization:
  custom_categories:
    - name: Family
      senders: ["family@example.com"]
      priority: high
    
    - name: Friends
      keywords: ["get together", "hang out", "catch up"]
      priority: medium

filter_suggestions:
  aggressive_mode: true
  suggestion_types:
    - auto_archive
    - spam_detection
```

## Next Steps

- [Output Guide](output_guide.md) - Understanding the analysis output
- [Automation Guide](automation.md) - Automating your workflow
