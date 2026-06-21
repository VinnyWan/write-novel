## ADDED Requirements

### Requirement: Stub pointer files resolve to shared references
The `write-novel-review` skill's reference stub files SHALL contain valid paths that resolve to the corresponding files in the global shared references directory.

#### Scenario: Anti-AI writing stub resolves
- **WHEN** the review skill loads `references/anti-ai-writing.md`
- **THEN** the stub file SHALL point to a resolvable path containing the anti-AI writing reference content

#### Scenario: All stub files resolve
- **WHEN** any of the 6 stub files (anti-ai-writing, banned-words, character-relations, dialogue-mastery, plot-core-methods, quality-checklist) is loaded
- **THEN** the pointer path SHALL resolve to the corresponding file in `write-novel/references/shared/`
