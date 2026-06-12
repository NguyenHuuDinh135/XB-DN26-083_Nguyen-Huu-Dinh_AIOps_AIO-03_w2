# Submission — GeekShop Observability + AIOps Stack Redesign

**Student:** Nguyễn Hữu Định  
**Student ID:** XB-DN26-083  
**Course/Track:** AIOps  
**Group:** AIO-03  
**Week:** w2  

This package contains the required Week 2 AIOps lab submission artifacts. Start here, then read the artifacts in this order:

1. `architecture-target.png` / `architecture-target.drawio` — target-state architecture and signal flow.
2. `diagram-review.md` — explicit A1 coverage checklist for the diagram.
3. `components.md` — component decisions and six-month change risks.
4. `decision-analysis.md` — alternatives considered across SaaS, OSS, hybrid, and custom AIOps paths, including deep-dive rebuttals.
5. `cost-model.md` — why the plan reaches the required 40% spend reduction.
6. `adr/` — the two hardest architecture decisions and their consequences.
7. `migration-plan.md` — eight-week migration with rollback and go/no-go gates.
8. `risks.md` — six highest risks, owners, and mitigations.
9. `FINDINGS.md` — required reflection plus the A7 POC validation plan.
10. `optional-bonus.md` — optional capacity, vendor exit, skills-gap, and DR analysis.

Supporting material is organized separately:

- `diagrams/` — source/current-state diagrams and rendered PNG exports.
- `inputs/` — original lab input data used as evidence.
- `assets/icons/` — local vendor/tool icons used while designing diagrams; the submitted Draw.io files also embed the icons so they render without external paths.

The design keeps PagerDuty as the paging surface, moves ingestion to OpenTelemetry, tiers logs into hot searchable storage plus cold S3 archive, and uses service-graph-aware alert correlation before paging. The target bill is modeled at **$20,930/month**, a **50.2% reduction** from the current $42,000/month baseline. Median MTTR must move from **26 minutes** to **≤18.2 minutes** to satisfy the 30% root-cause-time reduction requirement; the migration gates therefore validate synthetic incident triage, service-graph completeness, trace sampling, and top log-query latency before any SaaS reduction.

## Evidence basis

- Baseline spend comes from `inputs/current-stack.md`: total **$42,000/month**, including Splunk Cloud **$13,900/month**, Datadog APM **$11,800/month**, Datadog infrastructure metrics **$5,400/month**, and PagerDuty **$3,900/month**.
- Application topology comes from `inputs/services.json`: 10 application services, 4 backing stores, and 17 service edges.
- Incident claims come from `inputs/incidents_history.json`: 29 incidents, median MTTD **11 minutes**, median MTTR **26 minutes**, and repeated slow-query / connection-pool failure classes.
- Operational pain points come from `inputs/pain_points.md`, especially four-UI incident triage, 47-page alert cascades, 1% trace sampling gaps, cardinality overage, and slow 7-day log searches.

## Rubric checklist

| Rubric item | Artifact | Status |
|---|---|---|
| A1 architecture diagram | `architecture-target.png`, `architecture-target.drawio`, `diagram-review.md` | Complete + evidence: signal paths, retention tiers, alert/correlation surface, human query surfaces, SaaS/OSS/in-house boundaries, and arrow semantics are mapped. |
| A2 component decisions | `components.md`, `decision-analysis.md` | Complete + alternatives: every capability has a selected component, six-month reversal cost, rejected options across SaaS/OSS/hybrid choices, and deep-dive rebuttals for likely reviewer questions. |
| A3 cost model | `cost-model.md` | Complete + spot-check support: target is **$20,930/month**, **50.2%** below baseline, with unit drivers, public pricing evidence, and 2x-growth sensitivity. |
| A4 ADRs | `adr/adr-001-tiered-log-storage.md`, `adr/adr-002-otel-correlation-pagerduty.md` | Complete + strong alternatives: both ADRs cover hard choices, 5+ alternatives, consequences, and validation gates. |
| A5 migration plan | `migration-plan.md` | Complete + evidence artifacts: eight weeks, rollback per cut-over, no-blackout guarantee, go/no-go gates, and reviewable gate artifacts. |
| A6 risk register | `risks.md` | Complete + leading indicators: six risks with likelihood, impact, mitigation, owner, trigger thresholds, and actions. |
| A7 POC plan | `FINDINGS.md` | Complete + consistent cost target: uncertain component, first assumption, measurements, pass/fail threshold, and $4,500 log-platform budget. |
| Reflection | `FINDINGS.md` | Complete: all five questions reference concrete numbers, design choices, and real-world patterns. |
| Optional bonus | `optional-bonus.md` | Added + mapped: capacity model, vendor exit clauses, skills-gap plan, and DR posture. |
