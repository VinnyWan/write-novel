## ADDED Requirements

### Requirement: Phase 2 一次性完成角色集中设计

story-long-write Phase 2（核心设定）中的角色设计环节 SHALL 由 character-designer agent 集中执行，一次性产出以下文件：

- `设定/角色/主角_<姓名>.md`：完整主角卡，含身份/性格/动机弧线/语言风格档案/OOC 护栏
- `设定/角色/配角_<姓名>.md`（每人一个文件）：核心配角卡，含身份/性格/与主角关系/功能定位/OOC 护栏
- `设定/关系.md`：人物羁绊图，含所有已建角色之间的关系类型（核心对立/核心同盟/核心羁绊/功能关系）、冲突点、变化预期

配角数量上限 SHALL = 目标字数 / 20 万（即 200 万字最多 10 个核心配角）。

#### Scenario: 新书角色集中设计

- **WHEN** 用户在 story-long-write Phase 2 进入角色设计环节
- **THEN** character-designer agent 并行读取世界观设定和题材定位
- **THEN** 一次性产出主角卡、核心配角卡（上限按字数）、羁绊图
- **THEN** 所有文件写入对应路径

#### Scenario: Phase 3b 仅做增量配角补全

- **WHEN** 细纲中出现 Phase 2 未建档的角色且该角色后续出场 >= 2 次
- **THEN** character-designer agent 为新角色建简化卡（身份/性格/功能定位，不含完整语言风格档案）
- **THEN** 更新 `设定/关系.md` 添加新角色的关系连线
- **THEN** 已建档角色不被重复修改

### Requirement: 角色卡含 OOC 行为护栏

每个重要角色（主角 + 核心配角）的角色卡 SHALL 包含 OOC 护栏段落，定义：绝对不做的事、容易触发的情绪点、行为模式边界、道德底线。

#### Scenario: 主角卡包含 OOC 护栏

- **WHEN** character-designer 产出主角卡
- **THEN** 角色卡末尾包含 "OOC 行为护栏" 段落
- **THEN** 段落包含至少 3 条 "绝对不做" 的行为边界

### Requirement: 羁绊图记录关系动态

`设定/关系.md` SHALL 为每对关系记录：关系类型、当前状态（如"初识/信任/破裂/修复"）、冲突点、变化预期（如"第3卷决裂、第5卷和解"）。

#### Scenario: 关系变化追踪

- **WHEN** 正文写作推进到关系变化的章节
- **THEN** Phase 4 Stage E（Postwrite Gate）更新 `追踪/状态.md` 中的关系状态
- **THEN** reviewer agent 可在审查时交叉校验角色行为是否符合当前关系状态
