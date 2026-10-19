"""Turns the downloaded cab IRs (sources/raw, see CREDITS.md) into sources/cabs/<Backline name>.wav: 48 kHz mono 24-bit,
with the high cut their author recommends baked in, and trailing silence trimmed. Needs numpy, scipy and soundfile.

  python3 cabs.py
"""
import pathlib

import numpy as np
import soundfile as sf
from scipy.signal import butter, resample_poly, sosfilt

RAW = pathlib.Path(__file__).parent / 'sources/raw'
OUT = pathlib.Path(__file__).parent / 'sources/cabs'
ZW = 'TL806 and Basement Cab IRs v1_1'
BG = '34071__jesterdyne__brutal-bg412s-v30dv77-cabinet-irs'

# source -> (Backline name, high cut in Hz or None)
CABS = {
    f'{ZW}/God City Basement 1960B/Basement 1960B IR 96 24.wav': ('Marshall 1960B 4x12 (Zach Weeks)', 10000),
    f'{ZW}/God City TL806/TL806 Summed IR 96 24.wav': ('EV TL806 1x12 Summed (Zach Weeks)', 8000),
    f'{ZW}/God City TL806/TL806 Crimson 57 IR 96 24.wav': ('EV TL806 1x12 SM57 (Zach Weeks)', 10000),
    f'{ZW}/God City TL806/TL806 AEA N22 IR 96 24.wav': ('EV TL806 1x12 Ribbon (Zach Weeks)', 8000),
    f'{BG}/616702__jesterdyne__cabinet-ir-bg412s-even-v30-sm57.wav': ('Behringer BG412S V30 Even', None),
    f'{BG}/616705__jesterdyne__cabinet-ir-bg412s-balls-v30-sm57.wav': ('Behringer BG412S V30 Balls', None),
    f'{BG}/616704__jesterdyne__cabinet-ir-bg412s-brutal-v30-sm57.wav': ('Behringer BG412S V30 Brutal', None),
    f'{BG}/616703__jesterdyne__cabinet-ir-bg412s-brutzl-v30-pyle-pdmic78.wav': ('Behringer BG412S V30 Brutzl', None),
    f'{BG}/618896__jesterdyne__cabinet-ir-bg412s-eminence-dv77-sm57.wav': ('Behringer BG412S DV77', None),
    f'{BG}/618897__jesterdyne__cabinet-ir-bg412s-godmode-dv77v30-mix.wav': ('Behringer BG412S V30 + DV77 Godmode', None),
    '648392__mansardian__bristol.wav': ('Bristol Two-Cab Blend', None),
    '507167__tosha73__ir-brown-cab_audix-i5-center.wav': ('Brown Cab Audix i5', None),
    '205622__unfa__peavey-blazer-158-spring-reverb-and-cabinet-stereo-ir.flac': ('Peavey Blazer 158 1x12 + Spring', None),
}

OUT.mkdir(parents=True, exist_ok=True)
for src, (name, cut) in CABS.items():
    x, rate = sf.read(RAW / src, always_2d=True)
    x = x.mean(axis=1)
    if rate != 48000:
        g = np.gcd(48000, rate)
        x = resample_poly(x, 48000 // g, rate // g)
    if cut:
        x = sosfilt(butter(2, cut, fs=48000, output='sos'), x)  # 12 dB/oct, like an IR loader's high cut
    loud = np.nonzero(np.abs(x) > np.abs(x).max() * 10 ** (-80 / 20))[0]
    x = x[: loud[-1] + 1] if len(loud) else x
    sf.write(OUT / f'{name}.wav', x / np.abs(x).max() * 0.9, 48000, subtype='PCM_24')
    print(f'{name}: {len(x) / 48:.0f} ms')
