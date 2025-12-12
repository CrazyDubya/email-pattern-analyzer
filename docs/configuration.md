# Configuration Guide

This guide explains how to configure the Email Pattern Analyzer, including API credentials setup and customization options.

## Quick Start

1. Copy the example configuration:
   ```bash
   cp config.yaml.example config.yaml
   ```

2. Edit `config.yaml` with your settings

3. Set up API credentials (see below)

## Configuration File Structure

The `config.yaml` file contains all configuration options:

```yaml
general:
  log_level: INFO
  data_directory: ./data
  cache_enabled: true

gmail:
  enabled: true
  credentials_file: credentials.json
  # ... more Gmail settings

outlook:
  enabled: false
  client_id: YOUR_CLIENT_ID
  # ... more Outlook settings

analysis:
  time_range_days: 365
  # ... more analysis settings
```

## Gmail API Setup

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)

2. Click **"Create Project"**
   - Enter a project name (e.g., "Email Analyzer")
   - Click **"Create"**

3. Wait for the project to be created

### Step 2: Enable Gmail API

1. In the Cloud Console, go to **"APIs & Services" > "Library"**

2. Search for **"Gmail API"**

3. Click on it and press **"Enable"**

### Step 3: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services" > "Credentials"**

2. Click **"Create Credentials" > "OAuth client ID"**

3. If prompted, configure the OAuth consent screen:
   - Choose **"External"** user type
   - Fill in required fields:
     - App name: "Email Pattern Analyzer"
     - User support email: Your email
     - Developer contact: Your email
   - Click **"Save and Continue"**
   - Add scopes: `gmail.readonly` and `gmail.modify`
   - Add test users (your email)
   - Click **"Save and Continue"**

4. Back in Credentials, click **"Create Credentials" > "OAuth client ID"**
   - Application type: **"Desktop app"**
   - Name: "Email Analyzer Desktop"
   - Click **"Create"**

5. **Download the credentials**:
   - Click the download icon next to your client ID
   - Save as `credentials.json` in your project root

### Step 4: Configure Gmail Settings

In `config.yaml`:

```yaml
gmail:
  enabled: true
  credentials_file: credentials.json
  token_file: token.json
  scopes:
    - https://www.googleapis.com/auth/gmail.readonly
    - https://www.googleapis.com/auth/gmail.modify
  max_results: 1000
  batch_size: 100
```

### Step 5: First Time Authentication

Run the analyzer for the first time:

```bash
python examples/basic_analysis.py
```

A browser window will open asking you to:
1. Select your Google account
2. Grant permissions to the app
3. You may see a warning that the app is unverified - click "Advanced" then "Go to Email Analyzer (unsafe)"

The authentication token will be saved to `token.json` for future use.

## Outlook/Office 365 API Setup

### Step 1: Register an Azure Application

1. Go to [Azure Portal](https://portal.azure.com/)

2. Navigate to **"Azure Active Directory" > "App registrations"**

3. Click **"New registration"**:
   - Name: "Email Pattern Analyzer"
   - Supported account types: **"Accounts in any organizational directory and personal Microsoft accounts"**
   - Redirect URI: **"Public client/native"** with `http://localhost:8000`
   - Click **"Register"**

### Step 2: Configure API Permissions

1. In your app, go to **"API permissions"**

2. Click **"Add a permission" > "Microsoft Graph" > "Delegated permissions"**

3. Add these permissions:
   - `Mail.Read`
   - `Mail.ReadWrite`
   - `MailboxSettings.Read`

4. Click **"Add permissions"**

5. Click **"Grant admin consent"** (if you're an admin)

### Step 3: Get Credentials

1. Go to **"Overview"** in your app
   - Copy the **Application (client) ID**
   - Copy the **Directory (tenant) ID**

2. Go to **"Certificates & secrets"**
   - Click **"New client secret"**
   - Add description: "Email Analyzer"
   - Expires: Choose duration
   - Click **"Add"**
   - **Copy the secret value immediately** (you won't see it again!)

### Step 4: Configure Outlook Settings

In `config.yaml`:

```yaml
outlook:
  enabled: true
  client_id: YOUR_CLIENT_ID_FROM_STEP3
  client_secret: YOUR_CLIENT_SECRET_FROM_STEP3
  tenant_id: YOUR_TENANT_ID_FROM_STEP3
  redirect_uri: http://localhost:8000
  scopes:
    - https://graph.microsoft.com/Mail.Read
    - https://graph.microsoft.com/Mail.ReadWrite
  max_results: 1000
```

### Step 5: First Time Authentication

When you run the analyzer, it will:
1. Open a browser for authentication
2. Ask you to sign in to your Microsoft account
3. Request permissions
4. Save the token for future use

## Analysis Configuration

### Time Range

```yaml
analysis:
  time_range_days: 365  # Analyze last year (0 = all emails)
  min_pattern_occurrences: 5  # Minimum times a pattern must occur
```

### Pattern Thresholds

```yaml
analysis:
  pattern_thresholds:
    high_volume_sender: 50  # Emails per month to be considered high-volume
    frequent_sender: 20     # Minimum for frequent sender
    spam_likelihood: 0.7    # Threshold for spam detection (0-1)
```

### Advanced Features

```yaml
analysis:
  enable_ml_categorization: true  # Use machine learning
  enable_sentiment_analysis: false  # Analyze email sentiment
  enable_thread_analysis: true    # Analyze conversation threads
```

## Categorization Configuration

### Custom Categories

Add your own categories:

```yaml
categorization:
  custom_categories:
    - name: VIP
      keywords: ["urgent", "important", "asap"]
      senders: ["boss@company.com", "ceo@company.com"]
      priority: high
    
    - name: Newsletters
      keywords: ["unsubscribe", "newsletter", "weekly digest"]
      priority: low
    
    - name: Team Updates
      keywords: ["standup", "sprint", "team meeting"]
      senders: ["team@company.com"]
      priority: medium
```

### Confidence Threshold

```yaml
categorization:
  confidence_threshold: 0.6  # 0-1, higher = more strict
  enable_learning: true      # Learn from corrections
```

## Filter Suggestions Configuration

```yaml
filter_suggestions:
  min_emails_for_suggestion: 10  # Minimum emails before suggesting a filter
  confidence_threshold: 0.75      # Minimum confidence to suggest
  
  suggestion_types:
    - auto_archive
    - auto_label
    - priority_inbox
    - spam_detection
    - auto_delete
  
  aggressive_mode: false  # Suggest more filters (use with caution)
```

## Statistics Configuration

```yaml
statistics:
  report_types:
    - daily
    - weekly
    - monthly
    - yearly
  
  export_formats:
    - json
    - csv
    - html
  
  generate_charts: true
  chart_format: png  # png, svg, or pdf
```

## Performance Configuration

```yaml
performance:
  num_workers: 4              # Parallel processing threads
  cache_memory_limit: 500     # MB
  enable_parallel: true
  rate_limit: 10              # API requests per second
```

## Notifications (for Automation)

```yaml
notifications:
  enabled: true
  
  email:
    enabled: true
    smtp_server: smtp.gmail.com
    smtp_port: 587
    sender: analyzer@gmail.com
    password: YOUR_APP_PASSWORD
    recipients:
      - your-email@gmail.com
  
  webhook:
    enabled: false
    url: https://hooks.slack.com/services/YOUR/WEBHOOK/URL
    method: POST
```

## Environment Variables

You can also use environment variables (overrides config file):

```bash
export EMAIL_ANALYZER_LOG_LEVEL=DEBUG
export EMAIL_ANALYZER_DATA_DIR=/custom/path
export GMAIL_CREDENTIALS=/path/to/credentials.json
export OUTLOOK_CLIENT_ID=your_client_id
export OUTLOOK_CLIENT_SECRET=your_secret
```

Or use a `.env` file:

```env
EMAIL_ANALYZER_LOG_LEVEL=DEBUG
EMAIL_ANALYZER_DATA_DIR=./data
GMAIL_CREDENTIALS=credentials.json
```

## Security Best Practices

1. **Never commit credentials** to version control
   - `credentials.json`, `token.json`, and `config.yaml` are in `.gitignore`

2. **Use app-specific passwords** for email notifications

3. **Limit API scopes** to only what you need

4. **Regularly rotate secrets** in production

5. **Use environment variables** in production instead of config files

## Validation

Validate your configuration:

```python
from src.email_analyzer import EmailAnalyzer
import yaml

with open('config.yaml') as f:
    config = yaml.safe_load(f)

analyzer = EmailAnalyzer(config)
print("Configuration valid!")
```

## Next Steps

- [Usage Guide](usage.md) - Learn how to use the analyzer
- [Customization Guide](customization.md) - Advanced customization
- [Automation Guide](automation.md) - Set up automated analysis
