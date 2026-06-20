## ADDED Requirements

### Requirement: MANIFEST.yaml shared_sources SHALL reflect actual files in references/shared/

After the `cleanup-stale-references-and-check-gaps` change completes, MANIFEST.yaml's `shared_sources` list SHALL be updated to remove entries for files that no longer exist in `references/shared/`. The list SHALL only contain files that are actively present and consumed by at least one skill/agent/eval.

#### Scenario: Entries for deleted files removed
- **WHEN** MANIFEST.yaml is read after migration
- **THEN** `shared_sources` does not contain entries for the 4 deleted Chinese-named files (工作流总览, 脚本治理, 风险清单, 当前任务)

#### Scenario: Entries for archived files removed
- **WHEN** MANIFEST.yaml is read after migration
- **THEN** `shared_sources` does not contain entries for the 6 files moved to `references/archive/` (context-format, projection-spec, run-ledger-format, style-cache-schema, technique-tracker-schema, verification-checklist)

#### Scenario: Active shared_sources entries preserved
- **WHEN** MANIFEST.yaml is read after migration
- **THEN** `shared_sources` still contains entries for all actively-referenced files in `references/shared/` (anti-ai-writing, banned-words, quality-checklist, character-relations, hooks-suspense, hooks-chapter, format-and-structure, dialogue-mastery, genre-writing-formulas, genre-readers, genre-core-mechanics, genre-catalog, character-design-methods, character-basics, writing-craft, state-tracking, reversal-toolkit, plot-core-methods, opening-design, hooks-paragraph, emotional-methods, emotional-arc-design)

### Requirement: MANIFEST.yaml SHALL include an index of references/rules/ files

A new `rules_sources` section SHALL be added to MANIFEST.yaml that lists the files in `references/rules/` directory, including the 5 error-case samples (continuity-power-001, error-ai-slop-001, glossary-foreshadowing-001, hook-chapter-001, trope-face-slap-001) and the 4 story-format/consistency rule files.

#### Scenario: rules_sources section present
- **WHEN** MANIFEST.yaml is read
- **THEN** a `rules_sources` section exists listing all files in `references/rules/` with their purpose and origin

### Requirement: static-check SHALL pass after MANIFEST.yaml updates

After all MANIFEST.yaml changes are applied, running `bash write-novel/scripts/static-check.sh` SHALL produce zero failures and no new warnings.

#### Scenario: static-check passes
- **WHEN** `static-check.sh` is executed after MANIFEST updates
- **THEN** all checks pass with Fail=0
