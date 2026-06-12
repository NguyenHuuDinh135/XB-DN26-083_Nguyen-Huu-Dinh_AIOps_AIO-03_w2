# ADR 002 — Adopt OpenTelemetry-first correlation while retaining PagerDuty for paging

## Context

The current stack fragments incident context across Datadog APM, Datadog Logs, Splunk, Grafana, and PagerDuty. Pain point #3 says on-call opens four dashboards during every multi-service incident and spends a median **8 minutes** from page to first hypothesis. Pain point #5 says cascades can produce 47 PagerDuty incidents in 90 seconds. The lab requires a 30% median time-to-root-cause reduction without losing incident-response maturity.

## Decision

Make OpenTelemetry the common ingest layer for metrics, logs, and traces. Add topology-aware correlation using Alertmanager plus Robusta-style fingerprint/service-graph grouping before alerts reach PagerDuty. Retain PagerDuty as the human paging/routing system, but only after correlation and deduplication. Grafana becomes the primary starting surface for SLOs, dashboards, trace/log drilldown, and incident timeline links.

## Alternatives considered and rejected

1. **Replace PagerDuty entirely.** Rejected because paging schedules, escalation policies, and team trust are operationally sensitive; changing them during telemetry migration creates unnecessary blast radius.
2. **Keep Datadog as the full single pane.** Rejected because it does not meet the 40% cost constraint and keeps host-priced APM/metrics as the dominant model.
3. **Build a custom AIOps/LLM correlation engine first.** Rejected because the first value is deterministic fingerprinting, service graph grouping, and incident retrieval; LLM features can support decisions later but should not be the first dependency.

## Consequences

Positive consequences:

- Reduces alert storms before they reach humans.
- Gives on-call one starting point instead of four UIs.
- Keeps PagerDuty’s known escalation behavior while shrinking upstream noise.
- Preserves and improves tracing, which is the highest diagnostic-speed signal.

Negative consequences:

- Correlation rules can suppress important pages if fingerprints are wrong. **Mitigation:** "page anyway" escape hatch per service; weekly correlation audit replaying incident history.
- Service graph accuracy becomes safety-critical.
- The team must learn and maintain OTel collector pipelines and sampling policies.

## Validation gate

Run shadow correlation for two weeks: PagerDuty receives current production alerts while the new correlation layer labels what it would have grouped/suppressed. Cut over only if: (a) ≥95% of historical critical alerts map correctly, (b) 0 critical pages would have been suppressed, (c) median pages/incident ≤ 1.2, (d) on-call can triage one synthetic payment incident from Grafana first, and (e) rollback drill completes under 30 minutes.
