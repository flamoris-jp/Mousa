# Cycle47: collision feasibility, explicit derived MIDI and a new source series

## Existing six-candidate replay, not new music evaluation
A fixed2×2 comparison separates collision-aware octave search from allowing a one-group source. All six inputs were already observed in Cycle46. No model fit or new generation occurred.

Collision-constrained strict return completes4/6, versus3/6 with the old post-selection rejection. Its newly feasible path has objective37 instead of the old invalid25: feasibility improves, not the objective. Permitting a one-group source adds one **single-pitch-class repetition fallback**, not a multi-group phrase success. Another case remains rejected because its fixed target segment is too short. No replacement segment was searched.

All accepted event times, gates, velocities, templates, order, note count and rests remain unchanged. The fixed22-reference copy guard still rejects after selection, without another search. Maximum DP occupancy1210states/26520transitions stayed below caps4096/200000; CPU checks are cooperative, not OS hard preemption. Independent Cartesian and branch-bound enumerations confirm optimum/ties. Fifteen accepted policy-output instances come from only six inputs and are not15 independent samples. No human appeal result is claimed.

[Full variation experiment](2026-11-12-constrained-return-cycle47-overview.md).

## Satie37: explicit derived candidate, original unchanged
The original has two unmatched zero-velocity note-ons, which are note-offs, at track1 indices106/109, tick13824, channel0, pitch66. A frozen narrow transformation removed only those two events into a separate derived file; original bytes were not changed. All remaining651 events preserve absolute tick, order and complete payload, with the same header/EOT.

Independent binary SMF/VLQ/running-status decoding, separate from mido and the transform code, verifies this and the global unique-active-key transition trace. Other note tracks use distinct channels; there is no sustain/all-notes-off controller. The derived selected track is reader-compatible with181 notes.

**This does not recover notation voices or the long tied voice retriggered by accompaniment, and audio equivalence has not been demonstrated.** The derived file remains unadmitted, unscreened, untrained and unscored. It is not a new independent composition or an automatically corrected ground truth. Original technical-blocked status is retained.

[Transformation report](2026-11-12-satie37-cycle47-transform-report.json) · [Independent binary check](2026-11-12-satie37-cycle47-independent-review.json).

## Dvořák: first violin piece reserved, not trained
Individual Public Domain typesetting by Felix Janda and the original Simrock violin incipit were checked. Original metadata says Op.4; the historical score says Op.75, plate8765, matching B.150 and the selected opening. This discrepancy is annotated, not silently rewritten. The first score.mid member retains every track; selected violin track1 has123 notes/123 groups, first0/EOT69120. A different piano track uses an unsupported controller and was not repaired or substituted.

The unchanged fixed27-readable-reference screen reports no flags, maximum global similarity0.278689. Satie37's original cannot enter that parser, so this is explicitly **not full28-reference clearance**. All four movements and score/violin/piano forms belong to one source series. The original MIDI ZIP has12 forms, not12 independent works. No fitting/scoring/admission occurred.

There is a provenance-link complication: the official Sibley item10131 HTML itself links the violin PDF using itemId10198. That other bibliographic page is a Kummer work, not a parent/part relationship. The retained linked PDF image is Dvořák Op.75/plate8765. The official HTML, exact linked bytes and independent visual check are retained; no corrected URL is invented.

[Rights ledger](../datasets/research-dvorak1948-cycle47-20261112.json) · [Latest screening status](../datasets/research-dvorak1948-status-cycle47-20261112.json) · [Official-link audit](../datasets/research-dvorak1948-url-audit-cycle47-20261112.json) · [Independent check](2026-11-12-dvorak1948-cycle47-independent-review.json).

## Verification and unchanged learning roles
Final422 tests:421 pass, one existing AudioAnalyzer integration skip. Dependency-free422:381 pass,41 expected optional skips. Compile/diff checks pass. Exact-head CI and LIME full readbacks are recorded in the PR after publication. No MIDI/ZIP/LY/HTML/audio or private generated sequences are committed.

Actual training remains18 works/5512 notes/4190 groups; Groove58 training/16 observed-untrained/1076 unscored-untrained. Dowland remains observed, Lully/Satie38 screen-blocked, original Satie37 technical-blocked, A–D human feedback unanswered. New source reservation and a technical derivation are not training increases.
