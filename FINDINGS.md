# FINDINGS.md

## A7 — POC validation plan

The most uncertain component is the **new log storage/search path: Loki (hot ops) + ClickHouse (analytics) + S3 cold archive**. The first assumption to validate is that at the current scale of **~52GB/day indexed logs**, the top five incident queries used during payment, catalog, search, and checkout incidents can return under the agreed p99 latency target while keeping projected monthly log cost below the modeled log tier allocation (~$3,000/month within the $7,500 OSS backend). In a three-day POC, replay seven days of representative logs (**~364GB total**) including payment-svc connection-pool incidents and catalog-db slow-query incidents, run the top five queries across 1h/24h/7d windows. **Pass threshold:** p99 < 2s (1h window), p99 < 5s (24h), p99 < 10s (7d); ingest lag < 30s; cold-archive retrieval from S3 < 5 minutes. **Fail:** any query exceeds p99 threshold OR cold retrieval incomplete → redesign log tiering strategy before Week 3 gate.

## 1. Which capability turned out hardest to replace, and why? What did you compromise on?

The hardest capability to replace is **long-tail log search and audit reporting** currently served by Splunk Cloud. It is expensive at **$13,900/month**, but it also carries saved searches, compliance reports, and operator habits. The compromise is to keep a smaller hot searchable tier plus S3 cold archive rather than deleting long-tail logs entirely. That saves cost, but some 7–30 day ad-hoc searches will be less convenient than Splunk.

## 2. Where did the design trade resilience for cost? Quantify the trade-off.

The main trade-off is reducing 30-day hot Splunk search to a smaller hot tier and S3 cold archive. The modeled saving is roughly **$9,400/month** on the Splunk line ($13,900 → $4,500), but worst-case long-tail incident search may add **1–3 minutes** if an engineer must retrieve from cold archive or a narrower structured index. The design offsets this by improving traces, service graph correlation, and incident retrieval so the common path to first hypothesis should still improve.

## 3. If the budget cut requirement were 60% instead of 40%, which decisions would change?

A 60% cut means the target bill must be **≤ $16,800/month**, so the current modeled **$20,930/month** would not pass. Decisions that would change: reduce PagerDuty seats more aggressively or replace PagerDuty for non-critical teams; reduce Grafana managed spend by self-hosting; shrink hot log retention to 3 days for low/medium criticality services; remove more synthetics. Decisions that would not change: keep tracing stronger than today, keep OTel as ingestion layer, and keep a formal paging path for critical services. This shows cost structure is dominated by hot logs, host-priced APM/metrics, and human-seat SaaS.

## 4. Identify one real-world pattern copied into the design.

The design copies the common SRE pattern of **separating signal ingestion from human paging**: collect all telemetry through a common pipeline, evaluate rules/correlation centrally, and page humans only after deduplication/grouping. This pattern appears in Prometheus/Alertmanager-based systems and in Honeycomb/Charity Majors-style observability thinking: preserve high-cardinality diagnostic context, but do not page on every raw symptom. I changed it for GeekShop by keeping PagerDuty as the final routing surface to reduce migration risk.

## 5. What is the biggest unknown that could derail migration at week N?

The biggest unknown is whether the new log hot tier can meet incident-query latency and audit requirements by **week 5–6**. If p99 query latency is worse than Splunk, or if audit cannot retrieve required samples from S3 cleanly, the migration stalls because logs are the largest cost lever. The first-week spike should therefore define the top incident queries, prepare replay data, and set exact p99/pass thresholds before any log cut-over.

## Evidence references from data pack

- Current total bill: **$42,000/month** (`current-stack.md`).
- Largest current line item: Splunk Cloud **$13,900/month**, ~52GB/day, 30-day retention.
- Current median MTTR in incident file: **26 minutes**.
- Current median MTTD in incident file: **11 minutes**.
- Recurring incident classes include: slow_query (3), connection_pool_exhaustion (3), lock_contention (1), eviction (1), memory_leak (1).
- Most frequently involved services include: catalog-db (6), payment-svc (6), checkout-svc (6), payments-db (5), recommender-svc (5).
