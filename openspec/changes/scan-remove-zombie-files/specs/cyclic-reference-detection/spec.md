## ADDED Requirements

### Requirement: Detect simple two-node cycles
The system SHALL detect when file A references file B and file B references file A, forming a direct 2-node cycle.

#### Scenario: Two files referencing each other
- **WHEN** `references/workflow-daily.md` contains `](workflow-revision.md)` and `references/workflow-revision.md` contains `](workflow-daily.md)`
- **THEN** the check reports a cycle: `workflow-daily.md → workflow-revision.md → workflow-daily.md`

### Requirement: Detect multi-hop cycles
The system SHALL detect cycles spanning three or more files (A→B→C→A).

#### Scenario: Three-file cycle
- **WHEN** file A references B, B references C, and C references A
- **THEN** the check reports the full cycle path: `A → B → C → A`

### Requirement: Self-references not treated as cycles
The system SHALL NOT flag a file referencing itself as a cycle. Self-references are reported separately as WARN.

#### Scenario: File referencing itself
- **WHEN** `references/writing-workflow.md` contains `](writing-workflow.md)`
- **THEN** the check reports it as a self-reference WARN, NOT as a cycle FAIL

### Requirement: Cycle detection scope
The system SHALL build the reference graph from all `.md` files under `skills/*/references/` and `references/shared/`. Files in `references/methodology/` are excluded because they are static knowledge with no outbound refs to skill files.

#### Scenario: Methodology files excluded
- **WHEN** a methodology file references only other methodology files
- **THEN** those references are NOT included in the cycle detection graph

### Requirement: Cycle reported as FAIL
The system SHALL report detected cycles as FAIL (not WARN), because cycles in the reference graph can cause infinite recursion during agent context loading.

#### Scenario: Detected cycle causes FAIL
- **WHEN** any cycle is detected in the reference graph
- **THEN** the check exits with FAIL status and lists all cycles found
