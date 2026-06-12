# Submission — GeekShop Observability + AIOps Stack Redesign

**Student:** Nguyễn Hữu Định  
**Student ID:** XB-DN26-083  
**Course/Track:** AIOps  
**Group:** AIO-03  
**Week:** w2  

This package contains the required Week 2 AIOps lab submission artifacts. Start here, then read the artifacts in this order:

1. `target-observability-aiops-architecture.drawio` — target-state architecture and signal flow.
2. `cost-model.md` — why the plan reaches the required 40% spend reduction.
3. `components.md` — component decisions and six-month change risks.
4. `adr/` — the two hardest architecture decisions and their consequences.
5. `migration-plan.md` — eight-week migration with rollback and go/no-go gates.
6. `risks.md` — six highest risks, owners, and mitigations.
7. `FINDINGS.md` — required reflection plus the A7 POC validation plan.

The design keeps PagerDuty as the paging surface, moves ingestion to OpenTelemetry, tiers logs into hot searchable storage plus cold S3 archive, and uses service-graph-aware alert correlation before paging. The target bill is modeled at **$20,930/month**, a **50.2% reduction** from the current $42,000/month baseline, while preserving diagnostic speed through better tracing, correlation, and incident retrieval.
