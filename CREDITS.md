# Credits

Backline's sound packs are free and only contain sounds whose licences allow sharing them.

Amplifier, cabinet, instrument and drum brand names in sound names (Marshall, Fender, Mesa, Peavey, Pearl, Ludwig and
others) are trademarks of their owners. They only describe the gear that was captured or sampled; neither Backline nor
these packs are affiliated with or endorsed by them.

## Amp captures (Guitar Essentials, Guitar Encore)

Neural Amp Modeler captures by George B, Helga B, Luis R, Mikhail K, Phillipe P, Roman A, Sascha S, Tim R, Tom C and
Tudor N, members of the Neural Amp Modeler Facebook group, collected at https://github.com/pelennor2170/NAM_models.
Licensed under the GNU GPL v3 (see COPYING). Changes: renamed, and NAM loudness metadata added (tools/loudness.cpp).

## Cab impulse responses (Guitar Essentials, Guitar Encore)

All converted to 48 kHz mono 24-bit and trimmed (cabs.py).

- EV TL806 1x12 (Summed, SM57, Ribbon) and Marshall 1960B 4x12, by Zach Weeks, God City Studio
  (https://zachweeks.gumroad.com/l/tl806cabir). CC BY-SA 4.0 (https://creativecommons.org/licenses/by-sa/4.0/);
  the converted files are shared under the same licence. Changes: the author's recommended high cut applied
  (8 kHz Summed and Ribbon, 10 kHz SM57 and 1960B).
- Behringer BG412S (V30 Even, Balls, Brutal, Brutzl; DV77; V30 + DV77 Godmode), by jesterdyne
  (https://freesound.org/people/jesterdyne/packs/34071/). CC0.
- Brown Cab Audix i5, by tosha73 (https://freesound.org/s/507167/). CC0.
- Peavey Blazer 158 1x12 + Spring, by unfa (https://freesound.org/s/205622/). CC0. Summed to mono.
- Bristol Two-Cab Blend, by mansardian (https://freesound.org/s/648392/). CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/).

## Keys (Keys Essentials, Keys Encore)

All converted by keys_samples.py: one sample per recorded note and velocity layer, cut once decayed 60 dB (at most 10 s),
16-bit FLAC, levelled to peak at -10 dBFS; release and loop data dropped.

- Concert Grand: Salamander Grand Piano V3 by Alexander Holm, via FreePats
  (https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html). CC BY 3.0
  (https://creativecommons.org/licenses/by/3.0/). 3 of its 16 velocity layers kept.
- Upright Piano: Upright Piano KW, via FreePats (https://freepats.zenvoid.org/Piano/acoustic-grand-piano.html). CC0.
- Honky-tonk Piano: Old Piano FB, recorded by Piotr Barcz, via FreePats
  (https://freepats.zenvoid.org/Piano/honky-tonk-piano.html). CC0.
- Stage 73 Electric Piano: jRhodes3d (mono, no crossfade) by Jeff Learman
  (https://github.com/sfzinstruments/jlearman.jRhodes3d). CC BY-NC 4.0
  (https://creativecommons.org/licenses/by-nc/4.0/): free to share, not for commercial use.

## Drum kits (Drums Essentials, Drums Encore)

Converted by drums_samples.py: each kit's sounds mapped onto Backline's pads, the first round-robin take of each
velocity layer kept, each piece set to a standard mix level, cut once decayed 60 dB (at most 10 s), 16-bit FLAC.

- Muldjord Kit by Lars Muldjord (DrumGizmo), stereo SFZ version via FreePats
  (https://freepats.zenvoid.org/Percussion/acoustic-drum-kit.html). CC BY 4.0
  (https://creativecommons.org/licenses/by/4.0/).
- Black Pearl, Red Zeppelin, Blonde Bop and Buskman's Holiday: AVL Drumkits by Glen MacArthur
  (https://www.bandshed.net/avldrumkits/). CC BY-SA 3.0 (https://creativecommons.org/licenses/by-sa/3.0/); the
  converted files are shared under the same licence. The single rack tom plays both tom pads.

tools/loudness_input.wav is from Neural Amp Modeler (https://github.com/sdatkinson/neural-amp-modeler, MIT).
