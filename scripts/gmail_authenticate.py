#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gmail Authentication Helper

Run this script first to authenticate with Gmail API and generate token.json.

Usage:
    python gmail_authenticate.py

Setup Steps:
    1. Go to https://console.cloud.google.com/
    2. Enable Gmail API
    3. Download credentials.json (already done)
    4. Run this script
    5. Follow browser authentication flow
    6. token.json will be created automatically
"""

import os
import pickle
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# Gmail API scope - using full Gmail scope for reading AND sending
SCOPES = ['https://www.googleapis.com/auth/gmail']

def authenticate():
    """Authenticate with Gmail API and save token."""
    creds = None
    token_path = Path('token.json')
    credentials_path = Path('credentials.json')
    
    # Check if credentials file exists
    if not credentials_path.exists():
        print("Error: credentials.json not found!")
        print("\nPlease download Gmail API credentials from Google Cloud Console")
        return False
    
    # Load existing token if available
    if token_path.exists():
        with open(token_path, 'r') as f:
            creds = Credentials.from_authorized_user_file(f, SCOPES)
    
    # Check if we need to authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("Refreshing expired token...")
            try:
                creds.refresh(Request())
                print("✓ Token refreshed successfully!")
            except Exception as e:
                print(f"Token refresh failed: {e}")
                creds = None
        
        if not creds:
            print("Starting Gmail API authentication...")
            print("Opening browser for authentication...")
            print("\nInstructions:")
            print("1. Click 'Allow' when asked for permissions")
            print("2. You'll be redirected to localhost")
            print("3. Token will be saved automatically\n")
            
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_path, SCOPES
            )
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as f:
            pickle.dump(creds, f)
        
        print(f"\n{'✓'*50}")
        print("✓ Authentication successful!")
        print(f"✓ Token saved to: {token_path.absolute()}")
        print("\nYou can now run:")
        print("  python gmail_watcher.py ../AI_Employee_Vault")
        return True
    
    print("✓ Existing token is valid!")
    print(f"✓ Token location: {token_path.absolute()}")
    print("\nToken expires:", creds.expiry if creds.expiry else "Unknown")
    return True


def test_gmail_access():
    """Test Gmail API access."""
    try:
        from googleapiclient.discovery import build
        
        token_path = Path('token.json')
        if not token_path.exists():
            print("No token found. Please run authentication first.")
            return False
        
        with open(token_path, 'r') as f:
            creds = Credentials.from_authorized_user_file(f, SCOPES)
        
        # Refresh if needed
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('gmail', 'v1', credentials=creds)
        
        # Test by getting profile
        profile = service.users().getProfile().execute()
        print(f"\n✓ Gmail API access confirmed!")
        print(f"  Email: {profile['emailAddress']}")
        print(f"  Messages Total: {profile['messagesTotal']}")
        print(f"  Threads Total: {profile['threadsTotal']}")
        return True
        
    except Exception as e:
        print(f"✗ Gmail API test failed: {e}")
        return False


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_gmail_access()
    else:
        if authenticate():
            test_gmail_access()
