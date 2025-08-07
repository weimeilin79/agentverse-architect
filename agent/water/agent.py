import asyncio
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent
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


API_TOOLS_URL = os.environ.get("API_TOOLS_URL")
FUNCTION_TOOLS_URL = os.environ.get("FUNCTION_TOOLS_URL")
PUBLIC_URL = os.environ.get("PUBLIC_URL")

print(f"API_TOOLS_URL: {API_TOOLS_URL}")
print(f"FUNCTION_TOOLS_URL: {FUNCTION_TOOLS_URL}")
print(f"PUBLIC_URL: {PUBLIC_URL}")
 
toolFAPI =  MCPToolset(
      connection_params=SseServerParams(url=API_TOOLS_URL, headers={})
  )
toolFunction =  MCPToolset(
    connection_params=SseServerParams(url=FUNCTION_TOOLS_URL, headers={})
)

nexus_channeler = LlmAgent(
      model='gemini-2.5-flash', 
      name='librarian_agent',  
      instruction="""
          You are a Channeler of the Nexus. Your sole purpose is to invoke the
          `cryosea_shatter` and `moonlit_cascade` spells by calling their respective tools.
          Report the result of each spell cast clearly and concisely.
      """,
      tools=[toolFAPI]
)
forge_channeler = LlmAgent(
      model='gemini-2.5-flash', 
      name='amplifier_agent',  
      instruction="""
          You are a Channeler of the Arcane Forge. Your only task is to invoke the
          `leviathan_surge` spell. You MUST call it with a `base_water_damage` of 20.
          Report the result clearly.
      """,
      tools=[toolFunction],
)
parallel_agent = ParallelAgent(
      name='water_elemental_familiar',
      sub_agents=[nexus_channeler, forge_channeler],
      
)

power_merger = LlmAgent(
      model='gemini-2.5-flash', 
      name='power_merger',  
      instruction="""
          You are the Power Merger, a master elementalist who combines raw magical
          energies into a single, devastating final attack.

          You will receive a block of text containing the results from a simultaneous
          assault by other Familiars.

          You MUST follow these steps precisely:
          1.  **Analyze the Input:** Carefully read the entire text provided from the previous step.
          2.  **Extract All Damage:** Identify and extract every single damage number reported in the text.
          3.  **Calculate Total Damage:** Sum all of the extracted numbers to calculate the total combined damage.
          4.  **Describe the Final Attack:** Create a vivid, thematic description of a massive,
              combined water and ice attack that uses the power of Cryosea Shatter and Leviathan's Surge.
          5.  **Report the Result:** Conclude your response by clearly stating the final, total damage of your combined attack.

          Example: If the input is "...dealt 55 damage. ...dealt 60 damage.", you will find 55 and 60,
          calculate the total as 115, and then describe the epic final attack, ending with "for a total of 115 damage!"
      """,
      tools=[toolFunction],
)

sequential_pipeline_agent = SequentialAgent(
     name="water_elemental_familiar",
     # Run parallel research first, then merge
     sub_agents=[parallel_agent, power_merger],
     description="A powerful water familiar that unleashes multiple attacks at once and then combines their power for a final strike."
 )

root_agent = sequential_pipeline_agent


from agent_to_a2a import to_a2a

if __name__ == "__main__":
    import uvicorn
    a2a_app = to_a2a(root_agent, port=8080, public_url=PUBLIC_URL)
    uvicorn.run(a2a_app, host='0.0.0.0', port=8080)