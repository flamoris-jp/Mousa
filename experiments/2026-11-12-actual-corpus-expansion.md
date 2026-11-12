# Cycle29: actual five-to-eight-to-nine-work expansion

## What changed

The corpus was actually fitted at5works/444events,8works/1011events and9works/
1142events, using the same factorized and previous-gate-context(k4) timing models.
This is still small-scale exploratory research, not large-corpus generalization.
Each source retains its own sequence boundary and exact timing. No quantization,
truncation, lyric use, score execution or hidden track repair occurred.

The8work condition explicitly reassigns previously observed Schubert1578/1558
and Foster370 to exploratory training. Explicit research authorization for this reassignment
was obtained before fitting. Immutable earlier test results remain untouched;
they are not evaluation results for these newly trained models. The current
observation registry now records actual training use. Adam640andChopin921remain
untrained, previously observed diagnostic works, not fresh held-out evidence.
Brahms580remains excluded because of its relation to training583.

The9work condition adds a newly acquired131-event Handel98keyboardstaff. It has
chords and is not an isolated monophonic melody. Same5work baseline, same seeds,
same model configuration and same diagnostics permit descriptive comparison
with8works. The5work predictions and private generated-note bytes reproduce the
old cycle23baseline. Quantity, content, meter mixture and pitch vocabulary change
together; this is not a causal estimate of sample size alone.

## Source acquisition and rights

Official Mutopia and several mirror requests failed503. A verified legacy
ibiblio Mutopia route supplied original MIDI and matching old LilyPond files for
Handel98/DavidMaddock and Joplin263/ChrisSawer. Both old source files contain
explicit typesetter Public Domain dedication. Historical score incipits were
visually checked separately: Handel/Chrysander H.W.2printed150 and Joplin1902
Stark plate10-4. Modern reprint dates are not treated as new original editions.

The fetched legacy versions differ from current GitHub source hashes. Their
exact origins and byte hashes are retained; no latest-version identity is
claimed. Handel's1858catalogue versus1859source date is disclosed. Incipit review
is not full note-for-note collation. No old/new version is an independent work.
The immutable rights snapshot is `research-new-cohorts-cycle29-20261112.json`;
Handel's subsequent actual use is recorded in a separate training-use ledger.

Joplin's1394-note selected staff is readable and rights-reviewed but remains
reserved, not fitted/scored: it exceeds the current512-interval comparison bound.
Do not crop it to evade a bound or treat an incomplete comparison as zero.
Carcassi2209remains pending because its editor and original acquisition are
unresolved. Total new acquisition is2original MIDI files, but only1entered
training. Acquisition is not synonymous with admission.

## Fixed protocol and screening

Each assignment and plan was persisted before its fitting. A separate actual
review decision binds plan, assignment and screen hashes. JSON review flags are
not themselves permission. The unchanged exact-eight-onset / global0.80 gate
cleared16train-diagnostic comparisons for8works and18for9works; all events fit
fixed timing support. Within-training28and36pair comparisons respectively
reported no exact8or0.80flags. Shared edition/contributor cohorts remain grouped
regardless of these numeric results. Old blocked1692/804/1741were not admitted.

Correction to a frozen descriptive string: the9work assignment's
`family_interpretation` accidentally retains “Five” from8works. Its actual
`family_groups` and numeric `expected.conservative_families` correctly specify
SIXgroups. The frozen assignment is not rewritten. Neither five nor six groups
means that many independent contributors: NigelHolmes is shared across two
edition groups and StanSanderson links376/370. Added6/8sources do not make the
unchanged model meter-aware. This correction has no computational effect.

## Results: prediction worsened despite more training material

Lower timing NLL is better for this specific prediction task.

| Works / events | Factorized equal-work NLL | Context equal-work NLL |
| --- | ---: | ---: |
| 5 /444 | 8.769905 | 7.859410 |
| 8 /1011 | 9.482052 | 8.434755 |
| 9 /1142 | 9.491853 | 8.429055 |

Both diagnostics worsen relative to5works under both models. Adding Handel to
8works slightly improves the context equal-work mean, but worsens Adam640while
improving Chopin921. That mixed result is not a general improvement claim.
No additional evaluation piece or human rating was used to select a model.

For each corpus size,5fixed seeds0–4produce complete9216-tick note proposals:

| Works | Mean notes | Distinct pitches | Same-pitch repetition | Rest fraction | Over-octave interval fraction |
| --- | ---: | ---: | ---: | ---: | ---: |
| 5 | 23.2 | 10.0 | 0.309123 | 0.333333 | 0.012500 |
| 8 | 29.8 | 16.0 | 0.231072 | 0.134679 | 0.039388 |
| 9 | 29.4 | 15.6 | 0.195759 | 0.137500 | 0.092845 |

Lower repetition and more pitch variety coexist with worse timing likelihood
and more large leaps. None establishes greater musical appeal. The5work output
is repeated across the two comparisons, so this is15unique condition-seed
outputs, not20independent generated samples. Copy checks use all assigned
training plus both diagnostic works in each experiment; all reported matches0.
This finite check is not originality clearance. Symbolic proposals remain private
JSON; no new MIDI EOT, Cantabile listening or human preference result is claimed.

Repeated runs match all predictions, metrics and private note bytes; only measured
CPU time differs. Each run stays within its60secondCPU budget. This budget is
checked before bounded calls, not a hard OS preemption guarantee. Failed/skipped
runs would be reported rather than silently retried; none occurred here.

## Preservation and next issue

A private local recovery archive contains9original MIDI files totaling57,147bytes,
plus source/assignment ledgers. Every extracted source hash matches the original.
The ZIP is38,197bytes. It is outside Git and has NOTbeen uploaded or shared.
Because it is in the same research workspace, it is not a durable external backup.
An approved persistent private destination is a separate step; GitHub stores
provenance, code and metrics, not raw MIDI or media.

Actual expansion succeeded, but the previously identified time/pitch mixture
problem persists. Next comparisons should distinguish source weighting and
instrument/texture heterogeneity without retuning on these two observed
measurements. Large-dataset metadata discovery remains useful; this cycle's
nine works do not fulfill a large, culturally diverse corpus goal.

## Final verification

Fullsuite265discovered,264passed,1existing actualAudioAnalyzer integration skip.
Dependency-free265discovered,227passed,38expected optional skips. Compileall and
diff checks pass. Independent9work audit recomputed all11reference copy sets and
all10output safety checks, verified source counts and repeat/baseline parity.
Historical source result hashes remain intact. No main merge, deployment,
external raw-data upload, paid computation or GPU use.
