# A2 — Component Decision Table

Current pain points are not basic observability gaps; the team already has decent per-service dashboards and alert fidelity. The redesign targets cost, correlation, cognitive load, and migration safety.

| Capability | Chosen component / vendor | Why this one? | What gets worse if we change our mind in six months? |
|---|---|---|---|
| Metrics ingestion + storage + query | OpenTelemetry Collector → Prometheus Agent remote-write → VictoriaMetrics | Replaces Datadog host-priced metrics with an OSS/hybrid store while keeping PromQL-compatible dashboards and alert rules. VictoriaMetrics chosen over vanilla Prometheus for better compression (40%+ vs Prometheus), higher cardinality tolerance, and enterprise-grade long-term retention. | Query/rule semantics, retention tuning, and capacity assumptions must be revisited; teams may need to rewrite PromQL and SLO panels again. |
| Logs ingestion + storage + search | Loki (operational hot logs, 7d) + ClickHouse (structured analytics/audit queries) + Amazon S3 cold archive (1yr) | Logs are the largest cost pool; structured hot retention plus cheap cold archive attacks the $13.9k Splunk line without deleting audit capability. Loki serves day-to-day operational queries with label-based LogQL; ClickHouse handles high-cardinality structured analytics and audit queries that need SQL. | Long-tail ad-hoc search and compliance workflows get worse first; security/audit users may lose Splunk UX and saved-search behavior. Dual query dialect (LogQL + SQL) adds cognitive load. |
| Distributed tracing | OpenTelemetry instrumentation + Tempo (Grafana-native) | Tempo chosen because Grafana is the primary UI, giving native trace-to-metrics-to-logs correlation in one surface. The brief requires 30% faster root-cause; stronger trace coverage and tail/adaptive sampling preserve diagnostic value while removing Datadog APM host pricing. | Sampling policy and instrumentation become team-owned; bad sampling could hide the exact low-frequency tail events we are trying to expose. |
| Alerting + correlation / grouping | Alertmanager + Robusta-style topology correlation | Directly addresses PagerDuty clusters and the 8-minute manual “first hypothesis” phase by grouping by service graph/fingerprint before page. | Correlation rules encode operational judgement; a bad migration can suppress important pages or group unrelated failures. |
| Incident routing + paging | PagerDuty retained, but only receives grouped/correlated incidents | Paging is already the accepted human escalation surface; keeping it limits migration risk while reducing noisy incidents upstream. | The team keeps a vendor cost and integration dependency; if PagerDuty changes later, integration history and schedules must be migrated. |
| Dashboards + SLO tracking | Grafana as the primary human query surface | Gives on-call one starting point for metrics, logs, traces, SLOs, and incident context, reducing “which tool do I open first?” onboarding friction. | Existing Datadog query habits and exec dashboard semantics must be rewritten and validated. |
| Incident knowledge / decision trail | OpenSearch-backed incident index with action/service/rollback metadata | Addresses missing audit trail and inability to query incidents by service/action over 90 days. | Adds a new data governance responsibility; if abandoned, postmortems again become Slack-scroll archaeology. |

## Mapping to pain points

- Pain #1 and #6: log search latency / hot-tier rotation → hot/cold log tiering with benchmarked query SLOs.
- Pain #2: 1% tracing hides tail failures → adaptive/tail-based sampling on critical paths.
- Pain #3, #5, #8: manual correlation, alert storms, onboarding → service graph correlation + Grafana-first workflow.
- Pain #4: cardinality overage → OTel policy processor and metric-label governance.
- Pain #7 and #9: no incident decision audit → incident knowledge index.
- Pain #10: vendor lock-in → eight-week migration plan plus Splunk non-renewal notice gate.
