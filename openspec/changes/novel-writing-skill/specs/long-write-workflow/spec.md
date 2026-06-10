## ADDED Requirements

### Requirement: 三大写作场景支持

`write-novel-long-write` skill SHALL 支持三种写作场景，按优先级匹配：日更续写 > 大修/回炉 > 开书。

#### Scenario: 匹配日更续写场景
- **WHEN** 用户输入包含"日更""续写""继续写"关键词，且项目已有正文和历史章节摘要
- **THEN** 系统加载 `references/workflow-daily.md`，执行日更串行批量流程

#### Scenario: 匹配大修场景
- **WHEN** 用户输入包含"修改第X章""回炉""重写第X章"
- **THEN** 系统加载 `references/workflow-revision.md`，执行定向修改流程

#### Scenario: 匹配开书场景
- **WHEN** 用户输入"开书""写大纲"或项目目录为空
- **THEN** 系统执行完整 Phase 1→2→3→4→5 流程

### Requirement: 开书五阶段流程

开书流程 MUST 按以下顺序执行，每个阶段产出可验证的 Markdown 文件：

#### Scenario: Phase 1 - 确认选题
- **WHEN** 进入开书流程
- **THEN** 系统先检查 `选题决策.md` 是否存在，存在则读取推荐选题；否则通过提问确认题材、核心情绪、对标书

#### Scenario: Phase 2 - 设定搭建
- **WHEN** Phase 1 确认选题后
- **THEN** 系统创建/更新 `世界设定/世界观.md`、`人物/` 下的角色卡片，使用对应的 Markdown 模板

#### Scenario: Phase 3 - 大纲细纲
- **WHEN** 设定搭建完成后
- **THEN** 系统创建 `分卷大纲/` 目录，为每卷生成大纲文件和单章细纲文件

#### Scenario: Phase 4 - 正文写作
- **WHEN** 大纲细纲准备就绪后
- **THEN** 系统加载本章细纲、相关人物卡片、待回收伏笔、全局写作状态，组装写作上下文，生成正文

#### Scenario: Phase 5 - 续航闭环
- **WHEN** 每章正文生成完毕后
- **THEN** 系统执行：章节存档 → 摘要生成 → 状态更新 → 伏笔追踪，全部通过文件读写完成

### Requirement: 情绪驱动方法论

系统 SHALL 从情绪出发设计场景，每个场景 MUST 服务于一个明确的情绪目标。

#### Scenario: 场景设计必须先定情绪
- **WHEN** AI 设计一个场景时
- **THEN** 必须明确该场景交付的核心情绪（如爽感释放、期待感、意难平），场景中的每个节拍都服务于该情绪

### Requirement: 上下文最小化加载

写作每章时，系统 SHALL 只加载"不知道就会写错"的信息，而非加载所有项目文件。

#### Scenario: 加载本章写作上下文
- **WHEN** 准备写第 N 章
- **THEN** 系统加载：本章细纲、本章涉及角色的当前状态、待回收伏笔列表、相关设定片段、全局写作状态中的系统提示词和高压线。不加载其他章节正文或其他卷的细纲。
