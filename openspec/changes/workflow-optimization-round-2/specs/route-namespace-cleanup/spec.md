## ADDED Requirements

### Requirement: SKILL.md routing table SHALL only contain actively-used namespace entries

The SKILL.md routing compatibility section SHALL be cleaned of all `webnovel-*` prefixed entries (5 total) and old-format `write-novel-*` duplicate entries (7 total). Active `write-novel-*` namespace entries and the `story` alias SHALL be preserved. A brief note SHALL be added indicating that v2.3 cleaned obsolete namespaces.

#### Scenario: webnovel-* entries removed
- **WHEN** a user or system reads SKILL.md
- **THEN** no entries with `webnovel-write`, `webnovel-plan`, `webnovel-query`, `webnovel-review`, `webnovel-init`, `webnovel-dashboard` appear in the route table

#### Scenario: Duplicate write-novel-* old-format entries removed
- **WHEN** a user or system reads SKILL.md
- **THEN** entries marked as "(旧长形式)" or "(旧触发词)" that duplicate the active namespace are removed

#### Scenario: Active entries preserved
- **WHEN** a user or system reads SKILL.md
- **THEN** all 13 active `write-novel-*` skill entries (setup, long-scan, short-scan, long-analyze, short-analyze, long-write, short-write, import, deslop, review, cover, query, doctor) remain in the routing table

#### Scenario: story alias preserved
- **WHEN** a user triggers `/story` or equivalent keywords
- **THEN** the routing dispatches to `write-novel` router skill correctly

### Requirement: Removed namespace entries SHALL be documented in CHANGELOG as breaking change

The removal of `webnovel-*` and old-format `write-novel-*` entries SHALL be recorded in CHANGELOG under the v2.3.0 entry as a breaking change note, listing the specific trigger words that are no longer supported.

#### Scenario: CHANGELOG records the breaking change
- **WHEN** CHANGELOG.md is read
- **THEN** the v2.3.0 entry includes a note about removed namespace backward compatibility with the list of affected trigger words
