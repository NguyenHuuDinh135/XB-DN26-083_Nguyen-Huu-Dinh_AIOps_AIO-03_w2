# Evidence Notes

Computed from `inputs/incidents_history.json`:

- Incident count: 29
- Median MTTD: 11 minutes
- Median MTTR: 26 minutes
- Top root-cause classes: [('slow_query', 3), ('connection_pool_exhaustion', 3), ('lock_contention', 1), ('eviction', 1), ('memory_leak', 1), ('tls_expiry', 1), ('rebalance_storm', 1), ('infinite_retry', 1)]
- Most frequently involved services: [('catalog-db', 6), ('payment-svc', 6), ('checkout-svc', 6), ('payments-db', 5), ('recommender-svc', 5), ('search-svc', 4), ('catalog-svc', 3), ('edge-lb', 3)]

This file is supplementary and not part of the required handout list.

## Internal source map

| Source | Evidence extracted | Used in |
|---|---|---|
| `inputs/current-stack.md` | Current bill **$42,000/month**; Splunk **$13,900/month** at ~52GB/day; Datadog APM **$11,800/month**; Datadog infra metrics **$5,400/month**; PagerDuty **$3,900/month**. | `cost-model.md`, ADR 001, ADR 002, migration gates. |
| `inputs/services.json` | 10 services, 4 backing stores, 17 edges. | Architecture diagram, migration blast-radius reasoning. |
| `inputs/pain_points.md` | Four-UI triage, 47 pages/90s, 1% trace sampling misses tail events, cardinality overage, slow 7-day log searches. | Component decisions, ADR 002, risk register. |
| `inputs/incidents_history.json` | Median MTTD **11 min**, median MTTR **26 min**, repeated payment/catalog/checkout and DB-related incidents. | POC plan, migration replay criteria, FINDINGS. |

## Public evidence checked on 2026-06-12

| Source | Evidence used |
|---|---|
| Datadog pricing list: <https://www.datadoghq.com/pricing/list/> | Infrastructure Pro published at **$15/host/month annual** and **$18/host/month on-demand**. |
| Datadog APM billing docs: <https://docs.datadoghq.com/account_management/billing/apm_tracing_profiler/> | APM Pro and Enterprise are billed per underlying APM host, supporting the host-priced APM replacement argument. |
| PagerDuty Incident Management pricing: <https://www.pagerduty.com/pricing/incident-management/> | PagerDuty is priced per user/plan, supporting seat-count reduction rather than replacement. |
| Grafana Cloud pricing: <https://grafana.com/pricing/> | Pro is paid usage-based from **$19/month + usage**; Enterprise has annual spend commitment. |
| OpenTelemetry Collector configuration: <https://opentelemetry.io/docs/collector/configuration/> | Collector pipeline structure supports receivers/processors/exporters. |
| OpenTelemetry processors: <https://opentelemetry.io/docs/collector/components/processor/> | Processors transform, filter, and enrich telemetry flowing through the pipeline. |
| VictoriaMetrics Prometheus integration: <https://docs.victoriametrics.com/victoriametrics/integrations/prometheus/> | Supports Prometheus `remote_write` ingestion into VictoriaMetrics. |
| Grafana Loki retention: <https://grafana.com/docs/loki/latest/operations/storage/retention/> | Retention is handled by the Compactor; object-store lifecycle must be compatible with retention. |
| Grafana Tempo service graph: <https://grafana.com/docs/tempo/latest/metrics-from-traces/service_graphs/service-graph-view/> | Service graph view is generated from trace-derived metrics for request rates, errors, and durations. |

## Diagram arrow legend

- Blue: telemetry ingress and governed OTel pipeline.
- Pink: metrics lane and host-priced metric replacement.
- Orange: log/audit/Grafana query paths.
- Green: alert and correlation paths.
- Purple dashed: batch, retrieval, cold search, and incident-memory paths.
