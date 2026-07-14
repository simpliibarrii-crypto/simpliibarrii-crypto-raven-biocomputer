# Raven ecosystem integration

## Raven AI

Every completed run emits a `raven.evidence_graph.v1` source, claim, confidence, risk label, and answer trace. Raven can ingest the `integrations.raven_evidence_graph` object directly.

## JSpace Chain

The `jspace.chain.envelope.v1` object carries the policy decision, structured reflection summary, run identifier, and artifact count. This keeps execution bounded and reviewable.

## Home for AI

Home for AI receives a `home.raven_run_record.v1` preview with the input digest, privacy mode, replay flag, and source surface. A desktop adapter can POST the full receipt to a future `/api/v1/raven/biocomputer` endpoint.

## Hermes Edge

The bridge declares `deterministic-tool-first` and `cloud_required: false`. Hermes can execute the same tools locally on capable devices or forward only high-level approved tasks to a stronger workstation.

## OpenClinical AI

The bridge defaults `clinical_use` to false. Requests matching patient-specific decisions, raw PHI, or treatment language stop at the human-review gate rather than entering the clinical runtime.

## MCP

Install `.[mcp]` and run:

```bash
raven-biocomputer-mcp
```

The server exposes:

- `list_biology_tools`
- `run_biology_tool`
- `raven-biocomputer://runs/{run_id}`

The dependency is pinned to the stable MCP Python SDK v1 line (`mcp>=1.28,<2`) until v2 becomes stable.
