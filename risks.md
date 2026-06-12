# A6 — Risk Register

| Risk | Likelihood | Impact | Mitigation | Owner |
|---|---|---|---|---|
| Log query p99 is worse than Splunk for 7–30 day incident searches. | Medium | High | Replay 7 days of logs and benchmark top 5 incident queries before cut-over; keep Splunk read-only fallback for 30 days. | Observability lead |
| Correlation suppresses a real critical page or groups unrelated incidents. | Medium | High | Two-week shadow mode; require zero suppressed critical alerts in replay; start with grouping-only before suppression. | Incident response lead |
| OTel collector pipeline drops telemetry under peak 14:00 traffic. | Medium | High | Load test collector at 2x current 52GB/day log volume; deploy HA collectors with backpressure and queue metrics. | Platform team |
| Team underestimates OSS operational burden and creates a new fragile observability stack. | Medium | High | Add $7.5k/month backend ops budget, assign service owners, and define SLOs for the observability platform itself. | Platform manager |
| Splunk contract notice window is missed again. | Low | High | Create week-1 renewal gate, calendar alert 120/100/90 days before renewal, and assign procurement owner. | Engineering manager + Procurement |
| Security/audit users reject S3 cold archive or lose required report workflows. | Medium | Medium | Validate 30-day audit retrieval and compliance report sample before reducing Splunk; keep export format documented. | Security lead |
