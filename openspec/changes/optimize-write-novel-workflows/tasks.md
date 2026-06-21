## 1. 修复当前失败的断裂指针（B 组，最先做）

- [x] 1.1 跑 `bash write-novel/scripts/check-shared-files.sh`，记录全部 10 个断裂指针文件。根因：指针 `共享源:` 被脚本以 PLUGIN_ROOT 为基解析（line 172），但这 10 个文件写成 `../` 文件相对路径，逃出插件根。
- [x] 1.2 修 `write-novel-review` 的 6 个一级指针（`anti-ai-writing.md`/`character-relations.md`/`plot-core-methods.md`/`quality-checklist.md`/`banned-words.md`/`dialogue-mastery.md`）：`../../../references/shared/<file>` → `references/shared/<file>`。
- [x] 1.3 修 4 个嵌套指针（review/deslop/import/short-write 的 `references/shared/report-template.md`）：`../../../../references/shared/` → `references/shared/`。
- [x] 1.4 重跑 `check-shared-files.sh` → `Total errors: 0 / All shared files are consistent`。

## 2. 知识库单一来源去重（C 组）

- [x] 2.1 对 9 个 DIFFER 文件 `diff` 比对：确认 `shared/` 在每例中都是更丰富/更新版本（如 `hooks-paragraph.md` shared 146 行 vs methodology 49 行；`genre-writing-formulas.md` shared 多出「用作拆文标尺时」节）。methodology 副本均为陈旧遗留，无 shared 缺失的有效更新，无需合并。
- [x] 2.2 把 `references/methodology/genre-writing-formulas.md` 的 2 处引用（`skills/write-novel-long-write/references/workflow-daily.md:41` + `references/shared/workflow-daily.md:41`）改指 `references/shared/`，并删除 methodology 副本。
- [x] 2.3 删除其余 20 个「与 shared 同名」的 methodology 文件（删前确认 methodology 路径引用数为 0）。删后全仓无 dangling methodology 引用。
- [x] 2.4 在 `check-shared-files.sh` 增加「Single Source Validation」段：`methodology/` 不得出现与 `shared/` 同名的非指针文件，违例非零退出。
- [x] 2.5 新校验通过（Single source errors: 0）。methodology/ 去重后剩 14 个独有文件（>3），保留该目录；不并入 shared。

## 3. 仓库卫生（A 组）

- [x] 3.1 在 `.gitignore` 增补 `node_modules/`、`dist/`、`.pytest_cache/`、`__pycache__/`。已写入四项模式。
- [x] 3.2 `git rm -r --cached write-novel/dashboard/frontend/node_modules write-novel/dashboard/frontend/dist`（及其他被跟踪的缓存目录），确认本地文件保留。已取消跟踪（`git ls-files` 命中数 0），本地 node_modules/dist 仍 present。
- [x] 3.3 新增 `scripts/check-repo-hygiene.sh`（或并入 `audit-pipeline.py`）：`git ls-files` 命中 `node_modules/`/`dist/`/`__pycache__/`/`.pytest_cache/` 即非零退出（实现 `repo-hygiene-guard`）。新建并 chmod +x，独立运行 EXIT=0 [PASS]。
- [x] 3.4 把仓库卫生校验接入 `scripts/static-check.sh`，跑通确认 PASS。新增 `run_repo_hygiene`（Check 15），调用结果 [PASS]。注：static-check 整体仍报 3 个**既有** FAIL（已 `git show HEAD` 核实均在本变更前存在：workflow-daily.md 的 `write-novel-write-novel-story-explorer` 双前缀、analyze-short.md 的 genre/banned 引用、narrative-writer 模板 contract.md），与仓库卫生无关，留待 D 组/后续处理。
- [x] 3.5 在 dashboard 相关 README/说明处注明 `npm install` 步骤（因 node_modules 不再入库）。在 README 目录树 dashboard 行注明 `cd dashboard/frontend && npm install && npm run build`。

## 4. 文档真实度与主流程瘦身（D 组）

- [x] 4.1 校正 `README.md`：版本徽章 2.1.0→2.3.2；line 8 计数改为「13 个 Skills、8 个 Agents、9 个 Hook 条目（覆盖 5 类事件）」；快速开始命令全部改 `/write-novel:write-novel-*`；Skill 表重建为 13 行规范 + 4 别名说明；Agent 表重建为 8 行（移除不存在的 chapter-extractor，并入 deconstruction-agent 注）；Hooks 表对齐 hooks.json（5 事件 + validate_story_commit.sh 为 Git pre-commit 非 hooks.json 注）；目录树计数改 13 规范+4 别名 / 8 agent，dashboard 行加 `npm install` 注。
- [x] 4.2 校正 `USAGE.md`：全量 `/write-novel:story-*` → `/write-novel:write-novel-*`（含 scan/analyze 长短合流）；`/story`→`/write-novel:write-novel`；章节标题同步改名并补「（长篇/短篇模式）」标签；部署内容改「全套 hook 脚本」「8 个 agent」；Reference 架构段重写（shared/ 26 唯一来源、methodology/ 14 独有、指针文件机制）；Agent 体系改 8 行完整表。废弃别名不再列为规范命令。
- [x] 4.3 瘦身 `skills/write-novel/SKILL.md`「旧命名空间兼容」表：30+ 行替换为 4 行真实改名映射（long/short-analyze→analyze、long/short-scan→scan、plan→long-write、story→write-novel）+ 一行 `webnovel-*` 收敛说明。
- [x] 4.4 外移 `skills/write-novel-long-write/SKILL.md` 参考资料索引：新建 `references/loading-index.md`（Phase 1-5 场景→文件全表 + 横切主题权威文件表）；主文件 577-664 段替换为每 Phase 紧凑内联提示 + 指向 loading-index.md 的指针行。
- [x] 4.5 复核 agent 职责边界：产出 `agent-boundary-review.md`。结论——8 个 agent 均有真实 subagent_type 调用者（无僵尸）；reviewer↔consistency-checker、story-researcher↔story-explorer 两处「合并自」frontmatter 与现实矛盾，建议后续变更仅修措辞不合并；story-architect 维持不拆；deconstruction-agent 合并健康。本变更不强制任何合并。

## 5. 全量验证与门禁

- [x] 5.1 跑 `bash write-novel/scripts/check-shared-files.sh` → Total errors=0。证据：`Files checked (shared): 24 | Mismatches: 0`、Pointer 156/Errors 0、Whitelist 77/0、Namespace 0、Deploy 0、Single source 0；exit=0。
- [x] 5.2 跑 `bash write-novel/scripts/static-check.sh` → `Total: 23 | Pass: 22 | Fail: 0 | Warn: 9`，exit=0。本轮顺带修掉 3 个**既有** doc-truth FAIL（非本变更引入但属本变更 D 组真实度范畴，修复确定且低风险）：①`workflow-daily.md`（shared + long-write 两副本）双前缀 `write-novel-write-novel-story-explorer`→`write-novel-story-explorer`；②narrative-writer 模板 line 54 把 `.story-system/contracts/chapter_{N}.contract.md` 路径补反引号（消除裸 `contract.md` 误判，与同模板 line 51、reviewer 模板写法一致）；③`write-novel-analyze/references/` 补 3 个缺失指针文件（`banned-words.md` v1.5 / `anti-ai-writing.md` v2.3 / `genre-catalog.md` v1.8），使 analyze-short.md 的 3 处 shared 引用可解析。剩余 9 个 WARN 均为既有「裸 .md 未加反引号」非阻塞项，无一落在本次改动文件上。
- [x] 5.3 跑 `bash write-novel/scripts/check-version-consistency.sh` → `[PASS] plugin.json=2.3.2 marketplace.json=2.3.2 CHANGELOG=v2.3.2`，exit=0。
- [x] 5.4 `git status` 确认 node_modules/dist 已不再跟踪且不出现在未跟踪列表。证据：`git ls-files` 命中 `node_modules/`/`dist/`/`__pycache__/`/`.pytest_cache/` = 0；未跟踪（`??`）命中 = 0；`git check-ignore` 对四类产物路径均返回 ignored；现存 `D` 条目为上轮 `git rm --cached` 的索引内删除（待提交），非未跟踪再现。
