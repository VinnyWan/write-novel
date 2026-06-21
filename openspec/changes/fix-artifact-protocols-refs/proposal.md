## Why

`artifact-protocols.md` 是项目核心的产物模板文件，被 `write-novel-long-write`、`write-novel-setup`、`write-novel-story-architect` 等多个 skill/agent 引用。文件实际存在于 `write-novel-long-write/references/artifact-protocols.md`，但 `write-novel-setup` 和 `story-architect` 引用的路径指向了不存在的文件，导致运行时模板加载失败。

## What Changes

- 在 `write-novel-setup/references/artifact-protocols.md` 创建符号链接，指向 `../../write-novel-long-write/references/artifact-protocols.md`
- 在 `write-novel-setup/references/agent-references/artifact-protocols.md` 声明该文件为代理引用（写一个指针文件指向源文件）

## Capabilities

### New Capabilities

无新能力——此变更仅修复文件引用断链。

### Modified Capabilities

无——不涉及 spec 级别的行为变更。

## Impact

- `write-novel/skills/write-novel-setup/SKILL.md`：`references/artifact-protocols.md` 引用将可解析
- `write-novel/agents/write-novel-story-architect.md`：`write-novel-setup/references/agent-references/artifact-protocols.md` 引用将可解析
- MANIFEST.yaml 中已有的 `write-novel-long-write/references/artifact-protocols.md` 条目不受影响
