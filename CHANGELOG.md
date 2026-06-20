# 更新日志

这里记录每个正式版本对作者和维护者的影响。发布说明优先面向中文网文作者：先说写作体验有什么变化，再补维护者关心的技术细节。

## v2.3.0 (2026-06-20) — 文档清理 + 静态检查盲区补齐 + Skill 流程瘦身

### 变更

- **写作体验**：
  - **Skill 流程瘦身**（9 个 skill 合并/外移冗余步骤）：
    - **deslop**：六道 Gate 流程外移，主 SKILL.md 从 236 行精简为核心调度逻辑
    - **short-write**：写作流程外移，上下文按需加载
    - **review**：4 个 spawn 模板从 SKILL.md 移到 references/，上下文从内嵌改路径引用
    - **import**：细纲反推 + 状态重建双阶段合并，frontmatter 校验从同步改异步
    - **setup**：交互流程瘦身，每 Phase 写入 run-ledger 断点
    - **long-analyze**：上下文加载路径精简，按阶段按需读取
    - **short-analyze**：加载步骤精简，上下文路径对齐
    - **long-scan**：采集 + 趋势合并为一个通过式流程，报告按需读取
    - **short-scan**：合并策略对齐长扫描，共享趋势/偏好路径
  - **文档清理**：移除 `references/shared/` 下 14 个零引用文件（4 个 v0.3 死文档删除 + 6 个未接线规范归档至 `references/archive/` + 5 个错误案例样本归入 `references/rules/`），确保 shared 目录每个文件都有明确消费者
  - **CLAUDE.md 表述修正**：「不存在 CLI 脚本」更正为「脚本仅做确定性自动化」，与现实 13 个校验/统计 `.py` 对齐

- **稳定性与可维护性**：
  - **静态检查扩展 Check 10**：新增 `references/shared/` 引用完整性校验（wikilink + 路径悬空检测），修复此前只扫 per-skill references 的盲区
  - **版本一致性**：plugin.json / marketplace.json / CHANGELOG 三处版本号对齐至 v2.3.0

## v2.2.0 (2026-06-19) — 竞品加固：静态检查链 + 声明式上下文治理 + CI

### 变更

- **写作体验**：
  - **钩子议程字段**：细纲 frontmatter 新增可选字段 `must_advance_hooks`（本章必须推进的伏笔）与 `eligible_resolve_hooks`（可回收的伏笔）。写前自动把这些伏笔状态提到记忆包顶部，写后逐条核对是否真的推进——承诺推进却没动会被标为「必须处理」，避免长篇后期伏笔越积越多。既有细纲无此字段时自动跳过，不影响在写项目。
  - **长文件受控截断**：加载 400-700 行的大参考文件时保留头尾、中段显式标注省略了哪些小节，不再让你误把截断内容当全文。需要某小节时按标题定向补读。
  - **按章状态快照**：每章写完存一份状态副本到 `追踪/快照/chapter_{N}.state.md`，发现后面写歪了可按章回滚到任一断点重写。
- **稳定性与可维护性**：
  - **静态检查链**：新增 4 个发版前守护脚本（SKILL 结构与 references 断链、跨 skill 共享文件一致性、裸 python3 调用、跨平台字数统计），按 skill-local 三级解析规则消除历史「90 处断链」误报。
  - **结构化错误目录 + 作者术语表**：12 条已知失败模式（写前/写后自检未过、钩子议程未履行、字数不达标、伏笔逾期等）统一登记到 `author_error_catalog.json`，报告层按 code 查可读文案，不再向作者暴露内部 JSON。
  - **行为 eval 契约 + CI**：17 条可验证断言（frontmatter/契约短语/执行顺序/schema/错误目录覆盖/链接完整性）+ `.github/workflows/plugin-check.yml`，push 与 PR 自动跑全链，本地可复现无需 secrets。
  - **补建缺失 agent 模板**：story-setup 声称部署 9 个 agent 但模板仅 7 个，补齐 deconstruction-agent 与 reviewer。
  - **版本一致性校验**：plugin.json / marketplace.json / CHANGELOG 三处版本号对齐（修复 marketplace.json 滞留 2.0.0）。

## v2.1.0 (2026-06-17) — 竞品分析补齐 + 自有市场双通道分发

### 变更

- **Agent 体系扩展**：从 6 个扩展到 9 个专业 Agent（新增 consistency-checker、story-explorer、chapter-extractor）
- **Hooks 强化**：从 6 个扩展到 10 个 hook（新增 guard-outline-before-prose 阻断式大纲守护、detect-story-gaps 缺口检测、pre-compact/post-compact 上下文保护）
- **知识体系补齐**：新增 8 个方法论文件（段落钩子、商业化方法、女频写作、反转工具箱、风格模块、高级技法、跨书召回）
- **Python 辅助脚本层**：新增 5 个可选 Python 脚本（精确字符统计、禁词扫描、frontmatter 校验、元数据提取、项目状态快照）
- **新增 browser-cdp skill**：通过 CDP 协议复用浏览器登录态采集榜单数据
- **Dashboard 增强**：新增实体关系图、伏笔状态面板、追读力仪表盘组件规划
- **Write-Gate 系统**：单章写入前/中/后三阶段校验门禁
- **插件目录恢复子目录结构**：插件组件（skills/、agents/、hooks/ 等）移回 `write-novel/` 子目录，仓库根只保留市场和文档
- **新增自有市场清单**：`.claude-plugin/marketplace.json`，用户可通过 `claude plugin marketplace add VinnyWan/write-novel` 添加
- **README 更新**：新增自有市场安装方式，补充市场 badge
- **安装方式双通道**：自有市场（推荐）+ 社区市场

### 迁移指南

从 v2.0.0 升级：
1. 更新仓库：`git pull`
2. 已部署项目需重新运行 `/story-setup` 以获取新 Agent 和 Hook
3. Python 脚本为可选依赖，无 Python 环境时自动降级 AI 校验

## v2.0.0 (2026-06-16) — 插件化重构，支持市场分发

### 重大变更（BREAKING）

- **插件目录重组**：所有插件内容从 `write-novel/` 子目录移至仓库根目录，符合 Claude Code 官方插件规范
- **manifest 标准化**：`.claude-plugin/plugin.json` 重写为官方 schema，移除旧版非标准字段（`commands`、`skills`、`agents`、`files`、`compatibility`）
- **Skill 命名空间**：skills 现在以插件命名空间为前缀（`/write-novel:story` 而非 `/story`）

### 迁移指南

如果你从 v0.3.0 升级：
1. 更新仓库：`git pull`
2. 以插件模式加载：`claude --plugin-dir .`（而非依赖 `.claude/` 配置）
3. Skill 触发词变化：`/story` → `/write-novel:story`，`/story-deslop` → `/write-novel:story-deslop`，以此类推
4. 删除旧 `write-novel/` 目录（如果 git pull 未自动清理）

### 开发者变更

- 目录结构：`skills/`、`agents/`、`hooks/`、`references/`、`templates/`、`scripts/` 均在仓库根目录
- `write-novel/` 包装目录已删除
- `.claude/` 保留为项目本地工作区配置（不影响插件功能）
- 所有 14 个 skills、6 个 agents、7 个 hooks 功能不变，仅路径变更

## v0.3.0 (2026-06-13) — Skill/Agent 架构统一与故事系统 Markdown 化

### 新增
- **故事系统 Markdown 化**：Contract（设定→卷→章三层 YAML frontmatter 契约）→ Commit（正文 frontmatter 元数据）→ Projection（追踪/ 派生数据），详见 `story-long-write/references/story-system.md`
- **三阶段写门校验**：Prewrite（写前爽点密度/线索冲突/伏笔逾期检测）→ Precommit（字数/contract_nodes/hook/去AI味）→ Postcommit（投影更新/ledger/strand 计数），详见 `story-long-write/references/write-gates.md`
- **钩子五分类法**：危机/悬念/欲望/情绪/选择钩 + 分题材偏好参数，详见 `story-long-write/references/hooks-taxonomy.md`
- **读者债务追踪**：`追踪/foreshadowing.md` 完整模板字段（计划回收章/实际回收章/逾期标记），详见 `story-long-write/references/reader-debt-tracking.md`
- **三线叙事节奏**：Quest（主线）/ Fire（支线）/ Constellation（伏笔）标注体系 + 连续/间隔约束规则，详见 `story-long-write/references/strand-weave-rhythm.md`
- **去AI味六关检测体系**：A（禁词）/ B（句式）/ C（心理外化）/ D（节奏）/ E（对话）/ F（结尾）+ 三级强度控制，详见 `story-deslop/references/deai-six-gates.md`
- **去AI味自动检测脚本**：`scripts/deai_check.py`，支持 `--json` 和 `--intensity`，自动化 A/B/D 关
- **断点续传**：`追踪/run-ledger.md` 操作日志 + 断点诊断与智能恢复流程，详见 `story-long-write/references/checkpoint-resume.md`
- 端到端验证 checklist：`openspec/changes/absorb-competitor-advantages/validation-checklist.md`

### 变更
- **Skill 合并**：31 个 skill → 15 个规范 skill（`story-*` 统一命名空间）
  - story + write-novel → story（路由入口）
  - story-setup + write-novel-setup + webnovel-init → story-setup
  - story-long-write + write-novel-long-write + write-novel-plan + webnovel-plan + webnovel-write → story-long-write
  - 等 12 组合并（详见 tasks.md Phase 2）
- **Agent 合并**：15 个 agent → 6 个规范 agent
  - context-agent → story-architect
  - chapter-extractor → deconstruction-agent
  - consistency-checker → reviewer
  - story-explorer + data-agent → story-researcher
  - 所有 agent 标注模型分配（Opus/Sonnet/Haiku）和降级路径
- **旧触发词兼容**：所有 `/write-novel-*`、`/webnovel-*` 作为别名保留在路由表中
- **模板 agent 更新**：story-setup 部署模板的 frontmatter name 与规范 agent 名称统一
- README.md 全面更新为 v0.3.0 架构说明
- UPGRADING.md 新增 v11 条目

### 删除
- 19 个旧 skill 目录（write-novel-* / webnovel-*，已合并到 story-*）
- 9 个旧 agent 文件（已合并到 6 个规范 agent）

### 设计决策
- **Skill > Script**：后续功能优先使用 SKILL.md + references 文档驱动，脚本仅做确定性自动化
- **Contract → Commit → Projection**：三层 Markdown 契约链替代旧的 ad-hoc 文件结构

## v0.2.0 (2026-06-12) — 目录整合与竞品优势注入

### 新增
- 根目录文档层补齐（CHANGELOG、LICENSE、pytest.ini、sitecustomize.py、requirements.txt、releases/）
- docs/ 扩展为 7 个子目录（architecture/archive/guides/memory/operations/research/superpowers）
- 新增 evals/ 行为评估模块（从 webnovel-writer 移植）
- 新增 hooks/ 自动化体系（7 hooks：session_start/end、pre/post_compact、guard_runtime_write、detect_story_gaps、validate_story_commit）
- 新增 templates/ 题材模板模块（37 题材 + 输出模板）
- 新增短篇写作 skill（write-novel-short-write）
- 新增短篇拆文 skill（write-novel-short-analyze）
- 新增学习 skill（webnovel-learn）+ Dashboard skill（webnovel-dashboard）
- 项目文件结构升级为四维分离 + 对标联动 + 分层追踪
- Dashboard 注入 React 前端 + watcher + server
- references 方法论扩充（oh-story 25 方法论 + 4 rules）

### 变更
- skills 三方全量合并（当前 11 + webnovel 8 + oh-story 12 → 31 个目录）
- agents 三方合并（当前 7 + webnovel 4 + oh-story 7 → 15 个，按 Opus/Sonnet/Haiku 三级分工）
- scripts 三方整合（webnovel 25 独有脚本 + oh-story 6 校验脚本）
- 项目初始化模板更新（`世界设定/`+`人物/` → `设定/`，`分卷大纲/` → `大纲/`，`章节草稿/` → `正文/`，新增 `对标/`+`追踪/`）
- init/doctor/dashboard 脚本适配新目录结构
- README.md 同步更新所有模块说明

### 来源
- webnovel-writer v6.2.0
- oh-story-claudecode

---

## v6.2.0 - 写章结果更清楚，失败后更好恢复

发版范围：`v6.1.0..v6.2.0`。

### 给作者看的变化

- 写章、审查、规划和初始化结束后，最终报告更像写作助手的汇报：会说明已完成、部分完成、需要你处理或未完成。
- `/webnovel-write` 中断后，重复执行同一章会优先检查可信断点，尽量从失败位置继续，减少重写和误覆盖。
- 写章过程减少技术细节打扰；只有创作方向、事实取舍、文件覆盖风险或阻断问题需要裁决时才询问。
- 写作流程的上下文读取更克制，初始化、规划、写章、审查、查询等命令更聚焦，减少无关资料塞满上下文。
- 章节提交前后的中间结果校验更稳，能更早发现缺失的审查、事实提取或故事资料同步结果。
- 文档补充了最终报告读法、恢复边界、日志用途和常见运维入口。

### 是否需要改旧项目

不需要。已有书项目可以继续使用，不需要迁移 `.story-system/` 或 `.webnovel/` 数据。

### 给维护者

- 新增作者术语表、异常目录、审查作者视图、最终报告 helper、写章 run ledger、脱敏 run log。
- 新增 `user-report`、`run-ledger`、`run-log` 统一 CLI 子命令。
- 收紧 commit artifacts、projection writers、write-gate 和 postcommit 的结构化校验。
- 轻量化多个 Skill / Agent 的提示词，补充 reference loading map 和 region-read 规则。
- 增加 prompt integrity、unit tests、behavior eval，覆盖 artifact ownership、最小写章模式、projection retry、blocking review、断点续跑和日志脱敏。
- `Plugin Release` 工作流改为推送到 `master` 后自动发版，并保留手动兜底入口。

### 验证

- 相关 pytest 通过。
- behavior eval 通过。
- `compileall` 通过。
- `git diff --check` 通过。
- 版本同步和插件包校验通过。

## v6.1.0 - 项目体检更稳，出问题更容易定位

- 增加 doctor、project-status、write-gate、projection 重放、hooks、行为评估和插件包校验。
- 强化 Story System 运行时健康检查和 Marketplace 发布校验。

## v6.0.0 - Story System 主链上线，长篇事实更不容易写乱

- 上线合同种子、运行时合同、章节提交、事件审计和投影链路。
- 补齐主链相关集成测试。
