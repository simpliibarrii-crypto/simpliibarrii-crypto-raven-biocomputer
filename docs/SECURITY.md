# Security model

Raven BioComputer is an alpha research tool. It is not a medical device, biosafety system, clinical decision engine, or hardened multi-tenant sandbox.

## Default boundaries

- Registered deterministic tools only.
- Arbitrary shell and credential access are blocked.
- Path traversal outside a run workspace is rejected.
- Every input and result artifact is SHA-256 hashed.
- Sensitive clinical, wet-lab, genome-editing, and pathogen-engineering requests require human review.
- The Docker worker profile disables networking and drops Linux capabilities.

## Data handling

Use synthetic or properly governed data. Do not place secrets, raw PHI, regulated clinical records, or proprietary datasets in a public Space or public repository.

## Reporting

Do not disclose security vulnerabilities in public issues. Use the private security-reporting channel configured for the repository.
