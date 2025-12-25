
import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response, Choice

from task.agents.calculations.calculations_agent import CalculationsAgent
from task.agents.calculations.tools.simple_calculator_tool import SimpleCalculatorTool
from task.agents.calculations.tools.py_interpreter.python_code_interpreter_tool import PythonCodeInterpreterTool
from task.tools.deployment.content_management_agent_tool import ContentManagementAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.tools.mcp.mcp_client import MCPClient
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME

class CalculationsApplication(ChatCompletion):

    async def chat_completion(self, request: Request, response: Response) -> None:
        print(f"Endpoint: {request}")
        with response.create_single_choice() as choice:
            mcp_client = await MCPClient.create("http://localhost:8050/mcp")
            mcp_tools = await mcp_client.get_tools()
            agent = CalculationsAgent(
                endpoint=DIAL_ENDPOINT,
                tools=[
                    SimpleCalculatorTool(),
                    PythonCodeInterpreterTool(dial_endpoint=DIAL_ENDPOINT, tool_name="python_code_interpreter_tool",
                                              mcp_client=mcp_client, mcp_tool_models=mcp_tools),
                    ContentManagementAgentTool(endpoint=DIAL_ENDPOINT),
                    WebSearchAgentTool(endpoint=DIAL_ENDPOINT),
                ],
            )
            assistant_message = await agent.handle_request(
                deployment_name=DEPLOYMENT_NAME,
                choice=choice,
                request=request,
                response=response,
            )


if __name__ == "__main__":
    app = DIALApp(
        deployment_name="calculations-agent",
        impl=CalculationsApplication(),
    )

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5001,
    )
