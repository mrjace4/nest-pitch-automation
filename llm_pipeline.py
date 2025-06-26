import requests
import json
from typing import Dict, Optional
import time

class PitchPlanGenerator:
    def __init__(self, openai_api_key: str, anthropic_api_key: str):
        self.openai_api_key = openai_api_key
        self.anthropic_api_key = anthropic_api_key
    
    def openai_chat_completion(self, messages, model="gpt-4", temperature=0.1, max_tokens=2500):
        """Direct OpenAI API call using requests"""
        
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            print(f"OpenAI API Error: {response.status_code} - {response.text}")
            return None

    def anthropic_completion(self, prompt, model="claude-3-5-sonnet-20241022", max_tokens=1500, temperature=0.3):
        """Direct Anthropic API call using requests"""
        
        url = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": prompt}]
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            return response.json()["content"][0]["text"]
        else:
            print(f"Anthropic API Error: {response.status_code} - {response.text}")
            return None

    def generate_pitch_plan(self, client_data: Dict) -> Dict:
        """Complete 3-step pitch plan generation pipeline"""
        print(f"🚀 Starting pitch plan for {client_data.get('client_name', 'Unknown Client')}")
        
        # Step 1: Strategic Analysis (OpenAI via REST API)
        print("📊 Step 1: Strategic Analysis...")
        strategic_foundation = self.strategic_analysis(client_data)
        
        if not strategic_foundation:
            return {"error": "Failed at strategic analysis step"}
        
        # Step 2: Narrative Development (Anthropic via REST API)
        print("📖 Step 2: Narrative Development...")
        narrative = self.narrative_development(strategic_foundation, client_data)
        
        if not narrative:
            return {"error": "Failed at narrative development step"}
        
        # Step 3: Plan Integration (OpenAI via REST API)
        print("📋 Step 3: Plan Integration...")
        final_plan = self.plan_integration(strategic_foundation, narrative, client_data)
        
        if not final_plan:
            return {"error": "Failed at plan integration step"}
        
        print("✅ Pitch plan complete!")
        
        return {
            "client_name": client_data.get('client_name'),
            "strategic_foundation": strategic_foundation,
            "narrative": narrative,
            "final_plan": final_plan,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def strategic_analysis(self, client_data: Dict) -> Optional[str]:
        """Step 1: Strategic Intelligence Synthesis using OpenAI REST API"""
        
        client_info = self.format_client_info(client_data)
        
        prompt = f"""ROLE: Senior Strategy Consultant analyzing B2B agency pitch opportunity

CLIENT INTELLIGENCE:
{client_info}

TASK: Create comprehensive strategic foundation for pitch development with these exact sections:

1. STRATEGIC OBJECTIVES
   - 3-5 SMART goals aligned with client's stated needs
   - Connect their business ambitions to measurable outcomes

2. KEY CHALLENGES  
   - Top 5 prioritized obstacles with impact assessment
   - Focus on gaps between their ambitions and current state

3. CAPABILITY GAPS
   - Creative gaps (brand, messaging, content needs)
   - Media gaps (channel optimization, targeting, measurement)
   - Process gaps (operations, tech, integration needs)
   - For each gap, provide specific solution pathway

4. COMPETITIVE CONTEXT
   - Market positioning opportunities
   - How to differentiate our approach

5. NARRATIVE HOOKS
   - Key story elements for compelling pitch narrative
   - Specific client pain points that create urgency

OUTPUT: Well-structured analysis with clear section headers, client-specific insights."""

        messages = [
            {"role": "system", "content": "You are a senior strategy consultant specializing in B2B agency pitch development."},
            {"role": "user", "content": prompt}
        ]
        
        return self.openai_chat_completion(messages, max_tokens=2500)
    
    def narrative_development(self, strategic_foundation: str, client_data: Dict) -> Optional[str]:
        """Step 2: Narrative Development using Anthropic REST API"""
        
        client_name = client_data.get('client_name', 'the client')
        
        prompt = f"""Transform this strategic analysis into a powerful narrative using SITUATION → FRICTION → SOLUTION framework.

STRATEGIC FOUNDATION:
{strategic_foundation}

CLIENT: {client_name}

Create exactly 3 paragraphs:

SITUATION (Paragraph 1): Acknowledge {client_name}'s current position and ambitious goals
FRICTION (Paragraph 2): Identify the gap between their ambitions and current capabilities  
SOLUTION (Paragraph 3): Position our agency as the partner that delivers the new operating model they need

REQUIREMENTS:
- Use {client_name} specifically throughout
- Reference specific details from the strategic foundation
- Consultative confidence without overselling
- 150-200 words each paragraph"""

        return self.anthropic_completion(prompt, max_tokens=1500, temperature=0.3)
    
    def plan_integration(self, strategic_foundation: str, narrative: str, client_data: Dict) -> Optional[str]:
        """Step 3: Plan Integration using OpenAI REST API"""
        
        client_name = client_data.get('client_name', 'Client')
        
        prompt = f"""Create comprehensive pitch plan integrating strategic analysis with compelling narrative.

STRATEGIC FOUNDATION:
{strategic_foundation}

NARRATIVE:
{narrative}

CLIENT: {client_name}

Create a complete pitch plan with these sections:

1. EXECUTIVE SUMMARY
2. STRATEGIC FOUNDATION  
3. PROPOSED APPROACH
4. CAPABILITY DEMONSTRATION
5. INVESTMENT & NEXT STEPS

REQUIREMENTS:
- Strategic insights woven throughout
- Narrative elements enhance each section
- Client-specific customization
- 2000-3000 words total
- Professional formatting"""

        messages = [
            {"role": "system", "content": "You are a pitch plan specialist who creates execution-ready strategic documents."},
            {"role": "user", "content": prompt}
        ]
        
        return self.openai_chat_completion(messages, max_tokens=4000)
    
    def format_client_info(self, client_data: Dict) -> str:
        """Format client data for LLM consumption"""
        
        return f"""
CLIENT NAME: {client_data.get('client_name', 'Unknown')}
STATUS: {client_data.get('status', 'Unknown')}
CATEGORY: {client_data.get('category', 'Unknown')}
SERVICES NEEDED: {client_data.get('services', 'Unknown')}
ACCOUNT OWNER: {client_data.get('so_owner', 'Unknown')}
SALES OWNER: {client_data.get('sales_owner', 'Unknown')}

AVAILABLE DATA SOURCES:
- Qualification Call: {client_data.get('qualification_call', 'N/A')}
- Discovery Call: {client_data.get('discovery_call', 'N/A')}
- Discovery Notes: {client_data.get('discovery_notes', 'N/A')}
- Pitch Strategy: {client_data.get('pitch_strategy', 'N/A')}
"""
