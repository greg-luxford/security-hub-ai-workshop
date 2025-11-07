#!/usr/bin/env python3
"""
Security Hub AI Chatbot CLI
A user-friendly command-line interface for the Security Hub AI Remediation solution.
"""

import requests
import json
import sys
import argparse
from datetime import datetime

# Configuration
API_ENDPOINT = "https://cxwxf8coz6.execute-api.ap-southeast-2.amazonaws.com/dev/chat"

def format_response(response_data):
    """Format the JSON response into human-readable text"""
    
    print("\n" + "="*60)
    print("🛡️  SECURITY HUB AI ANALYSIS RESULTS")
    print("="*60)
    
    # Summary
    print(f"\n📊 SUMMARY:")
    print(f"   • Total findings analyzed: {response_data.get('findings_count', 0)}")
    print(f"   • Automatically remediated: {response_data.get('automated_count', 0)}")
    print(f"   • Require manual review: {response_data.get('manual_count', 0)}")
    
    # Main response
    if response_data.get('response'):
        print(f"\n💬 AI RESPONSE:")
        print(f"   {response_data['response']}")
    
    # Detailed remediations
    remediations = response_data.get('remediations', [])
    if remediations:
        print(f"\n🔧 DETAILED REMEDIATION ACTIONS:")
        print("-" * 60)
        
        for i, rem in enumerate(remediations, 1):
            status_icon = "✅" if rem.get('execution', {}).get('status') == 'success' else "⚠️"
            severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🟢"}.get(rem.get('severity', ''), "⚪")
            
            print(f"\n{i}. {status_icon} {rem.get('finding_title', 'Unknown Finding')}")
            print(f"   Severity: {severity_icon} {rem.get('severity', 'Unknown')}")
            
            analysis = rem.get('analysis', {})
            if analysis.get('explanation'):
                print(f"   Issue: {analysis['explanation']}")
            
            if analysis.get('automated'):
                print(f"   Action: 🤖 Automated remediation")
            else:
                print(f"   Action: 👤 Manual review required")
            
            execution = rem.get('execution')
            if execution:
                if execution.get('status') == 'success':
                    print(f"   Result: ✅ {execution.get('message', 'Completed successfully')}")
                elif execution.get('status') == 'error':
                    print(f"   Result: ❌ {execution.get('message', 'Failed')}")
                else:
                    print(f"   Result: ⏳ {execution.get('message', 'Manual action needed')}")
    
    print("\n" + "="*60)
    print(f"⏰ Analysis completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")

def send_query(message):
    """Send query to the API and return response"""
    try:
        payload = {"message": message}
        response = requests.post(
            API_ENDPOINT,
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Error connecting to API: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing response: {e}")
        return None

def interactive_mode():
    """Run in interactive chat mode"""
    print("🛡️  Security Hub AI Chatbot")
    print("Type your security questions in natural language.")
    print("Type 'quit' or 'exit' to stop.\n")
    
    while True:
        try:
            message = input("🔍 Ask me about security findings: ").strip()
            
            if message.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not message:
                continue
            
            print("\n⏳ Analyzing security findings...")
            response = send_query(message)
            
            if response:
                format_response(response)
            else:
                print("❌ Failed to get response. Please try again.")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Unexpected error: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Security Hub AI Chatbot CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 chat-cli.py                                    # Interactive mode
  python3 chat-cli.py "Show me critical findings"       # Single query
  python3 chat-cli.py "Fix SSH security issues"         # Remediation request
        """
    )
    
    parser.add_argument(
        'message', 
        nargs='?', 
        help='Security question in natural language'
    )
    
    parser.add_argument(
        '--endpoint', 
        default=API_ENDPOINT,
        help='API endpoint URL'
    )
    
    args = parser.parse_args()
    
    # Update global endpoint if provided
    global API_ENDPOINT
    API_ENDPOINT = args.endpoint
    
    if args.message:
        # Single query mode
        print("⏳ Analyzing security findings...")
        response = send_query(args.message)
        if response:
            format_response(response)
        else:
            sys.exit(1)
    else:
        # Interactive mode
        interactive_mode()

if __name__ == "__main__":
    main()
