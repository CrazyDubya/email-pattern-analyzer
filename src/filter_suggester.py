"""Filter suggestion module.

Generates intelligent filter rule suggestions based on email patterns
and user behavior analysis.
"""

import logging
from typing import Dict, List, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class FilterSuggester:
    """Generates filter rule suggestions.
    
    Suggests filters for:
    - Auto-archiving high-volume senders
    - Auto-labeling by category
    - Priority inbox rules
    - Spam detection
    - Auto-deletion rules
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the filter suggester.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        filter_config = self.config.get('filter_suggestions', {})
        
        self.min_emails = filter_config.get('min_emails_for_suggestion', 10)
        self.confidence_threshold = filter_config.get('confidence_threshold', 0.75)
        self.suggestion_types = filter_config.get('suggestion_types', [
            'auto_archive', 'auto_label', 'priority_inbox', 'spam_detection'
        ])
        self.aggressive_mode = filter_config.get('aggressive_mode', False)
        
        logger.info("FilterSuggester initialized")
    
    def generate_suggestions(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate filter suggestions based on analysis results.
        
        Args:
            analysis_results: Output from EmailAnalyzer
        
        Returns:
            List of suggestion dictionaries with rule, reason, confidence, etc.
        """
        suggestions = []
        
        # Auto-archive suggestions
        if 'auto_archive' in self.suggestion_types:
            suggestions.extend(self._suggest_auto_archive(analysis_results))
        
        # Auto-label suggestions
        if 'auto_label' in self.suggestion_types:
            suggestions.extend(self._suggest_auto_label(analysis_results))
        
        # Priority inbox suggestions
        if 'priority_inbox' in self.suggestion_types:
            suggestions.extend(self._suggest_priority_inbox(analysis_results))
        
        # Spam detection suggestions
        if 'spam_detection' in self.suggestion_types:
            suggestions.extend(self._suggest_spam_filters(analysis_results))
        
        # Sort by confidence and priority
        suggestions.sort(key=lambda x: (x.get('priority', 1), -x.get('confidence', 0)))
        
        logger.info(f"Generated {len(suggestions)} filter suggestions")
        return suggestions
    
    def _suggest_auto_archive(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest auto-archive rules for high-volume senders."""
        suggestions = []
        
        sender_stats = results.get('sender_stats', {})
        top_senders = sender_stats.get('top_senders', [])
        categories = results.get('categories', {}).get('distribution', {})
        
        for sender_info in top_senders:
            if sender_info['count'] < self.min_emails:
                continue
            
            # High-volume promotional senders
            if sender_info['percentage'] > 5:  # More than 5% of emails
                confidence = min(sender_info['percentage'] / 10, 1.0)
                
                if confidence >= self.confidence_threshold or self.aggressive_mode:
                    suggestions.append({
                        'type': 'auto_archive',
                        'rule': f"Archive emails from {sender_info['email']}",
                        'filter_criteria': {
                            'from': sender_info['email']
                        },
                        'action': 'archive',
                        'reason': f"This sender accounts for {sender_info['percentage']:.1f}% of your emails ({sender_info['count']} emails)",
                        'confidence': confidence * 100,
                        'priority': 1,
                        'impact': 'high' if sender_info['percentage'] > 10 else 'medium',
                        'estimated_emails_affected': sender_info['count']
                    })
        
        # Suggest archiving all promotional emails
        promo_info = categories.get('promotional', {})
        if promo_info and promo_info.get('percentage', 0) > 20:
            suggestions.append({
                'type': 'auto_archive',
                'rule': 'Archive promotional emails',
                'filter_criteria': {
                    'category': 'promotional'
                },
                'action': 'archive',
                'reason': f"Promotional emails make up {promo_info['percentage']:.1f}% of your inbox",
                'confidence': min(promo_info['percentage'] / 20 * 100, 100),
                'priority': 2,
                'impact': 'high',
                'estimated_emails_affected': promo_info['count']
            })
        
        return suggestions
    
    def _suggest_auto_label(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest auto-labeling rules based on categories."""
        suggestions = []
        
        categories = results.get('categories', {}).get('distribution', {})
        patterns = results.get('patterns', {})
        
        # Suggest labels for major categories
        for category, info in categories.items():
            if info['count'] >= self.min_emails and info['percentage'] > 10:
                suggestions.append({
                    'type': 'auto_label',
                    'rule': f"Auto-label {category} emails",
                    'filter_criteria': {
                        'category': category
                    },
                    'action': 'add_label',
                    'label': category.title(),
                    'reason': f"{category.title()} emails represent {info['percentage']:.1f}% of your inbox",
                    'confidence': min((info['percentage'] / 10) * 100, 100),
                    'priority': 2,
                    'impact': 'medium',
                    'estimated_emails_affected': info['count']
                })
        
        # Suggest labels for frequent senders
        sender_patterns = patterns.get('sender', {}).get('frequent_senders', [])
        for sender_info in sender_patterns[:5]:  # Top 5
            if sender_info['count'] >= self.min_emails * 2:
                # Extract domain for label suggestion
                domain = sender_info['sender'].split('@')[-1].split('.')[0]
                
                suggestions.append({
                    'type': 'auto_label',
                    'rule': f"Auto-label emails from {sender_info['sender']}",
                    'filter_criteria': {
                        'from': sender_info['sender']
                    },
                    'action': 'add_label',
                    'label': domain.title(),
                    'reason': f"Frequent sender with {sender_info['count']} emails",
                    'confidence': 80,
                    'priority': 3,
                    'impact': 'low',
                    'estimated_emails_affected': sender_info['count']
                })
        
        return suggestions
    
    def _suggest_priority_inbox(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest priority inbox rules for important emails."""
        suggestions = []
        
        categories = results.get('categories', {}).get('distribution', {})
        
        # Prioritize work emails
        work_info = categories.get('work', {})
        if work_info and work_info.get('count', 0) >= self.min_emails:
            suggestions.append({
                'type': 'priority_inbox',
                'rule': 'Mark work emails as important',
                'filter_criteria': {
                    'category': 'work'
                },
                'action': 'mark_important',
                'reason': 'Work emails should be prioritized for timely response',
                'confidence': 85,
                'priority': 1,
                'impact': 'medium',
                'estimated_emails_affected': work_info['count']
            })
        
        # De-prioritize promotional
        promo_info = categories.get('promotional', {})
        if promo_info and promo_info.get('percentage', 0) > 15:
            suggestions.append({
                'type': 'priority_inbox',
                'rule': 'Remove importance from promotional emails',
                'filter_criteria': {
                    'category': 'promotional'
                },
                'action': 'mark_not_important',
                'reason': 'Promotional emails rarely require immediate attention',
                'confidence': 80,
                'priority': 2,
                'impact': 'medium',
                'estimated_emails_affected': promo_info['count']
            })
        
        return suggestions
    
    def _suggest_spam_filters(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest spam detection rules."""
        suggestions = []
        
        patterns = results.get('patterns', {})
        content_patterns = patterns.get('content', {})
        
        # Check for high newsletter percentage
        newsletter_pct = content_patterns.get('newsletter_percentage', 0)
        if newsletter_pct > 30:
            suggestions.append({
                'type': 'spam_detection',
                'rule': 'Filter newsletters to separate folder',
                'filter_criteria': {
                    'body_contains': 'unsubscribe'
                },
                'action': 'move_to_folder',
                'folder': 'Newsletters',
                'reason': f'{newsletter_pct:.1f}% of emails are newsletters',
                'confidence': min(newsletter_pct / 30 * 100, 100),
                'priority': 2,
                'impact': 'medium',
                'estimated_emails_affected': int(results.get('total_emails', 0) * newsletter_pct / 100)
            })
        
        return suggestions
    
    def format_suggestion_for_gmail(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Format a suggestion as a Gmail filter."""
        criteria = suggestion.get('filter_criteria', {})
        
        gmail_filter = {
            'criteria': {},
            'action': {}
        }
        
        # Map criteria
        if 'from' in criteria:
            gmail_filter['criteria']['from'] = criteria['from']
        if 'subject' in criteria:
            gmail_filter['criteria']['subject'] = criteria['subject']
        if 'body_contains' in criteria:
            gmail_filter['criteria']['query'] = criteria['body_contains']
        
        # Map actions
        action = suggestion.get('action')
        if action == 'archive':
            gmail_filter['action']['removeLabelIds'] = ['INBOX']
        elif action == 'add_label':
            gmail_filter['action']['addLabelIds'] = [suggestion.get('label', 'Unknown')]
        elif action == 'mark_important':
            gmail_filter['action']['addLabelIds'] = ['IMPORTANT']
        elif action == 'mark_not_important':
            gmail_filter['action']['removeLabelIds'] = ['IMPORTANT']
        
        return gmail_filter
    
    def format_suggestion_for_outlook(self, suggestion: Dict[str, Any]) -> Dict[str, Any]:
        """Format a suggestion as an Outlook rule."""
        criteria = suggestion.get('filter_criteria', {})
        
        outlook_rule = {
            'displayName': suggestion.get('rule', 'New Rule'),
            'isEnabled': True,
            'conditions': {},
            'actions': {}
        }
        
        # Map criteria
        if 'from' in criteria:
            outlook_rule['conditions']['fromAddresses'] = [{
                'emailAddress': {'address': criteria['from']}
            }]
        if 'subject' in criteria:
            outlook_rule['conditions']['subjectContains'] = [criteria['subject']]
        
        # Map actions
        action = suggestion.get('action')
        if action == 'archive':
            outlook_rule['actions']['moveToFolder'] = 'Archive'
        elif action == 'add_label':
            outlook_rule['actions']['assignCategories'] = [suggestion.get('label', 'Unknown')]
        elif action == 'mark_important':
            outlook_rule['actions']['markAsRead'] = False
            outlook_rule['actions']['markImportance'] = 'high'
        
        return outlook_rule
