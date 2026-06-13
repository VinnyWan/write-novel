# 故事系统 Markdown 规范

Agent 执行写作流程时，遵循以下 Markdown 契约链：**Contract → Commit → Projection**。

---

## 一、Contract（契约层）

契约文件定义"应该写什么"，是写作前的约束。

### 1.1 全局设定契约：`设定/MASTER_SETTING.md`

```yaml
---
book_title: "书名"
genre: "题材"
target_platform: "起点|番茄|晋江|其他"
total_volumes: N
target_words: N万
---
```

正文为自由格式 Markdown，描述世界观、力量体系、势力分布等全局设定。

### 1.2 卷契约：`大纲/Volume-N.md`

```yaml
---
volume: N
title: "卷名"
theme: "卷主题"
arc_goal: "本卷主线目标"
estimated_chapters: N
strands:
  quest: ["主线线索描述"]
  fire: ["支线/感情线描述"]
  constellation: ["伏笔线描述"]
---
```

正文为卷级大纲，描述本卷主要事件、角色弧线、节奏规划。

### 1.3 章契约：`大纲/Chapter-NNN.md`

```yaml
---
chapter: NNN
volume: N
title: "章名"
target_words: N
strand: quest|fire|constellation
strand_sequence: N  # 当前线索连续章节数
contract_nodes:
  cbn: ["开篇钩子"]
  cpns: ["中间爽点/推进点"]
  cen: ["结尾悬念/读者期待"]
hook_type: crisis|suspense|desire|emotion|choice
payoff_density: N  # 本章微兑现数量
emotion_curve: "铺垫→升温→释放|平缓→紧张→反转|..."
---
```

正文为本章细纲，描述场景序列和关键情节点。

---

## 二、Commit（提交层）

`正文/Chapter-NNN.md` 是事实提交。Agent 写入正文时，YAML frontmatter 记录元数据：

```yaml
---
chapter: NNN
volume: N
word_count: NNNN
status: draft|polished|reviewed
contract_nodes_completed:
  cbn: true|false
  cpns: true|false
  cen: true|false
strand: quest|fire|constellation
hook_type: crisis|suspense|desire|emotion|choice
payoff_count: N
created_at: "YYYY-MM-DD"
updated_at: "YYYY-MM-DD"
---
```

正文内容为小说原文，Markdown 格式：
- `##` 二级标题作为场景分隔
- 段落间无空行
- 对话使用半角双引号 `"..."`

---

## 三、Projection（投影层）

投影文件是正文和设定的**派生数据**，Agent 从正文重建。所有投影文件位于 `追踪/` 目录。

### 3.1 写作状态：`追踪/state.md`

```yaml
---
active_book: "书名"
current_volume: N
current_chapter: NNN
total_words: NNNNNN
last_written_at: "YYYY-MM-DD"
phase: planning|writing|reviewing|polishing
---
```

### 3.2 进度摘要：`追踪/progress.md`

```yaml
---
volumes_completed: N
chapters_completed: N
daily_word_count: N
weekly_word_count: N
quality_trend: improving|stable|declining
---
```

表格记录每章完成情况：

| 章号 | 字数 | 状态 | 完稿日期 | 质量分 |
|------|------|------|---------|--------|
| 001 | NNNN | reviewed | YYYY-MM-DD | A/B/C |

### 3.3 角色状态：`追踪/characters.md`

```yaml
---
total_characters: N
updated_at: "YYYY-MM-DD"
---
```

每个角色一个 `###` 小节，含：
- 当前状态/境界/位置
- 最近变更（章节号 + 摘要）
- 关联角色（双向链接 `[[人物/角色名]]`）

### 3.4 伏笔状态：`追踪/foreshadowing.md`

```yaml
---
total_foreshadows: N
pending: N
resolved: N
overdue: N
---
```

| ID | 描述 | 埋入章 | 计划回收章 | 实际回收章 | 状态 | 逾期 |
|----|------|--------|-----------|-----------|------|------|
| F001 | ... | 005 | 015 | - | pending | false |

---

## 四、投影重建流程

Agent 在以下时机重建投影文件：
1. 每章写完后增量更新
2. `/story-doctor` 触发全量重建
3. 投影文件损坏或缺失时自动触发

增量更新只修改变更相关的字段和行；全量重建从正文和设定重新扫描生成。
