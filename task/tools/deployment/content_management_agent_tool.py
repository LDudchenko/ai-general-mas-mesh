from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class ContentManagementAgentTool(BaseAgentTool):

    @property
    def deployment_name(self) -> str:
        return "content-management-agent"

    @property
    def name(self) -> str:
        return "content_management_agent"

    @property
    def description(self) -> str:
        return (
            "Agent for content management tasks such as drafting, editing, "
            "rewriting, summarizing, organizing, and improving text content. "
            "Supports multi-step workflows and optional history propagation."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The content-related task or instruction to perform.",
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
