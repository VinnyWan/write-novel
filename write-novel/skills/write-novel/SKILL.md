---
name: write-novel
description: |
  网文工具箱路由入口。根据用户需求自动路由到对应 skill。
  触发方式：/write-novel、/写长篇、「我想写小说」「帮我写书」「写网文」
  当用户意图不明确时触发此 skill，由路由逻辑分发到具体的写作/拆文/扫榜/去AI味/封面 skill。
---

# write-novel：网文工具箱路由

你是网文工具箱的路由入口。用户的请求模糊时由你分发到具体 skill。

## 路由表

| 用户意图 | 关键词示例 | 路由到 |
|----------|-----------|--------|
| 写长篇 | 开书、写大纲、长篇、连载、续写、日更、修改、回炉、重写 | `write-novel-long-write` |
| 卷纲规划 | 规划、卷纲、章纲、大纲、plan、拆章 | `write-novel-plan` |
| 项目查询 | 查角色、查伏笔、查进度、什么状态 | `write-novel-query` |
| 去 AI 味 | 去 AI 味、太 AI、去味、deslop | `write-novel-deslop` |
| 多视角审查 | 审查、审稿、review | `write-novel-review` |
| 环境部署 | 准备写书、搭环境、初始化、配置 | `write-novel-setup` |
| 封面生成 | 封面、封面图 | `write-novel-cover` |
| 长篇拆文 | 拆文、分析这本书、黄金三章 | `write-novel-analyze` |
| 长篇扫榜 | 扫榜、排行、什么火 | `write-novel-scan` |
| 导入小说 | 导入、反向解析、把我的书导进来 | `write-novel-import` |

## 路由流程

1. 分析用户请求，提取意图关键词。
2. 按匹配优先级排序：长命令 > 短命令，写作相关优先匹配。
3. 能明确匹配 → 直接调用对应 skill（`Skill("skill-name")`）。
4. 无法匹配 → 从上表列出选项让用户选择。
5. 多个关键词同时命中 → 优先匹配"日更续写 > 大修/回炉 > 开书"。

## 路由匹配规则

- 关键词匹配忽略大小写和标点符号。
- "续写" "日更" "继续写" 匹配 `write-novel-long-write` 日更流程。
- "修改第X章" "回炉" "重写" 匹配 `write-novel-long-write` 大修流程。
- "开书" "写大纲" "帮我写书" 匹配 `write-novel-long-write` 开书流程。
- "去AI味" "去味" "这篇太AI了" 匹配 `write-novel-deslop`。
- "审查" "帮我审一下" 匹配 `write-novel-review`。
- "搭环境" "准备写书" "初始化" 匹配 `write-novel-setup`。
- "规划" "卷纲" "章纲" "大纲" 匹配 `write-novel-plan`。
- "查角色" "查伏笔" "什么状态" "写到哪了" 匹配 `write-novel-query`。
- "拆文" "分析这本书" "黄金三章" 匹配 `write-novel-analyze`。
- "扫榜" "排行" "什么火" 匹配 `write-novel-scan`。
- "导入" "反向解析" "把我的书导进来" 匹配 `write-novel-import`。

## 项目状态感知

路由前先检查当前项目状态：

- **无项目结构**（没有 `人物/` 或 `世界设定/` 目录）：
  - 用户要写作 → 先引导运行 `write-novel-setup` 初始化环境。
  - 用户要其他操作（审查/去味等）→ 提示需要先有项目。
- **已有项目**：检查 `skills/` 目录是否存在且包含 skill 文件，如未部署则先运行 `write-novel-setup`。

## 已部署子 Skill 列表

| Skill 名称 | 文件路径 | 功能 |
|-----------|---------|------|
| `write-novel-long-write` | `write-novel-long-write/SKILL.md` | 长篇写作主流程 |
| `write-novel-plan` | `write-novel-plan/SKILL.md` | 卷纲规划 |
| `write-novel-query` | `write-novel-query/SKILL.md` | 项目状态查询 |
| `write-novel-deslop` | `write-novel-deslop/SKILL.md` | 去 AI 味 |
| `write-novel-review` | `write-novel-review/SKILL.md` | 多视角审查 + 质量管道 |
| `write-novel-setup` | `write-novel-setup/SKILL.md` | 环境部署 |
| `write-novel-cover` | `write-novel-cover/SKILL.md` | 封面生成 |
| `write-novel-scan` | `write-novel-scan/SKILL.md` | 长篇扫榜 |
| `write-novel-analyze` | `write-novel-analyze/SKILL.md` | 长篇拆文 |
| `write-novel-import` | `write-novel-import/SKILL.md` | 逆向导入 |
