import os
import threading
from flask import Flask, request
from slack_bolt import App
from slack_bolt.adapter.flask import SlackRequestHandler

# Import our components
from notion_extractor import NotionPitchExtractor
from llm_pipeline import PitchPlanGenerator
from google_docs_formatter import GoogleDocsFormatter

class SlackPitchBot:
    def __init__(self):
        # Load configuration from environment
        self.slack_bot_token = os.getenv('SLACK_BOT_TOKEN')
        self.slack_signing_secret = os.getenv('SLACK_SIGNING_SECRET')
        self.notion_token = os.getenv('NOTION_TOKEN')
        self.notion_database_id = os.getenv('NOTION_DATABASE_ID')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        self.google_service_account_file = os.getenv('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        # Parse team emails
        team_emails_str = os.getenv('TEAM_EMAILS', '')
        self.team_emails = [email.strip() for email in team_emails_str.split(',') if email.strip()]
        
        # Initialize Slack app
        self.app = App(
            token=self.slack_bot_token,
            signing_secret=self.slack_signing_secret
        )
        
        # Initialize components
        self.notion_extractor = NotionPitchExtractor(self.notion_token)
        self.llm_generator = PitchPlanGenerator(self.openai_api_key, self.anthropic_api_key)
        self.docs_formatter = GoogleDocsFormatter(self.google_service_account_file)
        
        # Setup command handlers
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup Slack command handlers"""
        
        @self.app.command("/start-pitch")
        def handle_start_pitch(ack, respond, command, client):
            ack()
            client_name = command['text'].strip()
            channel_id = command['channel_id']
            user_id = command['user_id']
            
            if not client_name:
                respond({
                    "text": "❌ Please specify a client name: `/start-pitch ClientName`",
                    "response_type": "ephemeral"
                })
                return
            
            # Send immediate response
            respond({
                "text": f"🚀 Starting pitch plan for **{client_name}**...\n⏱️ This will take 5-10 minutes. I'll update you as I progress.",
                "response_type": "in_channel"
            })
            
            # Start background processing
            thread = threading.Thread(
                target=self.process_pitch_plan,
                args=(client_name, channel_id, user_id, client)
            )
            thread.daemon = True
            thread.start()
        
        @self.app.command("/pitch-help")
        def handle_pitch_help(ack, respond, command):
            ack()
            help_text = (
                "🤖 **Nest Pitch Plan Automation**\n"
                "**Available Commands:**\n"
                "- `/start-pitch ClientName` - Generate complete pitch plan\n"
                "- `/pitch-help` - Show this help message\n\n"
                "**How it works:**\n"
                "1. I extract client data from Notion\n"
                "2. I generate strategic analysis using AI\n"
                "3. I create compelling narrative \n"
                "4. I produce final formatted Google Doc\n"
                "5. I share with the team automatically\n\n"
                "**What I need:**\n"
                "- Client must exist in Notion database\n"
                "- Takes 5-10 minutes to complete\n"
                "- Results shared automatically with sales team"
            )
            respond({"text": help_text, "response_type": "ephemeral"})

    def process_pitch_plan(self, client_name: str, channel_id: str, user_id: str, client):
        try:
            # Steps 1-4 with chat_postMessage and error handling (unchanged)
            client.chat_postMessage(channel=channel_id, text=f"📊 **Step 1/4:** Extracting client data for {client_name} from Notion...")
            client_data = self.notion_extractor.extract_client_data(self.notion_database_id, client_name)
            if 'error' in client_data:
                client.chat_postMessage(channel=channel_id, text=f"❌ **Client not found:** Could not find '{client_name}' in Notion.")
                return

            client.chat_postMessage(channel=channel_id, text="🧠 **Step 2/4:** Generating strategic analysis and narrative...")
            pitch_plan_data = self.llm_generator.generate_pitch_plan(client_data)
            if 'error' in pitch_plan_data:
                client.chat_postMessage(channel=channel_id, text=f"❌ **Generation failed:** {pitch_plan_data['error']}")
                return

            client.chat_postMessage(channel=channel_id, text="📄 **Step 3/4:** Creating formatted Google Doc...")
            document_url = self.docs_formatter.create_pitch_plan_document(pitch_plan_data, self.team_emails)
            if not document_url:
                client.chat_postMessage(channel=channel_id, text="❌ **Document creation failed**")
                return

            success_message = (
                f"✅ **Pitch Plan Complete - {client_name}**\n\n"
                f"🎯 Strategic pitch plan ready for team review\n"
                f"📄 **Document:** {document_url}\n"
                f"📧 **Shared with:** {', '.join(self.team_emails)}\n"
                f"⏱️ **Generated:** {pitch_plan_data.get('generated_at', 'Now')}"
            )
            client.chat_postMessage(channel=channel_id, text=success_message)
        except Exception as e:
            client.chat_postMessage(channel=channel_id, text=f"❌ **System Error:** {str(e)}")

# Flask app for Slack events and commands
flask_app = Flask(__name__)
slack_bot = SlackPitchBot()
handler = SlackRequestHandler(slack_bot.app)

# Route for Slack events and slash commands
@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)

@flask_app.route("/slack/commands", methods=["POST"])
def slack_commands():
    return handler.handle(request)

@flask_app.route("/health", methods=["GET"])
def health_check():
    return {"status": "healthy", "service": "nest-pitch-automation"}

if __name__ == "__main__":
    # Bind to PORT for Railway compatibility
    port = int(os.environ.get("PORT", 3000))
    flask_app.run(host="0.0.0.0", port=port)
