## ADDED Requirements

### Requirement: 方法论知识单一权威来源

写作方法论知识库中的每个文件 SHALL 在 `references/shared/` 下有且仅有一份权威全文副本，所有 skill MUST 通过指针文件（首行 `> **共享参考文件**`，第二行 `> 共享源：references/shared/<file>`）消费该副本。`references/methodology/` 目录 MUST NOT 保存与 `references/shared/` 同名的非指针全文副本。

#### Scenario: 同名全文副本被检测为违例

- **WHEN** 校验脚本发现 `references/methodology/<name>.md` 与 `references/shared/<name>.md` 同名，且 `methodology/` 中的该文件不是指向 shared 源的指针文件
- **THEN** 脚本 MUST 以非零退出码报告该重复（含文件路径），并提示「方法论知识应在 shared/ 单一存放」

#### Scenario: methodology 独有且被引用的文件允许保留

- **WHEN** `references/methodology/<name>.md` 在 `references/shared/` 中没有同名文件，且仓库中存在对其的引用
- **THEN** 校验脚本 MUST 视其为合法，不报错

#### Scenario: 被运行时引用的同名文件改指 shared 后无残留

- **WHEN** 某文件（如 `genre-writing-formulas.md`）原同时存在于 methodology/ 与 shared/，且引用方已改为指向 `references/shared/` 的版本
- **THEN** `references/methodology/` 中该同名副本 MUST 已被删除，且全仓 `grep` 对 `references/methodology/<name>` 的引用数为 0
