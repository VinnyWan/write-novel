## ADDED Requirements

### Requirement: 细纲包含事件、冲突、转折点三要素

Phase 3b 细纲 frontmatter SHALL 包含以下三个必填字段：

- `event`：本章核心事件（1 句话，描述发生了什么）
- `conflict`：冲突对象，含 `type`（利益争夺/理念冲突/情感纠葛/生存危机/信息不对称）、`parties`（冲突双方数组）、`intensity`（1-5 整数）
- `turning_point`：转折点对象，含 `is_turning`（布尔值）、`type`（人物弧线/剧情方向/势力格局/世界观揭示，仅 is_turning=true 时必填）、`description`（1 句话描述转折内容）

#### Scenario: 细纲产出包含三要素

- **WHEN** Phase 3b 产出某章细纲
- **THEN** frontmatter 中的 event/conflict/turning_point 三个字段均非空
- **THEN** conflict.intensity 在 1-5 范围内
- **THEN** 若 turning_point.is_turning 为 false，turning_point.type 和 turning_point.description 可为空

#### Scenario: 三要素缺失时细纲被拒绝

- **WHEN** 细纲 frontmatter 缺少 event、conflict 或 turning_point 任一字段
- **THEN** Phase 3b 的 Gate 校验失败
- **THEN** 系统提示具体缺失字段，要求补全后重新提交

### Requirement: 冲突强度分级指导叙事节奏

冲突强度字段 SHALL 用于指导叙事节奏控制：
- 强度 1-2：过渡章/铺垫章，允许较慢节奏
- 强度 3：标准章，须有明确的冲突推进
- 强度 4-5：高潮章/关键章，须有清晰的对峙或爆发场面

连续 3 章强度 <= 2 SHALL 触发 reviewer 警告"节奏过缓"。

#### Scenario: 节奏过缓告警

- **WHEN** reviewer agent 检测到连续 3 章 conflict.intensity <= 2
- **THEN** 在审查报告中生成 "节奏过缓" 警告
- **THEN** 建议在下一章安排强度 >= 4 的事件

### Requirement: 转折点类型区分叙事功能

转折点类型 SHALL 用于 reviewer agent 交叉校验：
- "人物弧线"转折点 → 校验该章是否有对应的角色行为变化
- "剧情方向"转折点 → 校验后续章节的剧情走向是否与此转折一致
- "势力格局"转折点 → 校验势力关系是否在后续章节中体现了变化
- "世界观揭示"转折点 → 校验新揭示的设定是否在后续章节中持续生效

#### Scenario: 转折点类型校验

- **WHEN** reviewer agent 在 Phase 5 检测到 turning_point.is_turning = true 的章节
- **THEN** 根据转折点类型执行对应的交叉校验
- **THEN** 若发现转折未在后续章节生效，生成"转折未落地"问题
