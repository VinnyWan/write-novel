# 两阶段写门校验

每章写作经过两道门，Agent 在 SKILL.md 流程中依次执行。

---

## Gate 1: Prewrite（写前校验）

**时机**：加载上下文后、开始写正文前

**首项检查——细纲 frontmatter 字段完整性自检**：

| 检查项 | 方法 | 不通过处理 |
|--------|------|-----------|
| frontmatter 字段完整 | 检查细纲 frontmatter 必需字段齐全：`cbn`/`cpns`/`cen`/`target_words`/`strand`/`hook_type`/`payoff_density`/`event`/`conflict`/`turning_point` | 缺失则从细纲正文重新提取补全 frontmatter，最多重试 2 次；仍失败标记该章 `status: needs_review` 提示用户，不阻塞其他章 |
| 三要素存在性 | 检查 `event`/`conflict`/`turning_point` 三个字段均非空（D8 新增） | 任一缺失 → **阻塞**，Gate 拒绝通过，提示补全后重新提交 |

> 自检责任统一在 Gate 1（写前最后一道关）兜底，不再依赖 Phase 3b 生成时自检。

**默认体裁画像**（爽点密度与线配比检查的依据）：

无对标书时使用默认画像；有对标书或题材特殊参数时，按 `references/genre-writing-formulas.md` 对应题材参数覆盖默认值。

| 参数 | 默认值 |
|------|--------|
| 爽点密度下限 | 常规章 ≥1 微兑现/章；高潮章 ≥2 |
| 线配比上限 | 主线连续 ≥3 章提示切支线；支线连续 ≥2 章提示切回主线 |
| 钩子偏好 | 每章必须有章尾钩子，类型不限 |

**后续检查项**：

| 检查项 | 方法 | 不通过处理 |
|--------|------|-----------|
| 爽点密度预估 | 从细纲 frontmatter 读取 `payoff_density`，对比适用画像（默认或题材覆盖）最低要求 | 提示补充细纲爽点规划 |
| 线配比检查 | 检查 `strand` 字段：若前一章同线索已连续达到适用画像上限 | 提示或自动调整 |
| 伏笔逾期检测 | 读取 `追踪/状态.md` 伏笔 section，有逾期伏笔时提示优先回收 | 提示 |

**输出**：prewrite 检查报告（通过/警告/阻塞），阻塞项必须解决才能开始写作。

---

## Gate 2: Postwrite（写后校验 + 追踪更新）

**时机**：正文写完后、正式收尾前

### 质量校验

| 检查项 | 方法 | 不通过处理 |
|--------|------|-----------|
| 字数达标 | `word_count` 对比 `target_words`（±20% 容忍） | 低于 80% 阻塞落盘 |
| 合约合规 | 正文覆盖细纲 frontmatter 中所有 `must_cover` 项，无 `forbidden` 项出现 | 标注未完成项 |
| 钩子议程履行 | 细纲含 `must_advance_hooks` 时，逐条核对正文是否**实际推进**该伏笔（写入新进展或明显推动其状态）；`eligible_resolve_hooks` 为非强制提示项，未回收仅提醒不阻塞 | 未推进项按错误目录 `hook-agenda-unfulfilled` 报为「必须处理」，阻塞本章提交 |
| hook 有效 | 检查结尾段落是否包含有效的 hook（悬念/情绪/选择等，不含总结式结尾） | 标注弱结尾 |
| 格式合规 | 段落长度（无超长段）、对话独立、无多余空行 | 自动修复 |
| 禁用词扫描 | 对照 `references/banned-words.md`，一级词命中即替换 | 一级词阻塞落盘 |
| 去 AI 味 | 对照 `references/banned-words.md` 手动扫描正文，并参照 `references/anti-ai-writing.md` 对高频 AI 指纹做定性裁定 | 报告问题数 |
| 投影一致性 | 正文中角色状态与 `追踪/状态.md` 角色状态 section 一致 | 标注差异 |
| 段落覆盖率（D8 新增） | 实际段落数 vs 计划段落数（偏差 ≤1），整体段落覆盖率 ≥ 80% | 未达标 → 警告级，不阻塞，写入 `追踪/状态.md` 问题列表 |
| 冲突强度节奏（D8 新增） | 连续 3 章 `conflict.intensity` ≤ 2 | 生成「节奏过缓」警告，建议下章安排强度 ≥4 的事件 |
| 转折点落地（D8 新增） | 检查标记 `turning_point.is_turning: true` 的章节，按 type 交叉校验后续章节是否体现了转折 | 未体现 → 生成「转折未落地」问题 |
| 剧情线推进（D8 新增） | 支线连续 30 章无推进（strand 字段未引用该线名） | 生成「支线停滞」警告 |

### 追踪原子更新

质量校验全部通过（或仅警告级无阻塞项）后，一次性更新 `追踪/状态.md`：
- 伏笔 section：新增/回收伏笔
- 时间线 section：记录事件时序
- 角色状态 section：身份/能力/关系/公众形象变化
- 功法状态 section：功法获得或阶段升级

### CHAPTER_COMMIT

创建不可变提交记录 `.story-system/commits/chapter_{N}.commit.md`：

```yaml
---
chapter: N
timestamp: {ISO 8601}
word_count: {实际字数}
contract_compliance:
  cbn: pass | partial | fail
  cpns: "完成 X/3"
  cen: pass | fail
  must_cover: "覆盖 Y/Z 项"
  forbidden: "零违规" | "发现 X 处违规"
  must_advance_hooks: "推进 X/Y 项" | "未声明"   # 仅细纲声明了该字段时记录
  eligible_resolve_hooks: "回收 X/Y 项" | "未声明"
review_status: pass | partial | fail
deai_status: pass | revised | skipped
projection_status: full | partial | failed
---
```

### 收尾

- ledger 写入：`追踪/run-ledger.md` 追加一行（章号/步骤/状态/时间戳/产物路径）
- 连续线索计数：更新 strand_sequence
- 备份（可选）：复制正文到 `备份/第{N}章_*.md`
