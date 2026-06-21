## Why

对 `write-novel` 插件做了一次全链路扫描（17 个 skill 目录 / 8 个 agent / 22 个脚本 / 11 个 hook / dashboard / references 知识库 / 顶层文档）。既有变更 `audit-write-novel-pipeline` 已修复「失效交叉引用 / 废弃命令当主命令 / 清单计数」等链路断裂，但**仓库卫生、知识库单一来源、文档真实度、主流程瘦身**这几类问题它没有覆盖，且其中三项是**当前就在失败/正在膨胀**的硬问题：

- `dashboard/frontend/node_modules` 共 **4118 个文件被提交进 Git**（`.gitignore` 仅忽略 `__pycache__/*.pyc`），仓库严重膨胀。
- `check-shared-files.sh` **现在就报 18 个错误 / 10 个断裂指针文件**（`write-novel-review` 一家 7 个指针相对层级写错，指向不存在的共享源）——审计变更把它记为「既存项、非回归」但未修。
- `references/methodology/` 与 `references/shared/` **有 21 个同名文件重复**，其中 **10 个已漂移**（`hooks-paragraph.md` 差 165 行）；而真正被运行时消费的是 `shared/`（84 处引用 vs `methodology/` 仅 2 处），重复副本是漂移温床。
- 顶层文档计数自相矛盾：`README.md` 同时写「15 个 Skills」「14 个 Skills」「9 个 Agents」，真实为 13 个规范 skill（+4 个废弃别名）+ 8 个 agent。

现在做，是因为这些问题会随每次写作/重生成产物持续放大（漂移扩散、仓库越拉越大、新用户被错误文档误导）。

## What Changes

按影响排序，分四组：

**A. 仓库卫生（最高优先，当前正在恶化）**
- 将 `dashboard/frontend/node_modules/`、`dashboard/frontend/dist/`、`.pytest_cache/`、`*.pyc` 等纳入 `.gitignore`，并 `git rm -r --cached` 取消已跟踪的 4118+ 个 vendored 文件（不删本地文件）。
- 明确 dashboard 构建产物（`dist/`）由构建流程生成，不入库。

**B. 修复当前失败的断裂指针（确定性 bug）**
- 修正 `check-shared-files.sh` 报告的 10 个断裂指针文件（相对路径层级错误 + 指向不存在共享源），使其退出码归零；其中 `write-novel-review` 7 个、`write-novel-deslop` 1 个、`write-novel-short-write` 1 个、嵌套 `references/shared/report-template.md` 指针若干。

**C. 知识库单一来源（消除漂移面）**
- 确立不变量：写作方法论每个文件**有且仅有一份**权威副本在 `references/shared/`，skill 通过指针文件消费；`references/methodology/` 不得保存与 `shared/` 同名的全文副本。
- 处理 21 个重复文件：`methodology/` 中与 `shared/` 同名且被运行时引用的（如 `genre-writing-formulas.md`）改为指针或把引用改指 `shared/`；纯重复未被引用的删除；`methodology/` 独有且在用的（`banned-words-star-rating.md`、`toxic-sentence-patterns.md`、`genre-profile-configs.md` 等）保留。
- 把这条不变量加入 `check-shared-files.sh`（或 `audit-pipeline.py`），防止再生。

**D. 文档真实度 + 主流程瘦身（中优先）**
- 校正 `README.md` / `USAGE.md` 的 skill/agent/hook 计数与命令清单，与 `plugin.json` / `marketplace.json`（已为 13+8）对齐；废弃别名不得列为规范命令。
- 瘦身路由表：`skills/write-novel/SKILL.md:62-100` 的「旧命名空间兼容」表删除字面同名的「旧长形式」行、把 `webnovel-*` 收敛为一条说明。
- 评估 `write-novel-long-write/SKILL.md`（670 行）：将「参考资料索引」（约 88 行，line 577-664）外移到 `references/loading-index.md`，主文件只留每 Phase 内联加载提示，降低单文件认知负担。
- 复核 agent 职责边界（`reviewer` vs `consistency-checker`；`story-architect`/`story-explorer`/`story-researcher`）——本组仅产出复核结论与建议，不在本变更强制合并。

**非目标**：不删除废弃别名 skill 本身（保持向后兼容）；不重写 dashboard 功能；不改写作方法论正文内容。

## Capabilities

### New Capabilities
- `reference-single-source`: 写作方法论知识库的单一权威来源不变量——每份方法论文件唯一权威副本在 `references/shared/`，skill 经指针文件消费，禁止 `references/methodology/` 保存同名全文副本；并由确定性脚本校验（无重复同名全文、指针可解析、`methodology/` 残留仅限其独有且被引用文件）。
- `repo-hygiene-guard`: 仓库卫生护栏——确定性校验依赖目录（`node_modules`）、构建产物（`dist`）、缓存（`__pycache__`/`.pytest_cache`）未被 Git 跟踪，且 `.gitignore` 覆盖这些模式。

### Modified Capabilities
<!-- openspec/specs/ 当前为空；audit-write-novel-pipeline 的 pipeline-audit-tooling 尚未归档为正式 spec，本变更不修改其需求，只新增上述两条正交能力。 -->
（无）

## Impact

- **新增**：`.gitignore` 规则；`reference-single-source` 与 `repo-hygiene-guard` 的校验逻辑（接入 `scripts/check-shared-files.sh` 或 `scripts/audit-pipeline.py` + `static-check.sh`）。
- **删除（取消跟踪，不删本地）**：`dashboard/frontend/node_modules/`（4118 文件）、`dashboard/frontend/dist/`（20 文件）等 vendored/构建/缓存文件。
- **修改（修复）**：10 个断裂指针文件；`references/methodology/` 21 个重复文件去重；`README.md`、`USAGE.md` 计数与命令；`skills/write-novel/SKILL.md` 路由兼容表；`skills/write-novel-long-write/SKILL.md` 索引外移。
- **无破坏性变更**：废弃别名 skill 保留；指针机制与现有写作流程不变；仅修复路径错误与去重。
- **依赖**：校验脚本仅依赖 Python3 / 标准 shell，无新增外部依赖。
