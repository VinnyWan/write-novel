# 线索标注体系：Quest / Fire / Constellation

三线分类适用于所有长篇网文。每章必须标注一条主线索，同一线索连续章节有硬上限。

---

## 三线定义

| 线索 | 标签 | 含义 | 典型内容 |
|------|------|------|---------|
| **Quest** | 主线 | 主角核心目标的推进 | 升级、夺宝、复仇推进、主线冲突 |
| **Fire** | 支线/感情线 | 次要情节、关系发展 | 感情线、配角故事、势力经营、日常 |
| **Constellation** | 伏笔线 | 埋伏笔或回收伏笔为主的章节 | 新线索埋设、旧伏笔回收、设定揭示 |

---

## 连续约束（硬上限）

| 线索 | 最多连续章数 | 超出后果 | 例外条件 |
|------|------------|---------|---------|
| Quest | 不限 | — | — |
| Fire | **2 章** | 读者感觉主线停滞 | 卷末收束章可放宽至 3 |
| Constellation | **1 章** | 连续埋伏笔不回收 → 读者债务堆积 | 揭示章（集中回收多个伏笔）不算 constellation |

---

## 间隔约束

| 约束 | 规则 | 检测方式 |
|------|------|---------|
| Fire 回归 | Fire 线索后必须在 5 章内回到 Quest | 检查 `strand` 序列 |
| Constellation 回收 | Constellation 埋入的伏笔必须在其后 10 章内至少有一次 `in_progress` 推进 | 检查 `追踪/foreshadowing.md` |
| 三线轮转 | 任意 5 章窗口内必须至少出现 2 种线索 | 滑动窗口检测 |

---

## 线索标注流程

### 写前（Prewrite Gate）

1. 读取前一章的 `strand` 和 `strand_sequence` 字段
2. 若前一章 Fire 且 `strand_sequence ≥ 2` → 提示"必须切换回 Quest 或 Constellation"
3. 若前一章 Constellation 且 `strand_sequence ≥ 1` → 提示"必须切换回 Quest 或 Fire"
4. 检查最近 5 章线索分布，窗口内只有 1 种线索 → 提示"需引入第二线索"

### 写后（Postcommit Gate）

1. 更新本章 `strand` 和 `strand_sequence`
2. 同线索 → `strand_sequence += 1`
3. 切换线索 → `strand_sequence = 1`

---

## 线索切换决策表

| 当前状态 | 推荐切换至 | 理由 |
|---------|-----------|------|
| Quest 连续 5+ 章 | Fire | 主线需要情感缓冲，读者需要呼吸 |
| Fire 连续 2 章 | Quest | 回到主线推进，防止读者流失 |
| Constellation 刚埋完 | Quest | 伏笔埋完即回主线，让伏笔"沉淀" |
| 高潮前 1 章 | Quest | 高潮前不引入新线索 |
| 卷末收束章 | Quest + Constellation | 回收伏笔的同时推进主线收束 |
| 卷首开篇章 | Quest | 新卷用主线开场，快速建立方向感 |

---

## 质量检查

- [ ] 本章 `strand` 标签与正文内容匹配（不标错）
- [ ] Fire 连续未超过 2 章
- [ ] Constellation 连续未超过 1 章
- [ ] 最近 5 章至少覆盖 2 种线索
- [ ] `strand_sequence` 计数正确递增或归零
