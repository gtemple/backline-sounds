"""Keys instruments for the packs, from the SFZ sample sets in sources/keys (see CREDITS.md), into
build/<pack>/<keys|piano>/...: <midi>-<layer>.flac per recorded note and velocity layer (1 = softest), the format
Source/MidiInstrument.h loads. Samples are cut once they've decayed 60 dB (at most 10 s) to keep them small in memory.
Release, round-robin and keyswitch regions are left out. Each instrument is scaled so its loudest sample peaks at
PEAK dBFS, leaving headroom for chords. Needs soundfile and numpy (~/.cache/bl/venv).
"""
import pathlib
import re
import sys

import numpy as np
import soundfile as sf

sys.path.insert(0, '/mnt/c/dev/backline/tools')
from piano_samples import build as salamander, trim  # noqa: E402

ROOT = pathlib.Path(__file__).parent
SRC = ROOT / 'sources/keys'
PEAK = -10
NOTES = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}


def midi(v):
    """'60', 'F1', 'Bb3', 'C#4' -> MIDI note (C4 = 60)"""
    if v.lstrip('-').isdigit():
        return int(v)
    m = re.fullmatch(r'([a-gA-G])([#b]?)(-?\d)', v)
    return NOTES[m[1].lower()] + {'#': 1, 'b': -1, '': 0}[m[2]] + 12 * (int(m[3]) + 1)


def regions(sfz):
    """Every <region> of an SFZ with the <global>/<group>/<control> opcodes it inherits"""
    text = re.sub(r'//[^\n]*', '', sfz.read_text(errors='replace'))
    scope, group, out, cur = {}, {}, [], None
    for header, body in re.findall(r'<(\w+)>([^<]*)', text):
        ops = dict(re.findall(r'(\w+)=(.+?)(?=\s+\w+=|\s*$)', body.strip(), re.S))
        ops = {k: v.strip() for k, v in ops.items()}
        if header in ('global', 'control', 'master'):
            scope.update(ops)
            group = {}
        elif header == 'group':
            group = ops
        elif header == 'region':
            out.append({**scope, **group, **ops})
    return out


def convert(sfz, dst):
    found = {}
    for r in regions(sfz):
        if r.get('trigger', 'attack') != 'attack' or r.get('seq_position', '1') != '1' or 'sw_last' in r:
            continue
        root = midi(r.get('pitch_keycenter') or r['key'])
        found.setdefault(root, {})[int(r.get('lovel', 1))] = sfz.parent / r.get('default_path', '') / r['sample'].replace('\\', '/')
    dst.mkdir(parents=True, exist_ok=True)
    for root, layers in found.items():
        for k, lo in enumerate(sorted(layers), 1):
            x, rate = sf.read(layers[lo], always_2d=True)
            sf.write(dst / f'{root}-{k}.flac', trim(x, rate), rate, subtype='PCM_16')
    return sum(map(len, found.values()))


INSTRUMENTS = {  # Backline name -> SFZ
    'Upright Piano': 'upright/UprightPianoKW-SFZ+FLAC-20220221/UprightPianoKW-20220221.sfz',
    'Honky-tonk Piano': 'oldpiano/PianoFB SFZ+FLAC-20200401/PianoFB 20200401.sfz',
    'Stage 73 Electric Piano': 'rhodes/jlearman.jRhodes3d-master/jRhodes3d-mono/_jRhodes3d-mono-no-xfade-flac.sfz',
}


def level(folder):
    files = sorted(folder.glob('*.flac'))
    gain = 10 ** (PEAK / 20) / max(np.abs(sf.read(f)[0]).max() for f in files)
    for f in files:
        x, rate = sf.read(f)
        sf.write(f, x * gain, rate, subtype='PCM_16')


def stage(build):
    n = salamander(SRC / 'SalamanderGrandPiano-SFZ+FLAC-V3+20200602/samples', build / 'keys-essentials/piano')
    (build / 'keys-essentials/piano/CREDITS.txt').unlink()
    level(build / 'keys-essentials/piano')
    print(f'Concert Grand: {n} samples')
    for name, sfz in INSTRUMENTS.items():
        print(f'{name}: {convert(SRC / sfz, build / "keys-encore/keys" / name)} samples')
        level(build / 'keys-encore/keys' / name)


if __name__ == '__main__':
    assert midi('F1') == 29 and midi('Bb3') == 58 and midi('C4') == 60 and midi('A0') == 21 and midi('Db4') == 61
    stage(ROOT / 'build')
