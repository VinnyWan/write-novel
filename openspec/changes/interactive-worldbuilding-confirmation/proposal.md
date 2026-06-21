## Why

当前 `write-novel-setup` Phase 1.6 世界观初始化阶段，`设定/世界观.md`（时代背景、地理、势力格局、力量体系、社会结构）和 `设定/题材定位.md`（题材类型、核心梗三分法、对标作品）完全由 story-architect agent 自动生成，无用户交互确认环节。这导致世界观设定与用户创作意图偏差时，用户只能在部署完成后手动修改——而非在生成阶段逐项对齐。改为交互确认模式，让用户在初始化时即能逐板块审核和调整世界观设定，避免后期大规模返工。

## What Changes

- **Phase 1.6 增加交互确认步骤**：story-architect agent 生成初稿后、写入文件前，逐板块向用户展示并等待确认/修改
- 世界观六大板块（时代背景、地理环境、势力格局、力量体系、社会结构）分别展示，每项支持「确认/修改/跳过」
- 题材定位三大板块（题材类型、核心梗三分法、对标作品）分别展示，每项支持「确认/修改/跳过」
- 用户可选择「全部确认」批量通过，也可逐项精细调整
- 所有确认完成后统一写入 `设定/世界观.md` 和 `设定/题材定位.md`
- **BREAKING**: Phase 1.6 不再全自动静默生成，默认强制进入交互确认流程

## Capabilities

### New Capabilities
- `interactive-worldbuilding-review`: 世界观初始化阶段的分步交互确认机制，覆盖世界观六大板块和题材定位三大板块

### Modified Capabilities
_无现有 spec 需要修改（openspec/specs/ 为空，首次建立规范）_

## Impact

- `skills/write-novel-setup/` — Phase 1.6 流程重写，增加交互确认步骤
- `references/artifact-protocols.md` — 可能需要补充交互确认的提示模板
- `.story-run-ledger` — Phase 1.6 记录需增加交互确认的子步骤标记
- story-architect agent — 调用方式从「直接写入文件」变为「生成初稿 → 交还主线程展示」
