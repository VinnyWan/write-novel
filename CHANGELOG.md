# 更新日志

这里记录每个正式版本对作者和维护者的影响。发布说明优先面向中文网文作者：先说写作体验有什么变化，再补维护者关心的技术细节。

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
