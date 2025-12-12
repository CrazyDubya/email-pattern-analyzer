"""Email categorization module.

Provides intelligent categorization of emails into promotional, personal,
work, automated, social, financial, and spam categories.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Set
from collections import defaultdict
import numpy as np

logger = logging.getLogger(__name__)


class Categorizer:
    """Email categorizer using rule-based and heuristic methods.
    
    Categorizes emails into:
    - promotional: Marketing, newsletters, offers
    - personal: Messages from known contacts
    - work: Professional communications
    - automated: System notifications, alerts
    - social: Social media notifications
    - financial: Bills, statements, transactions
    - spam: Unwanted or suspicious emails
    """
    
    # Category definitions with keywords and patterns
    CATEGORY_RULES = {
        'promotional': {
            'keywords': [
                'sale', 'discount', 'offer', 'deal', 'promo', 'limited time',
                'buy now', 'shop', 'save', 'coupon', 'free shipping',
                'unsubscribe', 'newsletter', 'special offer', 'today only'
            ],
            'subject_patterns': [
                r'\d+%\s+off',
                r'(sale|deal)\s+(alert|now)',
                r'limited\s+time',
                r'buy\s+\d+\s+get\s+\d+'
            ],
            'sender_patterns': [
                r'(marketing|promo|newsletter|deals)@',
                r'no-?reply@',
                r'info@.*\.(shop|store|retail)'
            ]
        },
        'automated': {
            'keywords': [
                'notification', 'alert', 'automated', 'do not reply',
                'system message', 'confirmation', 'receipt', 'verify',
                'password reset', 'account created', 'noreply'
            ],
            'subject_patterns': [
                r'^(re:|fwd:)?\s*(notification|alert)',
                r'confirmation',
                r'(verify|confirm)\s+your',
                r'password\s+reset'
            ],
            'sender_patterns': [
                r'no-?reply@',
                r'(auto|automated|system|notification)@',
                r'donotreply@'
            ]
        },
        'social': {
            'keywords': [
                'liked your', 'commented on', 'tagged you', 'mentioned you',
                'friend request', 'connection', 'follow', 'notification from',
                'new message on', 'social'
            ],
            'subject_patterns': [
                r'(liked|commented|shared|mentioned)',
                r'friend\s+request',
                r'\d+\s+new\s+(notification|message)s?'
            ],
            'sender_patterns': [
                r'(facebook|twitter|linkedin|instagram|snapchat)@',
                r'notification@.*(social|network)',
                r'(fb|ig|tw)\.com'
            ]
        },
        'financial': {
            'keywords': [
                'invoice', 'payment', 'statement', 'bill', 'transaction',
                'account balance', 'receipt', 'charged', 'refund', 'bank',
                'credit card', 'paypal', 'venmo', 'wire transfer'
            ],
            'subject_patterns': [
                r'(invoice|bill|statement)\s+#?\d+',
                r'payment\s+(received|due|processed)',
                r'\$\d+',
                r'account\s+balance'
            ],
            'sender_patterns': [
                r'(billing|payments|finance|accounting)@',
                r'@(paypal|stripe|square|venmo)',
                r'bank@|credit@'
            ]
        },
        'work': {
            'keywords': [
                'meeting', 'calendar', 'deadline', 'project', 'report',
                'review', 'presentation', 'conference', 'task', 'urgent',
                'action required', 'fyi', 'please review'
            ],
            'subject_patterns': [
                r'^(re:|fwd:)',
                r'meeting\s+(request|invitation)',
                r'(deadline|due date)',
                r'\[project\]|\[task\]'
            ],
            'sender_patterns': [
                r'@(corp|company|inc|ltd)\.com',
                r'(hr|admin|support|team)@'
            ]
        },
        'spam': {
            'keywords': [
                'congratulations you won', 'claim your prize', 'urgent action',
                'verify your account', 'suspended', 'click here immediately',
                'nigerian prince', 'inheritance', 'lottery', 'casino',
                'viagra', 'pills'
            ],
            'subject_patterns': [
                r'!!!+',
                r'\$\$\$',
                r'urgent.*action.*required',
                r'claim.*prize',
                r'won.*\$\d+'
            ],
            'sender_patterns': [
                r'\d{5,}@',  # Many numbers in sender
                r'[a-z]{20,}@',  # Very long random string
            ]
        }
    }
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the categorizer.
        
        Args:
            config: Optional configuration dictionary with custom categories
        """
        self.config = config or {}
        self.custom_categories = self.config.get('categorization', {}).get('custom_categories', [])
        self.confidence_threshold = self.config.get('categorization', {}).get('confidence_threshold', 0.6)
        self.learning_enabled = self.config.get('categorization', {}).get('enable_learning', True)
        
        # Compile regex patterns for efficiency
        self._compile_patterns()
        
        # Learning data
        self.categorization_history = defaultdict(list)
        
        logger.info("Categorizer initialized")
    
    def _compile_patterns(self):
        """Compile regex patterns for efficient matching."""
        self.compiled_patterns = {}
        
        for category, rules in self.CATEGORY_RULES.items():
            self.compiled_patterns[category] = {
                'subject': [re.compile(p, re.IGNORECASE) for p in rules.get('subject_patterns', [])],
                'sender': [re.compile(p, re.IGNORECASE) for p in rules.get('sender_patterns', [])]
            }
    
    def categorize(self, email: Dict[str, Any]) -> str:
        """Categorize an email.
        
        Args:
            email: Email dictionary with 'sender', 'subject', 'body', etc.
        
        Returns:
            Category name as string
        """
        scores = self._calculate_category_scores(email)
        
        # Get category with highest score
        if scores:
            best_category, best_score = max(scores.items(), key=lambda x: x[1])
            
            if best_score >= self.confidence_threshold:
                if self.learning_enabled:
                    self.categorization_history[best_category].append(email)
                return best_category
        
        # Default to personal if no strong match
        return 'personal'
    
    def _calculate_category_scores(self, email: Dict[str, Any]) -> Dict[str, float]:
        """Calculate confidence scores for each category."""
        scores = {}
        
        sender = email.get('sender', '').lower()
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        
        for category, rules in self.CATEGORY_RULES.items():
            score = 0.0
            
            # Check keywords in subject and body
            keywords = rules.get('keywords', [])
            text = f"{subject} {body}"
            keyword_matches = sum(1 for kw in keywords if kw in text)
            score += keyword_matches * 0.3
            
            # Check subject patterns
            for pattern in self.compiled_patterns[category]['subject']:
                if pattern.search(subject):
                    score += 0.5
            
            # Check sender patterns
            for pattern in self.compiled_patterns[category]['sender']:
                if pattern.search(sender):
                    score += 0.7
            
            scores[category] = min(score, 1.0)  # Cap at 1.0
        
        # Check custom categories
        for custom_cat in self.custom_categories:
            score = self._check_custom_category(email, custom_cat)
            if score > 0:
                scores[custom_cat['name']] = score
        
        return scores
    
    def _check_custom_category(self, email: Dict[str, Any], 
                              custom_cat: Dict[str, Any]) -> float:
        """Check if email matches a custom category."""
        score = 0.0
        
        sender = email.get('sender', '').lower()
        subject = email.get('subject', '').lower()
        body = email.get('body', '').lower()
        text = f"{subject} {body}"
        
        # Check keywords
        keywords = custom_cat.get('keywords', [])
        keyword_matches = sum(1 for kw in keywords if kw.lower() in text)
        score += keyword_matches * 0.4
        
        # Check senders
        senders = custom_cat.get('senders', [])
        if any(s.lower() in sender for s in senders):
            score += 0.8
        
        return min(score, 1.0)
    
    def categorize_batch(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Categorize multiple emails efficiently.
        
        Args:
            emails: List of email dictionaries
        
        Returns:
            List of dictionaries with 'email' and 'category' keys
        """
        return [
            {
                'email': email,
                'category': self.categorize(email)
            }
            for email in emails
        ]
    
    def get_category_stats(self, emails: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Get categorization statistics for a list of emails."""
        categorized = self.categorize_batch(emails)
        category_counts = defaultdict(int)
        
        for item in categorized:
            category_counts[item['category']] += 1
        
        total = len(emails)
        return {
            'total': total,
            'distribution': {
                cat: {
                    'count': count,
                    'percentage': (count / total) * 100
                }
                for cat, count in category_counts.items()
            },
            'categories': list(category_counts.keys())
        }
    
    def add_custom_category(self, name: str, keywords: List[str], 
                           senders: Optional[List[str]] = None,
                           priority: str = 'medium'):
        """Add a custom category dynamically.
        
        Args:
            name: Category name
            keywords: List of keywords to match
            senders: Optional list of sender patterns
            priority: Priority level (high, medium, low)
        """
        custom_cat = {
            'name': name,
            'keywords': keywords,
            'senders': senders or [],
            'priority': priority
        }
        
        self.custom_categories.append(custom_cat)
        logger.info(f"Added custom category: {name}")
