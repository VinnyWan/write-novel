# 断点续传：run-ledger 与智能恢复

`追踪/run-ledger.md` 记录每次写作操作，支持中断后精确定位恢复点。

---

## run-ledger.md 模板

```markdown
# 操作日志

| # | 时间 | 操作 | 章号 | 阶段 | 状态 | 字数 | 备注 |
|---|------|------|------|------|------|------|------|
| 1 | 2026-01-01 10:00 | write | 001 | - | completed | 3200 | 首章开篇 |
| 2 | 2026-01-01 10:30 | review | 001 | - | completed | - | Gate A clean |
| 3 | 2026-01-01 11:00 | write | 002 | - | started | 1500 | 中断——未完成 |
| 4 | 2026-01-02 09:00 | openbook | - | phase1 | completed | - | 选题确认 |
| 5 | 2026-01-02 14:00 | openbook | - | phase2 | interrupted | - | 核心设定未完成 |
```

### 字段说明

| 字段 | 说明 |
|------|------|
| # | 自增序号 |
| 时间 | `YYYY-MM-DD HH:MM` 格式 |
| 操作 | `write` / `review` / `deslop` / `rewrite` / `outline` / `setup` / `openbook`（开书专用） |
| 章号 | 三位数字，无章节概念的操作填 `-` |
| 阶段 | 开书专用，取值 `phase1`/`phase2`/`phase3a`/`phase3b`/`phase4`；非开书操作填 `-` |
| 状态 | `completed` / `started` / `interrupted` / `abandoned` |
| 字数 | 本章最终字数（write 操作填），非 write 操作填 `-` |
| 备注 | 自由文本，中断原因/关键决策/待处理项 |

### 开书操作说明

开书流程（Phase 1→2→3a→3b）每个 Phase 结束时追加一行 `openbook` 记录：
- `阶段` 填该 Phase 标识（phase1/phase2/phase3a/phase3b/phase4）
- Phase 产物落盘且经用户确认 → 状态 `completed`，备注记录关键决策
- Phase 中途中断（用户退出/会话结束）→ 状态 `interrupted`，备注记录断点和已完成步骤
- `章号` 一律填 `-`（开书不对应具体章节）

---

## 断点诊断流程

Agent 恢复时执行以下诊断：

1. **读取 run-ledger**：找到最后一条记录
2. **判断中断状态**：

| 最后一条状态 | 诊断 | 操作 |
|------------|------|------|
| `completed` | 上一章已完成 | 自动定位下一章，开始写作 |
| `started` | 上一章写作被打断 | 检查 `正文/第{N}章_*.md` 是否已存在且内容完整 |
| `interrupted` | 明确标记中断 | 加载已有内容，从断点继续 |
| `abandoned` | 已放弃 | 询问用户是否重试 |

3. **章节文件验证**：
   - 若 ledger 标记 `completed` 但 `正文/第{N}章_*.md` 不存在 → 警告"文件可能丢失"
   - 若 ledger 标记 `started` 但文件存在且字数 ≥ 目标的 90% → 提示"接近完成，是否补完？"
   - 若 ledger 标记 `started` 但文件不存在 → 视为全新开始

4. **上下文重建**：
   - 读取上一章完整正文（`正文/第{N-1}章_*.md`）
   - 读取当前卷纲（`大纲/卷纲_第X卷.md`）
   - 读取 `追踪/状态.md` 伏笔 section 中待回收伏笔
   - 读取 `追踪/状态.md` 角色状态 section 中相关角色状态
   - 基于以上重建写作上下文

---

## 中断恢复流程

```
1. 读取 run-ledger → 诊断中断状态
2. 验证章节文件 → 确认实际进度
3. 加载上下文（上一章正文 + 卷纲 + 追踪/状态.md 伏笔/角色状态）
4. 显示恢复摘要：「上次写到第 N 章（{status}），{备注}。继续吗？」
5. 用户确认 → 执行 Prewrite Gate → 继续写作
```

---

## 开书 Phase 级恢复

开书流程（Phase 1→2→3a→3b→4）支持 Phase 级中断与恢复。每个 Phase 的产物即 checkpoint 载体，run-ledger 的 `openbook` 行记录阶段进度。

### Phase → 交付物映射

恢复时按此表验证对应 Phase 的产物是否已落盘，判断从该 Phase 续写还是跳到下一 Phase。

| 阶段 | Phase | 完成标志（产物已落盘） |
|------|-------|----------------------|
| phase1 | 选题 | `选题决策.md` 或核心设定表已确认 |
| phase2 | 核心设定 | `设定/关系.md` + `设定/题材定位.md` 落盘 |
| phase3a | 卷纲 | `大纲/大纲.md` + `大纲/卷纲_第1卷.md` + 设定需求预览已确认 |
| phase3b | 细纲 | 首批 10 章细纲落盘 + 设定补全完成 |
| phase4 | 写作 | 进入日更/正文写作（交回现有写作流程） |

### 开书恢复诊断流程

```
1. 读取 run-ledger 末行
2. 若末行 操作=openbook 且 状态=interrupted：
   a. 读取 阶段 字段，定位中断的 Phase
   b. 按 Phase→交付物映射验证该 Phase 产物完整性
      - 产物完整 → 视为该 Phase 已完成，跳到下一 Phase 接续
      - 产物缺失/不完整 → 从该 Phase 断点继续
   c. 显示恢复摘要：「上次开书到 Phase X（{阶段名}），{备注}。从该阶段继续？」
   d. 用户确认 → 接续开书
3. 若末行 操作=openbook 且 状态=completed：
   → 定位到该 Phase 的下一 Phase 接续开书
4. 若末行操作非 openbook（或 ledger 不存在）：
   → 不触发开书恢复，按既有场景匹配规则处理
```

> phase4 是开书的终点：phase3b 验证通过后即进入日更/正文写作流程，交回 SKILL.md 的日更续写或正文写作场景，开书恢复不再管辖。

---

## run-ledger 维护规则

- 每次操作开始前追加 `started` 行
- 每次操作完成后更新为 `completed` 并填写字数
- 中断时更新为 `interrupted` 并记录原因
- 永不删除历史行，只追加
- 每 50 章归档一次：保留最近 10 条详记，更早记录压缩到 `追踪/归档/run-ledger-archive.md`
