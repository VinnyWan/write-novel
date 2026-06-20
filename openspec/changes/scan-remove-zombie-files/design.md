## Context

`static-check.sh` 当前 16 checks 全部 PASS，但检查方向是**正向**的——"从引用方出发，目标是否存在"。缺失的是**反向**视角——"从文件出发，谁引用了它"。正向检查能发现悬空引用，但无法发现零引用僵尸文件。

此外，存在**循环引用**的可能：skill A 的 reference 文件引用 skill B 的 reference 文件，而后者又引用前者。循环引用不一定会导致悬空 error，但会造成加载时的无限递归风险。

当前 `references/shared/MANIFEST.yaml` 记录了 23 个共享文件及其 canonical owner skill，提供了部分消费关系，但并非全貌——per-skill `references/` 目录下的文件未登记消费方。

## Goals / Non-Goals

**Goals:**
- 新增 Check 11「反向引用计数」：扫描全仓库 .md 文件，对每个文件统计被引用次数，输出零引用文件列表（排除已知保留项）
- 新增 Check 12「循环引用检测」：构建内部引用有向图，检测并报告引用环
- 可选：新增 Check 13「Agent 调用方检测」：扫描 skill 的 `subagent_type` 引用，找出零调用 agent
- 整合输出：将检测结果以可用于清理决策的格式输出

**Non-Goals:**
- 不自动删除文件（仅报告僵尸候选，由后续 task 手动删除）
- 不修改 `CLAUDE.md` 或版本号（这些属于 `cleanup-stale-references-and-check-gaps` 的任务范围）
- 不对 `references/shared/` 做重复清理（上一个 change 已处理）
- 不改变现有 Check 1-10 的行为

## Decisions

### Decision 1: 反向引用计数——独立 Bash 函数内嵌于 static-check.sh

**选择**：在 `static-check.sh` 内新增 `check_reverse_references()` 函数，与现有 Check 1-10 并列。
**替代方案**：独立 Python 脚本。不选——需要维护额外的解析和路径查找逻辑，与现有 `extract_referenced_paths` / `resolve_ref` 重复。
**实现要点**：
- 扫描范围：`skills/*/SKILL.md` + `skills/*/references/**/*.md` + `agents/*.md` + `hooks/*.md` + `references/shared/*.md` + `references/rules/*.md`
- 对每个文件，提取其引用的其他文件（复用 `extract_referenced_paths` + `extract_agent_refs` + wikilink 提取）
- 构建关联数组 `ref_count[file_rel_path]` 记录被引用次数
- 零引用文件输出为 WARN（而非 FAIL），因为这可能是合法设计（如 report-template.md 仅在运行时使用）
- 白名单：`project-memory-init.json`、`author_error_catalog.json`、`author_glossary.json`、`writing_references.json`、`MANIFEST.yaml`、`.gitkeep`

### Decision 2: 循环引用检测——基于文件引用的简单 DFS

**选择**：在 `static-check.sh` 内新增 `check_cyclic_references()` 函数，使用 DFS + 递归栈检测环。
**实现要点**：
- 构建邻接表：file → [referenced_files]
- 对每个节点执行 DFS，维护 `visiting` 栈
- 检测到 back-edge（目标在 visiting 栈中）→ 报告环
- 检测到环时 FAIL（因为循环引用可能导致 agent 加载时无限递归）
- 限制：不追踪跨 `references/methodology/` 的回退引用（因为 methodology 文件是纯被读的静态知识，不可能反向引用 skill 文件）

### Decision 3: 统一路径表示

**选择**：所有被引用文件以相对 `PLUGIN_ROOT` 的路径表示（如 `skills/write-novel-long-write/references/state-tracking.md`）。
**理由**：与 `resolve_ref` 的三级解析逻辑一致，且方便人工审查。

## Risks / Trade-offs

- **[Risk] 误报零引用但对 agent 运行时必要的文件** → 缓解：白名单 + 仅输出 WARN 而非 FAIL，由人工审查后决定删除
- **[Risk] 循环检测性能** → 缓解：文件总数 < 500，即使 O(N²) 的 DFS 也在秒级完成，无需优化
- **[Risk] 裸名引用导致漏计数** → 缓解：当前的 bare 检测逻辑（Check 7）已能识别大部分裸名引用，反向引用计数复用同一解析
