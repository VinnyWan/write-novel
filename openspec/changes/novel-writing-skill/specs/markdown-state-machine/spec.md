## ADDED Requirements

### Requirement: 全局写作状态 Frontmatter 驱动

`全局写作状态.md` 文件的 YAML Frontmatter SHALL 是全书写作进度的单一真相来源。所有技能在需要进度数据时 MUST 读取此文件，而非查询其他来源。

#### Scenario: 读取当前进度
- **WHEN** 任何 skill 或 agent 需要知道当前写到哪一章
- **THEN** 系统读取 `全局写作状态.md` 的 Frontmatter 字段 `当前分卷` 和 `当前章节`

#### Scenario: 更新进度
- **WHEN** 一章写作完成
- **THEN** 系统更新 `全局写作状态.md` 的 Frontmatter：`已完成章数` +1，`已完成字数` 累加本章字数，更新 `最后更新章节` 和 `最后更新时间`

### Requirement: 伏笔生命周期三态追踪

`伏笔与线索回收池.md` SHALL 使用三态状态机追踪每条伏笔：🟡已埋 → 🟠发展中 → 🟢已回收。

#### Scenario: 埋设新伏笔
- **WHEN** 新章节写完且在 `单章细纲.md` 的 `埋下伏笔` 字段中出现新伏笔 ID
- **THEN** 系统在 `伏笔与线索回收池.md` 的伏笔总表中新增一行，状态为 🟡已埋，记录埋设章节和预计回收章节

#### Scenario: 伏笔推进
- **WHEN** 后续章节引用了已有伏笔 ID
- **THEN** 系统将该伏笔状态从 🟡已埋 更新为 🟠发展中

#### Scenario: 伏笔回收
- **WHEN** 某章揭晓了伏笔的全部内容
- **THEN** 系统将该伏笔状态更新为 🟢已回收，记录实际回收章节

#### Scenario: 逾期预警
- **WHEN** 当前章节序号超过某伏笔的预计回收章节但状态仍不是 🟢已回收
- **THEN** 系统在下次写作 Prompt 中注入该伏笔的回收提醒

### Requirement: 双语链接按需加载

Markdown 文件中的 `[[路径/文件名]]` 语法 SHALL 被解析为文件引用，在写作上下文中自动加载对应文件的关键信息。

#### Scenario: 解析人物引用
- **WHEN** 细纲或正文中出现 `[[人物/林动]]`
- **THEN** 系统读取 `人物/林动.md`，提取该角色的 `当前状态`、`当前境界`、`当前位置` 三个字段注入写作上下文

#### Scenario: 解析伏笔引用
- **WHEN** 细纲中出现 `[[伏笔/F001]]`
- **THEN** 系统从 `伏笔与线索回收池.md` 中提取该伏笔的当前状态和内容摘要

### Requirement: 用户保护区

`全局写作状态.md` 中 `<!-- USER_AREA_START -->` 和 `<!-- USER_AREA_END -->` 之间的内容 SHALL 永不被子动更新修改。

#### Scenario: 状态更新时跳过用户区
- **WHEN** 系统更新 `全局写作状态.md` 的 Frontmatter 或其他区域
- **THEN** 系统 MUST NOT 修改 `<!-- USER_AREA_START -->` 和 `<!-- USER_AREA_END -->` 之间的任何内容
