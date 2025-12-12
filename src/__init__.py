"""Email Pattern Analyzer - A comprehensive email analysis tool.

This package provides tools for analyzing email patterns, categorizing messages,
generating statistics, and suggesting filter rules for Gmail and Outlook.

Modules:
    email_analyzer: Main analysis engine
    categorizer: Message categorization
    pattern_detector: Pattern recognition
    filter_suggester: Filter rule recommendations
    stats_generator: Statistics and reporting
    gmail_connector: Gmail API integration
    outlook_connector: Outlook API integration
"""

__version__ = "1.0.0"
__author__ = "CrazyDubya"
__license__ = "MIT"

from .email_analyzer import EmailAnalyzer
from .categorizer import Categorizer
from .pattern_detector import PatternDetector
from .filter_suggester import FilterSuggester
from .stats_generator import StatsGenerator
from .gmail_connector import GmailConnector
from .outlook_connector import OutlookConnector

__all__ = [
    "EmailAnalyzer",
    "Categorizer",
    "PatternDetector",
    "FilterSuggester",
    "StatsGenerator",
    "GmailConnector",
    "OutlookConnector",
]
