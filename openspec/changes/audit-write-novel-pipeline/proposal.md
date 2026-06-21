## Why

write-novel 插件经过多次迭代合并（长篇/短篇 skill 统一、agent 合并、命名空间迁移），累积了链路断裂、文件缺失、引用不一致等隐性债务。上一轮修复解决了表层问题（9→8 agent、共享指针创建、命名格式统一），但深度全链路审计发现了 **21 个新问题**，分布在 agent 模板滞后、版本号冲突、路由错误、MANIFEST 缺失、wrapper 死代码等关键领域。

本次审计覆盖 16 个 skill + 8 个 agent 的端到端链路，按 4 个维度并行扫描。

## What Changes

### 阻断级 (CRITICAL) — 4 项

1. **主路由 agent 名称双前缀错误**：`write-novel/SKILL.md` 第 32 行 `write-novel-write-novel-story-researcher` → `write-novel:write-novel-story-researcher`
2. **agents_version 三方冲突**：setup 迁移写 v12、全新部署写 v11、doctor 检查 <12，导致无限循环误报"需要升级"
3. **Agent 模板严重滞后于实际 agent**（4/8 模板缺 D8 新增能力）：story-architect、character-designer、narrative-writer、story-researcher 的模板缺失关键能力章节
4. **story-explorer 实际 agent 严重缩水**：68 行 vs 模板 327 行，缺失 benchmark_style_load 等 6 种查询类型

### 高级 (HIGH) — 9 项

5. Setup line 30：`chapter-extractor` 幽灵引用（旧名检测列表 9 个名，应为 8）
6. Agent 模板 `subagent_type` 命名不一致：模板使用无前缀格式，实际使用 `write-novel:` 前缀格式（story-explorer 例外，实际也无前缀）
7. story-researcher 模型不匹配：实际使用 `haiku`，模板使用 `sonnet`
8. deslop/review 的 `report-template.md` 指针路径差一级 `../`
9. short-write 缺失 `references/shared/report-template.md` 指针文件
10. story-explorer `maxTurns` 不匹配：实际=8，模板=15
11. UPGRADING.md v12 节误写"9 个 agent"（实际 8 个）
12. story-architect 引用 `references/shared/pattern-schema.md` —— 文件不存在
13. agent 文件 `被调用协议` 章节缺失：deconstruction-agent、consistency-checker(实际)、reviewer、story-explorer(实际) 无此章节

### 中级 (MEDIUM) — 7 项

14. 4 个 wrapper skill 含 ~316KB 僵尸文件（references/ + scripts/）
15. MANIFEST.yaml 多处缺失：genre-writing-techniques.md 路径错误、5 个真实文件未列入白名单、7 个 shared/ 文件未录入 shared_sources
16. `workflow-daily.md` 在 long-write 和 shared/ 之间内容已分化
17. Setup line 66：`story-long-write` 应改为 `write-novel-long-write`
18. Setup line 140：Hook 验证未覆盖 `post-compact.sh` / `pre-compact.sh`
19. reviewer agent（实际+模板）tools 字段声明 Glob 但未列入 tools 列表
20. consistency-checker 实际 agent 缺少 `disallowedTools: [Bash]`（模板有，实际只有 Write/Edit）

### 低级 (LOW) — 1 项

21. 跨 skill 脚本路径格式不统一（`node scripts/...` vs `node "${CLAUDE_PLUGIN_ROOT}/scripts/..."`）

## Capabilities

### Modified Capabilities
- `write-novel` 主路由：修正 agent 名称双前缀
- `write-novel-setup`：修正 agents_version 统一为 12、移除 chapter-extractor 幽灵引用、补全 hook 验证清单、修正命名空间引用
- `write-novel-doctor`：修正 agents_version 检查阈值为 <12（与 setup v12 对齐）
- `write-novel-review`：修正 report-template 指针路径
- `write-novel-deslop`：修正 report-template 指针路径
- `write-novel-short-write`：创建缺失的 report-template 共享指针
- `Agent 模板（4个）`：同步 D8 新增能力到 story-architect/character-designer/narrative-writer/story-researcher 模板
- `story-explorer agent`：将实际 agent 对齐到丰富模板（补全 6 种查询类型和 benchmark_style_load）
- `MANIFEST.yaml`：补全缺失条目
- `UPGRADING.md`：修正 agent 数量 9→8
- `清理 4 个 wrapper skill`：删除僵尸 references/ 和 scripts/ 目录

## Impact

- 受影响目录：`write-novel/skills/write-novel/`、`write-novel/skills/write-novel-setup/`、`write-novel/skills/write-novel-doctor/`、`write-novel/skills/write-novel-review/`、`write-novel/skills/write-novel-deslop/`、`write-novel/skills/write-novel-short-write/`、`write-novel/agents/`、`write-novel/references/shared/`
- 受影响模板：`write-novel/skills/write-novel-setup/references/templates/agents/`（4 个文件）
- 受影响配置：`MANIFEST.yaml`、`UPGRADING.md`
- 无 API 变更，无数据迁移，全部为修正性改动
