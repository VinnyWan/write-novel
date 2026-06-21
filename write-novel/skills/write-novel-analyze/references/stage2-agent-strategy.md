# Stage 2 并行 Agent 策略详解

> 本文是 write-novel-long-analyze SKILL.md「Stage 2 并行 Agent 策略」的展开参考。SKILL.md 只保留决策点（spawn 条件、降级触发、硬门控存在性、升级重试）；本文件给出完整 spawn prompt、批量策略、可机械校验的硬门控 grep 模式、sonnet 升级重试调用、最终落盘规则、agent 不可用降级。

Stage 2 使用 deconstruction-agent agent 并行处理每章，替代原来的串行分块。

---

## 调用方式

```python
Agent(
  subagent_type: "write-novel:write-novel-deconstruction-agent",
  prompt: "章节编号：第{N}章\n章节标题：{标题}\n章节字数：{字数}\n\n章节原文：\n{原文文本}"
)
```

## 批量策略

- 每次 spawn 5-8 个 agent（避免并发限制）
- 等待当前批次全部完成后，再 spawn 下一批
- 每批完成后更新 `_progress.md` 记录已处理章节

## Agent 输出收集

- 每个 agent 返回 markdown 格式的提取结果
- 主线程将 agent 输出写入 `章节/第{N}章_摘要.md`
- 收集所有 agent 的出场人物表，供 Stage 3 合并使用

## 失败处理 + 质量升级重试

**两类失败**：
1. **执行失败**（agent crash / 超时 / 空输出）→ 同模型（haiku）重试 1 次
2. **质量失败**（输出落盘后跑 write-novel-deconstruction-agent.md「质量检查」10 条自检，任一不达标——典型：情节点 < 10、原文引用缺失、类型/基调/主题标签超出枚举、`基调：` 漏全角冒号、角色名为昵称/通用称呼）→ **升级到 sonnet 重试 1 次**

**可机械校验的硬门控**（主线程落盘后直接 grep，命中即判质量失败，不依赖 agent 自报）：
- 情节点数 `N = grep -cE '^P[0-9]+ '`；`grep -c '基调：'` 必须 == N（少于 N = 有情节点漏 `基调：` 或漏全角冒号 → 下游 Stage 6 文风采样按全角 `基调：` grep，会静默漏章）
- `grep -hoE '基调：[^ |]+'` 去重后 ⊆ {紧张, 轻松, 悲伤, 热血, 爽, 甜, 温馨, 恐怖, 压抑, 其他}
- `grep -hoE '主题标签[：]?[^ |]+'` 去重（去 `主题标签`/冒号前缀后）⊆ {爱情, 亲情, 友情, 权力, 金钱, 成长, 复仇, 悬念, 搞笑, 热血, 日常, 其他}（出现 `主题标签：` 带冒号、或值为基调词均判失败）

**升级重试调用方式**（主线程在校验失败后执行）：

```python
Agent(
  subagent_type: "write-novel:write-novel-deconstruction-agent",
  model: "sonnet",            # 显式覆盖 frontmatter 的 haiku
  prompt: "章节编号：第{N}章\n...（同首次 prompt，可追加：'上次校验失败原因：{自检失败项}'）"
)
```

**最终落盘规则**：
- haiku 首次通过 → 写入 `章节/第{N}章_摘要.md`，`_progress.md` 标记 `success`
- haiku 失败 + 同模型 retry 通过 → 同上，备注 `retry_same_model`
- 质量失败 + sonnet retry 通过 → 同上，备注 `retry_sonnet`
- sonnet retry 仍失败 → 章节标记 `⚠️ 跳过`，失败原因写入 `_progress.md` 「失败记录」表，拆文报告中注明
- 单章失败不阻断管道；批次全部 spawn 完成后才决定是否进入 Stage 3

## Agent 不可用降级

以下任一情况，Stage 2 自动退回串行模式，由主线程按 deconstruction-agent 方法论逐章处理（结果同样套 output-templates.md 的章节摘要模板，质量不受影响，只是改为串行、速度略慢）：

- **agent 未部署**：`.claude/agents/write-novel-deconstruction-agent.md` 不存在。`.claude/agents/` 通常不随仓库提交，由 `/write-novel-setup` 部署；模板源在 `skills/write-novel-setup/references/templates/agents/write-novel-deconstruction-agent.md`，必要时可手动复制部署。
- **环境不支持 spawn 子代理**：本 skill 正运行在某个子代理上下文中，无法再起下一层 agent。

> 与 [material-decomposition.md](material-decomposition.md) 阶段 2（原子提取并行 Agent）的关系：本文件描述 Stage 2 的 **agent 调度运维**（spawn/批量/重试/降级），material-decomposition.md 描述 **提取方法论**（A 章节摘要 / B 情节点 / C 角色提取的字段与密度公式）。两者互补，agent prompt 内部的提取要求以 material-decomposition.md 为准。
