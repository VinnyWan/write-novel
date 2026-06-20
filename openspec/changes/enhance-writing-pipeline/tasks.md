## 1. 模板新增与更新

- [x] 1.1 新增 `设定/世界观.md` 模板（时代背景/地理/势力格局/力量体系，按字数分级）
- [x] 1.2 新增 `设定/题材定位.md` 模板（题材/风格/目标读者/对标作品）
- [x] 1.3 新增 `大纲/剧情线.md` 模板（主线+支线，每条含起止卷/核心冲突/关键节点）
- [x] 1.4 更新 `大纲/细纲_第X章.md` 模板：frontmatter 增加 event/conflict/turning_point 三字段 + `## 写作段落` 段落
- [x] 1.5 更新 `设定/角色/主角_模板.md`：增加 OOC 护栏段落
- [x] 1.6 更新 `设定/角色/配角_模板.md`：增加与主角关系/功能定位字段
- [x] 1.7 更新 `设定/关系.md` 模板：增加关系类型/当前状态/冲突点/变化预期字段

## 2. story-setup 增加世界观初始化（Phase 1.6）

- [x] 2.1 在 `story-setup/SKILL.md` 中新增 Phase 1.6 流程描述（在配置向导后、部署前）
- [x] 2.2 Phase 1.6 读入用户配置（字数/题材/风格），调用 story-architect agent 产出世界观文件
- [x] 2.3 实现按字数分级的模板选择逻辑（<100万字简化模板，>=100万字完整模板）
- [x] 2.4 实现 `设定/世界观.md` 已存在时的跳过检测 + `--rebuild-worldbuilding` 标志
- [x] 2.5 更新 setup 验证清单在 Phase 3 中加入世界观文件存在性检查

## 3. story-long-write Phase 2 角色设计集中化

- [x] 3.1 调整 `story-long-write/SKILL.md` Phase 2 描述：角色设计提升为独立子阶段
- [x] 3.2 character-designer agent 调用流程改为一次完成主角+配角+羁绊图
- [x] 3.3 实现配角数量上限逻辑（目标字数/20万）
- [x] 3.4 角色卡输出格式增加 OOC 护栏段落
- [x] 3.5 `设定/关系.md` 输出格式增加关系动态字段

## 4. story-long-write Phase 3a/3b 剧情线与细纲结构强化

- [x] 4.1 在 Phase 3a 卷纲设计前增加剧情线设计 Gate：先产出 `大纲/剧情线.md`
- [x] 4.2 剧情线缺失时阻塞卷纲产出，提示补充
- [x] 4.3 卷纲每卷摘要增加剧情线推进标注
- [x] 4.4 Phase 3b 细纲 frontmatter 增加 event/conflict/turning_point 三要素必填校验
- [x] 4.5 细纲 `strand` 字段改为必填，标注推进的剧情线
- [x] 4.6 细纲产出 Gate 增加三要素完整性检查（缺失则拒绝）

## 5. story-long-write Phase 4 细纲驱动分段写作

- [x] 5.1 Stage B（Prewrite Gate）增加细纲拆段步骤：三要素→3-6个写作段落
- [x] 5.2 拆段输出写入细纲文件的 `## 写作段落` 段落
- [x] 5.3 爆发段识别逻辑：conflict.intensity >= 4 或 turning_point = true → 至少含 1 段"爆发"
- [x] 5.4 Stage C narrative-writer 调整为按段写作，段间 `---` 分隔
- [x] 5.5 写作偏离记录：允许段落数 ±1，偏离写入 `<!-- deviation -->` 注释
- [x] 5.6 Stage E（Postwrite Gate）增加段落覆盖率校验（段落数 ±1 + 覆盖率 >= 80%）
- [x] 5.7 日更模式默认跳过拆段和覆盖率校验，增加 `--segmented-writing` 标志

## 6. Agent 定义更新

- [x] 6.1 更新 `story-architect` agent 定义：增加世界观构建指引、剧情线设计方法论
- [x] 6.2 更新 `character-designer` agent 定义：集中化角色设计流程、羁绊图输出格式、OOC 护栏模板
- [x] 6.3 更新 `narrative-writer` agent 定义：分段写作流程、叙事功能（铺垫/推进/爆发/余韵）指引

## 7. Reviewer 校验规则更新

- [x] 7.1 新增三要素完整性校验规则（event/conflict/turning_point 是否存在）
- [x] 7.2 新增冲突强度节奏检测规则（连续3章 intensity <= 2 → 告警）
- [x] 7.3 新增转折点落地检测规则（按类型交叉校验后续章节是否体现转折）
- [x] 7.4 新增剧情线推进检测规则（支线连续30章未推进 → 告警）
- [x] 7.5 新增段落覆盖率检测规则

## 8. 验证与测试

- [ ] 8.1 用现有项目执行 story-setup，验证 Phase 1.6 世界观产出完整性
- [ ] 8.2 用新书项目走通完整 Phase 1-5 流程，验证各环节衔接
- [ ] 8.3 验证按字数分级的模板选择正确性
- [ ] 8.4 验证细纲三要素缺失时的 Gate 阻塞行为
- [ ] 8.5 验证分段写作的段落覆盖率和偏离处理
- [ ] 8.6 验证日更模式跳过分段逻辑
- [x] 8.7 运行 static-check.sh 确保无新增质量问题
