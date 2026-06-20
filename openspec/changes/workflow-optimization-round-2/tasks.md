## 1. 修复 session_start.sh 部署误报

- [ ] 1.1 修改 `write-novel/hooks/session_start.sh` 第 20-34 行：移除 `sentinel_exists "$ROOT/.story-deployed"` 作为外层判断，改为直接调用 hooks 文件自检逻辑（原 sentinel-self-check 的 8 个文件检查），统一为单层检测
- [ ] 1.2 运行 `bash write-novel/hooks/session_start.sh`（手动执行）确认不再输出 `[WARN] 写作环境未部署`
- [ ] 1.3 模拟 hooks 缺失场景：临时重命名 `lib/sentinel.sh`，确认警告正确触发；恢复后确认消失

## 2. 清理 SKILL.md 路由表旧命名空间

- [ ] 2.1 编辑 `write-novel/skills/write-novel/SKILL.md` 第 64-100 行「旧命名空间兼容」section：删除 5 个 `webnovel-*` 映射行 + 7 个旧 `write-novel-*` 长格式行；保留 section 标题并添加说明「v2.3 已清理 webnovel-* 和旧 write-novel-* 长格式命名」
- [ ] 2.2 在 CHANGELOG.md v2.3.0 条目中追加一条 breaking change note，列出被移除的旧触发词（`webnovel-write`、`webnovel-plan`、`webnovel-query`、`webnovel-review`、`webnovel-init`、`webnovel-dashboard` 及旧长格式别名）
- [ ] 2.3 运行 `bash write-novel/scripts/static-check.sh` 确认无新 FAIL（SKILL.md 修改不触发静态检查新告警）

## 3. 同步 MANIFEST.yaml

- [ ] 3.1 编辑 `write-novel/references/shared/MANIFEST.yaml` `shared_sources` section：移除已删除/归档的 10 个文件条目（context-format, projection-spec, run-ledger-format, style-cache-schema, technique-tracker-schema, verification-checklist, continuity-power-001, error-ai-slop-001, glossary-foreshadowing-001, hook-chapter-001, trope-face-slap-001 + 4 个中文文件）
- [ ] 3.2 在 MANIFEST.yaml 末尾新增 `rules_sources` section，列出 `references/rules/` 下 9 个文件（continuity-power-001, error-ai-slop-001, glossary-foreshadowing-001, hook-chapter-001, trope-face-slap-001, story-consistency, story-format, story-narrative, story-outline）
- [ ] 3.3 在 MANIFEST.yaml 末尾新增 `archived_sources` section，列出 `references/archive/` 下 6 个文件及其归档原因
- [ ] 3.4 运行 `bash write-novel/scripts/static-check.sh` 确认 MANIFEST 变更后全量 PASS

## 4. 全量验证

- [ ] 4.1 运行 `bash write-novel/scripts/static-check.sh`，确认 Total 全 PASS、Fail = 0
- [ ] 4.2 运行 `bash write-novel/scripts/check-shared-files.sh`，确认跨 skill 一致性检查 PASS
- [ ] 4.3 运行 `python3 write-novel/scripts/project_doctor.py`（若存在），确认项目健康度不下降
- [ ] 4.4 如实报告验证结果；任何无法执行的检查须说明原因
