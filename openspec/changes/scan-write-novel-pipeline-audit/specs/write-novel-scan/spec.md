## ADDED Requirements

### Requirement: Scripts directory exists for scan skill
The `write-novel-scan` skill SHALL include a `scripts/` directory containing all scraper scripts referenced in SKILL.md Phase 1.5.

#### Scenario: All referenced scripts present
- **WHEN** the scan skill's Phase 1.5 references `scripts/qidian-rank-scraper.js`
- **THEN** the file SHALL exist at `write-novel/skills/write-novel-scan/scripts/qidian-rank-scraper.js`

#### Scenario: CDP utility script present
- **WHEN** any scraper script requires CDP utilities
- **THEN** the file `cdp-utils.js` SHALL exist in the scan skill's `scripts/` directory

#### Scenario: All platform scrapers present
- **WHEN** all platform entries in the Phase 1.5 data source table are checked
- **THEN** each referenced scraper script SHALL exist: `fanqie-rank-scraper.js`, `qimao-rank-scraper.js`, `jjwxc-rank-scraper.js`, `ciweimao-rank-scraper.js`, `heiyan-booklist-scraper.js`, `dz-browse-scraper.js`
