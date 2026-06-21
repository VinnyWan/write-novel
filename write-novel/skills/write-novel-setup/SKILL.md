---
name: write-novel-setup
version: 1.2.0
description: |
  网文写作工具集基础设施部署。将 hooks/rules/agents/CLAUDE.md 等基础设施部署到用户项目目录。
  触发方式：/write-novel-setup、「准备写书」「帮我搭一下环境」「配置写作项目」（旧触发词：/story-setup）
  合并自：write-novel-setup + write-novel-setup + webnovel-init
metadata:
  openclaw:
    source: https://github.com/worldwonderer/oh-story-claudecode
---

# write-novel-setup：网文写作工具集基础设施部署

你是写作基础设施部署器。将网文写作工具集的全套基础设施（hooks、rules、agents、CLAUDE.md）部署到用户项目目录。

**执行铁律：不覆盖用户已有配置，合并而非替换。**

**交互模式（D7）**：用户确认部署位置后，自动执行 Phase 2 部署 + Phase 3 验证，一次性输出安装报告，不再单独询问「是否验证」。每个 Phase 结束立即向 `.story-run-ledger` 追加一行（含 Phase 名、时间戳、状态），便于中断恢复定位。

---

## Phase 1：检测项目状态

1. 检查当前目录是否已部署过（存在 `.story-deployed`）→ 已存在则 AskUserQuestion 确认是否重新部署
2. 检查是否有书名目录（含 `追踪/` 子目录或用户自定义结构）→ 有则识别为长篇项目，无则识别为新项目/短篇项目
3. 检查 `.claude/settings.local.json` → 存在则读取待合并，不存在则后续创建
4. 检查 `.active-book` → 存在则显示当前活跃书目
5. 检查 `.story-config.json` → 存在则展示配置摘要，AskUserQuestion「是否修改配置？」（是→Phase 1.5 预填已有值；否→跳过 Phase 1.5）；不存在或无书名目录→进入 Phase 1.5 全新收集
6. **旧命名部署迁移检测**（v0.4.0 命名空间统一后）：扫描 `.claude/skills/story-*` 目录和 `.claude/agents/{narrative-writer,reviewer,character-designer,consistency-checker,deconstruction-agent,story-architect,story-explorer,story-researcher}.md` 裸名/旧名文件 → 检测到旧命名进入 Phase 2.0a 迁移；未检测到跳过迁移按正常 Phase 2 部署

> **run-ledger**：Phase 1 完成后追加 `{timestamp} | phase-1-detect | {项目状态摘要} | success`。

## Phase 1.5：项目配置向导

> 配置向导收集项目核心参数，持久化到 `.story-config.json`。后续所有 skill 可从此文件读取参数，消除重复询问。

### 1.5.1 必填轮（4 问，顺序固定）

- **Q1 作者笔名**：默认 `git config user.name`；写入 `author_name`
- **Q2 书名**：默认 Phase 1 检测到的书名目录名；写入 `book_name`
- **Q3 目标平台**（单选）：起点、番茄、晋江、知乎盐言、其他；写入 `target_platform`
- **Q4 目标字数**（单选）：30万字（短篇）、100万字（中篇）、200万字+（长篇超）、自定义（弹出文本输入）；写入 `target_words`（整数，单位：字）

### 1.5.2 选填轮确认 + 选填轮（3 问，可跳过）

必填轮 4 项完成后，AskUserQuestion「是否进行更多配置（题材、风格、存储结构）？」；选「跳过」则选填字段写默认值进入 1.5.4。

- **Q5 题材/流派**（单选）：从 `agent-references/genre-catalog.md` 路由表第一列取前 8 个热门题材 +「其他」；写入 `genre`
- **Q6 写作风格偏好**（单选）：热血、轻松、暗黑、幽默、不指定；写入 `style_preference`
- **Q7 存储结构**（单选）：单书（`{书名}/`）、多书并列；写入 `storage_structure`

### 1.5.3 配置摘要确认

展示完整配置摘要，AskUserQuestion「确认以上配置？」→「确认」写入 `.story-config.json` 进 Phase 2；「重新填写」返回 1.5.1。

### 1.5.4 模板占位符替换

配置确认后、Phase 2 部署前，从 `.story-config.json` 读取值批量替换：`{作者名}`→`author_name`、`{书名}`/`{项目名}`→`book_name`、`{目标平台}`→`target_platform`、`{目标字数}`→格式化「X万字」、`{题材}`→`genre`。未收集到的字段对应占位符保留原样。

> **run-ledger**：Phase 1.5 完成后追加 `{timestamp} | phase-1.5-config | {book_name}/{target_platform} | success`。

## Phase 1.6：世界观初始化（D8 新增）

> 在配置向导完成后、Phase 2 部署前执行。产出 `设定/世界观.md` 和 `设定/题材定位.md`，建立故事的基础时空框架。
> 后续 write-novel-long-write Phase 2 在此基础上细化角色和核心冲突，不再从零构建世界观。

### 1.6.1 触发条件

- 长篇项目（已有书名目录或 Phase 1.5 刚创建）→ 执行 Phase 1.6
- 短篇项目 → 跳过，提示「短篇可跳过世界观初始化，写作时按需构建设定」

### 1.6.2 重跑检测

检查 `设定/世界观.md` 是否存在：
- 存在 → 跳过 Phase 1.6，提示「世界观已存在。使用 `--rebuild-worldbuilding` 重建」
- 不存在 → 进入 1.6.3 产出

### 1.6.3 世界观产出

从 `.story-config.json` 读取 `target_words`/`genre`/`style_preference`，调用 story-architect agent 产出两个文件：

**产出 A：`设定/世界观.md`**

按目标字数分级确定详细程度：
- `< 100 万字`：简化模板，各板块 2-5 行描述
- `>= 100 万字`：完整模板，各板块 5-15 行描述，含子条目

模板见 `references/artifact-protocols.md`「设定/世界观.md」。必含：
- 时代背景（时代/年份/历史阶段/关键历史事件）
- 地理环境（主要地域/势力范围/特色地貌）
- 势力格局（核心势力+次级势力+关系矩阵）
- 力量体系（体系类型/等级划分/晋升规则，如适用）
- 社会结构（阶层/资源分配/货币经济/信仰）

**产出 B：`设定/题材定位.md`**

模板见 `references/artifact-protocols.md`「设定/题材定位.md」。必含：
- 题材类型 + 风格定位 + 目标读者画像
- 核心梗三分法（表层卖点/深层爽点/长线钩子）
- 对标作品（1-3 部，如用户在 Phase 1.5 提供了对标信息）

**Agent 调用**：spawn `Agent(subagent_type: "write-novel:write-novel-story-architect", prompt: "项目目录：{dir}\n任务类型：世界观初始化\n参数：字数={target_words} 题材={genre} 风格={style_preference}\n产出：设定/世界观.md + 设定/题材定位.md\n按字数分级选择模板详细程度。")`。agent 不可用时由主线程直接执行。

### 1.6.4 产出后 Gate

产出后校验两个文件：
- `设定/世界观.md` frontmatter 含 `era`/`world_type`/`power_system`/`target_words` 字段
- `设定/题材定位.md` 含「核心梗三分法」段落
- 任一缺失 → 补全后重新校验

> **run-ledger**：Phase 1.6 完成后追加 `{timestamp} | phase-1.6-worldbuilding | 世界观+题材定位 | success`。

## Phase 2：部署基础设施

使用 AskUserQuestion 确认部署位置后，依次执行。**部署位置确认保留**（D7 仅合并验证环节的二次确认，部署位置确认不取消）。

### 2.0a 旧命名迁移（条件执行）

> 仅当 Phase 1 步骤 6 检测到旧命名部署时执行；否则跳过直接进入 2.0。

**迁移原则**：dry-run 列出变更 → 用户确认 → 原子迁移 → 迁移后无新旧并存。

1. **扫描旧命名部署**：`Glob .claude/skills/story-*` + `Glob .claude/agents/{裸名/旧名}.md`（8 个 agent）+ 读 `.claude/settings.local.json` 扫描 hooks 中引用旧 skill 名的 command 字段
2. **生成 dry-run 变更清单**（不执行修改）：skill 目录重命名映射（`story-X`→`write-novel-X`，14 项）、agent 文件重命名映射（裸名→`write-novel-` 前缀，8 项）、settings.local.json hook command 路径更新项（`/story-X`→`/write-novel-X`）、列出将被删除的旧路径
3. **AskUserQuestion 确认迁移**：「确认」→继续步骤 4；「取消」→跳过迁移仅执行 Phase 2 全新部署（旧命名文件保留，后续由 write-novel-doctor 标记）
4. **执行迁移**（顺序敏感）：4a 备份 `.claude/settings.local.json`→`.bak.{timestamp}`；4b `git mv`/`mv` 14 个 skill 目录 `story-X`→`write-novel-X`；4c `git mv`/`mv` 8 个 agent 文件裸名→`write-novel-` 前缀；4d 更新 `.claude/settings.local.json` hook command 路径引用；4e 如 `.story-deployed` 存在更新 `agents_version: 12`、`setup_skill_version: 1.2.0`
5. **迁移后校验**（无新旧并存）：`Glob .claude/skills/story-*` 零命中；`Glob .claude/agents/{裸名}.md` 零命中；grep `subagent_type:` 后接 `"story-` 或裸名调用零命中；任一失败→回滚（从备份恢复 + git mv 回去）报告失败原因
6. **追加 run-ledger 迁移记录**：在 `.story-deployed` 同目录的 `.story-run-ledger`（不存在则创建）追加：
   ```
   {timestamp} | namespace-migration | story-* → write-novel-* | {迁移 skill 数} skills, {迁移 agent 数} agents | success
   ```
7. **进入 Phase 2.0 常规部署清单**：迁移完成后继续执行 2.0 部署清单（覆盖更新 agents/hooks/rules 至最新版本）

### 2.0 部署清单（机械可检查）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/write-novel-setup/references/templates/CLAUDE.md.tmpl` | `CLAUDE.md` | user+managed | marker/section merge | contains story skill routing sections |
| `skills/write-novel-setup/references/templates/hooks/` | `.claude/hooks/` | managed | recursive replace | `session-*.sh`, `detect-story-gaps.sh`, `validate-story-commit.sh`, `post-compact.sh`, `pre-compact.sh`, `lib/common.sh`, `lib/sentinel.sh` exist |
| `skills/write-novel-setup/references/templates/rules/*.md` | `.claude/rules/*.md` | managed | replace | every rule contains `paths` frontmatter |
| `skills/write-novel-setup/references/templates/agents/*.md` | `.claude/agents/*.md` | managed | replace | 8 agent files exist |
| `skills/write-novel-setup/references/agent-references/*.md` | `.claude/skills/write-novel-setup/references/agent-references/*.md` | managed | replace | every agent-references ref resolves |
| `skills/write-novel-setup/references/templates/settings-hooks.json` | `.claude/settings.local.json` | user+managed | merge by hook command | hook JSON valid, commands deduped |
| `skills/write-novel-setup/references/templates/上下文.md.tmpl` | `{书名}/追踪/上下文.md` | user state | create only if absent | never overwrite existing context |
| generated config | `.story-config.json` | user state | create only if absent | contains `version`,`author_name`,`book_name`,`target_platform`,`target_words` |
| generated sentinel | `.story-deployed` | managed | replace | contains `agents_version`,`setup_skill_version`,`target_cli`,`resolver_strategy`,`references_dir` |
| generated script | `start-dashboard.sh` | managed | replace | executable, contains abs path to `novel-dashboard` |

### 2.1-2.8 部署步骤

- **2.1 CLAUDE.md**：读模板替换占位符→写项目根 `CLAUDE.md`（已存在按「CLAUDE.md 合并策略」处理）
- **2.2 Hooks**：递归复制 `templates/hooks/`→`.claude/hooks/`，保留 `lib/`（`common.sh` 提供 `project_root`/`discover_active_book`/`discover_all_books`，`sentinel.sh` 读 `.story-deployed`）；仅 `.claude/hooks/*.sh` 设 `chmod +x`
- **2.3 Rules**：复制 `templates/rules/*.md`→`.claude/rules/`
- **2.4 Agents**：复制 `templates/agents/*.md`→`.claude/agents/`（管理文件可安全覆盖，按 `UPGRADING.md` 版本检测重新部署）
- **2.4.1 Agent 兼容性**：frontmatter 以 Claude Code 为主，OpenClaw/qclaw 等忽略未知字段；若目标工具报错保留 `name`/`description`/`tools` 三项。agent 引用资料走 `write-novel-setup/references/agent-references/*.md` 单一 skill 内路径，不跨 skill 引用
- **2.4.2 Agent References**：复制 `references/agent-references/`→`.claude/skills/write-novel-setup/references/agent-references/`（主路径），可同步复制到项目本地 `skills/` 作 fallback，但不得只复制 fallback 遗漏主路径；校验源包与目标包文件均存在
- **2.5 Session State 模板**：仅当长篇书目且 `{书名}/追踪/` 已存在时创建缺失的 `{书名}/追踪/上下文.md`，已存在不覆盖，短篇不创建 `追踪/`
- **2.6 合并 Hooks 注册**：读 `settings-hooks.json` + 用户 `.claude/settings.local.json`，按 command 去重合并 hooks（用户已有 command 保留，模板新 command append，用户独有 permissions/env 完整保留），写入 `.claude/settings.local.json`
- **2.7 部署标记**：创建 `.story-deployed`（YAML）：`deployed_at`/`agents_version: 12`/`setup_skill_version: 1.2.0`/`target_cli: claude-code`/`resolver_strategy: project-local-skill-reference`/`references_dir: .claude/skills/write-novel-setup/references/agent-references`。已存在但 `agents_version` < 10 → 提示重新运行 setup 更新
- **2.8 Dashboard wrapper**：项目根生成 `start-dashboard.sh`（`exec "<tool-root>/bin/novel-dashboard" "$@"`，`<tool-root>` 为 skill 向上两级绝对路径），`chmod +x`

> **run-ledger**：Phase 2 完成后追加 `{timestamp} | phase-2-deploy | {部署文件数} files | success`。

## Phase 3：验证安装（D7：自动执行 + 一次性报告）

> 用户确认部署位置后自动执行，**不再单独询问「是否验证」**。验证与安装报告一次性输出。

1. **hooks 注册**：`.claude/settings.local.json` hooks 字段正确；`.claude/hooks/` 脚本存在且有执行权限；`lib/common.sh`+`lib/sentinel.sh` 存在
2. **rules 路径**：`.claude/rules/*.md` 存在且含 `paths` frontmatter
3. **agents**：`.claude/agents/` 下 8 个 agent 文件存在（write-novel-story-architect, write-novel-character-designer, write-novel-narrative-writer, write-novel-reviewer, write-novel-story-researcher, write-novel-deconstruction-agent, write-novel-consistency-checker, write-novel-story-explorer）
4. **agent reference bundle**：`.claude/skills/write-novel-setup/references/agent-references/` 文件完整，所有引用可解析到 deployed bundle
5. **部署标记**：`.story-deployed` 存在且含 `agents_version: 12`/`setup_skill_version: 1.2.0`/`target_cli`/`resolver_strategy`/`references_dir`
6. **项目配置**：`.story-config.json` 存在且必填字段（`author_name`/`book_name`/`target_platform`/`target_words`）非空；缺失输出警告
7. **Dashboard wrapper**：`start-dashboard.sh` 存在且可执行，含正确 `novel-dashboard` 绝对路径
8. **世界观文件**（长篇项目）：`设定/世界观.md` 存在且 frontmatter 含 `era`/`world_type`/`power_system`/`target_words` 字段；`设定/题材定位.md` 存在且含「核心梗三分法」段落。短篇项目跳过本项
9. **输出安装报告**（一次性）：列出已部署文件 + 注意事项（已有配置已合并等）+ 提示开始使用 `/write-novel-long-write` 或 `/write-novel-short-write`

> **run-ledger**：Phase 3 完成后追加 `{timestamp} | phase-3-verify | {验证通过项数}/{总项数} | success`。

---

## 合并策略参考

**CLAUDE.md 合并**：优先识别 write-novel-setup 管理块标记（只替换标记内内容）；无标记时按 `##` 标题切 section map，模板标准 section（Skill 路由表/项目配置/文件结构/协作规则/Context Recovery/语言）覆盖用户同名 section，用户独有 section 保留，未知冲突 AskUserQuestion 选择。

**settings-hooks.json 合并**：按 command 字段去重——用户已有 hook command 保留不重复，模板新 command append 到对应 event，用户独有 permissions/env 完整保留。

**重新部署**：`.story-deployed` 不存在→全新安装执行 Phase 2；存在且 `agents_version: 12`→AskUserQuestion 确认是否重新部署；存在但 `< 12`→提示需更新，重新执行 Phase 2 覆盖 bundle，CLAUDE.md/settings 走合并策略。

---

## 参考资料

| 文件 | 用途 |
|------|------|
| references/templates/CLAUDE.md.tmpl | 项目根 CLAUDE.md 模板 |
| references/templates/hooks/ | hook 脚本模板 + `lib/common.sh`/`lib/sentinel.sh` |
| references/templates/rules/ | path-scoped 规则模板 |
| references/templates/agents/ | 8 个 agent 定义模板（write-novel-story-architect, write-novel-character-designer, write-novel-narrative-writer, write-novel-reviewer, write-novel-story-researcher, write-novel-deconstruction-agent, write-novel-consistency-checker, write-novel-story-explorer） |
| references/agent-references/ | Agent 参考资料；部署到 `.claude/skills/write-novel-setup/references/agent-references/` |
| references/templates/settings-hooks.json | hooks 注册 JSON 片段 |
| references/templates/上下文.md.tmpl | 写作上下文模板 |
| references/config-schema.json | `.story-config.json` JSON Schema |

---

## 流程衔接

**流水线：** 部署
**位置：** 初始化（最前置）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 部署完成，开始写作 | write-novel-long-write / write-novel-short-write | `/write-novel-long-write` 或 `/write-novel-short-write` |
| 导入已有小说做拆解 | write-novel-import | `/write-novel-import` |
| 需要浏览器登录态（扫榜/拆文取原文） | browser-cdp | `/browser-cdp` |

后续所有 skill 可通过读取项目根 `.story-config.json` 获取项目参数，无需重复询问。
