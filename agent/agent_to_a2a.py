from __future__ import annotations

import logging
import sys


from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore


from starlette.applications import Starlette

from google.adk.agents.base_agent import BaseAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.cli.utils.logs import setup_adk_logger
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.adk.a2a.executor.a2a_agent_executor import A2aAgentExecutor
from google.adk.a2a.utils.agent_card_builder import AgentCardBuilder
#REPLACE-IMPORT

def to_a2a(
    agent: BaseAgent, *, host: str = "0.0.0.0", port: int = 8080, public_url: str | None = None
) -> Starlette:
  """Convert an ADK agent to a A2A Starlette application.

  Args:
      agent: The ADK agent to convert
      host: The host for the A2A RPC URL (default: "0.0.0.0")
      port: The port for the A2A RPC URL (default: 8080)

  Returns:
      A Starlette application that can be run with uvicorn

  Example:
      agent = MyAgent()
      app = to_a2a(agent, host="localhost", port=8000)
      # Then run with: uvicorn module:app --host localhost --port 8000
  """
  # Set up ADK logging to ensure logs are visible when using uvicorn directly
  setup_adk_logger(logging.INFO)

  async def create_runner() -> Runner:
    """Create a runner for the agent."""
    return Runner(
        app_name=agent.name or "adk_agent",
        agent=agent,
        # Use minimal services - in a real implementation these could be configured
        artifact_service=InMemoryArtifactService(),
        session_service=InMemorySessionService(),
        memory_service=InMemoryMemoryService(),
        credential_service=InMemoryCredentialService(),
        #REPLACE-PLUGIN
    )

  # Create A2A components
  task_store = InMemoryTaskStore()

  agent_executor = A2aAgentExecutor(
      runner=create_runner,
  )

  request_handler = DefaultRequestHandler(
      agent_executor=agent_executor, task_store=task_store
  )

  # Build agent card
  #rpc_url = f"http://{host}:{port}/"
  card_builder = AgentCardBuilder(
      agent=agent,
      rpc_url=public_url,
  )

  # Create a Starlette app that will be configured during startup
  app = Starlette()

  # Add startup handler to build the agent card and configure A2A routes
  async def setup_a2a():
    # Build the agent card asynchronously
    agent_card = await card_builder.build()

    # Create the A2A Starlette application
    a2a_app = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler,
    )

    # Add A2A routes to the main app
    a2a_app.add_routes_to_app(
        app,
    )

  # Store the setup function to be called during startup
  app.add_event_handler("startup", setup_a2a)

  return app