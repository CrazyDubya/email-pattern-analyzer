# Output Guide

Understand the output and results from the Email Pattern Analyzer.

## Analysis Results Structure

The main `analyze()` method returns a dictionary with the following structure:

```python
{
    "total_emails": 1234,
    "date_range": {
        "start": "2024-01-01T00:00:00",
        "end": "2024-12-12T23:59:59"
    },
    "basic_stats": {...},
    "sender_stats": {...},
    "temporal_patterns": {...},
    "categories": {...},
    "patterns": {...},
    "recommendations": [...],
    "analysis_timestamp": "2024-12-12T11:59:00"
}
```

## Basic Statistics

```python
"basic_stats": {
    "date_range": {
        "start": "2024-01-01T00:00:00",
        "end": "2024-12-12T23:59:59"
    },
    "total_size_mb": 245.67,
    "avg_per_day": 15.3,
    "unique_senders": 342,
    "unique_threads": 567
}
```

**Interpretation:**
- `total_size_mb`: Total storage used by emails
- `avg_per_day`: Average emails received daily
- `unique_senders`: Number of different people/systems that sent you emails
- `unique_threads`: Number of separate conversations

## Sender Statistics

```python
"sender_stats": {
    "total_senders": 342,
    "top_sender": {
        "email": "newsletter@company.com",
        "count": 156,
        "percentage": 12.6
    },
    "top_senders": [
        {
            "email": "newsletter@company.com",
            "count": 156,
            "percentage": 12.6
        },
        // ... more senders
    ],
    "sender_frequency": {
        "regular@sender.com": {
            "avg_days_between": 7.2,
            "regularity_score": 0.85
        }
    }
}
```

**Key Metrics:**
- `count`: Number of emails from this sender
- `percentage`: Percentage of your total emails
- `avg_days_between`: Average days between emails from this sender
- `regularity_score`: 0-1, higher = more consistent timing (1.0 = perfectly regular)

**What to Look For:**
- Senders with >10% should probably be filtered
- High regularity_score (>0.8) indicates automated/scheduled emails
- Low regularity with high volume may indicate spam

## Temporal Patterns

```python
"temporal_patterns": {
    "peak_hour": 14,  // 2 PM
    "hourly_distribution": {
        "0": 5,
        "1": 2,
        // ... all 24 hours
        "23": 8
    },
    "peak_day": "Monday",
    "daily_distribution": {
        "Monday": 245,
        "Tuesday": 198,
        // ... all days
        "Sunday": 45
    },
    "monthly_trends": {
        "2024-01": 456,
        "2024-02": 489,
        // ... all months
    },
    "weekend_percentage": 15.3
}
```

**Interpretation:**
- `peak_hour`: Hour when you receive most emails (24-hour format)
- `peak_day`: Day of week with most emails
- `weekend_percentage`: Emails received on Sat/Sun

**Insights:**
- If peak_hour is during work hours (9-17), mostly work emails
- High weekend_percentage (>30%) may indicate poor work-life balance
- Consistent monthly trends show stable email patterns

## Categories Distribution

```python
"categories": {
    "distribution": {
        "promotional": {
            "count": 345,
            "percentage": 28.0
        },
        "personal": {
            "count": 234,
            "percentage": 19.0
        },
        "work": {
            "count": 456,
            "percentage": 37.0
        },
        "automated": {
            "count": 123,
            "percentage": 10.0
        },
        "social": {
            "count": 45,
            "percentage": 3.6
        },
        "financial": {
            "count": 31,
            "percentage": 2.5
        }
    },
    "dominant_category": "work"
}
```

**Category Definitions:**
- **Promotional**: Marketing, newsletters, sales emails
- **Personal**: Messages from individuals you know
- **Work**: Professional correspondence, meetings, projects
- **Automated**: System notifications, alerts, confirmations
- **Social**: Social media notifications
- **Financial**: Bills, statements, payment receipts
- **Spam**: Unwanted or suspicious emails

**What to Look For:**
- High promotional (>30%): Consider unsubscribing
- Low personal (<10%): May be missing important personal emails
- Work dominating (>60%): Consider separating work/personal accounts

## Pattern Detection

### Temporal Patterns

```python
"patterns": {
    "temporal": {
        "time_of_day": {
            "morning": {"count": 234, "percentage": 19.0},
            "afternoon": {"count": 456, "percentage": 37.0},
            "evening": {"count": 345, "percentage": 28.0},
            "night": {"count": 199, "percentage": 16.0}
        },
        "workweek_vs_weekend": {
            "workdays": {"count": 1045, "percentage": 84.7},
            "weekends": {"count": 189, "percentage": 15.3}
        },
        "has_daily_routine": true,
        "monthly_seasonality": {
            "detected": true,
            "peak_month": "September",
            "monthly_distribution": {...}
        }
    }
}
```

**Insights:**
- `has_daily_routine: true`: Emails arrive at consistent times daily
- High night percentage (>20%): May need to adjust notification settings
- `monthly_seasonality: true`: Email volume varies by season/month

### Sender Patterns

```python
"patterns": {
    "sender": {
        "frequent_senders": [
            {
                "sender": "newsletter@company.com",
                "count": 156,
                "emails_per_month": 52.0
            }
        ],
        "burst_senders": [
            {
                "sender": "notifications@app.com",
                "burst_score": 0.85
            }
        ],
        "regular_senders": [
            {
                "sender": "weekly@report.com",
                "regularity_score": 0.92
            }
        ]
    }
}
```

**Metrics:**
- `burst_score`: 0-1, indicates emails arrive in clusters (1.0 = all at once)
- `regularity_score`: 0-1, indicates consistent timing (1.0 = perfectly regular)

**Actions:**
- High burst_score (>0.8): Consider batching notifications
- High regularity_score (>0.9): Good candidate for auto-archiving
- High frequency (>50/month): Definitely needs a filter

### Content Patterns

```python
"patterns": {
    "content": {
        "common_keywords": {
            "meeting": 89,
            "update": 67,
            "reminder": 54,
            "invoice": 43
        },
        "subject_patterns": [
            {
                "pattern": "weekly report",
                "occurrences": 52,
                "percentage": 4.2
            }
        ],
        "newsletter_percentage": 23.5
    }
}
```

**Insights:**
- High keyword frequency suggests common themes
- Subject patterns reveal automated/recurring emails
- High newsletter_percentage (>20%): Many subscription emails

### Volume Patterns

```python
"patterns": {
    "volume": {
        "average_daily": 15.3,
        "std_deviation": 4.2,
        "trend": "increasing",  // or "decreasing", "stable"
        "anomalies": [
            {
                "date": "2024-09-15",
                "count": 87,
                "deviation": 3.2,
                "type": "spike"
            }
        ]
    }
}
```

**Understanding Trends:**
- `increasing`: Email volume growing over time
- `stable`: Consistent email volume
- `decreasing`: Email volume declining

**Anomalies:**
- `spike`: Unusually high volume on that date
- `drop`: Unusually low volume
- Check anomaly dates for context (product launch, vacation, etc.)

## Recommendations

```python
"recommendations": [
    {
        "type": "filter",
        "priority": "high",
        "title": "Create filter for high-volume sender",
        "description": "newsletter@company.com accounts for 12.6% of your emails",
        "action": "Consider auto-labeling or archiving emails from newsletter@company.com"
    },
    {
        "type": "organization",
        "priority": "medium",
        "title": "High promotional email volume",
        "description": "Promotional emails make up 28.0% of your inbox",
        "action": "Consider unsubscribing or auto-archiving promotional emails"
    }
]
```

**Priority Levels:**
- `high`: Should act on soon (>10% email volume affected)
- `medium`: Worth considering (5-10% affected)
- `low`: Optional optimization (<5% affected)

**Recommendation Types:**
- `filter`: Create an email filter/rule
- `organization`: Better email organization
- `cleanup`: Delete or archive old emails
- `unsubscribe`: Unsubscribe from newsletters

## Filter Suggestions

```python
suggestions = [
    {
        "type": "auto_archive",
        "rule": "Archive emails from newsletter@company.com",
        "filter_criteria": {
            "from": "newsletter@company.com"
        },
        "action": "archive",
        "reason": "This sender accounts for 12.6% of your emails (156 emails)",
        "confidence": 85,
        "priority": 1,
        "impact": "high",
        "estimated_emails_affected": 156
    }
]
```

**Confidence Scores:**
- 90-100: Very confident, should definitely apply
- 75-89: Confident, likely beneficial
- 60-74: Moderate confidence, review before applying
- <60: Low confidence, manual review recommended

**Impact Levels:**
- `high`: Affects >100 emails or >10% of inbox
- `medium`: Affects 20-100 emails or 2-10% of inbox
- `low`: Affects <20 emails or <2% of inbox

## Statistics Reports

### JSON Output

The `generate_statistics()` method produces:

```json
{
  "summary": {
    "total_emails": 1234,
    "emails_per_day": 15.3,
    "unique_senders": 342,
    "top_sender": "newsletter@company.com",
    "dominant_category": "work"
  },
  "daily": {...},
  "weekly": {...},
  "monthly": {...},
  "sender_stats": {...},
  "category_stats": {...}
}
```

### CSV Output

Flattened statistics in tabular format:

```csv
Category,Metric,Value
summary,total_emails,1234
summary,emails_per_day,15.3
top_sender,newsletter@company.com,156
```

### HTML Report

Visual report with:
- Summary statistics boxes
- Top senders table
- Category distribution
- Styled with CSS

## Visualization Outputs

### Charts Generated

1. **Hourly Distribution** (`hourly_distribution.png`)
   - Bar chart showing emails by hour of day
   - Identifies peak email times

2. **Category Distribution** (`category_distribution.png`)
   - Pie chart of email categories
   - Shows proportional breakdown

3. **Top Senders** (`top_senders.png`)
   - Horizontal bar chart of top 10 senders
   - Ordered by volume

4. **Monthly Trend** (`monthly_trend.png`)
   - Line chart showing email volume over time
   - Reveals trends and seasonality

## Using the Results

### Quick Assessment

```python
results = analyzer.analyze(emails)

# Quick health check
print(f"Email Health Score:")
print(f"  Volume: {results['basic_stats']['avg_per_day']:.1f} emails/day")
print(f"  Sender diversity: {results['sender_stats']['total_senders']} unique")
print(f"  Top sender dominance: {results['sender_stats']['top_sender']['percentage']:.1f}%")
print(f"  Work-life balance: {results['temporal_patterns']['weekend_percentage']:.1f}% weekend")

if results['basic_stats']['avg_per_day'] > 50:
    print("⚠️  High email volume! Consider aggressive filtering.")

if results['sender_stats']['top_sender']['percentage'] > 20:
    print("⚠️  One sender dominates! Create a filter.")

if results['temporal_patterns']['weekend_percentage'] > 30:
    print("⚠️  High weekend email! Consider boundary setting.")
```

### Acting on Suggestions

```python
suggestions = suggester.generate_suggestions(results)

# Auto-apply high-confidence suggestions
for suggestion in suggestions:
    if suggestion['confidence'] > 85 and suggestion['priority'] == 1:
        print(f"Applying: {suggestion['rule']}")
        
        if 'gmail' in connector.__class__.__name__.lower():
            filter_config = suggester.format_suggestion_for_gmail(suggestion)
            connector.apply_filter(filter_config)
```

## Next Steps

- [Automation Guide](automation.md) - Automate regular analysis
- [Customization Guide](customization.md) - Customize for your needs
