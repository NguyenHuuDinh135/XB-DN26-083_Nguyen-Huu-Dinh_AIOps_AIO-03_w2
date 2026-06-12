# Diagram Review — A1 Coverage Checklist

This file explains how `architecture-target.png` satisfies A1. It is a reviewer aid; the diagram remains the primary artifact.

| A1 requirement | Where it appears in the diagram | Evidence / interpretation |
|---|---|---|
| Metrics ingestion path | Services and infrastructure feed OpenTelemetry / Prometheus Agent, then VictoriaMetrics. | Replaces Datadog host-priced metrics while keeping PromQL-style query and alert semantics. |
| Logs ingestion path | Service logs flow through OTel/Filelog into Loki, ClickHouse, and S3 archive. | Shows hot operational logs, structured analytics, and cold retention as separate paths. |
| Traces ingestion path | Application instrumentation sends traces through OTel to Tempo. | Supports Grafana service graph and trace-to-log-to-metric triage. |
| Storage and retention tier | Loki is labeled hot ops, ClickHouse analytics/audit, S3 cold archive, OpenSearch incident metadata. | Separates high-cost hot search from lower-cost long-tail retention. |
| Alerting and correlation surface | Alertmanager / topology correlation is placed before PagerDuty. | Shows that raw alerts are grouped before reaching humans. |
| Human query surfaces | Grafana, PagerDuty, Statuspage, and OpenSearch incident index are visible as operator-facing surfaces. | Makes tool switching explicit instead of pretending there is only one UI. |
| SaaS / OSS / in-house boundary | The diagram groups and shades platform areas by ownership model. | PagerDuty/Grafana/Statuspage remain SaaS; storage/correlation are OSS/hybrid; policy and incident memory are team-owned. |
| Arrow semantics | The legend explains blue, pink, orange, green, and purple dashed arrows. | Prevents ambiguity between telemetry ingress, metrics, logs, alerts, and batch/cold retrieval paths. |

## Reviewer reading path

1. Start at the application services and follow blue arrows into the governed telemetry pipeline.
2. Follow pink/orange lanes to see where metrics and logs are stored and queried.
3. Follow trace/service graph flow into Grafana to understand the MTTR reduction mechanism.
4. Follow green arrows to see how alerts are correlated before PagerDuty.
5. Use the right-hand legend to distinguish SaaS, OSS/hybrid, and in-house responsibility.

## Known trade-off represented visually

The diagram intentionally does not collapse all observability into one box. On-call starts in Grafana, but PagerDuty remains the paging surface and S3/ClickHouse remain separate retrieval paths for audit and long-tail search. That is a conscious trade-off: lower cost and less SaaS lock-in without hiding operational complexity.
