# Email Pattern Analyzer

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A powerful, production-ready email pattern analysis tool that helps you understand your email behavior, categorize messages automatically, and generate intelligent filter rules. Supports both Gmail and Outlook APIs.

## Features

- **📊 Pattern Analysis**: Analyze email frequency, timing patterns, and sender behaviors
- **🏷️ Smart Categorization**: Automatically categorize emails into promotional, personal, work, automated, and more
- **📈 Statistics Generation**: Comprehensive daily, weekly, and monthly email statistics
- **🔍 Filter Suggestions**: AI-powered recommendations for email filter rules
- **🔌 Multi-Platform**: Support for Gmail and Outlook APIs
- **⚙️ Customizable**: Easily configure categories and analysis parameters
- **📦 Production Ready**: Well-structured, documented, and tested code

## Quick Start

```bash
# Clone the repository
git clone https://github.com/CrazyDubya/email-pattern-analyzer.git
cd email-pattern-analyzer

# Install dependencies
pip install -r requirements.txt

# Or install as a package
pip install -e .

# Copy and configure settings
cp config.yaml.example config.yaml
# Edit config.yaml with your API credentials

# Run basic analysis
python examples/basic_analysis.py
```

## Installation

For detailed installation instructions, see [docs/installation.md](docs/installation.md).

### Requirements

- Python 3.8 or higher
- Gmail API credentials (for Gmail analysis)
- Outlook API credentials (for Outlook analysis)
- Internet connection for API access

### Quick Install

```bash
# Using pip
pip install -r requirements.txt

# Or using setup.py
python setup.py install
```

## Configuration

Before running the analyzer, you need to set up your API credentials:

1. **Gmail**: Follow the [Gmail API setup guide](docs/configuration.md#gmail-setup)
2. **Outlook**: Follow the [Outlook API setup guide](docs/configuration.md#outlook-setup)
3. **Copy configuration template**: `cp config.yaml.example config.yaml`
4. **Edit config.yaml** with your credentials and preferences

See [docs/configuration.md](docs/configuration.md) for detailed configuration instructions.

## Usage

### Basic Analysis

```python
from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector

# Initialize connector
connector = GmailConnector('path/to/credentials.json')
emails = connector.fetch_emails(max_results=1000)

# Analyze patterns
analyzer = EmailAnalyzer()
results = analyzer.analyze(emails)

print(f"Total emails analyzed: {results['total_emails']}")
print(f"Most active sender: {results['top_sender']}")
print(f"Peak email time: {results['peak_hour']}")
```

### Categorization

```python
from src.categorizer import Categorizer

categorizer = Categorizer()
for email in emails:
    category = categorizer.categorize(email)
    print(f"Email from {email['sender']}: {category}")
```

### Generate Filter Suggestions

```python
from src.filter_suggester import FilterSuggester

suggester = FilterSuggester()
suggestions = suggester.generate_suggestions(results)

for suggestion in suggestions:
    print(f"Rule: {suggestion['rule']}")
    print(f"Reason: {suggestion['reason']}")
    print(f"Confidence: {suggestion['confidence']}%")
```

For more examples, see the [examples/](examples/) directory.

## Project Structure

```
email-pattern-analyzer/
├── src/
│   ├── __init__.py
│   ├── email_analyzer.py      # Main analysis engine
│   ├── categorizer.py          # Message categorization
│   ├── pattern_detector.py     # Pattern recognition
│   ├── filter_suggester.py     # Filter rule recommendations
│   ├── stats_generator.py      # Statistics and reporting
│   ├── gmail_connector.py      # Gmail API integration
│   └── outlook_connector.py    # Outlook API integration
├── config/
│   └── README.md               # Configuration documentation
├── data/
│   └── README.md               # Data storage documentation
├── docs/
│   ├── installation.md         # Installation guide
│   ├── configuration.md        # Configuration guide
│   ├── usage.md                # Usage examples
│   ├── customization.md        # Customization guide
│   ├── output_guide.md         # Understanding output
│   └── automation.md           # Automation setup
├── examples/
│   ├── basic_analysis.py       # Basic usage example
│   ├── category_customization.py  # Custom categories
│   └── automated_monitoring.py    # Automated monitoring
├── README.md
├── requirements.txt
├── setup.py
├── config.yaml.example
├── .gitignore
└── LICENSE
```

## Documentation

- **[Installation Guide](docs/installation.md)**: Detailed installation instructions
- **[Configuration Guide](docs/configuration.md)**: API setup and configuration
- **[Usage Guide](docs/usage.md)**: Comprehensive usage examples
- **[Customization Guide](docs/customization.md)**: Customizing categories and rules
- **[Output Guide](docs/output_guide.md)**: Understanding analysis results
- **[Automation Guide](docs/automation.md)**: Setting up automated monitoring

## Key Features Explained

### Pattern Detection

- **Temporal Patterns**: Identifies peak email times, day-of-week patterns, and trend analysis
- **Sender Patterns**: Detects frequent senders, response time patterns, and communication clusters
- **Volume Patterns**: Analyzes email volume trends, anomaly detection, and seasonal patterns
- **Content Patterns**: Identifies recurring keywords, subject line patterns, and thread behaviors

### Smart Categorization

Automatic categorization into:
- **Promotional**: Marketing emails, newsletters, offers
- **Personal**: Messages from known contacts, personal communications
- **Work**: Professional emails, meeting invites, project discussions
- **Automated**: System notifications, alerts, automated reports
- **Social**: Social media notifications, community updates
- **Financial**: Bills, statements, transaction alerts
- **Spam**: Unwanted or suspicious emails

### Filter Suggestions

Generate intelligent filter rules based on:
- High-volume senders that could be auto-archived
- Promotional content that could be auto-labeled
- Important senders that should be prioritized
- Time-based patterns for better organization
- Subject line patterns for automatic categorization

## API Support

### Gmail API
- Full access to Gmail mailbox
- Support for labels and filters
- Batch operations for efficiency
- OAuth 2.0 authentication

### Outlook API
- Microsoft Graph API integration
- Access to Outlook mailbox
- Support for folders and rules
- OAuth 2.0 authentication

## Performance

- Efficiently handles mailboxes with 10,000+ emails
- Batch processing for API calls
- Caching for repeated analyses
- Parallel processing support
- Memory-efficient streaming for large datasets

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

If you encounter any issues or have questions:
- Open an issue on GitHub
- Check the [documentation](docs/)
- Review the [examples](examples/)

## Roadmap

- [ ] Machine learning-based categorization improvements
- [ ] Real-time monitoring dashboard
- [ ] Additional email provider support (Yahoo, ProtonMail)
- [ ] Browser extension for inline analysis
- [ ] Mobile app integration
- [ ] Advanced natural language processing
- [ ] Integration with task management tools

## Acknowledgments

Built with:
- Google Gmail API
- Microsoft Graph API
- Python email processing libraries
- Machine learning categorization models

---

**Made with ❤️ for better email management**
