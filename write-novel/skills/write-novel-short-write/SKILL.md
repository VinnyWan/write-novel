---
name: write-novel-short-write
version: 1.0.0
description: |
  短篇网文写作。辅助短篇小说创作，从构思到成稿，聚焦情绪拉扯与节奏把控。
  触发方式：/write-novel-short-write、/写短篇、「帮我写一篇短篇」「写个盐言故事」（旧触发词：/story-short-write）
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# write-novel-short-write：短篇网文写作

你是短篇网文写作执行器。从构思到成稿，完成一篇完整的短篇小说。

**执行规则：短篇以情绪为目标函数，所有内容为情绪服务。**

---

## 执行规则

1. **先定情绪，再定故事**。动笔前必须确定目标情绪（意难平/反转震撼/爽感释放/治愈温暖/细思极恐/共鸣感动），所有内容为这个情绪服务。
2. **一个反转撑一篇**。所有铺垫为反转服务，所有情绪为反转蓄力。不多线、不铺世界观。
3. **每句话必须有用**。不推动剧情、不铺垫反转、不推高情绪的句子 → 删。
4. **开头 3 句定生死，结尾定传播**。开头必须包含钩子，结尾必须有余韵。
5. **默认第一人称**。短篇网文（盐言/黑岩/点众/七猫短篇）绝大多数用第一人称，代入感最强。除非题材明确需要第三人称（如多视角悬疑），否则一律用「我」。

## 核心方法

- **从验证过的模式出发**：有对标书就先拆解，没有就从题材框架（genre-catalog.md）找对应的剧情模式
- **用模块组装**：铺垫段、升级段、反转段各有成熟写法，不要重新发明。参考 genre-writing-formulas.md 对应题材
- **只加载必需信息**：写每节前明确目标情绪和要用的技法，答不出就先回读参考

---

## 格式规范（最高优先级）

详细规则见 `references/format-and-structure.md`，写作前必须加载。**主会话与 narrative-writer 子代理使用同一套正文格式**：正文只允许保存在 `正文.md`，正文段落之间不加空行，对话引号风格按项目/平台约定统一（默认半角双引号，盐言可用「」），短篇小节标记全文统一（默认 `###1.`/`###2.`）。如果子代理输出与主会话格式不一致，按本格式规范重排后再写入文件。

---

## 写作流程

### Phase 1：确定情绪目标

问用户：**「你想让读者读完什么感觉？有没有想写的题材方向或灵感？」**

用户有明确想法 → 直接进入 Phase 2。用户只有模糊想法 → 帮用户做情绪选择：

| 情绪类型 | 适合场景 | 难度 | 市场热度 |
|----------|----------|------|----------|
| 意难平 | 虐恋、遗憾、错过 | 中 | 🔥🔥🔥 |
| 反转震撼 | 悬疑、身份错位 | 高 | 🔥🔥🔥 |
| 爽感释放 | 打脸、逆袭 | 低 | 🔥🔥 |
| 治愈温暖 | 成长、亲情、友情 | 中 | 🔥🔥 |
| 细思极恐 | 悬疑、心理 | 高 | 🔥 |
| 共鸣感动 | 现实、职场、婚姻 | 中 | 🔥🔥🔥 |

### Phase 2：构思核心框架

> 如果用户有参考小说，先用 `/write-novel-analyze` 拆解。默认输出存入项目根目录 `拆文库/{书名}/`；如用户指定当前短篇引用目录，则可输出/同步到 `{短篇标题}/对标/{书名}/`。写作时会自动查找并读取这些拆文结果，不需要用户手动复制到 prompt。

#### 对标上下文加载

> **拆文库/对标关系**：`拆文库/` = analyze skill 的原始产出（数据源），位于项目根目录。`对标/` = 当前短篇的引用视图，位于 `{短篇标题}/对标/`。短篇写作优先读取 `{短篇标题}/对标/{书名}/`，不存在则回退项目根 `拆文库/{书名}/`，再回退 `{短篇标题}/拆文库/{书名}/`（兼容旧结构）。

推荐目录结构：`项目根/拆文库/{书名}/{拆文报告.md, 情节节点.md, 写作手法.md}` + `{短篇标题}/{设定.md, 小节大纲.md, 正文.md, 对标/{书名}/{拆文报告.md, 情节节点.md, 写作手法.md}}`。

如果工作目录下存在 `对标/` 或项目根存在 `拆文库/`，或用户提到参考小说：

1. 按上述顺序查找 `拆文报告.md`、`情节节点.md`、`写作手法.md`
2. 读取核心发现：结构段落、情绪曲线、反转位置、铺垫方式、句式节奏、可借鉴技法
3. 写入本篇 `设定.md` 的"对标摘要"区，写作时每个场景从中召回 1-2 个相关技法
4. 如只找到原文、未找到拆文报告，提示用户先运行 `/write-novel-analyze`；如用户要求继续，也可只按原文做弱参考

> **拆文产出格式**：analyze 落盘的完整文件树、`_meta.json` schema、Stage→文件映射，以及「本 skill 怎么读这些产出」的下游消费规范，见 [references/output-contract.md](references/output-contract.md)。

<!-- cross-book-recall:trigger:structure-positioning -->
> **多对标书时**：参 `references/cross-book-recall.md`，副对标 anchor 入「对标摘要」区

#### Agent 调用：write-novel-story-architect

构思阶段，如果项目已部署 write-novel-story-architect agent（检查 `.claude/agents/write-novel-story-architect.md` 是否存在），可 spawn `Agent(subagent_type: "write-novel:write-novel-story-architect", prompt: "项目目录：{dir}\n任务类型：短篇构思\n查询参数：{情绪目标+题材方向}")` 辅助框架设计。如 agent 不可用，由主线程直接执行。

帮用户确定短篇核心框架（标题/目标字数 8000-20000/平台/情绪目标 + 一句话梗概 + 核心反转含≥3铺垫点 + 情绪设计含反转前1节升温反转后1节维持不骤降 + 人设速写）。框架确定后完成设计任务，然后在工作目录下创建文件。

#### 设计任务（框架确定后执行）

详细步骤和模板见 `references/writing-workflow.md`。构思时从目标情绪反推剧情，不是从灵感正向构建。按顺序完成：

1. 设计结构物件（1-2 个）→ 加载 `writing-craft.md`
2. 设计反派（如有）→ 加载 `villain-and-reveal.md`
3. 确定揭露方式 → 同上
4. 编写 小节大纲.md（格式见 writing-workflow.md）
5. 反转信息差验证（公式见 writing-workflow.md）
6. 伏笔回查清单（标准见 writing-workflow.md）

#### Agent 调用：character-designer

设计任务完成后，如果项目已部署 character-designer agent（检查 `.claude/agents/write-novel-character-designer.md` 是否存在），可 spawn `Agent(subagent_type: "write-novel:write-novel-character-designer", prompt: "项目目录：{dir}\n任务类型：角色设定\n查询参数：{人设速写+关系}")` 辅助角色设定和语言风格档案。如 agent 不可用，由主线程直接执行。

### Phase 3：逐场景写作

**逐场景写作的详细规范见 [references/short-writing-stage-details.md](references/short-writing-stage-details.md)**，含：准备层（记忆+召回/指令确认）、五段结构（开头/铺垫/升级/反转/结尾）、开头结尾技巧表、节长达标与验证流程、字数统计跨平台流程、Phase 3 完成门槛。

#### 关键决策点

- **分批 vs 串行**：正文写作默认由主会话按 2-3 节/批分批写正文，主会话输出是短篇正文的标准形态。不要要求单次 agent spawn 完成 8000+ 字全文。每批写完后先更新"已写小节摘要"（3-5 条：已揭示信息、情绪位置、未回收伏笔、下一批衔接句），下一批必须先读取该摘要和 `正文.md` 尾部 300-500 字再续写。
- **spawn narrative-writer 条件**：只有在用户明确要求子代理、主会话上下文不足，或需要隔离一段试写时，才检查 `.claude/agents/write-novel-narrative-writer.md` 并 spawn `Agent(subagent_type: "write-novel:write-novel-narrative-writer", prompt: "项目目录：{dir}\n任务描述：写正文\n输出文件：正文.md\n情绪目标：{从核心框架读取}\n小节大纲：小节大纲.md\n涉及角色：{从核心框架读取}\n对标/拆文路径：{本次查找到的 对标/{书名}/ 或 拆文库/{书名}/，没有则写 无}\n拆文召回摘要：{本场景最相关的结构/情绪/反转/写作手法模块，最多5条；没有则写 无}\n格式硬约束：必须完全遵守 write-novel-short-write/references/format-and-structure.md；全文小节标记统一，默认 ###1.、###2.；段落之间不加空行；对话独立成行，引号风格按项目/平台约定统一（默认半角双引号，盐言可用「」）；禁止使用 --- 分隔正文片段；禁止把自检/说明/审查报告写入正文.md。\n写作硬约束：按三维度织入写场景，但仍必须按镜头断段；一段只承载一个动作/信息变化，优先一段一句，避免一段到底。输出前做密度重排：段落 >60 字按句号/动作转折拆开，单句 >45 字拆短。")`。无论由谁写作，最终写入 `正文.md` 前都必须按同一格式规范重排一次。

#### 字数硬约束（必须在主文件可见）

- **每节 ≥ 800 字 / 50-65 行**（爽文/打脸/系统流等高信息密度题材可降至 ≥ 500 字/节，不得低于 500 字）
- **整篇总字数 ≥ 8000 字**
- **节数守恒**：正文节数 = 小节大纲规划节数，不得合并/省略
- **字数不足 = 章节未完成**：禁止在字数未达标时结束章节，必须继续展开直到达标
- 字数统计必须跨平台可执行（优先 Python 字符统计，禁止 `wc -c`/模型估算），完整流程见 [references/short-writing-stage-details.md](references/short-writing-stage-details.md)「字数统计跨平台流程」章节

### Phase 4：精修打磨

加载 `references/writing-workflow.md` 中的精修清单完成检查。重点：开头钩子、情绪曲线、反转铺垫、每句话价值、格式规范、AI 腔排查。

#### Agent 调用：narrative-writer（去AI味）+ reviewer

精修阶段，如果项目已部署对应 agent，可 spawn：
- `Agent(subagent_type: "write-novel:write-novel-narrative-writer", prompt: "项目目录：{dir}\n任务描述：去AI味+格式检查\n检查范围：{正文文件}")` — 执行去AI味（6 Gate）和格式合规检查
- `Agent(subagent_type: "write-novel:write-novel-reviewer", prompt: "项目目录：{dir}\n检查范围：{正文文件}\n检查类型：事实冲突+伏笔断线+角色属性不一致")` — 执行一致性检查

如 agent 不可用，由主线程直接执行。

**正文洁净规则**：
- 自检（字数统计、禁用词扫描、格式检查）是过程动作，结果直接在对话里说明，不落盘成文件
- **绝对不能**把自检记录附加到正文文件末尾
- 正文中不得出现任何 `<!-- 自检 -->` 或类似的检查标记注释

不通过 → 回退补足。

---

## 报告输出格式

每次完成写作操作后，必须使用标准化 3 段式报告（详见 `references/shared/report-template.md`），包含：完成状态 + 已生成文件、问题（自动处理/建议检查/必须处理）、下一步可复制命令。禁止向作者暴露内部 JSON 或 traceback。

---

## 流程衔接

**流水线：** 短篇
**位置：** 写作（第 3/3 步）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 有参考小说想对标 | write-novel-analyze | `/write-novel-analyze` |
| 写完，去 AI 味 | write-novel-deslop | `/write-novel-deslop` |
| 想自检 | 本 skill 质量自检 | 用 Phase 4 自检流程 + `references/quality-checklist.md` 逐项核对 |
| 需要市场方向 | write-novel-scan | `/write-novel-scan` |
| 设定太大，适合长篇 | write-novel-long-write | `/write-novel-long-write` |

---

## 参考资料

按需加载以下文件。写作时同时加载 ≤ 3 个：

| 文件 | 何时加载 |
|------|----------|
| [references/format-and-structure.md](references/format-and-structure.md) | 写作前必读 |
| [references/short-writing-stage-details.md](references/short-writing-stage-details.md) | **Phase 3 逐场景写作详解**：五段结构/技巧表/节长验证/字数统计流程 |
| [references/writing-workflow.md](references/writing-workflow.md) | Phase 2 设计任务 + Phase 4 精修 |
| [references/writing-craft.md](references/writing-craft.md) | 写作全程参考 |
| [references/anti-ai-writing.md](references/anti-ai-writing.md) | 去AI味时必读 |
| [references/genre-writing-formulas.md](references/genre-writing-formulas.md) | 核心参考，按题材加载 |
| [references/genre-writing-techniques.md](references/genre-writing-techniques.md) | 通用写作技法+情绪操控+感情线法则 |
| [references/emotional-methods.md](references/emotional-methods.md) | 设计情感时 |
| [references/hooks-chapter.md](references/hooks-chapter.md) | 章节钩子设计 |
| [references/hooks-suspense.md](references/hooks-suspense.md) | 悬念设计 |
| [references/hooks-paragraph.md](references/hooks-paragraph.md) | 段落钩子技巧 |
| [references/villain-and-reveal.md](references/villain-and-reveal.md) | Phase 2 设计反派时 |
| [references/reversal-toolkit.md](references/reversal-toolkit.md) | 设计反转时 |
| [references/emotional-arc-design.md](references/emotional-arc-design.md) | 设计情绪曲线时 |
| [references/quality-checklist.md](references/quality-checklist.md) | 精修检查时 |
| [references/banned-words.md](references/banned-words.md) | 禁用词表 |
| [references/female-audience-writing.md](references/female-audience-writing.md) | 女频写作时 |
| [references/character-basics.md](references/character-basics.md) | 人物基础设定 |
| [references/character-design-methods.md](references/character-design-methods.md) | 人设方法 |
| [references/character-relations.md](references/character-relations.md) | 人物关系设计 |
| [references/dialogue-mastery.md](references/dialogue-mastery.md) | 写对话时 |
| [references/opening-design.md](references/opening-design.md) | 设计开头时（短篇用法：「前3章」读作开篇首节~前1/3，七步法按目标字数等比缩放） |
| [references/genre-catalog.md](references/genre-catalog.md) | 题材框架 |
| [references/genre-core-mechanics.md](references/genre-core-mechanics.md) | 核心梗设计 |
| [references/genre-readers.md](references/genre-readers.md) | 读者心理 |
| [references/state-tracking.md](references/state-tracking.md) | 状态追踪协议（Phase 3 准备层参考） |
| [references/output-contract.md](references/output-contract.md) | Phase 2 对标上下文加载时（理解 analyze 产出格式与消费规范） |

### 按主题快速定位（横切主题）

有些主题散在多个文件里。下表给每个主题一个**权威文件**（先读它，通常够用），配套文件只在需要那个角度时再加载。括号是该文件里对应的小节。

| 主题 | 权威文件（先读） | 配套文件（按角度补充） |
|------|-----------------|----------------------|
| 情绪设计 | **`references/emotional-methods.md`**（情感三板斧 + 拉扯节奏 + 失败模式） | `references/emotional-arc-design.md`（六种弧线 / 前反应-复现-后反应结构）· `references/genre-writing-techniques.md`（情绪操控核心法则） |
| 反转 | **`references/reversal-toolkit.md`**（反转类型 / 铺垫 / 有效性自检） | `references/villain-and-reveal.md`（真相揭露机制 / 反转有效性自检） |
| 反派揭露 | **`references/villain-and-reveal.md`**（反派模板 / 揭露机制 / 报应设计） | `references/reversal-toolkit.md` |
| 人物 | **`references/character-basics.md`**（主角/配角/反派/动机模板速填） | `references/character-design-methods.md`（三层标签反差/深化）· `references/character-relations.md`（关系/感情线） |
| 钩子 | **`references/hooks-chapter.md`**（章节/开篇钩子类型） | `references/hooks-paragraph.md`（段落钩子）· `references/hooks-suspense.md`（悬念设计） |
| 女频写作 | **`references/female-audience-writing.md`**（核心原则 / 文案结构体系 / 感情线写法深化） | `references/genre-writing-techniques.md`（女频读者心理与写作技法 / 感情线四阶段推进法）· `references/genre-readers.md`（读者心理） |
| 题材公式 | **`references/genre-writing-formulas.md`**（各题材创作公式速查） | `references/genre-catalog.md`（题材框架）· `references/genre-core-mechanics.md`（核心梗设计） |
| 开头 | **`references/opening-design.md`**（黄金一章 / 三大基点 / 题材开头模板；短篇：「前3章」读作开篇首节~前1/3、七步法按目标字数等比缩放） | `references/hooks-chapter.md`（开篇钩子类型） |
| 格式与节奏 | **`references/format-and-structure.md`**（正文格式硬规范） | `references/writing-craft.md`（三维度织入）· `references/writing-workflow.md`（设计/精修工作流） |
| 对话 | **`references/dialogue-mastery.md`**（对话技法主文件：差异化/潜台词/对话节奏） | `references/writing-craft.md`（对话权力博弈的结构化用法） |
| 去AI味 | **`references/anti-ai-writing.md`**（AI指纹/核心规则/Show Don't Tell） | `references/banned-words.md`（禁用词扫描）· `references/quality-checklist.md`（成稿检查） |

---

## 语言

- 跟随用户的语言回复，用户用什么语言就用什么语言回复
- 中文回复遵循《中文文案排版指北》
