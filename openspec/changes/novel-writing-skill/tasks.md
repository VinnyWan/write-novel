## 1. 基础设施搭建

- [x] 1.1 创建 `skills/` 下 6 个 skill 目录结构（write-novel、write-novel-long-write、write-novel-deslop、write-novel-review、write-novel-setup、write-novel-cover），每个包含 `SKILL.md` 和 `references/` 子目录
- [x] 1.2 从 `oh-story-claudecode` 复制写作参考文件到 `write-novel-long-write/references/`（题材目录、写作公式、禁用词表、对话技巧、情绪方法、人物设计方法等 20+ 文件）
- [x] 1.3 从 `oh-story-claudecode` 复制去 AI 味参考文件到 `write-novel-deslop/references/`（anti-ai-writing.md、banned-words.md）
- [x] 1.4 从 `oh-story-claudecode` 复制审查参考文件到 `write-novel-review/references/`（review-schema.md）
- [x] 1.5 创建 `write-novel-setup/references/` 下的项目模板文件清单和部署配置
- [x] 1.6 验证所有参考文件中的路径引用已适配全中文目录约定（将原项目英文路径映射到本项目中文路径）

## 2. 数据模型固化

- [x] 2.1 完善 `人物卡片模板.md`：确认 Frontmatter 中文键名完整，补充 `关联角色` 的 Wikilink 示例（`[[人物/角色名]]`），添加人物关系图模板
- [x] 2.2 完善 `世界设定模板.md`：确认境界划分表格、势力格局、经济体系等模板区块完整
- [x] 2.3 完善 `分卷大纲模板.md`：确认卷级 Frontmatter 字段，补充分卷章节目录表格模板
- [x] 2.4 完善 `分卷与单章细纲模板.md`：硬性剧本任务、关键场景设计、出场人物状态、期待感控制模板区块
- [x] 2.5 完善 `全局写作状态.md`：确认进度 Frontmatter 字段、系统提示词区域、高压线禁用词区域、用户保护区标记
- [x] 2.6 完善 `伏笔与线索回收池.md`：确认三态状态机表格模板、逾期预警区、回收日志区

## 3. 路由 skill 实现

- [x] 3.1 编写 `write-novel/SKILL.md`：路由表（7 个意图→skill 映射）、路由流程（意图分析→匹配→分发→fallback）、项目状态感知逻辑
- [x] 3.2 实现路由分发逻辑：关键词匹配规则、优先级排序（长命令优先于短命令）、无法匹配时的选项展示
- [x] 3.3 编写路由后的项目状态检查：检查 `人物/` 和 `世界设定/` 目录是否存在，如未初始化引导 write-novel-setup
- [ ] 3.4 测试路由：模拟 5 种典型用户输入（"开书""续写""去AI味""审查""搭环境"），验证路由正确性

## 4. write-novel-setup 实现

- [x] 4.1 编写 `write-novel-setup/SKILL.md`：部署流程（检查已有文件→创建目录树→写入模板→部署 hooks/agents→验证）
- [x] 4.2 实现增量部署逻辑：只补充缺失文件，不覆盖已有内容，特别是用户保护区内容
- [x] 4.3 实现 hooks 部署：将写作相关的 session hooks 配置写入 `.claude/settings.local.json`
- [x] 4.4 实现 Agent 定义部署：将 5 个 Agent（write-novel-explorer、write-novel-researcher、write-novel-deslop-agent、write-novel-senior-editor、write-novel-picky-reader）定义写入项目 `agents/` 目录
- [ ] 4.5 测试部署：在空目录执行 write-novel-setup，验证所有文件和目录正确创建

## 5. 长篇写作 skill 实现

- [x] 5.1 编写 `write-novel-long-write/SKILL.md` 主文件：场景路由（日更/大修/开书）、Phase 1-5 完整流程描述
- [x] 5.2 实现 Phase 1（选题确认）：读取 `选题决策.md` 逻辑、提问流程（题材/情绪/对标书）、对标上下文加载
- [x] 5.3 实现 Phase 2（设定搭建）：角色卡片创建、世界观设定文件创建、力量体系设计引导
- [x] 5.4 实现 Phase 3（大纲细纲）：分卷大纲生成、单章细纲生成、伏笔规划与埋设点标记
- [x] 5.5 实现 Phase 4（正文写作）：上下文按需加载（细纲+人物状态+伏笔+设定+全局提示词）、写作约束与高压线注入、正文生成
- [x] 5.6 实现 Phase 5（续航闭环）：章节存档→摘要生成→Frontmatter 状态更新→伏笔状态推进→逾期预警检查
- [x] 5.7 编写 `workflow-daily.md`：日更续写快速流程（加载上章尾声→本章细纲→写作→闭环，串行批量模式）
- [x] 5.8 编写 `workflow-revision.md`：大修/回炉流程（定位目标章节→加载上下文→重写→更新关联伏笔和摘要）
- [x] 5.9 实现双语链接解析：`[[路径/文件名]]` → 正则匹配 → Read 文件 → 提取关键字段 → 注入上下文

## 6. write-novel-deslop 实现

- [x] 6.1 编写 `write-novel-deslop/SKILL.md`：检测流程（加载禁用词表→逐行扫描→标记违规→生成修改建议）
- [x] 6.2 实现 AI 痕迹检测规则：模板句式检测、重复开头检测、过度书面化检测、对话不自然检测
- [x] 6.3 实现去 AI 味改写建议生成：针对每种检测类型输出具体的替换建议和改写示例
- [x] 6.4 与写作流程集成：在 Phase 4 正文生成后自动运行 deslop 检查（可选开关）

## 7. write-novel-review 实现（审查 + 质量管道编排）

- [x] 7.1 编写 `write-novel-review/SKILL.md`：完整质量管道流程（Phase 1: 4 Agent 并行审查 → 综合裁决 → Phase 2: 3 Agent 串行加工 → 汇总报告）
- [x] 7.2 定义 Phase 1 审查 Agent 的 4 个 prompt 模板：结构审查、文风审查、连贯性审查、爽点审查，各自独立只读
- [x] 7.3 实现综合裁决逻辑：按严重性排序（致命/严重/建议），跨 Agent 去重，统一排版输出
- [x] 7.4 实现质量管道串行编排：审查报告生成后，依次启动 deslop-agent → senior-editor → picky-reader，上一轮输出作为下一轮输入
- [x] 7.5 实现管道中断逻辑：任一 Agent 发现致命问题时暂停，向用户汇报并等待决策
- [x] 7.6 实现最终报告汇总：Phase 1 审查摘要 + Phase 2 修改日志 + Phase 3 编辑意见 + Phase 4 读者感受 + 综合评估
- [ ] 7.7 测试完整质量管道：用一篇测试文本运行，验证 4+3 Agent 全流程和报告质量

## 8. 封面生成占位

- [x] 8.1 编写 `write-novel-cover/SKILL.md`：轻量占位 skill，说明封面生成需要配合外部工具（如 DALL-E/Midjourney），本 skill 负责生成封面设计提示词

## 9. 常驻 Agent 实现

- [x] 9.1 编写 `write-novel-explorer` Agent 定义：只读查询代理，接收查询类型（角色/伏笔/进度/设定）和参数，Read 对应文件返回信息
- [x] 9.2 编写 `write-novel-researcher` Agent 定义：外部搜索代理，调用 WebSearch 查资料，返回摘要
- [x] 9.3 编写 Agent 的查询协议：统一的结构化查询格式，方便主 skill 调用

## 9b. 质量管道 Agent 实现

- [x] 9b.1 编写 `write-novel-deslop-agent` Agent 定义：接收正文 + 审查报告 → 逐句扫描 AI 痕迹（使用 `references/banned-words.md` 和 `references/anti-ai-writing.md`）→ 直接改写输出清洁文本 + 修改日志
- [x] 9b.2 编写 `write-novel-senior-editor` Agent 定义：接收清洁文本 → 商业向深度审稿（开篇钩子/节奏/爽点密度/人物辨识度/章节钩子）→ 输出审稿意见 + 具体修改建议
- [x] 9b.3 编写 `write-novel-picky-reader` Agent 定义：接收清洁文本 + 编辑意见 → 模拟真实挑剔读者体验（第一句抓人/出戏点/情绪打到/想不想点下一章）→ 输出读后感 + 弃书风险评估
- [x] 9b.4 定义质量管道 Agent 之间的输入输出契约：确保数据格式一致，上一轮输出可直接作为下一轮输入

## 10. 集成验证

- [ ] 10.1 端到端测试：运行 write-novel-setup 初始化项目 → write-novel 路由到 long-write → 执行开书流程 Phase 1-3 → 生成第一章 → 续航闭环 → review 完整质量管道（4 Agent 并行审查 + 3 Agent 串行加工）
- [ ] 10.2 验证全中文路径：确认所有目录名、文件名、Frontmatter 键名均为中文，无英文/拼音残留
- [ ] 10.3 验证双语链接：在细纲中添加 `[[人物/测试角色]]`，确认系统能正确解析并加载对应文件
- [ ] 10.4 验证伏笔追踪：埋设一个伏笔 → 推进 → 回收，确认状态机三态转换正确
- [ ] 10.5 验证用户保护区：在 `全局写作状态.md` 的 USER_AREA 区域写入自定义内容，执行续航闭环后确认内容未被修改
- [ ] 10.6 验证上下文最小化：确认写作时只加载必要文件，未加载其他卷的细纲或其他章节正文
