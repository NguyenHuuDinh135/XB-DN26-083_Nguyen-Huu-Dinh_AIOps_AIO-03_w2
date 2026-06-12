# ADR 001 — Replace Splunk hot log search with tiered Loki + ClickHouse + S3 archive

## Context

Splunk Cloud is the largest single line item at **$13,900/month** for ~52GB/day indexed logs with 30-day hot retention. Pain point #1 says cross-7-day searches exceed 25 seconds and cost on-call engineers an extra 30–90 seconds. Pain point #6 says index rotation breaks dashboards for 5–15 minutes once a quarter. At the same time, security/audit still needs long-tail search and compliance evidence.

## Decision

Move application logs to an OpenTelemetry/Filelog pipeline with Loki (day-to-day operational hot tier, 7d, LogQL), ClickHouse (structured analytics and audit queries, SQL), and a cold audit archive in Amazon S3 (1yr). Keep 7 days of high-value structured logs hot by default, extend hot retention only for critical services and incident windows, and export cold logs to S3 with lifecycle policy and immutable/audit controls.

## Alternatives considered and rejected

1. **Keep Splunk Cloud and only negotiate discount.** Rejected because it may reduce price but does not fix index-rotation failures, query-model fragmentation, or vendor renewal risk.
2. **Move all logs to Datadog Logs.** Rejected because Datadog is already a major host-priced cost center and would preserve the SaaS concentration/lock-in problem.
3. **Store only cold logs in S3 and remove hot search.** Rejected because it would satisfy cost reduction but damage incident response and fail the “no capability loss” constraint.

## Consequences

Positive consequences:

- Removes the largest avoidable cost pool while keeping audit retention.
- Gives engineering control over structured logging, retention, and search SLOs.
- Creates an explicit place to enforce log sampling and PII redaction policy.

Negative consequences:

- The team now operates log infrastructure; OSS is not free.
- Long-tail ad-hoc search may be worse than Splunk for security users.
- Migration risk is high because saved searches and audit reports encode tribal knowledge.

## Validation gate

Before cut-over, replay 7 days of representative logs (~364GB) including payment-svc connection-pool incidents and catalog-db slow-query incidents. Run the top 5 incident queries across 1h/24h/7d windows. **Pass only if:** p99 query latency < 2s (1h window), < 5s (24h), < 10s (7d); ingest lag < 30s; and audit export can retrieve a 30-day sample from S3 in < 5 minutes.
