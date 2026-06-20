## Why

`static-check.sh` 已覆盖 per-skill 引用完整性（路径/交叉/内联/裸名/section）和 shared wikilink，但缺少**反向引用计数**和**循环引用检测**。当前的 WARN 只报告"裸名未包裹反引号"，不区分"文件被引用了但没包裹"和"文件完全无引用"——后者才是真正的僵尸。此外，多个 skill 的 references/ 目录经过多轮瘦身，可能存在：skill A 引用了 skill B 的 references 文件但 B 已删除该文件、Agent 定义文件声明了但无任何 skill 调用、references 文件之间形成引用环。

## What Changes

- **新增反向引用计数扫描**：扫描所有 skill SKILL.md + references/*.md + agents/*.md，对每个文件计算被引用次数，标记零引用文件为僵尸候选。
- **新增循环引用检测**：解析所有 `](...)` 和 `[[...]]` 引用构建有向图，检测环（A→B→A 或更长链），报告环路径和参与者。
- **Agent 调用方检测**：扫描所有 skill 的 `subagent_type` 引用，找出零调用的 agent 定义文件。
- **僵尸文件清理**：经反向引用计数确认零引用、且不在 MANIFEST.yaml 登记、且不在显式保留白名单中的文件，标记删除或归档。

## Capabilities

### New Capabilities
- `reverse-reference-audit`: 反向引用计数——扫描全仓库 .md 文件，构建「文件 → 被引用次数」映射，识别零引用僵尸。
- `cyclic-reference-detection`: 循环引用检测——解析所有内部引用构建有向图，检测简单环和多跳环，输出环路径。
- `agent-call-audit`: Agent 调用方检测——扫描 skill 的 `subagent_type` 引用，找出零调用的 agent 定义。

### Modified Capabilities
<!-- 纯检测+清理，不修改既有 spec 的行为要求 -->

## Impact

- **受影响文件**：`write-novel/scripts/static-check.sh`（新增 Check 11 反向引用计数 + Check 12 循环检测）、可能的僵尸文件删除。
- **受影响检查**：`static-check.sh` 当前 16/16 PASS，新 Check 预期揭示僵尸文件数量后仍 PASS（僵尸被删除或登记至 MANIFEST 白名单后）。
- **风险**：误删仍有隐性消费者的文件。缓解：反向引用计数扫描全仓库（skills/agents/hooks/scripts/evals/templates）后再判定零引用。
