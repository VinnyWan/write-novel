---
name: story
description: |
  网络小说工具箱主入口。根据用户需求自动路由到对应 skill。
  触发方式：/story、/网文、「我想写小说」「帮我写书」「写网文」
  当用户意图不明确时触发此 skill，由路由逻辑分发到具体的扫榜/拆文/写作/去AI味/封面/审查/导入/查询/面板/诊断 skill。
  旧触发词别名：/write-novel、/写长篇
---

# story：网文工具箱路由

你是网文工具箱的路由入口。用户的请求模糊时由你分发到具体 skill。

## 路由表

| 用户意图 | 关键词示例 | 路由到 |
|---------|-----------|--------|
| 写长篇（含规划） | 开书、写大纲、长篇、连载、续写、日更、修改、回炉、重写、规划、卷纲、章纲 | `/story-long-write` |
| 写短篇 | 短篇、盐言、一万字 | `/story-short-write` |
| 长篇拆文 | 拆文、分析这本书、黄金三章 | `/story-long-analyze` |
| 短篇拆文 | 拆短篇、分析这个故事 | `/story-short-analyze` |
| 长篇扫榜 | 长篇排行、什么火、起点/番茄/晋江、扫榜 | `/story-long-scan` |
| 选题决策 | 写什么能爆、帮我选题、选题方向 | `/story-long-scan` |
| 短篇扫榜 | 短篇排行、知乎盐言排行 | `/story-short-scan` |
| 去 AI 味 | 去 AI 味、太 AI、去味、deslop | `/story-deslop` |
| 审查 | 审查、审稿、review、审一下 | `/story-review` |
| 封面 | 封面、封面图、做封面 | `/story-cover` |
| 环境部署 | 准备写书、搭环境、初始化、配置 | `/story-setup` |
| 导入小说 | 导入、反向解析、把我的书导进来 | `/story-import` |
| 项目查询 | 查角色、查伏笔、查进度、查设定、什么状态、写到哪了 | `/story-query` |
| 面板 | 面板、数据看板、dashboard | `/story-query` |
| 诊断 | 体检、诊断、检查项目 | `/story-doctor` |
| 查资料 | 查资料、帮我查资料、调研、搜索一下 | 直接 spawn `story-researcher` agent |
| 切换/列出书目 | 切书、换书、列出我的书、我在写哪几本 | 见下方「多书切换」 |

## 路由流程

1. 分析用户请求，提取意图关键词
2. 按匹配优先级排序：长命令 > 短命令，写作相关优先匹配
3. 能明确匹配 → 直接调用对应 skill（`Skill("skill-name")`）
4. 无法匹配 → 从上表列出选项让用户选择
5. 多个关键词同时命中 → 优先匹配"日更续写 > 大修/回炉 > 开书"
6. 用户说"我想写小说"但未指定长篇/短篇 → 询问篇幅类型后再路由

## 路由匹配规则

- 关键词匹配忽略大小写和标点符号
- "续写" "日更" "继续写" 匹配 `story-long-write` 日更流程
- "修改第X章" "回炉" "重写" 匹配 `story-long-write` 大修流程
- "开书" "写大纲" "帮我写书" 匹配 `story-long-write` 开书流程
- "规划" "卷纲" "章纲" "大纲" 匹配 `story-long-write` 规划流程
- "去AI味" "去味" "这篇太AI了" 匹配 `story-deslop`
- "审查" "帮我审一下" 匹配 `story-review`
- "搭环境" "准备写书" "初始化" 匹配 `story-setup`
- "查角色" "查伏笔" "什么状态" "写到哪了" 匹配 `story-query`
- "拆文" "分析这本书" "黄金三章" 匹配 `story-long-analyze`
- "扫榜" "排行" "什么火" 匹配 `story-long-scan`
- "导入" "反向解析" "把我的书导进来" 匹配 `story-import`
- "面板" "dashboard" 匹配 `story-query`（原 story-dashboard 已合并至 story-query）
- "体检" "诊断" 匹配 `story-doctor`

## 旧命名空间兼容

旧触发词自动映射到新 skill（向后兼容）：

| 旧 skill | 新 skill |
|---------|---------|
| write-novel-long-write | story-long-write |
| write-novel-plan | story-long-write |
| write-novel-query | story-query |
| write-novel-deslop | story-deslop |
| write-novel-review | story-review |
| write-novel-setup | story-setup |
| write-novel-cover | story-cover |
| write-novel-analyze | story-long-analyze |
| write-novel-scan | story-long-scan |
| write-novel-import | story-import |
| webnovel-write | story-long-write |
| webnovel-plan | story-long-write |
| webnovel-query | story-query |
| webnovel-review | story-review |
| webnovel-init | story-setup |
| webnovel-dashboard | story-query |
| webnovel-doctor | story-doctor |

## 项目状态感知

路由前先检查当前项目状态：

- **无项目目录**（没有包含 `追踪/` 或 `设定/` 的书名目录）：
  - 用户要写作 → 先引导运行 `/story-setup` 初始化环境
  - 用户要扫榜/拆文 → 直接路由
- **已有项目**：检查 `.story-deployed` 标记，如未部署则先运行 `/story-setup`

## 多书切换

用户想切换或查看在写的书时（一个项目可同时有多本）：

1. 在项目根查找所有书目录：包含 `追踪/` 或 `设定/` 子目录的目录（含 `长篇/`、`短篇/` 下的子目录）
2. 列出书名，并标出当前 `.active-book` 指向的那本
3. 让用户选择，把所选书的相对路径写入项目根 `.active-book`（覆盖原内容）
4. 只发现一本时直接确认为活跃书，无需询问

## 已部署 Skill 列表

| Skill 名称 | 功能 |
|-----------|------|
| `story-setup` | 项目初始化与环境部署 |
| `story-long-scan` | 长篇扫榜分析 |
| `story-short-scan` | 短篇扫榜分析 |
| `story-long-analyze` | 长篇拆文分析 |
| `story-short-analyze` | 短篇拆文分析 |
| `story-long-write` | 长篇写作（含规划/日更/大修） |
| `story-short-write` | 短篇写作 |
| `story-import` | 反向解析导入 |
| `story-deslop` | 去 AI 味处理 |
| `story-review` | 多视角审查 |
| `story-cover` | 封面生成 |
| `story-query` | 项目状态查询 |
| `story-query` | 项目查询 + 数据面板（原 story-dashboard 已合并） |
| `story-doctor` | 项目诊断与维护 |
