## 1. 创建 write-novel-scan（合并 long-scan + short-scan）

- [x] 1.1 创建 `write-novel/skills/write-novel-scan/SKILL.md`，含篇幅分流逻辑（D1）和统一的 Phase 1-4 流程，长/短分支用 if/else 描述
- [x] 1.2 创建 `write-novel/skills/write-novel-scan/references/scan-common.md`：共享 Phase 流程、质量检查
- [x] 1.3 创建 `write-novel/skills/write-novel-scan/references/scan-long.md`：长篇特有（平台列表、分析维度、选题决策模板）
- [x] 1.4 创建 `write-novel/skills/write-novel-scan/references/scan-short.md`：短篇特有（平台列表、情绪分析维度、风口预警模板）
- [x] 1.5 复制共享 reference 文件到新目录（topic-decision.md, scan-output-format.md, scan-quality-gates.md 等）

## 2. 创建 write-novel-analyze（合并 long-analyze + short-analyze）

- [x] 2.1 创建 `write-novel/skills/write-novel-analyze/SKILL.md`，含字数探针分流逻辑（D1）和统一的 Stage 管道
- [x] 2.2 创建 `write-novel/skills/write-novel-analyze/references/analyze-common.md`：共享门控、恢复机制
- [x] 2.3 创建 `write-novel/skills/write-novel-analyze/references/analyze-long.md`：长篇特有（Stage 0-6 详细流程、Stage 2 并行策略）
- [x] 2.4 创建 `write-novel/skills/write-novel-analyze/references/analyze-short.md`：短篇特有（Stage 2-6 全篇管道、Phase 7 门控）
- [x] 2.5 复制共享 reference 文件到新目录（material-decomposition.md, output-contract.md, output-templates.md 等）

## 3. 创建旧 skill 别名 wrapper

- [x] 3.1 将 `write-novel-long-scan/SKILL.md` 替换为别名 wrapper（~15 行，转发到 write-novel-scan）
- [x] 3.2 将 `write-novel-short-scan/SKILL.md` 替换为别名 wrapper（转发到 write-novel-scan）
- [x] 3.3 将 `write-novel-long-analyze/SKILL.md` 替换为别名 wrapper（转发到 write-novel-analyze）
- [x] 3.4 将 `write-novel-short-analyze/SKILL.md` 替换为别名 wrapper（转发到 write-novel-analyze）

## 4. 更新路由器（write-novel）

- [x] 4.1 更新路由表：长/短扫榜 → write-novel-scan，长/短拆文 → write-novel-analyze，保留旧命令别名映射
- [x] 4.2 更新已部署 Skill 列表：用 write-novel-scan / write-novel-analyze 替代四个独立条目
- [x] 4.3 更新旧命名空间兼容表

## 5. 更新下游 skill 引用

- [x] 5.1 更新 `write-novel-import/SKILL.md`：analyze 调用路径改为统一入口
- [x] 5.2 更新 `write-novel-long-write/SKILL.md` 流程衔接表：scan/analyze 引用改为统一名称
- [x] 5.3 更新 `write-novel-short-write/SKILL.md` 流程衔接表：scan/analyze 引用改为统一名称
- [x] 5.4 更新 `write-novel-review/SKILL.md` 流程衔接表（如涉及）
- [x] 5.5 更新 `write-novel-deslop/SKILL.md` 流程衔接表

## 6. 验证

- [x] 6.1 验证 `/write-novel-scan` 能正确分流长/短扫榜（SKILL.md 含篇幅分流逻辑，reference 文件完整）
- [x] 6.2 验证 `/write-novel-analyze` 能正确分流长/短拆文（SKILL.md 含字数探针分流，reference 文件完整）
- [x] 6.3 验证旧命令别名（`/write-novel-long-scan` 等）仍可正常触发（4 个别名 wrapper 均含 correct frontmatter 和转发描述）
- [x] 6.4 验证 write-novel 路由器正确分发到新 skill（路由表 + 匹配规则 + 兼容表 + 已部署列表均已更新）
- [x] 6.5 确认无断链引用（已清扫所有下游 skill 中的旧命令引用，保留旧命名兼容表引用为向后兼容所需）
