"""Drum kits for the packs, from the SFZ kits in sources/drums (see CREDITS.md), into build/<pack>/drums/<kit>/:
<sound>-<layer>.flac per kit sound (Source/MidiInstrument.h kitSounds) and velocity layer (1 = softest). Each kit
maps its SFZ notes onto Backline's sounds; the first round-robin take of each layer is kept, and samples are cut once
they've decayed 60 dB (at most 10 s). A sound a kit lacks falls back to its piece in the engine.
Kits ship their pieces at very different levels (the AVL kits normalise every piece), so each piece's loudest layer is
set to a standard mix level (MIX, dB from the kick at KICK dBFS); the layers keep their levels relative to it.
"""
import pathlib

import numpy as np
import soundfile as sf

from keys_samples import midi, regions, trim

SRC = pathlib.Path(__file__).parent / 'sources/drums'
KICK = -10
MIX = {'kick': 0, 'snare': 0, 'snareRim': -2, 'sidestick': -6, 'tom1': -3, 'tom2': -3, 'floor': -3, 'hihat': -8,
       'hihatOpen': -6, 'hihatPedal': -10, 'crash': -6, 'ride': -8, 'rideBell': -6}

# General MIDI layout of the AVL kits: one rack tom (it plays both tom pads); 46 is a half-open hat
AVL = {'kick': 36, 'snare': 38, 'snareRim': 40, 'sidestick': 37, 'tom1': 45, 'tom2': 45, 'floor': 41, 'hihat': 42,
       'hihatOpen': 46, 'hihatPedal': 44, 'crash': 49, 'ride': 51, 'rideBell': 53}
KITS = {  # kit name -> (SFZ, Backline sound -> SFZ note)
    'Muldjord Kit': ('muldjord/MuldjordKit SFZ+FLAC-20201018/MuldjordKit 20201018.sfz',
                     {'kick': 48, 'snare': 50, 'tom1': 61, 'tom2': 62, 'floor': 64, 'hihat': 52, 'hihatOpen': 53,
                      'crash': 59, 'ride': 54, 'rideBell': 55}),
    'Black Pearl': ('BLACK_PEARL_2023_repack/BLACK_PEARL_2023_repack/Black_Pearl_2023_repack.sfz', AVL),
    'Red Zeppelin': ('RED_ZEPPELIN_2023_repack/RED_ZEPPELIN_2023_repack/Red_Zeppelin_2023_repack.sfz', AVL),
    'Blonde Bop': ('BLONDE_BOP_SFZ/BLONDE_BOP_SFZ/BLONDE_BOP.sfz', AVL),
    "Buskman's Holiday": ('BUSKMANS_HOLIDAY_SFZ/BUSKMANS_HOLIDAY_SFZ/Buskmans_Holiday.sfz',  # cajon, congas, shakers
                          {'kick': 36, 'snare': 38, 'snareRim': 40, 'sidestick': 37, 'tom1': 45, 'tom2': 47, 'floor': 41,
                           'hihat': 42, 'hihatOpen': 46, 'hihatPedal': 44, 'crash': 49, 'ride': 51, 'rideBell': 50}),
}


def convert(sfz, sounds, dst):
    layers = {}  # note -> lovel -> sample
    for r in regions(sfz):
        if r.get('trigger', 'attack') != 'attack' or r.get('seq_position', '1') != '1' or float(r.get('lorand', 0)) > 0:
            continue
        key = r.get('key') or r.get('lokey')
        if key is not None:
            layers.setdefault(midi(key), {}).setdefault(int(r.get('lovel', 1)), sfz.parent / r.get('default_path', '') / r['sample'].replace('\\', '/'))
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for sound, note in sounds.items():
        takes = [sf.read(layers[note][lo], always_2d=True) for lo in sorted(layers.get(note, {}))]
        if not takes:
            continue
        gain = 10 ** ((KICK + MIX[sound]) / 20) / max(np.abs(x).max() for x, _ in takes)
        for k, (x, rate) in enumerate(takes, 1):
            sf.write(dst / f'{sound}-{k}.flac', trim(x * gain, rate), rate, subtype='PCM_16')
            n += 1
    return n


def stage(build):
    for i, (kit, (sfz, sounds)) in enumerate(KITS.items()):
        pack = 'drums-essentials' if i == 0 else 'drums-encore'
        print(f'{kit}: {convert(SRC / sfz, sounds, build / pack / "drums" / kit)} samples')


if __name__ == '__main__':
    stage(pathlib.Path(__file__).parent / 'build')
