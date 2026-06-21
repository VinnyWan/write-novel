## Context

项目中有多个 skill 和 agent 引用 `artifact-protocols.md` 作为产物创建模板。文件实际存在于 `write-novel-long-write/references/artifact-protocols.md`，但以下两个引用路径指向不存在的文件：

| 引用方 | 引用路径 | 解析后绝对路径 | 状态 |
|--------|---------|---------------|------|
| `write-novel-setup/SKILL.md` | `references/artifact-protocols.md` | `write-novel-setup/references/artifact-protocols.md` | 缺失 |
| `write-novel-story-architect.md` | `write-novel-setup/references/agent-references/artifact-protocols.md` | 同上 | 缺失 |
| `write-novel-long-write/SKILL.md` | `references/artifact-protocols.md` | `write-novel-long-write/references/artifact-protocols.md` | 存在 |

## Goals / Non-Goals

**Goals:**
- 补齐两个缺失路径，使所有引用可解析

**Non-Goals:**
- 不修改 artifact-protocols.md 内容
- 不调整引用方中的路径

## Decisions

**方案：符号链接**

路径1 (`write-novel-setup/references/artifact-protocols.md`) 使用符号链接指向源文件。这样源文件更新时自动同步，无需维护多个副本。

路径2 (`write-novel-setup/references/agent-references/artifact-protocols.md`) 同样使用符号链接指向源文件。

备选方案（已排除）：
- **硬拷贝**：简单但会导致内容不同步，源文件更新后拷贝过期。
- **指针文件**（写 "see <path>"）：不标准，各 agent 需要额外解析逻辑。

选择符号链接的理由：git 跟踪符号链接，跨平台兼容（macOS/Linux），源文件更新自动生效。

## Risks / Trade-offs

- Windows 符号链接兼容性：当前开发环境为 macOS，生产环境为 Linux，不涉及 Windows。此风险可接受。
- Git 对符号链接的处理：Git 原生支持符号链接，`git clone` 后可正常解析。
