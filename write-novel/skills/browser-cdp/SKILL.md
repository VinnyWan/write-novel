---
name: browser-cdp
version: 1.0.0
description: |
  浏览器操控 skill。通过 Claude Code 内置 CDP 协议复用浏览器登录态，抓取网页数据。
  主要为扫榜和拆文提供登录态数据采集能力。
  触发方式：/browser-cdp、「打开浏览器」「帮我采集」「抓取榜单」
---

# browser-cdp：浏览器 CDP 操控

通过 CDP (Chrome DevTools Protocol) 连接已打开的 Chrome/Edge 浏览器，复用其登录 Cookie 抓取数据。

## 适用场景

| 场景 | 说明 |
|------|------|
| 扫榜数据采集 | 起点/番茄/晋江/七猫排行榜，采集书名+数据+标签 |
| 拆文原文获取 | 用登录态打开付费章节，获取完整正文 |
| 搜索验证 | 用浏览器搜索引擎验证外部事实 |

## CDP 连接

### 启动浏览器（如未运行）

macOS:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &
```

或者用 Edge:
```bash
/Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --remote-debugging-port=9222 &
```

### 检查连接

```bash
lsof -i :9222 -sTCP:LISTEN 2>/dev/null | grep -q LISTEN && echo "CDP available" || echo "CDP unavailable"
```

## 基本操作

### 导航
```
agent-browser --cdp 9222 eval "window.location.replace('<url>')"
agent-browser --cdp 9222 wait 5000
```

### 获取页面内容
```
agent-browser --cdp 9222 snapshot
```

### 提取数据
```
agent-browser --cdp 9222 eval 'document.body.innerText.substring(0, 10000)'
```

### 提取链接
```
agent-browser --cdp 9222 eval 'JSON.stringify(Array.from(document.querySelectorAll("a[href]")).filter(a=>a.href).slice(0,20).map(a=>({text:a.innerText.trim().substring(0,50),href:a.href})))'
```

## 降级策略

CDP 不可用时（浏览器未运行/未安装/端口被占用）：
1. 提示用户手动复制数据或截图
2. 降级到 WebSearch 兜底（信息量有限）
3. 用户可通过"! cd /path && chrome --remote-debugging-port=9222"在终端启动

## 连接失败时的处理

如果 lsof 检查失败：
```
CDP 端口 9222 未在监听。请先在终端启动 Chrome：
! /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &
然后重新运行扫榜。
```

## 注意事项

- CDP 复用浏览器的登录 Cookie，不注入凭证
- 抓取频率控制在每页 ≥ 3 秒
- 不访问非目标平台的页面
- 提取的数据保存为结构化 markdown 或 JSON
