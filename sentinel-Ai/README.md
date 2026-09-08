# Sentinel — Phase 1 (Week 1) Deliverables

This covers the Week 1 targets from the roadmap: research attack patterns,
build a labeled test set of attack + benign prompts, and draft both domain
packs' synthetic documents.

## Contents

```
sentinel/
├── README.md
├── research/
│   └── attack_patterns.md        # taxonomy grounding (OWASP LLM Top 10 2025)
├── test_dataset/
│   └── labeled_prompts.csv        # 43 labeled prompts across 10 categories
└── domain_packs/
    ├── banking/
    │   ├── config.json
    │   └── documents/
    │       ├── account_policies.md
    │       ├── transaction_faqs.md
    │       └── reimbursement_rules.md
    └── enterprise_hr/
        ├── config.json
        └── documents/
            ├── hr_handbook.md
            ├── leave_policy.md
            └── expense_policy.md
```

## What each piece is for

- **`research/attack_patterns.md`** — grounds the test set in the OWASP Top 10
  for LLM Applications (2025), covering direct/indirect prompt injection,
  jailbreak technique families, PII/secret disclosure, and system-prompt
  leakage. Ends in a category table (`DPI`, `IPI`, `JB-ROLE`, `JB-HYPO`,
  `JB-ENC`, `JB-MULTI`, `SPL`, `PII-IN`, `PII-OUT`, `BENIGN`) that the CSV
  schema follows directly.

- **`test_dataset/labeled_prompts.csv`** — 43 rows, columns
  `id, category, domain, label, text, notes`. 28 attack prompts across 9
  attack categories, 15 benign prompts — including several benign prompts
  deliberately worded to *resemble* an attack pattern (e.g. "pretend I'm a
  new hire," "decode this base64") so the Security Agent's false-positive
  rate gets tested, not just its recall.

- **`domain_packs/banking/`** and **`domain_packs/enterprise_hr/`** — each has
  3 synthetic policy/FAQ documents and a `config.json` with display name,
  branding, sample queries, and a `sensitive_field_patterns` hint list the
  Output Validator can use alongside Presidio's baseline PII detectors. Both
  packs are intentionally parallel in structure (policies / FAQs-or-handbook /
  reimbursement-or-expense) so retrieval quality and security-layer behavior
  can be compared apples-to-apples across domains — this is what Week 6's
  "generalization proof" evaluation depends on.

## Notes / assumptions made

- All document content is synthetic (no real institution, company, or person
  represented) — safe to check into a public repo or resume portfolio.
- The CSV is intentionally small enough to hand-review row by row in Week 2
  while building the Security Agent; it's meant to grow (via the Red-Team
  Agent in Week 4) rather than be the final evaluation set.
- Indirect prompt injection (`IPI`) rows are written as content *snippets*
  that would be embedded inside a domain-pack document during testing, not as
  standalone chat messages — flag this distinction when wiring them into the
  Assistant Agent's retrieval test harness in Week 3.

## Next (Week 2)

Build the Security Agent: an embedding-similarity or lightweight classifier
detector trained/tuned against `labeled_prompts.csv`, wire in Presidio for
input-side PII/secret detection, and add risk scoring on top. The CSV's
`category` column doubles as the label set for a first classifier baseline.
