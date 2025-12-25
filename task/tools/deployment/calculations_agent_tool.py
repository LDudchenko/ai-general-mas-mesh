from typing import Any

from task.tools.deployment.base_agent_tool import BaseAgentTool


class CalculationsAgentTool(BaseAgentTool):

    @property
    def deployment_name(self) -> str:
        return "calculations-agent"

    @property
    def name(self) -> str:
        return "calculations_agent"

    @property
    def description(self) -> str:
        return (
            "Agent for performing calculations, mathematical reasoning, "
            "and numeric problem solving. Supports multi-step reasoning "
            "and optional history propagation."
        )

    @property
    def parameters(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "prompt": {
                    "type": "string",
                    "description": "The calculation or mathematical problem to solve.",
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
