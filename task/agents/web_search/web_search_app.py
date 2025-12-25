import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response, Choice

from task.agents.web_search.web_search_agent import WebSearchAgent
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.mcp.mcp_client import MCPClient
from task.tools.mcp.mcp_tool import MCPTool
from task.utils.constants import DIAL_ENDPOINT

_DDG_MCP_URL = "http://localhost:8051/mcp"


class WebSearchApplication(ChatCompletion):

    async def chat_completion(self, request: Request, response: Response) -> None:
        choice = Choice(index=0)
        # Ініціалізація MCP та інструментів MAS Mesh
        mcp_client = MCPClient(_DDG_MCP_URL)
        mcp_tool = MCPTool(mcp_client)
        calculations_tool = CalculationsAgentTool(endpoint=DIAL_ENDPOINT)
        content_management_tool = ContentManagementAgentTool(endpoint=DIAL_ENDPOINT)

        agent = WebSearchAgent(
            endpoint=DIAL_ENDPOINT,
            tools=[mcp_tool, calculations_tool, content_management_tool],
        )

        # Делегуємо обробку запиту агенту
        await agent.handle_request(
            deployment_name="web-search-agent",
            choice=choice,
            request=request,
            response=response,
        )


if __name__ == "__main__":
    app = DIALApp(
        deployment_name="web-search-agent",
        impl=WebSearchApplication(),
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5003,
    )
