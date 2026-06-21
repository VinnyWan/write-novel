## Context

Clifford 平台 agent 注册使用 `插件名:agent名` 命名空间格式。`write-novel` 插件下的 agent 类型为 `write-novel:write-novel-story-architect`，而非裸名 `write-novel-story-architect`。Phase 1.6.3 的 agent spawn 调用使用了错误格式。

## Goals / Non-Goals

**Goals:**
- 修正 `subagent_type` 参数为 `"write-novel:write-novel-story-architect"`

**Non-Goals:**
- 不修改其他 agent 调用
- 不改变 Phase 1.6 其他逻辑

## Decisions

**D1：直接替换字符串**

SKILL.md 第 93 行的 `subagent_type: "write-novel-story-architect"` 改为 `subagent_type: "write-novel:write-novel-story-architect"`。

**Why**: 单行修改，无副作用。该 SKILL.md 中仅此一处 agent spawn 调用使用了裸名格式。

## Risks / Trade-offs

_无。纯字符串修正，不影响其他流程。_
