## ADDED Requirements

### Requirement: 目录名称全中文

项目中的所有目录名称 SHALL 使用中文，不得使用英文或拼音。标准目录结构如下：

#### Scenario: 验证项目目录结构
- **WHEN** 创建或验证一个写作项目
- **THEN** 以下目录 MUST 存在且使用中文名：`人物/`、`世界设定/`、`分卷大纲/`、`章节草稿/`、`历史章节摘要/`、`全局设定/`

### Requirement: 文件名称全中文

所有数据文件 SHALL 使用中文文件名。角色文件以角色名为文件名（如 `林动.md`），章节文件以章序号+标题命名（如 `第1章_序章.md`）。

#### Scenario: 创建新角色文件
- **WHEN** 用户创建新角色
- **THEN** 系统在 `人物/` 目录下以 `{角色姓名}.md` 格式创建文件

#### Scenario: 创建新章节正文
- **WHEN** 写作完成一章
- **THEN** 系统在 `章节草稿/` 目录下以 `第{N}章_{标题}.md` 格式存档

### Requirement: Frontmatter 键名全中文

所有 `.md` 文件的 YAML Frontmatter 键名 SHALL 使用中文。禁止使用英文键名。

#### Scenario: 人物卡片 Frontmatter
- **WHEN** 创建人物卡片
- **THEN** Frontmatter 中必须使用中文键名：`姓名`（非 `name`）、`当前境界`（非 `current_level`）、`关联角色`（非 `related_characters`）等

#### Scenario: 细纲 Frontmatter
- **WHEN** 创建单章细纲
- **THEN** Frontmatter 中必须使用中文键名：`所属分卷`、`章节序号`、`本章核心冲突`、`出场角色`、`埋下伏笔`、`期待感钩子`、`字数预期`、`关联伏笔ID`

### Requirement: NFC/NFD 兼容性

系统 SHALL 处理 macOS（NFD）和 Linux/Windows（NFC）之间的 Unicode 编码差异，确保中文文件名在不同操作系统间保持一致。

#### Scenario: macOS 创建的文件在 Linux 上读取
- **WHEN** 一个在 macOS 上创建的中文文件名在 Linux 上被引用
- **THEN** 系统自动进行 Unicode 规范化，将 NFD 转换为 NFC（或反之），确保 `[[人物/林动]]` 能正确解析
