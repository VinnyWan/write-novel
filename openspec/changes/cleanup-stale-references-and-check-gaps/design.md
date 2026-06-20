## Context

write-novel 经过 v0.3（Skill/Agent 统一）→ v2.0（插件化）→ v2.2（竞品加固 + 瘦身）多轮重构后，`references/shared/` 累积了一批与现状脱节的文件。全仓库引用扫描（覆盖 skills / agents / hooks / scripts / evals / templates / MANIFEST）确认 14 个文件**零引用**：

| 类别 | 文件 | 性质 |
|---|---|---|
| v0.3 死文档（4） | `工作流总览.md`、`脚本治理.md`、`风险清单.md`、`当前任务.md` | 描述 `工作流/`、`卡片/` 目录与 13 个 CLI 脚本（`main.py`/`prompt_builder.py`/`dashboard.py` 等），均不存在；内部 `[[工作流/...]]` wikilink 全悬空 |
| 未接线 schema（6） | `context-format.md`、`projection-spec.md`、`style-cache-schema.md`、`technique-tracker-schema.md`、`verification-checklist.md`、`run-ledger-format.md` | 内容是真实规范（投影管线 133 行、断点格式 82 行等），但无任何消费者加载 |
| 错误案例样本（5） | `continuity-power-001.md`、`error-ai-slop-001.md`、`glossary-foreshadowing-001.md`、`hook-chapter-001.md`、`trope-face-slap-001.md` | `-001` 教学样本，frontmatter 完整，无 skill 加载 |

**盲区根因**：`static-check.sh` 现有 Check 1-9 只校验 `skills/<skill>/references/` 内引用，不校验顶层 `references/shared/` 内的 wikilink 与路径引用（Check 4 的 `find` 范围是 `$skill_dir/references`）。所以悬空 wikilink 潜伏至今未触发 FAIL。

**保留文件**（曾误判为孤儿，实为活跃）：`contract-schema.md`（eval `contract_schema_fields` 断言引用）、`pattern-schema.md`（architect agent 第 50 行加载）、`风险清单` 模板引用实为 `templates/output/` 内的章节标题非文件引用。

## Goals / Non-Goals

**Goals:**
- 移除 / 归档 14 个零引用文件，让 `references/shared/` 每个文件都有明确消费者或显式登记。
- 修复 `CLAUDE.md`「不存在 CLI 脚本」与现实（13 个 `.py`）的矛盾表述。
- 扩展 `static-check.sh` 覆盖 `references/shared/` 引用完整性，防止悬空链接复发。
- 将 v2.2.0 后 6 个瘦身提交归档为 CHANGELOG v2.3.0，对齐三处版本号。

**Non-Goals:**
- 不重新设计投影管线 / 断点机制（未接线 schema 若有价值，仅归档不接线，接线是后续独立提案）。
- 不改动任何 skill 的运行逻辑（纯文档 + 检查脚本）。
- 不处理 `references/methodology/`、`references/taxonomy/` 等其他子目录（本次聚焦 shared）。
- 不打 git tag / 不实际发布（仅整理版本态，发布动作由用户决定）。

## Decisions

### D1: v0.3 死文档（4）→ 直接删除
**选择**：删除 `工作流总览.md`、`脚本治理.md`、`风险清单.md`、`当前任务.md`。
**理由**：内容 100% 描述不存在的体系，保留只会误导。git 历史可追溯，无知识损失。
**替代方案**：归档到 `references/archive/`——否决，因为内容已失效，归档等于把垃圾放进抽屉。

### D2: 未接线 schema（6）→ 归档到 `references/archive/`
**选择**：新建 `references/archive/`，移入这 6 个文件，并在 archive 目录加 `README.md` 说明「这些规范未接线，若要启用需在对应 skill 加载并补 eval 断言」。
**理由**：`projection-spec.md`（133 行投影管线）、`run-ledger-format.md`（82 行断点格式）内容真实有价值，可能后续要接线。归档保留知识、移出 shared 避免 static-check 误报，且明确标记「待接线」状态。
**替代方案**：
- 直接删除——否决，丢失可能复用的规范。
- 留在原位加 whitelist——否决，治标不治本，whitelist 膨胀且不解决「无人加载」本质。
**触发条件**：若 design review 阶段判定某文件应接线而非归档，则从归档移出并补加载点 + eval 断言。

### D3: 错误案例样本（5）→ 归档到 `references/rules/`
**选择**：移入已存在的 `references/rules/`（该目录已有同类规则文件，4 个），与现有 rules 体系融合。
**理由**：`-001` 样本是教学素材，`rules/` 是其自然归属。不删除因 frontmatter 完整、有 genre_tags，后续 deslop / review skill 可按需加载。
**替代方案**：移入 archive——否决，rules 目录已存在且语义匹配，无需新建。

### D4: static-check 新增 Check 10「shared 引用完整性」
**选择**：在 `static-check.sh` 末尾新增 Check 10，扫描 `references/shared/*.md` 内所有 `[[...]]` wikilink 与 `](...)` 路径引用，目标不存在则 FAIL。**不**校验「文件是否被消费」（引用计数），只校验「引用的目标是否存在」（悬空检测），避免误伤合法的低频文件。
**理由**：盲区是悬空链接而非孤儿文件。Check 4 已有路径解析逻辑可复用，扩展扫描范围到 `references/shared/` 即可。校验引用计数会误判 `contract-schema`（仅 eval 引用）这类合法低频文件，故只做悬空检测。
**替代方案**：扩展现有 Check 4——否决，Check 4 是 per-skill 的，shared 是跨 skill 的，混在一起会模糊职责。
**预期结果**：14 个孤儿移除后，shared 内剩余 wikilink 全部指向存在的目标，Check 10 PASS。

### D5: CLAUDE.md 表述修正
**选择**：将「**不存在 CLI 脚本或 Python 工具层**」改为「**脚本仅做确定性自动化（解析 / 校验 / 派生），写作流程全部由 skill + Markdown 驱动**」，并同步修正「不调用任何 Python/Shell 脚本（除非是编码处理等底层确定性工具）」表述。
**理由**：现状是 scripts/ 有 13 个 `.py` 做校验/统计/解析，与「不存在脚本」直接矛盾。修正后与 `脚本治理` 精神（脚本只做确定性自动化）一致。

### D6: 版本对齐 → v2.3.0
**选择**：CHANGELOG 新增 `## v2.3.0 (2026-06-20) — 文档清理 + 静态检查盲区补齐`，归档 6 个瘦身提交；plugin.json / marketplace.json 从 `2.2.0` → `2.3.0`；移除 v2.2.0 的「（未发布）」标注（标记为已随 v2.3 合并发布）。
**理由**：6 个瘦身提交已改变 skill 行为，不应继续挂在「未发布」的 v2.2 下。无 git tag，发布动作留给用户。

## Risks / Trade-offs

- **[删除死文档后 wikilink 仍悬空]** → 死文档是悬空链接的**源头**（`[[工作流/...]]` 都在它们内部），删除后悬空消失，风险自解。
- **[归档 schema 后有人按旧路径加载失败]** → 这些文件本就零引用，无人加载；归档后在 archive/README.md 列明原路径，可追溯。
- **[Check 10 误报合法文件]** → 只做悬空检测不做引用计数，`contract-schema`（eval 引用）、`pattern-schema`（agent 引用）不受影响。
- **[references/archive 新目录被 check-shared-files 误判]** → 需在 `check-shared-files.sh` 的扫描范围排除 `archive/`，或确认其 `find` 只扫 `skills/`（实际只扫 skills/，archive 在顶层不受影响——待 tasks 阶段验证）。
- **[版本升 v2.3.0 但无实质功能变化]** → 文档清理 + 检查增强属于维护性变更，CHANGELOG 明确标注「无功能变更」，避免用户误期待新功能。

## Migration Plan

1. **先补检查再清理**（安全顺序）：先实现 Check 10 并确认它能在「清理前」检出 shared 悬空链接（证明检查有效），再执行清理，最后确认 Check 10 PASS。
2. 清理按 D1（删 4）→ D2（归档 6）→ D3（归档 5）顺序执行，每步后跑 `static-check.sh` 确认不引入新 FAIL。
3. 修正 CLAUDE.md（D5）。
4. 版本对齐（D6）。
5. 全量验证：`static-check.sh` + `run-behavior-evals.sh` + `check-shared-files.sh` 三链全 PASS。
6. **回滚**：纯文件操作，`git revert` 单提交即可完整回滚，无数据迁移风险。

## Open Questions

- **Q1**：`projection-spec.md` / `run-ledger-format.md` 是否应该「接线」而非归档？即是否应在 long-write skill 里补加载点 + eval 断言？本次提案默认归档（Non-Goal），但若维护者认为接线更重要，可拆为后续提案。**建议**：先归档，接线单独提案。
- **Q2**：`references/archive/` 是否需要纳入 `check-shared-files.sh` 的扫描豁免？需在 tasks 阶段实测确认。
