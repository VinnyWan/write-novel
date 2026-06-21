## ADDED Requirements

### Requirement: Unified scan entry point

The system SHALL provide a single `write-novel-scan` skill that accepts both long-form and short-form market scanning requests. The skill MUST automatically detect the scope (long/short) based on the target platform specified by the user, or ask the user when the scope is ambiguous.

#### Scenario: Long-form scan via platform keyword

- **WHEN** user invokes scan with keywords matching long-form platforms (起点, 晋江, 七猫, 刺猬猫, 番茄长篇)
- **THEN** the system routes to the long-form scan pipeline (Phase 1-4: platform confirmation, data collection, analysis, topic decision)

#### Scenario: Short-form scan via platform keyword

- **WHEN** user invokes scan with keywords matching short-form platforms (知乎盐言, 黑岩短篇, 点众短篇)
- **THEN** the system routes to the short-form scan pipeline (Phase 1-4: platform confirmation, data collection, emotion analysis, topic matching)

#### Scenario: Ambiguous scope

- **WHEN** user invokes scan without specifying a platform (e.g., "扫榜", "什么火")
- **THEN** the system SHALL ask "看长篇还是短篇市场?" before proceeding

### Requirement: Backward compatibility aliases for scan

The system SHALL preserve `/write-novel-long-scan` and `/write-novel-short-scan` as aliases that delegate to the unified `write-novel-scan` skill with the appropriate scope preset.

#### Scenario: Old long-scan command

- **WHEN** user invokes `/write-novel-long-scan`
- **THEN** the system routes to `write-novel-scan` with `scope=long`

#### Scenario: Old short-scan command

- **WHEN** user invokes `/write-novel-short-scan`
- **THEN** the system routes to `write-novel-scan` with `scope=short`

### Requirement: Scan data collection and analysis

The system SHALL support both script-based data collection (priority 1) and user-provided data (priority 2) for all supported platforms, producing structured analysis reports with platform-appropriate metrics.

#### Scenario: Script-based collection for Qidian

- **WHEN** user selects 起点 as the platform
- **THEN** the system runs `scripts/qidian-rank-scraper.js` and analyzes subscription/ticket/trend data

#### Scenario: Script-based collection for Zhihu

- **WHEN** user selects 知乎盐言 as the platform
- **THEN** the system uses browser-cdp to collect story rankings and analyzes emotion distribution and viral patterns

### Requirement: Merged collection and trend analysis

The system SHALL execute data collection and trend analysis in a single execution context by default (merged mode), only falling back to a two-phase mode (collect then analyze) when the collected data volume exceeds context capacity.

#### Scenario: Normal merged execution

- **WHEN** collection produces data within context budget
- **THEN** analysis runs in the same context immediately after collection, without intermediate serialization

#### Scenario: Overflow fallback

- **WHEN** multi-platform collection produces data beyond context threshold
- **THEN** the system falls back to two-phase mode: write raw data to disk, then read back for analysis
