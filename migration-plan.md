# A5 — Eight-week Migration Plan

Migration rule: no observability blackout during business hours. Every production cut-over has a rollback path that restores the previous telemetry path within 30 minutes.

## Evidence behind the gates

- `inputs/services.json` defines the migration blast radius: 10 services, 4 backing stores, and 17 service edges.
- `inputs/current-stack.md` defines the systems that must be dual-run before cut-over: Datadog, Splunk, Grafana, PagerDuty, and Statuspage.
- `inputs/incidents_history.json` provides replay candidates for slow query, connection pool exhaustion, and payment/checkout/catalog failure modes.
- `inputs/pain_points.md` drives the gates for four-UI triage, 47-page alert cascades, missing trace tail events, and slow cross-7-day Splunk searches.

| Week | Work | Go/no-go gate | Rollback path (≤30 min) |
|---|---|---|---|
| 1 | Inventory Datadog monitors, Splunk saved searches, Grafana dashboards, PagerDuty integrations, and critical service owners. File Splunk non-renewal calendar notice (contract notice is 90 days). | 100% critical alerts and dashboards mapped to owners; Splunk renewal date visible in team calendar. | No production change. Keep existing stack as source of truth. Owner: EM. |
| 2 | Deploy OpenTelemetry Collector in shadow mode for all 10 services. Export duplicate metrics/logs/traces while Datadog/Splunk remain authoritative. | All high/critical services emit metrics, logs, and traces through OTel for 72h with no ingest gaps; OTel pipeline latency p50 < 50ms. | Disable OTel DaemonSet/exporter; Datadog/Splunk agents remain active. Owner: Platform Lead. |
| 3 | Stand up VictoriaMetrics backend and Grafana SLO dashboards for edge-lb, checkout-svc, payment-svc, catalog-db, and catalog/search paths. | 95% of critical service dashboards reproduced; alert evaluation matches Datadog for 7 days; p99 query latency < 2s for top 5 incident queries. | Turn off VictoriaMetrics alert rules; keep Datadog monitors paging. Owner: Metrics Lead. |
| 4 | Introduce cardinality budgets and metric-label policy. Block high-risk labels such as `customer_id`; add CI/dev feedback on active-series growth. | Custom metric excess projected to drop ≥70%; no critical dashboard loses required labels; active series reduced from ~440K excess to < 66K. | Revert policy processor config; Datadog custom metrics remain visible. Owner: Platform Lead. |
| 5 | Migrate log ingestion for low/medium criticality services to Loki (hot ops, 7d, LogQL) + ClickHouse (analytics, SQL) with S3 cold archive (1yr). Keep Splunk dual-write/read-only for all services. | Top 5 incident log queries return under p99 < 3s; cold audit retrieval from S3 < 5 minutes; 72h without ingest gaps. | Switch OTel log exporter back to Splunk-only; keep Loki + ClickHouse read-only for debugging. Owner: Logs Lead. |
| 6 | Migrate critical payment/checkout/catalog logs after replay benchmark. Add trace sampling policy: 10%+ for critical path and tail anomalies, 1% base. | Synthetic payment pool-exhaustion incident triaged from Grafana trace→log→metrics links; service graph complete for critical paths; no missed critical traces in replay. | Restore Splunk and Datadog as primary hot search; keep OTel trace export but disable cut-over alerts. Owner: SRE Lead. |
| 7 | Run Alertmanager + topology correlation in shadow mode, comparing grouped incidents to current PagerDuty behavior. | ≥95% historical alert rules reproduced; 0 critical pages suppressed; alert storm simulation reduces pages by ≥70% (median ≤ 1.2 pages/incident). | Keep PagerDuty integrations from Datadog/Splunk only; do not route grouped alerts. Owner: Incident Response Lead. |
| 8 | Cut PagerDuty inbound source to correlated alerts. Reduce seats 65→45. Freeze old SaaS config for 30 days, then begin contract reduction/non-renewal. Publish runbook and train on-call. | On-call independently triages one synthetic critical incident from Grafana first; rollback drill completed under 30 minutes; on-call ACK < 2 minutes; no severity regression. | Re-enable Datadog/Splunk PagerDuty webhooks and disable correlation webhook. Owner: EM. |

## No-blackout guarantee

- Weeks 2–7 are dual-run or shadow-run before authority changes.
- Production cut-overs occur outside business hours with named rollback owner.
- Old SaaS paths stay read-only for at least 30 days after each signal migration.
- The team never disables Datadog/Splunk/PagerDuty authority until equivalent target telemetry has passed a replay or synthetic incident gate.

## Evidence-to-gate traceability

| Gate | Evidence it protects | Why the threshold is there |
|---|---|---|
| 95% critical dashboards/alerts reproduced | Current stack has several human-facing surfaces and existing operational habits. | Prevents a cost migration from silently dropping known diagnostics. |
| Top 5 log queries p99 benchmark | Splunk is the largest cost line but also the audit/search workhorse. | Ensures the biggest cost lever does not regress incident response. |
| 0 critical pages suppressed in shadow mode | Pain points include 47-page cascades, but suppression is safety-sensitive. | Starts with grouping and evidence before any page suppression. |
| Synthetic payment incident triaged from Grafana first | Incident history repeatedly involves payment/checkout/catalog paths. | Proves the new “single starting point” workflow before PagerDuty cut-over. |
| Rollback drill under 30 minutes | Lab explicitly rejects observability blackout. | Makes rollback operational, not just a written promise. |
