# cmstack-django — HANDOFF

_Last refresh: 2026-06-24. Read with [`REFACTOR_PLAN.md`](REFACTOR_PLAN.md),
[`../FEATURE_MATRIX.md`](../FEATURE_MATRIX.md), [`../DESIGN_SYSTEM.md`](../DESIGN_SYSTEM.md)._

## Current state (verified, not asserted)
- Full test suite: **250 passed** (`.venv/bin/python -m pytest -q`). Was 218 at start.
- Lint: `.venv/bin/ruff check apps` → clean.
- Coverage: **95%** overall (`pytest --cov=apps`). pytest-cov + factory_boy installed and
  wired (`pyproject.toml [tool.coverage.*]`, `requirements/dev.txt`).
- Run app: `docker compose up` (or venv + `manage.py runserver`). Tests: `.venv/bin/python -m
  pytest`. Use `.venv/bin/python` directly — `source .venv/bin/activate` did not expose django
  in this shell, but `.venv/bin/python` works.

## DONE — Architecture (Task 2), per the two hard rules the user added mid-session
Two non-negotiable rules now govern (see REFACTOR_PLAN §0 + §0a):
1. **Views = HTTP boundary only.** Zero business logic, zero ORM in any `apps/*/views.py`.
2. **Services never touch the ORM** — only via a **repository** layer; side effects via signals.

Layering enforced everywhere: `view → service → repository → manager/QuerySet → model`.
- New `services.py` in: content, comments, core, media, seo, dashboard (+ existing search).
- New `repositories.py` in: content, comments, core, media, seo, search, accounts.
- Logic extractions (all tested): `Post.objects.editable_by(user)` (QuerySet),
  `Post.gate_publish_state(user)`, `Comment.approve()/mark_spam()` (model methods — entity
  behavior, intentionally kept), `comments.services.submit_comment` (returns an outcome enum:
  CREATED/INVALID/DISABLED/LOGIN_REQUIRED — owns ALL comment gating so the view only maps
  outcome→HTTP), `comments.services.moderate`, `dashboard.services.dashboard_stats`.
- Verification greps (both empty): ORM in `apps/*/views.py`; raw `Model.objects`/
  `get_object_or_404` in `apps/*/services.py`.
- Also done: **F1** search now includes Services; **F2** coverage tooling.

## Decisions / rejected (so they're not relitigated)
- `model = X` on Create/Update/Delete generic views is KEPT — it's declarative config, not an
  ORM call; the grep treats it as clean. List views' `queryset=`/`get_queryset` ORM was moved
  to services.
- Model methods (`approve`/`mark_spam`/`gate_publish_state`/`save()` invariants) are legit
  entity behavior, NOT "raw ORM in a service" — services call them. Repositories own queries +
  create-from-form + delete + counts.
- Services currently fire NO inline side effects (sanitize/cache/revisions already live in
  `model.save()` / existing signals), so the observer half of rule 2 is satisfied today. The
  signal→receiver pattern is to be introduced with the FIRST real effect = **F5 comment-
  notification email** (build: `submit_comment` emits a `comment_created` Django signal; a
  receiver in `apps/comments/signals.py` sends mail; test with locmem backend).

## PENDING (ordered) — resume here
1. **Adversarial verification (REQUIRED by prompt §21).** Subagent dispatch was failing with
   API 529 (overloaded) this session — retry. Dispatch 2–3 independent Opus skeptics per
   refactored module (lenses: behavior-preservation / security / N+1). Add a regression test
   for anything they break. Specifically have them probe: comment gating outcome mapping,
   `editable_by` permission scoping, parler translation saving through the thinned form_valid,
   N+1 on dashboard lists (`assertNumQueries`).
2. **Coverage gaps to close:** `apps/content/services.py` 84% (page/service visibility Http404
   branches, lines ~63-66/71 — add 2 tests); `apps/search/repositories.py` 70% (Postgres FTS
   branch — needs a Postgres CI job, §F13/F14). Target ≥80% services/managers (met except
   search-repo Postgres path), 100% critical paths.
3. **Task 3 — UI convergence (largest remaining).** See REFACTOR_PLAN §3. Order: U1 tokens
   (3 vars → ~20 semantic + `.dark`), U2 fonts (Space Grotesk/Geist → **Newsreader + Inter +
   Geist Mono**, preload/subset), U3 public shell, U4 admin shell, U5 missing components, U6
   a11y, U7 Lighthouse ≥95 (measure for real). Files: `frontend/{tailwind.config.js,src/
   styles.css,src/main.js,package.json}`, `templates/*`, `apps/*/templates/*`.
4. **Task 1 — feature parity (REFACTOR_PLAN §2).** Build through the new layers (view→service→
   repository; effects→signal). Suggested order: F5 comment email (also demos observer), F3
   RSS, F4 contact, F6 soft-delete+likes, F7 revision-restore UI, F8 scheduled publish, F9
   menus, F10 authors/profile, F11 media picker+storage driver, F12 REST API + MCP (largest),
   F13 CI, F14 E2E, F15 mypy django plugin.
5. **Task 5 — rewrite README** after the above; align with the other two stacks.
6. **Completeness-critic** Opus pass before declaring done (prompt §"production quality bar").

## Gotchas
- parler: query translated fields via `.language(code)`/`translations__field`, never
  `filter(title=...)`. Root `conftest.py` resets active language per test.
- Tests run on SQLite → only the search `icontains` fallback is exercised; the Postgres
  `SearchVector` path in `search/repositories.py` is untested without a Postgres CI job.
- Frontend changes need `docker compose up -d --build --renew-anon-volumes` (stale dist
  volume), or run Vite locally.
- Do NOT edit `../FEATURE_MATRIX.md` / `../DESIGN_SYSTEM.md` (parallel sessions depend on them).
  No matrix discrepancies found so far (REFACTOR_PLAN §7).

---

## Ready-to-paste continuation prompt (new window)
> You are a senior Django engineer continuing the autonomous `cmstack-django` refactor. Read
> `cmstack-django/HANDOFF.md`, `cmstack-django/REFACTOR_PLAN.md`, `../FEATURE_MATRIX.md` and
> `../DESIGN_SYSTEM.md` first (specs are read-only canon — do not edit them). Operating rules:
> work autonomously inside `cmstack-django/` (no permission for read/edit/test/manage.py/git);
> respond to me in **Russian**, keep all code/comments/docs in English; use the Superpowers
> framework (writing-plans / TDD / subagent-driven-development / requesting-code-review /
> verification-before-completion) and follow rigid skills exactly. Two NON-NEGOTIABLE
> architecture rules are already in force and MUST be preserved: (1) views hold zero business
> logic and zero ORM (HTTP boundary only); (2) services never touch the ORM directly — only via
> the `repositories.py` layer — and side effects go through Django signals/observers. Layering:
> view → service → repository → manager → model. The architecture refactor is DONE and verified
> (250 tests pass, ruff clean, 95% coverage, zero ORM in views/services per grep). **Resume from
> the first PENDING item in HANDOFF.md**: (1) adversarial verification of the refactor (retry
> subagents — they were 529-throttled), then (2) close the two coverage gaps, then (3) Task 3 UI
> convergence starting with U1 tokens + U2 fonts. Use `.venv/bin/python -m pytest` (not `source
> activate`). Show real test/coverage output; never claim passing without the run.
