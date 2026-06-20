## ADDED Requirements

### Requirement: Reverse reference counting for all plugin files
The system SHALL scan all Markdown files within the plugin (`skills/`, `agents/`, `hooks/`, `references/shared/`, `references/rules/`) and compute, for each file, the number of times it is referenced by other files.

#### Scenario: File referenced by multiple skills
- **WHEN** `references/shared/quality-checklist.md` is referenced by `write-novel-long-write/SKILL.md`, `write-novel-short-write/SKILL.md`, and `write-novel-review/SKILL.md`
- **THEN** its reference count is at least 3

#### Scenario: File with zero references
- **WHEN** a file in `skills/<skill>/references/` is not referenced by any SKILL.md, any other reference file, or any agent definition
- **THEN** the check reports it as WARN with "zero inbound references"

#### Scenario: Whitelisted file excluded from zero-reference warning
- **WHEN** a file appears in the zero-reference whitelist (MANIFEST.yaml, .gitkeep, JSON config files used at runtime)
- **THEN** the check does NOT report it even if it has zero references

### Requirement: Scan scope covers all reference types
The system SHALL count references from the following source types:
- Markdown links `](path/to/file.md)`
- Wikilinks `[[file-name]]` or `[[path/to/file]]`
- Backtick-wrapped file paths `` `path/to/file.md` ``
- Agent references via `subagent_type: "agent-name"` or `subagent_type="agent-name"`
- Bare prose `.md` filenames (with WARN classification to indicate lower confidence)

#### Scenario: Wikilink reference counted
- **WHEN** file A contains `[[quality-checklist]]` and a file named `quality-checklist.md` exists in the same directory
- **THEN** the reference is counted toward `quality-checklist.md`'s inbound count

#### Scenario: Agent reference counted
- **WHEN** a skill's SKILL.md contains `subagent_type: "write-novel:reviewer"`
- **THEN** the agent definition `agents/write-novel-reviewer.md` gets an inbound reference count increment

### Requirement: Output format supports cleanup decisions
The system SHALL output zero-reference findings grouped by directory, with file path and size, to support manual cleanup review.

#### Scenario: Zero-reference output grouping
- **WHEN** the check completes with multiple zero-reference files
- **THEN** output lists them grouped under headers like "skills/<skill-name>/references/" with relative paths
