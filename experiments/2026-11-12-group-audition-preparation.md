# Cycle38: private listening candidates, no ratings yet

Four existing Cycle37 candidates, seed0 from each arm, were exported without changing their original note data. Seed0 was fixed deterministically after the experiment results existed, not preregistered before generation and not selected by listening or numerical score. The opaque label mapping and shuffle seed remain private, outside Git and the storage snapshot.

The old exporter inserted velocity80/release0 and its renderer ignored velocities, so a separate exporter was implemented. All five fields (start,end,pitch,velocity,release_velocity), modeled same-tick event order, PPQ384,120BPM,6/8 and EOT9216 passed internal and isolated Cantabile CLI roundtrip checks for all four files. Cantabile's output MIDI bytes differ because of serialization; the checked note/performance fields, event order and timeline do not. No live Cantabile project was touched, and this is not a claim that anyone heard playback on a device.

The common analytic oscillator is0.8fundamental sine+0.2second harmonic, with gain0.18×velocity/127. It uses no recordings or SoundFont. Release velocity controls a declared simple in-gate5–35ms ramp, not a claim about standard real-instrument behavior. Gate endpoints remain exact in MIDI; PCM endpoints round to the common sample grid within0.5sample. The export's eight bars of6/8 at120BPM are a presentation convention, not learned meter.

All four WAVs are12seconds,mono22.05kHz16bit PCM. There is no per-file normalization. Peak is below0.473 and clipping count is0. RMS spans approximately−23.679 to−20.573dBFS, so density/velocity-related loudness differences have deliberately not been hidden. Repeated rendering was byte-identical for each clip. These are private analytic previews, not finished instruments or public-release-cleared music.

Final code-bound plan SHA: `5eee4c832dc05d246cf380f6e37228f18e927ae69d9bc971a9221f2ea4775cf8`.

See the final plan, verification and storage manifest with prefix `2026-11-12-group-audition-`. No raw MIDI/audio, generated source JSON, or label key is in Git. The separate storage snapshot contains4MID,4WAV and technical metadata only, explicitly generated-private/listening-only/not-training. Transfer is delegated to the storage worker; this preparation document does not claim it has completed. Technical verification metadata is not the blind listener packet. Human ratings remain blank; none were invented.
