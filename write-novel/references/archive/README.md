# 归档规范（待接线）

本目录存放从 `references/shared/` 移出的规范文件。这些文件的**内容真实有价值**（投影管线、断点格式、上下文格式等），但当前（v2.3）无任何 skill / agent / eval 加载它们。

## 使用说明

如需启用某个归档规范：
1. 在对应 skill 的 SKILL.md 或 references 中补加载点
2. 在 `evals/` 补对应的行为断言
3. 将该文件从本目录移回 `references/shared/`（或 skill-local references/）
4. 在 `references/shared/MANIFEST.yaml` 中登记

## 归档清单（2026-06-20）

| 文件 | 行数 | 内容 | 建议接线目标 |
|------|------|------|------------|
| `projection-spec.md` | 133 | 投影管线规范（CHAPTER_COMMIT 后 4 目标并行投影） | `write-novel-long-write` |
| `run-ledger-format.md` | 82 | 运行日志格式与断点恢复条目规范 | `write-novel-long-write` |
| `context-format.md` | 90 | 上下文加载格式与优先级规范 | `write-novel-long-write` / `write-novel-long-analyze` |
| `verification-checklist.md` | 42 | 端到端验证 checklist schema | `write-novel-review` / CI |
| `style-cache-schema.md` | 80 | 风格缓存 schema（笔触指纹） | `write-novel-long-write` / `write-novel-deslop` |
| `technique-tracker-schema.md` | 36 | 技法追踪器 schema | `write-novel-long-write` |
