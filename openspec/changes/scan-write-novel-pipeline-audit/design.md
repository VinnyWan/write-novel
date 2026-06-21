## Context

write-novel 工具集已完成两轮合并优化：

1. **Skill 合并**（`optimize-write-novel-skills`）：long-scan + short-scan → write-novel-scan，long-analyze + short-analyze → write-novel-analyze
2. **Agent 合并**（前序变更）：多个 agent 合并为 unified agent，引入共享 references 机制

当前状态：合并后的新 skill 已创建，旧 skill 目录保留作为兼容别名。但合并过程中产生了多条断链：
- 新 scan skill 引用了 7 个采集脚本但 scripts/ 目录未迁移
- 共享 reference 的指针文件路径在 review skill 中解析不到实际文件
- MANIFEST.yaml 中的 whitelist 仍引用旧 skill 名称
- normalize-punctuation.js 存在 5 份副本

### 关键约束

- 所有 skill 以 Markdown 文件为唯一驱动，脚本仅做确定性自动化
- 共享 references 机制：指针文件指向 `write-novel/references/shared/`，跨 skill 引用时优先读指针文件
- 旧 skill 目录（long-scan/short-scan/long-analyze/short-analyze）的 SKILL.md 需保留作为向后兼容别名
- 不改变任何公开接口、路由表、触发词

## Goals / Non-Goals

**Goals:**
- 修复 write-novel-scan 的 scripts/ 缺失问题，确保 Phase 1.5 脚本采集模式可用
- 修复 write-novel-review 的 6 个 stub 指针文件路径
- 修复 write-novel-import 和 write-novel-deslop 的 report-template.md 引用
- 更新 MANIFEST.yaml 中的过期引用
- 去重 normalize-punctuation.js

**Non-Goals:**
- 不修改任何 SKILL.md 中的流程逻辑、Phase 定义、路由规则
- 不改变 agent 的 subagent_type 名称或工具配置
- 不新增或删除任何 skill
- 不修改参考文件的实质内容
- 不涉及 OpenSpec spec 文件的创建或修改

## Decisions

### D1：Scripts 迁移策略

**决策**：将旧 long-scan/scripts/（6 个文件）和 short-scan/scripts/（2 个文件，cdp-utils.js 与前者重复）的采集脚本复制到新 `write-novel-scan/scripts/`，去重后保留 8 个文件。

**备选方案**：
- A. 在 scan skill 中引用旧目录的脚本路径 → 不选，旧目录最终应清理
- B. 创建符号链接 → 不选，跨平台兼容性差

**实现**：
```
write-novel/skills/write-novel-scan/scripts/
├── cdp-utils.js              # 共享 CDP 工具（从 long-scan）
├── qidian-rank-scraper.js    # 起点（从 long-scan）
├── fanqie-rank-scraper.js    # 番茄（从 long-scan）
├── qimao-rank-scraper.js     # 七猫（从 long-scan）
├── jjwxc-rank-scraper.js     # 晋江（从 long-scan）
├── ciweimao-rank-scraper.js  # 刺猬猫（从 long-scan）
├── heiyan-booklist-scraper.js # 黑岩（从 short-scan）
└── dz-browse-scraper.js      # 点众（从 short-scan）
```

### D2：Review stub 指针文件修复

**决策**：将 6 个 stub 文件内容改为指向正确的全局共享路径。从 review references/ 的视角解析 `../../references/shared/` 可到达 `write-novel/references/shared/`。

当前 stub 示例（broken）：
```
> 共享源：references/shared/anti-ai-writing.md
```
修正为：
```
> 共享源：../../references/shared/anti-ai-writing.md
```

**备选方案**：
- A. 在 review references/ 下创建 shared/ 子目录并放实际文件 → 不选，违反共享机制设计
- B. 将 stub 替换为完整内容 → 不选，与共享机制冲突，副本会漂移

### D3：report-template.md 引用修复

**决策**：在 `write-novel-import/references/shared/` 和 `write-novel-deslop/references/shared/` 下各创建一个指针文件 `report-template.md`，指向 `../../../references/shared/report-template.md`。

两个 skill 中各创建：
```
references/shared/
└── report-template.md  # 指针文件
```

### D4：normalize-punctuation.js 去重

**决策**：各 skill 的 `scripts/normalize-punctuation.js` 改为指针/说明文件，指向共享的 `write-novel/scripts/normalize-punctuation.js`。skill 的 SKILL.md 中引用路径统一使用共享路径 `write-novel/scripts/normalize-punctuation.js`。

当前 5 份副本位置：
- `write-novel/scripts/normalize-punctuation.js`（共享源）
- `write-novel/skills/write-novel-long-write/scripts/normalize-punctuation.js`
- `write-novel/skills/write-novel-short-write/scripts/normalize-punctuation.js`
- `write-novel/skills/write-novel-deslop/scripts/normalize-punctuation.js`
- `write-novel/skills/write-novel-review/scripts/normalize-punctuation.js`

### D5：MANIFEST.yaml 更新

**决策**：更新 `whitelist_real_files` 部分：
- 将 `write-novel-long-scan/references/*` 替换为 `write-novel-scan/references/*`
- 将 `write-novel-short-scan/references/*` 替换为 `write-novel-scan/references/*`
- 将 `write-novel-long-analyze/references/*` 替换为 `write-novel-analyze/references/*`
- 将 `write-novel-short-analyze/references/*` 替换为 `write-novel-analyze/references/*`
- 将合并后不再存在的旧条目移除，将新 skill 独有的 reference 文件加入

旧 skill 的 whitelist 条目保留不变（long/short analyze 的独有文件仍独立存在）。

### D6：旧目录保留策略

**决策**：旧 skill 目录（long-scan/short-scan/long-analyze/short-analyze）保留 SKILL.md 作为向后兼容别名。`references/` 子目录保留不删（旧 analyze 的 references 中有些文件是独有且被 MANIFEST whitelist 的）。`scripts/` 子目录保留不删（旧脚本可能被其他路径引用）。

## Risks / Trade-offs

- **脚本兼容性风险**：迁移后的 scraper 脚本可能依赖旧目录中的相对路径 → 迁移后验证每个脚本的 require/import 路径
- **指针文件维护**：指针文件只含元数据不含内容，agent 加载时需解析指针 → agent 已有路径解析逻辑，风险低
- **旧目录不删除**：保留旧目录避免破坏可能的硬编码引用，但增加了目录复杂度 → 下个大版本统一清理旧命名空间
