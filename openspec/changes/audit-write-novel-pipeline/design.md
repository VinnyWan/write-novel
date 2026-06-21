## Context

write-novel 插件当前为 v2.3.1。上一轮修复（v2.3.0→v2.3.1）解决了：chapter-extractor 移除、agent 数量 9→8、subagent_type 命名格式统一、report-template 共享指针创建、doctor 追踪文件引用更新。

深度全链路审计（4 个并行 agent 扫描 16 skill + 8 agent + 模板 + MANIFEST + 脚本）发现了 21 个新问题，说明表层修复不彻底，需要系统性地解决根源不一致。

### 核心矛盾

1. **Agent 实际 vs 模板双向偏离**：4 个 agent 模板缺失 D8 新增能力（滞后于实际），而 story-explorer 实际严重缩水（68 行 vs 模板 327 行）
2. **版本号三方不一致**：migration 路径、fresh deploy 路径、doctor 检查三者对 `agents_version` 的期望不同
3. **命名格式未彻底统一**：模板仍使用无前缀格式 `write-novel-story-architect`，而实际 agent 使用 `write-novel:write-novel-story-architect`
4. **Wrapper skill 僵尸文件**：4 个合并 stub 下残留 ~316KB 的 references/ 和 scripts/

## Goals / Non-Goals

**Goals:**
- 修复 4 个阻断级问题（路由双前缀、版本号冲突、模板滞后、story-explorer 缩水）
- 修复 9 个高级问题（幽灵引用、命名不一致、模型/参数不匹配、缺失文件）
- 修复 7 个中级问题（僵尸文件清理、MANIFEST 补全、文档修正、tools 字段修正）
- 统一 agent 模板与实际 agent 的内容

**Non-Goals:**
- 不修改 agent 核心业务逻辑（仅同步模板）
- 不改变 skill 流程控制流
- 不新增功能
- 不处理 references/ 下方法论文件的内容差异（属于文档维护范畴）

## Decisions

### D1：agents_version 统一为 12

**选择：setup fresh deploy 写 `agents_version: 12`，doctor 检查 `< 12`，UPGRADING.md 标注 v12 为当前版本**

**理由**：migration 路径已经写 v12（Phase 2.0a step 4e），v12 对应 write-novel-* 命名空间迁移完成后的版本。fresh deploy 写 v11 是历史遗留。统一为 12 消除三方冲突。

**影响范围**：
- `write-novel-setup/SKILL.md` Phase 2 step 2.7：v11→v12
- `write-novel-setup/SKILL.md` Phase 3 step 5 验证：v11→v12（保持与部署一致）
- `write-novel-setup/SKILL.md` Phase 3 re-deploy gate：v11→v12
- `UPGRADING.md` line 51：移除 v11→v12 的过期映射

### D2：Agent 模板 subagent_type 格式统一

**选择：模板统一使用 `write-novel:<agent-name>` 格式（与实际 agent 对齐）**

**理由**：实际 agent 的 `name` frontmatter 字段使用 `write-novel:` 前缀格式（story-explorer 例外需要修正），skill 文件中的 Agent() 调用也使用此格式。模板的「被调用协议」章节应反映实际调用方式。

**story-explorer 特殊处理**：其 frontmatter `name: write-novel-story-explorer` 缺少 `write-novel:` 前缀。Claude Code 的路由机制基于 `write-novel:` namespace，story-explorer 应改为 `write-novel:write-novel-story-explorer` 以与其他 agent 一致。

### D3：story-explorer 对齐方向

**选择：将实际 agent（68 行）对齐到模板（327 行），即以模板为准**

**理由**：模板定义了完整的查询协议（11 种查询类型、benchmark_style_load 流程、结构化 JSON 输出），这些是 design.md 级别的能力定义。实际 agent 的缩水看起来是某次合并中的丢失，而非有意精简。story-explorer 在 analyze 流程中有重要作用（上下文加载、对标加载、风格基准加载），缩水版无法胜任。

### D4：Wrapper skill 僵尸文件清理

**选择：删除 4 个 wrapper skill 的 references/ 和 scripts/ 子目录，保留 SKILL.md stub**

**理由**：上一轮 audit 决定保留 wrapper skill（向后兼容），但 references/ 和 scripts/ 下的文件是合并前的内容副本，SKILL.md stub 不引用它们，MANIFEST 也未管理它们。保留会造成内容漂移风险（有人更新了这些孤儿副本）。只保留 SKILL.md stub 即可维持路由兼容。

### D5：共享指针路径修正

**选择：修正 deslop 和 review 的 report-template.md 指针为 `../../../../references/shared/report-template.md`（4 级上跳），创建 short-write 的共享指针文件**

**理由**：从 `write-novel/skills/write-novel-{deslop,review}/references/shared/` 到 `write-novel/references/shared/` 需要 4 级上跳（`../../../../`），当前 3 级（`../../../`）少了一级。

## Risks / Trade-offs

- **[低风险] story-explorer 大幅更新**：从 68 行扩展到 327 行可能引入与现有调用方的不兼容。Mitigation：模板是之前已定义的协议，调用方（analyze、query skill）按照模板协议调用，不会冲突。
- **[无风险] agents_version 统一**：纯数值修正，不影响运行时行为。
- **[无风险] 模板同步**：模板仅用于 setup 的 agent 部署，不影响已部署项目。
- **[低风险] wrapper 清理**：SKILL.md stub 保留，路由不受影响。

## Migration Plan

1. 按 tasks.md 顺序执行修复（先阻断级，再高级，最后中级）
2. 每个分类完成后运行对应验证
3. 全部完成后运行 `bash scripts/static-check.sh` 和 `bash scripts/check-shared-files.sh`
4. 无需回滚策略（所有修改为修正性）

## Open Questions

- 无
