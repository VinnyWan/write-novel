---
name: write-novel-doctor
description: |
  项目诊断与维护。对网文项目做只读体检/诊断，检查目录/文件/依赖/产物完整性；
  同时支持从会话提取成功写作模式并写入项目记忆。
  触发方式：/write-novel-doctor、「体检」「诊断」「检查项目」（旧触发词：/story-doctor）
  合并自：webnovel-doctor + webnovel-learn
allowed-tools: Read Glob Bash
---

# write-novel-doctor：项目诊断与维护

## 两大功能

### A. 项目体检（纯 Markdown 诊断）

只读诊断当前书项目：确认所处阶段应有的目录、文件、依赖是否完整。
**不调用任何脚本，由 agent 直接读取 markdown 文件进行诊断。**

### B. 模式学习

从当前会话提取成功写作模式并写入项目记忆。

---

## A. 项目体检

### 原则

1. 只读诊断：不写项目文件、不自动修复
2. 纯 markdown 方式：agent 直接使用 Read/Glob 检查文件和目录
3. 缺失项按阶段解释影响与修复建议

### 检查项

| 检查项 | 诊断方式 |
|--------|----------|
| 目录结构 | Glob 检查 `设定/` `大纲/` `正文/` `追踪/` 是否存在 |
| 核心文件 | Read 检查 `设定/MASTER_SETTING.md` `追踪/state.md` `追踪/context.md` |
| 章节完整性 | Glob 检查正文章节是否连续，Read 抽查 YAML frontmatter |
| 伏笔状态 | Read `追踪/foreshadowing.md` 检查逾期伏笔 |
| 角色一致性 | Read `追踪/characters.md` 与 Glob `设定/角色/` 交叉验证 |
| 律条合规 | 标记近期章节中未登记实体和设定违反 |
| 模式记忆 | Read `追踪/project_memory.json`（如存在）检查文件完整性、各类条目数、去重有效性 |
| 合约系统 | Read `.story-system/contracts/` 检查合约覆盖率和 commit 连续完整性 |

### 全局健康检查（基础设施层）

除项目体检外，对工具集基础设施做只读巡检：

| 检查项 | 诊断方式 | 修复引导 |
|--------|----------|----------|
| 断链检测 | 运行 `bash scripts/static-check.sh`，读取输出中的 FAIL 项 | 按报告指引修复断链路径 |
| 共享引用指针一致性 | 运行 `bash scripts/check-shared-files.sh`，读取 Pointer/Whitelist/Namespace/Deploy 段错误数 | 指针文件格式错误 → 重新生成指针；命名空间违例 → 运行 `/write-novel-setup` 迁移 |
| hooks 配置完整性 | Read `.claude/settings.local.json` 检查 hooks 注册；Glob `.claude/hooks/*.sh` 检查脚本存在 + 执行权限；Read `.claude/hooks/lib/common.sh` `.claude/hooks/lib/sentinel.sh` 检查 lib 存在 | hooks 缺失 → 运行 `/write-novel-setup` 重新部署 |
| agent 定义完整性 | Glob `.claude/agents/write-novel-*.md` 检查 9 个 agent 文件存在 | agent 缺失 → 运行 `/write-novel-setup` 重新部署 |
| 命名空间一致性 | 检查 `.claude/skills/story-*` 目录是否残留；检查 `.claude/agents/` 下裸名 agent 文件（无 `write-novel-` 前缀的旧文件名）是否残留 | 残留旧命名 → 运行 `/write-novel-setup` 触发 Phase 2.0a 迁移 |
| 部署标记版本 | Read `.story-deployed` 检查 `agents_version` 字段；< 12 → 提示升级 | 版本过旧 → 运行 `/write-novel-setup` 升级到 v12 |

### 自动修复引导

对检测到的问题，给出修复命令或步骤指引：
- 断链/指针错误 → 「运行 `bash scripts/static-check.sh` 查看详情，按报告修复」
- 命名空间残留 → 「运行 `/write-novel-setup` 触发旧命名迁移（Phase 2.0a）」
- hooks/agents 缺失 → 「运行 `/write-novel-setup` 重新部署基础设施」
- 部署标记过旧 → 「运行 `/write-novel-setup` 升级到最新 agents_version」
- 共享源缺失 → 「检查 `references/shared/MANIFEST.yaml`，确认共享源文件存在」

### static-check 输出读取

如 `scripts/` 下存在 static-check 最近运行结果缓存（如 `.story-system/cache/static-check-latest.txt`），优先读取缓存呈现；无缓存时由 agent 直接执行 `bash scripts/static-check.sh` 获取输出。

### 执行

Agent 直接执行以下诊断步骤：
1. Glob 项目目录结构，确认四目录（设定/大纲/正文/追踪）存在
2. Read 核心文件，检查完整性
3. 执行全局健康检查（基础设施层 6 项）
4. 汇总输出阶段感知的诊断报告 + 基础设施健康报告

### 输出

- 阶段感知的诊断报告
- 每项标记：✅ 正常 / ⚠️ 警告 / ❌ 缺失
- 修复建议（由用户确认后手动执行）

---

## B. 模式学习

### 目标

提取可复用的写作模式（钩子/节奏/对话/微兑现/情绪等），追加到项目记忆。

### 执行流程

1. 确定当前项目根目录
2. 读取 `追踪/state.md` 获取当前进度作为上下文
3. 解析用户输入，归类 `pattern_type`：hook/pacing/dialogue/payoff/emotion/format/other
4. 将模式写入 `.claude/memory/` 目录下的对应记忆文件

### 模式类型

| pattern_type | 说明 | 示例 |
|-------------|------|------|
| hook | 钩子设计 | "每章结尾留悬念效果最好" |
| pacing | 节奏控制 | "打斗场景不超过3段，紧张感更集中" |
| dialogue | 对话技巧 | "配角对话带方言口音增强辨识度" |
| payoff | 微兑现 | "第3章提到的暗器在第7章用上" |
| emotion | 情绪把控 | "沈栀的冷淡要逐步破冰，每次推进一小步" |
| format | 格式技巧 | "打斗场景用短句，环境描写用长句" |
| other | 其他 | 无法归类的经验 |
