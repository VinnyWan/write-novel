---
name: write-novel
description: |
  网络小说工具箱主入口。根据用户需求自动路由到对应 skill。
  触发方式：/write-novel、/网文、「我想写小说」「帮我写书」「写网文」
  当用户意图不明确时触发此 skill，由路由逻辑分发到具体的扫榜/拆文/写作/去AI味/封面/审查/导入/查询/面板/诊断 skill。
  旧触发词别名：/story、/写长篇
---

# write-novel：网文工具箱路由

你是网文工具箱的路由入口。用户的请求模糊时由你分发到具体 skill。

## 路由表

| 用户意图 | 关键词示例 | 路由到 |
|---------|-----------|--------|
| 写长篇（含规划） | 开书、写大纲、长篇、连载、续写、日更、修改、回炉、重写、规划、卷纲、章纲 | `/write-novel-long-write` |
| 写短篇 | 短篇、盐言、一万字 | `/write-novel-short-write` |
| 扫榜 | 排行、什么火、起点/番茄/晋江、知乎盐言、扫榜 | `/write-novel-scan` |
| 选题决策 | 写什么能爆、帮我选题、选题方向 | `/write-novel-scan` |
| 拆文 | 拆文、拆书、分析这本书、拆短篇、黄金三章 | `/write-novel-analyze` |
| 去 AI 味 | 去 AI 味、太 AI、去味、deslop | `/write-novel-deslop` |
| 审查 | 审查、审稿、review、审一下 | `/write-novel-review` |
| 封面 | 封面、封面图、做封面 | `/write-novel-cover` |
| 环境部署 | 准备写书、搭环境、初始化、配置 | `/write-novel-setup` |
| 导入小说 | 导入、反向解析、把我的书导进来 | `/write-novel-import` |
| 项目查询 | 查角色、查伏笔、查进度、查设定、什么状态、写到哪了 | `/write-novel-query` |
| 面板 | 面板、数据看板、dashboard | `/write-novel-query` |
| 诊断 | 体检、诊断、检查项目 | `/write-novel-doctor` |
| 浏览器操控 | 打开浏览器、抓取榜单、采集数据 | `/browser-cdp` |
| 查资料 | 查资料、帮我查资料、调研、搜索一下 | 直接 spawn `write-novel-write-novel-story-researcher` agent |
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
- "续写" "日更" "继续写" 匹配 `write-novel-long-write` 日更流程
- "修改第X章" "回炉" "重写" 匹配 `write-novel-long-write` 大修流程
- "开书" "写大纲" "帮我写书" 匹配 `write-novel-long-write` 开书流程
- "规划" "卷纲" "章纲" "大纲" 匹配 `write-novel-long-write` 规划流程
- "去AI味" "去味" "这篇太AI了" 匹配 `write-novel-deslop`
- "审查" "帮我审一下" 匹配 `write-novel-review`
- "搭环境" "准备写书" "初始化" 匹配 `write-novel-setup`
- "查角色" "查伏笔" "什么状态" "写到哪了" 匹配 `write-novel-query`
- "拆文" "分析这本书" "黄金三章" "拆短篇" 匹配 `write-novel-analyze`（自动按字数分流）
- "扫榜" "排行" "什么火" "知乎盐言" 匹配 `write-novel-scan`（自动按篇幅/平台分流）
- "导入" "反向解析" "把我的书导进来" 匹配 `write-novel-import`
- "面板" "dashboard" 匹配 `write-novel-query`（原 story-dashboard 已合并至 write-novel-query）
- "体检" "诊断" 匹配 `write-novel-doctor`
- "打开浏览器" "抓取" "采集" 匹配 `browser-cdp`

## 旧命名空间兼容

旧触发词自动映射到新 skill（向后兼容）。三套旧命名保留至少一个版本，下个大版本清理 `webnovel-*`：

| 旧 skill 名 | 旧触发词 | 新 skill |
|---------|---------|---------|
| write-novel-long-write | /write-novel-long-write | write-novel-long-write |
| write-novel-short-write | /write-novel-short-write | write-novel-short-write |
| write-novel-long-analyze | /write-novel-long-analyze | write-novel-analyze |
| write-novel-short-analyze | /write-novel-short-analyze | write-novel-analyze |
| write-novel-long-scan | /write-novel-long-scan | write-novel-scan |
| write-novel-short-scan | /write-novel-short-scan | write-novel-scan |
| write-novel-deslop | /write-novel-deslop | write-novel-deslop |
| write-novel-review | /write-novel-review | write-novel-review |
| write-novel-cover | /write-novel-cover | write-novel-cover |
| write-novel-import | /write-novel-import | write-novel-import |
| write-novel-query | /write-novel-query | write-novel-query |
| write-novel-doctor | /write-novel-doctor | write-novel-doctor |
| write-novel-setup | /write-novel-setup | write-novel-setup |
| story | /story | write-novel |
| write-novel-long-write（旧长形式） | /write-novel-long-write | write-novel-long-write |
| write-novel-plan | /write-novel-plan | write-novel-long-write |
| write-novel-query（旧长形式） | /write-novel-query | write-novel-query |
| write-novel-deslop（旧长形式） | /write-novel-deslop | write-novel-deslop |
| write-novel-review（旧长形式） | /write-novel-review | write-novel-review |
| write-novel-setup（旧长形式） | /write-novel-setup | write-novel-setup |
| write-novel-cover（旧长形式） | /write-novel-cover | write-novel-cover |
| write-novel-analyze | /write-novel-analyze | write-novel-analyze |
| write-novel-scan | /write-novel-scan | write-novel-scan |
| write-novel-import（旧长形式） | /write-novel-import | write-novel-import |
| webnovel-write | /webnovel-write | write-novel-long-write |
| webnovel-plan | /webnovel-plan | write-novel-long-write |
| webnovel-query | /webnovel-query | write-novel-query |
| webnovel-review | /webnovel-review | write-novel-review |
| webnovel-init | /webnovel-init | write-novel-setup |
| webnovel-dashboard | /webnovel-dashboard | write-novel-query |
| webnovel-doctor | /webnovel-doctor | write-novel-doctor |

注：`write-novel-*`（旧长形式）与新 skill 名字面相同，路由器对二者一视同仁；保留在表中仅为说明历史。

## 项目状态感知

路由前先检查当前项目状态：

- **无项目目录**（没有包含 `追踪/` 或 `设定/` 的书名目录）：
  - 用户要写作 → 先引导运行 `/write-novel-setup` 初始化环境
  - 用户要扫榜/拆文 → 直接路由
- **已有项目**：检查 `.story-deployed` 标记，如未部署则先运行 `/write-novel-setup`

## 多书切换

用户想切换或查看在写的书时（一个项目可同时有多本）：

1. 在项目根查找所有书目录：包含 `追踪/` 或 `设定/` 子目录的目录（含 `长篇/`、`短篇/` 下的子目录）
2. 列出书名，并标出当前 `.active-book` 指向的那本
3. 让用户选择，把所选书的相对路径写入项目根 `.active-book`（覆盖原内容）
4. 只发现一本时直接确认为活跃书，无需询问

## 已部署 Skill 列表

| Skill 名称 | 功能 |
|-----------|------|
| `write-novel-setup` | 项目初始化与环境部署 |
| `write-novel-scan` | 网文扫榜分析（长篇+短篇统一入口，按篇幅自动分流） |
| `write-novel-analyze` | 网文拆文分析（长篇+短篇统一入口，按字数自动分流） |
| `write-novel-long-write` | 长篇写作（含规划/日更/大修） |
| `write-novel-short-write` | 短篇写作 |
| `write-novel-import` | 反向解析导入 |
| `write-novel-deslop` | 去 AI 味处理 |
| `write-novel-review` | 多视角审查 |
| `write-novel-cover` | 封面生成 |
| `write-novel-query` | 项目状态查询 + 数据面板 |
| `write-novel-doctor` | 项目诊断与维护 |
