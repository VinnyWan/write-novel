## ADDED Requirements

### Requirement: 静态检查须覆盖 references/shared 引用完整性

`static-check.sh` SHALL 包含对 `references/shared/` 目录内 wikilink（`[[...]]`）与路径引用（`](...)`）的悬空检测，目标文件不存在时 MUST 报 FAIL。此检查独立于 per-skill 的 Check 4，作为跨 skill 共享文件的守护门禁。

#### Scenario: shared 内悬空 wikilink 被检出
- **WHEN** `references/shared/某文件.md` 内含 `[[工作流/总览]]` 且 `工作流/` 目录不存在
- **THEN** static-check SHALL 报 FAIL 并指出悬空链接位置

#### Scenario: shared 内合法引用不误报
- **WHEN** `references/shared/某文件.md` 内含指向已存在文件的 `[[pattern-schema]]` 或 `](contract-schema.md)`
- **THEN** static-check SHALL PASS，不误报

### Requirement: 检查只做悬空检测不做引用计数

static-check 对 shared 目录的检查 SHALL 仅校验「引用目标是否存在」，MUST NOT 校验「文件是否被消费」（引用计数），以避免误伤 `contract-schema`（仅 eval 引用）、`pattern-schema`（仅 agent 引用）等合法低频文件。

#### Scenario: 低引用但被 eval 引用的文件不触发引用计数告警
- **WHEN** `contract-schema.md` 仅被 eval 引用、无 skill 引用
- **THEN** static-check SHALL NOT 因引用计数低而报错

### Requirement: 清理后全链检查须 PASS

执行孤儿文件清理后，`static-check.sh`、`run-behavior-evals.sh`、`check-shared-files.sh` 三条检查链 SHALL 全部 PASS，不得因清理引入新的 FAIL 或破坏既有断言。

#### Scenario: 清理后 static-check 全 PASS
- **WHEN** 14 个孤儿文件移除 / 归档完成
- **THEN** `static-check.sh` SHALL 输出 Total PASS = 15（或更多，含新增 Check 10），Fail = 0

#### Scenario: 清理后行为 eval 不回归
- **WHEN** 孤儿文件移除后运行 `run-behavior-evals.sh`
- **THEN** 全部 eval case SHALL PASS，尤其是 `contract_schema_fields`（依赖 contract-schema 保留）不得 FAIL
