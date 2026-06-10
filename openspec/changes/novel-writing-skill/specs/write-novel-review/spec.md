## ADDED Requirements

### Requirement: 多视角对抗式审查（Phase 1 — 并行）

`write-novel-review` skill SHALL 首先使用 4 个并行 Agent（full 模式）从不同角度审查文本，主线程综合裁决。每个 Agent 只关注其指定维度。

#### Scenario: 四维并行审查
- **WHEN** 用户输入"/审查"并提供待审文本
- **THEN** 系统 spawn 4 个 Agent 并行执行审查：
  - Agent 1: 结构审查（剧情连贯性、节奏、伏笔回收）
  - Agent 2: 文风审查（句式多样性、口语化程度、AI 痕迹）
  - Agent 3: 连贯性审查（前后设定一致性、角色行为一致性）
  - Agent 4: 爽点审查（情绪递送、期待感控制、高潮有效性）

#### Scenario: 综合裁决
- **WHEN** 4 个 Agent 全部返回审查结果
- **THEN** 主线程按严重性排序问题，去重后生成统一审查报告，包含问题描述、定位、修改建议

### Requirement: 质量管道串行加工（Phase 2 — 串行）

审查报告生成后，系统 SHALL 依次启动 3 个质量管道 Agent，串行执行，上一轮输出作为下一轮的输入文本。

#### Scenario: 串行质量管道完整流程
- **WHEN** Phase 1 审查报告生成完毕
- **THEN** 系统按以下顺序串行执行：
  1. **write-novel-deslop-agent**（去 AI 味）：接收正文 + 审查报告 → 逐句扫描改写 AI 痕迹 → 输出清洁文本
  2. **write-novel-senior-editor**（资深编辑）：接收清洁文本 → 商业向深度审稿 → 输出编辑意见 + 修改建议
  3. **write-novel-picky-reader**（挑剔读者）：接收清洁文本 + 编辑意见 → 真实读者体验评估 → 输出读后感 + 弃书风险评估

#### Scenario: 管道中途中断
- **WHEN** 任一 Agent 发现致命级别问题（如剧情逻辑断裂、人设崩塌）
- **THEN** 该 Agent 在输出中标注致命问题，管道暂停，主线程向用户汇报并要求决策（继续/回炉修改）

### Requirement: 去 AI 味 Agent

`write-novel-deslop-agent` SHALL 对文本进行深度清洁，不仅检测 AI 痕迹，而是直接改写输出清洁文本。

#### Scenario: 逐句改写
- **WHEN** Agent 接收到待处理文本
- **THEN** 逐句扫描，对命中禁用词表的句子进行替换改写，确保不改变原意、不增删剧情信息、保留作者风格特征

#### Scenario: 输出清洁文本
- **WHEN** 处理完成
- **THEN** 输出完整清洁文本 + 修改日志（列出每一处修改的位置和原因）

### Requirement: 资深编辑 Agent

`write-novel-senior-editor` SHALL 以终点线精修编辑的标准审核清洁后的文本，关注商业价值和阅读体验。

#### Scenario: 商业向审稿
- **WHEN** Agent 接收到清洁文本
- **THEN** 从以下维度逐项审核：
  - 开篇钩子：第一段是否足够抓人
  - 节奏控制：有无拖沓或过快的段落
  - 爽点密度：每 3000 字至少一个情绪释放点
  - 人物辨识度：角色对话能否仅通过语气区分
  - 章节钩子：结尾是否让人想翻下一章
  - 输出编辑审稿意见，每个问题附具体位置和修改建议

### Requirement: 挑剔读者 Agent

`write-novel-picky-reader` SHALL 模拟真实挑剔网文读者的第一反应，不讲术语，只讲真实感受。

#### Scenario: 读者体验评估
- **WHEN** Agent 接收到清洁文本 + 编辑意见
- **THEN** 以读者口吻写出真实读后感受，回答以下问题：
  - 第一句话抓住我没有？前三段我想继续读吗？
  - 哪里让我出戏了？（设定矛盾、逻辑 bug、角色行为不符人设）
  - 情绪有没有打到我？哪个节点最爽/最感动/最紧张？
  - 读完本章我想点下一章吗？如果不想，为什么？
  - 输出"弃书风险评估"：低/中/高 + 一句理由

### Requirement: 审查报告汇总格式

最终输出 MUST 包含完整的质量管道加工过程报告。

#### Scenario: 生成最终审查报告
- **WHEN** 质量管道全部执行完毕
- **THEN** 输出包含以下分区的 Markdown 报告：
  - `## Phase 1: 四维审查摘要`（综合裁决结果）
  - `## Phase 2: 去 AI 味修改日志`（deslop-agent 输出）
  - `## Phase 3: 编辑审稿意见`（editor 输出）
  - `## Phase 4: 读者真实感受`（reader 输出）
  - `## 综合评估`（弃书风险 + 是否建议发布）
