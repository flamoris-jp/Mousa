"""Fixed-protocol progression audition. No fitting, rerolls, or imported melodies.

Run with PYTHONPATH=src. Audio is optional and must stay outside any Git checkout.
The identical self-authored C-major arpeggio in all arms is NOT an AI melody.
"""
import argparse
import array
import hashlib
import json
import math
import os
from pathlib import Path
import random
import selectors
import struct
import subprocess
import wave
import zipfile

from mousa.degrees import Degree
from mousa.harmony import Chord, Progression, TRIADS, SEVENTHS, resolve_progression
from mousa.scale_midi import _meta, _vlq
from mousa.scales import Key, ScaleCondition, load_catalogue

CONTEXT = [0, 4, 5, 3] * 2
SEEDS = (17, 29, 43)
TASK_CONTEXTS = {
    "mousa.major-progression.weak-label.experimental.v1": 8,
    "mousa.major-progression-local2.weak-label.experimental.v1": 2,
}
MELODY = (72, 76, 79, 76, 72, 76, 79, 76)


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sample(probabilities, rng):
    if len(probabilities) != 14 or any(type(p) not in (int, float) or not math.isfinite(p) or p < 0 for p in probabilities):
        raise ValueError('invalid probability vector')
    total = sum(probabilities)
    if not math.isclose(total, 1, abs_tol=1e-5):
        raise ValueError('probabilities must sum to one')
    u = rng.random() * total
    cumulative = 0
    for label, probability in enumerate(probabilities):
        cumulative += probability
        if u < cumulative:
            return label
    raise ValueError('invalid cumulative probabilities')


def model_context(manifest):
    task = manifest.get('task_id')
    if task not in TASK_CONTEXTS:
        raise ValueError('unsupported model task')
    expected = TASK_CONTEXTS[task]
    if type(manifest.get('context_length')) is not int or manifest['context_length'] != expected:
        raise ValueError('model context_length/task mismatch')
    return expected


def generate(query, seed, context_length=8):
    if type(context_length) is not int or context_length not in (2, 8):
        raise ValueError('unsupported context length')
    history = list(CONTEXT)
    rng = random.Random(seed)
    trace = []
    for step in range(8):
        row = {'input': [1] + [v + 2 for v in history[-context_length:]], 'label': 0,
               'family': 'audition:independent-context', 'index': 8 + step}
        probabilities = query(row)
        label = sample(probabilities, rng)
        trace.append({'input': row['input'], 'probabilities': probabilities, 'label': label})
        history.append(label)
    return history[8:], trace


def render(labels):
    if len(labels) != 8 or any(type(x) is not int or not 0 <= x < 14 for x in labels):
        raise ValueError('eight labels 0..13 required')
    progression = Progression(tuple(Chord(Degree(x % 7), (SEVENTHS if x >= 7 else TRIADS)[x % 7], 1920) for x in labels), 8)
    condition = ScaleCondition(load_catalogue()['major_12tet'], Key.from_name('C3'))
    rows = resolve_progression(progression, condition)
    events = [(0, -2, _meta(81, (600000).to_bytes(3, 'big'))),
              (0, -2, _meta(88, bytes((4, 2, 24, 8)))),
              (0, -2, _meta(89, bytes((0, 0)))),
              (0, -1, bytes((192, 0))), (0, -1, bytes((193, 0)))]
    for bar, row in enumerate(rows):
        for note in row['midi_notes']:
            events.extend(((bar * 1920, 1, bytes((144, note, 48))),
                           ((bar + 1) * 1920, 0, bytes((128, note, 0)))))
        for slot, note in enumerate(MELODY):
            start = bar * 1920 + slot * 240
            events.extend(((start, 1, bytes((145, note, 80))),
                           (start + 240, 0, bytes((129, note, 0)))))
    track = bytearray()
    last = 0
    for tick, _, content in sorted(events, key=lambda e: (e[0], e[1])):
        track.extend(_vlq(tick - last) + content)
        last = tick
    track.extend(_vlq(15360 - last) + _meta(47, b''))
    midi = b'MThd' + struct.pack('>IHHH', 6, 0, 1, 480) + b'MTrk' + struct.pack('>I', len(track)) + track
    return midi, progression.to_dict()


def train_matches(labels, data):
    matches = []
    for row in data['train']:
        previous = [x - 2 for x in row['input'][1:]]
        if len(previous) != 8:
            raise ValueError('training context width')
        for offset, candidate in ((-8, previous), (-7, previous[1:] + [row['label']])):
            if candidate == labels:
                matches.append({'family': row['family'], 'start_index': row['index'] + offset})
    return sorted({(x['family'], x['start_index']) for x in matches})



def match_diagnostic(labels, data, context_length):
    if context_length == 8:
        return {'eight_chord_exact_check_performed': True,
                'train_eight_chord_exact_matches': train_matches(labels, data),
                'caveat': 'Only stored train windows checked; absence is not an originality or non-memorization guarantee.'}
    if context_length != 2:
        raise ValueError('unsupported context length')
    trigrams = set()
    for row in data['train']:
        inputs = row['input']
        if len(inputs) != 3 or inputs[0] != 1 or any(type(x) is not int or not 2 <= x <= 15 for x in inputs[1:]) or type(row['label']) is not int or not 0 <= row['label'] < 14:
            raise ValueError('invalid local2 training row')
        trigrams.add(tuple([x - 2 for x in inputs[1:]] + [row['label']]))
    windows = [tuple(labels[i:i+3]) for i in range(len(labels)-2)]
    matches = [window in trigrams for window in windows]
    return {'eight_chord_exact_check_performed': False,
            'eight_chord_check_reason': 'Eight consecutive training chords cannot be reconstructed reliably from the local2 training JSON alone.',
            'limited_trigram_diagnostic': {'scope': 'six windows wholly within the played eight chords; seed context excluded',
                'windows': [list(window) for window in windows], 'matched': matches,
                'matched_count': sum(matches), 'window_count': len(windows),
                'match_rate': sum(matches) / len(windows) if windows else None},
            'caveat': 'Limited local-pattern overlap only; not an originality or non-memorization guarantee.'}


def call(args):
    return subprocess.run(list(map(str, args)), check=True, capture_output=True, text=True, timeout=90).stdout


def audio(out, names, args):
    import mido  # optional verification dependency; no installation side effects
    prepared = []
    for name in names:
        midi = out / (name + '.mid')
        project = out / (name + '.cantabile.json')
        roundtrip = out / (name + '-roundtrip.mid')
        wav = out / (name + '-raw.wav')
        call([args.cantabile_cli, 'import-midi', midi, project])
        call([args.cantabile_cli, 'validate', project])
        call([args.cantabile_cli, 'export-midi', project, roundtrip])
        if mido.MidiFile(midi).tracks != mido.MidiFile(roundtrip).tracks:
            raise ValueError('MIDI message roundtrip mismatch')
        call([args.renderer, '--midi', roundtrip, '--soundfont', args.soundfont, '--output', wav,
              '--sample-rate', '48000', '--tail-seconds', '2', '--max-seconds', '30'])
        with wave.open(str(wav), 'rb') as w:
            params = w.getparams()
            if params.sampwidth != 2 or params.comptype != 'NONE':
                raise ValueError('expected PCM16 audio')
            pcm = array.array('h', w.readframes(w.getnframes()))
            if os.sys.byteorder != 'little':
                pcm.byteswap()
        if not pcm or max(map(abs, pcm)) == 0:
            raise ValueError('empty or silent audio')
        prepared.append((name, params, pcm))
    gain = min(12, 28000 / max(max(map(abs, p)) for _, _, p in prepared))
    reports = []
    for name, params, pcm in prepared:
        peak_before = max(map(abs, pcm))
        adjusted = array.array('h', (round(x * gain) for x in pcm))
        peak_after = max(map(abs, adjusted))
        if peak_before >= 32767 or peak_after >= 32767:
            raise ValueError('audio clipping detected')
        if os.sys.byteorder != 'little':
            adjusted.byteswap()
        wav = out / (name + '.wav')
        with wave.open(str(wav), 'wb') as w:
            w.setparams(params)
            w.writeframes(adjusted.tobytes())
        mp3 = out / (name + '.mp3')
        call([args.ffmpeg, '-v', 'error', '-n', '-i', wav, '-b:a', '160k', mp3])
        reports.append({'name': name, 'common_gain': gain, 'seconds': params.nframes / params.framerate,
                        'pcm_peak_before': peak_before, 'pcm_peak_after': peak_after,
                        'midi_message_roundtrip_exact': True, 'mp3_sha256': digest(mp3)})
    return reports


def readme(context_length):
    if context_length == 2:
        conditioning = 'local2モデルへの初期入力は固定進行 I-V-vi-IV×2 の末尾2コード（vi-IV）のみ。以降も直前2コードだけを参照して8コードを生成し、生成部分だけ再生。再抽選なし。'
        matching = 'generation.json 内の照合は3連続コードの限定的な一致率のみ。8連続の独立した照合については別監査の報告を参照。'
    elif context_length == 8:
        conditioning = 'モデルへの初期入力は固定進行 I-V-vi-IV×2 の8コード。以降も直前8コードを参照して8コードを追加生成し、追加部分だけ再生。再抽選なし。'
        matching = 'generation.json 内の照合は保存済み学習窓との8連続完全一致検査のみ。独創性や非記憶の保証ではありません。'
    else:
        raise ValueError('unsupported context length')
    return ('Mousa コード進行学習の試聴実験\n'
            '固定 I-V-vi-IV×2 と AI seed 17/29/43。各8小節、C major、100 BPM。\n'
            + conditioning + '\n'
            '旋律は全例同一の自作固定アルペジオ。AI生成の旋律ではありません。原曲旋律・歌詞は含みません。\n'
            '弱教師コード解析は人手の正解ではありません。自然さ・汎化・独創性は未保証。\n'
            + matching + '\n')


def output_in_git_worktree(output):
    """Inspect the nearest existing directory, not incidental .git markers.

    Runtime placeholder markers are not necessarily repositories. git itself
    resolves real worktrees, including worktree .git files and parent roots.
    """
    current = Path(output).resolve()
    while not current.exists():
        if current == current.parent:
            raise ValueError('no existing output ancestor')
        current = current.parent
    if not current.is_dir():
        raise ValueError('output ancestor is not a directory')
    # Do not let inherited Git overrides redirect this local worktree check.
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    result = subprocess.run(['git', '-C', str(current), 'rev-parse', '--show-toplevel'],
                            capture_output=True, text=True, timeout=10, env=env)
    if result.returncode == 0:
        return True
    if result.returncode == 128 and 'not a git repository' in result.stderr.lower():
        return False
    raise RuntimeError('Git worktree check failed: ' + result.stderr.strip())


def main():
    p = argparse.ArgumentParser(description=__doc__)
    for arg in ('executable', 'model', 'data', 'output'):
        p.add_argument('--' + arg, required=True, type=Path)
    for arg in ('cantabile-cli', 'renderer', 'soundfont'):
        p.add_argument('--' + arg, type=Path)
    p.add_argument('--ffmpeg', default='ffmpeg')
    args = p.parse_args()
    wants_audio = any((args.cantabile_cli, args.renderer, args.soundfont))
    if wants_audio and not all((args.cantabile_cli, args.renderer, args.soundfont)):
        p.error('audio requires all three: --cantabile-cli --renderer --soundfont')
    out = args.output.resolve()
    if output_in_git_worktree(out):
        p.error('output must be outside Git')
    data = json.loads(args.data.read_text())
    manifest = json.loads((args.model / 'manifest.json').read_text())
    context_length = model_context(manifest)
    if data.get('task_id') != manifest['task_id']:
        raise ValueError('model/data task mismatch')
    if manifest['data_sha256'] != digest(args.data):
        raise ValueError('model/data digest mismatch')
    out.mkdir(parents=True, exist_ok=False)
    report = {'schema': 'mousa.progression-audition.experimental.v1', 'model_manifest_sha256': digest(args.model / 'manifest.json'),
              'data_sha256': digest(args.data), 'task_id': manifest['task_id'], 'context_length': context_length, 'initial_model_context': CONTEXT[-context_length:], 'context': CONTEXT, 'seeds': SEEDS, 'temperature': 1,
              'sampling': 'Python random.Random cumulative categorical, no reroll', 'bpm': 100, 'bars': 8,
              'melody': 'Identical self-authored fixed C-major arpeggio in every arm, NOT AI-generated',
              'melody_midi_notes_per_bar': MELODY, 'human_listening': False, 'arms': []}
    with subprocess.Popen([str(args.executable.resolve()), 'serve', str(args.model.resolve())], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=out.joinpath('serve.stderr.txt').open('w'), text=True) as proc:
        selector = selectors.DefaultSelector()
        selector.register(proc.stdout, selectors.EVENT_READ)
        def query(row):
            proc.stdin.write(json.dumps([row]) + '\n'); proc.stdin.flush()
            if not selector.select(30):
                proc.kill(); raise TimeoutError('model query timeout')
            answer = json.loads(proc.stdout.readline())
            return answer[0]['probabilities']
        try:
            arms = [('fixed', list(CONTEXT), [])]
            for seed in SEEDS:
                labels, trace = generate(query, seed, context_length)
                arms.append((f'ai-seed-{seed}', labels, trace))
        finally:
            selector.close()
            proc.stdin.close()
            try: proc.wait(timeout=10)
            except subprocess.TimeoutExpired: proc.kill(); proc.wait(); raise
        if proc.returncode:
            raise RuntimeError('model server failed; see serve.stderr.txt')
    for name, labels, trace in arms:
        midi, progression = render(labels)
        (out / (name + '.mid')).write_bytes(midi)
        report['arms'].append({'name': name, 'labels': labels, 'progression': progression, 'trace': trace,
                               'matching_diagnostic': match_diagnostic(labels, data, context_length),
                               'midi_sha256': hashlib.sha256(midi).hexdigest()})
    report['match_caveat'] = 'Local2: no eight-chord copy check; only limited trigram overlap. Context8: stored eight-chord windows only. Neither guarantees originality or non-memorization.'
    if wants_audio:
        report['audio'] = audio(out, [x[0] for x in arms], args)
    (out / 'generation.json').write_text(json.dumps(report, indent=2) + '\n')
    (out / 'README.txt').write_text(readme(context_length), encoding='utf-8')
    with zipfile.ZipFile(out / 'Mousa-Progression-Audition.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        for filename in ['README.txt', 'generation.json'] + [n + ext for n, _, _ in arms for ext in (('.mid', '.mp3') if wants_audio else ('.mid',))]:
            z.write(out / filename, filename)
    print(json.dumps({'output': str(out), 'arms': len(arms), 'audio_rendered': wants_audio}))


if __name__ == '__main__':
    main()
