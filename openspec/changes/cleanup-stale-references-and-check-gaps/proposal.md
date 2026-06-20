## Why

项目经过 v0.3 → v2.2 多轮重构后，`references/shared/` 残留一批 v0.3 时代的「工作流 / CLI 脚本」体系文档，它们描述的目录结构（`工作流/`、`卡片/`）和脚本（`main.py`、`prompt_builder.py`、`dashboard.py` 等 13 个）均已不存在，内部 wikilink 全部悬空，且无任何 skill / agent / MANIFEST 引用。同时 `CLAUDE.md` 声称「不存在 CLI 脚本」与 `scripts/` 下实际 13 个 `.py` 自相矛盾，`static-check.sh` 只校验 SKILL.md 内引用、不校验 shared 目录 wikilink，导致这批死文档潜伏至今未被检测。CHANGELOG v2.2.0 标注「未发布」但此后已有 6 个瘦身提交未归档，版本态混乱。

## What Changes

- **清理孤儿文档**：经全仓库（skills / agents / hooks / scripts / evals / templates / MANIFEST）引用扫描确认，移除 `references/shared/` 下 14 个零引用文件，分三类处理：
  - 删除 v0.3 遗留死文档（4）：`工作流总览.md`、`脚本治理.md`、`风险清单.md`、`当前任务.md`——描述的 `工作流/`、`卡片/` 目录与 `main.py`/`prompt_builder.py`/`dashboard.py` 等 13 个 CLI 脚本均不存在，内部 wikilink 全悬空，与项目现状完全脱节。
  - 归档未接线的 schema / 格式规范（6）：`context-format.md`、`projection-spec.md`、`style-cache-schema.md`、`technique-tracker-schema.md`、`verification-checklist.md`、`run-ledger-format.md`——内容是真实规范（投影管线、断点格式等）但无任何 skill/agent/eval 加载，属「写了没接线」。移至 `references/archive/` 保留知识价值，不直接删除（design 阶段定夺归档 vs 接线）。
  - 归档错误案例样本（5）：`continuity-power-001.md`、`error-ai-slop-001.md`、`glossary-foreshadowing-001.md`、`hook-chapter-001.md`、`trope-face-slap-001.md`——教学样本，无 skill 加载，移至 `references/rules/`（已有同类目录）或 archive。
  - **保留**：`contract-schema.md`（被 eval `contract_schema_fields` 断言引用）、`pattern-schema.md`（被 architect agent 加载）、`report-template.md`/`workflow-daily.md` 等高引用文件。
- **修复 CLAUDE.md 矛盾表述**：将「不存在 CLI 脚本」更正为「脚本仅做确定性自动化（解析 / 校验 / 派生），写作流程全部由 skill + Markdown 驱动」，与 `scripts/` 现状及 `脚本治理` 精神一致。
- **补静态检查盲区**：扩展 `scripts/static-check.sh` 增加 Check 10「shared 目录 wikilink / 路径引用完整性」，扫描 `references/shared/` 内所有 `[[...]]` 与裸路径引用，发现目标不存在即 FAIL，防止悬空链接复发。
- **处理版本 / 发布状态**：将 v2.2.0 后的 6 个瘦身提交归档为 CHANGELOG v2.3.0 条目，对齐 plugin.json / marketplace.json 版本号，标记 v2.2.0 为已发布或合并进 v2.3.0。

## Capabilities

### New Capabilities
- `reference-hygiene`: 共享参考文件的引用完整性治理——孤儿文件识别、清理与归档规范，确保 `references/shared/` 内每个文件都有明确消费者或被显式登记。
- `static-check-coverage`: 静态检查链的覆盖范围扩展，新增对 `references/shared/` 内 wikilink 与路径引用的完整性校验，作为发版前守护门禁的一部分。

### Modified Capabilities
<!-- 无既有 spec，全部为新建 -->

## Impact

- **受影响文件**：`write-novel/references/shared/*.md`（删除 / 归档 16 个）、`write-novel/scripts/static-check.sh`（新增 Check）、`write-novel/scripts/check-shared-files.sh`（可能联动）、`CLAUDE.md`（表述修正）、`CHANGELOG.md` + `write-novel/.claude-plugin/plugin.json` + `.claude-plugin/marketplace.json`（版本对齐）。
- **受影响检查**：`static-check.sh` 当前 15/15 PASS、10 WARN，新增 Check 后预期仍 PASS（因悬空文件被删除）；`check-shared-files.sh` 的 `IGNORE_NAMES` / whitelist 可能需同步调整。
- **行为 eval**：`write-novel/evals/` 内若有断言引用被删文件需更新（待 design 阶段核查）。
- **风险**：删除文件不可逆，但引用计数为 0 + git 可追溯，风险可控；归档样本保留在 `references/rules/` 避免丢失教学价值。
- **依赖**：无外部依赖变更，纯仓库内清理。
