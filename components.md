# A2 — Component Decision Table

Current pain points are not basic observability gaps; the team already has decent per-service dashboards and alert fidelity. The redesign targets cost, correlation, cognitive load, and migration safety.

## Evidence basis

- `inputs/current-stack.md`: observability spend is concentrated in Splunk Cloud (**$13,900/month**) plus Datadog APM/metrics host-priced lines (**$17,200/month** combined).
- `inputs/pain_points.md`: the current incident workflow requires multiple vendor UIs, produces alert cascades, and suffers from low trace sampling and slow 7-day log searches.
- `inputs/incidents_history.json`: incident history repeatedly involves payment, checkout, catalog, and database paths, so the design optimizes trace-to-log-to-metric navigation rather than only dashboard polish.
- Public docs support the primitives used: OpenTelemetry Collector pipelines are built from receivers/processors/exporters; VictoriaMetrics accepts Prometheus `remote_write`; Loki retention is handled by the Compactor; Tempo service graphs are generated from trace-derived metrics.

| Capability | Chosen component / vendor | Why this one? | What gets worse if we change our mind in six months? |
|---|---|---|---|
| Metrics ingestion + storage + query | OpenTelemetry Collector → Prometheus Agent remote-write → VictoriaMetrics | Replaces Datadog host-priced metrics with an OSS/hybrid store while keeping PromQL-compatible dashboards and alert rules. VictoriaMetrics chosen over vanilla Prometheus for better compression (40%+ vs Prometheus), higher cardinality tolerance, and enterprise-grade long-term retention. | Query/rule semantics, retention tuning, and capacity assumptions must be revisited; teams may need to rewrite PromQL and SLO panels again. |
| Logs ingestion + storage + search | Loki (operational hot logs, 7d) + ClickHouse (structured analytics/audit queries) + Amazon S3 cold archive (1yr) | Logs are the largest cost pool; structured hot retention plus cheap cold archive attacks the $13.9k Splunk line without deleting audit capability. Loki serves day-to-day operational queries with label-based LogQL; ClickHouse handles high-cardinality structured analytics and audit queries that need SQL. | Long-tail ad-hoc search and compliance workflows get worse first; security/audit users may lose Splunk UX and saved-search behavior. Dual query dialect (LogQL + SQL) adds cognitive load. |
| Distributed tracing | OpenTelemetry instrumentation + Tempo (Grafana-native) | Tempo chosen because Grafana is the primary UI, giving native trace-to-metrics-to-logs correlation in one surface. The brief requires 30% faster root-cause; stronger trace coverage and tail/adaptive sampling preserve diagnostic value while removing Datadog APM host pricing. | Sampling policy and instrumentation become team-owned; bad sampling could hide the exact low-frequency tail events we are trying to expose. |
| Alerting + correlation / grouping | Alertmanager + Robusta-style topology correlation | Directly addresses PagerDuty clusters and the 8-minute manual “first hypothesis” phase by grouping by service graph/fingerprint before page. | Correlation rules encode operational judgement; a bad migration can suppress important pages or group unrelated failures. |
| Incident routing + paging | PagerDuty retained, but only receives grouped/correlated incidents | Paging is already the accepted human escalation surface; keeping it limits migration risk while reducing noisy incidents upstream. | The team keeps a vendor cost and integration dependency; if PagerDuty changes later, integration history and schedules must be migrated. |
| Dashboards + SLO tracking | Grafana as the primary human query surface | Gives on-call one starting point for metrics, logs, traces, SLOs, and incident context, reducing “which tool do I open first?” onboarding friction. | Existing Datadog query habits and exec dashboard semantics must be rewritten and validated. |
| Incident knowledge / decision trail | OpenSearch-backed incident index with action/service/rollback metadata | Addresses missing audit trail and inability to query incidents by service/action over 90 days. | Adds a new data governance responsibility; if abandoned, postmortems again become Slack-scroll archaeology. |

## Public documentation cross-checks

| Component choice | Evidence checked | Why it matters |
|---|---|---|
| OpenTelemetry Collector | Collector configuration uses receivers, processors, exporters, and connectors; processors transform/filter/enrich telemetry before export. | Supports using one governed ingest pipeline instead of three vendor agents. |
| VictoriaMetrics | VictoriaMetrics documents Prometheus `remote_write` ingestion at `/api/v1/write`; vmagent can receive, relabel/filter, and proxy remote-write data. | Supports PromQL-compatible metrics migration from Datadog dashboards and alerts. |
| Loki | Loki retention is implemented through the Compactor; object-store lifecycle policy should be longer than the Loki retention period. | Supports explicit 7-day hot retention plus S3 cold retention controls. |
| Tempo | Tempo documentation describes service graph views and metrics generated from traces; Grafana can use Tempo data for trace/log/metric correlation. | Supports the design claim that traces help reduce first-hypothesis time. |
| Grafana Cloud | Grafana Cloud Pro is paid usage-based; Enterprise has annual spend commitments. | Supports modeling Grafana as a paid primary UI rather than a free replacement. |

## Alternatives reviewed but not selected

| Capability | Alternatives reviewed | Why the selected component remains stronger for this lab |
|---|---|---|
| Metrics | Vanilla Prometheus, Mimir, Datadog metrics, New Relic / Dynatrace consolidation | VictoriaMetrics gives a lower-operational-weight path than Mimir for this scale, keeps PromQL compatibility, and removes Datadog host pricing without replacing one SaaS bill with another. |
| Logs | Splunk discount, Datadog Logs, OpenSearch-only, Elastic Cloud, ClickHouse-only, S3-only archive | Loki + ClickHouse + S3 is the best balance: hot operational search, SQL/audit analytics, and cheap cold retention. The rejected options either miss the cost target, weaken incident response, or over-index everything. |
| Tracing | Jaeger, Datadog APM, Honeycomb, SkyWalking | Tempo is selected because Grafana is the target human surface and service-graph correlation matters more than introducing another SaaS UI. |
| Alerting / correlation | PagerDuty Event Orchestration only, Grafana OnCall, Coroot, custom LLM-first AIOps | Deterministic Alertmanager + topology grouping is safer for the first migration; PagerDuty receives fewer, better incidents without replacing the paging system. |
| Dashboards / SLO | Self-host Grafana, Datadog dashboards, vendor all-in-one dashboards | Grafana Cloud reduces self-hosting burden while still consolidating the on-call starting point across metrics/logs/traces. |
| Incident knowledge | Postgres-only, ticket comments only, Splunk saved searches | OpenSearch keeps incident retrieval queryable by service/action/root-cause over 90 days without requiring Splunk as the long-term incident memory. |

## Mapping to pain points

- Pain #1 and #6: log search latency / hot-tier rotation → hot/cold log tiering with benchmarked query SLOs.
- Pain #2: 1% tracing hides tail failures → adaptive/tail-based sampling on critical paths.
- Pain #3, #5, #8: manual correlation, alert storms, onboarding → service graph correlation + Grafana-first workflow.
- Pain #4: cardinality overage → OTel policy processor and metric-label governance.
- Pain #7 and #9: no incident decision audit → incident knowledge index.
- Pain #10: vendor lock-in → eight-week migration plan plus Splunk non-renewal notice gate.
