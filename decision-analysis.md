# Decision Analysis — Alternatives and Rejected Paths

This file makes the trade-off analysis explicit. Scores are 1-5, where 5 is best for the criterion. The selected design is a hybrid: OpenTelemetry-controlled ingestion, OSS/hybrid storage for cost control, Grafana as the primary query surface, and PagerDuty retained for human paging.

## Decision matrix

| Capability | Option | Cost reduction | MTTR / RCA impact | Migration risk | Ops burden | Lock-in reduction | Decision |
|---|---|---:|---:|---:|---:|---:|---|
| Metrics | VictoriaMetrics + Prometheus Agent | 5 | 4 | 3 | 3 | 5 | **Selected.** Strong PromQL compatibility, better long-term retention/compression than plain Prometheus, and removes Datadog host pricing. |
| Metrics | Mimir | 4 | 4 | 3 | 2 | 5 | Rejected for v1 because it is operationally heavier than needed for 300 hosts and 10 services. |
| Metrics | Keep Datadog metrics | 1 | 4 | 5 | 5 | 1 | Rejected because host-priced metrics block the 40% cost target. |
| Metrics | New Relic / Dynatrace consolidation | 2 | 4 | 3 | 4 | 2 | Rejected because it likely shifts SaaS spend rather than solving host/log cost structure. |
| Logs | Loki + ClickHouse + S3 | 5 | 4 | 3 | 2 | 5 | **Selected.** Separates operational hot logs, structured analytics, and cold audit retention. |
| Logs | Negotiate Splunk discount only | 2 | 3 | 5 | 5 | 1 | Rejected because it does not fix lock-in, 7-day query pain, or renewal risk. |
| Logs | OpenSearch-only | 4 | 3 | 3 | 2 | 4 | Rejected because full-text indexing all logs at 52GB/day risks higher storage/query cost and heavier cluster operations. |
| Logs | Elastic Cloud | 2 | 4 | 4 | 4 | 2 | Rejected because it lowers migration risk but makes the 40% cost target less credible. |
| Logs | ClickHouse-only | 5 | 3 | 3 | 3 | 5 | Rejected because SQL analytics is strong, but on-call tail/search UX is weaker than Loki for operational logs. |
| Logs | S3-only cold archive | 5 | 1 | 4 | 4 | 5 | Rejected because it damages incident response and fails the no-capability-loss constraint. |
| Tracing | OpenTelemetry + Tempo | 5 | 4 | 3 | 3 | 5 | **Selected.** Grafana-native trace-to-metric/log workflow and removes Datadog APM host pricing. |
| Tracing | Jaeger | 5 | 3 | 3 | 3 | 5 | Rejected because Grafana/Tempo service graph integration is more direct for the target UI. |
| Tracing | Keep Datadog APM | 1 | 4 | 5 | 5 | 1 | Rejected because the $11,800/month APM host line is one of the largest cost levers. |
| Tracing | Honeycomb | 2 | 5 | 3 | 4 | 2 | Rejected for this lab because it improves high-cardinality debugging but keeps SaaS spend and vendor dependency. |
| Alerting / correlation | Alertmanager + topology grouping | 5 | 4 | 3 | 3 | 5 | **Selected.** Deterministic grouping before paging directly addresses alert storms. |
| Alerting / correlation | PagerDuty Event Orchestration only | 3 | 3 | 4 | 4 | 2 | Rejected because it improves routing but does not solve telemetry correlation upstream. |
| Alerting / correlation | Coroot full-stack RCA | 4 | 4 | 2 | 3 | 4 | Rejected as the core v1 dependency; useful as a POC/reference but too much behavior change at once. |
| Alerting / correlation | Custom LLM-first AIOps | 3 | 3 | 1 | 1 | 4 | Rejected because deterministic fingerprint/service-graph grouping is safer for first migration. |
| Paging | PagerDuty retained | 3 | 5 | 5 | 5 | 2 | **Selected.** Preserves schedules, escalation policy, and responder trust while reducing upstream noise. |
| Paging | Grafana OnCall | 5 | 3 | 2 | 3 | 5 | Rejected because replacing paging while also migrating telemetry increases blast radius. |
| Paging | Alertmanager-only paging | 5 | 2 | 2 | 2 | 5 | Rejected because it lacks the established incident-routing maturity the team already depends on. |
| Dashboard / SLO | Grafana Cloud primary UI | 3 | 5 | 4 | 4 | 4 | **Selected.** One starting point for metrics, logs, traces, SLOs, and incident links. |
| Dashboard / SLO | Self-host Grafana only | 5 | 4 | 3 | 2 | 5 | Rejected for v1 because operational burden increases while the observability backend is already changing. |
| Dashboard / SLO | Keep Datadog dashboards | 1 | 3 | 5 | 5 | 1 | Rejected because it keeps the team split across UIs and preserves Datadog query lock-in. |

## Strategy comparison

| Strategy | Why it was not chosen |
|---|---|
| Current vendor optimization | Too conservative: preserves fragmented UIs, host pricing, and Splunk renewal risk. |
| Pure SaaS consolidation | Operationally easy but unlikely to deliver a defensible 40% reduction at current host/log scale. |
| Pure OSS replacement | Strong cost and lock-in story, but paging and operational maturity risk become too high. |
| Hybrid OSS + retained paging | **Chosen** because it attacks the largest cost pools while preserving the most safety-critical human workflow. |
| Custom AIOps-first platform | Attractive later, but unsafe as the first dependency for alert suppression and root-cause claims. |

## Deep-dive rebuttals

### 1. Why not negotiate harder and stay on Splunk + Datadog?

This is the lowest migration-risk option, but it is structurally weak against the brief. The current bill is not caused by one bad contract line; it is caused by multiple expensive unit drivers at the same time: Datadog host-priced APM, Datadog host-priced infrastructure metrics, custom metric cardinality overage, and Splunk hot log search. A discount might reduce the bill temporarily, but the team would still keep four-UI triage, low trace sampling, alert storms, and Splunk renewal risk.

Best case, vendor negotiation is useful as a bridge during dual-run. It is not the target architecture because it does not independently explain how median root-cause time moves from 26 minutes to <=18.2 minutes.

### 2. Why not consolidate everything into one SaaS vendor?

A single SaaS vendor improves operational simplicity, support ownership, and migration speed. The weakness is cost credibility: moving Datadog + Splunk workloads into another all-in-one SaaS usually preserves the same expensive dimensions, especially indexed logs, host-based APM, and per-seat/user features. This may reduce cognitive load but is unlikely to cut at least 40% while retaining audit and incident-response capability.

The selected design keeps one SaaS where it matters most, PagerDuty for human paging, but moves high-volume telemetry storage to lower-cost controlled backends.

### 3. Why not go pure OSS and remove PagerDuty/Grafana Cloud too?

Pure OSS has the strongest lock-in and cost story on paper, but it creates a safety problem. Paging is a trust system, not just a notification tool: escalation policies, schedules, responder expectations, and incident history must work every time. Replacing PagerDuty while also replacing metrics, logs, tracing, and alert grouping would combine too many operational risks in the same eight-week plan.

Grafana Cloud is also intentionally retained as a managed UI surface so the team does not have to operate every layer of the observability stack during the migration. The design cuts the largest cost pools first, not every paid tool.

### 4. Why Loki + ClickHouse + S3 instead of one log backend?

One backend is simpler, but logs have conflicting access patterns. On-call engineers need fast recent operational search and tailing. Security/audit needs longer retention and reproducible retrieval. Analytics users may need structured SQL over high-cardinality fields. Splunk currently bundles those needs, but it is the largest cost line.

The selected split assigns each access pattern to the cheapest reasonable tier:

| Need | Selected tier | Why |
|---|---|---|
| Recent operational debugging | Loki hot tier | Good Grafana workflow and label-based incident search. |
| Structured analysis / audit queries | ClickHouse | Better for SQL analytics and high-cardinality structured fields. |
| Long-tail retention | S3 cold archive | Lowest-cost retention path for compliance evidence. |

OpenSearch-only and Elastic Cloud are rejected because indexing everything risks recreating the cost problem. S3-only is rejected because it loses incident response speed. ClickHouse-only is rejected because it is not the best operator-facing log tail/search UX.

### 5. Why not use Coroot or an LLM-first AIOps engine for RCA?

Coroot and LLM-assisted RCA are relevant, but they should not be the first production dependency for alert suppression. The current pain is alert storming and manual correlation; deterministic grouping by fingerprint, service graph, and historical alert behavior solves that with lower safety risk. LLMs can summarize incident context later, but they should not decide whether a critical page is suppressed until the team has replay evidence and service-owner sign-off.

The plan therefore uses deterministic correlation first, then keeps incident knowledge in OpenSearch so future AI/RCA features can retrieve structured incident history without being part of the first cut-over.

### 6. Why Tempo instead of Jaeger or keeping Datadog APM?

Keeping Datadog APM preserves capability but leaves the $11,800/month APM host line in place. Jaeger is viable, but the target human workflow is Grafana-first, and Tempo integrates directly with Grafana service graph and trace-to-log navigation. Since the brief requires faster root-cause analysis, the selected trace backend must make cross-signal navigation easy for on-call, not merely store spans.

Tempo is not chosen because it is universally better than Jaeger; it is chosen because it fits this design's UI and correlation strategy with lower cost than Datadog APM.

## What would change if constraints changed?

| Constraint change | Better alternative | Reason |
|---|---|---|
| Team has no OSS operations skill | Managed Grafana Cloud stack or Elastic Cloud | Reduces operational burden even if cost savings shrink. |
| Budget cut is 60% instead of 40% | More aggressive OSS/self-hosting and PagerDuty seat reduction | Current target $20,930 does not meet a $16,800 ceiling. |
| Audit requires Splunk-specific saved searches | Longer Splunk read-only phase or partial Splunk retention | Avoids audit regression while log tier proves equivalence. |
| Incident response maturity is weak | Keep PagerDuty and Datadog alerts longer | Safety beats cost until on-call can pass synthetic incident drills. |
| Log volume doubles before governance works | Reduce hot retention to 3 days and enforce structured log allowlist | Protects query p99 and budget before adding capacity. |

## Final decision

The selected stack is not the cheapest possible design. It is the best balance for the brief: cut spend by at least 40%, reduce median root-cause time by at least 30%, avoid observability blackout, and keep incident-response maturity.
