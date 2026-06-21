# analyze-short：短篇拆文 Stage 2-6 + Phase 7 门控

scope=short 时的完整管道执行细节。Stage 路由表见主 SKILL.md。

---

## 上下文加载

启动时只读核心三项：
1. **进度**：`_meta.json`（`stages_completed[]`、`last_stage_in_progress`、`genre_detected`、`word_count`）
2. **本阶段计划**：根据 resume 契约确定下一 Stage 及其输入
3. **方法论三件套**：`output-contract.md`（Stage→文件映射）、`output-templates.md`（模板+质量门控）、`material-decomposition.md`（方法论+质量标准）

其余对照标尺在拆解对应题材/维度时按需 Read。

---

## 题材识别（Phase 1.3）

用户提到具体题材→加载 `genre-catalog.md` 对应章节作拆文标尺。常见关键词：

| 关键词 | 题材 |
|--------|------|
| 追妻火葬场/渣男后悔 | 追妻 |
| 重生复仇/前世今生 | 重生复仇 |
| 死后视角/灵魂旁观 | 死人文学 |
| 小三/出轨/知三当三 | 小三 |
| 世情/现实/婆媳 | 世情 |

扫不到则 `genre_detected = "通用"`。

---

## Stage 写盘协议（crash safety）

每个 Stage 开始前：
1. 把 `_meta.json.last_stage_in_progress` 置为当前 Stage 编号
2. 该 Stage 所有目标文件写完
3. non-empty / 最小长度检查
4. 通过 → 清空 `last_stage_in_progress`，append 到 `stages_completed[]`
5. 不通过 → resume 时该 Stage 整段重跑

---

## Stage 2-6 详细要求

### Stage 2：结构+情节节点

- 故事核：一句话概括核心冲突
- 故事梗概：200-400 字完整情节
- 功能分段：≥4 段，必须含开端/发展/高潮/结局
- 情节节点清单：按字数分档提取（3000字→10-15节点，8000字→20-30节点，15000字→30-40节点）

### Stage 3：情感线+爆点

- 情感曲线：≥5 节点，标注情绪类型和强度
- 爆点分析 6 维度：爆点类型/位置/铺垫方式/情绪冲击/功能/读者反应预期
- 期待感分析：读者在每段结束时的问题/期待

### Stage 4：反转+写作手法

- 前置反转检查：确认 Stage 2 是否有反转结构
- 反转机制：铺垫≥2条，含反转类型（视角/身份/动机/时间线/信息/认知）
- 写作手法：≥5 项维度（POV/对话/时间/信息/其他）

### Stage 5：人物+开头结尾

- 所有人物：分类（主角/反派/配角/功能角色）+ 功能标签 + 功能评估
- 开头分析：前 50/100 字，钩子类型 + 信息建立
- 结尾分析：收束检查（信息揭示/情绪收束/余韵）

### Stage 6：综合评估

- 五维评分：故事核/结构/情感/人物/文笔
- 爆点性 + 话题性
- 共鸣分析：≥3 层（情感共鸣/经历共鸣/价值观共鸣）
- 可复用结构：≥3 条
- 节奏速报
- 写入 `_meta.json.structure_counts`

---

## Phase 7 门控验收详情

### 7.1 拆文报告 AI 腔自检

扫描 `拆文报告.md` 全文 against `banned-words.md` + `anti-ai-writing.md` 句式规则。

跳过源文引用——以 `>` 开头的引用行、表格中「关键台词/原文引用」列的引号直引不计入。

- 命中 → 不写 `stages_completed[6]`，列出命中位置
- 未命中 → 继续 7.2

### 7.2 `_meta.json.structure_counts` 数值校验

| 字段 | 最低值 |
|------|--------|
| `structure_counts.beats` | ≥ 4 |
| `structure_counts.hooks` | ≥ 3 |
| `structure_counts.setup_clues` | ≥ 3 |
| `structure_counts.character_archetypes` | ≥ 2 |
| `structure_counts.reusable_structures` | ≥ 3 |
| `structure_counts.reversal_type` | 在枚举内（视角/身份/动机/时间线/信息/认知） |
| `genre_detected` | 非空 |

### 7.3 `output-templates.md` [BLOCK] 项扫描

扫描所有 `[BLOCK]` 标注项，确认对应产出段已完成。`[WARN]` 项不阻断。

### 7.4 通过

7.1 + 7.2 + 7.3 全通过 → 清空 `last_stage_in_progress`，append `6` 到 `stages_completed[]`。

---

## 非标文本分段

对话体、聊天记录、帖子体、书信体等非标准章节格式：
- 先按时间/说话人切换/信息揭示点分段
- 再映射到开端、发展、高潮、结局
- 不要机械按自然段数量切分
