# 短篇采集目标 + 采集质量

> 本文是 write-novel-short-scan SKILL.md「Phase 1.5 browser-cdp 采集模式」的展开参考。SKILL.md 只保留采集入口、合并 agent context 决策点、按需读指引；本文件给出点众/黑岩采集目标表（页面 URL + 核心字段）、采集要点、文件命名、跨平台采集质量底线。

---

## 点众采集目标

| 页面 | URL | 核心字段 |
|------|-----|----------|
| 男频短篇 | ishugui.com/browse | 书名·作者·标签·状态·字数·评分·最新章节 |
| 女频短篇 | ishugui.com/browse/on3 | 书名·作者·标签·状态·字数·评分·最新章节 |

点众专用参数：`--channel male/female/all`。

## 黑岩采集目标

| 页面 | URL | 核心字段 |
|------|-----|----------|
| 书库列表 | manage.zhangwenpindu.cn/books/booklist | 书名·作者·字数·分类·类型·价格·创建/更新时间·标签（详情模式） |

黑岩专用参数：`--pages N`（每页 20 条）、`--detail`（逐本详情，含标签/简介，速度较慢）、`--channel male/female`。

> **黑岩需要登录！** 必须先在 Chrome 中手动登录 `manage.zhangwenpindu.cn`，脚本才能从 Cookie 中提取 Bearer token 调用后端 API。未登录会报错提示。**黑岩采集失败时标记为 SKIP，继续其他平台采集，不中断整个 Phase 1。**

## 文件命名

`{平台}{类型}_{YYYYMMDD}.md`，例：`点众男频短篇_20260501.md`

## 跨平台采集质量底线

| 检查项 | 标准 | 处理 |
|--------|------|------|
| 条目数量 | 主流平台 >= 10 条有效数据 | 不足则文件头注明 `[数据稀疏] 实际采集 N 条` |
| 必填字段 | 书名、作者（缺任一项视为无效） | 无效条目移除，条目数重算 |
| 平台登录态 | 黑岩等需登录的平台未登录 → SKIP | 标记 SKIP 不中断 Phase 1，报告中注明缺失平台 |

## 浏览器操控（高级模式）

- 如果可用 agent-browser CLI，通过 CDP 连接 Chrome 获取平台数据
- 示例：`agent-browser --cdp 9222 open "https://www.ishugui.com/browse"`
- 可复用用户已登录的 Chrome session，获取完整榜单数据
- 适用于需要登录才能看到的数据（知乎个人中心、番茄书架等）

## 与 real-market-data.md 的关系

[real-market-data.md](real-market-data.md) 给**跨平台写作差异对照、各平台简介公式速查、题材爆款公式速查表、各平台写作特征**（内置知识模式必载，也是 Phase 2 分析的对照标尺）。本文件给**采集目标表 + 采集质量底线**（脚本/CDP 采集时用）。两者互补：采集看本文件，分析对照看 real-market-data.md。
