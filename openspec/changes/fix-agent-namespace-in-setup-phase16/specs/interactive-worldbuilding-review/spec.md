## MODIFIED Requirements

### Requirement: Agent generates draft only

在 Phase 1.6 世界观初始化中，story-architect agent SHALL 仅生成初稿文本并返回主线程，不得直接写入 `设定/世界观.md` 或 `设定/题材定位.md`。Agent 调用 SHALL 使用完整命名空间前缀 `subagent_type: "write-novel:write-novel-story-architect"`。

#### Scenario: Agent returns draft without writing files
- **WHEN** Phase 1.6 触发且 `设定/世界观.md` 不存在
- **THEN** spawn agent 使用 `subagent_type: "write-novel:write-novel-story-architect"`
- **AND** agent 成功启动并返回世界观初稿文本
- **AND** `设定/` 目录下不产生新文件
- **AND** 初稿全文缓存在主线程记忆中
