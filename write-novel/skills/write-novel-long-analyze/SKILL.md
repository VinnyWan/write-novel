---
name: write-novel-long-analyze
version: 1.0.0
description: |
  长篇网文拆文。深度拆解爆款长篇小说的黄金三章、人设架构、爽点设计、节奏控制。
  单一深度拆解管道：跑完黄金三章（Stage 1）后产出快速预览报告并询问是否继续全量拆解，
  确认后从 Stage 2 续跑逐章摘要、聚合分析、设定关系、汇总报告，全程产物落盘 `拆文库/{书名}/`。
  触发方式：/write-novel-long-analyze、/长篇拆文、「帮我拆这本书」「拆这本书」「分析黄金三章」
  「深度拆解」「完整拆解」「系统拆解」或提供小说文本文件路径——全部进入同一管道。
  （旧触发词：/story-long-analyze、/write-novel-analyze、「拆文」）
  合并自：write-novel-long-analyze + write-novel-analyze
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# write-novel-long-analyze：长篇网文拆文

你是网络小说结构分析师。

**核心信念：看懂别人的爆款，才能写出自己的爆款。**

---

## 上下文加载（核心三项 + 按需）

启动管道时只读**核心三项**，不预读全部章节摘要与设定——降低启动 token：

1. **进度摘要**：`拆文库/{书名}/_progress.md`（断点 / 已完成阶段 / 章节边界表）。
2. **本阶段计划**：根据断点确定下一 Stage，及其输入文件清单（见各 Stage 入口）。
3. **（仅 Stage 3+ 需要）待回收伏笔**：`拆文库/{书名}/剧情/散落情节.md`、`剧情/*.md`（聚合时校验覆盖率用）。

其余文件在**对应 Stage 入口按需 Read**，不启动时全量预读：

| Stage | 入口按需 Read |
|-------|--------------|
| 0 | 原文（首版 thin first-pass 概要） |
| 1 | Stage 0.5 章节边界表中前 3 章切片 |
| 2 | Stage 0.5 章节边界表中本章切片（每章一个 agent） |
| 3 | 全部 `章节/*_摘要.md`（聚合输入） |
| 4 | Stage 2 情节点 + 章节摘要（4a）；Stage 3 合并后角色数据（4b/4c） |
| 5 | 全部输出（汇总报告 + 全书概要覆盖） |
| 6 | `拆文报告.md` + `章节/第1-3章_深度拆解.md` + `章节/*_摘要.md` + `原文/原文.txt` |

---

## Phase 1：确认拆解对象 + 进入管道

问用户：**「你要拆哪本书？（书名+平台）有原文文件路径吗？」**

如果没有明确目标，按题材或用户想写的类型推荐 2-3 本对标作品。

**统一入口**：确认拆解对象后直接进入拆解管道（Phase 2）。没有快速/深度分叉——只有一条深度拆解管道，跑到 Stage 1（黄金三章）后自动停靠产出快速预览报告。无文本路径时，引导用户提供原文文件路径或直接贴原文，拿到原文后进入管道。

---

## Phase 2：深度拆解管道

### 输出目录

默认输出到 `拆文库/{书名}/`（项目根目录下）。用户指定了其他路径时按用户指定路径输出。

### 管道前置（按需执行，非启动时预读）

| 步骤 | 操作 | 完成标志 |
|------|------|----------|
| **已有分析利用** | 若 `拆文库/{书名}/_progress.md` 存在 → 读断点恢复；若 `角色/*.md`、`设定/*.md` 已存在 → 读作交叉验证基线（新提取信息与之对比，冲突在输出中标注让用户裁定，避免重复提取） | 已有数据已加载为基线 |
| **原文备份** | 若 `拆文库/{书名}/原文/` 不存在 → 从源路径复制（或对话贴文本存为 `原文.md`），验证文件非空且与源一致 | `原文/` 落盘且非空 |

### 输出目录结构

`拆文库/{书名}/` 下：`原文/`（备份）、`概要.md`、`章节/`（第N章_深度拆解.md + 第N章_摘要.md）、`快速预览.md`、`角色/`（{角色名}.md + 角色关系.md）、`剧情/`（{剧情标题}.md + 故事线.md + 散落情节.md）、`设定/`（世界观/{背景设定,力量体系,地理,金手指}.md + 势力/{势力名}.md）、`拆文报告.md`、`文风.md`、`_progress.md`。字段级落盘规则（势力≥200字独立否则并入背景设定等）见 [material-decomposition.md](references/material-decomposition.md)。

> **预留产物（当前不写）**：`剧情/节奏.md`、`剧情/时间线.md` 是 Stage 3 预留输出，**当前管道不产出**——等 write-novel-long-write 日更循环加入对应读取逻辑后再启动。不要把这两份文件当作既有契约。

### 管道主体：Stage 0-6（路由表，执行骨架，保留在主文件）

这是 write-novel-long-analyze 唯一的执行管道。Stage 0-1 跑完后**自动停靠**产出快速预览报告（见下「Stage 1 停靠点」），用户确认后从 Stage 2 续跑。

**预期耗时提示**：开始前根据章节数给用户粗估：<50 章 30-60 分钟；50-200 章 1-3 小时；>200 章可能多轮会话。Stage 2 可并行，但 Stage 3-6 依赖前序产物，按阶段推进。


| 阶段 | 名称 | 输入 | 输出 | 完成标志 |
|------|------|------|------|----------|
| 0 | 概要提取 | 原始文本 | 概要.md（**首版 200 字 thin first-pass** + 章节索引；full plot-aware 500-1000 字版在 Stage 5 落盘覆盖）+ **Stage 0.5 章节边界表写入 `_progress.md`**（详见下方说明） | 章节结构识别完成 + 章节边界落盘 |
| 1 | 黄金三章 | 前3章原文 | 第1章_深度拆解.md / 第2章_深度拆解.md / 第3章_深度拆解.md（每章一个文件）。非人形反派（灵气复苏/末世/国运等抽象对抗型）出现在前三章时，在本阶段一并按抽象对抗型路由分析（核心对抗面/紧迫感来源/升级机制/叙事替代）。 | 3章拆解完成 → **停靠产出快速预览.md** |
| 2 | 逐章摘要 | 分块章节文本 | 章节摘要.md（含情节点+角色）。角色过滤（龙套不提取、别名归类）。每章10-40情节点（密度150-200字/个，按字数动态调节；公式低于10时仍按硬下限10拆足关键步骤）。**并行模式：每章 spawn deconstruction-agent agent**。**计数验证：摘要数 == 章节数，不等则标记失败章节**。 | 所有章节处理完成 |
| 3 | 聚合分析 | 全部章节摘要 | 剧情/*.md + 故事线.md。**故事框架识别**（前置，决定聚合策略）。**两步法剧情聚合**（先从摘要识别剧情大纲，再按大纲分配情节点）。**角色合并**（跨章节去重+别名归一）。**角色分级**（主角/反派/核心配角/功能角色）。**孤立情节兜底**（6步，含覆盖率验证）。**桥段标签**（每个剧情模块按 deconstruction-notes.md 桥段词表打标，best-effort，无匹配留空）。**质量门控**（阈值详见 material-decomposition.md 质量阈值体系）。 | 质量检查通过 |
| 4 | 设定+关系（4a/4b/4c） | **4a**：Stage 2 情节点+章节摘要（不依赖 Stage 3，与 3 并行）；**4b/4c**：Stage 3 合并后角色数据+情节点 | 设定/*.md + 角色/*.md。**4a 设定**（世界观/金手指/势力，从 Stage 2 mention 数据归纳）。**4b 角色完整档案**（两阶段模型：Stage 2 轻量提及 → Stage 4b 完整档案；别名解析置信度≥0.85自动合并）。**4c 角色关系提取**（从情节点提取，不从原文；含演变追踪+最终状态合并+隐含推断）。非人形反派在 4a 做完整抽象对抗型分析。 | 4a/4b/4c 全部完成 |
| 5 | 汇总报告 | 全部输出 | 拆文报告.md（含「写法技巧」清单，覆盖一笔两用/延迟揭示/视角欺骗/对比锚点/行为循环/身体反应替代心理描写/**跨章回扣**——物品/意象在不同章节承担不同功能）+ **概要.md 全书 500-1000 字版**（plot-aware，覆盖 Stage 0 的 200 字 thin first-pass） | 报告 + 全书概要生成完成 |
| 6 | 文风 | 拆文报告.md + 章节/第1-3章_深度拆解.md + 章节/*_摘要.md + 原文/原文.txt | 文风.md（整书级写作技法视图：句长/标点/对话潜台词/情绪交替周期 + 4-6 段原文锚点 few-shot 片段，硬上限 ~4000 字。详见 [style-profile-protocol.md](references/style-profile-protocol.md) + [style-profile-generator.md](references/style-profile-generator.md)） | 文风落盘 `拆文库/{书名}/文风.md` |

### Stage 0.5 章节边界表（Stage 0 子步骤）

Stage 0 完成概要 + 章节索引之后、转入 Stage 1 之前，**必须**产出「章节边界」表写入 `_progress.md`。这是 Stage 1 / Stage 2 / Stage 6 共用的**唯一切片来源**——避免每个阶段各跑一次 regex 切片导致结果不一致。

操作：用 `style-profile-generator.md` Step 4 的章节正则（含 `千`/`两`，覆盖 1000+ 章）grep 全部章节行号 → 按 `| 章号 | 标题 | 起始行 | 字数 |` 四列写入 `_progress.md`「章节边界」section（模板见 [pipeline-ops.md](references/pipeline-ops.md)），顶部 `schema_version: 2` 同时落盘。**旧拆文库续跑兼容**：旧 `_progress.md`（schema v1，无章节边界表）resume 时由 [pipeline-ops.md](references/pipeline-ops.md)「恢复机制操作步骤 0」做 lazy migration，现场重建切片表后正常续跑，不破 `paused_after_stage1` 契约。

### Stage 1 停靠点（保留在主文件）

Stage 0+1 完成后，管道**自动停靠**，产出快速预览报告并询问用户是否继续全量拆解：

1. **生成停靠交付物**：写 `拆文库/{书名}/快速预览.md`（模板见 [output-templates.md](references/output-templates.md)「快速预览报告」）。此时 `概要.md`、`章节/第1-3章_深度拆解.md`、`原文/` 均已落盘。
2. **写停靠状态**：`_progress.md`「最终状态」字段写 `paused_after_stage1`，「断点」段记录「下一操作：Stage 2 逐章摘要」。
3. **询问用户**（AskUserQuestion 风格明确二选一）：
   > 「黄金三章已拆完，快速预览报告见 `快速预览.md`。是否继续全量拆解（Stage 2-6：逐章摘要 / 聚合分析 / 设定关系 / 汇总报告 / 文风）？预计耗时 {基于章节数粗估}。」
   - 选「继续全量拆解」→ 读 `_progress.md`，从 **Stage 2** 续跑，**不重跑 Stage 0/1**。
   - 选「就到这里」→ 管道结束，`_progress.md` 状态保持 `paused_after_stage1`，告知用户「之后可随时 `/write-novel-long-analyze` 同一本书，会自动从 Stage 2 续跑」。
4. **跳过询问的情形**：用户在一开始就明确说「完整拆解 / 一次跑完 / 系统拆解 / 别问」时，仍生成 `快速预览.md`（保留早期判断快照），但**不停下询问**，直接从 Stage 2 续跑到 Stage 6。

### Stage 5 后：选题决策回填（可选）

`拆文报告.md` 出来后（Stage 5 跑完）执行，与 Stage 6 无关，Stage 6 失败也不影响这步。

**仅当**项目根存在 `选题决策.md` 时：按本书题材，在它的推荐选题里找**题材关键词对得上**的那个——
- 正好对上一个 → 把该选题的"能爆的原因"从 `待拆文验证` 改成带出处的支撑：「本书拆解支撑：{`拆文报告.md` 的 写法技巧 Top + 可借鉴套路 + 核心机制 摘要}（`拆文库/{书名}/拆文报告.md`）」。注意还只是假设（只拆了一本，不算坐实）。
- 对上多个 / 拿不准 → 问用户「《{书名}》对应选题决策里的哪个方向？」
- 一个都对不上 / `选题决策.md` 里没有"能爆的原因"这栏（旧模板或文件坏了）→ 直接跳过，不提示。
- 重复拆文不覆盖：只回填还标着 `待拆文验证` 的；已经填过的不动。

没有 `选题决策.md` → 直接跳过，不影响拆文。

### Stage 6 文风

Stage 5 完成后追加 Stage 6，生成 `文风.md`：句长分布、标点习惯、对话潜台词模式、情绪交替周期 + 4-6 段原文 few-shot 片段。

按 [references/style-profile-generator.md](references/style-profile-generator.md) 的 6 步 SOP 跑；模板见 [references/style-profile-protocol.md](references/style-profile-protocol.md)。

原文缺失或章节分隔符识别不出 → 在 `文风.md` 的「生成记录」写明 `文风可用：否：{原因}`。Stage 6 失败不阻断管道。

### Stage 3-4 并行执行图（保留在主文件）

**并行执行图**：
```
Stage 3（剧情聚合 + 角色合并）       ──┐
                                       ├── 4a 与 Stage 3 可并行
Stage 4a（设定：世界观/金手指/势力）  ──┘
              │
              ▼（Stage 3 + 4a 都完成后）
Stage 4b（角色完整档案）— 串行，依赖 Stage 3 合并后的角色实体
              │
              ▼
Stage 4c（角色关系提取）— 串行，依赖 4b 角色实体存在
```

**依赖来源**（事实依据，非投票）：Stage 4b/4c 必须串行——角色完整档案构建依赖 Stage 3「角色合并（跨章节去重+别名归一）」产物（material-decomposition.md「阶段 B」明确依赖 Stage 3 合并实体）。Stage 4a 可与 Stage 3 并行——世界观/金手指字段数据源是 Stage 2 章节摘要 + 情节点，不依赖 Stage 3 输出（见 material-decomposition.md 世界观字段表、金手指合并规则）。

**部分失败容忍**：单章/单阶段失败不阻断管道，记入 `_progress.md`「失败记录」表（`| 类型 | 章节/阶段 | 错误信息 | 重试状态 |`）；最终状态可为 `completed_with_errors`（拆文报告中注明失败详情）。

> 与 material-decomposition.md 的对应关系：Stage 0 含 Material 阶段1（章节解析）；Stage 1、5 为新增；Stage 2 = Material 阶段2；Stage 3 = Material 阶段3；Stage 4 合并 Material 阶段4+5。

详细模板见 [output-templates.md](references/output-templates.md)，方法论见 [material-decomposition.md](references/material-decomposition.md)。

---

## 质量门控概要

Stage 3-4 完成前需通过质量检查（置信度、覆盖率、重叠率）。阈值、计算方式与自检清单的唯一权威定义见 [material-decomposition.md 质量阈值体系](references/material-decomposition.md)。

**Stage 3-5 还须过「事实可溯源」自检**：设定/角色/报告里的硬事实（等级/数值/距离/属性/势力数/出场章/谁说的话）必须能 grep 回原文，原文没给的写「原文未明确」、禁推断填空。详见 [material-decomposition.md 合成阶段事实保真](references/material-decomposition.md)。

---

## Stage 2 并行 Agent 策略

Stage 2 使用 deconstruction-agent agent 并行处理每章，替代原来的串行分块。

**决策点（主文件保留）**：
- **spawn 条件**：`.claude/agents/write-novel-deconstruction-agent.md` 已部署 + 当前不在子代理上下文 → 每章 spawn `Agent(subagent_type: "write-novel-deconstruction-agent")`，每批 5-8 个并发，批次全部完成才进 Stage 3。
- **降级触发**：agent 未部署或环境不支持 spawn 子代理 → 自动退回串行，主线程按 deconstruction-agent 方法论逐章处理（结果同样套 output-templates.md 章节摘要模板，质量不受影响，仅速度变慢）。
- **质量升级重试**：执行失败（crash/超时/空输出）→ 同模型（haiku）重试 1 次；质量失败（agent 10 条自检不达标 / 主线程硬门控 grep 命中）→ `model: "sonnet"` 升级重试 1 次。硬门控含情节点数、`基调：` 全角冒号数量、基调/主题标签枚举校验。
- **最终落盘**：通过即写 `章节/第{N}章_摘要.md` 并标记 `success`（retry 备注模型/方式）；sonnet retry 仍失败 → 标 `⚠️ 跳过`，写入 `_progress.md`「失败记录」表；单章失败不阻断管道。

完整 spawn prompt、硬门控 grep 模式、升级重试调用方式、落盘规则、降级细节见 [references/stage2-agent-strategy.md](references/stage2-agent-strategy.md)。

---

## 分块策略

**路由级说明**：Stage 2 使用 deconstruction-agent agent 按章节并行，**不分块**。

Stage 3-5 的分块策略（规模分级、智能分块、跨块合并、输出长度上限）的唯一权威定义见 [material-decomposition.md](references/material-decomposition.md)。

---

## 恢复机制

1. 管道启动时检查输出目录是否已有 _progress.md
2. 如有，读取断点信息（最后处理章节 + 当前阶段 + 最终状态）
3. **断点状态为 `paused_after_stage1`**（Stage 1 停靠点）→ 跳过 Stage 0/1，直接从 Stage 2 续跑逐章摘要，不重跑已完成的概要与黄金三章。
4. 其他断点状态 → 从断点所在块的起始章节恢复，覆盖该块已有输出。

`_progress.md` 模板与各状态值说明、schema v1 lazy migration 操作步骤见 [pipeline-ops.md](references/pipeline-ops.md)。

---

## 流程衔接

**流水线：** 长篇
**位置：** 拆文（长篇流水线第 2 步，在 write-novel-long-scan 之后、write-novel-long-write 之前）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 准备开写 | write-novel-long-write | `/write-novel-long-write` |
| 需要市场数据 | write-novel-long-scan | `/write-novel-long-scan` |
| 更适合短篇 | write-novel-short-scan → write-novel-short-analyze | `/write-novel-short-scan` |

> **选题决策回填**：若项目根有 `选题决策.md`（write-novel-long-scan 产出），拆完汇总报告（Stage 5 跑完）后会自动回填对应选题的"能爆的原因"（见上「Stage 5 后：选题决策回填」）。

---

## 参考资料

| 文件 | 何时加载 |
|------|----------|
| [references/output-templates.md](references/output-templates.md) | 管道全程：各 Stage 输出模板 + 快速预览报告模板 + 通用速查表 |
| [references/material-decomposition.md](references/material-decomposition.md) | Stage 2-5：素材拆解方法论 + 质量阈值 + 分块策略；Stage 6 另见文风资料 |
| [references/pipeline-ops.md](references/pipeline-ops.md) | 管道运维：_progress.md 模板、错误处理、恢复机制操作步骤 |
| [references/stage2-agent-strategy.md](references/stage2-agent-strategy.md) | Stage 2：deconstruction-agent 完整 spawn prompt、批量策略、硬门控 grep、sonnet 升级重试、降级 |
| [references/deconstruction-notes.md](references/deconstruction-notes.md) | 拆书方法+影视拆解+抽象拆解法+题材实战 |
| [references/style-profile-protocol.md](references/style-profile-protocol.md) | Stage 6：文风模板 + 可信度/可用性说明 |
| [references/style-profile-generator.md](references/style-profile-generator.md) | Stage 6：文风生成 SOP（6 步，含中文数字章节识别 + 全角冒号基调 grep） |

---

## 语言

- 跟随用户的语言回复，用户用什么语言就用什么语言回复
- 中文回复遵循《中文文案排版指北》
