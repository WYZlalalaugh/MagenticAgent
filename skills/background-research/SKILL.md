---
name: background-research
description: 扫描用户最近的对话，发现新话题后主动做背景研究，下次聊到时 agent 能提供有价值的信息。
---

# 后台研究

## 目标

从最近的对话中识别用户新关注的话题，主动进行背景研究（web_search + web_fetch），将结果写成简报。下次用户聊到这个话题时，agent 可以引用这些研究结果，显得"很懂"。

## 工作文件

- `drift/skills/background-research/researched.json`：已研究过的话题记录
- `drift/skills/background-research/briefings/`：研究简报存档目录

## 工作流程

1. `read_file` 读取 `researched.json`（不存在则为空）。
2. `recall_memory` 检索最近 7 天内新增的 `event` 或 `profile` 记忆。
3. 从新记忆中识别**未被研究过的新话题**。话题判断标准：
   - 是用户可以深入聊的内容（不是日常问候、闲聊）
   - 用户表达了兴趣或好奇心
   - 类似话题最近未被研究过
4. 选择 **1 个** 最适合深入研究的话题。
5. `web_search` + `web_fetch` 进行背景研究（至少 3 个来源）。
6. 将研究结果写成简报，写入 `briefings/{topic_slug}.md`：
   - 话题概述
   - 关键信息点（来源附 URL）
   - 用户可能的后续问题方向
7. 将话题记录到 `researched.json`。
8. **不要 `message_push`**——这是纯后台研究，用户不需要知道。
9. `finish_drift(message_result="silent")`

## 话题选择优先级

- 用户最近主动提到的新话题（刚被提起的 > 提到很久的）
- 用户表达了"想了解/想试试/看上去不错"的话题
- 话题有足够的公开信息可供研究（太偏门的不选）
- 避开通识话题（"今天天气不错"）、一次性事件（"快递到了"）、已经深入研究过的

## 简报格式

```markdown
# {话题名称}
研究时间: {时间}

## 概述
{2-3 句简介}

## 关键信息
- {要点1} [来源]({url})
- {要点2} [来源]({url})

## 用户可能的展开方向
- {方向1}
- {方向2}
```

## 要求

- 每次只研究一个话题
- 不推送，不通知——用户无感知，下次聊到才有惊喜
- 简报控制在 500 字以内，精炼优先
- 如果没有任何值得研究的话题，直接 `finish_drift(message_result="silent")`
