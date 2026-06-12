---
name: write-novel-import
description: |
  逆向导入已有小说。将外部小说文本反向解析为 write-novel 项目结构。
  触发方式：/write-novel-import、「导入」「反向解析」「把我的书导进来」
---

# write-novel-import：逆向导入

你是小说逆向工程专家。将已有小说文本反向解析为 write-novel 的标准项目结构，使现有作品也能享受全套写作工具链。

## 核心原则

1. **无损导入**：原文一字不改，只做结构化提取。
2. **按长度分流**：短篇/中篇/长篇走不同的解析策略。
3. **能自动的自动，该手动的留白**：自动提取角色名、章节边界、伏笔标记；复杂设定关系留待作者手动补充。

## 4 Phase 流程

### Phase 1：确认导入源

1. 确定导入源类型：本地文件 / 网页 URL / 粘贴文本
2. 确认文本编码（UTF-8 / GBK），处理中文编码兼容
3. 字数评估 → 按长度路由：
   - 短篇（< 3万字）→ 全量解析
   - 中篇（3-15万字）→ 采样解析（前中后各20%）
   - 长篇（> 15万字）→ 分阶段解析
4. 参考：`references/length-routing.md`

### Phase 2：结构识别

1. **章节边界检测**：正则匹配"第X章"、"Chapter X"等模式
2. **卷结构推断**：通过章节聚类推断卷边界
3. **章节元数据提取**：标题、字数、时间标记
4. 产出：`分卷大纲/` 下的卷级大纲和章级索引
5. 参考：`references/structure-mapping-long.md`（长篇）、`references/structure-mapping-short.md`（短篇）

### Phase 3：内容提取

1. **角色提取**：
   - 命名实体识别（人名/地名/势力名）
   - 角色出场频次统计 → 主角/配角/路人分级
   - 角色关系推断（共现分析）
   - 产出：`人物/*.md` 角色卡片
   - 参考：`references/character-state-reverse.md`

2. **设定提取**：
   - 世界观关键概念识别
   - 力量体系/境界链提取
   - 产出：`世界设定/*.md`
   - 参考：`references/state-tracking.md`

3. **伏笔标记**：
   - 扫描跨章节回调/伏线
   - 产出：`伏笔与线索回收池.md` 初始数据

### Phase 4：项目激活

1. 生成 `全局写作状态.md`（基于提取的数据填充）
2. 生成 `历史章节摘要/`（每章 ~200 字摘要）
3. 生成 `章节提交记录/`（标记新增设定）
4. 运行 `python scripts/main.py project` 重建索引
5. 生成导入报告
6. 参考：`references/format-and-structure.md`

---

## 调用链

导入过程中遇到复杂分析需求时，委托给对应 skill：

| 需求 | 委托到 |
|------|--------|
| 深度角色/设定分析 | `write-novel-analyze` |
| 章节批量提取 | `write-novel-chapter-extractor` agent |

## 流程衔接

| 时机 | 跳转到 | 命令 |
|------|--------|------|
| 导入完成，开始写作 | write-novel-long-write | `/write-novel-long-write` |
