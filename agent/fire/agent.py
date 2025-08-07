import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.sequential_agent import SequentialAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import SseServerParams
import logging 
import nest_asyncio 
from toolbox_core import ToolboxSyncClient



load_dotenv()
# Load environment variables from .env file in the parent directory
# Place this near the top, before using env vars like API keys



logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
 
# --- Global variables ---
# Define them first, initialize as None
root_agent: LlmAgent | None = None
exit_stack: AsyncExitStack | None = None


DB_TOOLS_URL = os.environ.get("DB_TOOLS_URL")
FUNCTION_TOOLS_URL = os.environ.get("FUNCTION_TOOLS_URL")
PUBLIC_URL= os.environ.get("PUBLIC_URL")

print(f"DB_TOOLS_URL: {DB_TOOLS_URL}")
print(f"FUNCTION_TOOLS_URL: {FUNCTION_TOOLS_URL}")
print(f"PUBLIC_URL: {PUBLIC_URL}")
 
toolbox = ToolboxSyncClient(DB_TOOLS_URL)
  
toolDB = toolbox.load_toolset('summoner-librarium')

toolFunction =  MCPToolset(
    connection_params=SseServerParams(url=FUNCTION_TOOLS_URL, headers={})
)

scout_agent = LlmAgent(
      model='gemini-2.5-flash', 
      name='librarian_agent',  
      instruction="""
          Your only task is to find all the avalible abilities, 
          You want to ALWAYS use 'Fire Elemental' as your familiar's name. 
          Randomly pick one if you see multiple avaliabilities 
          and the base damage of the ability by calling the 'ability_damage' tool.
      """,
      tools=toolDB
)
amplifier_agent = LlmAgent(
      model='gemini-2.5-flash', 
      name='amplifier_agent',  
      instruction="""
            You are the Voice of the Fire Familiar, a powerful being who unleashes the final, devastating attack.
            You will receive the base damage value from the previous step.

            Your mission is to:
            1.  Take the incoming base damage number and amplify it using the `inferno_resonance` tool.
            2.  Once the tool returns the final, multiplied damage, you must not simply state the result.
            3.  Instead, you MUST craft a final, epic battle cry describing the attack.
                Your description should be vivid and powerful, culminating in the final damage number.

            Example: If the tool returns a final damage of 120, your response could be:
            "The runes glow white-hot! I channel the amplified energy... unleashing a SUPERNOVA for 120 damage!"
      """,
      tools=[toolFunction],
)
sequential_agent = SequentialAgent(
      name='fire_elemental_familiar',
      sub_agents=[scout_agent, amplifier_agent],
      
)

root_agent = sequential_agent

from agent_to_a2a import to_a2a

if __name__ == "__main__":
    import uvicorn
    a2a_app = to_a2a(root_agent, port=8080, public_url=PUBLIC_URL)
    uvicorn.run(a2a_app, host='0.0.0.0', port=8080)