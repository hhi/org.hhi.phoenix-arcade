# Niet-geraakte C-functies (coverage-run 2026-07-10)

> [!WARNING]
> **Achterhaald per 11 juli 2026.** De vervolg-audit
> ([`jphoenix_crosscheck.md`](jphoenix_crosscheck.md)) heeft vrijwel
> alle vermoedens in dit bestand herroepen: de "niet geraakte" functies
> bleken dode duplicaat-stubs naast levende vertalingen, geïnlinede
> hulproutines, of harnas-artefacten — geen ontbrekend spelgedrag. Dit
> bestand blijft staan als momentopname van de ruwe coverage-run;
> raadpleeg voor de actuele status de Status-kolom in
> [`c_functions_by_address.md`](c_functions_by_address.md) en de
> eindconclusie in `jphoenix_crosscheck.md`.

> Resultaat van een `gcov --coverage`-run met alle 55 input-scripts uit
> `context/input-scripts/` (5 handgeschreven + 50 door de coverage-guided
> input-bot gegenereerde mutaties), elk `--run-frames=8000`. Van de 313
> unieke functies in [`c_functions_by_address.md`](c_functions_by_address.md)
> werden er **250 (79,9%) geraakt** en **63 niet** (62 met 0% lines executed,
> plus 1 door de compiler als `-Wunused-function` gemarkeerd).
>
> De kolom **Waarschijnlijke reden** is bepaald door voor elke functie de hele
> codebase te doorzoeken op echte aanroepen (dus niet de eigen declaratie/
> definitie, en niet losse asm-adrescommentaren). Twee hoofdgroepen:
> - **Nul aanroepen gevonden**: de functie zit niet in het aanroepnetwerk dat
> vanuit `phoenix_main_loop()` bereikbaar is — dit is dus geen "scripts dekken
> het niet", maar mogelijk **dode/overbodige code**. Zelfde
> patroon als de 6 duplicaat-stubs die al eerder zijn opgeruimd (zie
> `../STATUS.nl.md` → "Opruiming").
> - **Wel aanroepen gevonden**: de functie is bereikbaar, maar geen van de
> 55 scripts stuurt het spel naar dat codepad (bv. audio in headless-modus,
> of een volledige mothership-kill) — hier is een beter script de oplossing,
> geen contra-indicatie voor de vertaling zelf.
>
> Een `—` bij ASM-adres betekent dat de functie in de mapping-tabel zelf al
> geen ROM-adres heeft (platform-/C-only hulpfunctie zonder Z80-tegenhanger).


## Audio-synthese (16)

### `tms36xx_tone` (ASM: —)
- **Bestand**: [tms36xx.c](../../tms36xx.c#L162)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (tms36xx.c:250), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `tms36xx_decay` (ASM: —)
- **Bestand**: [tms36xx.c](../../tms36xx.c#L131)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (tms36xx.c:232), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `tms36xx_restart` (ASM: —)
- **Bestand**: [tms36xx.c](../../tms36xx.c#L145)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (tms36xx.c:244), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `sound_render_frame` (ASM: —)
- **Bestand**: [sound.c](../../sound.c#L59)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (platform_sdl.c:149, platform_sdl.c:159), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `clamp_pcm16` (ASM: —)
- **Bestand**: [sound.c](../../sound.c#L53)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound.c:73), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `effect1_data` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L44)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:447), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `effect1_filter_selected` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L46)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:294, sound_discrete.c:448, sound_discrete.c:452), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `effect1_frequency` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L45)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:444), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `effect2_data` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L40)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:441), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `effect2_frequency` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L41)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:429, sound_discrete.c:430), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `noise_c24_discharge` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L42)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:333), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `noise_c25_charge` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L43)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:358), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `sound_discrete_noise` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L382)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound.c:71), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `update_c24` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L332)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:383), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `update_c25` (ASM: —)
- **Bestand**: [sound_discrete.c](../../sound_discrete.c#L357)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wel aangeroepen (sound_discrete.c:384), maar het audiopad staat uit in headless-modus: `sound_render_frame()` wordt alleen uitgevoerd als er een SDL-audiodevice open is, en dat gebeurt nooit bij `--run-frames`. Geen aanwijzing voor een bug.

### `update_audio_registers` (ASM: —)
- **Bestand**: [hw_video_audio.c](../../hw_video_audio.c#L185)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. (Extra: audiopad is sowieso uitgeschakeld in headless-modus.)


## Recording/tooling (alleen actief bij --record-input / --coverage-dump) (4)

### `record_input_event` (ASM: —)
- **Bestand**: [platform_sdl.c](../../platform_sdl.c#L441)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (platform_sdl.c:685), maar alleen via `--record-input=`/`--coverage-dump=`-paden die deze coverage-run niet gebruikte (pure `--input-script`-replay).

### `start_input_recording` (ASM: —)
- **Bestand**: [platform_sdl.c](../../platform_sdl.c#L425)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (platform_sdl.c:521), maar alleen via `--record-input=`/`--coverage-dump=`-paden die deze coverage-run niet gebruikte (pure `--input-script`-replay).

### `write_screenshot` (ASM: —)
- **Bestand**: [platform_sdl.c](../../platform_sdl.c#L279)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (platform_sdl.c:840, platform_sdl.c:845), maar alleen via `--record-input=`/`--coverage-dump=`-paden die deze coverage-run niet gebruikte (pure `--input-script`-replay).

### `coverage_set_output_path` (ASM: —)
- **Bestand**: [coverage.c](../../coverage.c#L45)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (platform_sdl.c:498), maar alleen via `--record-input=`/`--coverage-dump=`-paden die deze coverage-run niet gebruikte (pure `--input-script`-replay).


## Rendering / hardware-hulpfuncties (3)

### `render_sprites` (ASM: —)
- **Bestand**: [hw_video_audio.c](../../hw_video_audio.c#L171)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: de functiebody zelf is ook een no-op (`// Draw active sprite to framebuffer (emulator core responsibility)` — geen echte implementatie). De daadwerkelijke sprite-tekencode zit rechtstreeks in `platform_sdl.c` (pixel-voor-pixel uit screen-RAM). Kandidaat om te verwijderen of alsnog aan te sluiten.

### `hw_toggle_palette_bank` (ASM: —)
- **Bestand**: [platform_sdl.c](../../platform_sdl.c#L71)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.
### `hw_is_vblank` (ASM: —)
- **Bestand**: [platform_sdl.c](../../platform_sdl.c#L45)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.


## Mothership-eindfase (9)

### `state_6_mother_ship_explosion` (ASM: $2400)
- **Bestand**: [state_endings.c](../../state_endings.c#L134)
- **Range**: 2400-244B
- **Waarschijnlijke reden**: Wordt aangeroepen (game_state_machine.c:40) — vereist dat een script het spel daadwerkelijk tot de mothership-explosie brengt (game_state 6). Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `state_7_mother_ship_score_display` (ASM: —)
- **Bestand**: [state_endings.c](../../state_endings.c#L177)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (game_state_machine.c:41) — vereist game_state 7 (score-scherm na mothership-kill). Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `erase_mothership` (ASM: $246A)
- **Bestand**: [mothership_logic.c](../../mothership_logic.c#L22)
- **Range**: 246A-2475
- **Waarschijnlijke reden**: Wordt aangeroepen (state_endings.c:130, state_endings.c:144) — onderdeel van de mothership-explosiesequentie. Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `mothership_core_hit_check` (ASM: $2520)
- **Bestand**: [mothership_logic.c](../../mothership_logic.c#L36)
- **Range**: 2520-255D
- **Waarschijnlijke reden**: Wordt aangeroepen (state_endings.c:130, state_endings.c:149) — onderdeel van de mothership-explosiesequentie. Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `l2552_mothership_explosion_done` (ASM: $2552)
- **Bestand**: [state_endings.c](../../state_endings.c#L110)
- **Range**: 2552-255D
- **Waarschijnlijke reden**: Wordt aangeroepen (state_endings.c:139) — laatste stap van de mothership-explosiesequentie. Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `update_counters_for_mothership_explosion` (ASM: —)
- **Bestand**: [mothership_impl.c](../../mothership_impl.c#L195)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (state_endings.c:122, state_endings.c:136) — onderdeel van de mothership-explosiesequentie. Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `l2085_draw_particles` (ASM: —)
- **Bestand**: [mothership_impl.c](../../mothership_impl.c#L133)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen (state_endings.c:169) — deeltjes-animatie tijdens mothership-explosie. Geen van de 55 scripts speelt door tot een volledige mothership-kill op level 9+; dieper/gerichter script nodig, geen bug-indicatie.

### `mothership_barrier_collision` (ASM: —)
- **Bestand**: [mothership_logic.c](../../mothership_logic.c#L26)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `mothership_descent_logic` (ASM: —)
- **Bestand**: [mothership_logic.c](../../mothership_logic.c#L12)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.


## Vogel-/spiraalpatronen (10)

### `spiral_fill_animation` (ASM: $2230)
- **Bestand**: [alien_logic.c](../../alien_logic.c#L331)
- **Range**: 2230-225F
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: dit hoort bij het level-4/6/8-spiraalpatroon.

### `bird_flight_path` (ASM: —)
- **Bestand**: [bird_logic.c](../../bird_logic.c#L69)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Opvallend: bevat zelf wel een `coverage_hit("bird_flight_path")`-marker, dus was ooit bedoeld om aangeroepen te worden.

### `drawfirst4birdobjects` (ASM: $3474)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 3474-34BB
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l37b0` (ASM: $34C0)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 34C0-3519, 3520-35A2, 35B0-35DB, 35E0-373E, 3744-37AA, 37B0-37C6
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l37cc` (ASM: $37CC)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 37CC-37E5
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l3800` (ASM: $3800)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 3800-388D
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l3894` (ASM: $3894)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 3894-389C
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l38a1` (ASM: $38A1)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 38A1-38F1
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l38f8` (ASM: $38F8)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 38F8-397B
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).

### `l3980` (ASM: $3980)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 3980-39EA
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: onderdeel van de vogel-introductie-animatiereeks (generated_stubs.c).


## Bevestigd dood (3)

### `l242c_mothership_scroll_update` (ASM: —)
- **Bestand**: [state_endings.c](../../state_endings.c#L95)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Door de compiler zelf gemarkeerd met `-Wunused-function` (state_endings.c:95) — bevestigd dode code.

### `unused_bcd_subtracter` (ASM: $0236)
- **Bestand**: [utilities.c](../../utilities.c#L153)
- **Range**: 0236-0252
- **Waarschijnlijke reden**: Naam zegt het al (`unused_`) — vermoedelijk al eerder als dood geïdentificeerd door een vorige vertaalronde.

### `l0e02_unused` (ASM: $0E02)
- **Bestand**: [weapon_collision.c](../../weapon_collision.c#L207)
- **Range**: 0E02-0E0B
- **Waarschijnlijke reden**: Naam zegt het al (`_unused`) — vermoedelijk al eerder als dood geïdentificeerd.


## Overig / vroege utility-routines (18)

### `init_alien_movement_pointers` (ASM: $0506)
- **Bestand**: [state_init.c](../../state_init.c#L73)
- **Range**: 0506-0514
- **Waarschijnlijke reden**: Wordt aangeroepen vanuit state_init.c:81, maar geen van de scripts triggert dat codepad — vermoedelijk een init-variant die niet elk potje wordt gebruikt.

### `l0526` (ASM: —)
- **Bestand**: [state_init.c](../../state_init.c#L77)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Wordt aangeroepen vanuit alien_wave.c:114 ("init alien data"), maar geen van de scripts triggert dat codepad — vermoedelijk een init-variant die niet elk potje wordt gebruikt.

### `add_bc_to_mem` (ASM: $0206)
- **Bestand**: [utilities.c](../../utilities.c#L217)
- **Range**: 0206-020E
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `add_to_score` (ASM: $0220)
- **Bestand**: [utilities.c](../../utilities.c#L321)
- **Range**: 0220-0232
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `check_player_ship_collision` (ASM: —)
- **Bestand**: [weapon_collision.c](../../weapon_collision.c#L171)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Opvallend: klinkt als kernlogica (speler-vs-vijand-botsing) die je wél zou verwachten — eerste kandidaat om echt na te lezen.

### `clear_b_bytes_at_hl` (ASM: $05D8)
- **Bestand**: [utilities.c](../../utilities.c#L123)
- **Range**: 05D8-05DF
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `copy_b_bytes_hl_to_de` (ASM: $05E0)
- **Bestand**: [utilities.c](../../utilities.c#L137)
- **Range**: 05E0-05E8
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `game_demo` (ASM: $03B0)
- **Bestand**: [attract_mode.c](../../attract_mode.c#L385)
- **Range**: 03B0-03FD
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: heeft dezelfde ROM-adressen als check_demo_mode_player_and_alien (03B0-03FD) — mogelijk een echte duplicaat-naam voor dezelfde routine.

### `l00b6` (ASM: $00B6)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 00B6-00B7
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: lege functiebody (`{}`) in generated_stubs.c — puur automatisch gegenereerde placeholder.

### `l01e1` (ASM: —)
- **Bestand**: [misc_logic.c](../../misc_logic.c#L19)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `l0c00_bonus_explosion_scoring` (ASM: $0C00)
- **Bestand**: [alien_logic.c](../../alien_logic.c#L362)
- **Range**: 0C00-0C23
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `l0cf4` (ASM: $0FC0)
- **Bestand**: [weapon_collision.c](../../weapon_collision.c#L190)
- **Range**: 0FC0-0FFD, 0CF4-0CF6
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: lege functiebody (`{}`).

### `l0e9e` (ASM: $0280)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 0280-0285, 0E9E-0EA3
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: lege functiebody (`{}`).

### `l14e0` (ASM: $14E0)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 14E0-14FD
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: lege functiebody (`{}`).

### `l3452` (ASM: $1EE0)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 1EE0-1EFA, 2030-2037, 21DC-21FC, 2204-222B, 2260-22C5, 22CA-22E8, 22F0-22F4, 22FA-2337, 3000-3012, 3028-306D, 3074-314E, 315A-31AD, 31B4-325E, 3264-32F0, 3452-345B
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: dit adresbereik is ongebruikelijk groot (15 losse ranges, o.a. 3074-314E) voor een lege stub — controleer of dit een grote hoeveelheid logica vertegenwoordigt die elders (mogelijk correct) is geïmplementeerd.

### `l3462` (ASM: $3462)
- **Bestand**: `generated_stubs.c` is verwijderd; het ROM-bereik is aan een levende implementatie gekoppeld.
- **Range**: 3462-346D
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt. Extra: lege functiebody (`{}`).

### `l34de` (ASM: —)
- **Bestand**: [utilities.c](../../utilities.c#L438)
- **Range**: Unknown / None
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.

### `print_score_column` (ASM: $06E8)
- **Bestand**: [utilities.c](../../utilities.c#L87)
- **Range**: 06E8-06ED
- **Waarschijnlijke reden**: Geen enkele aanroep gevonden in de hele codebase — vermoedelijk een overbodige/dode duplicaat-stub (zelfde patroon als de 6 stubs die al zijn opgeruimd, zie `../STATUS.nl.md` → "Opruiming") of nog niet aangesloten logica. Controleer eerst of dit adresbereik al elders correct is vertaald voordat je hier tijd in steekt.
