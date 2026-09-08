# Sentinel — Development & Engineering Rules

## Development lifecycle (every module follows this — never skip a phase)

```
Implement
      ↓
Architecture Review
      ↓
Critical Fixes Only
      ↓
Unit Testing
      ↓
Integration Testing
      ↓
Integration into Sentinel
      ↓
System Integration Testing
      ↓
Move to Next Module
```

- Never recommend or start work from a future phase.
- Never go back and redesign a completed phase without explicit instruction.

## Testing strategy (current, agreed — do not change without explicit request)

- Goal: use **real production components** in integration tests.
- Use: `OutputValidationAgentFactory`, `GeminiLLm Clinet`, real validators,
  real policy engine, real risk engine, real sanitizer.
- Avoid mocks unless an external dependency makes them unavoidable (e.g. a
  live third-party API in a CI environment without credentials).
- Always build dependencies through the module's factory in integration
  tests. Never manually construct a chain of dependencies by hand — that
  defeats the purpose of factory-based testing and can hide wiring bugs
  (see: the `EscalationPolicy` = `None` bug found in
  `HallucinationValidator`, which a hand-built test might not catch).

## Coding standards

Every generated or modified code artifact must:

- Follow SOLID principles.
- Use dependency injection (constructor injection preferred).
- Include type hints on all public functions/methods.
- Include docstrings on all public classes/functions.
- Match existing project style — don't introduce new patterns or libraries
  without discussion.
- Be production quality, not a prototype/sketch.
- Preserve existing public APIs unless a breaking change is explicitly
  approved.
- Avoid unnecessary refactoring — fix only what's in scope for the current
  task.

## Local environment & repo conventions

- **Git:** local repository is sufficient. Pushing to a remote (GitHub) is
  not required for day-to-day development and is a separate, later decision
  — not a prerequisite for using Copilot Agent mode or running tests.
- **Commit before every agent session** that will modify files, so changes
  can be reviewed via `git diff` and reverted via `git checkout -- .` /
  `git reset --hard` if needed.
- **`.gitignore` must exclude:** `__pycache__/`, `*.pyc`, `.venv/`, `.env`,
  `.pytest_cache/`, `test_chroma_db/`, `chroma_db/` (decide case-by-case if
  vector DB data should be versioned or regenerated via the ingestion
  pipeline), `*.zip`.
- **`pytest.ini` at repo root is required** — without it, `pytest` run
  directly (not via `python -m pytest`) will not find the `src` package,
  and duplicate test filenames across module folders (e.g. multiple
  `test_factory.py`) will collide during collection.
  ```ini
  [pytest]
  pythonpath = .
  addopts = --import-mode=importlib
  ```
- **Baseline before any agent session:** always run
  `pytest tests/ -v > baseline_test_results.txt 2>&1` and review it before
  opening Copilot Agent mode. Never let an agent discover collection errors
  itself first — this is a common cause of long unresponsive/hung agent
  runs.

## Working with GitHub Copilot Agent mode on this project

1. **Plan before code.** First prompt in a new task: ask the agent to read
   the relevant files and propose a plan (files it will touch, order of
   operations) without editing anything. Approve or correct the plan before
   letting it proceed.
2. **Reference real files explicitly** (`#file:path`) for anything the
   agent needs ground truth on — never let it infer constructors or
   behavior from memory or from prose descriptions.
3. **One module/phase per chat session.** Don't mix unrelated fixes in one
   session; start a fresh session per module or per bug.
4. **Small, scoped asks.** Prefer "fix this one failing test" over "fix
   everything and run the whole suite."
5. **Require diffs before applying changes**, especially under `src/`.
6. **If the agent hangs on a terminal command** ("Running command in
   terminal…" with no output for several minutes): click into the terminal
   and press Enter first (known completion-detection bug), then cancel and
   restart the step if it's still stuck rather than waiting indefinitely.
7. **Re-run the full test baseline after every accepted change**, and
   compare against the last known baseline in `docs/module_status.md`
   before considering a fix complete.

## Rules for how "proceed" is interpreted

When told to "proceed," continue the current agreed task only. Do not
reinterpret it as permission to redesign architecture, change testing
strategy, or jump to another module or phase.