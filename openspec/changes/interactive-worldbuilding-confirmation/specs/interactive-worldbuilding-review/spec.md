## ADDED Requirements

### Requirement: Agent generates draft only

在 Phase 1.6 世界观初始化中，story-architect agent SHALL 仅生成初稿文本并返回主线程，不得直接写入 `设定/世界观.md` 或 `设定/题材定位.md`。写入操作 SHALL 由主线程在交互确认完成后执行。

#### Scenario: Agent returns draft without writing files
- **WHEN** Phase 1.6 触发且 `设定/世界观.md` 不存在
- **THEN** story-architect agent 生成世界观初稿文本
- **AND** `设定/` 目录下不产生新文件
- **AND** 初稿全文缓存在主线程记忆中

### Requirement: Worldview section-by-section confirmation

系统 SHALL 将世界观初稿按六大板块拆分，逐板展示并请求用户确认：时代背景、地理环境、势力格局、力量体系、社会结构。每板块 SHALL 提供「确认」「修改」「全部确认」三个选项。

#### Scenario: User confirms a section
- **WHEN** 系统展示「时代背景」板块内容
- **AND** 用户选择「确认」
- **THEN** 该板块标记为已确认
- **AND** 系统继续展示下一板块

#### Scenario: User modifies a section
- **WHEN** 系统展示「地理环境」板块内容
- **AND** 用户选择「修改」
- **THEN** 系统弹出文本输入框
- **AND** 用户输入修正后的完整段落
- **AND** 修正段落替换该板块原有内容并标记为已确认

#### Scenario: User approves all remaining sections at once
- **WHEN** 系统展示「势力格局」板块内容
- **AND** 用户选择「全部确认」
- **THEN** 当前及后续所有未确认板块均标记为已确认
- **AND** 跳过剩余逐个展示

### Requirement: Genre-positioning section-by-section confirmation

系统 SHALL 将题材定位初稿按三大板块拆分，逐板展示并请求用户确认：题材类型、核心梗三分法、对标作品。每板块 SHALL 提供「确认」「修改」「全部确认」三个选项。

#### Scenario: User confirms genre positioning sections
- **WHEN** 世界观六大板块全部确认完毕
- **THEN** 系统开始逐板展示题材定位三大板块
- **AND** 每板块交互选项与世界观确认一致

### Requirement: Unified write after full confirmation

所有板块确认完成后，系统 SHALL 统一将确认后的内容写入 `设定/世界观.md` 和 `设定/题材定位.md`，并执行 Phase 1.6.4 Gate 校验。

#### Scenario: All sections confirmed, files written
- **WHEN** 世界观六大板块和题材定位三大板块全部确认完毕
- **THEN** 系统写入 `设定/世界观.md` 含 frontmatter（era/world_type/power_system/target_words）
- **AND** 系统写入 `设定/题材定位.md` 含「核心梗三分法」段落
- **AND** 执行 Phase 1.6.4 校验

#### Scenario: User-modified content fails Gate check
- **WHEN** 用户修改后内容缺少必要 frontmatter 字段
- **THEN** 系统提示缺失的具体字段
- **AND** 要求用户补全后重新写入

### Requirement: Skip option for short-form projects preserved

短篇项目的 Phase 1.6 跳过逻辑保持不变。系统 SHALL 仅在长篇项目（≥ 检测到书名目录或 Phase 1.5 刚创建）时执行交互确认。

#### Scenario: Short-form project skips worldbuilding
- **WHEN** 项目为目标字数 < 100 万字且无书名目录
- **THEN** 系统提示「短篇可跳过世界观初始化」
- **AND** 不进入交互确认流程
