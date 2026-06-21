## Why

当前 write-novel 工具集 15 个 skill 中存在 4 对 long/short 变体（scan/analyze/write 各一对 + review/deslop 并非成对），其中 **scan 对和 analyze 对存在高度结构重合**（分别达 ~70% 和 ~60%），维护成本高、改动需双写、路由逻辑分散。合并这两对可降低维护负担、减少路由复杂度，同时保持对外接口不变。

## What Changes

- **合并 write-novel-long-scan + write-novel-short-scan → write-novel-scan**：统一扫榜入口，内部按篇幅/平台分流。Phase 流程（确认→采集→分析→报告→选题）复用，平台列表和分析维度按篇幅动态切换。**BREAKING**: 移除 `/write-novel-long-scan` 和 `/write-novel-short-scan` 直接触发路径，统一为 `/write-novel-scan`（旧路径保留一层别名兼容）
- **合并 write-novel-long-analyze + write-novel-short-analyze → write-novel-analyze**：统一拆文入口，内部按字数和结构特征分流到长/短管道。Stage 概念统一，但执行细节（逐章 vs 全篇）由分流逻辑选择。**BREAKING**: 移除 `/write-novel-long-analyze` 和 `/write-novel-short-analyze` 直接触发路径，统一为 `/write-novel-analyze`（旧路径保留一层别名兼容）
- **write-novel-long-write 与 write-novel-short-write 保持独立**：虽然共享核心哲学（情绪优先），但文件结构（章节 vs 单文件）、流程阶段（5 Phase vs 4 Phase）、追踪体系完全不同。合并会产生超过 2000 行的巨型 skill，维护反而更困难。不做合并。
- **write-novel-review 与 write-novel-deslop 保持独立**：review 是多维度审查（结构+角色+文字+一致性），deslop 是专项去 AI 味。功能正交，仅共享禁词表引用，不做合并。
- **其余 7 个 skill 保持独立**：write-novel（路由）、setup（部署）、cover（封面）、import（导入）、query（查询）、doctor（诊断）、browser-cdp（浏览器）各司其职，无冗余。

## Capabilities

### New Capabilities

- `write-novel-scan`: 统一扫榜能力，替代 write-novel-long-scan 和 write-novel-short-scan，按篇幅和平台自动分流
- `write-novel-analyze`: 统一拆文能力，替代 write-novel-long-analyze 和 write-novel-short-analyze，按字数和结构特征自动分流到长/短管道

### Modified Capabilities

- `write-novel-router`: 路由表中 long-scan/short-scan → scan，long-analyze/short-analyze → analyze；保留旧命令别名

## Impact

- 受影响文件：`write-novel/skills/write-novel/SKILL.md`（路由表更新）、`write-novel/skills/write-novel-long-scan/`（合并入 scan）、`write-novel/skills/write-novel-short-scan/`（合并入 scan）、`write-novel/skills/write-novel-long-analyze/`（合并入 analyze）、`write-novel/skills/write-novel-short-analyze/`（合并入 analyze）
- 新增文件：`write-novel/skills/write-novel-scan/SKILL.md`、`write-novel/skills/write-novel-analyze/SKILL.md`
- 下游影响：write-novel-import 内部调用 long-analyze/short-analyze（需更新为统一入口）、write-novel-long-write/short-write 的流程衔接表（需更新引用）
- 旧命令别名保留至少一个版本，下个大版本清理
