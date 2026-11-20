## Summary
Preparation plus thirty-nine documented research cycles, without spacing work by calendar days. Related #2 #3 #4 #7; none closed. Main, PR #6 and live Cantabile projects remain untouched.

- Provenance/quarantine/split preflight with separate composition, arrangement and MIDI contribution evidence.
- Historical three-work diagnostic, then three PD-source works unfitted during cycle 3's frozen transfer probe, explicitly reassigned to exploratory training in cycle 4. No raw corpus, MIDI, audio or weights committed.
- Statistical event baselines, controlled pitch/duration factorization, train-only duration priors and relative-pitch context ablations.
- Strict 4/4 and 6/8 monophonic research reader/writer: exact meter, pitches, note events and EOT, no quantization or silent padding.
- Bounded eight-note interval/rhythm/gap copying guard. Retain failures, sparse outputs, tradeoffs and exact source/experiment hashes.

## Findings
- Original 2-gram overfits: train 157/174 versus known-test 1/52 events.
- Factorization improves known-test duration 8/52 to 27/52, not artistic quality.
- Empirical duration prior changes same-seed onset counts from 10/9/14 to 37/31/32. Typed rest priors can still create long silences.
- Relative pitch improves two new 6/8 works and worsens one. Cycle 3 had no meter-position features; cycle 4 adds optional clock contexts, not validated musical phrasing.
- **Correction retained:** old 70-grid-step match is 68 REST + 2 HOLD, zero onsets, not evidence of a copied melodic phrase.
- Exact MIDI roundtrip now passes on generated candidates. Nine 6/8 eight-bar candidates generated; metrics and hashes reproduce.
- Private neutral A/B previews prepared; no human or perceptual quality/originality assessment claimed.

## Verification
- Final local suite with mido: 370 discovered, 369 passed, one existing actual AudioAnalyzer integration skipped (its environment not configured).
- New meter module: 21 focused tests; all three new source files round-trip without meter conversion, including a partial final bar.
- Separate fixed PR #6 Python music suite: 22 passed. Native neural training was not rerun.
- Uniform-absolute ablation reproduces the prior factorized control NLL in an independent unit test; all probability distributions normalize.
- Source hash, duplicate-screen, repeat-run, compileall and diff checks passed. Remote tree equals locally tested content. Check CI on final head separately.

See experiments/2026-11-12-duration-meter.md plus earlier cycle reports and JSON results. No GPU, paid operation, release, deployment or merge. This is a draft research foundation, not finished musical intelligence.

## Exploratory cycle 4
- Four training works from three conservative source families, explicitly reusing prior transfer-test works. Prior reports remain historical; no fresh held-out claim.
- Clock/bar and fixed four-bar-cycle contexts, plus optional generation-only consecutive-rest mask. Pickup alignment and human phrasing remain unvalidated.
- More source diversity increased output density but worsened known diagnostic NLL; clock contexts improved some diagnostic predictions, not proven attractiveness.
- 120 eight-bar 6/8 candidates, exact MIDI roundtrip and repeat hashes. All 60 rest-capped outputs satisfy the limit. Typed-prior seed 43 long rests 18/24 steps become 11/4 with cap 12.
- Eleven additional model tests pass; complete suite 101 discovered / 100 passed / one existing integration skip.
- Two new Finnish-song sources reserved pending historical composition corroboration, never fitted or model-scored. Unsupported candidates remain quarantined.

See experiments/2026-11-12-position.md and machine-readable results. Exact tested tree verified before branch update; latest CI must be checked separately.

## Cycle 5: phase, shrinkage and Cantabile
- Source-linked pickup correction: Water of Tyne begins at 6/8 phase 10/12, not a downbeat. Explicit per-song origins preserve MIDI timing; true phrase origin still unannotated.
- Count-level position shrinkage, fixed k grid and leave-family-out diagnostics. Exploratory family-macro NLL 5.3706 to 5.1332, with worse training fit and mixed known-dev/test tradeoffs; no sealed generalization claim.
- 30 new candidates reproduce metrics/hashes and exact MIDI timing. Actual pinned Cantabile native CLI imports/exports all 30 byte-identically.
- One earlier private B sample rendered by actual Cantabile FluidSynth worker: 14s PCM16 WAV, zero clipping. Live connected project only read; identity/revision unchanged. No human listening or Windows GUI claim.
- Full suite 106 discovered / 105 passed / one existing integration skip, native codec CTest 1/1. Finnish candidates still pending despite historical catalog corroboration; exact old melody comparison missing.

See experiments/2026-11-12-origin-cantabile.md, source annotation/provenance ledgers and results.

## Cycle 6: form and opt-in listening
- Freeze selected model/controls before new-source scoring. Six new named-composer candidates checked; zero admitted due tempo changes, off-grid/overlapping notes or unresolved license scope. No silent quantization or fresh-test claim.
- Bounded handcrafted A-A′-B-A″ comparator with pitch-range rejection and full-form copy/rest checks across joins. Not learned form or quality selection.
- Three direct/form private audition pairs, analytic sine renderer without sampled sound. All six complete, exact MIDI roundtrip, reproducible MIDI/WAV hashes, zero clipping. One pitch-bound rejection retained.
- Japanese human listening protocol separates coherence, repetition, replay preference, ties/neither, technical failures and missing responses. No human ratings received, no identifiable feedback committed. Method key/media kept private.
- 113 local tests discovered / 112 passed / one existing integration skip. Seven new form tests include actual cross-boundary copy/rest failures.

See experiments/2026-11-12-phrase-listening.md and docs/HUMAN_LISTENING_PROTOCOL.md. Public-release/originality clearance is not claimed.

## Cycle 7: fresh transfer without quantization
- Separate exact-tick reader preserves tempo/CC7/program maps, selected/global EOT and same-tick channel-event order. Original strict reader and frozen model/config hashes unchanged. Explicit pitch/rhythm projection excludes performance controls but preserves originals and full modeled events.
- Two rights-reviewed Schubert works admitted test-only as one correlated composer/edition/typesetter family. No fitting or post-score model selection. Repeat frozen scores reproduce.
- NLL/event equal-work mean: selected 4.637447, position-k0 4.762668, no-position 5.373551. Selected exact top-one counts are lower than k0 on both works; tradeoffs retained. Not musical attractiveness or broad generalization.
- Added bounded interval-edit near-duplicate screen; 28 source pairs have zero exact eight-onset matches and max whole-interval similarity 0.377778. Not perceptual/legal clearance.
- Hypothetical sixteenth rounding would collapse 2/2/6 notes in three excluded sources. No rounded data emitted or scored.
- Real Cantabile native CLI roundtrips both complete original MIDIs byte-identically. No live project mutation or new audio release.
- 131 tests discovered / 130 passed / one existing integration skip. Independent review fixed aggregate output bounds and an off-grid test false positive; admitted-source and model results unchanged.

See experiments/2026-11-12-exact-transfer.md and exact intake/transfer/quantization diagnostics. These new works are now observed and will not be called fresh again.

## Cycle 8: rational time and qualified composer transfer
- Exact rational beat-duration events preserve every note onset, repeated-pitch articulation, rests and note/release velocity. Performance maps remain in original TickMelody. No quantization or rational-duration generator claim.
- Two off-grid sources need 31,488/27,552 minimum dense-grid cells but only 110/120 rational events. Exact note/EOT roundtrip and PPQ invariance verified. Byte formats/cost caveats retained; fractions are not automatically smaller than compact integer ticks.
- Previously unscored Foster370 evaluated with unchanged frozen model: selected NLL 3.832389, k0 4.524361, melodic 4.111161. Exact top-one favors melodic 30/113 over selected17/113. Contributor overlaps train376, so this is composer transfer, NOT independent-contributor validation.
- Bach1534 is a distinct composer/contributor candidate but remains pending explicit new-adaptation attribution; no fitting or scoring. Edition/retrieval failures recorded. No completed new contributor-independent set this cycle.
- 139 tests discovered / 138 passed / one existing integration skip. Repeated reports/canonical hashes and unchanged originals confirmed. Old Schubert test works are not relabeled fresh.

See experiments/2026-11-12-rational-time.md. Human preference and a learned ornament-duration model remain separate unfinished work.

## Cycle 9: exact unknown-duration support
- Fixed PPQ384 support1..12288ticks, positive unseen-duration prior, explicit incompatible/out-of-range rejection. No quantization.
- Predeclared synthetic common-outcome experiment: rational/integer labels have identical probabilities and20 seeded sequences filling eight6/8bars. Not a musical-quality or fresh-corpus result.
- Full suite145 discovered,144 passed,1 existing actual AudioAnalyzer integration skip. Independent review reproduced the report.
- Five source candidates checked; none admitted. Mozart252 source warning prevents assuming unrestricted rights from a PD label. Bach645/Brahms580 expose reader meter/overlap limits. No forced cleanup or test-to-training reuse.
- [Cycle9 report](experiments/2026-11-12-duration-support.md), comparison plan/results and reserved-source ledger committed. No new audio, live Cantabile edits, model/corpus publication or main merge.


## Cycle 10: meter maps and candidate selection
- Separate exact variable-meter profile, frozen reader/models untouched; full modeled-state synthetic roundtrip tests including2/2,3/2 and actual changes.
- Brahms580 composition/edition/contribution rights corroborated against1904 score scan. Still technically quarantined: real overlapping vocal note events remain, no truncation/deletion. Bach645 also blocked by overlaps. No new held-out music score claimed.
- Predeclared20 groups of4 candidates: above-octave leap fraction0.036151 to0.002986, unique pitches14.20 to12.95, repeated-pitch fraction0.222049 to0.247754. Objective reduction is by construction; diversity tradeoffs and4x candidate budget retained, no appeal claim.
- All80 candidates pass exact MIDI roundtrip and narrow copy screen; repeated reports/hashes match.154tests discovered,153pass,1existing integration skip.
- See experiments/2026-11-12-variable-meter-smoothness.md. No main merge, live project mutation, raw MIDI/media publication or human-rating claim.


## Cycle 11: preserve ornament performance and diversity
- Separate overlap-preserving profile:92Brahms580 notes,9meter declarations,maximum3simultaneous notes roundtrip unchanged. Independent raw channel signatures match. No mono truncation.
- Historicalnotation confirms sequential grace ornament, not intended vocalchord. Old-renderer causation remains a hypothesis. Hypothetical clipping would alter4notes/remove334summed gate-ticks; not performed.
- Exact onset-delta/gate diagnostic reconstructs notes; oldmonophonic models remain incompatible. No newsource fitting/predictive scoring.
- Alreadyobserved candidate reanalysis with diversity floors: leapfraction0.036151→0.018694,unique pitches14.20→15.40,repeatedpitchfraction0.222049→0.194814. Objective-defined tradeoff, not human appeal evidence.
- Cornelius583 historicaledition/PDcontribution corroborated; reserve as singlepitch edgecase, groupwith580 bycontributor/publisher. No fresh independentbenchmark claim.
-167tests discovered,166pass,1existing integration skip. Independent actual-source/selection review and repeat reports passed.
- See experiments/2026-11-12-overlap-diversity.md. No mainmerge/liveproject/media release or paid operation.

- Cycle11 bootstrap correction: initial eager optional-mido import broke dependency-free helper tests. Fixed lazy import, retained tests, reran actualsource probe. Full suite167/166pass/1skip; dependency-free167/130pass/37expectedoptional skips. No music metrics changed.


## Cycle12: bounded onset/gate timing models
- Fixed shared151,007,232pair support, sparse joint and factorized priors; training only old4works/364notes. Brahms580 previously representation-inspected, predictively unscored before this cycle, now observed. Sourcefamily and exact/nearinterval screens precede scoring.
-92testevents all in support; timing NLL joint12.599041 vs factorized4.613662. Different prior structure and one-family limitations retained; not directly comparable with old REST/HOLD task NLL.
- Generation joint10/10complete, factorized9/10complete +1explicit boundedfailure.19MIDI outputs exactroundtrip, max3voices/no active samepitchretriggers/end9216ticks independently verified. Uniform trainingpitch support is not a coherent melody model.
- Many overlaps remain: model does not learn previousgate/nextonset dependence or symbolicornament intent. No human appeal claim. No580fit or model reselection.
-174tests discovered,173pass,1existing integration skip; dependencyfree174/137pass/37optional skips. Repeated reports/hashes match. Stricter reviewer0.80 similarity gate vs planned0.90 documented as protocoldeviation, originalplan retained.
- See experiments/2026-11-12-onset-gate.md. Main/liveproject/media release untouched.


## Cycle13: previous gate and pitch continuity factorial
-4conditions share old4trainingworks, supports, budgets and newcontrolsampler. Observed580diagnostic NLL4.613662→3.638074 with previousgate context; NOTfresh generalization.
- Complete counts9/9/8/8 of10. Overlap fraction .390455/.347019/.159433/.168377 amongcompleted; context reduces overlap but worsens completion in thissample. Pitch treatment reducesleaps but reduces distinctpitches and increasesrepetition; initialpitchprior also changes.
- All34completeMIDIs exactroundtrip/end9216/max3activevoices verified. Six failedattempts retained, zero copyguardfailures. Common-success7seed analysis and permetric denominators disclose survivalbias.
- Cornelius583 exacttechnicalroundtrip80singlepitch notes, separate selected/globalEOT retained. Remains reserved/unscored, same580contributor/publisher family.
-181tests discovered,180pass,1existing integration skip; dependencyfree181/144pass/37optional skips. Independent review fixed undefinedinterval summary edgecase; initial model results/MIDIhashes unchanged.
- See experiments/2026-11-12-context-onset-gate.md and prospective private listening design. No humanlabels/mediarelease/mainmerge/liveprojectchanges.


## Cycle14: proposal starvation and joint feasibility
- Exactfailed replay: final64proposals repeatedly staynearzero delta while3notes active; legalcontinuations exist. Pitchonly masking cannotfixthis, so finalsampler conditions timing/gate/pitch jointly without clipping/timeadvance.
- Fixedfactorial: rejection/directconditioning ×uniformpitchmix0/.25. Completion8/8/10/10 of10; rejectedproposals209/160/0/0. Baseline oldnotes/status/rejections exactlyreproduced.
- Cost caveat: fewerproposals but slower implementation, approx0.4s→2.7–3.2s per10seeds forpurecase. No wallclock speedup claim.
-25%mix reducesrepetition/increasespitchvariety but increasesleaps. Pure directsampler also produces moretinyendpointnotes, reported as postinitial diagnostic. Completion isnotmusicquality.
-36completeMIDIs exacttarget/roundtrip/max3voices/noactive samepitch, repeatbytes verified.187tests discovered,186pass,1existing integration skip; dependencyfree187/150pass/37optional skips. Independent finalformula/dataaudit passed.
- See experiments/2026-11-12-feasible-generation.md. No newpredictivebenchmark,sourcefit,publicaudio,mainmerge,liveprojectchange,GPUorfees.


## Cycle15: equivalent optimization and separate ending policy
- Release-boundary legalpitchmass caching preserves integerdelta masses, RNGorder and all20 exactend seeded outputs. Existing cycle14MIDIs byteidentical.
- Paired local10seed timing2.754→.487s and2.997→.538s; repeat2.597→.449 and2.859→.525. Approx5.4–5.8x implementation microbenchmark, not universal/endtoend speedclaim.
- Separate max384tick trailingrest policy preserves notes/EOT9216 but changesstop/outputdistribution. Purecontinuity shortgatecount10→0, mean notes31.4→27.9, actualtail287.2ticks. Fewerpitches/notes and unlearnedcadence remain limitations.
- All4conditions10/10complete;40MIDI safety/roundtrip/hash checks pass.193tests discovered,192pass,1existing integration skip; dependencyfree193/155pass/38optional skips. Independent mass/seed/prefix and dataflow audit passed.
- See experiments/2026-11-12-efficient-ending.md. No fresh source evaluation, humanappeal claim, publicaudio, mainmerge/liveproject changes.


## Cycle16: settling proxy and reserved independent source
- Frozen generator40candidates, shared4/group. Allgenerate, but only5/10groups have eligible long/small-step ending. Other5 explicitnoeligible, noextra retries.
- Matched5groups endpointgate441.6→537.6ticks and finalinterval2.2→.8 byselection, while whole-line octaveleapfraction .022685→.049257. Proxy improvement isnot musicalappeal/tonalcadence. Searchcost/missingdenominators retained.
- Postplan simultaneity concern: nofinalsimultaneousonsets in40files; strictdistinct reanalysis leavesselection unchanged. GeneralAPI limitation disclosed, originalplan notrewritten.
- Adam640/GérardGréco rights and historicGrusincipit corroborated;98noteexactselectedroundtrip. Newcomposer/contributor RESERVEDuntrained/predictiveunscored, futurefamily/similarityscreen needed. No newsourcefit.
-199tests discovered,198pass,1existing integration skip; dependencyfree199/161pass/38optional skips. Repeated40MIDI/metrics match; independent implementation/dataaudit passed.
- See experiments/2026-11-12-settling-ending.md. No humanratings,publicaudio,mainmerge/liveprojectchanges.


## Cycle17: fixed Adam validation and observation record
- Model/support/train/task freeze before predictivecalls; independent13source screen clears Adam640.98/98events scored withoutquantization/dropping; old4train364only.
- Timing NLL joint13.302415,factorized7.435282,previousgatecontext6.351487. Allmodels reported,no retune/refit. One inspected newcomposer/contributor work,not broadgeneralization/musicappeal.
-640 is NOW predictive-observed. datasets/research-source-observations.json supersedes historicalreservedlabel while preserving frozenrightssnapshot. Never callfreshagain; no640training.
- Existingpool endingvariant that prohibitsfinalrepetition reduces selectablegroups5→3 and raisescandidateexaminations28→33. Unequaldenominators, no improvementclaim; localanti-repetition rule doesnotguarantee globallylessrepetition.
-205tests discovered,204pass,1existing integration skip; dependencyfree205/167pass/38optional skips. First/repeatpredictivereports byteidentical, independentcode/dataaudit passed.
- See experiments/2026-11-12-adam-transfer-ending.md. No newmedia,mainmerge/liveprojectchanges,GPU/fees.


## Cycle18: timing prediction versus generated behavior
- Fixed timing-context off/on ablation, identical pitchmix1/4, feasibility and tail384; old4train only. Both10/10complete,20exactMIDIs, zero narrowcopyguard flags. No newpredictive scoring.
- Overlap .383380→.152751 and silence .371875→.171875, but adjacent repetition .190241→.226704. Distinctpitches12.6→13.3, notes28.1→31. Prediction improvement isnot uniformgeneration or musicalappeal improvement.
- Repeat metrics/20MIDIbytes match; contexton also reproduces knowncycle15 outputs. Initialregistryhash differed due historicalobservation backfill only; originalplans retained and difference documented.
- Telemann1692/Perez newfamily rights/1728–1729originalincipit corroborated;192noteexactroundtrip, RESERVEDunfitted/unscored pending similarityscreen.885/268remain pending. No newaudio/humanratings.
-208tests discovered,207pass,1existing integration skip; dependencyfree208/170pass/38expected skips. Remote tree equals tested tree. See experiments/2026-11-12-timing-generation.md and prospective timing-listening design. No mainmerge/liveproject changes/GPU/fees.


## Cycle19: bar recurrence and blocked independent intake
- Reanalyze same20cycle18outputs, no newgeneration: adjacent repetition .190241→.226704 while nonadjacentbar relativepitchsimilarity .301384→.273336. Exactrhythm/fullbar recurrence0both; strict-tick/single-note/emptybar caveats and denominators retained. No appeal or significance claim.
- Telemann1692 freeze saved before predictivecalls;192/192events supported. Exact8interval matches with train888 and observed2245 BLOCK evaluation. Independent26reference review confirms;586unscreenable, no forcedrepair. Commonpatterns are NOTplagiarism proof; thresholdnotrelaxed.
- Actualscoreentrypoint stops beforeoutput/modelconstruction; no1692fit/score/NLL. Immutable rightssnapshot preserved; currentscreenstatus separate. Allmovements/parts remain onefamily.
-215tests discovered,214pass,1existing integration skip; dependencyfree215/177pass/38expected skips. Repeatdescriptor equality verified. See experiments/2026-11-12-bar-recurrence-telemann.md. No newmedia/mainmerge/liveprojectchange/GPU/fees.


## Cycle20: synthetic sensitivity and requested quantity comparison
-15authored synthetic cases expose pitch-only commonpattern collisions, exacttiming1tick sensitivity, time-normalization tradeoffs and short/local/global mismatch. No newthreshold or real-source application; Telemann remains blocked. Synthetictransform labels areNOTplagiarism groundtruth.
- Owner-requested quantity trial: all7subsets of old4works/3families,14tinyfits, observed580/640 only. Equal-subset mean timingNLL1→2→3families: factorized8.660→6.934→6.024; context7.983→6.005→4.995. Content/eventcount/familycount confounded, not large-scale learning or appeal.
- Negative posthocaddition audit: eachmodel worsens equal-workNLL on3/9nestededges. Allsubsetresults retained. Repeats and4full-data historicalNLL values exactlymatch.
- Burgmuller202/214 newcomposer/contributor candidates remain pending exactLitolffedition evidence; no fit/score. Two works sharefamily; uncertainrights notrelaxed.
-222tests discovered,221pass,1existing integration skip; dependencyfree222/184pass/38expected skips. See experiments/2026-11-12-sensitivity-quantity.md. No rawmedia/mainmerge/liveprojectchange/GPU/fees.


## Cycle21: fixed-event budgets, generation and auditions
- Fixed60event originalprefix contrast reducescountconfound but retains content/prefix/workboundary differences. Context equal-workNLL376family5.190,8888897.729,78914.580,balanced3families5.557 onalreadyobserved580/640. Mixing isnotuniversallybest; no causal/freshclaim.
- Separate fullsource singleton3 vsfull,5seeds each:20/20complete/copy0; allMIDI safety/repeat checks pass. Full usesmorepitches but adjacentrepetition exceeds2singletons; vocab and content changealongsidequantity.
-4seed0private12sanalytic-tone WAVs prepared, samegain/tempo, overlap/tailpreserved,0clipping, repeatbytesmatch. Independentreviewer reproduced everyPCM sample. No delivery/humanrating/Cantabile-render claim; media/key private, publicMIDIlinkage omitted.
- Chopin921/Goretzki newfamily rights/historicalScholtz-Petersincipit corroborated, selected92note2/2pickup trackreserved; accompanimentunsupportedcontroller, no fullperformanceclaim. No fit/score/similarityadmission. Burgmuller202/214 stillpending exactedition.
-228tests discovered,227pass,1existing integration skip; dependencyfree228/190pass/38expected skips. See experiments/2026-11-12-fixed-budget-generation.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle22: frozen Chopin transfer and semantic evidence design
-921rights/family and29reference fixedscreen cleared beforepredictivecalls;586 used explicitreadonly paired-noteprojection only, fullreaderrejection retained. No controllerrepair or quarantinedtraining.
-92/92events: timingNLL joint16.873450,factorized9.576718,context8.924260. Old4train364only; fixedmodels/priors, no tuning. Independent report andbefore-score records byteidentical.
-921 is NOW predictive-observed, neverfreshagain, stilluntrained. Observationledger supersedes immutable historicalreservedlabel. One inspectedwork, timingonly, sharedpipeline/editorial caveats, not appeal.
- Posthoc60event coverage shows contentdifferences atfixedcount; traininggenre labels absent, sourcefamily count isnotgenre count. Clementi804newcandidate pendingedition/editor evidence, no fit/score.
- Semanticresearch design separates symbolicfacts, literalhuman intent/perception and modelhypotheses. No inventedlabels, feedback or semantictraining; existing gates unchanged.
-230tests discovered,229pass,1existing integration skip; dependencyfree230/192pass/38expected skips. See experiments/2026-11-12-chopin-transfer-semantics.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle23: fictional semantic evidence and explicit augmentation
- Synthetic-only schema separates observations, fictionalhumanreports and hypotheses; originalwording/proposedtags/provenance/review/use distinct.3valid/2rejected examples, actualhumanreports0, trainingeligible0evenapproved. No semanticmodel/realfeedback claim.
- Rights-reviewed583 explicitlyassigned to exploratorytraining:old4/364→5/444events. Samefamily580 excluded fromevaluation; registrywarns. Only alreadyobserved640/921diagnostics, fixedcrosssplit screen beforefit.
- Moredata worsens timingNLL: factor8.506→8.770,context7.638→7.859.10generatednote arrays complete/copy0; distinct12.2→10,repeat.259→.309,rest.208→.333. Legitimate singlepitchwork isnotbadmusic; quantity/contentconfound, no appealclaim.
- Independent rerun/hashes and safety pass; no MIDI/audio emittedthiscycle, horizoncheck notEOTclaim. Clementi804rights/1893Schirmerincipit nowcorroborated, reservedunfitted/unscored pendingindependentscreen.
-236tests discovered,235pass,1existing integration skip; dependencyfree236/198pass/38expected skips. See experiments/2026-11-12-semantic-prototype-augmentation.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle24: pathway/weighting controls and synthetic-state checks
-2x2addition of583timing/pitch counts:20/20complete/copy0. Repeat fractions neither/pitchonly/timingonly/both .259/.283/.240/.309, showing interactions ratherthan uniformsinglepitch explanation. Neither/both reproducecycle23. TimingNLL onlydepends ontimingpath bytaskdefinition, not proofpitchunimportant.
- Exactweighted-count predictivecontrols: rawcontext7.638→7.859; augmentedtotalmass3647.834; equalworkmass364 old7.877/aug8.113. Equalweight doesnotfixloss here; prior/k4relativecounts andcontent confounds retained. No weightedgenerator or winneradopted.
- Probability normalization/parity and independentrepeats pass. Fractiondenominator externalinput bounds notproductionhardened; fixedsmall researchonly.
-216fictional semanticstate combinations:24schema-valid/192rejected, actualhumanreports0/trainingeligible0. No realfeedback/meaninglabels.
- Clementi804fixedscreen blockedbytrain376 andotherpatterns; rightsremainreviewed, no fit/score or thresholdchange.243tests discovered,242pass,1integration skip; dependencyfree243/205pass/38expected skips. See experiments/2026-11-12-augmentation-pathways-weights.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle25: new-draw robustness and exact fictional binding
- Frozen4conditions×newrecordedseeds100..109:40/40complete/copy0/safety pass, repeatnote bytes match. This is random-draw robustness, NOT independentmusic generalization.
- Interaction contrasts old→new:repeat+.045→+.040,notes−7.8→+1.1,distinct−1.2→−2.0,overlap−.214→−.006. Some directions reverse/shrink; no stableuniversalinteraction or appealclaim.
- Replay audit fixed toexclude only4exactownartifactnames; initialplans/hashes retained, finalcode yieldsidentical40arrays. Models/settings unchanged.
- Syntheticbinding checks exactbytes/segment/clock and soundingunion arithmetic; wording, actor/origin, consent andtraining remainunverified/ineligible. No actualcomments or meaninglabels.
- Mendelssohn1741/RyanPrince historicRietz/Breitkopfincipit+PD reviewed, reservedunscreened;1744/1042pending. No newmusic fitted/scored.249tests discovered,248pass,1integration skip; dependencyfree249/211pass/38expected skips. See experiments/2026-11-12-seed-robustness-evidence.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle26: blocked Mendelssohn and semantic partition hygiene
-1741fixed5condition plan prepared;161/161support/local7screenclear, but independent33reference screen finds exact8matches to580/804. BLOCKED beforemodelconstruction/fit/score; no NLL. Rightsvalidity separate from conservativeadmission.
-879note1042reference fullycompared using declared1024bound with SAMEexactmetric/.80threshold;31sharedcomparisons agree witholdhelper. No deletion/splitting/helperchange, existingflagsremain.1744/1042sameunusedcomposercohort, not independentsamples.
- Fictional semanticpartition audit flags crosssplit family/source/artifact duplicates and contradictorydeclarations;2comments ononeclip count2rows but1artifact/family. Trainingauthorizationfalse, actualfeedback0. Auditonly, not connectedtrainingruntime.
-256tests discovered,255pass,1integration skip; dependencyfree256/218pass/38expected skips. See experiments/2026-11-12-mendelssohn-gate-semantic-splits.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle27: prospective synthetic gate benchmark and expansion review
-80authored cases,10strata ×8variants; persisted plan/code/fixture hashes before scoring. Repeat report byte-identical. Existing exact8/.80gate unchanged; no real-source rescoring or blocked-source release.
-Transpose/time-scale/timing-jitter each8/8flag;3insertions/3deletions/7note excerpts each0/8. Separate common scale/repeat/alternation recipes each8/8collision; random-walk controls0/8. Each commonstratum is ONEcontour with8offsetvariants, not8independentmusicalworks. Construction labels, not population/legal/perceptualerrorrates.
-Review-location/rhythm diagnostics, savedblocked1692/804/1741index and corpus-expansion checklist added. Corpus still5works/444events; no fresh evaluation or humanratings.
-Dvorak2211 officialpinnedsource confirmsManen/Simrock1894/typesetterPD; originalMIDI andhistoricincipit missing, PENDING. Noexecution/conversion/fit/score.
-260tests discovered,259pass,1integration skip; dependencyfree260/222pass/38expectedskips. Compile/diffchecks pass. See experiments/2026-11-12-synthetic-gate-corpus-preparation.md. No mainmerge/publicmedia/liveprojectchange/GPU/fees.


## Cycle28: scalable dataset discovery priority
-Compared8corpus routes with primary-source evidence: PDMX/IMSLP/Mutopia metadata-first for melody, commissioned CC BYGroove for separate rhythm; Lakh unresolveditemrights, MAESTRO/GigaNC/scope issues distinguished from intrinsicAIbans; generatedKeynata upstreamclaims unverified.
-PDMX250K+scorecount is NOTverifiedMIDIcount;31,221licenseconflicts disclosed bymaintainers. No blanketPDadmission.
-Actual boundedprobe:10MutopiaSatiemetadata rows, allpending, onecomposer/pianocohort. Not10independentfamilies or successfuldiversityexpansion. IMSLP/PDMX100rowaudit remainsproposal. No MIDI/audio/scorepayload, fit orscore.
-Stagedintake plan preservesfamily/rights/split/oldblockedstates, separatesmelodyfromdrums and originalMIDIfromfutureconversion. Currenttrainingstill5works/444events.
-Finalsuite260/259pass/1skip, dependencyfree260/222pass/38expectedskips; compile/diffchecks pass. See experiments/2026-11-12-scalable-corpus-survey.md. No mainmerge/publicmedia/GPU/fees.


## Cycle29: actual exploratory corpus growth to9works
-Actual fixed5→8→9work fits,444→1011→1142events.1578/1558/370 explicitly reassigned from observedtests toexploratorytraining; immutablepastresults retained, currentregistryupdated.640/921remainobserved/untrained,580excluded.
-NewHandel98legacyibiblioMIDI+pairedPDsource andChrysanderhistoricalincipit reviewed/used. Joplin263original1394notes alsoacquired/rightsreviewed butreserved above512distancebound; Carcassi pending. Legacyversionsnotclaimedlatestbyteidentity.
-Context timingNLL7.859410→8.434755→8.429055; factor8.769905→9.482052→9.491853. Bothdiagnosticsworse than5workbaseline. No qualityclaim.
-5seeds/corpus: repeatedpitch.309→.231→.196,distinctpitches10→16→15.6,octaveleaps.0125→.0394→.0928. Allcomplete/copy0;15uniqueconditionseeds, not20independentoutputs. Repeatnotes/metricsidenticalexceptCPUtime; base5matchescycle23.
-16/18crosssplit and28/36withintrain comparisonsclear; no oldblockedsourceadmission. Frozen9assignment prose saysFivegroups accidentally; actualgroups/numericcountSIX, correction documentedwithoutrewritingplan. Groupsnotindependentcontributors.
-9originals57,147bytes preserved inlocalZIP38,197bytes, allhashesverified. NOexternalupload or durabilityclaim; sameworkspacebackupcanbelosttogether.
-265tests discovered,264pass,1integration skip; dependencyfree265/227pass/38expectedskips, compile/diffpass. See experiments/2026-11-12-actual-corpus-expansion.md. No mainmerge/publicmedia/GPU/fees.


## Cycle30: full-length Joplin and12work actual comparison
-Predeclared exact2048interval resourceprofile, sameLevenshteinformula/.80andlocalexact8rule, no truncation/approximation. Oldhelper untouched; rollingrows O(minlength), arraysO(n+m), timeO(nm).40random+512boundaryparity; longthreshold/memorytests.
-FullJoplin1394notes added→10works2536events; newlyrightsreviewed originalBeethoven904628notes andTchaikovsky208099notes→12works3263events. PairedPDdedications+historicincipits, reproduction/publisherlimits retained; actualuse separated fromhistoricalreservedledgers.
-12workscreen24cross+66within=90complete,65old-supported exactparity/25longexactcomparisons. No oldblockedsourceadmission, no freshheldout claim.
-ContextNLL5/9/10/12:7.859410/8.429055/8.116754/7.990111. Latestmean betterthan9/10butstillworsethan5; Adamimproves/Chopinworsens vs5.5seeds/corpuscomplete/copy0; repetition falls butoverlap/leapsincrease, noappealclaim.14referenceoutputaudit+repeat/baselineparitypass.
-Owner-authorized separate storagehandoff receivedfixed12originals91,230bytes+16metadataJSON; upload/readbackcompletion NOTclaimedbyresearch. No trainingaudio/newMIDIexport.
-270tests discovered,269pass,1integration skip; dependencyfree270/232pass/38expectedskips, compile/diffpass. See experiments/2026-11-12-long-source-twelve-work-expansion.md. No mainmerge/publicmedia/deployment/GPU/fees.


## Cycle31: exact weighting and private audition prototypes
-Posthoc textureaudit:842/3251adjacenttransitions shareonset;149overoctave sourceintervals allinHandel5/Joplin105/Beethoven39. Eventorderisnotvoiceleading; no causal/appealclaim.
-Same12sources/vocab36, fixedweightednotemass3263, raw/equalwork/equaldeclaredfamily9. Fractioncounts +exactintegerpitchsamplerforALLconditions; rawprobabilityparity butNOToldseedbyteparity. Transitionmasses differ andlocal k4 effectsdisclosed.
-Independentreview caught inheritedlegacy-sampler fractional-gatebug before anyrealfit. Fixedstandalone model rejectsoldroutes; oldunrunplans/failure retained.5tests+87,016tinygate drawpositions checked.
-ContextNLLraw/work/family7.990111/7.886584/7.979924; factor9.055696/9.106083/9.174167. Leap6.66→4.21/4.63,overlap.460→.273/.261,repeat.107→.220/.172. Tradeoffs, notqualityranking.15/15complete/copy0; repeatidenticalexceptCPU,1.92CPU seconds.
-Threepreselectedseed0 opaque12sWAV+8bar6/8MIDIs privatelyprepared, samplewiseaudioverification0clipping. IsolatedCantabileCLIallmessagesroundtripequal,serializationbytesdifferent; no liveproject/UIaudition. No realratings/publicrelease/keyinGit. OriginalteachingMIDI andgeneratedpreviews keptdistinct.
-279tests discovered,278pass,1integration skip; dependencyfree279/240pass/39optional skips; compile/diffpass. See experiments/2026-11-12-weighting-texture-audition.md. No mainmerge/deploy/GPU/fees.


## Cycle32: fourteen pitched works and a separate licensed rhythm reserve
- Added rights-reviewed Czerny2060/2061 originals (191 selected events, 2,778 bytes):14 works /3,454 events. Same Op821/editorial cohort; Ruthardt links2080 and within-training scale matches are retained. Grieg1888/Schumann354 remain excluded pending rights.
- Initial intake-only cap expansion failed after base5 and expanded factorized counts; partial training use/failure is preserved. New14-work context profile leaves frozen12 model unchanged, resets work boundaries, and performs synthetic capability checks before original access. Independent1,800 probability/240 generation checks passed; two standalone-test import issues fixed before retry, old unrun plans retained.
- Final frozen comparison:5 versus14, same observed640/921 diagnostics and fixed copy gates. Context NLL7.859410→8.020197 worsens; repetition.309→.076, leaps3.07→7.03, overlap.132→.356. Both5/5 generation, no fixed copy flags, repeat identical except CPU (.720s),10 private note files byte-identical. No appeal or fresh-generalization claim.
- Projection×weighting2×2 removes842 staff notes, not proven melody extraction. Overlap decreases, but equal-work pitch leaps increase4.21→5.40 and original-staff timing NLL worsens.20/20 safe/complete, repeat verified, original14-reference copy guard unchanged.
- Actual official Google CC BY4.0 Groove MIDI-only ZIP acquired:1,150 drum recordings,1,149 distinct hashes,18 source top-level style labels. All MIDI/CSV/hash inventory checked. Separate UNTRAINED rhythm reserve, not1,150 independent songs or melody additions.9/10 performers and17/25 sessions cross original splits;10 shared evaluation patterns retained. Native PPQ480, no audio. Official hit-count difference818 recorded without adjustment.
- Owner-designated storage transfers use immutable versioned manifests and full read-back verification; do not confuse local inventory with completed storage. No raw MIDI/media in Git.
- Final tests294 discovered/293pass/1existing integration skip; dependency-free294/254pass/40optional skips; compile/diffpass. Main unchanged; no deployment/GPU/fees/public media release. See experiments/2026-11-12-corpus-and-representation-cycle32.md and docs/GROOVE_RHYTHM_RESERVE.md.

- Cycle32 storage follow-through: official Groove ZIP +5 metadata files and2 Czerny originals +14 metadata files all passed size/SHA and full byte read-back (22 artifacts). Versioned latest-state and verification records also reread successfully; existing12 originals unchanged. Current14 pitched training works are distinguished from1,150 untrained drum recordings. No public dataset release.


## Cycle33: performer-grouped drum pilot,16 pitched works, lossless note groups
- Groove is separate from melody:12 complete performances/5,034 events from6 drummers train;4 validation/2,758 events from2 others and4 test/3,850 events from2 others.40 shared-pattern eval recordings remain reserved. Fixed hash selection, no truncated files, native PPQ480 retained.
-12,416 cross-split candidate comparisons: no exact/strong fixed flags,67 weak common-window matches recorded. No exhaustive pattern-independence claim. Original release splits are provenance only; source style/length imbalances and same-tick source ordering retained as confounds.
- Fixed prior1 and previous-instrument empirical count backoff k4: context is WORSE on all8 held-out performances. Pooled NLL validation5.165146→5.462280, test6.353313→6.898952. Repeat exact exceptCPU(.253/.276s), all source hashes unchanged. These8 are now observed;1130 recordings unused, not all1150 trained. No rhythm generation/appeal claim.
- Posthoc frozen-score reconstruction exactly reproduces16 work×condition loss sums. Globally known but locally unseen IOIs account for large penalties (306validation/853test events). No unknown previous-key labels. No parameter or sample changes after seeing results; future backoff/residual-timing experiments remain hypotheses.
- Haydn186/Rameau487 rights/incipits reviewed and added:16 pitched works/4,150 events. Haydn editorial/contributor links and8 within-training pattern links retained; blocked sources remain excluded. Fixed5→16 context timingNLL7.859410→7.368052 improves on ALREADY OBSERVED640/921 only. Leaps/overlap increase; all10 candidates safe/complete/copy0 and repeated note bytes match. Not aesthetic or fresh-generalization evidence.
- New bounded32-work integer-count profile leaves frozen models unchanged; actual16 synthetic preflight before source access. Independent630 exact probability/48 seeded legacy-output parity checks pass, original gates/budgets preserved.
- Lossless selected-note onset view restores all3,454 notes/order/velocities of starting14 corpus from2,610groups. Not melody/voice inference or full MIDI metadata representation; no notes discarded.
-311 tests discovered/310pass/1existing integration skip; dependency-free311/271pass/40optional skips; compile/diffpass. New original and metadata snapshots sent for versioned owner-store read-back; prior storage unchanged. No mainmerge/deployment/publicmedia/GPU/fees. See experiments/2026-11-12-rhythm-pilot-and-sixteen-works.md.

- Cycle33 storage verified:2 new originals +10 pitched metadata files,20 rhythm metadata files +manifest,33 unique artifacts total; every file passed size/SHA and full byte read-back. Versioned latest-state/verification records also verified.16 pitched works and drum12train/8observed/1130unused roles distinguished; originals/history unchanged. A redundant manifest transfer was refused by the no-overwrite guard, and its existing first-copy bytes were verified; no overwrite occurred.


## Cycle34: exact rhythm backoff and intact polyphonic groups
- Same12 drum training /8 ALREADY OBSERVED diagnostics; no new source admission or split change. Six fixed conditions, all reported: exact unigram,k4,k32,k256,exact quotient/residual,contextual quotient/residual. dt=120*q+r preserves all native ticks, including the one-outcome endpoint bucket; not inferred beat phase or expressive microtiming.
- Validation/test pooled NLL: control5.165146/6.353313; k4 5.462280/6.898952; k32 5.261982/6.516660; k256 5.134922/6.291667; q/r5.112428/5.742597; qcontext/r5.049289/5.773584. Extra qcontext improves validation pooled but worsens test and validation macro; k256 worsens one drummer. No universal winner/adoption or appeal claim. Old16 control loss sums exactly reproduce; repeats match exceptCPU(.477/.505s).
-16 pitched works/4150notes form3259distinct-onset groups. Same-outcome groupdelta global versus previous-cardinality context: NLL4.144505→4.799273, both observed diagnostics worse. Do not compare these scores with event-level NLL.
- Whole empirical groups preserve relativepitches/gates/velocities/releasevelocities/memberorder.18/3259occurrences(0.5523%) above3notes remain fitted but generation-ineligible. Both5/5 private candidates complete, copyflags0, exact repeat bytes/template reconstruction and safety checks. No clipping, voice/harmonic labels, new audio or public-release clearance.
- Independent216 drum/1200 group exact probability checks,120 grouped generation safety/repro cases;321 tests discovered/320pass/1existing skip, dependency-free321/281pass/40optional skips; compile/diffpass. Old frozen models/plans remain unchanged; unrun intermediate group plans retained.
- Owner-designated storage COMPLETE:Groove15+group7=22metadata files fully reread with byte/SHA/size equality; latest-state and verification records also reread.16 pitched works and drum12train/8observed/1130unused roles unchanged; originals/history not overwritten. No mainmerge/deploy/GPU/fees.
- See experiments/2026-11-12-backoff-and-group-models.md and the two detailed study reports. Timing prediction, generation feasibility and musical appeal remain separate questions.


## Cycle 35: performer-specific error accounting, group structure and Purcell reserve

- Same Groove12 train/8 already-observed diagnostics/1130 unused. All48 historical recording-condition NLL sums exactly reproduced;192 independent aggregate checks and repeat passed. The large quotient/residual improvement concentrates in drummer9's previously unseen whole intervals assembled from known components; k256 still worsens drummer10, including high-exposure contexts. Full six-condition/drummer/category denominators retained, not a causal genre result.
- New group-structure diagnostics separate simultaneous spans from minimum-pitch-anchor changes and measure rests using all earlier sustained notes. One/two-beat boundary counts differ materially; these are analytic conventions, not inferred phrase/role labels. All10 prior candidates reproduce exact diagnostics;1000 independent occupancy-oracle fixtures pass. No new generation, audio, human rating or semantic labels.
- Purcell2243 rights-reviewed reserve: original1843 Macfarren/Chappell score title and incipit/rests corroborated, anonymous typesetter explicitPD.169 vocal notes, original first onset12672 exceeds current12288 support. **Not fitted/scored or trimmed**; needs prospective support/intake review. Contributor independence not proven. Scarlatti139/141 remain quarantined for unresolved edition/editor rights.
- Coverage-adaptive backoff and nested training-coverage expansion are proposals only, not implemented/scored. Trained pitched count remains16/4150notes/3259groups. New rights-reviewed original is reserve, not a seventeenth training work.
- Final327 tests/326pass/1existing integration skip; dependency-free327/287pass/40optional skips; compileall/diff checks pass. Remote tree matches tested local tree; exact-head Research baseline, Bootstrap and Media policy CI all passed. Versioned LIME archival completed:17 files plus latest-state/verification records, SHA/size/full-byte readback matched. Cycle35 snapshot retains16 trained originals plus Purcell reserve; old history unchanged.
- Overview: `experiments/2026-11-12-performer-and-structure-cycle35.md`. Detailed diagnosis/results/proposals and source-rights ledger linked there. No merge/deploy/release or live Cantabile changes.


## Cycle 36: preserved initial silence and actual dataset expansion

- Pitched corpus now17works/4319notes/3428groups. Purcell2243's12672-tick initial silence and original EOT retained under a separate first-support profile; later/gate12288 and outputtarget9216 unchanged. Six fixed conditions separate16oldcap/16newcap/17newcap, each global/context. Both broader support and source addition worsened observed timing diagnostics (global4.144505→4.153045→4.185509; context4.799273→4.807813→4.852378). Not a music-quality claim.
- Thirty grouped candidates all completed, exact byte repeat, limited copying flags0. Old10 reproduce Cycle34 bytes. Independent field/active-note checks and1000 synthetic probability/mass checks pass.16new/17new first distributions conditional on finite target are exactly equal; unconditioned outside-target mass grows10.9375%→15.8854%. No long source rest was shortened.
- Groove increased from12/5034events to35 unique recordings/19409events, within unchanged six training drummers.36 candidate records included one exact duplicate; retained baseline/lowest-ID identity, excluded alias with no replacement.23024 fixed cross comparisons,strong0/weak138. Heldout8 remain already observed/untrained;1107not fitted=40reserved+1excludedalias+1066other.
- Same six estimators: pooled test unigram6.353313→6.242511 and k4 context6.898952→6.596587 improve; quotient/residual5.742597→5.819849 and contextual quotient5.773584→5.794152 worsen. Performer-specific signs vary. Content/style/duration/quantity confounded, no fresh generalization.
- Before-fit clearance-schema rejection2attempts preserved, corrected using same approved scope/plan. All12 actual constructors journaled,48 historical baseline scores exact, repeat identical exceptCPU, source bytes unchanged. No raw source/media or generated notes committed.
- Final346tests/345pass/1existing skip; dependency-free346/306pass/40expected skips,compile/diffpass. Tested local tree matches remote. Versioned Cycle36 LIME archival completed:37 metadata files plus latest-state/verification records, SHA/size/full-byte readback matched. Original17 MIDI files and Groove ZIP/history unchanged. Exact-head Research baseline, Bootstrap and Media policy CI all passed.
- Overview `experiments/2026-11-12-silence-and-coverage-cycle36.md`; details `2026-11-12-initial-rest-comparison.md` and `2026-11-12-groove-cycle36-coverage-results.md`. No merge/deploy/release, no live Cantabile changes or new audio.


## Cycle 37: sounding history, exact probability accounting and prospective new recordings

- Old Groove12/35 ×6 conditions:96 historical recording NLL sums exactly reproduced. Fixed support separates281old-known/86new-known/30354still-unseen intervals. Fixed unigram prior1 means remaining unseen events incur+1.349375nats after corpus expansion. Quotient/residual mass sharing behaves differently; component familiarity does not guarantee better exact-outcome probability. All per-drummer losses/masses retained; new smoothing-ratio idea remains unimplemented.
- Pitched17-source four-arm comparison: same supports, first law, templates, copying guard and fixed duration bins. Group-delta NLL global4.185509/cardinality4.852378/previous-max-gate3.714385/active-horizon3.747764. History is past-only, rejected proposals do not advance it. Twenty candidates complete/byte-repeat/copyflags0; old10 match Cycle36. Duration context improves already-observed prediction, while horizon changes silence structure, not proven musical appeal. Independent probability/generation/occupancy checks pass. Prefit class-contract issue fixed before real fitting and preserved in correction record.
- Separate prospective probe froze8 unscored recordings/4779events from heldout drummers7–10 before prediction, with identity/byte exclusions and independent review.8872screen comparisons,strong0/weak92. Same12/35×6 models, no tuning: every pooled and recording-macro split improves with35 here (test unigram8.009007→7.444297; q/r6.352690→6.337867), but several drummer9 subsets worsen. Prior negative results retained. New recordings are NOT new performers or representative genre samples.
- New8 now observed/untrained forever: current Groove35train/16observed-untrained/1099unscored-untrained=40reserved+1excludedalias+1058other. Pitched17/4319notes/3428groups unchanged. Probe12construction/96prediction journals and repeats verified; source originals unchanged. No new drum generation/audio, no human ratings.
- Final359tests/358pass/1existing skip; dependency-free359/319pass/40optional skips;compile/diffpass. Remote tree matches tested local tree. Exact-head Research baseline/Bootstrap/Media policy CI all passed. Cycle37 LIME32 metadata files plus latest-state/verification records fully saved with SHA/size/full-byte readback matched. Original MIDI/ZIP and previous ledgers preserved; no merge/release/deployment/live project changes.
- Overview `experiments/2026-11-12-history-and-fresh-probe-cycle37.md`; detailed loss/mass analysis, gate-context comparison and fresh-recording probe include all denominators, failures, plans and role transitions.


## Cycle 38: private listening artifacts and cohort-dependent effects

- Four fixed seed0 candidates from Cycle37 exported as opaque A–D MIDI/WAV outside Git. Selection was deterministic after prior numerical results, not a pre-generation preregistration or listening-selected winner. All5note fields/same-tick order/PPQ384/tempo120/6-8/EOT9216 preserved; isolated Cantabile CLI roundtrips pass despite serialization-byte differences. No live project or claimed human listening.
- Own analytic oscillator, common gain/velocity policy, declared release-envelope convention,12s/22.05kHz/16bit mono. No SoundFont, per-file normalization or clipping; peak<.473,RMS−23.679..−20.573dBFS. Repeated WAV bytes match. Independent direct MIDI pairing and actualPCM readback confirm fields/format/quantization-tolerant statistics. Listening packet excludes method key/technical reports; actual delivery belongs to root and human ratings remain unrecorded here.
- Optional-mido portability failure discovered in one new test, fixed with availability skip only. Historical test/hash/diff and run preserved. New portableplan8ab74… re-rendered all8media files byte-identically, without changing renderer/sources/labelkey/oldmanifest. Actual artifacts unaffected; no media in Git.
- Blank human-feedback template and neutral protocol permit ties/dislikes/cannotjudge, separating observed facts, actual comments and hypotheses; no invented ratings or automatic training labels. Separate LIME audition folders marked generated-private/listening-only/not-training; correspondence key archived separately, not in listener packet.
- Groove saved-score-only analysis, no MIDI reads/fit/new scores: same4drummers×6conditions gives9pooled and8macro cohort sign reversals among24 comparisons. Some pooled improvements accompany macro deterioration. Old/new recording cohorts are all observed, not16independent people; content/event-support/length confounds retained.35train/16observed/1099unscored and pitched17/4319/3428 unchanged.
- Final364tests/363pass/1existing integration skip; dependency-free364/323pass/41optional skips;compile/diffpass. Remote tree matches tested local tree. LIME28files plus latest-state/verification fully saved with SHA/size/full-byte readback, original corpus/history unchanged. Exact-head Research baseline/Bootstrap/Media policy CI all passed; no merge/release/deploy.
- Overview `experiments/2026-11-12-listening-and-cohort-effects-cycle38.md`; audition verification/portability records, listener protocol and full cohort comparisons retain limitations and all denominators.


## Cycle39: fixed rhythm coverage expansion and Dowland reserve
- Actually expanded Groove35→58 unique recordings,19409→32141events;23 newly trained sources, same6train drummers and16already observed diagnostics. Prior35 retained, known byte alias excluded without replacement, all40eval-session recordings remain reserved. Fixed40302cross-split checks had no strong unresolved match. Separate60work/60000event profile leaves historical limits/formulas unchanged.
- All6conditions improved test pooled NLL; validation quotient/residual2conditions slightly worsened, including drummer8. Event share of drummer5 rose37.78→44.81%; provided style labels12→19 are not independent verified genres. Count/content/length confounds and reused evaluation prohibit causal-volume or musical-quality claims.96old scores reproduce exactly;repeat matches except CPU;independent selection,576probability parity and276result checks pass.
- Two Dowland Cantus sources89+43notes reviewed against1597first-book and contributor's explicit legacyPD dedication, originalSATB retained.45fixed similarity comparisons flag0. Samebook/contributor cohort, reserved NOT fitted or predictively scored. No raw MIDI/audio/LY committed.
- Final370tests/369pass/1existing skip;dependency-free370/329pass/41expected skips;compile/diff pass. HumanA–D ratings remain unanswered; no new generation or live-project action. Exact-head Bootstrap/Research/Media CI all passed. LIME archival COMPLETE:32files (Groove24 + Dowland2MIDI/2LY/4JSON) plus latest-state/verification records passed SHA/size/full-byte readback.19originals127961bytes retain17train/2reserve distinction; old originals/ZIP/history unchanged.
- Overview: `experiments/2026-11-12-coverage-and-dowland-reserve-cycle39.md`; detailed rhythm report `experiments/2026-11-12-groove-cycle39-coverage-overview.md`. Current Groove58train/16observed/1076unscored; pitched17training plus2reserved.
