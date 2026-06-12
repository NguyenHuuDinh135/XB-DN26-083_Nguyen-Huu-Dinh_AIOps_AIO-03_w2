# Optional Bonus — Capacity, Exit Clauses, Skills Gap, and DR

This section is not required for A1-A7, but it reduces reviewer uncertainty around six-month execution risk.

## B. Capacity Model

Baseline evidence:

- Current indexed log volume: **52GB/day** from `inputs/current-stack.md`.
- Current topology: **10 services**, **4 backing stores**, and **17 edges** from `inputs/services.json`.
- Current median incident baseline: **MTTD 11 minutes**, **MTTR 26 minutes** from `inputs/incidents_history.json`.

| Scenario | 12-month assumption | Log volume | Target monthly cost impact | Budget status |
|---|---|---:|---:|---|
| Slow growth | Service count stable; 15% more traffic/logs after structured logging cleanup. | ~60GB/day raw; hot indexed subset stays near 35GB/day. | +$800 to +$1,200 | Still under $25,200. |
| Expected growth | 20% traffic growth plus two new services; label budgets remove high-cardinality waste. | ~78GB/day raw; hot indexed subset ~45GB/day. | +$1,800 to +$2,800 | Still under $25,200 if hot retention remains 7 days. |
| Fast growth | Traffic doubles before sampling/tiering policies mature. | ~104GB/day raw; hot indexed subset can exceed 65GB/day. | +$3,000 to +$6,000 | Budget risk; first constraint is log hot-tier cost and p99 query latency. |

Capacity controls:

- Keep critical-service hot retention at 7 days, but reduce low/medium services to 3 days if fast growth appears.
- Enforce service-owner metric label budgets in CI before production rollout.
- Review top 20 log fields monthly; demote high-cardinality fields to ClickHouse/S3-only unless they are incident-critical.
- Alert when OTel collector queue age exceeds 30 seconds, dropped telemetry is non-zero for 5 minutes, or log hot-tier p99 exceeds the migration SLO.

## C. Vendor Exit-Clause Analysis

| Vendor/tool | Current constraint | Clause to negotiate | Why it matters |
|---|---|---|---|
| Splunk Cloud | 12-month contract ending in 7 months; 90-day notice; bulk export capped at 100GB/day. | 30-day transition export window at >=200GB/day, export in JSON or Parquet, no egress penalty for termination export, and read-only search access for 30 days after cut-over. | Logs are the largest cost lever and the highest audit risk. |
| Datadog | Monthly billing; API export but no bulk export tool. | Preserve 30-day read-only account access after cancellation, bulk monitor/dashboard export in JSON, and no penalty for reducing host counts during dual-run. | Monitor and dashboard migration must be reversible. |
| PagerDuty | Monthly billing; integration history export requires support ticket. | API export of schedules, escalation policies, services, integrations, and incident history before any seat reduction. | PagerDuty remains the paging surface; seat cleanup must not lose operational history. |
| Grafana Cloud | Monthly; dashboards exportable as JSON. | Dashboard, alert rule, and contact-point export guaranteed at cancellation; usage-based cost cap during migration. | Grafana becomes the primary UI, so portability remains important. |

## D. Skills-Gap and Transition Plan

| Role | New skills needed | Training / transition plan | Success signal |
|---|---|---|---|
| Platform engineers | OpenTelemetry Collector pipelines, queue/backpressure tuning, HA collector rollout. | Week 1-2 workshop using shadow OTel deployment; one owner writes the collector runbook. | On-call can explain and roll back receivers/processors/exporters in under 30 minutes. |
| SRE/on-call engineers | Grafana-first incident flow, trace-to-log drilldown, LogQL basics, correlation audit. | Week 6-8 synthetic incident drills; two recorded triage walkthroughs. | On-call independently triages synthetic payment incident from Grafana first. |
| Service teams | Metric label budgets, structured logging, critical trace attributes. | CI feedback plus service-owner review of top labels/log fields. | Custom metric excess falls >=70% without breaking critical dashboards. |
| Security/audit | Cold archive retrieval, ClickHouse audit SQL, evidence export process. | Week 5 audit retrieval rehearsal with 30-day sample. | Security accepts the sample report before Splunk reduction. |

## E. Multi-Region / Disaster-Recovery Posture

The application itself is not redesigned for multi-region in this lab, but the observability stack should avoid becoming a single point of blindness.

| Component | DR posture | RTO | RPO | Justification |
|---|---|---:|---:|---|
| OTel collectors | Run at least two collector replicas per production cluster/AZ with queued retry and local backpressure metrics. | 15 minutes | <1 minute for metrics/traces; logs may buffer longer | Collector loss must not create observability blackout. |
| VictoriaMetrics | Daily snapshots plus replicated remote storage; keep Grafana read path documented. | 4 hours | 24 hours for historical metrics; live metrics continue through collectors. | Metrics are important but not the largest audit obligation. |
| Loki hot logs | Object storage backend with compactor; indexes backed up daily. | 4 hours | 24 hours for hot log indexes; raw logs retained through cold archive path. | Hot operational search can tolerate short degradation if Splunk fallback remains during migration. |
| ClickHouse analytics | Replicated production nodes and daily backup of structured log tables. | 4 hours | 24 hours | SQL analytics supports audit and incident deep dive, but not first-line paging. |
| S3 cold archive | Versioning, lifecycle policy, and object lock for audit prefixes. | 24 hours | Near-zero once object is written | Cold archive is the compliance backstop. |
| PagerDuty | SaaS retained; export schedules/integrations monthly. | Vendor-managed | Vendor-managed | Paging maturity is preserved by not replacing PagerDuty during telemetry migration. |

