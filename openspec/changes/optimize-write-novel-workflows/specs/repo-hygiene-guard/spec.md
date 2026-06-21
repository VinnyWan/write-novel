## ADDED Requirements

### Requirement: 依赖与构建产物不入库

Git 仓库 MUST NOT 跟踪第三方依赖目录（`node_modules/`）、构建产物目录（`dist/`）或缓存目录（`__pycache__/`、`.pytest_cache/`）。`.gitignore` MUST 覆盖这些模式，使其不再被新提交回流。

#### Scenario: 已跟踪的依赖目录被检测

- **WHEN** 仓库卫生校验运行 `git ls-files` 且结果命中 `node_modules/`、`dist/`、`__pycache__/` 或 `.pytest_cache/` 路径
- **THEN** 校验 MUST 以非零退出码报告被跟踪的产物目录（含命中数量与示例路径）

#### Scenario: gitignore 覆盖产物模式

- **WHEN** 检查 `.gitignore` 内容
- **THEN** 其 MUST 包含 `node_modules/`、`dist/`、`__pycache__/`、`.pytest_cache/`（或等价模式），且 `git status` 在这些目录存在时不显示其为未跟踪/已修改

#### Scenario: 取消跟踪后本地副本保留

- **WHEN** 对已跟踪的 `node_modules/` 执行取消跟踪操作（`git rm -r --cached`）
- **THEN** 这些文件 MUST 从 Git 索引移除，但本地文件系统中的副本 MUST 仍然存在（dashboard 仍可本地运行）
