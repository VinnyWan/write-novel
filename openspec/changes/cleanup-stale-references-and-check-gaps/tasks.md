## 1. 先补静态检查盲区（证明有效再清理）

- [x] 1.1 在 `write-novel/scripts/static-check.sh` 末尾新增 Check 10「shared 引用完整性」：扫描 `references/shared/*.md` 内所有 `[[...]]` wikilink 与 `](...)` 路径引用，目标不存在则 FAIL。复用 Check 4 的路径解析逻辑，扫描范围改为顶层 `references/shared/`。只做悬空检测，不做引用计数。
- [x] 1.2 运行 `bash write-novel/scripts/static-check.sh`，确认 Check 10 在清理前能检出 `工作流总览.md` / `脚本治理.md` 等文件内的悬空 `[[工作流/...]]` wikilink（证明检查有效）。记录检出清单。
- [x] 1.3 若 Check 10 误报 `contract-schema`（eval 引用）或 `pattern-schema`（agent 引用）等合法文件，调整检查逻辑只校验引用目标存在性，不校验消费方。
- [x] 1.4 Check 10 额外检出 `quality-checklist.md` 引用 `output-templates.md` 悬空（shared 无此文件，仅各 skill-local 有）。修复：将 `](output-templates.md)` 链接改为裸名叙述，因 shared 文件不应绑定具体 skill 路径。

## 2. 清理 v0.3 死文档（删除 4 个）

- [ ] 2.1 删除 `write-novel/references/shared/工作流总览.md`
- [ ] 2.2 删除 `write-novel/references/shared/脚本治理.md`
- [ ] 2.3 删除 `write-novel/references/shared/风险清单.md`
- [ ] 2.4 删除 `write-novel/references/shared/当前任务.md`
- [ ] 2.5 运行 `static-check.sh` 确认悬空 wikilink FAIL 数下降，无新 FAIL。

## 3. 归档未接线 schema（6 个 → references/archive/）

- [ ] 3.1 新建 `write-novel/references/archive/` 目录
- [ ] 3.2 创建 `write-novel/references/archive/README.md`，列明 6 个归档文件的原路径、内容性质、待接线状态
- [ ] 3.3 移动 `context-format.md`、`projection-spec.md`、`style-cache-schema.md`、`technique-tracker-schema.md`、`verification-checklist.md`、`run-ledger-format.md` 到 `references/archive/`
- [ ] 3.4 确认 `check-shared-files.sh` 的 `find` 范围只扫 `skills/`（不扫顶层 `references/archive/`），归档文件不触发跨 skill 一致性检查。若会触发，在脚本中排除 `archive/`。
- [ ] 3.5 运行 `static-check.sh` 确认归档后 shared 顶层不再有这些文件的悬空引用。

## 4. 归档错误案例样本（5 个 → references/rules/）

- [ ] 4.1 确认 `write-novel/references/rules/` 目录存在及现有内容（4 个 rules 文件）
- [ ] 4.2 移动 `continuity-power-001.md`、`error-ai-slop-001.md`、`glossary-foreshadowing-001.md`、`hook-chapter-001.md`、`trope-face-slap-001.md` 到 `references/rules/`
- [ ] 4.3 确认这些样本的 frontmatter（id/category/genre_tags）在 rules 目录下仍有效，无引用断裂。
- [ ] 4.4 运行 `static-check.sh` 确认无新 FAIL。

## 5. 修复 CLAUDE.md 矛盾表述

- [ ] 5.1 将 `CLAUDE.md` 中「**不存在 CLI 脚本或 Python 工具层**」改为「**脚本仅做确定性自动化（解析 / 校验 / 派生），写作流程全部由 skill + Markdown 驱动**」
- [ ] 5.2 修正「不调用任何 Python/Shell 脚本（除非是编码处理等底层确定性工具）」表述，与 scripts/ 下 13 个 .py 现状对齐
- [ ] 5.3 同步检查 `write-novel/` 内是否有其他文档（README / USAGE）复述「不存在脚本」的说法，一并修正。

## 6. 版本对齐 v2.3.0

- [ ] 6.1 在 `CHANGELOG.md` 顶部新增 `## v2.3.0 (2026-06-20) — 文档清理 + 静态检查盲区补齐`，归档 6 个瘦身提交（write-novel-short-scan / long-scan / short-analyze / long-analyze / setup / import）的变更摘要
- [ ] 6.2 将 v2.2.0 条目的「（未发布）」标注移除或改为「合并入 v2.3.0 发布」
- [ ] 6.3 更新 `write-novel/.claude-plugin/plugin.json` 版本号 `2.2.0` → `2.3.0`
- [ ] 6.4 更新 `.claude-plugin/marketplace.json` 版本号 `2.2.0` → `2.3.0`
- [ ] 6.5 运行 `bash write-novel/scripts/check-version-consistency.sh` 确认三处版本号一致。

## 7. 全量验证（Change Delivery Gate）

- [x] 7.1 运行 `bash write-novel/scripts/static-check.sh`，确认 Total PASS（含新增 Check 10）、Fail = 0。记录输出。
- [x] 7.2 运行 `bash write-novel/scripts/run-behavior-evals.sh`，确认全部 eval case PASS，尤其 `contract_schema_fields`（依赖 contract-schema 保留）不回归。记录输出。
- [x] 7.3 运行 `bash write-novel/scripts/check-shared-files.sh`，确认跨 skill 一致性 PASS，归档文件不误报。记录输出。
- [x] 7.4 确认 `references/shared/` 顶层剩余文件全部有消费者或 MANIFEST 登记（contract-schema / pattern-schema / 各 shared_sources 等），无残留孤儿。
- [x] 7.5 如实报告验证结果；任何无法执行的检查须说明原因，不得声称「通过」而无证据。
