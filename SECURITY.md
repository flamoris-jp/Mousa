# Security policy

Mousa is early research software and has no production service or supported security release channel yet.

Do not include tokens, credentials, private repository data, user-specific preference histories, private MIDI assets, or sensitive host information in public Issues or PRs.

For a sensitive vulnerability, use GitHub's private vulnerability reporting when available, or a non-public contact channel indicated by the FLAMORIS organization. Do not publish exploitation details before a maintainer has had a chance to review.

All input MIDI, manifests, archives and model artifacts are untrusted. Bound sizes and event counts, validate content and source provenance, and never treat model output as authorization for a filesystem, network, runtime or Cantabile action.
