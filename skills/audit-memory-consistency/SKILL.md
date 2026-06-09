---
name: audit-memory-consistency
description: 定期抽检长期记忆的准确性——回溯原始对话，验证记忆摘要是否准确，发现可疑时通知用户。
---

# 记忆一致性审计

## 目标

从 memory2.db 中随机抽取一条带 `source_ref` 的记忆，回溯原始对话消息，判断记忆摘要是否与原文一致。不一致时通知用户，一致时静默记录。

## 工作文件

- `drift/skills/audit-memory-consistency/audited.json`：已审计的 memory_id 列表，防止重复审计同一记忆
- `drift/skills/audit-memory-consistency/suspicious.json`：标记为可疑的记忆及其审计结果

## 工作流程

1. `recall_memory` 随机查询一条近 30 天内创建、带 `source_ref` 的 event 或 profile 类型记忆。
2. 检查 `audited.json`：如果该记忆 ID 已审计过，换一条。
3. 通过 `fetch_messages` 读取该 `source_ref` 对应的原始对话消息（至少拉取 ±3 条上下文）。
4. **对比摘要与原文**：
   - 摘要是否准确反映了原文内容？
   - 摘要是否添加了原文中没有的推断？
   - 摘要是否遗漏了原文中的重要信息？
   - 日期、数字、名称等关键细节是否正确？
5. **判断**：
   - 一致 → 写入 `audited.json`，静默结束
   - 可疑 → 写入 `suspicious.json`，通过 `message_push` 通知用户：
     - 哪条记忆（ID + 摘要）
     - 原始消息说了什么
     - 为什么认为不一致
6. `finish_drift(message_result="sent")` 或 `finish_drift(message_result="silent")`

## 审计判断标准

- **高置信可疑**（必须通知）：
  - 摘要中出现了原文完全未提及的事实
  - 日期、数字、名称与原文明显不符
  - 摘要表达的情感/态度与原文相反
- **低置信可疑**（可选通知）：
  - 摘要省略了原文中的重要限定条件
  - 摘要的表达比原文更绝对（如 "用户喜欢 X" vs 原文 "用户觉得 X 还行"）

## 要求

- 每次只审计一条记忆，不要批量
- 模糊不清时不强行判断为可疑——宁可漏判不可误判
- 通知用户的语气：客观陈述事实，不做主观推断
- 不要调用 `message_push` 以外的写操作
