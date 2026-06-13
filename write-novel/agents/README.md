# Agent 通信协议

## 6 个规范 Agent

| Agent | 模型 | 降级 | 职责 |
|-------|------|------|------|
| story-architect | Opus | Sonnet | 架构/世界观/大纲/叙事工程 |
| narrative-writer | Sonnet | Haiku | 正文写作/去AI味/格式合规 |
| character-designer | Sonnet | Haiku | 角色设计/对话/关系网络 |
| reviewer | Haiku | - | 5维审查（设定/时间线/叙事/角色/逻辑） |
| deconstruction-agent | Sonnet | Haiku | 拆文分析/章节提取 |
| story-researcher | Haiku | - | 资料研究/搜索检索 |

## 通信协议

### 1. Agent 间通信全部通过 Markdown 文件

Agent A 产出 → Markdown 文件落盘 → Agent B 读取。

不通过内存共享、不通过环境变量传递复杂数据。

### 2. 文件传递规范

**Agent 调用方（Skill）：**
```bash
# spawn agent with explicit artifact paths
Agent(
  subagent_type="general-purpose",
  model="<agent-model>",
  prompt="...读取设定/{book}/设定/MASTER_SETTING.md，产出追踪/{book}/追踪/state.md..."
)
```

**Agent 被调用方：**
- 读取输入 Markdown 文件（设定/、大纲/、正文/、追踪/）
- 产出输出 Markdown 文件，写入指定路径
- 不得修改非指定的文件

### 3. 并发安全

- 不同 Agent 不得同时写入同一文件
- 同一本书的 agent 调用按 Phase 顺序串行
- 不同书的 agent 调用可并行（工作空间隔离）

### 4. 降级路径

当主模型不可用时，自动降级：
- Opus → Sonnet（story-architect）
- Sonnet → Haiku（narrative-writer、character-designer、deconstruction-agent）
- Haiku → 无降级（reviewer、story-researcher 成本已最低）

降级时在 run-ledger 中记录 `model_degraded: true`。

### 5. 错误处理

- Agent spawn 失败 → 主线程直接执行，solo 模式
- Agent 输出文件丢失 → 重新 spawn，不尝试恢复
- Agent 超时 → 降级模型重试一次，仍失败则 solo
