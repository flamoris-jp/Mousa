# ChoCo intake review — 2026-11-17

ChoCo was investigated as a discovery/integration layer, not accepted wholesale.
The inspected upstream revision is `5fe168fd55be5c84512abcfbc4e6f1b1f8f0092a`.
This experiment selects **original McGill Billboard annotation files**, not
ChoCo-converted JAMS and not original recordings, lyrics, or melody transcriptions.

## License scope and candidates

[ChoCo's original paper, Table 8](https://pmc.ncbi.nlm.nih.gov/articles/PMC10511441/)
distinguishes collection licenses and the integration's licenses. The authors
also describe contacting the curators of collections without explicit original
licenses. That is meaningful provenance, not an absence of permission; it does
not license every underlying recording, lyric or score.

| Partition | Original basis reported by ChoCo | Intake decision here |
| --- | --- | --- |
| Billboard | CC0 | Original annotation-only source selected |
| Rock Corpus | CC BY 4.0 | Original grant confirmed; converted timing/provenance needs repair |
| Winterreise | CC BY 3.0 | Annotation candidate; overlaps existing D911 family |
| JAAH | CC BY-NC-SA | Excluded from this permissive-source task |
| Chordify subjectivity | CC BY-NC-SA | Excluded |
| Mozart sonatas | CC BY-NC-SA | Excluded |
| Weimar Jazz | ODbL | Quarantined; not treated as BY-only |
| When in Rome | CC BY-SA | Quarantined; not treated as BY-only |
| Isophonics | Unspecified; curator contact reported | Not selected |
| Robbie Williams | Unspecified; curator contact reported | Not selected; original archive link unavailable |
| USpop | Unspecified; curator contact reported | Not selected |
| RWC-Pop | Unspecified in Table 8 | Current annotation archive has NC terms; quarantined |
| Real Book | Unspecified; curator contact reported | Not selected; underlying score rights not inferred |
| Band-in-a-Box | Unspecified; curator contact reported | Not selected |
| Jazz Corpus | Unspecified; curator contact reported | Not selected |
| Wikifonia | Public domain in Table 8 | No blanket PD claim for underlying songs |
| iReal Pro | Public domain in Table 8 | No blanket PD claim for underlying songs |
| Nottingham | Unspecified; curator contact reported | Piece-level rights and timing checks still needed |

The individual original-source checks supporting these decisions include:

- [McGill Billboard](https://ddmal.ca/research/The_McGill_Billboard_Project_(Chord_Analysis_Dataset)/): explicit CC0 annotation grant; original audio cannot be redistributed. Its chart samples contain repeated songs. Internal LAB chord timestamps are interpolated within human-aligned phrases, not all individually hand-timed.
- [Rock Corpus](https://rockcorpus.midside.com/): explicit CC BY 4.0 for the researchers' data, analyses and software, including commercial adaptation. The two annotators disagree on some harmony; alternate analyses are not independent songs.
- [Winterreise v2.1](https://zenodo.org/records/10839767): dataset CC BY 3.0, but recording-specific restrictions must be kept separate. D911 overlaps prior OpenScore materials; another representation or performance is not a new held-out family.
- [Weimar](https://jazzomat.hfm-weimar.de/download/download.html): ODbL data conditions, distinct from software licensing.
- [RWC archive](https://github.com/rwc-music/rwc-annotations-archive): current NC terms cannot simply be replaced by the integration's BY label.
- [Nottingham source](https://abc.sourceforge.net/NMD/): Ashover ownership is specifically identified. A sampled original `playford.abc` also includes modern Mark Knopfler source entries, so its filename is not proof that all compositions are old/public-domain.

## Timing and duplicate audit

The accompanying JSON records nine inspected JAMS files and their exact source
URLs. Findings are limited to those examples and relevant parser code, not a
claim that every ChoCo record is wrong.

- Audio annotations use seconds; symbolic annotations encode measure/beat
  differently across parsers. A decimal position is not a universal elapsed-time
  coordinate or a simple fractional measure.
- Rock examples show a suspected annotator mismatch, compressed empty bars,
  and a beat-10 encoding collision in 12/8. These converted examples are not
  used for fitting here.
- Original/converted and Roman/Harte layers are alternate representations, not
  extra independent examples. Some converted files retain both layers.
- Winterreise score/recording variants belong to the same works. A MusicBrainz
  release ID shared by several tracks is not a unique composition identity.
- The inspected JAMS did not contain note-level melody streams. They cannot
  silently substitute for aligned melody/rhythm training material.

## Decision

Prefer the directly licensed, documented and small Billboard annotation archive
for one bounded chord-event pilot. Keep other partitions out until their specific
rights, transformations and time contracts are reviewed. Do not download audio
or lyrics, do not bypass site restrictions, and do not claim a blanket license
for modern compositions from an annotation dataset's grant.
