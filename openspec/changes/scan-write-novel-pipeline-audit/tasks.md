## 1. 修复 write-novel-scan scripts 目录

- [x] 1.1 创建 `write-novel/skills/write-novel-scan/scripts/` 目录
- [x] 1.2 从 `write-novel/skills/write-novel-long-scan/scripts/` 复制 6 个文件到新 scripts 目录（cdp-utils.js, qidian-rank-scraper.js, fanqie-rank-scraper.js, qimao-rank-scraper.js, jjwxc-rank-scraper.js, ciweimao-rank-scraper.js）
- [x] 1.3 从 `write-novel/skills/write-novel-short-scan/scripts/` 复制 2 个文件到新 scripts 目录（heiyan-booklist-scraper.js, dz-browse-scraper.js），跳过重复的 cdp-utils.js
- [x] 1.4 验证 scan skill SKILL.md Phase 1.5 引用的 7 个脚本文件均存在于新 scripts/ 目录

## 2. 修复 write-novel-review stub 指针文件

- [x] 2.1 更新 `write-novel/skills/write-novel-review/references/anti-ai-writing.md` 指针路径指向 `../../../references/shared/anti-ai-writing.md`
- [x] 2.2 更新 `write-novel/skills/write-novel-review/references/banned-words.md` 指针路径指向 `../../../references/shared/banned-words.md`
- [x] 2.3 更新 `write-novel/skills/write-novel-review/references/character-relations.md` 指针路径指向 `../../../references/shared/character-relations.md`
- [x] 2.4 更新 `write-novel/skills/write-novel-review/references/dialogue-mastery.md` 指针路径指向 `../../../references/shared/dialogue-mastery.md`
- [x] 2.5 更新 `write-novel/skills/write-novel-review/references/plot-core-methods.md` 指针路径指向 `../../../references/shared/plot-core-methods.md`
- [x] 2.6 更新 `write-novel/skills/write-novel-review/references/quality-checklist.md` 指针路径指向 `../../../references/shared/quality-checklist.md`

## 3. 修复 report-template.md 引用断链

- [x] 3.1 创建 `write-novel/skills/write-novel-import/references/shared/` 目录
- [x] 3.2 在 `write-novel/skills/write-novel-import/references/shared/report-template.md` 创建指针文件，指向 `../../../references/shared/report-template.md`
- [x] 3.3 创建 `write-novel/skills/write-novel-deslop/references/shared/` 目录
- [x] 3.4 在 `write-novel/skills/write-novel-deslop/references/shared/report-template.md` 创建指针文件，指向 `../../../references/shared/report-template.md`

## 4. normalize-punctuation.js 去重

- [x] 4.1 验证 `write-novel/scripts/normalize-punctuation.js` 为最新版本（与各 skill 副本做 diff 对比，如有差异选择最完整版本覆盖共享源）
- [x] 4.2 将 `write-novel/skills/write-novel-long-write/scripts/normalize-punctuation.js` 替换为指针文件，指向共享源
- [x] 4.3 将 `write-novel/skills/write-novel-short-write/scripts/normalize-punctuation.js` 替换为指针文件，指向共享源
- [x] 4.4 将 `write-novel/skills/write-novel-deslop/scripts/normalize-punctuation.js` 替换为指针文件，指向共享源
- [x] 4.5 将 `write-novel/skills/write-novel-review/scripts/normalize-punctuation.js` 替换为指针文件，指向共享源

## 5. 更新 MANIFEST.yaml

- [x] 5.1 更新 `whitelist_real_files` 中旧 scan skill 条目：`write-novel-long-scan/references/*` → `write-novel-scan/references/*`，`write-novel-short-scan/references/*` → 移除（合并到 scan）
- [x] 5.2 更新 `whitelist_real_files` 中旧 analyze skill 条目：`write-novel-long-analyze/references/*` → `write-novel-analyze/references/*`，`write-novel-short-analyze/references/*` → `write-novel-analyze/references/*`
- [x] 5.3 补充缺失的 whitelist 条目：`write-novel-scan/references/scan-common.md`、`write-novel-analyze/references/analyze-common.md`、`write-novel-analyze/references/stage2-agent-strategy.md`、`write-novel-analyze/references/output-contract.md`

## 6. 最终验证

- [x] 6.1 运行 `find write-novel -type l ! -exec test -e {} \; -print` 确认无断链
- [x] 6.2 确认所有 SKILL.md 中引用的 `references/` 路径对应的文件均存在
- [x] 6.3 确认所有 agent .md 中引用的 `agent-references/` 文件均存在
- [x] 6.4 确认 write-novel-scan SKILL.md Phase 1.5 中引用的所有脚本文件存在
