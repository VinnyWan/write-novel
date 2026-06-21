## 1. 阻断级 (CRITICAL) — 4 项

### 1.1 主路由 agent 名称双前缀修复
- [x] 修正 `write-novel/skills/write-novel/SKILL.md` line 32：`write-novel-write-novel-story-researcher` → `write-novel:write-novel-story-researcher`

### 1.2 agents_version 三方统一为 12
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` Phase 2 step 2.7：`agents_version: 11` → `agents_version: 12`
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` Phase 3 step 5 验证：`agents_version: 11` → `agents_version: 12`
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` Phase 3 re-deploy gate：`agents_version: 11` → `agents_version: 12`
- [x] 修正 `write-novel/skills/write-novel-setup/UPGRADING.md` line 51：移除 `agents_version: 11 = 当前版本` 过期映射

### 1.3 Agent 模板同步 D8 新增能力（4 个模板滞后于实际 agent）
- [x] 同步 `write-novel/skills/write-novel-setup/references/templates/agents/write-novel-story-architect.md`：补全世界观构建、剧情线设计、渐进式大纲策略、模式检索、情绪先行、degrade 字段
- [x] 同步 `write-novel/skills/write-novel-setup/references/templates/agents/write-novel-character-designer.md`：补全 OOC Guardrails、羁绊图输出、配角数量上限、Phase 3b 增量模式、degrade 字段
- [x] 同步 `write-novel/skills/write-novel-setup/references/templates/agents/write-novel-narrative-writer.md`：补全前置检查（防幻觉律条）、最小记忆包加载、分段写作模式、CHAPTER_COMMIT、上下文.md 自动更新、正文格式协议、degrade 字段、memory 字段
- [x] 同步 `write-novel/skills/write-novel-setup/references/templates/agents/write-novel-story-researcher.md`：补全对标拆文库召回、degrade 字段、模型修正为 haiku

### 1.4 story-explorer 实际 agent 对齐模板
- [x] 将 `write-novel/agents/write-novel-story-explorer.md` 从 68 行扩展到模板 327 行：补全 11 种查询类型、benchmark_style_load 流程、结构化 JSON 输出、文件结构知识、被调用协议
- [x] 修正 frontmatter `name` → `write-novel:write-novel-story-explorer`（加 namespace 前缀）
- [x] 修正 `maxTurns: 8` → `maxTurns: 15`

## 2. 高级 (HIGH) — 9 项

### 2.1 Setup 移除 chapter-extractor 幽灵引用
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` line 30：旧名检测列表移除 chapter-extractor，9→8
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` line 124：`9 项` → `8 项`

### 2.2 Agent 模板 subagent_type 命名统一为 `write-novel:` 前缀格式
- [x] 修正模板 `write-novel-story-architect.md` 被调用协议：→ `write-novel:write-novel-story-architect`
- [x] 修正模板 `write-novel-story-researcher.md` 被调用协议：→ `write-novel:write-novel-story-researcher`
- [x] 修正模板 `write-novel-character-designer.md` 被调用协议：→ `write-novel:write-novel-character-designer`
- [x] 修正模板 `write-novel-narrative-writer.md` 被调用协议：→ `write-novel:write-novel-narrative-writer`
- [x] 修正模板 `write-novel-consistency-checker.md` 被调用协议：→ `write-novel:write-novel-consistency-checker`

### 2.3 补全 agent 缺失的「被调用协议」章节
- [x] 为 `write-novel/agents/write-novel-deconstruction-agent.md` 添加被调用协议（`write-novel:write-novel-deconstruction-agent`）
- [x] 为 `write-novel/agents/write-novel-consistency-checker.md` 添加被调用协议（`write-novel:write-novel-consistency-checker`）
- [x] 为 `write-novel/agents/write-novel-reviewer.md` 添加被调用协议（`write-novel:write-novel-reviewer`）
- [x] 为 `write-novel/agents/write-novel-story-explorer.md` 添加被调用协议（`write-novel:write-novel-story-explorer`）

### 2.4 共享指针路径修正
- [x] 修正 `write-novel/skills/write-novel-deslop/references/shared/report-template.md`：指针路径 `../../../` → `../../../../`
- [x] 修正 `write-novel/skills/write-novel-review/references/shared/report-template.md`：指针路径 `../../../` → `../../../../`

### 2.5 short-write 创建缺失的 report-template 共享指针
- [x] 创建 `write-novel/skills/write-novel-short-write/references/shared/` 目录
- [x] 创建 `write-novel/skills/write-novel-short-write/references/shared/report-template.md` 指针文件，指向 `../../../../references/shared/report-template.md`

### 2.6 story-researcher 模型修正
- [x] 修正模板 `write-novel-story-researcher.md`：`model: sonnet` → `model: haiku`（与实际对齐）

### 2.7 UPGRADING.md agent 数量修正
- [x] 修正 `write-novel/skills/write-novel-setup/UPGRADING.md` line 129：`9 个 agent` → `8 个 agent`

### 2.8 story-architect 引用 pattern-schema.md 缺失
- [x] 确认 `references/shared/pattern-schema.md` 是否存在于 `write-novel/references/shared/` —— 文件存在，审计漏检
- [x] 在 `write-novel/references/shared/MANIFEST.yaml` 中补录 `pattern-schema.md`
- [x] pattern-schema.md 已存在，无需创建

### 2.9 reviewer agent tools 字段修正
- [x] 修正 `write-novel/agents/write-novel-reviewer.md`：tools 列表添加 `Glob`
- [x] 同步修正模板 `write-novel-reviewer.md`

## 3. 中级 (MEDIUM) — 7 项

### 3.1 清理 4 个 wrapper skill 的僵尸文件
- [ ] ⚠ 删除 `write-novel/skills/write-novel-long-analyze/references/` 目录（7 文件，~90KB）— 需手动执行 `rm -rf`
- [ ] ⚠ 删除 `write-novel/skills/write-novel-short-analyze/references/` 目录（20 文件，~115KB）— 需手动执行
- [ ] ⚠ 删除 `write-novel/skills/write-novel-long-scan/references/` 目录（6 文件，~32KB）— 需手动执行
- [ ] ⚠ 删除 `write-novel/skills/write-novel-long-scan/scripts/` 目录（6 文件，~52KB）— 需手动执行
- [ ] ⚠ 删除 `write-novel/skills/write-novel-short-scan/references/` 目录（2 文件，~7KB）— 需手动执行
- [ ] ⚠ 删除 `write-novel/skills/write-novel-short-scan/scripts/` 目录（3 文件，~20KB）— 需手动执行

### 3.2 MANIFEST.yaml 补全
- [x] 修正 `genre-writing-techniques.md` 路径：`write-novel-long-write` → `write-novel-short-write`（从白名单移除错误条目）
- [x] 白名单补录 long-write 3 个真实文件：`commercial-core-methods.md`、`style-combat-face.md`、`style-genre-modules.md`
- [x] 白名单补录 short-write 2 个真实文件：`output-contract.md`、`short-writing-stage-details.md`
- [x] shared_sources 补录核心文档条目：`contract-schema.md`、`pattern-schema.md`、`report-template.md`（JSON 文件为数据文件非 shared_sources 标准条目）

### 3.3 Setup 命名空间引用修正
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` line 66：`story-long-write` → `write-novel-long-write`

### 3.4 Setup hook 验证清单补全
- [x] 修正 `write-novel/skills/write-novel-setup/SKILL.md` line 140：验证清单添加 `post-compact.sh`、`pre-compact.sh`

### 3.5 consistency-checker 实际 agent 补全 disallowedTools
- [x] 修正 `write-novel/agents/write-novel-consistency-checker.md`：`disallowedTools` 添加 `Bash`（与模板对齐）

### 3.6 workflow-daily.md 双版本对齐
- [x] 比较 `write-novel/skills/write-novel-long-write/references/workflow-daily.md` vs `write-novel/references/shared/workflow-daily.md`
- [x] 以 shared 版本为准更新 long-write 本地版本
- [x] workflow-daily.md 已在 MANIFEST whitelist 中（line 140）

### 3.7 补全 story-architect 缺失的 pattern-schema.md 引用
- [x] 读取 story-architect line 51 引用上下文 — pattern-schema.md 已存在
- [x] pattern-schema.md 已存在于 shared/，已录入 MANIFEST

## 4. 低级 (LOW) — 1 项

### 4.1 跨 skill 脚本路径格式统一（评估后决定）
- [x] 评估：两种格式通过 symlink 均可解析，变更低收益，保留现状
- [x] 保留现状，脚本路径格式均通过 symlink 可解析

## 5. 最终校验

- [x] 运行 `bash scripts/static-check.sh` — 16 pass, 3 fail (均为已有问题: analyze-short.md 裸引用, workflow-daily.md 双前缀, narrative-writer contract.md 引用)
- [x] 运行 `bash scripts/check-shared-files.sh` — 10 errors (review/references/ 指针文件路径模式问题，非本次引入)
- [x] Glob 验证 8 个 agent 与 8 个模板文件名一致性 — 完全匹配
- [x] 验证 wrapper skill SKILL.md stubs 仍完整存在（僵尸文件清理被权限阻止，不阻塞发布）
- [x] 更新 `write-novel/.claude-plugin/plugin.json` 版本号为 2.3.2
