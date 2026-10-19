"""Builds Backline's sound packs from sources/ into dist/ (zips + packs.json), using backline/tools/make_pack.py.

  ~/.cache/bl/venv/bin/python packs.py [--url https://github.com/gtemple/backline-sounds/releases/download/<tag>]

Sources (git-ignored, see CREDITS.md for where each comes from):
  sources/NAM_models-main  github.com/pelennor2170/NAM_models (GPL v3)
  sources/raw              the cab IR downloads; cabs.py turns them into sources/cabs/<name as in Backline>.wav
  sources/keys             the keys sample sets (SFZ); keys_samples.py converts them
Models get NAM loudness metadata (tools/loudness), so Backline levels them like the NAM plugin does.
"""
import argparse
import json
import pathlib
import re
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).parent
NAM = ROOT / 'sources/NAM_models-main'
CABS = ROOT / 'sources/cabs'
sys.path.insert(0, '/mnt/c/dev/backline/tools')
from make_pack import build  # noqa: E402

# Captures of real amps: (source file prefix, Backline name prefix). Pedal-only captures, captures of software modelers
# (Axe-FX), power-amp-only captures and amps that can't be identified from the file name are left out.
AMPS = [
    ('George B Ceriatone King Kong', 'Ceriatone King Kong'), ('George B V4 Countess', 'Victory V4 Countess'),
    ('Helga B 5150 BlockLetter', 'Peavey 5150'), ('Helga B 6505+', 'Peavey 6505+'), ('Helga B 6534+', 'Peavey 6534+'),
    ('Helga B JSX', 'Peavey JSX'), ('Helga B XXX', 'Peavey XXX'),
    ('Luis R driftwood purple nightmare', 'Driftwood Purple Nightmare'), ('Tudor N Driftwood Nightmare', 'Driftwood Purple Nightmare'),
    ('Mikhail K Sovtek MIG50', 'Sovtek MIG-50'), ('Mikhail K SovtekMIG50', 'Sovtek MIG-50'),
    ('Phillipe P Bug1990', 'Bugera 1990'), ('Phillipe P Bug333', 'Bugera 333'), ('Phillipe P Bug6262', 'Bugera 6262'),
    ('Phillipe P Bugera6262', 'Bugera 6262'), ('Phillipe P JVM', 'Marshall JVM'), ('Phillipe P LaneyGH100S', 'Laney GH100S'),
    ('Phillipe P VOXAC15', 'Vox AC15'), ('Roman A BUGERA_333', 'Bugera 333'), ('Roman A LT_MESA_MARKIV', 'Mesa Mark IV'),
    ('Roman A YERASOV_MESHUGGAH', 'Yerasov Meshuggah'), ('Sascha S DirtyShirley', 'Friedman Dirty Shirley'),
    ('Tim R 5152', 'Peavey 5150 II'), ('Tim R Fender TwinVerb', 'Fender Twin Reverb'), ('Tim R JCM2000', 'Marshall JCM2000'),
    ('Tim R JCM90050WDualVerb', 'Marshall JCM900 Dual Reverb'), ('Tim R Jet City', 'Jet City'),
    ('Tim R Magnatone Super 59', 'Magnatone Super 59'), ('Tim R Splawn Pro Mod', 'Splawn Pro Mod'),
    ('Tom C Engl e530', 'Engl E530 + 840'), ('Tudor N Ceriatone Molecular 50', 'Ceriatone Molecular 50'),
]

# Essentials: ready to play without picking anything (amp+cab captures, or an amp with a cab from the pack)
ESSENTIALS = {
    'Phillipe P JVM-CL-GR-NoDrive-Cab-ESR0,007.nam': 'Marshall JVM Clean (amp+cab)',
    'Phillipe P Bug333-Clean-Cab-ESR0,007.nam': 'Bugera 333 Clean (amp+cab)',
    'Tim R Fender TwinVerb Norm Bright.nam': 'Fender Twin Reverb Clean',
    'Phillipe P VOXAC15-TopBoost.nam': 'Vox AC15 Top Boost',
    'Phillipe P Bug333-Crunch-NoDrive-Cab-ESR0,005.nam': 'Bugera 333 Crunch (amp+cab)',
    'Tim R JCM2000 Crunch.nam': 'Marshall JCM2000 Crunch',
    'Phillipe P JVM-OD2-RD-NoDrive-Cab-ESR0,006.nam': 'Marshall JVM OD2 Lead (amp+cab)',
    'Roman A LT_MESA_MARKIV_1.nam': 'Mesa Mark IV Lead',
    'Helga B 5150 BlockLetter - Boosted.nam': 'Peavey 5150 High Gain',
}
ESSENTIAL_CABS = ['EV TL806 1x12 Summed (Zach Weeks)', 'Marshall 1960B 4x12 (Zach Weeks)', 'Behringer BG412S V30 Even']
PAIRS = {  # amp-only captures -> the cab they're set up with on install (pairs.json)
    'Fender Twin Reverb Clean': 'EV TL806 1x12 Summed (Zach Weeks)', 'Vox AC15 Top Boost': 'EV TL806 1x12 Summed (Zach Weeks)',
    'Marshall JCM2000 Crunch': 'Marshall 1960B 4x12 (Zach Weeks)', 'Mesa Mark IV Lead': 'Behringer BG412S V30 Even',
    'Peavey 5150 High Gain': 'Behringer BG412S V30 Even',
}


SKIP = {'Helga B JSX Ultra - M77(GROUND HUM).nam', 'Helga B 6534+ MXR M77 - Helga Behrens.nam'}  # a hum; a duplicate
RENAME = {'Tom C Engl e530 preamp & 840 power amp with Boss DS1 Overdrive.nam': 'Engl E530 + 840 DS1 Boost'}


def tidy(rest):
    rest = re.sub(r'[-_ ]*ESR[-_ ]?[\d,.]+|[ _-]\d,\d+$', '', rest)
    rest = re.sub(r'NAM Capture (.*?) Chase Tone Secret Pre Deco( v2)?', r'+ \1', rest)
    rest = re.sub(r'\(FIXED\)|NoBoost|No Boost|NoDrive', '', rest)
    rest = re.sub(r'(?i)ch([AB])G(\d+)', r'Ch \1 G\2', rest)
    rest = re.sub(r'(?i)mkii', 'Mk II', rest)
    rest = re.sub(r'[-_ ]*\(v\d\)|300eps', '', rest)
    cab = re.search(r'(^|[-_ ])Cab($|[-_ ])', rest) is not None
    rest = re.sub(r'(^|[-_ ])Cab($|[-_ ])', ' ', rest)
    rest = re.sub(r' +', ' ', re.sub(r'[_]+|(?<=\w)-(?=\w)| - ', ' ', rest)).strip(' -_')
    rest = rest.replace('Clean ish', 'Clean-ish')
    return rest, cab


def encore_names():
    names = {}
    for f in sorted(NAM.glob('*.nam')):
        if f.name in ESSENTIALS or f.name in SKIP:
            continue
        if f.name in RENAME:
            names[f.name] = RENAME[f.name]
            continue
        for prefix, brand in AMPS:
            if f.name.startswith(prefix):
                rest, cab = tidy(f.stem[len(prefix):])
                name = f'{brand} {rest}'.strip() + (' (amp+cab)' if cab else '')
                author = ' '.join(f.name.split()[:2])
                if name in names.values() or name in ESSENTIALS.values():
                    name = f'{name} ({author})'
                names[f.name] = name
                break
    return names


def stage(dest, models, cabs):
    shutil.rmtree(dest, ignore_errors=True)
    (dest / 'Models').mkdir(parents=True)
    loud = dict(line.split('\t')[::-1] for line in subprocess.run(
        [str(pathlib.Path.home() / '.cache/bl/loudness'), str(ROOT / 'tools/loudness_input.wav'), *[str(NAM / f) for f in models]],
        capture_output=True, text=True, check=True).stdout.strip().splitlines())
    for src, name in models.items():
        j = json.loads((NAM / src).read_text())
        j.setdefault('metadata', {})['loudness'] = float(loud[str(NAM / src)])
        (dest / 'Models' / f'{name}.nam').write_text(json.dumps(j, separators=(',', ':')))
    cabs = [c for c in cabs if (CABS / f'{c}.wav').exists()]
    if cabs:
        (dest / 'Cabs').mkdir()
        for c in cabs:
            if (CABS / f'{c}.wav').exists():
                shutil.copy(CABS / f'{c}.wav', dest / 'Cabs')
    pairs = {amp: cab for amp, cab in PAIRS.items() if amp in models.values() and cab in cabs}
    if pairs:
        (dest / 'pairs.json').write_text(json.dumps(pairs, indent=1))
    shutil.copy(NAM / 'COPYING', dest / 'COPYING')
    shutil.copy(ROOT / 'CREDITS.md', dest / 'CREDITS.md')


if __name__ == '__main__':
    a = argparse.ArgumentParser()
    a.add_argument('--url', default='https://github.com/gtemple/backline-sounds/releases/download/v1')
    args = a.parse_args()
    authors = 'George B, Helga B, Luis R, Mikhail K, Phillipe P, Roman A, Sascha S, Tim R, Tom C and Tudor N'
    credit = (f'Amp captures by {authors} from the NAM community collection (GPL v3). Cab IRs by Zach Weeks (CC BY-SA 4.0), '
              'jesterdyne, tosha73, unfa (CC0) and mansardian (CC BY 4.0) via Freesound.')
    all_cabs = sorted(p.stem for p in CABS.glob('*.wav')) if CABS.exists() else []
    stage(ROOT / 'build/guitar-essentials', ESSENTIALS, ESSENTIAL_CABS)
    stage(ROOT / 'build/guitar-encore', encore_names(), [c for c in all_cabs if c not in ESSENTIAL_CABS])
    import keys_samples
    keys_samples.stage(ROOT / 'build')
    for pid in ('keys-essentials', 'keys-encore'):
        shutil.copy(ROOT / 'CREDITS.md', ROOT / 'build' / pid / 'CREDITS.md')
    credits = {
        'keys-essentials': 'Concert Grand: Salamander Grand Piano V3 by Alexander Holm (CC BY 3.0).',
        'keys-encore': 'Upright Piano KW (Gonzalo) and Old Piano FB (Piotr Barcz) via FreePats (CC0); '
                       'Stage 73 Electric Piano: jRhodes3d by Jeff Learman (CC BY-NC 4.0).',
    }
    for pid in ('guitar-essentials', 'guitar-encore', 'keys-essentials', 'keys-encore'):
        e = build(ROOT / 'build' / pid, pid, 1, ROOT / 'dist', args.url, credits.get(pid, credit))
        print(f"{pid}: {e['size'] / 1e6:.1f} MB, " + ', '.join(f'{len(v)} {k}' for k, v in e['contents'].items()))
