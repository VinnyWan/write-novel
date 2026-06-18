# 模式学习 Schema

## 存储位置

`追踪/project_memory.json`

## 6 类模式定义

| 类名 | 键名 | 说明 | 示例 |
|------|------|------|------|
| 钩子 | `hook` | 有效的章首/章尾/文中钩子结构 | 信息差钩子、危机钩子、选择钩子 |
| 节奏 | `pacing` | 成功的节奏序列模式 | 快-缓-快的三拍结构、高潮前的蓄能节奏 |
| 对话 | `dialogue` | 出色的对话交锋模式 | 潜台词交锋、问非所答、角色差异化语气 |
| 爽点 | `cool_points` | 爽点释放模式 | 打脸兑现、身份暴露、实力碾压的铺陈-释放节奏 |
| 情绪 | `emotion` | 情绪递进/转折模式 | 从愤怒到决然的转折、从绝望到希望的递进 |
| 格式 | `format` | 有效的格式/结构模式 | 短句连击节奏、镜头切换频率、段落密度 |

## JSON Schema

```json
{
  "schema_version": 1,
  "patterns": {
    "hook": [],
    "pacing": [],
    "dialogue": [],
    "cool_points": [],
    "emotion": [],
    "format": []
  }
}
```

每个模式条目结构：

```json
{
  "pattern": "模式的自然语言描述（1-2句）",
  "source": "第42章",
  "hash": "abc123def456",
  "captured_at": "2026-06-18T15:30:00"
}
```

## 去重策略

1. **精确去重**：计算模式描述文本的 SHA256 hash，取前 12 位（SHA256-12）
2. **近似去重**：计算与已有模式的编辑距离（Levenshtein），< 5 时视为 near-duplicate
3. 精确匹配或 near-duplicate → 跳过存储，追加一条日志到 `追踪/projection-log.jsonl`
4. 新模式的 hash 不冲突且编辑距离 ≥ 5 → 追加到对应类别数组

## LRU 淘汰规则

- 每类（如 `patterns.hook`）最多 200 条
- 超出时淘汰最旧的条目（按 `captured_at` 排序，删最早）
- 淘汰时追加日志：`{"event": "lru_evict", "category": "hook", "evicted_source": "第3章", "timestamp": "..."}`

## 检索协议

写作前准备章节 brief 时：

1. 确定本章类型（opening / climax / transition / daily / resolution）
2. 从 `project_memory.json` 中检索匹配的模式（按类别匹配）
3. 最多返回 3 条最相关的模式
4. 返回格式：模式描述 + 来源章引用
5. 如果没有匹配结果 → 报告「无相关模式记录」，不阻塞写作
