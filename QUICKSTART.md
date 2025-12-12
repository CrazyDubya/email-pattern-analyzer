# Quick Start Guide

Get up and running with Email Pattern Analyzer in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Gmail or Outlook account
- 5 minutes of your time

## Installation (2 minutes)

```bash
# Clone the repository
git clone https://github.com/CrazyDubya/email-pattern-analyzer.git
cd email-pattern-analyzer

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration (2 minutes)

### Option A: Gmail

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Gmail API
4. Create OAuth 2.0 credentials (Desktop app)
5. Download credentials as `credentials.json`
6. Copy to project root

### Option B: Outlook

1. Go to [Azure Portal](https://portal.azure.com/)
2. Register new application
3. Add Mail.Read and Mail.ReadWrite permissions
4. Copy Client ID, Tenant ID, and Client Secret

### Configure

```bash
# Copy example config
cp config.yaml.example config.yaml

# Edit config.yaml with your credentials
# For Gmail: Set gmail.enabled = true
# For Outlook: Add your client_id, client_secret, tenant_id
```

## First Run (1 minute)

```bash
python examples/basic_analysis.py
```

That's it! The script will:
1. Authenticate with your email provider (browser will open)
2. Fetch your recent emails
3. Analyze patterns
4. Display results
5. Generate detailed reports

## What You Get

After running, you'll see:

- **Summary Statistics**: Total emails, emails per day, unique senders
- **Top Senders**: Who emails you most
- **Temporal Patterns**: When you get most emails
- **Categories**: Email distribution (promotional, work, personal, etc.)
- **Filter Suggestions**: Intelligent recommendations to organize your inbox
- **Detailed Reports**: JSON, CSV, HTML reports with charts

## Next Steps

### Customize Categories

```bash
python examples/category_customization.py
```

Add custom categories like "VIP", "Project Updates", "Team Communications".

### Set Up Monitoring

```bash
python examples/automated_monitoring.py
```

Continuously monitor your inbox for anomalies and patterns.

### Explore Documentation

- [Installation Guide](docs/installation.md) - Detailed setup instructions
- [Configuration Guide](docs/configuration.md) - All configuration options
- [Usage Guide](docs/usage.md) - Advanced usage examples
- [Customization Guide](docs/customization.md) - Customize for your needs
- [Output Guide](docs/output_guide.md) - Understanding results
- [Automation Guide](docs/automation.md) - Automate analysis

## Common Issues

### Authentication Error
- Make sure credentials.json is in the project root
- Check that you've enabled the Gmail/Outlook API
- Try deleting token.json and re-authenticating

### No Emails Found
- Check your date range in config.yaml
- Verify you have emails in your inbox
- Try increasing max_results

### Import Errors
- Make sure virtual environment is activated
- Run: `pip install -r requirements.txt`

## Getting Help

- **Documentation**: Check the `docs/` folder
- **Examples**: Review the `examples/` folder  
- **Issues**: [GitHub Issues](https://github.com/CrazyDubya/email-pattern-analyzer/issues)

## What's Next?

1. Review your filter suggestions and apply them
2. Set up weekly reports
3. Customize categories for your workflow
4. Share insights with your team
5. Automate your email management!

---

**Happy Analyzing! 📧**
