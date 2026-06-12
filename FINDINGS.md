# FINDINGS.md

## A7 — POC validation plan

The most uncertain component is the **new log storage/search path: Loki (hot ops) + ClickHouse (analytics) + S3 cold archive**. The first assumption to validate is that at the current scale of **~52GB/day indexed logs**, the top five incident queries used during payment, catalog, search, and checkout incidents can return under the agreed p99 latency target while keeping projected monthly log cost below the modeled **$4,500/month additive log-platform budget**. In a three-day POC, replay seven days of representative logs (**~364GB total**) including payment-svc connection-pool incidents and catalog-db slow-query incidents, run the top five queries across 1h/24h/7d windows. **Pass threshold:** p99 < 2s (1h window), p99 < 5s (24h), p99 < 10s (7d); ingest lag < 30s; cold-archive retrieval from S3 < 5 minutes. **Fail:** any query exceeds p99 threshold OR cold retrieval incomplete → redesign log tiering strategy before Week 3 gate.

Evidence used: `inputs/current-stack.md` gives the ~52GB/day Splunk volume and **$13,900/month** Splunk line; `inputs/incidents_history.json` identifies repeated payment/catalog incident classes; `cost-model.md` separates the **$4,500/month** log-platform budget from the **$7,500/month** non-log observability backend.

## 1. Which capability turned out hardest to replace, and why? What did you compromise on?

The hardest capability to replace is **long-tail log search and audit reporting** currently served by Splunk Cloud. It is expensive at **$13,900/month**, but it also carries saved searches, compliance reports, and operator habits. The compromise is to keep a smaller hot searchable tier plus S3 cold archive rather than deleting long-tail logs entirely. That saves cost, but some 7–30 day ad-hoc searches will be less convenient than Splunk.

This answer is grounded in `inputs/pain_points.md`: cross-7-day searches are already slow, and index rotation already breaks dashboards periodically. The target design does not pretend this goes away; it moves common incident queries to hot Loki/ClickHouse paths and makes cold retrieval an explicit, measured workflow.

## 2. Where did the design trade resilience for cost? Quantify the trade-off.

The main trade-off is reducing 30-day hot Splunk search to a smaller hot tier and S3 cold archive. The modeled saving is roughly **$9,400/month** on the Splunk line ($13,900 → $4,500), but worst-case long-tail incident search may add **1–3 minutes** if an engineer must retrieve from cold archive or a narrower structured index. The design offsets this by improving traces, service graph correlation, and incident retrieval so median MTTR can move from **26 minutes** to the required **≤18.2 minutes** target.

Evidence: incident history has median MTTR **26 minutes** and median MTTD **11 minutes**; the migration plan therefore uses p99 log-query gates and a synthetic incident triage gate rather than treating cost savings as sufficient proof.

## 3. If the budget cut requirement were 60% instead of 40%, which decisions would change?

A 60% cut means the target bill must be **≤ $16,800/month**, so the current modeled **$20,930/month** would not pass. Decisions that would change: reduce PagerDuty seats more aggressively or replace PagerDuty for non-critical teams; reduce Grafana managed spend by self-hosting; shrink hot log retention to 3 days for low/medium criticality services; remove more synthetics. Decisions that would not change: keep tracing stronger than today, keep OTel as ingestion layer, and keep a formal paging path for critical services. This shows cost structure is dominated by hot logs, host-priced APM/metrics, and human-seat SaaS.

Evidence: `cost-model.md` shows the largest removed current lines are Datadog APM, Datadog infrastructure metrics, and Splunk Cloud. PagerDuty and Grafana are intentionally retained because the lab forbids a pure cost-cut that harms incident response.

## 4. Identify one real-world pattern copied into the design.

The design copies the common SRE pattern of **separating signal ingestion from human paging**: collect all telemetry through a common pipeline, evaluate rules/correlation centrally, and page humans only after deduplication/grouping. The concrete real-world pattern is Prometheus/Alertmanager-style inhibition/grouping plus Grafana Tempo service graphs for topology context, combined with Honeycomb-style high-cardinality diagnostic thinking: preserve context for debugging, but do not page on every raw symptom. I changed it for GeekShop by keeping PagerDuty as the final routing surface to reduce migration risk.

Evidence: `inputs/pain_points.md` reports alert storms and four-UI triage; `adr/adr-002-otel-correlation-pagerduty.md` documents why PagerDuty is retained while correlation moves upstream.

## 5. What is the biggest unknown that could derail migration at week N?

The biggest unknown is whether the new log hot tier can meet incident-query latency and audit requirements by **week 5–6**. If p99 query latency is worse than Splunk, or if audit cannot retrieve required samples from S3 cleanly, the migration stalls because logs are the largest cost lever. The first-week spike should therefore define the top incident queries, prepare replay data, and set exact p99/pass thresholds before any log cut-over.

## Evidence references from data pack

- Current total bill: **$42,000/month** (`inputs/current-stack.md`).
- Largest current line item: Splunk Cloud **$13,900/month**, ~52GB/day, 30-day retention.
- Current median MTTR in incident file: **26 minutes**.
- Current median MTTD in incident file: **11 minutes**.
- Recurring incident classes include: slow_query (3), connection_pool_exhaustion (3), lock_contention (1), eviction (1), memory_leak (1).
- Most frequently involved services include: catalog-db (6), payment-svc (6), checkout-svc (6), payments-db (5), recommender-svc (5).
