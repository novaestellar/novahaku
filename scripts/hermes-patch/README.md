# Hermes Patch

Selection-level guardrail patch for a **local** Hermes Agent install.

Disables prompt-injection scanning on the memory and cron entry points so that
user-curated content authored by this operator is not rejected by the platform
scanner. Everything else keeps its defences — see *Scope* below.

This is a **local-only** tool. It is never invoked by the novahaku loader, the
routing table, or any skill. Nothing in this repo calls it automatically.

## What it changes

Four files in the target Hermes tree. Twelve statement-level anchors.

- `tools/memory_tool_store.py` — 5 anchors
  memory write guard, load-time scan, and the `add()` / `replace()` / `batch()`
  call sites
- `cron/scheduler_prompt.py` — 3 anchors
  scan dispatch for the assembled prompt and the raw user prompt
- `tools/cronjob_tools.py` — 3 anchors
  prompt scanning on create / update / bulk-create
- `gateway/platforms/api_server.py` — 1 anchor
  cron scanning via the API server entry point

Each replaced statement is rewritten to a no-op carrying a `# [novahaku-patch]`
marker, so patch state is greppable and idempotent.

## Scope — what stays defended

The patch is deliberately narrow. It does **not** touch:

- `tools/skills_guard.py` — the install guard, including its unoverridable
  `hard_block`. Flattening this was explicitly rejected.
- `agent/prompt_builder.py` — context-file scanning, which keeps its own
  supported switch `HERMES_CONTEXT_SKIP_SCAN=1`
- `agent/tool_dispatch_helpers.py` — tool-result scanning
- `tools/threat_patterns.py` — the pattern definitions themselves, so any other
  caller still gets real patterns

If the only goal is to stop context-file scanning from blocking security skills,
use `HERMES_CONTEXT_SKIP_SCAN=1` instead — no source edits, no restart of
patched code, no blast radius on memory or cron.

## Usage

```bash
export HERMES_AGENT_HOME=/path/to/hermes-agent/app   # dir containing tools/

python hermes_patch.py --root "$HERMES_AGENT_HOME" --check
python hermes_patch.py --root "$HERMES_AGENT_HOME" --apply
python hermes_patch.py --root "$HERMES_AGENT_HOME" --verify
python hermes_patch.py --root "$HERMES_AGENT_HOME" --restore
```

`--root` is authoritative: an invalid path aborts with exit 2 rather than
falling back to a different install. Without `--root` the tree is auto-resolved
from `HERMES_HOME`, `~/.hermes/hermes-agent`, and `%LOCALAPPDATA%`.

`--apply` backs up first, then runs `--verify` automatically and rolls back if
verification fails. `--no-verify` skips that (not recommended).

Exit codes: `0` success, `1` failure or unhealthy tree, `2` root not resolved.

## Safety properties

- **Fail-closed on drift.** Every anchor is validated across every target
  *before* any file is written. A single missing anchor aborts the whole run
  with zero files written.
- **Idempotent.** Re-running `--apply` on a patched tree writes nothing and
  exits 0.
- **Reversible.** A sha256 manifest is written before the first modification.
  `--restore` verifies every backup exists *and hashes correctly* before
  overwriting anything, so a missing backup cannot produce a half-restored tree.
- **Self-preserving.** `--restore` copies the current (patched) files to a
  `pre-restore-<timestamp>/` directory first, so a restore over drifted source
  is itself reversible.
- **Static verification.** `--verify` is AST-based and import-free, so it works
  against a bare source copy with no runtime dependencies. It detects any live
  call to a defused scanner, including call sites the patch does not own.
- **No machine paths.** `--root` is the only input; nothing is hardcoded.

## Operational warnings

1. Scope is **platform-wide**. After a gateway restart every session on this
   machine runs with memory and cron scanning defused.
2. Cron jobs run unattended. An exfiltration pattern in a cron prompt
   (`curl -H "Authorization: Bearer ..." https://...`) is accepted with the
   patch applied, and there is no user turn in which to notice it.
3. Memory enters the system prompt. A poisoned entry persists across sessions
   and is invisible in the transcript.
4. An upstream Hermes upgrade overwrites the patched files. The manifest's
   `source_fingerprint` warns when the tree no longer matches the revision the
   anchors were authored against — but re-verify after every upgrade regardless.

## Rollback

Restore your own snapshot first — the tool's backup directory is a single point
of failure. Then, if you want the tool to agree:

```bash
python hermes_patch.py --root "$HERMES_AGENT_HOME" --restore
git -C "$HERMES_AGENT_HOME" diff --stat      # expect empty; this is the load-bearing check
grep -rn "novahaku-patch" <the 4 files>      # expect zero hits
python hermes_patch.py --root "$HERMES_AGENT_HOME" --check   # expect 0 of 4 patched
```

`--restore` reporting success is **not** proof the tree matches upstream. The
`git diff --stat` is.

## Tests

`test-hermes-patch.sh` exercises the full cycle on a disposable copy: check,
apply, verify, idempotency, restore, byte-identity, anchor drift, missing
backup, and invalid root. It never touches a live install.

```bash
bash test-hermes-patch.sh /path/to/hermes-agent/app
```
