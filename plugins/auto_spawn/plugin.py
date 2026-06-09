from __future__ import annotations

import logging
from typing import Any, cast

from agent.lifecycle.types import BeforeTurnCtx
from agent.plugins import Plugin

logger = logging.getLogger("plugin.auto_spawn")

_RULES: dict[str, str] = {
    # pattern (在消息中匹配) → spawn task 模板
    "查一下": "用户想深入了解某个话题，如需要多步调研，用 spawn(profile=research, background=true) 创建后台研究任务",
    "帮我搜": "用户想搜索某些信息，如搜索范围较大，用 spawn(profile=research, background=true) 创建后台搜索任务",
    "整理一下": "用户想整理/汇总信息，如涉及多个来源，用 spawn(profile=research) 创建整理任务",
    "写一个": "用户想写代码/文档，如复杂度较高，用 spawn(profile=scripting) 创建编写任务",
}

_HINT_SLOT = "session:extra_hint:auto_spawn"


class AutoSpawnHintModule:
    slot = "auto_spawn.hint"
    requires = ("before_turn.emit",)

    async def run(self, frame) -> object:
        state = frame.input
        msg = state.msg.content

        hints: list[str] = []
        for pattern, hint in _RULES.items():
            if pattern in msg:
                hints.append(hint)

        if hints:
            frame.slots[_HINT_SLOT] = "\n".join(hints)
            logger.info(f"auto_spawn: injected hints for message with patterns={list(_RULES.keys() & set(msg.split()))}")

        return frame


class AutoSpawnPlugin(Plugin):
    name = "auto_spawn"

    def before_turn_modules(self) -> list[object]:
        return [AutoSpawnHintModule()]
