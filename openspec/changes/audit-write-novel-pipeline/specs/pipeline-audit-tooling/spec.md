## ADDED Requirements

### Requirement: Agent count consistency check
The system SHALL ensure that the number of agents declared in write-novel-setup Phase 3 matches the number of agent definition files in `write-novel/agents/`.

#### Scenario: Agent count matches
- **WHEN** `write-novel/agents/` contains exactly 8 agent definition files
- **THEN** write-novel-setup Phase 3 SHALL check for exactly 8 agents

#### Scenario: Agent count mismatch detected
- **WHEN** doctor performs global health check on agent definitions
- **THEN** it SHALL report a warning if agent count in templates differs from main agent directory

### Requirement: Shared pointer file completeness
All skills that reference `references/shared/<file>.md` SHALL have the corresponding pointer file present in their skill-local `references/shared/` directory.

#### Scenario: Missing shared pointer detected
- **WHEN** a skill's SKILL.md references `references/shared/report-template.md`
- **THEN** the corresponding pointer file SHALL exist at `<skill>/references/shared/report-template.md`

#### Scenario: Pointer file points to correct source
- **WHEN** a pointer file exists
- **THEN** it SHALL contain a valid relative path to the shared source in `references/shared/`

### Requirement: Subagent type naming consistency
All skill files and agent definition files SHALL use a consistent format for `subagent_type` identifiers.

#### Scenario: Skill file uses colon format
- **WHEN** a skill spawns an agent
- **THEN** the subagent_type value SHALL use the format `<plugin>:<agent-base-name>` (colon separator)

#### Scenario: Agent file documentation matches
- **WHEN** an agent's "被调用协议" section documents the calling convention
- **THEN** the subagent_type example SHALL match the format used by skill files

### Requirement: Script path reference validity
All script paths referenced in SKILL.md files SHALL resolve to existing files relative to the plugin root.

#### Scenario: normalize-punctuation.js path valid
- **WHEN** write-novel-review references `scripts/normalize-punctuation.js`
- **THEN** the file SHALL exist at `<plugin-root>/scripts/normalize-punctuation.js`

#### Scenario: static-check.sh path valid
- **WHEN** write-novel-doctor references `bash scripts/static-check.sh`
- **THEN** the file SHALL exist at `<plugin-root>/scripts/static-check.sh`
