## 1. 审计工具实现（pipeline-audit-tooling）

- [x] 1.1 在 `write-novel/scripts/audit-pipeline.py` 实现审计脚本骨架：以插件根为基准，枚举全部 `skills/*/SKILL.md` 与 `agents/*.md`，集中定义废弃别名常量（`write-novel-long-analyze`/`write-novel-short-analyze`/`write-novel-long-scan`/`write-novel-short-scan`/`write-novel-plan`）。
- [x] 1.2 实现「文件引用可解析」校验（spec 不变量 1）：提取相对路径，按「文件目录/skill 根/插件根」解析，缺失报 `BROKEN_REF`（含来源文件+行号）。
- [x] 1.3 实现「交叉引用指向存活」校验（不变量 2）：检测元数据/调用方中废弃别名，区分重定向表白名单上下文，违例报 `STALE_CALLER`。
- [x] 1.4 实现「部署模板使用规范命令名」校验（不变量 3）：扫描 `templates/CLAUDE.md.tmpl`、`templates/hooks/*.sh`、`templates/agents/*.md`，违例报 `DEPLOY_STALE_CMD`。
- [x] 1.5 实现「双份 hooks 同步」校验（不变量 4）：命名映射对齐 `hooks/` 与 `templates/hooks/`，比对 `settings-hooks.json` 引用一一对应，违例报 `HOOK_NAME_MISMATCH`/`HOOK_DRIFT`。
- [x] 1.6 实现「清单计数与版本一致性」校验（不变量 5）：比对 `marketplace.json`/`plugin.json` 声明与真实 skill(规范/别名)/agent 计数及版本，违例报 `MANIFEST_COUNT_MISMATCH`/`VERSION_MISMATCH`。
- [x] 1.7 实现结构化报告 + 退出码（不变量 6）：分类汇总、来源行号、修复建议；存在高优先级问题时非零退出。
- [x] 1.8 对当前仓库跑首轮审计，核对报告与 proposal 枚举的缺口一致，确认零误报。

## 2. 修复具体缺口

- [x] 2.1 修 `agents/write-novel-deconstruction-agent.md` 调用方：`write-novel-long-analyze` → `write-novel-analyze`（并修正正文 `/webnovel-init` 失效引用）。
- [x] 2.2 修 `skills/write-novel-setup/references/templates/agents/write-novel-deconstruction-agent.md` 同一 stale caller（及正文 `/webnovel-init`）。
- [x] 2.3 修 `templates/CLAUDE.md.tmpl` 路由表：4 行废弃命令收敛为 `/write-novel-analyze`、`/write-novel-scan` 两行规范命令。
- [x] 2.4 修部署 hook 提示文案：`templates/hooks/session-start.sh`、`templates/hooks/detect-story-gaps.sh` 中废弃命令 → 规范命令。
- [x] 2.5 校验双份 hooks 的「配置引用可解析」：`settings-hooks.json`→`templates/hooks/`、`hooks.json`→`hooks/` 引用全部存在。经核查两套 hooks 按角色分化（运行态含额外脚本），非简单副本，**不做内容强同步**（spec 已据此修订）。同步修正运行态 `hooks/detect_story_gaps.sh` 残留废弃命令提示。
- [x] 2.6 修清单元数据：`marketplace.json` 描述计数改为 13 Skills + 8 Agents、版本与 `plugin.json` 对齐到 `2.3.2`。
- [x] 2.7 清理用户可见/会回流到产物的 `references/*.md` 废弃名（低优先级 WARN 项中影响产物的部分）。14 个参考文档批量更正，byte-equal 同步对（output-contract.md analyze↔short-write）保持一致；审计 DOC_STALE_NAME 清零。

## 3. 接入与验证

- [x] 3.1 把 `audit-pipeline.py` 接入 `scripts/static-check.sh`（新增 Check 14 `run_pipeline_audit`，在 reference-audit 之后运行，按退出码计入 PASS/FAIL）。
- [x] 3.2 修复后重跑审计，达到高优先级问题清零（PASS / 零退出码）：`python3 scripts/audit-pipeline.py` → `结果：PASS — 全部链路不变量通过`（EXIT=0）；static-check Check 14 → `[PASS] all pipeline invariants hold`。
- [x] 3.3 运行既有回归检查确认无回归：`check-version-consistency.sh` → `[PASS] plugin.json=2.3.2 marketplace.json=2.3.2 CHANGELOG=v2.3.2`；`check-shared-files.sh` 退出 0（8 处 shared 不匹配均在 review/deslop/short-write 未编辑文件，为既存项，非本次回归）。注：`check-hook-regex-sync.sh` 不存在于仓库（任务原始引用有误），实际 hook 同步由 `check-shared-files.sh` Deploy State 段覆盖（错误 0）。
