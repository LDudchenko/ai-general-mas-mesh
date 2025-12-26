import uvicorn
from aidial_sdk import DIALApp
from aidial_sdk.chat_completion import ChatCompletion, Request, Response

from task.agents.content_management.content_management_agent import ContentManagementAgent
from task.agents.content_management.tools.files.file_content_extraction_tool import FileContentExtractionTool
from task.agents.content_management.tools.rag.document_cache import DocumentCache
from task.agents.content_management.tools.rag.rag_tool import RagTool
from task.tools.deployment.calculations_agent_tool import CalculationsAgentTool
from task.tools.deployment.web_search_agent_tool import WebSearchAgentTool
from task.utils.constants import DIAL_ENDPOINT, DEPLOYMENT_NAME


class ContentManagementApplication(ChatCompletion):
    def __init__(self):
        self.tools = [
                FileContentExtractionTool(endpoint=DIAL_ENDPOINT),
                RagTool(endpoint=DIAL_ENDPOINT, document_cache=DocumentCache(), deployment_name=DEPLOYMENT_NAME),
                CalculationsAgentTool(endpoint=DIAL_ENDPOINT),
                WebSearchAgentTool(endpoint=DIAL_ENDPOINT),
            ]

    async def chat_completion(self, request: Request, response: Response) -> None:
        with response.create_single_choice() as choice:
            agent = ContentManagementAgent(
                endpoint=DIAL_ENDPOINT,
                tools=self.tools,
            )
            await agent.handle_request(
                deployment_name=DEPLOYMENT_NAME,
                choice=choice,
                request=request,
                response=response,
            )



if __name__ == "__main__":
    app: DIALApp = DIALApp()
    agent_app = ContentManagementApplication()
    app.add_chat_completion(deployment_name="content-management-agent", impl=agent_app)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5002,
    )

