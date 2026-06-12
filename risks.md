# A6 — Risk Register

Risks are ranked from the lab inputs rather than generic observability concerns. The highest-severity risks tie to the biggest cost lever (`inputs/current-stack.md` Splunk/Datadog spend), fastest incident path (`inputs/incidents_history.json` payment/checkout/catalog incidents), and most explicit operator pain (`inputs/pain_points.md` four-UI triage, alert storms, trace gaps, slow log search).

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Log query p99 is worse than Splunk for 7–30 day incident searches. | Medium | High | Replay 7 days of logs and benchmark top 5 incident queries before cut-over; keep Splunk read-only fallback for 30 days. | Observability lead |
| Correlation suppresses a real critical page or groups unrelated incidents. | Medium | High | Two-week shadow mode; require zero suppressed critical alerts in replay; start with grouping-only before suppression. | Incident response lead |
| OTel collector pipeline drops telemetry under peak 14:00 traffic. | Medium | High | Load test collector at 2x current 52GB/day log volume; deploy HA collectors with backpressure and queue metrics. | Platform team |
| Team underestimates OSS operational burden and creates a new fragile observability stack. | Medium | High | Add $7.5k/month backend ops budget, assign service owners, and define SLOs for the observability platform itself. | Platform manager |
| Splunk contract notice window is missed again. | Low | High | Create week-1 renewal gate, calendar alert 120/100/90 days before renewal, and assign procurement owner. | Engineering manager + Procurement |
| Security/audit users reject S3 cold archive or lose required report workflows. | Medium | Medium | Validate 30-day audit retrieval and compliance report sample before reducing Splunk; keep export format documented. | Security lead |

## Risk evidence map

| Risk area | Evidence | Control in plan |
|---|---|---|
| Log tier regression | Splunk is **$13,900/month** at ~52GB/day and handles long-tail searches. Pain points mention slow 7-day searches and index rotation. | Week 5 replay benchmark, 30-day Splunk fallback, and S3 retrieval gate. |
| Alert safety | Pain points include 47 PagerDuty incidents in 90 seconds, but critical pages cannot be lost. | Week 7 shadow mode, 0 suppressed critical pages, grouping-only first. |
| Telemetry loss | Migration touches all 10 services and 4 backing stores from `inputs/services.json`. | Weeks 2–7 dual-run and no-blackout guarantee. |
| OSS burden | Cost model explicitly adds **$7,500/month** backend compute/storage plus **$2,490/month** reserve. | Assign platform owners and observability-platform SLOs. |
| Contract timing | The design depends on reducing Splunk/Datadog spend within six months. | Week 1 procurement calendar gate with 120/100/90-day reminders. |
