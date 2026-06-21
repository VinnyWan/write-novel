## MODIFIED Requirements

### Requirement: Router table includes unified scan and analyze

The write-novel router SHALL route scan requests to the unified `write-novel-scan` skill and analyze requests to the unified `write-novel-analyze` skill. The router SHALL maintain backward-compatible routing for old skill names.

#### Scenario: Long scan routing

- **WHEN** user input matches long-form scan keywords (长篇排行, 起点/番茄/晋江, 扫榜, 什么火)
- **THEN** the router invokes `Skill("write-novel-scan")` and the unified skill auto-detects scope=long

#### Scenario: Short scan routing

- **WHEN** user input matches short-form scan keywords (短篇排行, 知乎盐言排行)
- **THEN** the router invokes `Skill("write-novel-scan")` and the unified skill auto-detects scope=short

#### Scenario: Long analyze routing

- **WHEN** user input matches long-form analyze keywords (拆文, 分析这本书, 黄金三章)
- **THEN** the router invokes `Skill("write-novel-analyze")` and the unified skill probes word count for scope detection

#### Scenario: Short analyze routing

- **WHEN** user input matches short-form analyze keywords (拆短篇, 分析这个故事, 番茄短篇拆文)
- **THEN** the router invokes `Skill("write-novel-analyze")` with user intent signaling scope=short

#### Scenario: Topic decision routing

- **WHEN** user input matches topic decision keywords (写什么能爆, 帮我选题, 选题方向)
- **THEN** the router invokes `Skill("write-novel-scan")` (scan Phase 4 produces 选题决策)

### Requirement: Router lists updated skill inventory

The router's deployed skill list SHALL reflect the merged skill structure, listing `write-novel-scan` and `write-novel-analyze` instead of the separate long/short variants.

#### Scenario: Skill list display

- **WHEN** the router displays available skills
- **THEN** the list includes `write-novel-scan` (扫榜分析) and `write-novel-analyze` (拆文分析) without separate long/short entries

## REMOVED Requirements

### Requirement: Router routes to write-novel-long-scan directly

**Reason**: write-novel-long-scan merged into write-novel-scan
**Migration**: Route to `write-novel-scan` instead; old `/write-novel-long-scan` trigger preserved as alias

### Requirement: Router routes to write-novel-short-scan directly

**Reason**: write-novel-short-scan merged into write-novel-scan
**Migration**: Route to `write-novel-scan` instead; old `/write-novel-short-scan` trigger preserved as alias

### Requirement: Router routes to write-novel-long-analyze directly

**Reason**: write-novel-long-analyze merged into write-novel-analyze
**Migration**: Route to `write-novel-analyze` instead; old `/write-novel-long-analyze` trigger preserved as alias

### Requirement: Router routes to write-novel-short-analyze directly

**Reason**: write-novel-short-analyze merged into write-novel-analyze
**Migration**: Route to `write-novel-analyze` instead; old `/write-novel-short-analyze` trigger preserved as alias
