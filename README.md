# Submission — GeekShop Observability + AIOps Stack Redesign

**Student:** Nguyễn Hữu Định  
**Student ID:** XB-DN26-083  
**Course/Track:** AIOps  
**Group:** AIO-03  
**Week:** w2  

This package contains the required Week 2 AIOps lab submission artifacts. Start here, then read the artifacts in this order:

1. `architecture-target.png` / `architecture-target.drawio` — target-state architecture and signal flow.
2. `cost-model.md` — why the plan reaches the required 40% spend reduction.
3. `components.md` — component decisions and six-month change risks.
4. `adr/` — the two hardest architecture decisions and their consequences.
5. `migration-plan.md` — eight-week migration with rollback and go/no-go gates.
6. `risks.md` — six highest risks, owners, and mitigations.
7. `FINDINGS.md` — required reflection plus the A7 POC validation plan.

Supporting material is organized separately:

- `diagrams/` — source/current-state diagrams and rendered PNG exports.
- `inputs/` — original lab input data used as evidence.
- `assets/icons/` — local vendor/tool icons used while designing diagrams; the submitted Draw.io files also embed the icons so they render without external paths.

The design keeps PagerDuty as the paging surface, moves ingestion to OpenTelemetry, tiers logs into hot searchable storage plus cold S3 archive, and uses service-graph-aware alert correlation before paging. The target bill is modeled at **$20,930/month**, a **50.2% reduction** from the current $42,000/month baseline, while preserving diagnostic speed through better tracing, correlation, and incident retrieval.

## Evidence basis

- Baseline spend comes from `inputs/current-stack.md`: total **$42,000/month**, including Splunk Cloud **$13,900/month**, Datadog APM **$11,800/month**, Datadog infrastructure metrics **$5,400/month**, and PagerDuty **$3,900/month**.
- Application topology comes from `inputs/services.json`: 10 application services, 4 backing stores, and 17 service edges.
- Incident claims come from `inputs/incidents_history.json`: 29 incidents, median MTTD **11 minutes**, median MTTR **26 minutes**, and repeated slow-query / connection-pool failure classes.
- Operational pain points come from `inputs/pain_points.md`, especially four-UI incident triage, 47-page alert cascades, 1% trace sampling gaps, cardinality overage, and slow 7-day log searches.
