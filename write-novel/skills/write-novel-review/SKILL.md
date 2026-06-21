---
name: write-novel-review
version: 1.1.0
description: |
  多视角对抗式审查。full/lean 模式在已部署 reviewer agents 时并行 spawn；缺失/异常 agents 或 spawn 失败时自动降级 solo，参考文件不可读时使用内置 rubric fallback。
  触发方式：/write-novel-review、/审查、「审查一下」「帮我审一下」（旧触发词：/story-review）
  合并自：write-novel-review + write-novel-review + webnovel-review
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# write-novel-review：多视角对抗式审查

你是审查协调器。你的职责是找出小说文本中的结构、角色、文字、设定问题，并给出可执行修改建议。

**执行铁律：审查是找问题，不是验证正确性。**

---

## Review Mode 选择

- `/write-novel-review` 或 `/write-novel-review full` → 优先 spawn 全部 5 个 Agent；如果当前已经在子代理内，核心 Agent 未部署/异常，或 spawn 失败，自动降级为 solo。
- `/write-novel-review lean` → 优先 spawn `write-novel-story-architect` + `write-novel-reviewer`；如果当前已经在子代理内，任一所需 Agent 未部署/异常，或 spawn 失败，自动降级为 solo。
- `/write-novel-review solo` → 不 spawn Agent，由当前会话执行基础审查。
- 未指定 → 默认 full，并在报告里写明最终实际执行模式。

---

## Phase 0：预检与降级（必须先执行）

1. **确定请求模式**：解析用户输入中的 `full`、`lean`、`solo`；未指定时目标模式为 `full`。
2. **确认是否允许 spawn**：如果当前已经在子代理/Agent 内执行，不再递归 spawn，直接降级为 `solo`。
3. **检查核心 Agent 部署状态**（只检查项目内 agents，不要假设一定存在）：
   - full 必需：`.claude/agents/write-novel-story-architect.md`、`.claude/agents/write-novel-character-designer.md`、`.claude/agents/write-novel-narrative-writer.md`、`.claude/agents/write-novel-reviewer.md`、`.claude/agents/write-novel-consistency-checker.md`
   - lean 必需：`.claude/agents/write-novel-story-architect.md`、`.claude/agents/write-novel-reviewer.md`
   - 对每个必需 Agent 文件，读取 frontmatter，确认 `name:` 与 subagent_type 完全一致；frontmatter 缺失、不可解析或 name 不匹配时视为 malformed agent。
   - 如果 `.story-deployed` 存在且 `agents_version` 缺失或小于 `10`，视为 stale deployment；不要 spawn，降级 `solo`，建议用户重新运行 `/write-novel-setup`。
   - 如果目标模式所需任一文件缺失或 malformed，**不要尝试 spawn 缺失/异常 Agent**；自动降级为 `solo`，并在报告开头写明：`Fallback: missing agents -> solo` 或 `Fallback: malformed agents -> solo`，列出问题文件，建议用户运行 `/write-novel-setup`。
4. **确认 Agent/Task 工具可用**：如果当前环境没有可用的子 Agent/Task 调用能力，直接降级为 `solo`，报告 `Fallback: agent tool unavailable -> solo`。
5. **运行时失败降级**：如果任何 Agent spawn 返回失败、`subagent_type` 不可用、frontmatter 运行时解析失败或子 Agent 无法启动，停止继续 spawn，改用 `solo` 重新审查，并报告 `Fallback: spawn failed -> solo` 与失败的 subagent_type；不要把部分成功的 Agent 结果当成 full/lean 结论。
6. **确定实际模式**：报告中必须同时列出 `Requested Mode` 与 `Effective Mode`。
7. **禁止把 `.active-book` 当作平台来源**：`.active-book` 只表示当前书名/目录名，不代表目标平台。

---

## 审查基准与参考资料规则（必须遵守）

`write-novel-review` 的核心审查标准必须始终可用。参考文件是增强资料，不是运行前提。

### 报告元数据字段（必须逐字输出）

最终报告开头必须逐行输出以下英文 key，**不要翻译、不要改名、不要只输出中文同义词**。可以在英文 key 后追加中文说明，但 key 本身必须逐字出现：

```md
Requested Mode: full | lean | solo
Effective Mode: full | lean | solo
Fallback: none | missing agents -> solo | malformed agents -> solo | stale agents -> solo | agent tool unavailable -> solo | spawn failed -> solo | subagent recursion guard -> solo
Rubric: fanqie | qidian | zhihu | generic web-fiction
Rubric Source: file | embedded fallback
```

### 参考资料解析顺序

可读取参考文件时，按以下顺序尝试：
1. `{项目根}/.claude/skills/{规范路径}`（项目内安装）
2. `{项目根}/skills/{规范路径}`（本仓库开发环境）
3. 工具自身可访问的全局 skill 搜索路径中同名 `{skill-name}/...` 目录

规范路径如下；禁止只写裸文件名，禁止跨 skill 误读其他 skill 的 references：

| 用途 | 规范路径 |
|---|---|
| 通用质量清单 | `write-novel-review/references/quality-checklist.md` |
| 通用内容评分 rubric | `write-novel-review/references/quality-rubric.md` |
| 去 AI 味方法 | `write-novel-review/references/anti-ai-writing.md` |
| 剧情循环/高潮公式 | `write-novel-review/references/plot-core-methods.md` |
| 角色关系/好感度 | `write-novel-review/references/character-relations.md` |
| 对话质量 | `write-novel-review/references/dialogue-mastery.md` |
| 审查禁用词 | `write-novel-review/references/banned-words.md` |
| 平台 rubric | `write-novel-review/references/rubrics/{fanqie,qidian,zhihu}.md` |
| 标点预检脚本 | `scripts/normalize-punctuation.js`（插件根 scripts/，由 deslop 和 review 共用） |
| Agent spawn 模板 | `write-novel-review/references/reviewer-spawn-templates.md` |

### 内置审查基准包（路径不可读时必用）

如果上述参考文件在当前项目中不可读，**不要把审查降级为无 rubric，也不要在报告里说"无法加载具体 rubric"后停止使用标准**。必须使用本节内置基准包，并报告：`Rubric Source: embedded fallback`。

通用网文内容 rubric：
- 核心卖点：本章是否围绕明确卖点推进；看不出卖点至少 S2。
- 冲突推进：本章是否有阻碍、选择、代价或关系变化；只解释/闲聊/总结至少 S2。
- 情绪曲线：是否有铺垫、升温、释放或反转；情绪平直或突兀至少 S2/S3。
- 钩子与期待：开头或结尾是否制造后续问题；没有悬念或未完成期待至少 S2。
- 角色动机：行为是否符合目标、性格、处境和关系压力；为剧情服务而失真是 S1/S2。
- 对话质量：是否有潜台词、信息控制、角色差异；说明书式对话至少 S2。
- 设定一致性：不违背已写规则、时间线、角色属性；明确事实冲突通常 S1。
- 文字自然度：具体、可感、动作承载信息；AI 腔、陈词滥调、总结体按影响定 S2/S3。
- 格式可读性：段落短、对话独立、无多余空行；格式阻碍阅读按 S3，严重混乱按 S2。
- 最小剧情循环：目标 → 阻碍 → 行动 → 代价/反馈 → 新期待；缺少目标/阻碍/反馈通常至少 S2。
- 高潮构建：蓄能 → 假胜 → 崩解 → 反转/兑现；高潮直接平铺、无代价或无兑现通常 S2/S3。
- 关系/好感度：互动尺度必须匹配当前关系阶段；越界亲密、突然信任、突然敌对都需要铺垫，否则按影响定 S1/S2。
- 伏笔与连载期待：伏笔状态需可追踪；伏笔密度只作为结构风险提示，除非直接造成理解混乱，否则不升级到 S2+。

AI 味 / 禁用词 fallback 速查：
- 高频套话：`命运的齿轮开始转动`、`心猛地一沉`、`眼神复杂`、`深刻变化`、`踏上新的旅程`。
- 章末总结体：`这一切都说明...`、`他终于明白...`、`新的篇章开始了...`。
- 信息倾倒：角色直接说"我要解释世界观/规则/关系变化"。
- 论文体/万能结论：过度使用"然而、与此同时、不可否认、这意味着"。
- 处理原则：有原文证据才输出 finding；给出可执行替换方向，不只评价"AI 味重"。

平台 fallback 摘要：
- 番茄：强开局、强冲突、高频爽点/情绪反馈、低理解门槛。
- 起点：设定自洽、升级路径、长线期待、世界观承载力。
- 知乎盐言：短篇钩子、反转密度、情绪兑现、信息差推进。

### 传给子 Agent 的规则

full/lean 模式下，主会话必须把"审查基准包摘要"直接写进每个 Agent prompt。**不要要求子 Agent 必须读取 `write-novel-review/references/*` 才能完成任务**；子 Agent 可读取 `write-novel-setup/references/agent-references/*` 作为补充，但最终必须遵守本 skill 注入的 rubric 摘要和统一 Findings Schema。

---

## Phase 1：收集待审查内容

1. **确定审查范围**：
   - 用户指定了章节/文件 → 只审查指定内容。
   - 用户未指定 → 优先审查最近修改的正文文件（`git diff --name-only` 中的正文/设定/大纲相关文件），否则审查当前书的当前章节。
2. **范围传递策略**：优先把文件路径、章节名、行号范围传给 reviewer，不整本复制；单文件或短片段可附 300-1200 字关键摘录；多章/整卷/整本审查必须分批，每批输出独立 findings 再综合。
3. **读取相关支撑材料**：正文、相关设定、角色档案、大纲、追踪/上下文、伏笔文件、`.story-system/contracts/chapter_{N}.contract.md`（合约文件，如存在则必须读取）；缺失时在报告中标记证据不足。
4. **识别目标平台并加载 rubric**：
   - 优先使用用户显式指定的平台。
   - 其次读取项目文档里的 `目标平台` / `平台` 字段，例如 `设定/`、`大纲/`、`概要.md`、`项目简介.md`、`拆文报告` 等。
   - 不要把 `.active-book` 当作平台来源；它只能辅助定位当前书名目录。
   - 番茄小说 → 优先读取 `write-novel-review/references/rubrics/fanqie.md`；不可读时使用内置番茄 fallback 摘要。
   - 起点 → 优先读取 `write-novel-review/references/rubrics/qidian.md`；不可读时使用内置起点 fallback 摘要。
   - 知乎盐言 → 优先读取 `write-novel-review/references/rubrics/zhihu.md`；不可读时使用内置知乎 fallback 摘要。
   - 未识别平台 → 优先读取 `write-novel-review/references/quality-rubric.md`；不可读时使用内置通用网文内容 rubric，并报告 `Rubric: generic web-fiction` 与 `Rubric Source: file | embedded fallback`。
5. **形成审查基准包摘要**：把已加载的文件内容或内置 fallback 摘要压缩为 5-12 条审查标准，后续 solo 和子 Agent 都必须使用这份摘要。
6. **确定性标点预检（只报告，不修改）**：当审查范围包含本地正文文件路径时，运行 `node "${CLAUDE_PLUGIN_ROOT}/scripts/normalize-punctuation.js" --check <正文文件...>`，将 `em-dash`、`double-hyphen`、`markdown-divider` 结果作为 `format` 或 `prose` findings 合并进报告。`write-novel-review` 不修改文件；需要自动修复时建议转 `/write-novel-deslop`。默认 `--quote-mode keep`，不把知乎盐言短篇的 `「」` 当作问题。该脚本位于插件根目录 `scripts/normalize-punctuation.js`（`${CLAUDE_PLUGIN_ROOT}/scripts/normalize-punctuation.js`），由 write-novel-deslop 和 write-novel-review 共用。

**Phase 1.5：可选 write-novel-story-researcher 预查询**。仅当 `Effective Mode` 仍为 `full`/`lean`、当前允许 spawn 且 Agent/Task 工具可用时，才可检查 `.claude/agents/write-novel-story-researcher.md` 并 spawn `write-novel-story-researcher` 预查设定摘要；`solo` 或子代理递归保护场景下不得 spawn，只能直接 Read/Grep。此步可选，跳过不影响审查流程。

---

## 统一 Findings Schema（所有模式必须使用）

所有 reviewer（包括 solo）输出问题时必须使用统一结构，方便综合排序。`location` 必须使用工具读取结果显示的原始文件行号；不要删除空行后重新编号。

对 `consistency` / `factual` 类 finding，`fix` 字段只写事实统一方向（例如"统一为左臂旧伤，并同步正文/设定中冲突处"或"需在 A/B 时间线中裁定一个来源"），不要写文学创作建议。

```yaml
- severity: S1 | S2 | S3 | S4
  category: structure | character | prose | consistency | platform | factual | format
  location: 文件路径:行号 或 章节/段落描述
  evidence: "引用原文或具体证据"
  issue: "问题描述"
  fix: "可执行修改建议"
```

严重度定义：
- **S1**：会破坏主线、角色动机、世界规则或读者信任，需优先修。
- **S2**：明显影响章节效果、留存、节奏、人物可信度，建议本轮修。
- **S3**：局部质量问题，如措辞、轻微格式、局部节奏，可排期修。
- **S4**：建议项或风格微调，不阻塞发布。

---

## Phase 2：并行 Spawn Agent（full/lean 模式）

使用 Agent 工具并行调用。每个 Agent 不继承父对话上下文，prompt 必须自包含。

**调度决策点**：
- 执行 Phase 0 后，只有实际模式仍是 full/lean 时才 spawn。不要 spawn 缺失 Agent。
- **full 模式**：并行 spawn 全部 5 个 Agent（story-architect、character-designer、narrative-writer、reviewer、consistency-checker）
- **lean 模式**：只 spawn story-architect + reviewer
- **上下文传递（D6）**：prompt 不嵌入完整角色/伏笔/设定列表，只传「项目目录 + 共享路径 + 审查基准包摘要（必须内联）」，Agent 自行 Read 设定/大纲/角色/合约文件。

**每个 Agent 的完整 spawn prompt 模板**（含检查项、输出格式、subagent_type）详见 [references/reviewer-spawn-templates.md](references/reviewer-spawn-templates.md)。调度顺序：

| # | subagent_type | full | lean | 视角 |
|---|---|---|---|---|
| 1 | write-novel-story-architect | ✓ | ✓ | 主题/大纲/钩子反转/范围/平台 |
| 2 | write-novel-character-designer | ✓ | — | 角色/对话/人物弧线/关系 |
| 3 | write-novel-narrative-writer | ✓ | — | AI味/格式/节奏/文字自然度 |
| 4 | write-novel-reviewer | ✓ | ✓ | 事实冲突/合约合规（grep-first） |
| 5 | write-novel-consistency-checker | ✓ | — | 时间线/战力/地点/伏笔/知识边界 |

任一必需 Agent 缺失/malformed/stale/spawn 失败 → 按 Phase 0 降级 solo，不把部分成功当 full/lean 结论。

---

## Phase 3：综合裁决

1. 收集实际执行的 reviewer VERDICT 和 FINDINGS。
2. 合并去重：按 `severity` 排序（S1 > S2 > S3 > S4），同级内按影响范围排序。
3. **可选事实核查**：如果审查内容涉及需要验证的外部事实（历史年代、地理方位、职业细节等），只有在 `Effective Mode` 仍为 `full`/`lean`、当前不是子 Agent、Agent/Task 工具可用且 `.claude/agents/write-novel-story-researcher.md` 已部署时，才可额外 spawn `write-novel-story-researcher` 搜索验证；`solo`、missing/malformed/stale/spawn failed 降级或子代理递归保护场景下不得 spawn，只能在报告中标记"需人工事实核查"。
4. **分歧呈现**：如果 reviewer 间有冲突意见，明确呈现分歧让用户裁决；不要自动妥协。
5. 输出综合审查报告。报告必须列出实际模式、fallback 原因、使用的 rubric、Rubric Source、审查范围和证据不足项。

---

## Phase 4：输出报告

只有 `Effective Mode` 确实为 `full` 或 `lean` 时才使用 full/lean 模板；如果 Phase 0 或运行时失败导致降级 `solo`，必须改用 solo 模式模板。

注意：下列 `Requested Mode`、`Effective Mode`、`Fallback`、`Rubric`、`Rubric Source` 五个英文 key 必须逐字保留；不要改成"请求模式/实际模式/回退/评估标准"等中文 key。

### full / lean 模式输出格式

```md
=== 故事审查报告 ===
Requested Mode: full | lean
Effective Mode: full | lean
Fallback: none
Rubric: fanqie | qidian | zhihu | generic web-fiction
Rubric Source: file | embedded fallback
审查范围: {章节/文件/批次}

## Verdict Summary / 结论汇总
- write-novel-story-architect: APPROVE / CONCERNS(n) / REJECT / NOT_RUN
- write-novel-character-designer: APPROVE / CONCERNS(n) / REJECT / NOT_RUN
- write-novel-narrative-writer: APPROVE / CONCERNS(n) / REJECT / NOT_RUN
- write-novel-reviewer: APPROVE / CONCERNS(n) / REJECT / NOT_RUN
- write-novel-consistency-checker: APPROVE / CONCERNS(n) / REJECT / NOT_RUN

> `NOT_RUN` 只用于 lean 模式排除的 reviewer 或可选 reviewer（character-designer、narrative-writer、consistency-checker）；如果 full/lean 必需 reviewer 缺失或 spawn 失败，应降级 solo，而不是在 full/lean 报告中标记 NOT_RUN 后继续综合。

## Severity Counts
- S1: n / S2: n / S3: n / S4: n

## 综合评定
APPROVE(通过) / CONCERNS(有问题) / REJECT(需重写)

## 发现的问题
{按统一 Findings Schema 或等价表格列出所有问题}

## Agent 分歧（如有）
{列出 reviewer 间不同意见和证据}

## 证据不足 / 需补充
{缺失设定、缺失大纲、无法核查事实等}

## 修改建议
{按 S1→S4 优先级排列}
```

### solo 模式

不 spawn Agent。先按 Phase 1 第 4 步识别目标平台并加载对应 rubric；即使是 solo，也必须用平台 rubric、`write-novel-review/references/quality-rubric.md` 或内置审查基准包校准判断。

solo 必须执行基础检查：
1. 格式合规性检查（一段一句、无空行、对话格式、段落过长）。
2. 简单的设定一致性 grep（角色名、属性、关键设定、伏笔关键词）。
3. AI 味与禁用词检查（优先读取 `write-novel-review/references/banned-words.md` 与 `write-novel-review/references/anti-ai-writing.md`，不可读时使用内置 AI 味 / 禁用词 fallback 速查）。
4. 通用网文内容评分（优先读取 `write-novel-review/references/quality-rubric.md`，不可读时使用内置通用网文内容 rubric）。
5. **钩子密度与类型分布检测**：统计本章钩子数量，对照 `write-novel-long-write/references/hooks-taxonomy.md` 五分类法，检查：钩子密度是否达标（章首 1 + 章尾 1 + 文中每 1000 字至少 1 微钩子）、连续两章主分类是否重复、题材偏好配比是否偏离（±15% 标记 S3）。hooks-taxonomy.md 不可读时使用内置五分类定义（危机/悬念/欲望/情绪/选择）做基本判断。
6. **线索约束检查**：对照 `write-novel-long-write/references/strand-weave-rhythm.md`，检查 Fire 连续≤2章、Constellation 连续≤1章、任意5章窗口至少2种线索。strand-weave-rhythm.md 不可读时使用内置规则（Fire≤2、Constellation≤1）做基本判断。
7. 按统一 Findings Schema 输出简化版报告。

### solo 模式输出格式

```md
=== 故事审查报告（solo）===
Requested Mode: {full | lean | solo}
Effective Mode: solo
Fallback: none | missing agents -> solo | malformed agents -> solo | stale agents -> solo | agent tool unavailable -> solo | spawn failed -> solo | subagent recursion guard -> solo
Rubric: fanqie | qidian | zhihu | generic web-fiction
Rubric Source: file | embedded fallback
审查范围: {章节/文件}

## 基础检查结果

### 格式合规性
- [{x| }] 段落 ≤60 字：通过/不通过；证据：...
- [{x| }] 无段间空行：通过/不通过；证据：...
- [{x| }] 对话独立成行：通过/不通过；证据：...
- 违规位置：{列出}

> checklist 约定：`[x]` 只表示通过，`[ ]` 表示未通过；不得出现"`[x] ... 不通过`"这种矛盾写法。

### 设定一致性（grep 扫描）
- {列出发现的矛盾或证据不足}

### AI 味 / 禁用词
- {列出问题，必须附 evidence}

### 钩子密度与类型分布
- 章首钩子：{有/无}，类型：{危机/悬念/欲望/情绪/选择}
- 章尾钩子：{有/无}，类型：{危机/悬念/欲望/情绪/选择}
- 文中微钩子密度：{每1000字 N 个}，达标/未达标
- 连续章类型重复：{是/否}
- 题材偏好配比偏离：{无/S3标记}

### Findings
{按统一 Findings Schema 或等价表格列出，severity 必须是 S1/S2/S3/S4}

### 修改建议
{按优先级排列}
```

---

## 报告输出格式

审查报告可保留现有结构（Verdict Summary + Findings + 修改建议），但结尾必须追加标准化 3 段摘要（详见 `references/shared/report-template.md`），包含：完成状态、问题严重度汇总（S1/S2/S3/S4 分布 + 阻断/高优/中低优）、下一步命令。solo 模式输出已基本兼容，仅需在结尾补"下一步"命令块。

---

## 流程衔接

**流水线：** 通用
**位置：** 审查（写作之后）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 要修改查出的问题 | write-novel-long-write / write-novel-short-write | 返回对应写作 skill 修改 |
| 发现 AI 味需清理 | write-novel-deslop | `/write-novel-deslop` |
| 需要重新拆解对标书 | write-novel-analyze | `/write-novel-analyze` |

---

## 语言

- 跟随用户的语言回复，用户用什么语言就用什么语言回复。
- 中文回复遵循《中文文案排版指北》。
