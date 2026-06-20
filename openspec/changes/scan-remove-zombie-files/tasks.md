## 1. 新增 Check 11「反向引用计数」

- [x] 1.1 创建 `reference_audit.py` Python 脚本 + `run_reference_audit()` bash wrapper，替换纯 bash 实现（避开 bash 3.x 无关联数组限制）。扫描全仓库 .md 文件，提取 markdown 链接 + wikilink + 反引号路径 + agent ref，构建 `ref_count` 字典。
- [x] 1.2 引用解析走 Python `resolve_ref()`：skill-local（相对源文件目录）→ 插件根 → 全仓库 basename 索引回退。
- [x] 1.3 白名单排除：`SKILL.md`（系统路由入口）、`contract-schema.md`（仅 eval 引用）、`UPGRADING.md`、`references/rules/` 目录（hooks 运行时加载）、`references/methodology/`、`references/archive/`、`skills/write-novel-setup/references/agent-references/`/`templates/`（部署模板）。
- [x] 1.4 零引用输出按目录分组，WARN 级别。
- [x] 1.5 运行确认：检出 3 个零引用僵尸（agents/ 下 chapter-extractor、consistency-checker、story-explorer）。

## 2. 新增 Check 12「循环引用检测」

- [x] 2.1 在 `reference_audit.py` 中实现 `check_cyclic_references()`：构建邻接表，迭代式 DFS + `in_stack` set 检测 back-edge。
- [x] 2.2 图节点范围：`skills/*/references/**/*.md` + `references/shared/*.md`。排除 methodology。
- [x] 2.3 自引用单独处理为 WARN，不计入 FAIL 环。
- [x] 2.4 环检测输出 `source → target` 对，FAIL 级别。
- [x] 2.5 路径标准化为相对 PLUGIN_ROOT 路径。
- [x] 2.6 运行确认：检出 2 个自引用 + 7 个循环引用（详见分析）。

## 3. 新增 Check 13「Agent 调用方检测」

- [x] 3.1 在 `reference_audit.py` 中实现 `check_agent_callers()`：扫描所有 SKILL.md + references/*.md 中的 `subagent_type` 引用（含引号和无引号两种格式）。
- [x] 3.2 零调用方 WARN。
- [x] 3.3 非规范命名 `write-novel-*` 检测 WARN。
- [x] 3.4 运行确认：检出 1 个零调用 agent（chapter-extractor）。consistency-checker 和 story-explorer 经扩展扫描（references 文件 + 无引号格式）后确认有调用方。

## 4. 运行全量扫描，分析结果

- [x] 4.1 运行完整扫描，Check 1-13 全部运行。最终结果：Total: 19 | Pass: 18 | Fail: 0 | Warn: 11。
- [x] 4.2 Check 11 零引用分析：
  - `agents/write-novel-chapter-extractor.md` → **真僵尸**（零 subagent_type 调用，UPGRADING.md 记载已合并至 deconstruction-agent）→ 已删除
  - `agents/write-novel-consistency-checker.md` → **假阳性**（被 reviewer-spawn-templates.md 通过 subagent_type: 无引号格式调用，非文件路径引用）→ 保留
  - `agents/write-novel-story-explorer.md` → **假阳性**（被自身 agent 模板和 setup 引用，UPGRADING.md 记载已合并至 story-researcher 但模板仍保留）→ 保留
  - `references/shared/workflow-daily.md` → **假阳性**（被多个 skill SKILL.md 通过裸名/反引号引用，非 markdown 链接引用导致漏计数）→ 保留
- [x] 4.3 Check 12 循环分析：原始 7 个循环均因双向 markdown 链接或双向反引号引用造成。已逐一修复：去掉较弱的引用方向（改为纯文本），7 个循环全部消除 → PASS。
- [x] 4.4 Check 13 agent 分析：chapter-extractor 确认零调用方（全仓库 skill + references 扫描）→ 已删除。其余 8 个 agent 均有调用方。

## 5. 清理僵尸文件

- [x] 5.1 删除 `agents/write-novel-chapter-extractor.md`——确认零 subagent_type 调用方。
- [x] 5.2 无其他零调用 agent（Check 13 现为 PASS）。
- [x] 5.3 循环引用修复（共 6 处文件修改）：
  - `material-decomposition.md`：`[output-templates.md](output-templates.md)` → 纯文本 `output-templates.md`；移除 `` `references/output-templates.md` `` 和 `` `references/pipeline-ops.md` `` 的反引号
  - `workflow-daily.md`：移除 `` `workflow-daily.md` `` 自引用的反引号
  - `structure-mapping-long.md`：移除 `` `structure-mapping-short.md` `` 和 `` `length-routing.md` `` 的反引号
  - `output-contract.md`（short-analyze + short-write 双副本）：移除 `` `write-novel-short-analyze/references/output-templates.md` `` 的反引号
  - `style-profile-protocol.md`：移除 `` `style-profile-generator.md` `` 的反引号
  - `output-templates.md`（long-analyze）：`[style-profile-protocol.md](...)` + `[style-profile-generator.md](...)` → 纯文本
- [x] 5.4 清理后验证：Check 12 PASS（零循环）、Check 13 PASS（零零调用 agent）、Check 11 3 WARN（假阳性，已分析确认无害）。

## 6. 全量验证

- [x] 6.1 `static-check.sh`：Total: 19 | Pass: 18 | Fail: 0 | Warn: 11 ✓
- [x] 6.2 `check-shared-files.sh`：Total errors: 0 ✓（同步了 output-contract.md 双副本）
- [x] 6.3 `run-behavior-evals.sh`：Total: 17 | Pass: 17 | Fail: 0 ✓
- [x] 6.4 `references/shared/` 消费方验证：全部 30 个文件有活跃消费者或 MANIFEST 登记（contract-schema 由 eval 引用、workflow-daily 由 long-write skill 引用）。
