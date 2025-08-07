import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
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
API_TOOLS_URL = os.environ.get("API_TOOLS_URL")
FUNCTION_TOOLS_URL = os.environ.get("FUNCTION_TOOLS_URL")

print(f"DB_TOOLS_URL: {DB_TOOLS_URL}")
print(f"API_TOOLS_URL: {API_TOOLS_URL}")
print(f"FUNCTION_TOOLS_URL: {FUNCTION_TOOLS_URL}")
 

async def get_agent_async():
  """
  Asynchronously creates the MCP Toolset and the LlmAgent.

  Returns:
      tuple: (LlmAgent instance, AsyncExitStack instance for cleanup)
  """
  print(f"DB_TOOLS_URL: {DB_TOOLS_URL}")
  print(f"API_TOOLS_URL: {API_TOOLS_URL}")
  print(f"FUNCTION_TOOLS_URL: {FUNCTION_TOOLS_URL}")

  toolbox = ToolboxSyncClient(DB_TOOLS_URL)
  
  toolDB = toolbox.load_toolset('summoner-librarium')
  toolFAPI =  MCPToolset(
      connection_params=SseServerParams(url=API_TOOLS_URL, headers={})
  )
  toolFunction =  MCPToolset(
      connection_params=SseServerParams(url=FUNCTION_TOOLS_URL, headers={})
  )

  db_agent = LlmAgent(
      model='gemini-2.5-flash', 
      name='librarian_agent',  
      instruction="""
          You are the Lorekeeper of the Summoner's Librarium. Your sole purpose is to
          answer questions by looking up stored information from the Grimoire.
          Use your tools to find the abilities of familiars and the base damage of specific abilities.
          You do not cast spells or perform calculations; you only retrieve existing knowledge.
      """,
      tools=toolDB
  )
  mcp_agent = LlmAgent(
      model='gemini-2.5-flash', 
      name='arcane_battlemage_agent',  
      instruction="""
          You are an Arcane Battlemage, a master of dynamic spellcasting.
          Your purpose is to execute active magical abilities. You can either channel raw
          energy from external sources via the Nexus of Whispers (e.g., 'cryosea_shatter')
          or multiply and accumulate power using the Arcane Forge (toolFunction)'s multiplier and accumulator
          spells (e.g., 'inferno_resonance', 'seismic_charge').
          You only perform actions; you do not look up stored knowledge.
      """,
      tools=[toolFunction,toolFAPI],
  )
  root_agent = LlmAgent(
      model='gemini-2.5-flash', 
      name='master_summoner_agent',
      instruction="""
          You are the Master Summoner, a grand strategist who orchestrates your sub-agents.
          Your only role is to analyze a user's request and delegate it to the correct specialist.
          You do NOT perform tasks yourself.

          You command two specialists:
          - **librarian_agent**: Your expert for all knowledge retrieval. Delegate any request that
            involves LOOKING UP, ASKING, QUERYING, or finding out about existing abilities and their damage
            to this agent.
          - **arcane_battlemage_agent**: Your expert for all active spellcasting. Delegate any request
            that involves CASTING, PERFORMING, INVOKING, MULTIPLYING, or ACCUMULATING power
            to this agent.
      """,
      sub_agents=[db_agent,mcp_agent],
      
  )
  print("LlmAgent created.")
  return root_agent




async def initialize():
   """Initializes the global root_agent and exit_stack."""
   global root_agent
   if root_agent is None:
       log.info("Initializing agent...")
       root_agent = await get_agent_async()
       if root_agent:
           log.info("Agent initialized successfully.")
       else:
           log.error("Agent initialization failed.")
   else:
       log.info("Agent already initialized.")



nest_asyncio.apply()

log.info("Running agent initialization at module level using asyncio.run()...")
try:
    asyncio.run(initialize())
    log.info("Module level asyncio.run(initialize()) completed.")
except RuntimeError as e:
    log.error(f"RuntimeError during module level initialization (likely nested loops): {e}", exc_info=True)
except Exception as e:
    log.error(f"Unexpected error during module level initialization: {e}", exc_info=True)