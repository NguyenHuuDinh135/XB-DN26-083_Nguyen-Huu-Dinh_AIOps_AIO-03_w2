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

## Final decision

The selected stack is not the cheapest possible design. It is the best balance for the brief: cut spend by at least 40%, reduce median root-cause time by at least 30%, avoid observability blackout, and keep incident-response maturity.
