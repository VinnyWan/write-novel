## Context

`write-novel` 是纯 Markdown 驱动的中文网文创作插件：13 个规范 skill（+4 个废弃别名）、8 个 agent、22 个脚本、11 个 hook、一个可选 dashboard，以及 `references/` 知识库。知识库已采用「指针文件 + 单一共享源」反漂移设计——`references/shared/` 存全文，各 skill 的 `references/*.md` 是 6 行指针（首行 `> **共享参考文件**`，指向 `references/shared/<file>`）。`check-shared-files.sh` 负责校验指针可解析。

当前状态偏差：
- 指针机制被两处破坏。其一，`references/methodology/` 又存了 21 个与 `shared/` 同名的**全文副本**，10 个已漂移；其二，10 个 skill 指针的**相对层级写错**，`check-shared-files.sh` 现在报 18 错。
- `dashboard/frontend/node_modules`（4118 文件）与 `dist`（20 文件）被提交进库，`.gitignore` 几乎为空。
- 文档计数三处自相矛盾。

约束：CLAUDE.md 规定 `/docs`、`/openspec`、`/.claude` 不入库；废弃别名必须保留向后兼容；写作方法论正文内容不在本次改动范围（只动「副本/指针/路径」结构，不动知识本身）。既有变更 `audit-write-novel-pipeline` 提供了 `audit-pipeline.py` 与 `static-check.sh` Check 14，本变更复用该接入点，不重复造轮子。

## Goals / Non-Goals

**Goals:**
- 让 `git` 仓库停止跟踪依赖/构建/缓存产物，且未来不再回流。
- `check-shared-files.sh` 退出码归零（10 个断裂指针修好）。
- 写作方法论每文件单一权威副本；去除 `methodology/`↔`shared/` 重复，并用脚本固化「不得再生重复」。
- 文档与清单计数一致、准确；路由兼容表瘦身；主流程文件认知负担下降。

**Non-Goals:**
- 不删除废弃别名 skill；不改变写作流程语义。
- 不重构/重写 dashboard 功能（仅停止跟踪其构建产物）。
- 不修改写作方法论的知识正文。
- agent 合并/退休不在本次执行（仅产出复核结论）。

## Decisions

**D1：node_modules 用 `git rm -r --cached` 而非物理删除。** 取消跟踪但保留本地工作副本，dashboard 仍可本地运行。同时 `.gitignore` 增补 `node_modules/`、`dist/`、`.pytest_cache/`、`__pycache__/`。备选「物理删 + 重装」被否，风险高且无收益。

**D2：methodology/shared 去重策略按「是否被运行时引用」分流，而非一刀切删。**
- `methodology/` 中**与 shared 同名且被引用**者（仅 `genre-writing-formulas.md`，被 `workflow-daily.md` 引用）：把引用方改指 `shared/`，删 methodology 副本——单一来源。
- `methodology/` 中**与 shared 同名且无人引用**者（其余 20 个）：直接删除。
- `methodology/` **独有且在用**者（`banned-words-star-rating.md`、`toxic-sentence-patterns.md`、`genre-profile-configs.md` 等）：保留。
- 备选「把 methodology 副本全转成指针」被否：徒增 21 个指针文件，不如消除目录重复职责。

**D3：单一来源不变量交给脚本固化，而非仅靠纪律。** 在 `check-shared-files.sh` 增一段校验：`methodology/` 不得出现与 `shared/` 同名的非指针文件。归入新能力 `reference-single-source`，复用现有 Check。

**D4：仓库卫生不变量同样脚本化。** 新增轻量校验（可并入 `audit-pipeline.py` 或独立 `check-repo-hygiene.sh`）：`git ls-files` 不得命中 `node_modules/`、`dist/`、`__pycache__/`、`.pytest_cache/`；接入 `static-check.sh`。归入 `repo-hygiene-guard`。

**D5：断裂指针按 `check-shared-files.sh` 报告逐个修相对层级。** 嵌套指针 `skills/X/references/shared/report-template.md` 需 `../../../../`，一级指针 `skills/X/references/foo.md` 需 `../../../`。逐文件核对解析结果，修完重跑至 0 错。

**D6：文档计数以 `plugin.json`/`marketplace.json`（13 Skills + 8 Agents）为准绳。** README/USAGE 对齐到该口径，hook 计数按 `hooks.json` 实际条目数核定。

## Risks / Trade-offs

- [取消跟踪 node_modules 后，依赖 git 拉取 node_modules 的克隆流程会断] → dashboard 本就需 `npm install`；在 dashboard README/requirements 旁注明安装步骤即可。
- [删 methodology 重复文件可能误删仍被引用者] → 删除前对每个待删文件 `grep -r` 全仓确认零引用；只有 `genre-writing-formulas.md` 需先改引用再删。
- [漂移副本中 methodology 版本可能比 shared 更新] → 删除前对 10 个 DIFFER 文件逐一 `diff`，若 methodology 含 shared 缺失的有效更新，先把更新合并进 `shared/` 再删副本（避免丢内容）。
- [指针层级修错会引入新断链] → 以 `check-shared-files.sh` 退出码为唯一验收标准，修后必跑。
- [README 改动可能与正在进行的 audit 变更冲突] → audit 变更只改 `marketplace.json`，本变更只改 README/USAGE，无文件重叠。

## Migration Plan

1. 先做 B 组（修断裂指针）→ 跑 `check-shared-files.sh` 验证归零。
2. 做 C 组（去重 + 不变量），每删一个文件前 grep 确认；漂移文件先合并有效更新。
3. 做 A 组（gitignore + rm --cached）。
4. 做 D 组（文档/路由/索引）。
5. 全量回归：`static-check.sh` + `check-shared-files.sh` + `check-version-consistency.sh` 全绿。
回滚：全部为文件级改动，`git revert` 即可；node_modules 取消跟踪可 `git checkout` 恢复跟踪。

## Open Questions

- dashboard 是否仍为活跃功能？若已弃用，可考虑后续单独变更整体移除（本次仅停止跟踪产物，不决策去留）。
- `methodology/` 去重后是否整目录仅剩少数独有文件——若 ≤3 个，是否并入 `shared/` 彻底取消该目录（留待复核组结论）。
