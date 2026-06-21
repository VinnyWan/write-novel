## Why

Phase 1.6.3 中 `subagent_type` 写成 `"write-novel-story-architect"`（裸名），但 Clifford 平台注册的 agent 类型为 `"write-novel:write-novel-story-architect"`（带插件命名空间前缀）。当前写法导致 Agent spawn 时报错 `Agent type 'write-novel-story-architect' not found`，世界观初始化流程卡死在初稿生成阶段。

## What Changes

- Phase 1.6.3 Agent 调用中 `subagent_type` 从 `"write-novel-story-architect"` 改为 `"write-novel:write-novel-story-architect"`

## Capabilities

### New Capabilities
_无（纯 bug fix）_

### Modified Capabilities
- `interactive-worldbuilding-review`: Agent 调用中的 `subagent_type` 参数需使用完整命名空间前缀 `write-novel:write-novel-story-architect`

## Impact

- `skills/write-novel-setup/SKILL.md` — Phase 1.6.3 Agent spawn 调用中的 `subagent_type` 参数
