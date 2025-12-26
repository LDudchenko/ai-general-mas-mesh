import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response, Choice

from task.agents.web_search.web_search_agent import WebSearchAgent
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.mcp.mcp_client import MCPClient
from task.tools.mcp.mcp_tool import MCPTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

_DDG_MCP_URL = "http://localhost:8051/mcp"


class WebSearchApplication(ChatCompletion):

    async def chat_completion(self, request: Request, response: Response) -> None:
        with response.create_single_choice() as choice:
            mcp_client = await MCPClient.create(_DDG_MCP_URL)
            mcp_tool_models = await mcp_client.get_tools()
            mcp_tools = [MCPTool(mcp_tool_model=mcp_tool_model, client=mcp_client) for mcp_tool_model in mcp_tool_models]
            calculations_tool = CalculationsAgentTool(endpoint=DIAL_ENDPOINT)
            content_management_tool = ContentManagementAgentTool(endpoint=DIAL_ENDPOINT)
            tools = [calculations_tool, content_management_tool]
            tools.extend(mcp_tools)
            agent = WebSearchAgent(
                endpoint=DIAL_ENDPOINT,
                tools=tools,
            )
            await agent.handle_request(
                deployment_name=DEPLOYMENT_NAME,
                choice=choice,
                request=request,
                response=response,
            )


if __name__ == "__main__":
    app: DIALApp = DIALApp()
    agent_app = WebSearchApplication()
    app.add_chat_completion(deployment_name="web-search-agent", impl=agent_app)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5003,
    )
