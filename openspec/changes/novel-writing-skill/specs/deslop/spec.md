## ADDED Requirements

### Requirement: AI 写作痕迹检测

`write-novel-deslop` skill SHALL 检测文本中的 AI 写作痕迹，包括但不限于：模板化句式、过度书面化表达、重复句式结构、缺乏口语节奏的对话。

#### Scenario: 检测模板化句式
- **WHEN** 用户输入"/去AI味"并提供文本
- **THEN** 系统扫描文本，标记"在……的过程中""与此同时""此时此刻"等高频 AI 句式，返回检测结果和修改建议

#### Scenario: 检测连续重复句式
- **WHEN** 文本出现连续三个自然段以"他/她"开头
- **THEN** 系统标记为需要修改，建议交替主语位置或用动作/环境/对话开头

### Requirement: 禁用词表强制执行

系统 SHALL 维护一份写作禁用词表（`references/banned-words.md`），在检测和生成过程中强制执行。

#### Scenario: 生成时过滤禁用词
- **WHEN** AI 在写作流程中生成正文
- **THEN** 系统在生成前将禁用词表注入 Prompt 的高压线区域，要求 AI 不得使用这些词汇

#### Scenario: 检测时标记禁用词
- **WHEN** 用户对已有文本运行 deslop
- **THEN** 系统逐行匹配禁用词表，用 Markdown 注释或高亮标记违规位置

### Requirement: 中文口语化适配

系统 SHALL 针对中国网络文学的口语化标准进行检测和优化，确保对话自然、叙述有节奏感、打斗有画面感。

#### Scenario: 对话去书面化
- **WHEN** 检测到角色对话使用过于书面化的表达（如"然而""因此""此外"在对话中出现）
- **THEN** 系统标记并建议口语化替换
