## Context

项目经 v2.2→v2.3 瘦身后，hooks / agents / skills / references 四个子系统已完成重构，但 session lifecycle 和 routing layer 仍有摩擦点遗留。以下分析基于当前 `main` 分支源码状态。

### 1. Session start 部署检测

`session_start.sh` 第 20-34 行的部署检测逻辑：

```bash
if sentinel_exists "$ROOT/.story-deployed"; then
  # 自检 hooks 完整性（通过 .claude/hooks/ 下文件存在性）
  ...
else
  OUTPUT+="[WARN] 写作环境未部署。运行 /write-novel-setup 初始化。\n"
fi
```

问题：`sentinel_exists` 检查 `$ROOT/.story-deployed` 文件存在性。该文件是 `write-novel-setup` skill 的部署标记，但 setup 流程在 deploy 阶段写入此文件到项目根目录的 `.story-deployed`。当前项目根目录并无此文件（写入逻辑可能在特定书目录），导致每次 session start 均触发误报。

根本原因：部署标记与实际部署状态脱钩。hooks 文件和 lib 函数库都已通过 Claude Code 插件机制正确安装（在 CLAUDE_PLUGIN_ROOT 路径下），但 sentinel 文件缺乏可靠的创建/维护机制。

### 2. 路由层旧命名空间

`SKILL.md` 第 64-100 行保留了大量旧命名空间兼容映射：

- `webnovel-*` 系列（5 个）：`webnovel-write`, `webnovel-plan`, `webnovel-query`, `webnovel-review`, `webnovel-init`, `webnovel-dashboard`
- 旧 `write-novel-*` 长格式（7 个）：`write-novel-long-write(旧长形式)`, `write-novel-plan`, `write-novel-query(旧长形式)`, `write-novel-deslop(旧长形式)`, `write-novel-review(旧长形式)`, `write-novel-setup(旧长形式)`, `write-novel-cover(旧长形式)`

这些映射在 v0.3→v2.0 迁移期间作为过渡方案引入，当前活跃触发词已全部规范化为 `write-novel-*` 短格式。Superpowers 加载的 skill 表中的 `write-novel:story-*` 前缀与当前插件命名空间一致，不存在旧名调用路径。

### 3. MANIFEST.yaml 与文件系统不同步

`references/shared/MANIFEST.yaml` 定义了两个索引：
- `shared_sources`：24 个共享源文件的版本、base_skill、备注
- `whitelist_real_files`：允许在 skill 本地 references/ 下以实体存在的文件

`cleanup-stale-references-and-check-gaps` 变更完成后，以下 14 个文件将从 `shared/` 移除：
- 4 个中文文件：删除（不登记）
- 6 个 schema：移至 `references/archive/`
- 5 个案例样本：移至 `references/rules/`

但 MANIFEST.yaml 的 `shared_sources` 列表未反映这些变更。此外，新增的 `references/rules/` 目录需要建立索引机制。

## Goals / Non-Goals

**Goals:**
- 消除 session start 的误报警告，改为基于实际 hooks 文件存在性的检测
- 精简 SKILL.md 路由表，移除 5 个 `webnovel-*` + 7 个旧 `write-novel-*` 长格式兼容条目
- 更新 MANIFEST.yaml，移除已删除/归档文件的 shared_sources 条目，为 rules/ 目录添加索引

**Non-Goals:**
- 不修改 sentinel.sh 的 `sentinel_exists` 函数本身（保持向后兼容）
- 不删除 SKILL.md 路由表中的 `故事系统旧命名空间兼容` 章节标题（保留注释意图）
- 不重新设计 MANIFEST.yaml schema（保持现有结构）
- 不改变插件注册或 superpowers 加载逻辑

## Decisions

### D1: .story-deployed 检测改为 hooks 文件自检

**方案**：将第一层判断从 `sentinel_exists "$ROOT/.story-deployed"` 改为直接检查 hooks 文件是否存在于 `$ROOT/.claude/hooks/` 或 `$CLAUDE_PLUGIN_ROOT/hooks/`。

**替代方案**：
- 方案 A：在 setup skill 中确保每次部署都写入 `.story-deployed` — 但 setup 流程只对"书目录"做 deploy，项目根目录的 hooks 由插件机制安装，不经过 setup。
- 方案 B：完全删除 sentinel 检查 — 但失去 hooks 缺失时的修复提示能力。

**选择 D1**：改为直接检查 hooks 文件。插件机制已保证 hooks 安装，文件存在即可判断部署状态。只有当 hooks 文件真的缺失时才报警，让用户重跑 setup。

### D2: 路由兼容条目移除方式

**方案**：从路由表的 "旧命名空间兼容" section 移除 12 个条目，保留 section 标题并添加一句说明"v2.3 已清理旧命名空间"。

**替代方案**：
- 方案 A：完全删除兼容 section — 可能让未来读者不知道曾经存在过这些命名。
- 方案 B：只注释不删除 — 继续占用上下文窗口。

**选择 D2**：移除条目但保留标题 + 简短说明。route table 自身的 30 行是 session 加载时进入上下文的，精简后节省 ~100 tokens。

### D3: MANIFEST.yaml 维护策略

**方案**：`shared_sources` 只保留仍在 `references/shared/` 中活跃的源文件；为 `references/rules/` 和 `references/archive/` 各添加一个简短索引 section。

**替代方案**：
- 方案 A：MANIFEST 保持原样，仅跑 static-check 来验证 — static-check 只做悬空检测不做源索引，无法替代。
- 方案 B：拆成三个 YAML 文件 — 简单场景下过度设计。

**选择 D3**：单文件维护，扩展 section。MANIFEST 是 references 的 canonical index，需要与文件系统一致。

## Risks / Trade-offs

- [旧命名空间移除] 若存在外部脚本或用户宏调用 `webnovel-init` 等旧命令，会路由失败 → 缓解：CHANGELOG 记录 breaking change，skill 注册表中已无旧名。
- [Session start 变更] 若项目确实未部署（.claude/hooks/ 为空），新逻辑走 hooks 文件检查也能正确检测缺失并提示 → 文件检查比 sentinel 更可靠。
- [MANIFEST 更新] 若 `cleanup-stale-references-and-check-gaps` 变更尚未完成所有文件移动，MANIFEST 更新需对应 → 本变更设计为在后者的基础上执行，依赖关系明确。

## Migration Plan

1. `cleanup-stale-references-and-check-gaps` 变更先完成（文件移动 + 删除 + 版本对齐）
2. 本变更的 tasks 按顺序执行：session_start.sh → SKILL.md → MANIFEST.yaml
3. 每步执行后跑 `static-check.sh` 确认无回归
4. 无需 rollback 策略（纯文本修改，git revert 即可）
