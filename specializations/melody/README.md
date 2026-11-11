# Mousa Melody

Mousa Melody researches bounded melody suggestions, motif development, phrases and variation. Models propose notes; they do not gain authority to edit a Cantabile project or call tools.

## Implemented research slice

[grid_v1](grid_v1/README.md) migrates the recovered Maidionis Music Trial 001 into this repository while keeping Maidionis Core external and pinned. It includes curated MIDI preparation, a native 16,667-parameter next-token model composition, training and checkpoint load, comparison against simple baselines, MIDI output and neutral previews.

Its immutable experimental task ID remains `research.music-next-token` version `1`; moving code into Mousa does not silently change model semantics. It is an unadmitted offline research checkpoint, not a deployable Runtime model.

## Important limits

The task sees only eight sixteenth-grid symbols plus a bar position, uses one training work, and does not learn a full song or artistic value. Evaluate note onsets separately from HOLD/REST and preserve failure evidence. Preference learning belongs to a separate Critic task; Runtime coordination and Cantabile editing are not implemented here.
