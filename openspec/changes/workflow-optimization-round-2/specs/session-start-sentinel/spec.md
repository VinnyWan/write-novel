## ADDED Requirements

### Requirement: SessionStart hook SHALL detect deployment by hooks file presence

The SessionStart hook SHALL verify deployment state by checking for the existence of required hook files in the project's `.claude/hooks/` directory, rather than relying on a sentinel file (`.story-deployed`) that may not exist even when hooks are correctly installed by the plugin system.

#### Scenario: All hooks files present
- **WHEN** SessionStart executes and all required hook files exist in `.claude/hooks/`
- **THEN** no deployment warning is emitted and the hook proceeds to normal status display (branch, outline buffer, foreshadowing, etc.)

#### Scenario: One or more hook files missing
- **WHEN** SessionStart executes and one or more required hook files are absent from `.claude/hooks/`
- **THEN** a warning message SHALL be emitted listing the missing hooks and instructing the user to run `/write-novel-setup`

#### Scenario: Plugin hooks directory is used instead of project hooks
- **WHEN** hooks are installed via Claude Code plugin mechanism (CLAUDE_PLUGIN_ROOT) but not in the project's `.claude/hooks/` directory
- **THEN** the hook SHALL detect this as deployed (hooks are available via plugin) and SHALL NOT emit a false warning

### Requirement: Deployment check SHALL use the same file list as the sentinel-self-check

The files checked for deployment SHALL be identical to the list used in the existing sentinel-self-check block (lines 22-25 of session_start.sh): session-start.sh, session-end.sh, detect-story-gaps.sh, pre-compact.sh, post-compact.sh, validate-story-commit.sh, lib/common.sh, lib/sentinel.sh. This ensures no regression in what constitutes a "deployed" state.

#### Scenario: Same file list used
- **WHEN** the deployment check runs
- **THEN** it checks the exact same 8 files currently listed in the sentinel-self-check block
