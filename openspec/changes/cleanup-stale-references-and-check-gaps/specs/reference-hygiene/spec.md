## ADDED Requirements

### Requirement: references/shared 每个文件须有明确消费者或显式登记

`references/shared/` 目录下每个文件 MUST 至少满足以下一项，否则 SHALL 被移除或归档到 `references/archive/`：
- 被至少一个 skill 的 SKILL.md / references / agent / hook / script / eval 引用
- 在 `references/shared/MANIFEST.yaml` 的 `shared_sources` 或 `whitelist_real_files` 中显式登记

未接线但保留知识价值的规范文件 SHALL 归档至 `references/archive/`，不得留在 `references/shared/` 顶层。

#### Scenario: 零引用文件不得留在 shared 顶层
- **WHEN** `references/shared/` 下某文件在 skills / agents / hooks / scripts / evals / templates / MANIFEST 中均无引用
- **THEN** 该文件 SHALL 被删除（死文档）或移至 `references/archive/`（有价值规范）或 `references/rules/`（教学样本）

#### Scenario: 归档文件须有 README 说明
- **WHEN** 文件被移至 `references/archive/`
- **THEN** `references/archive/README.md` SHALL 列明每个归档文件的原路径、内容性质与「待接线」状态

### Requirement: v0.3 遗留死文档须删除

描述已不存在的 `工作流/`、`卡片/` 目录结构或 `main.py`/`prompt_builder.py`/`dashboard.py` 等 CLI 脚本体系的文档 MUST 删除，不得保留，因内部 wikilink 全部悬空且内容与现状脱节。

#### Scenario: 工作流总览等死文档被删除
- **WHEN** 执行清理后
- **THEN** `工作流总览.md`、`脚本治理.md`、`风险清单.md`、`当前任务.md` SHALL 不存在于 `references/shared/`

### Requirement: 活跃低频文件须保留

被 eval 断言或 agent 加载的文件即使引用计数低，MUST 保留在 `references/shared/`，不得因「低引用」误删。

#### Scenario: contract-schema 保留
- **WHEN** eval `contract_schema_fields` 断言引用 `references/shared/contract-schema.md`
- **THEN** 该文件 SHALL 保留，不被清理

#### Scenario: pattern-schema 保留
- **WHEN** architect agent 加载 `references/shared/pattern-schema.md`
- **THEN** 该文件 SHALL 保留，不被清理
