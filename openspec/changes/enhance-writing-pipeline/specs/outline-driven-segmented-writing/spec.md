## ADDED Requirements

### Requirement: Phase 4 Stage B 执行细纲拆段

story-long-write Phase 4 Stage B（Prewrite Gate）SHALL 在写作前将细纲的 event/conflict/turning_point 拆分为 3-6 个写作段落，每段标注：

- 预期字数（不超过该章目标字数的 40%）
- 叙事功能（铺垫/推进/爆发/余韵）
- 对应的事件或冲突点

拆段结果写入细纲文件的 `## 写作段落` 段落（位于 frontmatter 之后、正文之前），作为 Stage C 的输入。

#### Scenario: 细纲拆段产出

- **WHEN** Phase 4 Stage B 启动
- **THEN** 读取细纲的三要素（event/conflict/turning_point）
- **THEN** 拆分为 3-6 个段落，每段含预期字数/叙事功能/对应事件
- **THEN** 写入细纲文件的 `## 写作段落` 段落

#### Scenario: 爆发段识别

- **WHEN** conflict.intensity >= 4 或 turning_point.is_turning = true 的章节
- **THEN** 拆段中至少包含 1 个叙事功能为"爆发"的段落
- **THEN** "爆发"段的预期字数不低于该章总字数的 25%

### Requirement: Stage C 按段写作

narrative-writer agent 在 Stage C 执行正文写作时 SHALL 以拆段为输入，逐段产出正文，段与段之间用 `---` 分隔。每段写作时 SHALL 只关注当前段的叙事功能，不跨越段落边界。

#### Scenario: 逐段写作输出格式

- **WHEN** narrative-writer 执行 Stage C
- **THEN** 正文文件按段落组织，段间 `---` 分隔
- **THEN** 每段开头标注叙事功能（如 `<!-- 铺垫 -->`）
- **THEN** 全文保持统一叙事视角和人称

#### Scenario: 写作中偏离拆段

- **WHEN** narrative-writer 在写作中发现拆段的段落划分不合理
- **THEN** 允许适度偏离（段落数差异 ±1，叙事功能可调整）
- **THEN** 偏离情况记录在文件末尾的 `<!-- deviation: ... -->` 注释中

### Requirement: Stage E 校验段落覆盖率

Phase 4 Stage E（Postwrite Gate）SHALL 校验实际正文与拆段计划的一致性：

- 段落数是否在计划 ±1 范围内
- 每段的叙事功能是否达成（铺垫段是否真正在铺垫，爆发段是否有高潮内容）
- 整体段落覆盖率 >= 80%（即至少 80% 的计划段落有对应正文）

#### Scenario: 段落覆盖率校验通过

- **WHEN** 实际段落数 = 计划段落数 ± 1，且覆盖率 >= 80%
- **THEN** Postwrite Gate 通过
- **THEN** 段落覆盖情况写入 `追踪/状态.md`

#### Scenario: 段落覆盖率校验失败

- **WHEN** 实际段落数偏离计划 > 1，或覆盖率 < 80%
- **THEN** Postwrite Gate 生成警告
- **THEN** 警告记录到 `追踪/状态.md` 的问题列表
- **THEN** 不阻塞正文提交（警告级而非阻塞级）

### Requirement: 日更模式分段写作可选

日更模式下，细纲拆段和段落覆盖率校验 SHALL 为可选（默认跳过），用户可通过 `--segmented-writing` 标志启用。

#### Scenario: 日更模式跳过拆段

- **WHEN** 用户以日更模式执行 Phase 4
- **THEN** 默认跳过 Stage B 的细纲拆段和 Stage E 的段落覆盖率校验
- **THEN** 正文不分段，连续输出
