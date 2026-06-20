# 文风缓存 Schema

> 本文件定义 `追踪/文风缓存.md` 的格式和读写规则。write-novel-long-write Phase 4 Stage B2 使用此缓存避免卷内章章重复文风召回。

---

## 缓存文件格式

`追踪/文风缓存.md` 使用 YAML frontmatter + Markdown 正文：

```yaml
---
volume: 1
base_chapter: 1
style_profile:
  path: "对标/大奉打更人/文风.md"
  summary: "短句为主，对话占比高，段落切换快，标点节奏密"
tone_matches:
  紧张:
    chapter_K: 12
    techniques: ["信息差揭示", "短句加速", "悬念连锁"]
  热血:
    chapter_K: 5
    techniques: ["情绪递进三步", "爽点铺放比 3:1"]
  轻松:
    chapter_K: 3
    techniques: ["对话流", "反差萌", "吐槽节奏"]
last_updated: "2026-06-19T10:00:00"
---
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `volume` | int | 当前卷号，用于跨卷自动刷新判断 |
| `base_chapter` | int | 缓存创建时的章节号（该卷首章） |
| `style_profile.path` | string | 文风文件绝对或相对路径。无对标项目时值为 `"none"` |
| `style_profile.summary` | string | 文风文件 2-3 句摘要 |
| `tone_matches` | map | 基调→匹配章节+技法映射。key 为基调名（紧张/热血/轻松/悲伤/爽/甜/温馨/恐怖/压抑），value 为 `{chapter_K, techniques[]}` |
| `last_updated` | ISO 8601 | 最后更新时间戳 |

---

## 读写规则

### 创建（卷首章）

当 `追踪/文风缓存.md` 不存在，或 `volume` 字段与当前卷号不同时：

1. 完整执行文风召回流程（按对标书路径查找读 `文风.md` → grep `基调：XX` 匹配章节 → 读 `第K章_摘要.md`）
2. 将结果按上述格式写入 `追踪/文风缓存.md`
3. 无对标项目时：`style_profile.path: "none"`，`style_profile.summary: "无对标参考"`，`tone_matches: {}`

### 读取（同卷后续章）

1. 读取 `追踪/文风缓存.md` 的 YAML frontmatter
2. 从细纲获取本章 `目标情绪`
3. 在 `tone_matches` 中按目标情绪查找：
   - **命中**：直接使用 `{chapter_K, techniques}`，跳过 grep 和摘要读取
   - **未命中**：对该基调增量匹配 → 追加到 `tone_matches` → 更新 `last_updated`

### 跨卷刷新

新卷首章检测到 `volume` 不等于当前卷号时：
1. 将旧缓存归档到 `追踪/归档/文风缓存_第{旧卷号}卷.md`（可选）
2. 重新执行完整文风召回，写入新缓存覆盖旧文件

### 降级

- `style_profile.path: "none"` 时：所有 tone_matches 查找返回空，写作跳过文风召回
- 缓存文件损坏或 YAML 解析失败：删除缓存文件，回退到完整文风召回流程

---

## 与 Phase 4 Stage B2 的关系

Stage B2 文风召回步骤首先检查 `追踪/文风缓存.md`：
- 存在且卷号匹配 → 从缓存读取（可能增量更新）
- 不存在或卷号不匹配 → 完整文风召回 + 写入缓存
