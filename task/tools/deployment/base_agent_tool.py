import json
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any

from aidial_client import AsyncDial
from aidial_sdk.chat_completion import Message, Role, CustomContent, Stage, Attachment
from pydantic import StrictStr

from task.tools.base_tool import BaseTool
from task.tools.models import ToolCallParams
from task.utils.stage import StageProcessor


class BaseAgentTool(BaseTool, ABC):

    def __init__(self, endpoint: str):
        self.endpoint = endpoint

    @property
    @abstractmethod
    def deployment_name(self) -> str:
        pass

    async def _execute(self, tool_call_params: ToolCallParams) -> str | Message:
        client = AsyncDial(api_version='2025-01-01-preview', endpoint=self.endpoint, api_key=tool_call_params.api_key)
        print(f"Endpoint: {self.endpoint}")
        messages = self._prepare_messages(tool_call_params)
        chunks = client.chat.completions.create(messages=messages, deployment_name=self.deployment_name,
                                       stream=True,
                                       extra_headers={"x-conversation-id": tool_call_params.conversation_id})
        content = ""
        custom_content: CustomContent = CustomContent()
        stages_map: dict[int, Stage] = {}

        async for chunk in chunks:
            delta = chunk.choices[0].delta
            if delta.content:
                content += delta.content
                tool_call_params.stage.append_content(delta.content)
            if delta.custom_content:
                if delta.custom_content.attachments:
                    custom_content.attachments.extend(delta.custom_content.attachments)
                if delta.custom_content.state:
                    custom_content.state = delta.custom_content.state

                custom_content_dict = delta.custom_content.dict(exclude_none=True)
                if "stages" in custom_content_dict:
                    for stg in custom_content_dict["stages"]:
                        idx = stg["index"]
                        if idx in stages_map:
                            mapped_stage = stages_map[idx]
                            if stg.get("content"):
                                mapped_stage.append_content(stg["content"])
                            if stg.get("attachments"):
                                for att in stg["attachments"]:
                                    mapped_stage.add_attachment(Attachment(**att))
                            if stg.get("status") == "completed":
                                StageProcessor.close_stage_safely(mapped_stage)
                        else:
                            mapped_stage = StageProcessor.open_stage(tool_call_params.choice, name=stg.get("name"))
                            stages_map[idx] = mapped_stage

        for stage in stages_map.values():
            StageProcessor.close_stage_safely(stage)

        return Message(role=Role.TOOL, tool_call_id=tool_call_params.tool_call.id, content=StrictStr(content),
                       custom_content=custom_content)


    def _prepare_messages(self, tool_call_params: ToolCallParams) -> list[dict[str, Any]]:
        args = json.loads(tool_call_params.tool_call.function.arguments)
        prompt: str = args.get("prompt", "")
        propagate_history: bool = args.get("propagate_history", False)
        messages: list[dict[str, Any]] = []

        if propagate_history:
            request_messages = tool_call_params.messages
            for idx in range(len(request_messages)):
                msg = request_messages[idx]

                if (
                        msg.role == Role.ASSISTANT and msg.custom_content and msg.custom_content.state and self.name in msg.custom_content.state):
                    last_user_message = request_messages[idx - 1]
                    messages.append(last_user_message.dict(exclude_none=True))

                    assistant_message = deepcopy(msg)
                    assistant_message.custom_content.state = msg.custom_content.state.get(self.name)
                    messages.append(assistant_message.dict(exclude_none=True))

        messages.append({
            "role": Role.USER,
            "content": prompt,
            "custom_content": CustomContent().dict(exclude_none=True),
        })

        return messages
