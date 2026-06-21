## Why

`write-novel` 插件经过多轮合并演进（`long/short-analyze → analyze`、`long/short-scan → scan`、`plan → long-write`，8 个 agent 由更多旧 agent 合并而来）。合并后散落了大量**失效交叉引用**、**面向用户的已部署模板仍把废弃命令当作主命令**、**插件运行态 hooks 与部署模板 hooks 双份漂移**、以及**清单元数据与真实文件不符**。目前没有任何可重复运行的自动校验，链路断裂只能靠人工巡检发现——这正是本次需要系统梳理「每个 skill 与 agent 从头到尾链路」并查漏补缺的根因。

## What Changes

- **新增 `pipeline-audit-tooling` 能力**：一个确定性、可重复运行的审计脚本（落在 `write-novel/scripts/`），校验下列五条链路不变量并输出结构化报告，可被 `/write-novel-doctor` 与静态检查复用。
- **修复初次审计发现的全部具体缺口**（证据见下，均已实地核查）：

  1. **Agent 元数据失效调用方** — `agents/write-novel-deconstruction-agent.md:5` 写「被 write-novel-long-analyze 和 write-novel-import 调用」，而 `write-novel-long-analyze` 已是废弃别名（合并进 `write-novel-analyze`）。调用方引用已死。
  2. **已部署的用户级模板把废弃命令当主命令**：
     - `skills/write-novel-setup/references/templates/CLAUDE.md.tmpl:22-25` 的路由表把 `/write-novel-long-analyze`、`/write-novel-short-analyze`、`/write-novel-long-scan`、`/write-novel-short-scan` 列为规范命令。
     - 已部署 hooks `templates/hooks/session-start.sh:96`、`detect-story-gaps.sh:84` 提示用户运行 `/write-novel-long-analyze`、`/write-novel-short-analyze`（废弃）。
     - 已部署 agent 模板 `templates/agents/write-novel-deconstruction-agent.md:5` 携带同样失效调用方。
  3. **插件运行态 hooks 与部署模板 hooks 双份漂移**：插件 `hooks/` 用下划线命名（`session_start.sh`、`detect_story_gaps.sh`、`post_compact.sh`、`pre_compact.sh`、`session_end.sh`、`validate_story_commit.sh`），部署模板 `templates/hooks/` 用连字符命名（与 `settings-hooks.json` 自洽）。两份副本 + 两套命名，仅 `scripts/check-hook-regex-sync.sh` 部分护栏；改一份易漏另一份。
  4. **清单/市场元数据与现实不符**：`.claude-plugin/marketplace.json` 写 version `2.3.0`、描述「14 Skills + 6 Agents」；`write-novel/.claude-plugin/plugin.json` 写 version `2.3.2`；真实为 17 个 skill 目录（13 个规范 + 4 个废弃别名）+ 8 个 agent。计数与版本均失同步。
  5. **参考文档大面积在正文里使用废弃 skill 名**（多个 `references/*.md` 仍写「write-novel-long-analyze Stage 6」等）。优先级较低（内部文档），但会扩散困惑并在重生成产物时回流。

- **确立命名规范策略**：废弃别名只允许出现在显式「重定向/兼容表」中，**严禁**出现在用户级部署模板、hooks 提示、agent 调用方元数据里。

## Capabilities

### New Capabilities
- `pipeline-audit-tooling`: 对 write-novel 全部 skill 与 agent 做确定性链路审计的工具能力——校验文件引用可解析、交叉引用指向存活（非废弃）目标、部署模板使用规范命令名、双份 hooks 同步、清单计数/版本与文件系统一致，并输出可追溯的结构化报告。

### Modified Capabilities
<!-- openspec/specs/ 当前为空，无既有 spec 需要改动 -->
（无）

## Impact

- **新增**：`write-novel/scripts/audit-pipeline.*`（审计脚本）+ 其在 `/write-novel-doctor` 或 `scripts/static-check.sh` 中的接入点。
- **修改（修复）**：`agents/write-novel-deconstruction-agent.md`、`skills/write-novel-setup/references/templates/CLAUDE.md.tmpl`、`templates/hooks/session-start.sh`、`templates/hooks/detect-story-gaps.sh`、`templates/agents/write-novel-deconstruction-agent.md`、`.claude-plugin/marketplace.json`、`write-novel/.claude-plugin/plugin.json`、`hooks/` 与 `templates/hooks/` 同步、多个 `references/*.md` 正文废弃名清理。
- **无破坏性变更**：废弃别名 skill（`write-novel-long-analyze` 等）继续保留为兼容入口；本次只修正「把废弃名当规范名」的引用，不删除别名本身。
- **依赖**：审计脚本仅依赖 Python3 / 标准 shell，无新增外部依赖。
