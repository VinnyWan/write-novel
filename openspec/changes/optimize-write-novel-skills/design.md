## Context

当前 15 个 write-novel skill 中有 4 对 long/short 变体。经过逐 skill 对比分析：

| 对 | 结构重合度 | 核心差异 | 合并建议 |
|---|---|---|---|
| long-scan ↔ short-scan | ~70% | 平台列表、分析维度（情绪 vs 题材）、选题输出格式 | **合并** |
| long-analyze ↔ short-analyze | ~60% | Stage 粒度（逐章 vs 全篇）、产出目录结构 | **合并** |
| long-write ↔ short-write | ~40% | 文件结构（章节目录 vs 单文件）、Phase 数（5 vs 4）、追踪体系 | 不合并 |
| review ↔ deslop | ~15% | 审查是多维审查，deslop 是专项去 AI 味 | 不合并 |

合并后从 15 减至 13 个 skill。合并对象为 scan 对和 analyze 对。

## Goals / Non-Goals

**Goals:**
- 将 long-scan + short-scan 合并为单一 `write-novel-scan` skill，内部按平台/篇幅分流
- 将 long-analyze + short-analyze 合并为单一 `write-novel-analyze` skill，内部按字数/结构分流
- 保留旧命令别名至少一个版本（`/write-novel-long-scan` → `/write-novel-scan --long` 等）
- 更新路由器（write-novel）的路由表和下游 skill 的流程衔接表
- 合并后每个 skill 的 SKILL.md 控制在 500 行以内

**Non-Goals:**
- 不合并 long-write 和 short-write（文件结构/流程差异过大）
- 不合并 review 和 deslop（功能正交）
- 不修改各 skill 对外行为（用户感知的功能不变）
- 不迁移旧项目中的 `.claude/skills/story-*` 等历史遗留路径
- 不修改 agent 定义

## Decisions

### D1: 统一 skill 内部用「篇幅参数 + 平台探测」分流

**选择**：在统一 skill 入口处，通过用户输入关键词 + 平台列表判断篇幅类型，设置内部 `scope` 变量（`long` | `short`），后续 Phase/Stage 按 scope 选择执行分支。

**scan 分流逻辑**：
```
用户输入 → 提取平台关键词 →
  起点/晋江/七猫/刺猬猫 → scope=long
  知乎盐言/黑岩/点众短篇 → scope=short
  未指定平台 → 询问「看长篇还是短篇市场？」
```

**analyze 分流逻辑**（复用现有 short-analyze Phase 1.2 字数探针）：
```
拿到原文 → 数字数 →
  < 15,000 → scope=short
  15,000-20,000 → 询问用户
  > 20,000 → scope=long（提示用户如不同意可覆盖）
  用户显式指定 → 优先用户选择
```

**替代方案考虑**：曾考虑让用户每次显式指定 `--long`/`--short` flag，但当前触发词已经携带篇幅信息（"起点排行"=长篇，"知乎盐言"=短篇），自动探测可减少交互摩擦。

### D2: 使用 if/else 分支而非独立子 skill

**选择**：在 SKILL.md 中用 Phase 级 if/else 分支描述两套流程，不创建独立子 skill 或 agent。

**理由**：scan 和 analyze 的 long/short 差异在细节层面（平台列表、分析维度、输出模板），不在流程骨架。用分支描述可以：(a) 保持单一入口，(b) 共享 Phase 0 预检逻辑，(c) 避免 spawn agent 的额外延迟。

**替代方案考虑**：曾考虑让统一 skill 做薄路由再调用子 skill，但这增加了调用层级，破坏了「减少 skill 数量」的初衷。

### D3: 参考文件按 scope 用子目录组织

**选择**：合并后的参考文件结构：
```
write-novel-scan/references/
  scan-common.md          # 共享：Phase 流程、质量检查
  scan-long.md            # 长篇特有：平台列表、分析维度、选题决策
  scan-short.md           # 短篇特有：平台列表、情绪分析、风口预警
  topic-decision.md       # 共享（已存在）
  scan-output-format.md   # 共享（已存在）
  scan-quality-gates.md   # 共享（已存在）

write-novel-analyze/references/
  analyze-common.md        # 共享：门控、恢复机制
  analyze-long.md          # 长篇特有：Stage 管道、逐章摘要
  analyze-short.md         # 短篇特有：Stage 管道、全篇分析
  output-contract.md       # 短篇已有，保留
  material-decomposition.md # 共享（已存在）
```

**理由**：拆分为 common/long/short 三个文件，避免单一巨型 reference 文件；共享部分不重复。

### D4: 旧 skill 目录保留为别名 wrapper

**选择**：旧目录 `write-novel-long-scan/`、`write-novel-short-scan/`、`write-novel-long-analyze/`、`write-novel-short-analyze/` 各保留一个极简 `SKILL.md`（~15 行），只做路由转发到新 skill。

```markdown
---
name: write-novel-long-scan
description: 已合并至 write-novel-scan，保留为向后兼容别名。
---
# 此 skill 已合并至 write-novel-scan
请使用 `/write-novel-scan --long` 或 `/write-novel-scan` 后选择长篇平台。
系统将自动转发...
```

**理由**：现有项目中的 hooks/settings.local.json 可能直接引用旧 skill 名。保留别名 wrapper 确保这些引用不中断。下个大版本清理。

### D5: 路由器更新

write-novel 路由表中：
- "长篇扫榜" / "起点排行" → 路由到 `write-novel-scan`（自动识别为 long）
- "短篇扫榜" / "知乎盐言排行" → 路由到 `write-novel-scan`（自动识别为 short）
- "长篇拆文" / "分析这本书" → 路由到 `write-novel-analyze`（按字数探针分流）
- "短篇拆文" / "拆短篇" → 路由到 `write-novel-analyze`（按字数探针分流，或用户指定）

## Risks / Trade-offs

- **[合并后 SKILL.md 变长]** → scan SKILL.md 预估 ~350 行，analyze SKILL.md 预估 ~400 行。通过将详细执行细节下沉到 reference 文件控制主文件长度。
- **[旧别名 wrapper 增加调用层级]** → wrapper 只做转发，增加一层 Skill 调用。代价可接受（~1 次额外 LLM 调用），大版本清理后消除。
- **[下游 skill 引用需同步更新]** → write-novel-import 内部调用 analyze、write-novel-long-write 流程衔接表引用 scan/analyze。此变更是本提案的一部分。
- **[用户学习成本]** → 旧命令保留别名，用户无感知。新用户只学 `/write-novel-scan` 和 `/write-novel-analyze` 两个命令，反而更简单。

## Migration Plan

1. 创建 `write-novel-scan/SKILL.md` 和 `write-novel-analyze/SKILL.md`
2. 复制并整理 reference 文件（按 D3 结构）
3. 创建 4 个旧 skill 的别名 wrapper SKILL.md
4. 更新 write-novel 路由表
5. 更新 write-novel-import 中 analyze 调用路径
6. 更新 write-novel-long-write / write-novel-short-write 流程衔接表
7. 验证：触发新旧命令均能正确路由
8. 下个大版本：删除旧别名目录和 wrapper

## Open Questions

- 旧 reference 文件是否在合并后立即删除？建议保留到下一大版本，当前只做新增不做删除。
- scan 的平台采集脚本（qidian-rank-scraper.js 等）是否移动？保持原位，它们被 reference 文件按路径引用。
