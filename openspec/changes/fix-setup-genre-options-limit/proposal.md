## Why

`write-novel-setup` Phase 1.5.2 的 Q5（题材/流派选择）从 genre-catalog.md 路由表取前 8 个热门题材 +「其他」，共 9 个选项塞进单个 `AskUserQuestion` 调用。`AskUserQuestion` 硬限制每个问题最多 4 个选项，导致 `InputValidationError: Too big: expected array to have <=4 items`，setup 流程中断。需要在保持完整题材覆盖的前提下，将选项拆分到符合 4 选项上限的交互中。

## What Changes

- **修复 Q5 题材选择**：将单次 9 选项的 AskUserQuestion 拆分为不超过 4 选项的多轮交互（两级选择：大类 → 细分题材）
- **Q3 目标平台**同样检查：5 个平台选项（起点/番茄/晋江/知乎盐言/其他）也超过 4 上限，一并修复

## Capabilities

### New Capabilities

- `setup-genre-selection`: write-novel-setup Phase 1.5 的题材/流派选择交互，确保每次 AskUserQuestion 调用选项数 ≤4

### Modified Capabilities

<!-- 无现有 spec 需要修改 -->

## Impact

- 受影响文件：`skills/write-novel-setup/SKILL.md`（Phase 1.5.2 Q5 + Phase 1.5.1 Q3）
- 不影响其他 skill 或 agent
- 不影响已部署项目的配置文件格式
