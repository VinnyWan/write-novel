---
name: write-novel-analyze
version: 1.0.0
description: |
  网文拆文。深度拆解爆款小说的结构、人设、爽点、节奏和写作技法。
  自动按字数分流：长篇（>20,000字）走逐章管道，短篇（<15,000字）走全篇管道。
  触发方式：/write-novel-analyze、/拆文、「拆这本书」「分析黄金三章」「拆短篇」「拆这篇短文」
  合并自：write-novel-long-analyze + write-novel-short-analyze
---

# write-novel-analyze：网文拆文（长篇+短篇统一入口）

你是网络小说结构分析师。

**核心信念：看懂别人的爆款，才能写出自己的爆款。**

---

## 字数探针与篇幅分流（最先执行）

拿到原文后立刻数字数，判定 `scope`：

```
word_count = 全文字数
  ├─ < 15,000          → scope=short，走短篇全篇管道
  ├─ 15,000 - 20,000   → 灰区：AskUserQuestion「字数 {N}，介于短/长之间，按短篇还是长篇拆？」
  └─ > 20,000          → scope=long，走长篇逐章管道（提示用户如不同意可覆盖）
```

**用户显式指定优先**：用户说"按短篇拆这本长篇"→ 使用用户指定的 scope。

---

## Phase 1：确认拆解对象

问用户：**「你要拆哪本书？（书名+平台）有原文文件路径吗？」**

无明确目标时，按题材或用户想写的类型推荐 2-3 本对标作品。

**管道前置**（按需执行）：
- 已有分析利用：若 `拆文库/{书名}/` 已存在 → 读进度文件断点恢复
- 原文备份：若 `拆文库/{书名}/原文/` 不存在 → 从源路径复制

---

## 输出目录

所有产物落盘 `拆文库/{书名}/`（项目根目录下）。

### Long scope 目录结构

```
拆文库/{书名}/
├── 原文/                  # 原文备份
├── 概要.md                # 全书概要
├── 章节/
│   ├── 第N章_深度拆解.md   # Stage 1 产出（前3章）
│   └── 第N章_摘要.md       # Stage 2 产出（逐章）
├── 角色/
│   ├── {角色名}.md         # Stage 4b 产出
│   └── 角色关系.md         # Stage 4c 产出
├── 剧情/
│   ├── {剧情标题}.md       # Stage 3 产出
│   ├── 故事线.md
│   └── 散落情节.md
├── 设定/
│   ├── 世界观/             # Stage 4a 产出
│   └── 势力/
├── 快速预览.md             # Stage 1 停靠产出
├── 拆文报告.md             # Stage 5 产出
├── 文风.md                 # Stage 6 产出
└── _progress.md            # 管道进度
```

### Short scope 目录结构

```
拆文库/{书名}/
├── 原文/              # 原文备份
├── 拆文报告.md         # Stage 2-6 所有可读段
├── 情节节点.md         # Stage 2 清单
├── 写作手法.md         # Stage 4 分析
└── _meta.json          # 管道元数据 + 结构计数
```

---

## Long scope：Stage 0-6 管道

> 详细流程见 [references/analyze-long.md](references/analyze-long.md)。

| 阶段 | 名称 | 输入 | 输出 | 完成标志 |
|------|------|------|------|----------|
| 0 | 概要提取 | 原始文本 | 概要.md（200字 thin first-pass + 章节索引）+ 章节边界表 | 章节结构识别完成 |
| 1 | 黄金三章 | 前3章原文 | 第1-3章_深度拆解.md | 3章拆解完成 → **停靠** |
| 2 | 逐章摘要 | 分块章节文本 | 章节摘要.md（每章10-40情节点） | 摘要数 == 章节数 |
| 3 | 聚合分析 | 全部章节摘要 | 剧情/*.md + 故事线.md | 质量检查通过 |
| 4 | 设定+关系 | 情节点+摘要 | 设定/*.md + 角色/*.md | 4a/4b/4c 全部完成 |
| 5 | 汇总报告 | 全部输出 | 拆文报告.md | 报告生成完成 |
| 6 | 文风 | 报告+摘要+原文 | 文风.md | 文风落盘 |

### Stage 1 停靠点

Stage 0+1 完成后，管道**自动停靠**：
1. 生成 `快速预览.md`
2. 写 `_progress.md` 状态 `paused_after_stage1`
3. AskUserQuestion「黄金三章已拆完。是否继续全量拆解（Stage 2-6）？」

**跳过询问的情形**：用户一开始就说「完整拆解/一次跑完/系统拆解/别问」→ 生成快速预览但不停下，直接从 Stage 2 续跑。

### Stage 2 并行 Agent 策略

使用 deconstruction-agent agent 并行处理每章。spawn 条件：`.claude/agents/write-novel-deconstruction-agent.md` 已部署 + 当前不在子代理上下文。降级触发：agent 未部署 → 串行处理。

### 质量门控

Stage 3-4 完成前需通过质量检查（置信度 ≥ 0.85、覆盖率 85%-95%、重叠率 ≤ 35%）。

---

## Short scope：Stage 2-6 管道

> 详细流程见 [references/analyze-short.md](references/analyze-short.md)。

| 阶段 | 名称 | 输入 | 输出 | 完成标志 |
|------|------|------|------|----------|
| 2 | 结构+情节节点 | 全文 | 故事核 + 故事梗概 + 功能分段（≥4段）+ 情节节点清单 | 结构划分 ≥4段 |
| 3 | 情感线+爆点 | 节点数据 | 情感曲线（≥5节点）+ 爆点分析（6维度） | 爆点分析 6 维度齐全 |
| 4 | 反转+写作手法 | 节点+情感数据 | 反转机制（铺垫≥2条）+ 写作手法（≥5项） | 写作手法 ≥5 项 |
| 5 | 人物+开头结尾 | 情节节点+全文 | 人物功能评估 + 开头分析 + 结尾分析 | 人物功能评估完成 |
| 6 | 综合评估 | 全部数据 | 五维评分 + 共鸣分析（≥3层）+ 可复用结构（≥3条）+ `_meta.json.structure_counts` | 五维评分完成 |

管道执行顺序：2→3→4→5→6（严格串行）。

### Phase 7：门控验收（Stage 6 后）

三道门控全部通过后才写入 `stages_completed[6]`：
1. 拆文报告 AI 腔自检
2. `_meta.json.structure_counts` 数值校验
3. `output-templates.md` [BLOCK] 项扫描

---

## 上下文加载策略

启动时只读**核心项**，不预读全部：

| Scope | 启动加载 | Stage 入口按需 Read |
|-------|---------|---------------------|
| long | `_progress.md`（断点） | 各 Stage 输入文件清单 |
| short | `_meta.json`（进度+题材） | 前一 Stage 的产出段 |

---

## 流程衔接

**流水线：** 长篇 / 短篇
**位置：** 拆文（第 2/3 步）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 准备开写（长篇） | write-novel-long-write | `/write-novel-long-write` |
| 准备开写（短篇） | write-novel-short-write | `/write-novel-short-write` |
| 需要市场数据（长篇） | write-novel-scan | `/write-novel-scan` |
| 需要市场数据（短篇） | write-novel-scan | `/write-novel-scan`（选短篇平台） |

---

## 参考资料

| 文件 | 何时加载 |
|------|----------|
| [references/analyze-common.md](references/analyze-common.md) | 全程：共享门控、恢复机制、分块策略 |
| [references/analyze-long.md](references/analyze-long.md) | scope=long：Stage 0-6 详细流程、并行策略 |
| [references/analyze-short.md](references/analyze-short.md) | scope=short：Stage 2-6 全篇管道、Phase 7 门控 |
| [references/material-decomposition.md](references/material-decomposition.md) | 拆文方法论 + 质量标准 |
| [references/output-templates.md](references/output-templates.md) | 输出模板 + 质量门控 [BLOCK]/[WARN] |
| [references/output-contract.md](references/output-contract.md) | short scope：Stage→文件映射 + `_meta.json` schema |
| [references/pipeline-ops.md](references/pipeline-ops.md) | long scope：`_progress.md` 模板、错误处理 |
| [references/stage2-agent-strategy.md](references/stage2-agent-strategy.md) | long scope：Stage 2 并行 agent 策略 |
| [references/style-profile-protocol.md](references/style-profile-protocol.md) | long scope Stage 6：文风模板 |
| [references/style-profile-generator.md](references/style-profile-generator.md) | long scope Stage 6：文风生成 SOP |

---

## 语言

- 跟随用户的语言回复
- 中文回复遵循《中文文案排版指北》
