## Why

第一轮瘦身（v2.2→v2.3）主要集中在 agent 合并和 references 目录清理，但流程层还有三个被遗漏的摩擦点：session start 误报"环境未部署"导致每次打开项目都看到莫名告警；SKILL.md 路由表保留了 30+ 行 `webnovel-*` 旧命名空间兼容映射，实际已有 6+ 个月未被触发；MANIFEST.yaml 的 shared_sources 列表和 rules/archive 目录迁移后未同步更新。这些问题单独看都是小事，但每天出现累积起来就是持续的认知负荷。

## What Changes

- **修复 session start 误报警告**：`session_start.sh` 检查 `.story-deployed` sentinel 文件，但 sentinel 从未被真正写入。改为检查实际 hooks 文件是否存在来判断部署状态，消除每次启动的假告警。
- **清理路由层旧命名空间兼容**：从 SKILL.md 移除 `webnovel-*`（5 个）和已废弃旧 `write-novel-*` 长格式（7 个）兼容条目，保留向后兼容说明 2 行。这些映射在 v0.3→v2.0 迁移中使用，当前已无用户触发。
- **同步 MANIFEST.yaml**：修复 shared_sources 列表——移除已删除/归档文件的条目，为新增 `references/rules/` 下 5 个错误案例样本添加登记。对齐白名单与实际目录状态。
- **补齐迁移遗漏**：确认 4 个中文文件（工作流总览/脚本治理/风险清单/当前任务）的删除已落盘，5 个案例样本（continuity-power-001 等）的 rules 迁移已完成，archive 的 6 个 schema 文件归档已完成，static-check 已扩展且通过。

## Capabilities

### New Capabilities
- `session-start-sentinel`: SessionStart hook 的部署状态检测逻辑——用实际文件存在性替代 sentinel 文件机制，消除误报。
- `route-namespace-cleanup`: 路由表命名空间治理——旧兼容条目移除标准与流程，确保 SKILL.md 只保留活跃命名空间。
- `manifest-post-migration-sync`: MANIFEST.yaml 与 filesystem 的一致性校验——迁移后同步 shared_sources/whitelist/rules 登记。

### Modified Capabilities
<!-- 无既有 spec，全部为新建 -->

## Impact

- **受影响文件**：`write-novel/hooks/session_start.sh`（部署检测逻辑）、`write-novel/skills/write-novel/SKILL.md`（路由兼容表）、`write-novel/references/shared/MANIFEST.yaml`（源文件索引）。
- **风险**：移除旧命名空间兼容后，若有用户仍用 `webnovel-init` 等旧触发词会路由失败。缓解：已废弃 6+ 个月且 CLAUDE.md 未引用任何旧名；CHANGELOG 记录 breaking change。
- **依赖**：依赖 `cleanup-stale-references-and-check-gaps` 变更先落地（因为它负责实际的 references 文件移动），本变更在该变更基础上做验证和收尾。
