#!/usr/bin/env python3
"""
YouTube Music Authentication Setup
Provides multiple authentication methods for YouTube Music API access
"""

import os
import sys
from pathlib import Path

try:
    from ytmusicapi import setup, setup_oauth
    from ytmusicapi import YTMusic
except ImportError:
    print("❌ ytmusicapi not installed. Run: pip install ytmusicapi")
    sys.exit(1)

def test_authentication(auth_file: str) -> bool:
    """Test if authentication works by trying to access YouTube Music."""
    try:
        if 'oauth' in auth_file:
            # For OAuth, we need to test differently since we don't have client credentials here
            # This is a basic file existence and format check
            if os.path.exists(auth_file):
                with open(auth_file, 'r') as f:
                    import json
                    auth_data = json.load(f)
                    if 'token' in auth_data or 'access_token' in auth_data:
                        print(f"✅ OAuth authentication file {auth_file} appears valid")
                        print("💡 Full authentication test requires client credentials in your app")
                        return True
            print(f"❌ OAuth authentication file {auth_file} appears invalid")
            return False
        else:
            # For headers auth, test directly
            ytmusic = YTMusic(auth_file)
            # Try a simple operation to test auth
            ytmusic.get_home()
            print(f"✅ Authentication test successful with {auth_file}")
            return True
    except Exception as e:
        print(f"❌ Authentication test failed: {e}")
        return False

def setup_browser_auth():
    """Set up browser-based authentication."""
    print("🌐 Browser Headers Authentication Setup")
    print("=" * 50)
    print()
    print("📋 Instructions:")
    print("1. Open YouTube Music in your browser: https://music.youtube.com")
    print("2. Make sure you're logged in to your Google account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to the Network tab")
    print("5. Refresh the page (F5)")
    print("6. Look for a request to 'music.youtube.com' (usually the first one)")
    print("7. Right-click on it → Copy → Copy as cURL")
    print("8. Or copy the request headers manually")
    print()
    print("⚠️ You need these specific headers:")
    print("   - cookie (contains authentication)")
    print("   - x-goog-authuser")
    print("   - user-agent")
    print()
    
    try:
        setup('headers_auth.json')
        print("✅ Headers saved to headers_auth.json")
        
        # Test the authentication
        if test_authentication('headers_auth.json'):
            print("🎉 Browser authentication setup complete!")
            return True
        else:
            print("❌ Authentication test failed. Please try again.")
            return False
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

def setup_oauth_auth():
    """Set up OAuth-based authentication."""
    print("🔐 OAuth Authentication Setup")
    print("=" * 50)
    print()
    print("📋 Instructions:")
    print("1. Go to Google Cloud Console: https://console.cloud.google.com/apis/credentials")
    print("2. Create a new project or select an existing one")
    print("3. Enable the YouTube Data API v3")
    print("4. Create OAuth 2.0 credentials:")
    print("   - Click 'Create Credentials' → 'OAuth client ID'")
    print("   - Select 'TVs and Limited Input devices' as application type")
    print("   - Give it a name (e.g., 'YouTube Music API')")
    print("5. Note down your Client ID and Client Secret")
    print()
    print("⚠️ IMPORTANT: As of November 2024, YouTube Music requires both")
    print("   Client ID and Client Secret for API access!")
    print()
    print("� Full documentation: https://ytmusicapi.readthedocs.io/en/latest/setup/oauth.html")
    print("📖 Google credentials guide: https://developers.google.com/youtube/registering_an_application")
    print()
    
    confirm = input("Have you created OAuth credentials? Continue with setup? (y/n): ").strip().lower()
    if confirm not in ['y', 'yes']:
        return False
    
    try:
        print("\n� Running ytmusicapi OAuth setup...")
        print("This will open a browser window for authentication.")
        print("Follow the on-screen instructions to complete OAuth flow.")
        print()
        
        # Get client credentials from user
        print("📝 Enter your OAuth credentials from Google Cloud Console:")
        client_id = input("Client ID: ").strip()
        client_secret = input("Client Secret: ").strip()
        
        if not client_id or not client_secret:
            print("❌ Both Client ID and Client Secret are required!")
            return False
        
        # Use the ytmusicapi command line OAuth setup with credentials
        setup_oauth(client_id=client_id, client_secret=client_secret, filepath='oauth_auth.json')
        
        print("✅ OAuth setup completed! File saved as oauth_auth.json")
        
        # Test the authentication
        if test_authentication('oauth_auth.json'):
            print("🎉 OAuth authentication setup complete!")
            return True
        else:
            print("❌ Authentication test failed. Please verify your credentials.")
            return False
    except Exception as e:
        print(f"❌ OAuth setup failed: {e}")
        print("💡 Make sure you have valid OAuth credentials from Google Cloud Console")
        print("💡 Follow the setup guide: https://ytmusicapi.readthedocs.io/en/latest/setup/oauth.html")
        return False

def main():
    """Main authentication setup menu."""
    print("🎵 YouTube Music Authentication Setup")
    print("=" * 50)
    print()
    
    # Check existing auth files
    if os.path.exists('headers_auth.json'):
        print("📁 Found existing headers_auth.json")
        if test_authentication('headers_auth.json'):
            print("✅ Existing browser authentication is working!")
            return
        else:
            print("⚠️ Existing browser authentication is not working")
    
    if os.path.exists('oauth_auth.json'):
        print("📁 Found existing oauth_auth.json")
        if test_authentication('oauth_auth.json'):
            print("✅ Existing OAuth authentication is working!")
            return
        else:
            print("⚠️ Existing OAuth authentication is not working")
    
    print()
    print("Choose authentication method:")
    print("1. Browser Headers (copy headers from browser - quick setup)")
    print("2. OAuth (more reliable - requires Google Cloud Console setup)")
    print("3. Exit")
    print()
    print("💡 Recommendation:")
    print("   - For testing: Use Browser Headers (option 1)")
    print("   - For production: Use OAuth (option 2)")
    print()
    print("📖 Updated OAuth guide: https://ytmusicapi.readthedocs.io/en/latest/setup/oauth.html")
    print("🔗 Google Cloud Console: https://console.cloud.google.com/apis/credentials")
    
    while True:
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            if setup_browser_auth():
                break
        elif choice == '2':
            if setup_oauth_auth():
                break
        elif choice == '3':
            print("👋 Setup cancelled")
            break
        else:
            print("❌ Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
