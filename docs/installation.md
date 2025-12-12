# Installation Guide

This guide will help you install and set up the Email Pattern Analyzer on your system.

## Prerequisites

- **Python 3.8 or higher** - [Download Python](https://www.python.org/downloads/)
- **pip** (Python package installer) - Usually comes with Python
- **Git** (optional, for cloning) - [Download Git](https://git-scm.com/downloads)
- **Gmail or Outlook account** with API access enabled

## Installation Methods

### Method 1: Install from Source (Recommended)

1. **Clone the repository**

```bash
git clone https://github.com/CrazyDubya/email-pattern-analyzer.git
cd email-pattern-analyzer
```

2. **Create a virtual environment** (recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Install the package**

```bash
# Development mode (recommended for customization)
pip install -e .

# Or regular installation
python setup.py install
```

### Method 2: Direct pip Install

If the package is published to PyPI:

```bash
pip install email-pattern-analyzer
```

## Verifying Installation

Verify that the installation was successful:

```bash
python -c "import src; print(src.__version__)"
```

You should see the version number printed (e.g., `1.0.0`).

## System-Specific Instructions

### Windows

1. **Install Python** from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Open Command Prompt** or PowerShell

3. Follow the installation steps above

4. **Troubleshooting Windows**:
   - If you get SSL errors, try:
     ```bash
     pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
     ```

### macOS

1. **Install Homebrew** (if not already installed):
   ```bash
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```

2. **Install Python**:
   ```bash
   brew install python@3.11
   ```

3. Follow the installation steps above

4. **Troubleshooting macOS**:
   - If you have issues with matplotlib, install:
     ```bash
     brew install pkg-config
     brew install freetype
     ```

### Linux (Ubuntu/Debian)

1. **Update system**:
   ```bash
   sudo apt update
   sudo apt upgrade
   ```

2. **Install Python and pip**:
   ```bash
   sudo apt install python3 python3-pip python3-venv
   ```

3. **Install system dependencies**:
   ```bash
   sudo apt install python3-dev build-essential
   ```

4. Follow the installation steps above

## Optional Dependencies

### For Gmail Support

```bash
pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
```

### For Outlook Support

```bash
pip install msal requests
```

### For Machine Learning Features

```bash
pip install scikit-learn nltk textblob
```

### For Visualization

```bash
pip install matplotlib seaborn
```

## Development Installation

If you want to contribute or modify the code:

1. **Fork the repository** on GitHub

2. **Clone your fork**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/email-pattern-analyzer.git
   cd email-pattern-analyzer
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements.txt
   pip install pytest pytest-cov black flake8 mypy
   ```

4. **Install in editable mode**:
   ```bash
   pip install -e .
   ```

## Docker Installation (Alternative)

If you prefer using Docker:

```dockerfile
# Create a Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN pip install -e .

CMD ["python", "examples/basic_analysis.py"]
```

Build and run:
```bash
docker build -t email-analyzer .
docker run -v $(pwd)/data:/app/data email-analyzer
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'google'**
   - Solution: `pip install google-api-python-client`

2. **SSL Certificate Error**
   - Solution: Update certificates or use `--trusted-host` flag

3. **Permission Denied**
   - Solution: Use `pip install --user` or activate virtual environment

4. **Matplotlib Backend Issues**
   - Solution: Set backend in code: `matplotlib.use('Agg')`

5. **Memory Issues with Large Mailboxes**
   - Solution: Process emails in smaller batches using the `max_results` parameter

### Getting Help

- **GitHub Issues**: [Report a bug](https://github.com/CrazyDubya/email-pattern-analyzer/issues)
- **Documentation**: Check other docs in the `docs/` folder
- **Examples**: Review the `examples/` directory

## Next Steps

After installation:

1. [Configure API Access](configuration.md) - Set up Gmail/Outlook API credentials
2. [Usage Guide](usage.md) - Learn how to use the analyzer
3. [Customization](customization.md) - Customize categories and rules

## Updating

To update to the latest version:

```bash
# If installed from source
cd email-pattern-analyzer
git pull origin main
pip install -r requirements.txt --upgrade
pip install -e . --upgrade

# If installed via pip
pip install email-pattern-analyzer --upgrade
```

## Uninstallation

To completely remove the analyzer:

```bash
pip uninstall email-pattern-analyzer

# Also remove data and cache
rm -rf ~/email-pattern-analyzer
rm -rf data/
```
