## ADDED Requirements

### Requirement: Report template reference is resolvable
The `write-novel-import` skill SHALL be able to resolve the `references/shared/report-template.md` reference to load the shared report template.

#### Scenario: Report template loaded during import completion
- **WHEN** Phase 4 of write-novel-import generates the completion report
- **THEN** the reference `references/shared/report-template.md` SHALL resolve to a file containing the standardized 3-section report template
