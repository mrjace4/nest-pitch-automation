import os
from dotenv import load_dotenv
from slack_bot import create_app

# Load environment variables
load_dotenv()

def main():
    # Validate required environment variables
    required_vars = [
        'SLACK_BOT_TOKEN',
        'SLACK_SIGNING_SECRET', 
        'NOTION_TOKEN',
        'NOTION_DATABASE_ID',
        'OPENAI_API_KEY',
        'ANTHROPIC_API_KEY',
        'GOOGLE_SERVICE_ACCOUNT_FILE'
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {missing_vars}")
        print("Please check your .env file")
        return
    
    print("🚀 Starting Nest Pitch Automation Bot...")
    print("📋 Available commands:")
    print("   /start-pitch ClientName")
    print("   /pitch-help")
    print("🔗 Server ready for Slack events")
    
    # Create and run the Flask app
    app = create_app()
    app.run(host='0.0.0.0', port=3000, debug=False)

if __name__ == "__main__":
    main()
