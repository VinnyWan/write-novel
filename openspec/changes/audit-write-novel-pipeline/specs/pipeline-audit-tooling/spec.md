## ADDED Requirements

### Requirement: 文件引用可解析校验

审计工具 SHALL 扫描每个 `skills/*/SKILL.md` 与 `agents/*.md`，提取其引用的相对文件路径（`scripts/`、`references/`、`templates/`、`hooks/`、`assets/`、`agents/`），并验证每个引用都能在「文件自身目录、所属 skill 根、插件根」之一解析到存在的文件。

#### Scenario: 引用指向存在的文件
- **WHEN** 一个 SKILL.md 引用 `references/genre-catalog.md` 且该文件在解析根之一存在
- **THEN** 工具将该引用标记为 PASS，不计入断链

#### Scenario: 引用指向缺失文件
- **WHEN** 一个 SKILL.md 或 agent 引用的相对路径在所有解析根都不存在
- **THEN** 工具将其报告为 `BROKEN_REF`，并打印来源文件、行号与缺失路径

### Requirement: 交叉引用指向存活目标

审计工具 SHALL 检测 skill 与 agent 元数据（frontmatter description、agent 调用方声明）及用户级部署模板中对其他 skill/agent 的命名引用，并区分「存活规范名」与「废弃别名名」。废弃别名（如 `write-novel-long-analyze`、`write-novel-short-analyze`、`write-novel-long-scan`、`write-novel-short-scan`、`write-novel-plan`）只允许出现在显式重定向/兼容表中。

#### Scenario: 调用方元数据使用废弃别名
- **WHEN** 某 agent 的 description 声明「被 `write-novel-long-analyze` 调用」而该名是废弃别名
- **THEN** 工具报告 `STALE_CALLER`，并提示应替换为规范名 `write-novel-analyze`

#### Scenario: 废弃别名出现在重定向表内
- **WHEN** 废弃别名出现在主路由 skill 的「旧命令 → 规范命令」重定向表中
- **THEN** 工具将其视为合法，不报告问题

### Requirement: 部署模板使用规范命令名

审计工具 SHALL 校验 `skills/write-novel-setup/references/templates/` 下所有交付给用户项目的模板（`CLAUDE.md.tmpl`、`hooks/*.sh`、`agents/*.md`、`rules/*.md`）不得把废弃别名命令作为规范命令呈现给用户。

#### Scenario: 部署模板把废弃命令当主命令
- **WHEN** `CLAUDE.md.tmpl` 路由表或部署 hook 的提示文案把 `/write-novel-long-analyze` 列为可运行的规范命令
- **THEN** 工具报告 `DEPLOY_STALE_CMD`，标注文件与行号

### Requirement: 配置引用的 hook 文件存在

审计工具 SHALL 校验每个 hook 配置文件引用的 hook 脚本都解析到存在的文件：部署侧 `settings-hooks.json` 引用须落在 `skills/write-novel-setup/references/templates/hooks/`；运行态 `hooks/hooks.json` 引用须落在插件 `hooks/`。注：运行态 hooks 与部署模板 hooks 是**两套按角色分化的实现**（运行态含 `guard_runtime_write.py`、`session_start.py` 等额外脚本），二者不要求逐字节相同，故工具只校验「配置引用可解析」，不做跨副本内容比对。

#### Scenario: 部署 settings 引用了不存在的 hook 文件
- **WHEN** `settings-hooks.json` 引用 `.claude/hooks/session-start.sh` 但部署模板 hooks 目录缺少对应文件
- **THEN** 工具报告 `HOOK_NAME_MISMATCH`，列出被引用但缺失的 hook 名

#### Scenario: 运行态 hooks.json 引用了不存在的 hook 文件
- **WHEN** `hooks/hooks.json` 引用某个 hook 脚本但插件 `hooks/` 缺少对应文件
- **THEN** 工具报告 `HOOK_NAME_MISMATCH`

### Requirement: 清单计数与版本一致性

审计工具 SHALL 校验 `.claude-plugin/marketplace.json` 与 `write-novel/.claude-plugin/plugin.json` 中声明的 skill/agent 计数、版本号与文件系统真实状态一致。

#### Scenario: 清单计数与真实数量不符
- **WHEN** marketplace 描述声明「14 Skills + 6 Agents」而文件系统存在 13 个规范 skill 与 8 个 agent
- **THEN** 工具报告 `MANIFEST_COUNT_MISMATCH`，给出声明值与实测值

#### Scenario: 两个清单版本号不一致
- **WHEN** `plugin.json` 版本为 `2.3.2` 而 `marketplace.json` 版本为 `2.3.0`
- **THEN** 工具报告 `VERSION_MISMATCH`

### Requirement: 结构化可追溯报告

审计工具 SHALL 以结构化、可追溯的形式输出全部发现（问题类别、来源文件、行号、修复建议），并以非零退出码表示存在未修复的高优先级问题，使其可被 `/write-novel-doctor` 与 `scripts/static-check.sh` 复用。

#### Scenario: 存在高优先级问题
- **WHEN** 审计发现任意 `BROKEN_REF`、`HOOK_NAME_MISMATCH` 或 `DEPLOY_STALE_CMD`
- **THEN** 工具以非零退出码结束，并打印分类汇总

#### Scenario: 全部通过
- **WHEN** 所有不变量校验通过
- **THEN** 工具以零退出码结束并打印 PASS 摘要
