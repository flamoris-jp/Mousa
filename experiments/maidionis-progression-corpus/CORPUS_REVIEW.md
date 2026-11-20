# Corpus intake review — 2026-11-17

This review distinguishes public availability, an encoding's license, underlying
music editions, and separately authored annotations. It is not a universal legal
warranty. `source-candidates.json` records exact old-edition source references and
evidence hashes; candidate status is not training admission.

## Selected score candidates

OpenScore/Lieder pinned commit `38c5db510224d9facdc4b08d741fc788cfb58ea8`:
Brahms, Schubert and Robert Schumann metadata initially yielded 278 entries,
263 available score files. Historical edition review retained 22 sets / 198
entries, before exact file/CC0/structural checks. The broader upstream corpus
metadata lists 1,454 scores but this experiment has **not** admitted all of them.

The individual score's source overrides the set's default where they differ.
For example, Brahms Op.32 uses the individually referenced historical scan
rather than silently substituting the set-level scan. Six sets with unresolved
exact scan IDs were quarantined. Named historical first editions and explicitly
PD 1926–27 Mandyczewski Brahms editions were reviewed; no modern critical edition
was silently substituted.

Only note data and timing are used. The exact upstream Git blob, SHA-256,
encoding marker, source metadata digests and family mapping are checked before
preparation. Bundled automatic RomanText is not used: the README's explicit CC0
statement concerns scores, and a separate annotation-specific grant was not
established by this review.

## Sources not admitted

| Source | Observed terms / limitation | Decision |
| --- | --- | --- |
| [DCML Mozart](https://dcmlab.github.io/mozart_piano_sonatas/introduction), [Beethoven](https://dcmlab.github.io/beethoven_piano_sonatas/), [ABC](https://dcmlab.github.io/ABC/introduction) | Current CC BY-NC-SA 4.0; underlying editions also need review | Not in this permissive-source pilot |
| [When in Rome](https://github.com/MarkGotham/When-in-Rome) | New analysis/conversions CC BY-SA 4.0; external material retains source licenses | Separate rights decision required |
| [BPS-FH](https://github.com/Tsung-Ping/functional-harmony) | GPLv3 repository LICENSE; no separate permissive annotation grant established | Quarantined, not fitted |
| [BPSD](https://doi.org/10.5334/tismir.196) | Dataset metadata CC BY 3.0 but paper derives harmony/local-key labels from BPS-FH | Rights chain unresolved; large archive not downloaded |
| [IDMT-SMT-CHORD-SEQUENCES](https://www.idmt.fraunhofer.de/en/publications/datasets/chord-sequences.html) | Evaluation-only CC BY-NC-ND 4.0; synthetic sequences | Not training data; archive not downloaded |

NC/SA/GPL are not intrinsically unusable licenses. They were not absorbed into
this existing permissive-source research frame without a separate decision about
conditions, artifact distribution and compatibility. Composition public-domain
status does not erase encoding, arrangement, critical edition or annotation
rights. A paper's license is not automatically its dataset's license.

## What would improve this research

1. A documented annotation grant and verified score alignment for a suitable
   source, or independently reviewed human chord annotations on admitted CC0
   scores. Keep annotator identity/version, exact bar/beat spans and uncertainty.
2. Broader repertoire and explicit major/minor/local-key handling, developed as
   new protocols rather than relabeling this pilot's failures as success.
3. Separate phrase-scale and local-transition tasks, independently fixed before
   their fits, with unseen-family controls and sufficient denominators.
4. Human listening comparisons. Weak-label prediction and a common-chord lookup
   are not measures of naturalness or creativity.
