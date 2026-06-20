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

---

## Phase 1：检测项目状态

1. 检查当前目录是否已部署过（存在 `.story-deployed`）
   - 如果已存在 → 使用 AskUserQuestion 确认是否重新部署
2. 检查是否有书名目录（包含 `追踪/` 子目录的目录，或用户自定义结构）
   - 有 → 识别为长篇项目，显示当前项目信息
   - 无 → 识别为新项目或短篇项目
3. 检查 `.claude/settings.local.json` 是否存在
   - 存在 → 读取现有配置，后续合并
   - 不存在 → 后续创建新文件
4. 检查 `.active-book` 文件是否存在
   - 存在 → 显示当前活跃书目
   - 不存在 → 跳过
5. 检查 `.story-config.json` 是否存在
   - 存在 → 读取并展示当前配置摘要（作者、书名、平台、目标字数、题材、风格），使用 AskUserQuestion 询问「是否修改配置？」。选择「是」→ 进入 Phase 1.5 且预填已有值；选择「否」→ 跳过 Phase 1.5 直接进入 Phase 2
   - 不存在 → 进入 Phase 1.5 全新收集模式
   - 无书名目录 → 进入 Phase 1.5 全新收集模式（即使有 `.story-config.json`）
6. **旧命名部署迁移检测**（v0.4.0 命名空间统一后）：扫描 `.claude/skills/story-*` 目录和 `.claude/agents/{narrative-writer,reviewer,character-designer,consistency-checker,deconstruction-agent,chapter-extractor,story-architect,story-explorer,story-researcher}.md` 裸名/旧名文件
   - 检测到旧命名部署 → 进入「旧命名迁移」流程（见 Phase 2.0a）
   - 未检测到 → 跳过迁移，按正常 Phase 2 部署

## Phase 1.5：项目配置向导

> 配置向导收集项目核心参数，持久化到 `.story-config.json`。
> 后续所有 skill 可从此文件读取参数，消除重复询问。

### 1.5.1 必填轮（4 问，顺序固定）

**Q1 — 作者笔名**
- 使用 AskUserQuestion 询问作者笔名
- 默认值：`git config user.name` 的输出（如可获取）
- 写入 `author_name`

**Q2 — 书名**
- 使用 AskUserQuestion 询问书名
- 默认值：Phase 1 检测到的书名目录名（如有）
- 写入 `book_name`

**Q3 — 目标平台**
- 使用 AskUserQuestion（单选）询问目标平台
- 选项：起点、番茄、晋江、知乎盐言、其他
- 写入 `target_platform`

**Q4 — 目标字数**
- 使用 AskUserQuestion（单选）询问目标字数
- 选项：30万字（短篇）、100万字（中篇）、200万字+（长篇超）、自定义
- 选择「自定义」时，弹出文本输入框让用户输入数字（单位：万字）
- 写入 `target_words`（整数，单位：字）

### 1.5.2 选填轮确认

- 必填轮 4 项收集完成后，使用 AskUserQuestion 询问「是否进行更多配置（题材、风格、存储结构）？」
- 选项：「继续配置」/「跳过，使用默认值」
- 选择「跳过」→ 选填字段写入默认值，直接进入 1.5.3 配置摘要确认

### 1.5.3 选填轮（3 问，可跳过）

**Q5 — 题材/流派**
- 使用 AskUserQuestion（单选）询问题材
- 选项：从 `agent-references/genre-catalog.md` 的路由表第一列提取热门题材（取前 8 个作为选项），末尾加「其他」
- 写入 `genre`

**Q6 — 写作风格偏好**
- 使用 AskUserQuestion（单选）询问风格偏好
- 选项：热血、轻松、暗黑、幽默、不指定
- 写入 `style_preference`

**Q7 — 存储结构**
- 使用 AskUserQuestion（单选）询问存储结构
- 选项：单书（`{书名}/`）、多书并列
- 写入 `storage_structure`

### 1.5.4 配置摘要确认

- 展示完整配置摘要（键值对列表）
- 使用 AskUserQuestion 询问「确认以上配置？」
- 选项：「确认」→ 写入 `.story-config.json` 并进入 Phase 2；「重新填写」→ 返回 1.5.1 必填轮第一问

### 1.5.5 模板占位符替换

> 配置确认后、Phase 2 部署前执行。

从 `.story-config.json` 读取值，按以下映射批量替换：

| 占位符 | 配置字段 | 格式 |
|--------|----------|------|
| `{作者名}` | `author_name` | 原值 |
| `{书名}` | `book_name` | 原值 |
| `{项目名}` | `book_name` | 同书名 |
| `{目标平台}` | `target_platform` | 原值 |
| `{目标字数}` | `target_words` | 格式化为「X万字」 |
| `{题材}` | `genre` | 原值 |

对于未收集到的字段（用户跳过且无默认值），对应占位符保留原样不替换。

## Phase 2：部署基础设施

使用 AskUserQuestion 确认部署位置后，依次执行。

### 2.0a 旧命名迁移（条件执行）

> 仅当 Phase 1 步骤 6 检测到旧命名部署时执行；否则跳过本节直接进入 2.0。

**迁移原则**：dry-run 列出变更 → 用户确认 → 原子迁移 → 迁移后无新旧并存。

1. **扫描旧命名部署**：
   - `Glob .claude/skills/story-*` 列出所有旧命名 skill 目录
   - `Glob .claude/agents/{narrative-writer,reviewer,character-designer,consistency-checker,deconstruction-agent,chapter-extractor,story-architect,story-explorer,story-researcher}.md` 列出所有裸名/旧名 agent 文件
   - 读取 `.claude/settings.local.json`（如存在），扫描 hooks 部分中引用旧 skill 名的 command 字段
2. **生成 dry-run 变更清单**（不执行任何修改）：
   - skill 目录重命名映射：`.claude/skills/story-X` → `.claude/skills/write-novel-X`（14 项）
   - agent 文件重命名映射：`.claude/agents/{裸名}.md` → `.claude/agents/write-novel-{裸名}.md`（9 项）
   - settings.local.json hook command 路径更新项（如 `/story-review` → `/write-novel-review`）
   - 列出将被删除的旧路径（迁移后原路径应不存在）
3. **AskUserQuestion 确认**：展示 dry-run 清单，询问「确认迁移？」
   - 「确认」→ 继续步骤 4
   - 「取消」→ 跳过迁移，仅执行 Phase 2 全新部署（旧命名文件保留，会在后续巡检中由 write-novel-doctor 标记）
4. **执行迁移**（顺序敏感）：
   - 4a. 先备份当前 `.claude/settings.local.json` 到 `.claude/settings.local.json.bak.{timestamp}`
   - 4b. `git mv` 或 `mv` 14 个 skill 目录：`story-X` → `write-novel-X`
   - 4c. `git mv` 或 `mv` 9 个 agent 文件：裸名 → `write-novel-` 前缀
   - 4d. 更新 `.claude/settings.local.json` 中 hook command 路径引用：`/story-X` → `/write-novel-X`、`story-X` 目录路径 → `write-novel-X`
   - 4e. 如 `.story-deployed` 存在，更新 `agents_version` 为 `12`、`setup_skill_version` 为 `1.2.0`
5. **迁移后校验**（无新旧并存）：
   - `Glob .claude/skills/story-*` 应零命中
   - `Glob .claude/agents/{narrative-writer,reviewer,...}.md` 应零命中（裸名）
   - `grep -r 'subagent_type: "story-' .claude/` 应零命中
   - `grep -r 'subagent_type: "narrative-writer"' .claude/` 应零命中
   - 任一校验失败 → 回滚（从备份恢复 settings.local.json，git mv 回去），报告失败原因
6. **追加 run-ledger 迁移记录**：
   - 在 `.story-deployed` 同目录的 `.story-run-ledger`（如不存在则创建）追加一行：
     ```
     {timestamp} | namespace-migration | story-* → write-novel-* | {迁移 skill 数} skills, {迁移 agent 数} agents | success
     ```
7. **进入 Phase 2.0 常规部署清单**：迁移完成后，继续执行下方 2.0 部署清单（覆盖更新 agents/hooks/rules 至最新版本）。

### 2.0 部署清单（机械可检查）

| Source path | Target path | Owner class | Merge mode | Validation check |
|-------------|-------------|-------------|------------|------------------|
| `skills/write-novel-setup/references/templates/CLAUDE.md.tmpl` | `CLAUDE.md` | user+managed | marker/section merge | contains story skill routing sections |
| `skills/write-novel-setup/references/templates/hooks/` | `.claude/hooks/` | write-novel-setup managed | recursive replace | `session-*.sh`, `detect-story-gaps.sh`, `validate-story-commit.sh`, `lib/common.sh`, `lib/sentinel.sh` exist |
| `skills/write-novel-setup/references/templates/rules/*.md` | `.claude/rules/*.md` | write-novel-setup managed | replace | every rule contains `paths` frontmatter |
| `skills/write-novel-setup/references/templates/agents/*.md` | `.claude/agents/*.md` | write-novel-setup managed | replace | 9 agent files exist |
| `skills/write-novel-setup/references/agent-references/*.md` | `.claude/skills/write-novel-setup/references/agent-references/*.md` | write-novel-setup managed | replace | every `write-novel-setup/references/agent-references/*.md` reference resolves |
| `skills/write-novel-setup/references/templates/settings-hooks.json` | `.claude/settings.local.json` | user+managed | merge by hook command | hook JSON valid and registered commands deduped |
| `skills/write-novel-setup/references/templates/上下文.md.tmpl` | `{书名}/追踪/上下文.md` | user state | create only if absent | never overwrite existing writing context |
| generated config | `.story-config.json` | user state | create only if absent | contains `version`, `author_name`, `book_name`, `target_platform`, `target_words` |
| generated sentinel | `.story-deployed` | write-novel-setup managed | replace | contains `agents_version`, `setup_skill_version`, `target_cli`, `resolver_strategy`, `references_dir` |
| generated script | `start-dashboard.sh` | write-novel-setup managed | replace | executable, contains absolute path to `novel-dashboard` |

### 2.1 部署 CLAUDE.md

- 读取 `skills/write-novel-setup/references/templates/CLAUDE.md.tmpl`
- 替换占位符（已在 Phase 1.5.5 完成，此处使用替换后的内容）
- 写入项目根目录 `CLAUDE.md`（如已存在，按「CLAUDE.md 合并策略」处理）

### 2.2 部署 Hooks

- **递归复制完整目录树**：将 `skills/write-novel-setup/references/templates/hooks/` 复制到用户项目 `.claude/hooks/`
- 必须保留子目录 `lib/`，其中：
  - `lib/common.sh` 提供 `project_root`、`discover_active_book`、`discover_all_books`
  - `lib/sentinel.sh` 提供 `.story-deployed` 字段读取
- 只需对 `.claude/hooks/*.sh` 设置执行权限（`chmod +x`）；`lib/*.sh` 由 hook `source`，不要求可执行位

### 2.3 部署 Rules

- 读取 `skills/write-novel-setup/references/templates/rules/` 下所有 `.md` 文件
- 复制到用户项目的 `.claude/rules/` 目录

### 2.4 部署 Agents

- 读取 `skills/write-novel-setup/references/templates/agents/` 下所有 `.md` 文件
- 复制到用户项目的 `.claude/agents/` 目录
- Agent 文件属于 write-novel-setup 管理文件，可安全覆盖；版本升级时按 `UPGRADING.md` 的版本检测结果重新部署

### 2.4.1 Agent 兼容性处理

- Agent frontmatter 以 Claude Code 为主；OpenClaw/qclaw 等只要支持 AgentSkills，未知字段（如 `memory`、`skills`、`disallowedTools`）应被忽略。若目标工具报 frontmatter 错误，保留 `name`、`description`、`tools` 三项，删除不支持字段后再部署。
- 部署到项目后，agent 内引用的参考资料必须走 `write-novel-setup/references/agent-references/*.md` 这一本 skill 内复制路径；不要跨 skill 引用其他 skill 的 references。若全局安装路径不同，优先用项目内 `.claude/skills/` 或 `skills/` 作为规范路径前缀，其次用工具的 skill 搜索能力，不要假定固定绝对路径。

### 2.4.2 部署 Agent References

- 将 `skills/write-novel-setup/references/agent-references/` 下所有 `.md` 复制到项目内 `.claude/skills/write-novel-setup/references/agent-references/`
- 如目标项目已经使用项目本地 `skills/` 目录，也可以同步复制到 `skills/write-novel-setup/references/agent-references/` 作为 fallback，但不得只复制 fallback 而遗漏 `.claude/skills/` 主路径
- 校验：凡 agent 或 reference 中出现 `write-novel-setup/references/agent-references/<file>.md`，源包与目标包都必须存在 `<file>.md`

### 2.5 部署 Session State 模板

- 读取 `skills/write-novel-setup/references/templates/上下文.md.tmpl`
- 仅当已识别为长篇书目且 `{书名}/追踪/` 已存在时，创建缺失的 `{书名}/追踪/上下文.md`
- 如果目标文件已存在，不覆盖；短篇项目不得因此创建 `追踪/` 目录

### 2.6 合并 Hooks 注册到 settings.local.json

> 兼容性说明：`settings-hooks.json` 中 PreToolUse 的 `if` 字段使用 Claude Code hook 条件语法，需要运行环境支持 hook-level if。若目标工具不支持该字段，hook 脚本本身仍会自检并 advisory-only 退出；部署时可删除该 `if` 字段并保留 matcher + command。

- 读取 `skills/write-novel-setup/references/templates/settings-hooks.json`
- 读取用户项目的 `.claude/settings.local.json`（如存在）
- 合并 hooks 配置（按「settings-hooks.json 合并算法」处理）
- 写入 `.claude/settings.local.json`

### 2.7 创建部署标记

- 创建 `.story-deployed` 文件（sentinel file）
- 写入以下字段（YAML `key: value` 格式，hook 用 `references/templates/hooks/lib/sentinel.sh` 读取）：
  ```
  deployed_at: <date -u +"%Y-%m-%dT%H:%M:%SZ">
  agents_version: 11
  setup_skill_version: 1.2.0
  target_cli: claude-code
  resolver_strategy: project-local-skill-reference
  references_dir: .claude/skills/write-novel-setup/references/agent-references
  ```
- 此文件供 session-start.sh 和写作 skill 检测部署状态，避免重复提示
- 如果 `.story-deployed` 已存在但无 `agents_version` 或版本 < 10，提示用户重新运行 write-novel-setup 以更新 hooks/agents/rules/reference bundle（具体变更见 `UPGRADING.md`）

### 2.8 生成 Dashboard 启动 wrapper

- 在项目根目录生成 `start-dashboard.sh`：
  ```bash
  #!/usr/bin/env bash
  exec "<write-novel-tool-root>/bin/novel-dashboard" "$@"
  ```
- `<write-novel-tool-root>` 为本 skill 文件所在位置的 `../../`（即 skill 文件向上两级目录）的绝对路径
- 赋予可执行权限：`chmod +x <project-root>/start-dashboard.sh`
- 提示用户：「可通过 `./start-dashboard.sh` 在项目目录中一键启动 Dashboard」

## Phase 3：验证安装

1. 验证 hooks 注册：
   - 检查 `.claude/settings.local.json` 中的 hooks 字段是否正确
   - 检查 `.claude/hooks/` 下的脚本是否存在且有执行权限
   - 检查 `.claude/hooks/lib/common.sh` 与 `.claude/hooks/lib/sentinel.sh` 是否存在
2. 验证 rules 路径：
   - 检查 `.claude/rules/` 下的规则文件是否存在且包含 `paths` frontmatter
3. 验证 agents：
   - 检查 `.claude/agents/` 下的 9 个 agent 定义文件是否存在（write-novel-story-architect, character-designer, narrative-writer, reviewer, write-novel-story-researcher, deconstruction-agent, consistency-checker, write-novel-story-explorer, chapter-extractor）
4. 验证 agent reference bundle：
   - 检查 `.claude/skills/write-novel-setup/references/agent-references/` 下 reference 文件完整
   - 检查所有 `write-novel-setup/references/agent-references/<file>.md` 都能解析到 deployed bundle
5. 验证部署标记：
   - 检查 `.story-deployed` 是否存在且包含时间戳、`agents_version: 10`、`setup_skill_version: 1.1.1`、`target_cli`、`resolver_strategy`、`references_dir`
6. 验证项目配置：
   - 检查 `.story-config.json` 是否存在
   - 如存在，校验必填字段（`author_name`、`book_name`、`target_platform`、`target_words`）均非空
   - 缺少必填字段时输出警告「⚠️ .story-config.json 配置不完整，建议重新运行 /write-novel-setup」
7. 验证 Dashboard wrapper：
   - 检查 `start-dashboard.sh` 是否存在且可执行
   - 检查其内容包含正确的 `novel-dashboard` 绝对路径
8. 输出安装报告：
   - 列出所有已部署的文件
   - 列出需要注意的事项（如已有配置已合并）
   - 提示用户可以开始使用 `/write-novel-long-write` 或 `/write-novel-short-write`

---

## 模板占位符

> 占位符替换已在 Phase 1.5.5 中自动完成。此段保留供手动干预时参考。

| 占位符 | 替换规则 | 示例 |
|--------|----------|------|
| `{项目名}` | `book_name` 字段值或项目目录名 | 《剑来》、《暗卫》 |
| `{书名}` | `book_name` 字段值 | 同 `{项目名}` |
| `{目标平台}` | `target_platform` 字段值 | 起点、番茄、晋江、知乎盐言 |
| `{作者名}` | `author_name` 字段值 | 未指定时用「作者」 |

替换时去掉花括号。未收集到的占位符保留原样不替换。

## CLAUDE.md 合并策略

用户已有 CLAUDE.md 时，按 marker/section 合并：
1. 优先识别 write-novel-setup 管理块标记（如果旧项目已有标记，只替换标记内内容）
2. 无标记时，读取用户现有 CLAUDE.md，按 `##` 标题切分为 section map
3. 读取模板 CLAUDE.md.tmpl，同样切分
4. 模板中的标准 section（Skill 路由表、项目配置、文件结构、协作规则、Context Recovery、语言）**覆盖**用户同名 section
5. 用户独有的 section（自定义内容）**保留**不动
6. 未知冲突用 AskUserQuestion 让用户选择保留哪个版本

## settings-hooks.json 合并算法

hooks 注册合并按 command 字段去重：
1. 读取用户现有 `.claude/settings.local.json`（如存在），提取 hooks 部分
2. 读取 `settings-hooks.json` 模板，提取要注册的 hooks
3. 对每个 hook event（SessionStart、PreToolUse 等）：
   - 用户已有的 hook command → 保留，不重复添加
   - 模板中的新 hook command → append 到对应 event 的 hooks 数组
   - 用户独有的其他配置（permissions、env 等）→ 完整保留
4. 写入合并后的完整 settings.local.json

## 重新部署

- `.story-deployed` 不存在 → 全新安装，Phase 2 全部执行
- `.story-deployed` 存在且 `agents_version: 11` → 提示已部署，AskUserQuestion 确认是否重新部署
- `.story-deployed` 存在但 `agents_version` < 11 → 提示需要更新，重新执行 Phase 2 覆盖 agents/hooks/rules/reference bundle，CLAUDE.md 和 settings.local.json 走合并策略

---

## 参考资料

| 文件 | 用途 |
|------|------|
| references/templates/CLAUDE.md.tmpl | 项目根 CLAUDE.md 模板 |
| references/templates/hooks/ | 6 个 hook 脚本模板 + `lib/common.sh`/`lib/sentinel.sh` |
| references/templates/rules/ | 4 条 path-scoped 规则模板 |
| references/templates/agents/ | 9 个 agent 定义模板（write-novel-story-architect, character-designer, narrative-writer, reviewer, write-novel-story-researcher, deconstruction-agent, consistency-checker, write-novel-story-explorer, chapter-extractor） |
| references/agent-references/ | Agent 模板自带的参考资料副本；部署到 `.claude/skills/write-novel-setup/references/agent-references/`，避免跨 skill references |
| references/templates/settings-hooks.json | hooks 注册 JSON 片段 |
| references/templates/上下文.md.tmpl | 写作上下文模板 |
| references/config-schema.json | `.story-config.json` 的 JSON Schema 参考文件 |

---

## 流程衔接

**流水线：** 部署
**位置：** 初始化（最前置）

| 时机 | 跳转到 | 命令 |
|---|---|---|
| 部署完成，开始写作 | write-novel-long-write / write-novel-short-write | `/write-novel-long-write` 或 `/write-novel-short-write` |
| 导入已有小说做拆解 | write-novel-import | `/write-novel-import` |
| 需要浏览器登录态（扫榜/拆文取原文） | browser-cdp | `/browser-cdp` |

后续所有 skill 可通过读取项目根目录 `.story-config.json` 获取项目参数（作者、书名、平台、题材、字数目标），无需重复询问。
