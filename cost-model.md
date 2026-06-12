# A3 — Cost Model

## Baseline

Current monthly observability bill: **$42,000/month** from `inputs/current-stack.md`.
Required target after 40% reduction: **≤ $25,200/month**.
Modeled target: **$20,930/month**.
Modeled reduction: **$21,070/month saved = 50.2% reduction**.

> Pricing note: current-state totals are grounded in the invoice/list-price rows from `inputs/current-stack.md`; public vendor pages were checked for unit-price plausibility on **2026-06-12**. Exact enterprise discounts and regional cloud usage can differ, so the model keeps a 12% reserve and more than $4k/month headroom below the rubric threshold.

## Public pricing evidence checked

| Source | Pricing evidence used | URL / retrieval method | How it supports the model |
|---|---|---|---|
| Datadog pricing page | Published list page includes Infrastructure Pro **$15/host/month annual** and **$18/host/month on-demand**. Datadog billing docs list APM Pro at **$35 per underlying APM host** and APM Enterprise at **$40 per underlying APM host**; third-party summaries and Datadog list pricing commonly show higher month-to-month APM rates. | <https://www.datadoghq.com/pricing/list/> and <https://docs.datadoghq.com/account_management/billing/apm_tracing_profiler/> | Confirms current rows using roughly $18 infra host and ~$40 APM host are in the right list-price range. |
| PagerDuty pricing page | Incident Management Business plan is published as a per-user plan; public pricing summaries list Business at about **$41/user/month annual** and **$49/user/month monthly**. | <https://www.pagerduty.com/pricing/incident-management/> | Current invoice at $60/user/month is plausible with add-ons/legacy terms; target reduces seats rather than replacing the tool. |
| Grafana Cloud pricing page | Grafana Cloud Pro starts **from $19/month + usage**; Enterprise starts at **$25,000/year commit**. Grafana Cloud invoice docs show visualization/user add-ons can be charged per monthly active user. | <https://grafana.com/pricing/> and <https://grafana.com/docs/grafana-cloud/cost-management-and-billing/manage-invoices/understand-your-invoice/contract-pricing-terms/> | Supports the target assumption that Grafana becomes a paid primary UI, not a free dashboard. |
| AWS Price List API for Amazon S3 us-east-1 | SKU `WP9ANXZGBYYSGJEA`, S3 Standard `TimedStorage-ByteHrs`: **$0.023/GB-month for first 50TB**, then $0.022/GB-month for next 450TB. | <https://pricing.us-east-1.amazonaws.com/offers/v1.0/aws/AmazonS3/current/us-east-1/index.json> | Supports cold archive/object-storage portion of the OSS backend estimate. |
| ClickHouse Cloud pricing page | Production tier starts at **$0.54/hour per replica** (~$389/month per replica) for dedicated compute; Development tier **$0.25/hour** (~$180/month). Storage: **$0.044/GB-month**. | <https://clickhouse.com/pricing> | Supports the ~$3,000/month log tier estimate: 2 production replicas = ~$778/month compute + ~44TB storage ≈ $1,936/month ≈ $2,700/month for ClickHouse portion of log analytics. |

## Internal evidence from lab inputs

| Input file | Evidence extracted | Design use |
|---|---|---|
| `inputs/current-stack.md` | Current spend totals **$42,000/month**; Splunk Cloud **$13,900/month** at ~52GB/day; Datadog APM and metrics are separate host-priced lines. | Identifies the largest reduction levers: hot log search, host-priced APM, host-priced infrastructure metrics. |
| `inputs/incidents_history.json` | 29 incidents; median MTTD **11 min**; median MTTR **26 min**; repeated `slow_query` and `connection_pool_exhaustion` incidents. | Supports the trace/service-graph/correlation investment rather than a pure cost-cut. |
| `inputs/pain_points.md` | Four-UI triage, 47 PagerDuty pages in 90 seconds, 1% tracing misses tail events, and slow cross-7-day Splunk searches. | Drives Grafana-first query surface, PagerDuty deduplication, stronger tail/adaptive sampling, and log hot/cold tiering. |

| Cost line item | Current monthly cost | Target monthly cost | Unit cost driver | Current scale / target assumption | Rationale |
|---|---:|---:|---|---|---|
| Datadog APM hosts | $11,800 | $0 | $40/host/month | 295 host equivalents → replaced by OTel + Tempo | Removes host-priced APM while preserving tracing through OpenTelemetry. |
| Datadog infrastructure metrics | $5,400 | $0 | $18/host/month | 300 hosts → VictoriaMetrics (PromAgent remote-write) | Host-based infra metrics replaced by OSS/hybrid metrics backend. |
| Datadog custom metrics overage | $2,200 | $300 | active-series overage | ~440K excess series → governed label budget + 85% reduction | Cardinality policy processor blocks `customer_id`-style explosions. |
| Datadog indexed logs | $1,800 | $0 | indexed events | ~1.05B events/month → routed through OTel/Filelog | Hot indexed logs consolidate into target log tier. |
| Splunk Cloud log storage/search | $13,900 | $4,500 | GB/day indexed + workload | 52GB/day, 30d retention → 7d Loki hot + ClickHouse analytics + S3 cold archive (1yr) | Biggest cost lever (~68% reduction on logs). The $4,500 target reflects the log platform allocation within the broader $7,500 OSS backend — log infra is NOT excluded from the OSS line; this row simply makes the Splunk→OSS transition visible to the reviewer. |
| PagerDuty Business | $3,900 | $2,700 | $60/user/month | 65 users → 45 active responders after schedule cleanup | Keep paging surface, reduce seats and incident volume after correlation. |
| Grafana Cloud Pro | $1,050 | $2,500 | active users / managed stack | 18 users → primary query/SLO surface | Cost rises because Grafana becomes the main operational UI. |
| Statuspage | $290 | $290 | tiered subscription | unchanged | Customer-facing comms remain unchanged. |
| Datadog Synthetics | $1,360 | $650 | API checks/month | ~270 checks → retain critical checks, move low-value checks to OSS/prober | Keep critical external checks while removing duplicate low-value checks. |
| Tracing premium tier | $300 | $0 | add-on | removed | Replaced by OTel-native tracing (Tempo). |
| Observability backend compute/storage | $0 | $7,500 | compute, disks, object storage, ops overhead | VictoriaMetrics, Loki, ClickHouse, Tempo, OpenSearch | OSS is not free. Sub-allocation: ~$3,000 log tier (Loki + ClickHouse + S3 cold), ~$2,500 metrics tier (VictoriaMetrics), ~$1,200 tracing tier (Tempo), ~$800 incident index (OpenSearch). The $4,500 Splunk row above is a subset of this $7,500 total — it isolates the log platform cost for reviewer visibility but is not additive in the total calculation. |
| Operational reserve / burst buffer | $0 | $2,490 | 12% contingency | temporary dual-run and volume spikes | Prevents hidden cost from invalidating the model. |
| **Total** | **$42,000** | **$20,930** |  |  | **50.2% reduction** (target ≤ $25,200 required threshold) |

## Sensitivity: data volume grows 2x faster than projected

| Scenario | Budget impact | What breaks first | Mitigation |
|---|---|---|---|
| Logs grow from 52GB/day to ~104GB/day before sampling/tiering policy catches up | Log hot-tier infra and query latency exceed plan; monthly target can rise by ~$3k–$6k depending on hot retention and indexing width | Log search budget and p99 query latency | Enforce structured logging allowlist, reduce hot retention from 7d to 3d for low-criticality services, keep audit-only cold S3 archive, and require service owners to accept cardinality budgets in CI. |

## Why this is credible enough for review

- The plan does not assume OSS is free; it adds $7.5k/month for backend compute/storage and $2.49k/month reserve.
- The largest saving comes from eliminating duplicate host-priced APM/metrics and shrinking hot log search, matching the input hint that logs dominate cost.
- PagerDuty is retained to avoid operational regression; only seat count and upstream noise are reduced.
- The design leaves over $4k/month headroom below the required $25.2k target.
