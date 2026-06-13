---
name: story-dashboard
description: |
  启动只读小说管理面板，查看项目状态、实体图谱、章节内容与追读力数据。
  触发方式：/story-dashboard、「面板」「数据看板」（旧触发词：/webnovel-dashboard）
  来源：webnovel-dashboard
allowed-tools: Bash Read
---

# story-dashboard：小说管理面板

## 目标

- 在本地启动只读 Web 面板，查看创作进度、设定词典、关系图谱、章节内容与追读力数据。
- 暴露故事系统状态：进度、伏笔、角色、质量趋势。
- 可监听项目文件变化，但不修改任何项目文件。

## 执行流程

### Step 1：确认环境

```bash
export WORKSPACE_ROOT="${CLAUDE_PROJECT_DIR:-$PWD}"

if [ -z "${CLAUDE_PLUGIN_ROOT}" ] || [ ! -d "${CLAUDE_PLUGIN_ROOT}/dashboard" ]; then
  echo "ERROR: 未找到 dashboard 模块: ${CLAUDE_PLUGIN_ROOT}/dashboard" >&2
  exit 1
fi

export DASHBOARD_DIR="${CLAUDE_PLUGIN_ROOT}/dashboard"
export SCRIPTS_DIR="${CLAUDE_PLUGIN_ROOT}/scripts"
```

### Step 2：启动 Dashboard

```bash
cd "${DASHBOARD_DIR}"
python -X utf8 -m uvicorn main:app --host 127.0.0.1 --port 8765 --reload &
```

### Step 3：展示访问地址

- 本地访问：http://127.0.0.1:8765
- 数据来源：项目目录下的 Markdown 文件（设定/、追踪/、正文/）
- 只读模式：不修改任何项目文件

## 面板功能

| 功能 | 说明 | 数据源 |
|------|------|--------|
| 创作进度 | 卷/章完成情况、字数统计 | `追踪/progress.md` |
| 角色图谱 | 角色关系网络可视化 | `人物/*.md` |
| 伏笔追踪 | 伏笔状态一览 | `追踪/foreshadowing.md` |
| 质量趋势 | 逐章质量指标变化 | `追踪/progress.md` |
| 章节预览 | 正文内容浏览 | `正文/Chapter-*.md` |
| 设定词典 | 世界观/力量体系查询 | `设定/MASTER_SETTING.md` |
