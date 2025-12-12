#!/usr/bin/env python3
"""Category customization example.

This script demonstrates how to:
1. Add custom email categories
2. Test categorization on sample emails
3. Analyze with custom categories
"""

import sys
import yaml
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.categorizer import Categorizer
from src.email_analyzer import EmailAnalyzer
from src.gmail_connector import GmailConnector

def main():
    print("\n" + "="*60)
    print("  EMAIL PATTERN ANALYZER - Category Customization")
    print("="*60 + "\n")
    
    # Load configuration
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Create categorizer
    categorizer = Categorizer(config)
    
    print("🏷️  Adding custom categories...\n")
    
    # Add custom categories
    custom_categories = [
        {
            'name': 'VIP',
            'keywords': ['urgent', 'important', 'critical', 'asap', 'priority'],
            'senders': ['ceo@company.com', 'boss@company.com'],
            'priority': 'high'
        },
        {
            'name': 'Project Updates',
            'keywords': ['project update', 'sprint', 'milestone', 'deliverable', 'roadmap'],
            'senders': [],
            'priority': 'high'
        },
        {
            'name': 'Team Communications',
            'keywords': ['team meeting', 'standup', 'team sync', 'all hands'],
            'senders': ['team@company.com'],
            'priority': 'medium'
        },
        {
            'name': 'Learning & Development',
            'keywords': ['webinar', 'training', 'course', 'tutorial', 'workshop'],
            'senders': [],
            'priority': 'low'
        },
        {
            'name': 'Invoices',
            'keywords': ['invoice', 'payment due', 'billing', 'receipt'],
            'senders': ['billing@', 'invoices@'],
            'priority': 'high'
        }
    ]
    
    for category in custom_categories:
        categorizer.add_custom_category(**category)
        print(f"  ✅ Added: {category['name']} (Priority: {category['priority']})")
    
    # Test categorization with sample emails
    print("\n\n🧪 Testing with sample emails...\n")
    
    sample_emails = [
        {
            'sender': 'ceo@company.com',
            'subject': 'URGENT: Board meeting tomorrow',
            'body': 'We need to discuss the quarterly results ASAP.',
            'date': '2024-12-12'
        },
        {
            'sender': 'team@company.com',
            'subject': 'Daily Standup Notes',
            'body': 'Here are today\'s team standup notes...',
            'date': '2024-12-12'
        },
        {
            'sender': 'newsletter@marketing.com',
            'subject': '50% OFF - Limited Time Offer!',
            'body': 'Shop now and save big! Unsubscribe link...',
            'date': '2024-12-12'
        },
        {
            'sender': 'friend@email.com',
            'subject': 'Catch up this weekend?',
            'body': 'Hey! Want to grab coffee this weekend?',
            'date': '2024-12-12'
        },
        {
            'sender': 'notifications@github.com',
            'subject': '[GitHub] New issue in your repository',
            'body': 'A new issue has been created...',
            'date': '2024-12-12'
        },
        {
            'sender': 'training@company.com',
            'subject': 'New Python Course Available',
            'body': 'Check out our latest Python training course...',
            'date': '2024-12-12'
        },
        {
            'sender': 'billing@service.com',
            'subject': 'Invoice #12345 - Payment Due',
            'body': 'Your invoice for December is attached.',
            'date': '2024-12-12'
        }
    ]
    
    for email in sample_emails:
        category = categorizer.categorize(email)
        print(f"📧 From: {email['sender']:30} | Subject: {email['subject'][:40]}")
        print(f"   ➡️  Category: {category}")
        print()
    
    # Analyze real emails with custom categories
    print("\n\n🔍 Analyzing your emails with custom categories...\n")
    
    if config.get('gmail', {}).get('enabled'):
        connector = GmailConnector(config=config)
        
        if connector.authenticate():
            emails = connector.fetch_emails(max_results=200)
            
            if emails:
                # Count categories
                category_counts = {}
                for email in emails:
                    category = categorizer.categorize(email)
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                # Display results
                print("📊 Category Distribution:\n")
                total = len(emails)
                
                for category, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    bar = '█' * int(percentage / 2)
                    print(f"  {category:25} {bar} {percentage:5.1f}% ({count:,})")
                
                # Find VIP emails
                if 'VIP' in category_counts:
                    print(f"\n\n🌟 Found {category_counts['VIP']} VIP emails:")
                    print("-" * 60)
                    vip_count = 0
                    for email in emails:
                        if categorizer.categorize(email) == 'VIP':
                            vip_count += 1
                            if vip_count <= 5:  # Show first 5
                                print(f"  • From: {email['sender']}")
                                print(f"    Subject: {email['subject'][:50]}")
                                print()
            else:
                print("❌ No emails found.")
        else:
            print("❌ Authentication failed.")
    else:
        print("⚠️  Gmail not enabled in config. Skipping real email analysis.")
    
    # Save custom configuration
    print("\n\n💾 Saving custom categories to config...")
    
    if 'categorization' not in config:
        config['categorization'] = {}
    
    config['categorization']['custom_categories'] = custom_categories
    
    with open('config_custom.yaml', 'w') as f:
        yaml.dump(config, f, default_flow_style=False)
    
    print("✅ Saved to config_custom.yaml")
    
    print("\n" + "="*60)
    print("  CUSTOMIZATION COMPLETE!")
    print("="*60)
    print("\nYour custom categories are now active. To use them permanently:")
    print("  1. Review config_custom.yaml")
    print("  2. Copy custom_categories section to your config.yaml")
    print("  3. Run basic_analysis.py again to see the custom categories in action")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
