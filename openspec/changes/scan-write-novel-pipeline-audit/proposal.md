## Why

write-novel 工具集经过多轮合并优化（scan/analyze 合并、agent 合并、references 共享），产生了多条断链：新合并的 skill 缺少必需的 scripts 目录、跨 skill 的共享引用路径无法解析、旧 skill 目录残留但引用未更新、MANIFEST.yaml 记录过期。这些断链在运行时会导致脚本不可用、参考文件加载失败、spawn 降级等问题。本次变更对全部 17 个 skill 和 8 个 agent 做端到端链路审计，修复所有发现的断链和缺失。

## What Changes

- **修复 write-novel-scan 缺少 scripts 目录**：从旧 long-scan/short-scan 迁移 7 个采集脚本到新 scan 目录，确保 Phase 1.5 脚本采集模式可用
- **修复 references/shared/report-template.md 引用断链**：import 和 deslop 两个 skill 引用 `references/shared/report-template.md` 但路径解析不到全局 shared 目录，需在各个 skill 的 references/ 下创建指针文件
- **修复 write-novel-review 的 6 个 stub 指针文件**：当前指向 `references/shared/*.md` 但 review references/ 下无 shared/ 子目录，需修正指针路径
- **清理旧 skill 目录残留**：long-scan/short-scan/long-analyze/short-analyze 4 个旧目录保留 SKILL.md 作为兼容别名即可，references 和 scripts 迁移后清理
- **更新 MANIFEST.yaml**：将 whitelist_real_files 中的旧 skill 名更新为新 skill 名，补充新合并 skill 的引用条目
- **去重 normalize-punctuation.js**：5 份副本统一到 `write-novel/scripts/`，各 skill 引用共享位置
- **修正 write-novel-import 描述中的旧引用**：description frontmatter 中仍引用已合并的 `write-novel-long-analyze`

## Capabilities

### New Capabilities

无新能力——此变更仅修复链路断链和缺失文件。

### Modified Capabilities

- `write-novel-scan`: 补齐 scripts/ 目录，修复 Phase 1.5 脚本采集模式
- `write-novel-review`: 修复 stub 指针文件路径，使参考文件可正确加载
- `write-novel-import`: 修复 `references/shared/report-template.md` 引用路径
- `write-novel-deslop`: 修复 `references/shared/report-template.md` 引用路径

## Impact

- 受影响 skill：write-novel-scan、write-novel-review、write-novel-import、write-novel-deslop
- 受影响文件：`write-novel/references/shared/MANIFEST.yaml`、旧 long-scan/short-scan/long-analyze/short-analyze 目录
- 受影响脚本：7 个采集 scraper 脚本（迁移）、normalize-punctuation.js（去重）
- 不改变任何 skill 的外部接口、路由表、触发词
