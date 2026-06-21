## Context

`write-novel` 是纯 Markdown 驱动的网文创作插件，由多个历史插件多轮合并而来（`合并自：…` 痕迹遍布 frontmatter）。合并把 4 个旧 skill 收敛为别名（`long/short-analyze`、`long/short-scan`），把多个旧 agent 收敛为 8 个 agent，并把 `plan` 并入 `long-write`。本次审计实地核查了全部 17 个 skill 目录与 8 个 agent，确认链路断裂集中在五类不变量上（详见 proposal 与 spec）。

约束：
- 项目铁律——脚本只做确定性自动化（Frontmatter 解析、字数统计、禁词扫描、断链校验），不做创作决策。审计工具必须落在这一边界内。
- 废弃别名 skill **不能删除**（仍是用户兼容入口），因此「废弃名」与「规范名」的区分必须显式可枚举。
- 插件目录嵌套在仓库内 `write-novel/`，OpenSpec 在仓库根 `openspec/`，工具需以插件根为基准路径。

## Goals / Non-Goals

**Goals:**
- 提供一个可重复运行的确定性审计脚本，把五类不变量从「人工巡检」变成「一条命令 + 结构化报告」。
- 一次性修复初次审计发现的全部具体缺口（stale caller、部署模板废弃命令、双份 hooks 漂移、清单计数/版本）。
- 把审计接入既有体检/静态检查链路（`/write-novel-doctor`、`scripts/static-check.sh`），让回归可被持续拦截。

**Non-Goals:**
- 不删除任何废弃别名 skill，不改动创作语义或正文模板内容。
- 不做主观质量评判（那是 reviewer agent 的职责），审计只做客观链路/引用/计数校验。
- 不重写 hooks 行为逻辑，只消除双份漂移与命名不一致。

## Decisions

**D1：单一 Python3 审计脚本，而非多个 shell 校验拼接。**
理由：五类不变量都需要路径解析、frontmatter 解析、跨文件枚举，Python3 比 shell 更易维护且仓库已大量使用 Python（`hooks/*.py`、`scripts/*.py`）。脚本落在 `write-novel/scripts/audit-pipeline.py`，输出分类报告 + 非零退出码。
备选：扩展现有 `scripts/static-check.sh`（被否，shell 解析 frontmatter/路径脆弱）；复用 `scripts/check-shared-files.sh`（被否，职责窄）。

**D2：废弃别名清单作为脚本内显式常量，集中维护。**
理由：「规范名 vs 废弃名」的判定必须确定性、可枚举；从主路由 skill 的重定向表自动推断会引入歧义。集中常量 + 注释来源，未来新增合并时一处更新。
备选：从 frontmatter「已合并至…」文案正则推断（被否，文案不规整易漏）。

**D3：废弃名允许域用「白名单上下文」界定。**
重定向表、`合并自：` 历史行、`description` 中说明合并来源的句子属于合法出现；用户级部署模板、agent 调用方声明、hook 用户提示属于非法出现。脚本按「文件类别 + 行模式」判定，降低误报。

**D4：双份 hooks 同步以「逻辑内容比对 + 命名映射」实现。**
两份副本命名风格不同（下划线 vs 连字符），先用命名映射对齐文件，再比对去除路径风格差异后的内容；同时强校验部署模板 hook 名与 `settings-hooks.json` 引用一一对应。
备选：强制两份命名统一（被否，影响面大且非本次必需，留作 Open Question）。

**D5：修复遵循「规范名替换、保留兼容」原则。**
所有 stale caller / 部署废弃命令统一替换为规范名（`analyze`/`scan`），别名 skill 本体不动；清单计数改为「区分规范 skill 与兼容别名」的准确表述，版本号两清单对齐到 `plugin.json` 的 `2.3.2`。

## Risks / Trade-offs

- **[误报：废弃名的合法出现被错判为 stale]** → 用 D3 白名单上下文 + 行模式精确界定；初版在全仓跑一遍，人工确认零误报后再接入门禁。
- **[审计脚本本身成为新的维护负担]** → 保持单文件、零外部依赖、常量集中；接入 `static-check.sh` 后回归自动覆盖。
- **[双份 hooks 内容比对对格式差异敏感]** → 比对前归一化（去命名风格、去空白），只比逻辑行；无法自动归一的差异降级为 WARN 而非 FAIL。
- **[参考文档正文废弃名量大]** → 列为低优先级 WARN，不阻断门禁；本次只清理用户可见/会回流到产物的部分，纯内部文档分批跟进。

## Migration Plan

1. 实现 `audit-pipeline.py`，对当前仓库跑首轮，确认其报告与本设计枚举的缺口一致（零误报）。
2. 按 spec 五类不变量逐项修复具体缺口（stale caller → 部署模板 → 双份 hooks → 清单）。
3. 修复后重跑审计，达到高优先级问题清零（PASS / 零退出码）。
4. 把审计接入 `/write-novel-doctor` 与 `scripts/static-check.sh`，作为持续护栏。
5. 回滚策略：全部改动为文本/脚本，纯 Git 可逆；审计脚本独立新增，接入点改动小，回滚不影响创作链路。

## Open Questions

- 是否在后续变更中统一两份 hooks 的命名风格（彻底消除双份漂移根因）？本次先做同步校验，不强行统一。
- 参考文档正文中的废弃名是否需要全量清理，还是只清理会回流到生成产物的部分？倾向后者，待确认。
