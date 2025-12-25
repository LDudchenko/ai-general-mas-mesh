from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class WebSearchAgentTool(BaseAgentTool):

    @property
    def deployment_name(self) -> str:
        return "web-search-agent"

    @property
    def name(self) -> str:
        return "web_search_agent"

    @property
    def description(self) -> str:
        return (
            "Agent for performing web searches and information retrieval. "
            "Finds up-to-date, relevant information from the web, "
            "summarizes results, and provides source-based answers. "
            "Supports optional history propagation."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The search query or information request to look up on the web.",
                },
                "propagate_history": {
                    "type": "boolean",
                    "description": (
                        "Whether to propagate previous interaction history "
                        "with this agent."
                    ),
                    "default": False,
                },
            },
            "required": ["prompt"],
        }
