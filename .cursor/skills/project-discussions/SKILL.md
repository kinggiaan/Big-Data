---
name: project-discussions
description: >-
  Log important discussions, insights, debugging findings, and design decisions
  into docs/discussions.md for future report writing. Use when the user discusses
  search quality, debugging results, design trade-offs, benchmark analysis,
  or any technical insight worth preserving for the final report.
---

# Project Discussions Logger

## When to Trigger

Append a new discussion entry to `docs/discussions.md` when ANY of these occur:

1. **Bug found & fixed** — document root cause, fix, and lesson learned
2. **Search quality analysis** — compare modes, explain why results are good/bad
3. **Benchmark/evaluation results** — record numbers with interpretation
4. **Design decision** — why we chose approach A over B (e.g., manual RRF vs native)
5. **Data insight** — distribution issues, quality problems, scaling observations
6. **User frustration explained** — when something "doesn't work as expected" and we find out why

## How to Log

1. Read `docs/discussions.md` to find the last discussion number
2. Append a new section using the template below
3. Always include a **"Takeaway cho report"** section — this is the key value

## Entry Template

```markdown
---

## Discussion #N: [Concise title]

**Ngày:** DD/MM/YYYY
**Context:** [1-2 sentences: what happened, what the user observed]

**Root cause / Analysis:**
[Technical explanation with code snippets if relevant]

**Solution / Finding:**
[What was done or discovered]

**Takeaway cho report:**
- [Bullet points: what to include in the final report]
- [Why this matters for a Big Data course]
- [Comparison, trade-off, or insight worth highlighting]
```

## Quality Guidelines

- Write in a mix of Vietnamese + English (technical terms in English)
- Include actual numbers, metrics, code snippets — not vague descriptions
- Each entry should be self-contained (readable without context)
- "Takeaway cho report" must connect the finding to Big Data / IR concepts
- Keep entries concise: 30-60 lines each
