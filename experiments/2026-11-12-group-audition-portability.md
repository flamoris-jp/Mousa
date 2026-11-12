# Cycle38 test-only portability correction

Independent QA found that the MIDI roundtrip test failed with `ModuleNotFoundError: mido` when Python site-packages were disabled. The two analytic-render tests passed. This was an optional-test dependency oversight, not an audio or original-data failure.

Only the MIDI roundtrip test gained `skipUnless(importlib.util.find_spec('mido'))`. The exporter, renderer, source candidates, label mapping and old snapshots are unchanged. The exact historical test was reconstructed and hash-verified against the old code-bound plan, then preserved privately. The supplemental correction JSON records both test hashes and the complete two-line diff.

A separate portability plan binds the current test hash and references the old plan. A new private run produced four MIDI and four WAV files byte-identical to the original eight artifacts; all four per-clip verification objects also match. No old artifact or manifest was replaced, and no media resend is needed.

Verification:
- With mido:364tests,363passed,1existing skip.
- Dependency-free `python -S`:364tests,323passed,41skipped. The added41st skip is this optional MIDI test; it is not reported as passed.
- Focused dependency-free:2analytic tests passed,1MIDI test skipped.

Portable plan SHA: `8ab74aeba771479b8856b18008965d56ae8452fe867416d14349cbd7c34f8567`.
Only new supplemental metadata is prepared for the separate audition metadata directory. Historical media and its original verified run remain valid historical records.
