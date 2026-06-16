# run-ledger 格式规范

## 文件位置

`追踪/run-ledger.md`

## 用途

记录写作流程每一步的执行状态，支持步骤级断点续传。

## 格式

每行一条记录，格式：

```
| 章节 | 步骤 | 状态 | 时间戳 | 产物路径 |
```

### 步骤编号定义（9 步标准流程）

| 步骤 | 名称 | 执行者 |
|------|------|--------|
| 1/9 | preflight | 主线程 |
| 2/9 | context | context-agent |
| 3/9 | prewrite-gate | 主线程 |
| 4/9 | preparation | 主线程 |
| 5/9 | draft | narrative-writer |
| 6/9 | reviewer | reviewer agent |
| 7/9 | polish | narrative-writer |
| 8/9 | commit | 主线程 |
| 9/9 | postcommit-gate | 主线程 |

### 状态枚举

| 状态 | 含义 |
|------|------|
| `done` | 步骤成功完成 |
| `failed` | 步骤执行失败（有错误信息） |
| `interrupted` | 步骤进行中被中断（可能有部分产物） |
| `skipped` | 步骤被跳过（可选步骤或条件不满足） |

### 示例

```
| 003 | 1/9 preflight | done | 2026-06-14T10:30:00 | - |
| 003 | 2/9 context | done | 2026-06-14T10:32:00 | 追踪/上下文.md |
| 003 | 3/9 prewrite-gate | done | 2026-06-14T10:33:00 | - |
| 003 | 4/9 preparation | done | 2026-06-14T10:35:00 | - |
| 003 | 5/9 draft | done | 2026-06-14T10:50:00 | 正文/Chapter-003.md |
| 003 | 6/9 reviewer | done | 2026-06-14T10:55:00 | 追踪/reviews/Chapter-003-review.md |
| 003 | 7/9 polish | done | 2026-06-14T11:00:00 | 正文/Chapter-003.md |
| 003 | 8/9 commit | done | 2026-06-14T11:02:00 | - |
| 003 | 9/9 postcommit-gate | done | 2026-06-14T11:03:00 | 追踪/state.md, 追踪/foreshadowing.md |
```

### 恢复协议

1. 读取 `追踪/run-ledger.md`，找到最后一条记录
2. 若最后步骤状态为 `done` → 定位下一章
3. 若最后步骤状态为 `failed` 或 `interrupted` → 从该步骤恢复
4. 若产物文件存在但未标记 → 标记为 "可能部分完成"，询问用户
5. 产物超过 24 小时未更新 → 标记"可能过期"，建议重新执行
