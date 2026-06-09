---
name: self-health-check
description: 定期检查系统健康状态——工具调用成功率、记忆库状态、token 用量趋势，发现异常时通知用户。
---

# 系统健康检查

## 目标

通过检查 `observe.db`、`memory2.db` 和 `proactive.db`，诊断系统是否存在异常，发现潜在问题时通知用户。

## 工作文件

- `drift/skills/self-health-check/last_run.txt`：上次运行日期
- `drift/skills/self-health-check/health_log.md`：历史健康检查记录

## 检查项目

### 1. 工具调用成功率
- 查询 `observe.db` 的 `turns` 表，统计近期 tool_calls 中是否有高频错误
- 如某工具近 24h 内连续失败 > 3 次 → 标记为异常

### 2. 记忆库状态
- `recall_memory` 查询记忆总数和各类别分布
- 检查是否有大量 `status='superseded'` 的记忆（超过总量的 30%）
- 检查最近的 consolidation 是否正常（HISTORY.md 最近一次更新是否在 24h 内）

### 3. Prompt Cache 命中率
- 查询 `observe.db` 的 `turns` 表，统计 `react_cache_hit_tokens / react_cache_prompt_tokens`
- 命中率 < 50% → 可能 MEMORY.md 变化过于频繁

### 4. 主动推送统计
- 查询 `proactive.db` 的 `tick_log`，统计最近 24h 的推送次数和跳过原因分布
- 跳过率 > 95% 且不是 quiet 模式 → 可能数据源有问题

## 通知规则

- 所有指标正常 → `finish_drift(message_result="silent")`
- 发现异常 → `message_push` 汇总报告：
  - 异常项及其严重程度
  - 建议操作（重启服务、检查 MCP 连接、清理记忆等）
- 异常持续 > 3 天 → 加重提醒语气

## 要求

- 只读操作，不修改任何数据库
- 每次只检查，不做自动修复
- 报告格式简洁，先结论后细节
