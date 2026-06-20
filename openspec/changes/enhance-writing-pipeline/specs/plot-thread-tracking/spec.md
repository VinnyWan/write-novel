## ADDED Requirements

### Requirement: Phase 3a 产出剧情线文件

story-long-write Phase 3a（卷纲）SHALL 在卷纲产出前，先由 story-architect agent 产出 `大纲/剧情线.md`，包含：

- 主线 1 条：线名 / 核心冲突 / 起止卷 / 关键节点列表（卷:章粒度，每节点 1-2 句描述）
- 支线 2-5 条：每条含线名 / 类型（感情线/成长线/势力线/悬疑线/复仇线等）/ 核心冲突 / 起止卷 / 关键节点列表
- 每条线的状态追踪：未开始 / 推进中 / 已完成

#### Scenario: 新书剧情线设计

- **WHEN** story-architect agent 在 Phase 3a 启动卷纲设计前
- **THEN** 先产出 `大纲/剧情线.md`，含 1 条主线 + 2-5 条支线
- **THEN** 每条线标注起止卷和至少 3 个关键节点
- **THEN** 卷纲的每卷摘要标注该卷推进了哪些剧情线

#### Scenario: 缺少剧情线时卷纲产出被阻塞

- **WHEN** `大纲/剧情线.md` 不存在或内容不完整（主线缺失或支线 < 2 条）
- **THEN** Phase 3a 卷纲产出被 Gate 阻塞
- **THEN** 系统提示需先完成剧情线设计

### Requirement: 细纲和卷纲标注剧情线推进

每章细纲的 frontmatter 中 `strand` 字段 SHALL 为必填，标注该章推进的剧情线（至少 1 条，可多条）。卷纲的每卷摘要 SHALL 包含该卷的剧情线推进摘要（每条线推进到哪个关键节点）。

#### Scenario: 细纲标注剧情线

- **WHEN** Phase 3b 产出细纲
- **THEN** 每章细纲 frontmatter 必填 `strand` 字段
- **THEN** strand 字段值引用 `大纲/剧情线.md` 中定义的线名

#### Scenario: 剧情线进展检测

- **WHEN** reviewer agent 执行全文审查
- **THEN** 检查剧情线的推进状态是否符合预期
- **THEN** 若某条支线连续 30 章未推进，生成警告
