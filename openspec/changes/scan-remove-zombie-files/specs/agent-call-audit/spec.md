## ADDED Requirements

### Requirement: Detect uncalled agent definitions
The system SHALL scan all skill SKILL.md files for `subagent_type` references and compare against the set of agent definition files in `agents/`. Agent definitions with zero skill callers are reported.

#### Scenario: Agent with zero callers
- **WHEN** `agents/write-novel-story-explorer.md` exists but no SKILL.md in any skill references `write-novel:story-explorer` or `story-explorer` as a subagent_type
- **THEN** the check reports it as WARN with "agent definition has zero callers"

#### Scenario: Agent with active callers
- **WHEN** `agents/write-novel-reviewer.md` exists and `write-novel-review/SKILL.md` references it via `subagent_type: "write-novel:reviewer"`
- **THEN** the check does NOT report it

### Requirement: Agent count matches agent directory
The system SHALL verify that the total number of agent definitions matches expectations and report any orphaned `.md` files in `agents/` that do not follow the naming convention `write-novel-<name>.md`.

#### Scenario: Non-conforming file in agents directory
- **WHEN** `agents/some-random-file.md` exists but doesn't match the `write-novel-*` naming pattern
- **THEN** the check reports it as WARN

### Requirement: Integration with static check
The agent audit SHALL run as part of `static-check.sh` (Check 13) and SHALL report findings grouped by type: zero-caller agents, non-conforming files.

#### Scenario: Agent audit integrated into static check
- **WHEN** `static-check.sh` runs
- **THEN** agent call audit appears as Check 13 with PASS/WARN/FAIL status
