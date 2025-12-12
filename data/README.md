# Data Directory

This directory stores analysis results, reports, and cached data.

## Directory Structure

```
data/
├── reports/          # Generated reports
│   ├── 20241212_120000/
│   │   ├── email_stats.json
│   │   ├── email_stats.csv
│   │   ├── email_stats.html
│   │   ├── hourly_distribution.png
│   │   ├── category_distribution.png
│   │   ├── top_senders.png
│   │   └── monthly_trend.png
│   └── latest/       # Symlink to most recent report
├── cache/            # Cached analysis data
├── exports/          # Manual data exports
└── monitor_state.json # Monitoring state (for automated_monitoring.py)
```

## Generated Files

### Report Files

- **JSON** (`email_stats.json`): Complete analysis results in JSON format
- **CSV** (`email_stats.csv`): Tabular statistics for spreadsheet analysis
- **HTML** (`email_stats.html`): Visual report with styled HTML

### Charts

- **Hourly Distribution**: Bar chart of emails by hour
- **Category Distribution**: Pie chart of email categories
- **Top Senders**: Bar chart of most frequent senders
- **Monthly Trend**: Line chart of email volume over time

## Data Retention

Reports are organized by timestamp and kept indefinitely. To manage storage:

```bash
# Remove reports older than 90 days
find data/reports -type d -mtime +90 -exec rm -rf {} +

# Keep only last 10 reports
ls -t data/reports | tail -n +11 | xargs rm -rf
```

## Cache Management

The cache directory stores temporary analysis data:

- Speeds up repeated analyses
- Automatically cleaned based on config
- Safe to delete at any time

Clear cache:

```bash
rm -rf data/cache/*
```

## Backup

To backup your analysis history:

```bash
# Backup reports
tar -czf email_analyzer_backup_$(date +%Y%m%d).tar.gz data/reports

# Backup everything
tar -czf email_analyzer_full_backup_$(date +%Y%m%d).tar.gz data/
```

## Privacy Note

⚠️ Reports may contain:
- Email addresses
- Subject lines
- Sender information
- Usage patterns

Do NOT share reports publicly without reviewing content!

## Accessing Reports

### View in Browser

Open HTML reports directly:

```bash
# macOS
open data/reports/latest/email_stats.html

# Linux
xdg-open data/reports/latest/email_stats.html

# Windows
start data/reports/latest/email_stats.html
```

### Import to Spreadsheet

Import CSV files into:
- Microsoft Excel
- Google Sheets
- LibreOffice Calc

### Parse JSON

Process with tools like `jq`:

```bash
# Extract top senders
jq '.sender_stats.top_senders' data/reports/latest/email_stats.json

# Get email count by category
jq '.category_stats.distribution' data/reports/latest/email_stats.json
```

## Disk Usage

Monitor data directory size:

```bash
du -sh data/
du -sh data/reports/
```

Typical sizes:
- JSON report: 100-500 KB
- CSV report: 50-200 KB
- HTML report: 100-300 KB
- Charts (each): 100-500 KB
- Total per analysis: 1-2 MB
