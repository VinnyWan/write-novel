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

**纯 Markdown 传递，不通过脚本或数据库：**

Agent A 产出 → Markdown 文件落盘（通过 Write 工具） → Agent B 读取（通过 Read 工具）。

**Agent 调用方（Skill）：**
- 通过 `Agent()` 工具 spawn agent，prompt 中指定输入/输出文件路径
- 不传 JSON 数据，只传文件路径

**Agent 被调用方：**
- 读取输入 Markdown 文件（设定/、大纲/、正文/、追踪/）
- 产出输出 Markdown 文件，写入指定路径
- 不得修改非指定的文件
- **不调用任何 Python/Shell 脚本**——所有读取、搜索、分析由 agent 直接执行

### 3. 上下文效率（最小记忆包协议）

Agent 在加载上下文时必须遵循分层加载策略：
- 写作 agent：只加载"不知道就会写错"的信息（~3000 tokens）
- 审查 agent：加载正文 + 相关设定文件 + 前章摘要（按需加载，不全量）
- 研究 agent：只加载与查询相关的对标/拆文库文件，不全量加载

### 4. 并发安全

- 不同 Agent 不得同时写入同一文件
- 同一本书的 agent 调用按 Phase 顺序串行
- 不同书的 agent 调用可并行（工作空间隔离）

### 5. 降级路径

当主模型不可用时，自动降级：
- Opus → Sonnet（story-architect）
- Sonnet → Haiku（narrative-writer、character-designer、deconstruction-agent）
- Haiku → 无降级（reviewer、story-researcher 成本已最低）

降级时在 `追踪/run-ledger.md` 中记录 `model_degraded: true`。

### 6. 错误处理

- Agent spawn 失败 → 主线程直接执行，solo 模式
- Agent 输出文件丢失 → 重新 spawn，不尝试恢复
- Agent 超时 → 降级模型重试一次，仍失败则 solo
