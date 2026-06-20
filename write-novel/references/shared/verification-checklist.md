# 集成验证清单

本文件用于验证 `competitor-analysis-and-optimization-round2` 变更的 5 大能力是否正常工作。

## 1. 故事系统工程验证

- [ ] 1.1 在大纲阶段运行 Phase 3「细纲转合约」，检查 `.story-system/contracts/chapter_001.contract.md` 是否生成
- [ ] 1.2 检查合约文件包含所有必填 YAML 字段：cbn, cpns(2-4条), cen, strand, hook_type, payoff_density, target_words
- [ ] 1.3 故意创建不完整合约（缺少 CEN），运行 narrative-writer —— 应拒绝写作并提示合约不完整
- [ ] 1.4 写正文包含 must_cover 中某项后运行 reviewer —— 应 PASS 该项
- [ ] 1.5 正文中出现 forbidden 内容后运行 reviewer —— 应报告 blocking issue
- [ ] 1.6 章末检查 `.story-system/commits/chapter_001.commit.md` 是否创建且包含合约合规状态

## 2. 运行账本与恢复验证

- [ ] 2.1 写完一章后检查 `追踪/run-ledger.md` —— 应有 prewrite-gate/draft/reviewer/precommit-gate/commit/postcommit-gate 各步骤的 done 记录
- [ ] 2.2 运行 `/write-novel-long-write {N} --resume` —— 应跳过已完成步骤，仅执行未完步骤
- [ ] 2.3 模拟中断：手动将 run-ledger 最后一行状态改为 `interrupted`，运行 `--resume` —— 应从该步骤恢复
- [ ] 2.4 Context compact 后检查 run-ledger —— 应有 `context_compact | interrupted` 记录
- [ ] 2.5 Post-compact 后检查输出 —— 应显示 resume 诊断（合约/细纲/前章路径 + 中断检测）

## 3. 投影管线验证

- [ ] 3.1 章末 commit 后检查 `追踪/角色状态.md` —— 应有本章出场角色的状态更新
- [ ] 3.2 章末 commit 后检查 `追踪/索引.md` —— 应有新实体/关系/伏笔条目
- [ ] 3.3 章末 commit 后检查 `追踪/章节摘要/第{N}章.md` —— 应包含摘要+情节点+角色+连接
- [ ] 3.4 检查 `追踪/projection-log.jsonl` —— 应有本章的投影记录，各 target 状态为 success/skipped

## 4. 标准化报告验证

- [ ] 4.1 write-novel-long-write 写完一章后的输出是否符合 3 段式报告（完成状态/问题/下一步）？
- [ ] 4.2 write-novel-review 输出是否包含 S1-S4 严重度汇总和下一步命令？
- [ ] 4.3 write-novel-deslop 输出是否包含 AI 味定级和修改统计？
- [ ] 4.4 是否有任何 skill 输出暴露了原始 JSON 或 traceback？（应全部没有）

## 5. 模式学习验证

- [ ] 5.1 写完第 1 章后检查 `追踪/project_memory.json` —— 如识别到模式，对应类别数组应有条目
- [ ] 5.2 连续写 3 章后检查 —— 每类条目数 ≤200，较旧条目可能被 LRU 淘汰
- [ ] 5.3 写完全相同的模式后检查 —— 应被精确去重，不增加条目
- [ ] 5.4 写第 5 章时，write-novel-story-architect 的 brief 是否包含「历史模式参考」小节？（如 project_memory.json 有匹配模式）
- [ ] 5.5 运行 `/write-novel-doctor` —— 应包含 project_memory.json 健康检查（文件完整性、各类条目数）
