# Agent 职责边界复核（agent-boundary-review）

> 本文件是 `optimize-write-novel-workflows` 变更 D 组任务 4.5 的产出：复核 8 个 agent 的职责边界，给出结论与建议。
> **本变更不强制执行任何合并/重命名**，仅记录结论供后续决策。

## 复核范围

当前 8 个 agent（`write-novel/agents/`，均带 `write-novel-` 前缀）：

| Agent | 模型 | 实际被引用（skill 文件数） | 角色 |
|-------|------|--------------------------|------|
| write-novel-story-architect | opus→sonnet | 15 | 架构/世界观/大纲/钩子-反转/情绪弧线 |
| write-novel-narrative-writer | sonnet→haiku | 9 | 正文起草 + 去AI味 + 格式合规 |
| write-novel-story-researcher | haiku | 9 | 外部资料研究（CDP 优先）+ 输出带引用参考 |
| write-novel-deconstruction-agent | sonnet→haiku | 8 | 拆文 + 章节提取（含原 chapter-extractor） |
| write-novel-reviewer | haiku | 7 | 多维主观审查 + 多视角（挑剔读者/资深编辑） |
| write-novel-character-designer | sonnet→haiku | 6 | 角色设计/语言风格/对话 |
| write-novel-consistency-checker | haiku | 4 | 客观事实冲突扫描（时间线/战力/地点/伏笔） |
| write-novel-story-explorer | haiku | 4 | 项目内只读结构化查询，返回 JSON |

> 说明：`static-check.sh` 的「zero inbound references」WARN 仅统计 Markdown 链接入边，不统计 `subagent_type:` 调用。上表按 `subagent_type` 实际调用统计，8 个 agent 全部有真实调用者，**无僵尸 agent**。

## 结论一：reviewer ↔ consistency-checker 的「合并自」措辞自相矛盾（需修正措辞，不需合并）

- `write-novel-reviewer` frontmatter 写「合并自：reviewer + **consistency-checker** + picky-reader + senior-editor」。
- 但 `write-novel-consistency-checker` 仍作为独立 agent 存在，且其 frontmatter 明确写「**不与 reviewer 重叠** — reviewer 做多维主观审查，consistency-checker 做客观事实冲突扫描」。
- 二者职责其实**清晰互补**：reviewer = 主观多维 + 多视角；consistency-checker = 确定性 grep/read 事实比对（无 Write/Edit/Bash）。`write-novel-review` 的 full 模式同时调用二者。
- **矛盾点**：reviewer 的「合并自 consistency-checker」是历史措辞残留，与现实（两者并存且分工）冲突，易误导维护者以为可删除 consistency-checker。
- **建议（低风险，下个变更执行）**：把 reviewer frontmatter 的「合并自」一行中的 `consistency-checker` 去掉，改为「与 consistency-checker 分工：本 agent 主观多维审查，事实冲突交由 consistency-checker」。**保留两个 agent。**

## 结论二：story-researcher 的「合并自 story-explorer」措辞自相矛盾（需修正措辞，不需合并）

- `write-novel-story-researcher` frontmatter 写「合并自：story-researcher + data-agent + **story-explorer**」。
- 但 `write-novel-story-explorer` 仍独立存在，二者职责不同：
  - story-explorer：**纯只读、无外网**（disallowedTools: Write/Edit/Bash），从本地项目文件检索，返回结构化 JSON；用于日更上下文加载、审查查设定。
  - story-researcher：**有外网 + 可写**（tools 含 Bash/Write），CDP/WebSearch 抓外部资料，输出带来源引用的参考文件。
- 二者均有真实调用者（各 4 / 9 处），边界清晰：项目内查询 vs 项目外研究。
- **建议（低风险，下个变更执行）**：把 story-researcher 的「合并自」一行去掉 `story-explorer`，改注「与 story-explorer 分工：explorer 查项目内、researcher 查项目外」。**保留两个 agent。**

## 结论三：story-architect 职责偏宽，但不建议拆分

- story-architect 覆盖题材选择 + 世界观 + 大纲 + 钩子/悬念/反转 + 情绪弧线 + 范围控制审查，是被引用最多的 agent（15 处），且为唯一 opus 级。
- 职责虽宽，但全部属于「架构期创作决策」同一认知阶段，调用者高度依赖其一体化输出；拆分会增加 spawn 次数与上下文传递成本。
- **建议**：维持现状，不拆分。

## 结论四：deconstruction-agent 合并 chapter-extractor 是健康合并

- `write-novel-deconstruction-agent` frontmatter「合并自：deconstruction-agent + chapter-extractor」与现实一致（无独立 chapter-extractor 文件残留），被 analyze/import 调用。属正确合并，无需动作。

## 汇总建议

| 项 | 风险 | 是否本变更执行 | 建议时机 |
|----|------|---------------|---------|
| 修正 reviewer frontmatter「合并自」措辞（移除 consistency-checker） | 低 | 否 | 下个文档/措辞变更 |
| 修正 story-researcher frontmatter「合并自」措辞（移除 story-explorer） | 低 | 否 | 下个文档/措辞变更 |
| story-architect 维持不拆分 | — | — | 无需动作 |
| deconstruction-agent 现状 | — | — | 无需动作 |

**总体结论**：8 个 agent 边界实质清晰、各有调用者，无需合并或删除；唯一问题是 reviewer 与 story-researcher 两处 frontmatter 的「合并自」历史措辞与现实矛盾，应在后续变更中修正措辞（非本变更范围）。
