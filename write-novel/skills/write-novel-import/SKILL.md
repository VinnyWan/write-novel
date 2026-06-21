---
name: write-novel-import
version: 1.0.0
description: |
  逆向导入已有小说。将已写好的小说（半成品或完本）反向解析为标准项目目录结构，
  兼容 write-novel-long-write / write-novel-short-write 后续写作流程。内部复用 write-novel-long-analyze /
  write-novel-analyze 的拆解管道，按篇幅自动分流。
  触发方式：/write-novel-import、「导入小说」「反向解析」「导入」「把我的书导进来」（旧触发词：/story-import）
  合并自：write-novel-import + write-novel-import
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# write-novel-import：逆向导入已有小说

你是小说项目逆向工程师。将用户已有的小说文本（半成品或完本）解析为标准项目目录结构，使其可以无缝接入 write-novel-long-write / write-novel-short-write 的后续写作流程。导入流程按篇幅分流：长篇走长篇路径，短篇走短篇路径。

**核心信念：好的工具不是从零开始，而是从你已有的东西开始。**

**交付物是写作工程**：把作者已有的书重建为可续写的**写作工程**（项目结构 + 拆文库分析资产）。`拆文库/` 是工程的一部分（喂给项目 `对标/`），不是用完即弃的中间产物、也不是交付物本身——交付物是作者能直接续写的项目。

---

## 核心原则

1. **先分析后迁移**：先用拆解管道完整拆解小说（输出到 `拆文库/`），再将分析结果迁移为项目结构。`拆文库/` 是写作工程的一部分（分析资产，喂给项目 `对标/`），保留不丢弃。
2. **复用不重复**：深度分析阶段调用现成的拆解管道，不重新发明——运行 `/write-novel-analyze`（自动按字数分流长/短管道）。拆解方法论与输出模板由 analyze skill 自带，write-novel-import 不执行拆解方法论、不维护这些文件。

---

## Phase 1：确认导入源

问用户：**「你要导入哪本书？请提供文件路径或直接贴文本。」**

### 1.0 确认意图（写作工程 vs 仅拆文库）

默认目标是**完整写作工程**（可续写）。若用户意图不明确，**主动询问**：

> 「你是想把这本书做成可续写的写作工程（设定/大纲/正文/追踪，能接着写第 N+1 章），还是只要一份拆文库分析？」

- 要可续写工程 → 走完整 write-novel-import（Phase 2 拆 + Phase 3 迁移）。
- 只要分析 / 拆文库 → 直接用 `/write-novel-analyze`（短篇 `/write-novel-analyze`），到拆文库为止，不进 Phase 3 迁移。

### 输入方式识别

```
用户提供路径？
├─ 单文件路径（.txt/.md）→ 按章节分隔符自动切分
├─ 目录路径             → 按文件名排序，合并处理
└─ 无路径 → 用户直接贴文本？是→保存临时文件处理；否→提示提供源文件
```

### 基本信息确认

1. **自动检测**：从文本中识别书名（如果有）、总章数、总字数、章节格式
2. **用户确认**：书名、题材类型、目标平台（起点/番茄/晋江/其他）、是否完本、**篇幅类型**（长篇/短篇，按 [references/length-routing.md](references/length-routing.md) 自动检测：用户显式声明 > 结构信号 > 字数兜底，向用户复述请其确认）、**最后一章是否完整**（完整章/残稿；残稿时记入上下文让用户决定「基于残章续写」还是「先补完再导入」，write-novel-import 只记录决定不替用户选）
3. **输出确认**：向用户展示检测到的章节范围、字数、判定的篇幅类型、最后一章状态，确认后开始分析

### 环境检测前置

进入 Phase 2 之前，先检测项目是否已部署 write-novel-setup 基础设施：

- 检测 `.story-deployed` 是否存在；
- 检测 `.claude/agents/write-novel-deconstruction-agent.md` 是否存在（Phase 2 长篇深度分析的并行 agent）。

**未部署时**，提示用户：「检测到当前项目尚未部署写作基础设施。建议先运行 `/write-novel-setup` 再回来导入，否则深度分析阶段无法使用并行 deconstruction-agent agent。」

给用户两个选择：

1. **先去 setup**：暂停导入，运行 `/write-novel-setup`，部署完成后重新触发 `/write-novel-import`；
2. **继续导入**：接受 Phase 2 降级为串行处理（长篇逐章摘要不并行，速度较慢，但产物完整）。

用户选择记入上下文，Phase 2 据此决定是否走并行模式。

### 原文备份

原文备份由 Phase 2 调用的 analyze 拆解管道负责（analyze 管道前置步骤会把原文复制/保存到 `拆文库/{书名}/原文/`）。Phase 1 只需确认源文件就绪，不在此处单独备份，避免与 analyze 管道重复备份逻辑。

---

## Phase 2：深度分析

按 Phase 1 判定的篇幅类型，调用对应 analyze skill 的**完整拆解管道**（真正驱动整条管道跑完，拿到全套结构化产物）。

| 篇幅 | 调用的拆解管道 | 产物目录 |
|------|--------------|---------|
| 长篇 | write-novel-analyze 的长篇管道（Stage 0-6，scope=long） | `拆文库/{书名}/` |
| 短篇 | write-novel-analyze 的短篇管道（Stage 2-6，scope=short） | `拆文库/{书名}/` |

### 调用契约

<!--
  契约说明：write-novel-import 依赖 write-novel-analyze 的「跳过询问」机制
  （对应 write-novel-analyze long scope「Stage 1 停靠点」的「跳过询问的情形」）。
  若 write-novel-analyze 后续重构改动了该机制的触发措辞，需同步检查并更新本契约。
-->

#### 长篇：自动续跑过 Stage 1 停靠点

write-novel-analyze 在 long scope Stage 0+1（黄金三章）后会**自动停靠**并用 AskUserQuestion 询问是否继续全量拆解。但导入场景需要 Stage 2-6 的全套产物——否则 Phase 3 迁移会拿到半成品。

因此调用 write-novel-analyze 时**必须在一开始就以「完整拆解、一次跑完、不要停下询问」模式驱动管道**，命中其「跳过询问」路径。

- 措辞示例：启动深度分析时声明「以『完整拆解、一次跑完、不要停下询问』模式拆解本书」。
- **兜底**：若运行环境实际仍停在 Stage 1 询问处，write-novel-import 自动选择「继续全量拆解」，**绝不把停靠询问透传给用户**。

#### 短篇：单一全量管道

write-novel-analyze 在 short scope 是单一全量拆解管道（Stage 2-6），**无 Stage 1 停靠点**，契约较简单：调用后让其跑完 Stage 2-6 即可，无需声明跳过询问。

### 输出目录

| 篇幅 | 拆文库结构 |
|------|-----------|
| 长篇 | `拆文库/{书名}/{原文/, 概要.md, 章节/{第N章_深度拆解.md, 第N章_摘要.md}, 快速预览.md, 角色/{角色名}.md+角色关系.md, 剧情/{剧情标题}.md+故事线.md+散落情节.md, 设定/{世界观.md, 金手指.md}, 拆文报告.md, 文风.md, _progress.md}` |
| 短篇 | `拆文库/{书名}/{原文/, 拆文报告.md, 情节节点.md, 写作手法.md}` |

### 长篇 6 阶段管道概要

> 管道详细说明见 write-novel-analyze（运行 `/write-novel-analyze`），此处仅列概要。

| 阶段 | 名称 | 输出 | 完成标志 |
|------|------|------|----------|
| 0 | 概要提取 | 概要.md + 章节索引 | 章节结构识别完成 |
| 1 | 黄金三章 | 第1-3章_深度拆解.md → **停靠产出快速预览.md**（导入场景自动续跑，不停下询问） | 3 章拆解完成 |
| 2 | 逐章摘要 | 章节摘要.md（每章3-40情节点，密度150-200字/个）。**并行 deconstruction-agent 模式**（未部署时降级串行）。**计数验证：摘要数 == 章节数** | 所有章节处理完成 |
| 3 | 聚合分析 | 剧情/*.md + 故事线.md。故事框架识别→两步法剧情聚合→角色合并/分级→孤立情节兜底→质量门控（置信度>=0.85/覆盖率85%-95%/重叠率<=35%） | 质量检查通过 |
| 4 | 设定+关系 | 设定/*.md + 角色/*.md。两阶段角色模型 + 别名解析（置信度≥0.85自动合并） | 设定和关系提取完成 |
| 5 | 汇总报告 | 拆文报告.md | 报告生成完成 |
| 6 | 文风 | 文风.md（整书级写作技法视图，write-novel-long-write 日更循环必读） | 文风落盘 `拆文库/{书名}/文风.md` |

### 短篇拆文管道

> 管道详细说明见 write-novel-analyze，此处仅列概要。

短篇为单一全量管道（Stage 2-6 严格串行），产物落盘 `拆文库/{书名}/`：Stage 2 结构+情节节点 → Stage 3 情感线+爆点 → Stage 4 反转+写作手法 → Stage 5 人物+开头结尾 → Stage 6 综合评估，最终汇总为 `拆文报告.md`、`情节节点.md`、`写作手法.md`。

### 分块策略（长篇）

沿用 write-novel-analyze 的分块策略（Stage 2 使用 deconstruction-agent agent 并行）：

| 规模 | 策略 | 块大小 |
|------|------|--------|
| <100 章 | 按阶段整体处理 | 无需分块（50-100 章可选智能分块） |
| 100-500 章 | 按章节分块 | 5-8 章/块 |
| >500 章 | 语义分块：按自然分界切分，无明确分界时按固定章节数均匀切分 | 50-200 章/块 |

### 恢复机制

- 中断时通过进度文件追踪进度；新会话读取进度文件定位断点；从断点所在块的起始章节恢复
- 长篇进度文件格式沿用 write-novel-analyze 拆解管道的进度段落约定（当前阶段、最后处理章节、已完成阶段列表、更新时间）

### 质量门控

长篇阶段 3-4 完成前执行质量检查（置信度 >= 0.85，覆盖率 85%-95%，重叠率 <= 35%），由 write-novel-analyze 拆解管道自带的质量门控负责。短篇质量门控见 write-novel-analyze 各阶段的完成标志。

---

## Phase 3：结构迁移

将 `拆文库/{书名}/` 的分析结果迁移为可被写作 skill 消费的项目结构。

### 分流路由

按 Phase 1 判定的篇幅类型分流，两条路径产出的工程结构完全不同：

| 篇幅 | 迁移路径 | 映射规则 | 续写接手 |
|------|---------|---------|---------|
| 长篇 | **3-L：长篇结构迁移** | [references/structure-mapping-long.md](references/structure-mapping-long.md) | write-novel-long-write 日更循环 |
| 短篇 | **3-S：短篇结构迁移** | [references/structure-mapping-short.md](references/structure-mapping-short.md) | write-novel-short-write Phase 3 逐场景写作 |

### Phase 3-L：长篇结构迁移

**逐步骤迁移规则详见 [references/import-stage-details.md](references/import-stage-details.md)「Phase 3-L」**，含：项目骨架、正文标准化、角色/关系迁移、世界观拆分（两种形态识别）、大纲/卷纲生成、追踪文件四件套（按序生成）、题材定位、文风同步。

**关键决策点**：
- **细纲反推 + 状态重建合并（D4）**：3.6 细纲生成与 3.7③ 角色状态反推合并为**单次 spawn deconstruction-agent**，输出双段 `---` 分隔（上段细纲、下段角色状态），主线程解析支持双段切分 + 单段回退。合并执行细节与解析逻辑见 [references/import-stage-details.md](references/import-stage-details.md)「细纲反推 + 状态重建合并 agent」。`追踪/角色状态.md` 不可遗漏——write-novel-long-write 日更准备层「状态筛选」依赖此文件，缺失会永久走兜底分支长期降级。
- **追踪文件四件套必须按序生成**：伏笔.md → 时间线.md → 角色状态.md → 上下文.md（后一个依赖前一个产出）。
- **卷划分用户确认制**：原文有明确卷界直接划分；无卷界不机械硬切，展示候选方案等用户确认后才写定卷纲。

### Phase 3-S：短篇结构迁移

**逐步骤迁移规则详见 [references/import-stage-details.md](references/import-stage-details.md)「Phase 3-S」**，含：正文迁移（单文件 `正文.md`）、设定生成（核心框架+对标摘要）、小节大纲生成、对标引用视图。

> **短篇工程与长篇完全不同**：短篇正文是单文件 `正文.md`（不切章），**不产** `追踪/`、`大纲/`、`正文/` 等长篇目录。迁移时严禁误建这些长篇专属目录。

### 大型作品处理（>200 章）

仅适用长篇。采用增量导入策略：首期导入前 50 章 + 全书概要 → 后续按需分批导入剩余章节 → 未导入章节生成简化摘要（200 字/章）。详见 [references/import-stage-details.md](references/import-stage-details.md)「大型作品处理」。

---

## Phase 4：项目激活

### 4.1 质量检查

按篇幅对照对应的质量检查清单：

- **长篇**：完整迁移质量清单见 [references/structure-mapping-long.md](references/structure-mapping-long.md) 末尾（含正文文件数对照、主要角色覆盖、`追踪/角色状态.md` 已生成且对齐标准模板、卷划分已经用户确认等）。
- **短篇**：质量清单见 [references/structure-mapping-short.md](references/structure-mapping-short.md) 末尾（含 `正文.md` 单文件存在且格式合规、`设定.md` 含核心框架+对标摘要、未误建长篇专属目录等）。

### 4.2 frontmatter 异步校验（D5）

frontmatter 完整性校验**异步化**，不阻断主流程：

1. **批量导入后扫描**：Phase 3 全部文件落盘后，扫描 `设定/角色/*.md`、`大纲/卷纲_*.md`、`设定/题材定位.md` 等应有 frontmatter 的文件，检查 `name:` 等必需字段是否缺失。
2. **缺失标记 `needs_review`**：缺失字段的文件在 frontmatter 追加 `needs_review: true`（或在导入报告的「待补充项」列出），**不阻断**迁移主流程，不回退已生成产物。
3. **最终报告汇总**：导入完成报告中「待补充项」汇总所有 `needs_review` 文件与缺失字段，提示用户后续补全；frontmatter 完整的文件直接可用。

> 原 import 同步校验每个章节文件 frontmatter、缺失即阻断。改为异步后大书导入不再因个别字段缺失卡顿，用户可在续写前按报告补全。

### 4.3 缺失项提示

输出导入结果摘要和待补充项，按篇幅分支。完成报告模板见 [references/import-stage-details.md](references/import-stage-details.md)「完成报告模板」。

### 4.4 项目激活

- 设置 `.active-book` 指向导入的书名/标题目录
- 确认项目可以被对应写作 skill 识别（长篇 → write-novel-long-write，短篇 → write-novel-short-write）
- 可选验证：如果项目已部署 write-novel-story-researcher agent（检查 `.claude/agents/write-novel-story-researcher.md` 是否存在），可 spawn `Agent(subagent_type: "write-novel:write-novel-story-researcher", prompt: "项目目录：{dir}\n查询类型：progress\n查询参数：导入验证")` 交叉验证迁移数据完整性

> setup 环境检测已在 Phase 1「环境检测前置」完成，此处不再重复检测。

---

## 参考资料索引

按阶段加载，不一次全部加载。本 skill 自带 reference 文件全部位于 `references/`，按场景加载。涉及别的 skill 的方法论/模板时，write-novel-import 不直接加载文件，而是运行对应 `/命令` 由该 skill 自行加载。

| Phase | 场景 | 加载文件 / 相关 skill |
|-------|------|----------------------|
| 1 | 篇幅分流判定 | `references/length-routing.md` |
| 1 | 章节格式识别 | 由 write-novel-analyze 拆解管道的阶段 1 负责 |
| 2 | 长篇深度分析 | 运行 `/write-novel-analyze`（方法论/质量门控/输出模板均自带） |
| 2 | 短篇深度分析 | 运行 `/write-novel-analyze`（方法论/质量门控/输出模板均自带） |
| 3 | 长篇迁移逐步骤 | `references/import-stage-details.md`（Phase 3-L） + `references/structure-mapping-long.md`（映射规则） |
| 3 | 短篇迁移逐步骤 | `references/import-stage-details.md`（Phase 3-S） + `references/structure-mapping-short.md`（映射规则） |
| 3 | 角色状态反推规则（长篇） | `references/character-state-reverse.md` |
| 3 | 角色状态规则（依赖） | `references/state-tracking.md` |
| 3 | 短篇正文格式规范 | `references/format-and-structure.md` |
| 4 | 长篇项目结构规范 | 参见 write-novel-long-write（Phase 4 项目文件结构） |
| 4 | 短篇项目结构规范 | 参见 write-novel-short-write（Phase 3 项目结构） |
| 4 | 环境部署 | 部署模板由 `/write-novel-setup` 提供，write-novel-import 不负责部署 |

> 长篇细纲模板格式参见 write-novel-long-write（Phase 3 细纲部分）；短篇核心框架模板参见 write-novel-short-write（核心框架部分）。这两项为纯文本指引，write-novel-import 不加载对应 skill 的文件。

---

## 报告输出格式

导入完成后，输出标准化 3 段式报告（详见 `references/shared/report-template.md`）：
1. 完成状态：导入章数、生成文件清单、拆解/迁移阶段完成情况
2. 问题：自动处理项（别名合并、低置信度标记）、建议检查项、必须处理项（含 frontmatter `needs_review` 汇总）
3. 下一步：可复制的 `/write-novel-long-write {N}` 或 `/write-novel-short-write {N}` 命令

---

## 流程衔接

**流水线：** 长篇 / 短篇
**位置：** 导入（在开书之前）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 导入完想继续写（长篇） | write-novel-long-write | `/write-novel-long-write` + "日更" |
| 导入完想继续写（短篇） | write-novel-short-write | `/write-novel-short-write` |
| 导入完想审查质量 | write-novel-review | `/write-novel-review` |
| 想深入分析对标 | write-novel-analyze | `/write-novel-analyze` |
| 从零开新书（长篇） | write-novel-long-write | `/write-novel-long-write` + "开书" |
| 从零开新书（短篇） | write-novel-short-write | `/write-novel-short-write` |
| 项目未部署环境 | write-novel-setup | `/write-novel-setup` |

---

## 语言

- 跟随用户的语言回复，用户用什么语言就用什么语言回复
- 中文回复遵循《中文文案排版指北》
