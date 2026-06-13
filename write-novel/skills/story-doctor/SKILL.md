---
name: story-doctor
description: |
  项目诊断与维护工具。对网文项目做只读体检/诊断，检查目录/文件/依赖/产物完整性；
  同时支持从会话提取成功写作模式并写入项目记忆。
  触发方式：/story-doctor、「体检」「诊断」「检查项目」（旧触发词：/webnovel-doctor）
  合并自：webnovel-doctor + webnovel-learn
allowed-tools: Read Bash
---

# story-doctor：项目诊断与维护

## 两大功能

### A. 项目体检（来自 webnovel-doctor）

只读诊断当前书项目：确认所处阶段应有的目录、文件、依赖是否完整。

### B. 模式学习（来自 webnovel-learn）

从当前会话提取成功写作模式并写入项目记忆。

---

## A. 项目体检

### 原则

1. 只读诊断：不写项目文件、不自动修复、不安装依赖、不启动 Dashboard
2. 统一用 `python -X utf8`，避免中文路径编码问题
3. 缺失项按阶段解释影响与修复建议

### 检查项

| 检查项 | 说明 |
|--------|------|
| 目录结构 | `设定/` `大纲/` `正文/` `追踪/` `人物/` 是否存在 |
| 核心文件 | `设定/MASTER_SETTING.md` `追踪/state.md` `追踪/progress.md` |
| 章节完整性 | 正文章节是否连续，YAML frontmatter 是否完整 |
| 伏笔状态 | `追踪/foreshadowing.md` 中是否有逾期未回收的伏笔 |
| 角色一致性 | `追踪/characters.md` 与 `人物/` 中的角色是否一致 |
| 依赖检查 | Python 依赖是否满足 `requirements.txt` |

### 执行

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"
python -X utf8 scripts/main.py doctor --project-root "${WORKSPACE_ROOT}"
```

### 输出

- 阶段感知的诊断报告
- 每项标记：✅ 正常 / ⚠️ 警告 / ❌ 缺失
- 修复建议（由用户确认后手动执行）

---

## B. 模式学习

### 目标

提取可复用的写作模式（钩子/节奏/对话/微兑现等），追加到项目记忆。

### 执行流程

1. 确定当前项目根目录
2. 读取 `追踪/progress.md` 获取当前章节号作为上下文
3. 解析用户输入，归类 `pattern_type`：hook/pacing/dialogue/payoff/emotion/format/other
4. 调用 `python -X utf8 scripts/main.py memory add-pattern` 写入

### 模式类型

| pattern_type | 说明 | 示例 |
|-------------|------|------|
| hook | 钩子设计 | "每章结尾留悬念效果最好" |
| pacing | 节奏控制 | "打斗场景不超过3段，紧张感更集中" |
| dialogue | 对话技巧 | "配角对话带方言口音增强辨识度" |
| payoff | 微兑现 | "第3章提到的暗器在第7章用上" |
| emotion | 情绪把控 | "沈栀的冷淡要逐步破冰，每次推进一小步" |
| format | 格式技巧 | "打斗场景用短句，环境描写用长句" |
| other | 其他 | 无法归类的经验 |
