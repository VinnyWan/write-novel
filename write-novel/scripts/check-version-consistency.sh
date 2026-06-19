#!/bin/bash
# check-version-consistency.sh — 校验插件版本号三处一致
#   1. write-novel/.claude-plugin/plugin.json 的 version
#   2. .claude-plugin/marketplace.json 中 write-novel 条目的 version
#   3. CHANGELOG.md 顶部含对应 vX.Y.Z 小节
# 三者不一致即失败（非零退出）。

set -uo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
if [ -z "$REPO_ROOT" ]; then
  echo "Error: not in a git repository" >&2
  exit 2
fi

PLUGIN_ROOT=""
for cand in "$REPO_ROOT" "$REPO_ROOT/write-novel"; do
  if [ -d "$cand/skills" ] && [ -d "$cand/agents" ]; then
    PLUGIN_ROOT="$cand"
    break
  fi
done
if [ -z "$PLUGIN_ROOT" ]; then
  echo "Error: cannot locate plugin root (skills/ + agents/)" >&2
  exit 2
fi

PYBIN=""
for cand in python3 python py; do
  if command -v "$cand" >/dev/null 2>&1; then PYBIN="$(command -v "$cand")"; break; fi
done
if [ -z "$PYBIN" ]; then
  echo "Error: no python interpreter found" >&2
  exit 2
fi

"$PYBIN" - "$REPO_ROOT" "$PLUGIN_ROOT" <<'PYEOF'
import json, re, sys
from pathlib import Path

repo_root = Path(sys.argv[1])
plugin_root = Path(sys.argv[2])

errors = []

plugin_json = plugin_root / ".claude-plugin" / "plugin.json"
if not plugin_json.is_file():
    errors.append(f"missing {plugin_json}")
    plugin_version = None
else:
    try:
        plugin_version = json.loads(plugin_json.read_text(encoding="utf-8")).get("version")
    except json.JSONDecodeError as e:
        errors.append(f"invalid plugin.json: {e}")
        plugin_version = None

marketplace_json = repo_root / ".claude-plugin" / "marketplace.json"
market_version = None
if not marketplace_json.is_file():
    errors.append(f"missing {marketplace_json}")
else:
    try:
        mp = json.loads(marketplace_json.read_text(encoding="utf-8"))
        for plugin in mp.get("plugins", []):
            if plugin.get("name") == "write-novel":
                market_version = plugin.get("version")
                break
        if market_version is None:
            errors.append("marketplace.json has no write-novel plugin entry")
    except json.JSONDecodeError as e:
        errors.append(f"invalid marketplace.json: {e}")

changelog = repo_root / "CHANGELOG.md"
changelog_has_version = False
if not changelog.is_file():
    errors.append(f"missing {changelog}")
elif plugin_version:
    # match top-most "## vX.Y.Z" heading
    text = changelog.read_text(encoding="utf-8")
    m = re.search(r"^##\s+v?(\d+\.\d+\.\d+)", text, re.MULTILINE)
    if not m:
        errors.append("CHANGELOG.md has no '## vX.Y.Z' heading")
    else:
        changelog_top_version = m.group(1)
        if changelog_top_version != plugin_version:
            errors.append(
                f"CHANGELOG top version {changelog_top_version} != plugin.json version {plugin_version}"
            )
        else:
            changelog_has_version = True

# consistency: plugin.json == marketplace.json
if plugin_version and market_version and plugin_version != market_version:
    errors.append(
        f"version mismatch: plugin.json={plugin_version} vs marketplace.json={market_version}"
    )

if errors:
    print("[FAIL] version consistency:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print(f"[PASS] version consistency: plugin.json={plugin_version} marketplace.json={market_version} CHANGELOG=v{plugin_version}")
sys.exit(0)
PYEOF
