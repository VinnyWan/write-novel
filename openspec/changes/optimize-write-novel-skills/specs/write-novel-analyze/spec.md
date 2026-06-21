## ADDED Requirements

### Requirement: Unified analyze entry point

The system SHALL provide a single `write-novel-analyze` skill that accepts both long-form and short-form deconstruction requests. The skill MUST use word count probing to determine the scope (long/short), and SHALL respect explicit user override.

#### Scenario: Short text auto-detected as short-form

- **WHEN** user provides text with word count < 15,000
- **THEN** the system routes to the short-form deconstruction pipeline (Stage 2-6, full-story analysis)

#### Scenario: Long text auto-detected as long-form

- **WHEN** user provides text with word count > 20,000
- **THEN** the system routes to the long-form deconstruction pipeline (Stage 0-6, chapter-level analysis) with a prompt confirming the choice

#### Scenario: Gray zone asks user

- **WHEN** user provides text with word count between 15,000 and 20,000
- **THEN** the system SHALL ask "字数 {N}，介于短/长之间，按短篇还是长篇拆?"

#### Scenario: User explicit override

- **WHEN** user explicitly specifies scope (e.g., "按短篇拆这本长篇")
- **THEN** the system SHALL use the user-specified scope regardless of word count

### Requirement: Backward compatibility aliases for analyze

The system SHALL preserve `/write-novel-long-analyze` and `/write-novel-short-analyze` as aliases that delegate to the unified `write-novel-analyze` skill with the appropriate scope preset.

#### Scenario: Old long-analyze command

- **WHEN** user invokes `/write-novel-long-analyze`
- **THEN** the system routes to `write-novel-analyze` with `scope=long`

#### Scenario: Old short-analyze command

- **WHEN** user invokes `/write-novel-short-analyze`
- **THEN** the system routes to `write-novel-analyze` with `scope=short`

### Requirement: Stage 1 pause point preserved for long-form

The system SHALL continue to pause after Stage 1 (黄金三章) in long-form mode, producing a quick preview report and asking the user whether to continue full deconstruction. In short-form mode, the pipeline runs straight through Stage 2-6 without pausing.

#### Scenario: Long-form pause after Stage 1

- **WHEN** Stage 0+1 complete in long-form mode
- **THEN** the system pauses and asks "黄金三章已拆完，是否继续全量拆解?"

#### Scenario: Short-form no pause

- **WHEN** short-form pipeline starts
- **THEN** the system runs Stage 2-6 without intermediate pauses

### Requirement: Output directory and format consistency

The system SHALL output all deconstruction results to `拆文库/{书名}/` regardless of scope. Long-form output SHALL include chapter-level files (`章节/` directory). Short-form output SHALL include whole-story files (`情节节点.md`, `写作手法.md`).

#### Scenario: Long-form output structure

- **WHEN** long-form deconstruction completes
- **THEN** the output directory contains `章节/`, `角色/`, `剧情/`, `设定/`, `拆文报告.md`, `文风.md`

#### Scenario: Short-form output structure

- **WHEN** short-form deconstruction completes
- **THEN** the output directory contains `拆文报告.md`, `情节节点.md`, `写作手法.md`, `_meta.json`
