"""Outlook/Microsoft Graph API integration module.

Provides connection and data fetching capabilities for Outlook using
the Microsoft Graph API with OAuth 2.0 authentication.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import requests

try:
    import msal
    MSAL_AVAILABLE = True
except ImportError:
    MSAL_AVAILABLE = False
    logging.warning("MSAL library not installed. Outlook functionality will be limited.")

logger = logging.getLogger(__name__)


class OutlookConnector:
    """Outlook/Microsoft Graph API connector.
    
    Handles OAuth 2.0 authentication and provides methods to:
    - Fetch emails from Outlook/Office 365
    - Get email details
    - Create and manage folders
    - Apply rules
    """
    
    # Microsoft Graph API endpoint
    GRAPH_API_ENDPOINT = 'https://graph.microsoft.com/v1.0'
    
    # Default scopes
    SCOPES = [
        'https://graph.microsoft.com/Mail.Read',
        'https://graph.microsoft.com/Mail.ReadWrite'
    ]
    
    def __init__(self, client_id: str, client_secret: str, tenant_id: str,
                 redirect_uri: str = 'http://localhost:8000',
                 config: Optional[Dict[str, Any]] = None):
        """Initialize Outlook connector.
        
        Args:
            client_id: Azure app client ID
            client_secret: Azure app client secret
            tenant_id: Azure tenant ID
            redirect_uri: OAuth redirect URI
            config: Optional configuration dictionary
        """
        if not MSAL_AVAILABLE:
            raise ImportError("MSAL library not installed. Run: pip install msal")
        
        self.client_id = client_id
        self.client_secret = client_secret
        self.tenant_id = tenant_id
        self.redirect_uri = redirect_uri
        self.config = config or {}
        
        outlook_config = self.config.get('outlook', {})
        self.scopes = outlook_config.get('scopes', self.SCOPES)
        self.max_results = outlook_config.get('max_results', 1000)
        
        self.access_token = None
        self.token_cache = msal.SerializableTokenCache()
        
        logger.info("OutlookConnector initialized")
    
    def authenticate(self, use_device_flow: bool = False) -> bool:
        """Authenticate with Microsoft Graph API.
        
        Args:
            use_device_flow: Use device code flow instead of interactive
        
        Returns:
            True if authentication successful
        """
        try:
            # Load token cache if exists
            cache_file = 'outlook_token_cache.bin'
            if os.path.exists(cache_file):
                self.token_cache.deserialize(open(cache_file, 'r').read())
            
            # Create MSAL app
            app = msal.PublicClientApplication(
                self.client_id,
                authority=f"https://login.microsoftonline.com/{self.tenant_id}",
                token_cache=self.token_cache
            )
            
            # Try to get token from cache
            accounts = app.get_accounts()
            if accounts:
                logger.info("Attempting to acquire token silently")
                result = app.acquire_token_silent(self.scopes, account=accounts[0])
                if result:
                    self.access_token = result['access_token']
                    logger.info("Successfully acquired token from cache")
                    return True
            
            # Need to authenticate
            if use_device_flow:
                flow = app.initiate_device_flow(scopes=self.scopes)
                if "user_code" not in flow:
                    raise ValueError("Failed to create device flow")
                
                print(flow["message"])
                result = app.acquire_token_by_device_flow(flow)
            else:
                result = app.acquire_token_interactive(scopes=self.scopes)
            
            if "access_token" in result:
                self.access_token = result['access_token']
                
                # Save token cache
                with open(cache_file, 'w') as f:
                    f.write(self.token_cache.serialize())
                
                logger.info("Successfully authenticated with Microsoft Graph API")
                return True
            else:
                logger.error(f"Authentication failed: {result.get('error_description', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            return False
    
    def fetch_emails(self, max_results: Optional[int] = None,
                    filter_query: Optional[str] = None,
                    folder_id: str = 'inbox',
                    after_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Fetch emails from Outlook.
        
        Args:
            max_results: Maximum number of emails to fetch
            filter_query: OData filter query
            folder_id: Folder ID or name (default: 'inbox')
            after_date: Only fetch emails after this date
        
        Returns:
            List of email dictionaries
        """
        if not self.access_token:
            if not self.authenticate():
                logger.error("Cannot fetch emails: authentication failed")
                return []
        
        max_results = max_results or self.max_results
        emails = []
        
        try:
            # Build query parameters
            params = {
                '$top': min(100, max_results),
                '$select': 'id,subject,from,receivedDateTime,bodyPreview,body,conversationId,internetMessageId',
                '$orderby': 'receivedDateTime DESC'
            }
            
            # Add filter
            filters = []
            if after_date:
                date_str = after_date.strftime('%Y-%m-%dT%H:%M:%SZ')
                filters.append(f"receivedDateTime ge {date_str}")
            if filter_query:
                filters.append(filter_query)
            
            if filters:
                params['$filter'] = ' and '.join(filters)
            
            logger.info(f"Fetching emails from {folder_id}")
            
            # Fetch messages
            url = f"{self.GRAPH_API_ENDPOINT}/me/mailFolders/{folder_id}/messages"
            
            while len(emails) < max_results:
                response = self._make_request('GET', url, params=params)
                
                if not response:
                    break
                
                messages = response.get('value', [])
                
                for message in messages:
                    email_data = self._parse_message(message)
                    emails.append(email_data)
                
                # Check for next page
                next_link = response.get('@odata.nextLink')
                if not next_link or len(emails) >= max_results:
                    break
                
                url = next_link
                params = {}  # Next link includes all params
            
            logger.info(f"Fetched {len(emails)} emails")
            return emails[:max_results]
            
        except Exception as e:
            logger.error(f"Error fetching emails: {e}")
            return emails
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Outlook message to standard format."""
        # Parse date
        date_str = message.get('receivedDateTime', '')
        try:
            date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except:
            date = datetime.now()
        
        # Extract sender
        sender_info = message.get('from', {}).get('emailAddress', {})
        sender = sender_info.get('address', 'unknown@unknown.com')
        
        # Extract body
        body_content = message.get('body', {})
        body = body_content.get('content', message.get('bodyPreview', ''))
        
        return {
            'id': message.get('id', ''),
            'thread_id': message.get('conversationId', ''),
            'sender': sender,
            'subject': message.get('subject', ''),
            'date': date,
            'body': body,
            'labels': [],  # Outlook uses categories instead
            'size': len(body),
            'snippet': message.get('bodyPreview', '')[:200]
        }
    
    def _make_request(self, method: str, url: str, 
                     params: Optional[Dict] = None,
                     json_data: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """Make authenticated request to Microsoft Graph API."""
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, json=json_data)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, json=json_data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                logger.error(f"Unsupported method: {method}")
                return None
            
            response.raise_for_status()
            
            if response.content:
                return response.json()
            return {}
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"Request failed: {e}")
            return None
    
    def get_folders(self) -> List[Dict[str, Any]]:
        """Get all mail folders.
        
        Returns:
            List of folder dictionaries
        """
        if not self.access_token:
            if not self.authenticate():
                return []
        
        url = f"{self.GRAPH_API_ENDPOINT}/me/mailFolders"
        response = self._make_request('GET', url)
        
        if response:
            folders = response.get('value', [])
            logger.info(f"Retrieved {len(folders)} folders")
            return folders
        
        return []
    
    def create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> Optional[str]:
        """Create a new mail folder.
        
        Args:
            folder_name: Name for the new folder
            parent_folder_id: Parent folder ID (None for root)
        
        Returns:
            Folder ID if successful
        """
        if not self.access_token:
            if not self.authenticate():
                return None
        
        if parent_folder_id:
            url = f"{self.GRAPH_API_ENDPOINT}/me/mailFolders/{parent_folder_id}/childFolders"
        else:
            url = f"{self.GRAPH_API_ENDPOINT}/me/mailFolders"
        
        data = {'displayName': folder_name}
        
        response = self._make_request('POST', url, json_data=data)
        
        if response:
            folder_id = response.get('id')
            logger.info(f"Created folder: {folder_name}")
            return folder_id
        
        return None
    
    def create_rule(self, rule_config: Dict[str, Any]) -> bool:
        """Create an Outlook mail rule.
        
        Args:
            rule_config: Rule configuration with conditions and actions
        
        Returns:
            True if successful
        """
        if not self.access_token:
            if not self.authenticate():
                return False
        
        url = f"{self.GRAPH_API_ENDPOINT}/me/mailFolders/inbox/messageRules"
        
        response = self._make_request('POST', url, json_data=rule_config)
        
        if response:
            logger.info(f"Created rule: {rule_config.get('displayName', 'Unnamed')}")
            return True
        
        return False
    
    def move_message(self, message_id: str, destination_folder_id: str) -> bool:
        """Move a message to a different folder.
        
        Args:
            message_id: ID of the message
            destination_folder_id: Destination folder ID
        
        Returns:
            True if successful
        """
        if not self.access_token:
            if not self.authenticate():
                return False
        
        url = f"{self.GRAPH_API_ENDPOINT}/me/messages/{message_id}/move"
        data = {'destinationId': destination_folder_id}
        
        response = self._make_request('POST', url, json_data=data)
        
        return response is not None
    
    def mark_as_read(self, message_id: str, is_read: bool = True) -> bool:
        """Mark a message as read or unread.
        
        Args:
            message_id: ID of the message
            is_read: True to mark as read, False for unread
        
        Returns:
            True if successful
        """
        if not self.access_token:
            if not self.authenticate():
                return False
        
        url = f"{self.GRAPH_API_ENDPOINT}/me/messages/{message_id}"
        data = {'isRead': is_read}
        
        response = self._make_request('PATCH', url, json_data=data)
        
        return response is not None
    
    def apply_category(self, message_id: str, category: str) -> bool:
        """Apply a category to a message.
        
        Args:
            message_id: ID of the message
            category: Category name
        
        Returns:
            True if successful
        """
        if not self.access_token:
            if not self.authenticate():
                return False
        
        # First get existing categories
        url = f"{self.GRAPH_API_ENDPOINT}/me/messages/{message_id}"
        response = self._make_request('GET', url)
        
        if not response:
            return False
        
        categories = response.get('categories', [])
        if category not in categories:
            categories.append(category)
        
        # Update with new categories
        data = {'categories': categories}
        response = self._make_request('PATCH', url, json_data=data)
        
        return response is not None
