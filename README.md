# Divination Casting Randomizer｜Legacy Compatibility / Archive Surface

> **Retired as a canonical development repository.**
>
> Canonical stochastic runtime authority and production development have moved to [`masini1491/ai-divination-playbook`](https://github.com/masini1491/ai-divination-playbook), path [`runtime/casting/`](https://github.com/masini1491/ai-divination-playbook/tree/main/runtime/casting).

This repository is retained for **historical provenance, rollback evidence, and compatibility only**. Do not implement new Randomizer features here.

## Current canonical source

```text
repository: masini1491/ai-divination-playbook
runtime:    runtime/casting/randomizer.py
API:        runtime/casting/api/cast.py
Web UI:     runtime/casting/index.html
```

Current canonical production endpoint:

```text
https://ai-divination-playbook-casting-masini1491-9205.vercel.app/api/cast
```

The former endpoint may remain available as a compatibility/historical deployment:

```text
https://tarot-plum-randomizer-masini1491-9205.vercel.app/api/cast
```

It is **not** the current production authority.

## Historical provenance

The last pre-retirement implementation baseline used for the monorepo migration is:

```text
legacy repository: masini1491/divination-casting-randomizer
source commit:     17cc4c84fd5c09b60de721b671c1d6511ab3d0e9
source tree:       f29bde4b6556fadd15ad69bd627f134a299cf94d
```

Historical records that reference this repository or its commits remain valid and must not be rewritten. Git history is intentionally preserved so old `runtime_source_commit` values remain resolvable.

The logical runtime identity also remains unchanged after relocation:

```text
source = divination-casting-randomizer-python
algorithm_version = 2
schema_version = 4
ai_schema_version = 1
```

The logical source name is an execution identity, not a claim that current implementation ownership remains in this repository.

## Supported historical contract

The migrated implementation supports:

- **Tarot** — 78-card deck, fresh full-deck shuffle per question identity, no duplicates within one reading, independent orientation.
- **Meihua** — independent A/B `000..999`, `A % 8` upper trigram, `B % 8` lower trigram, `(A+B) % 6` moving line with zero-remap rules.
- **Liuyao raw cast** — six bottom-to-top lines, three independent fair coins per line, yin=2 / yang=3, values 6/7/8/9, 6/9 changing.

Interpretation, Liuyao deterministic structured facts, reading lifecycle, routing, provenance governance, and current runtime acquisition are owned by `ai-divination-playbook`.

## Maintenance policy

```text
new feature / bug fix / contract change
→ modify masini1491/ai-divination-playbook
→ validate tests/casting/**
→ deploy from runtime/casting
```

This repository should receive no further feature development. A change here should only be made when necessary to preserve compatibility, historical provenance, or an explicitly authorized rollback.

## Preserved files

The original runtime, API, OpenAPI, Web UI, contract vectors, and tests remain in Git history and in this repository for auditability. The migration intentionally does not delete the repository or rewrite old commits.

For the migration contract and retirement evidence, see the canonical Playbook:

- `RANDOMIZER_INTEGRATION_MIGRATION.md`
- `RANDOMIZER_RETIREMENT_READINESS.md`
- `runtime/casting/MIGRATION_SOURCE.json`
