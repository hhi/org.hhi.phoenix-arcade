# C Functions Sorted by ROM Address (Including Analyzed Gaps)

> [!NOTE]
> **Gap Analysis Conclusion**
> In the entire 16KB ROM-space, 142 unmapped gaps/data blocks were found:
> - **Padding (FF)**: 94 (Confirmed empty EPROM space)
> - **UNREFERENCED DATA**: 45 (Unreadable bytes, likely unused arrays, sprites, or artifacts)
> - **DATA TABLE**: 2 (Data explicitly referenced by C code)
> - **Padding (00)**: 1
>
> **Conclusion:** Zero blocks of unreferenced executable Z80 code were found. Every executable Z80 instruction is either translated to a C function or explicitly stubbed. The codebase is 100% covered regarding executable logic.
>
> **Let op — dit is byte-dekking, geen bevestiging van correctheid.** "100% covered" betekent dat elke ROM-byte een naam of expliciete gap-markering heeft, *niet* dat elke vertaling ook bevestigd actief en correct is in de C-poort. Een cross-check tegen echte Z80-executie (jphoenix) en de c-phoenix-coverage vond 33 functies waarbij dat niet zo simpel lag — zie de **Status**-kolom hieronder en [`jphoenix_crosscheck.md`](jphoenix_crosscheck.md) voor de volledige analyse. Rijen zonder Status-vermelding zijn nog niet op deze manier onderzocht ("Unconfirmed").

| ASM Address | Function | File | Full Range(s) | Status |
|---|---|---|---|---|
| $0000 | [`phoenix_main_loop`](../../hw_video_audio.c#L123) | [hw_video_audio.c](../../hw_video_audio.c) | 0000-004F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0050 | [`init_sound_screen`](../../hw_video_audio.c#L94) | [hw_video_audio.c](../../hw_video_audio.c) | 0050-006A | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $006B | [`clear_ram_bank`](../../hw_video_audio.c#L76) | [hw_video_audio.c](../../hw_video_audio.c) | 006B-0077 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0078 | [`slow_print_scroll_register_update`](../../attract_mode.c#L241) | [attract_mode.c](../../attract_mode.c) | 0078-007D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$007E** | **Padding (2 bytes of FF)** | **---** | **007E-007F** | |
| $0080 | [`wait_vblank_coin`](../../hw_video_audio.c#L30) | [hw_video_audio.c](../../hw_video_audio.c) | 0080-00B5 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $00B6 | [`l00b6`](../../rom_compat_stubs.c#L8) | [rom_compat_stubs.c](../../rom_compat_stubs.c) | 00B6-00B7 | Dode code: nul aanroepers, ook in de originele ROM |
| **$00B8** | **Padding (3 bytes of FF)** | **---** | **00B8-00BA** | |
| $00BB | [`check_input_bits`](../../utilities.c#L16) | [utilities.c](../../utilities.c) | 00BB-00C3 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $00C4 | [`print_number`](../../utilities.c#L30) | [utilities.c](../../utilities.c) | 00C4-00E1 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$00E2** | **Padding (1 bytes of FF)** | **---** | **00E2-00E2** | |
| $00E3 | [`splash_and_demo`](../../attract_mode.c#L32) | [attract_mode.c](../../attract_mode.c) | 00E3-013A, 0140-0172 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$013B** | **Padding (5 bytes of FF)** | **---** | **013B-013F** | |
| $0140 | [`clear_fore_and_background`](../../attract_mode.c#L113) | [attract_mode.c](../../attract_mode.c) | 0140-0172 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0173 | [`get_player_inputs_for_demo`](../../attract_mode.c#L169) | [attract_mode.c](../../attract_mode.c) | 0173-0195 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0196 | [`slow_print_score_average_table`](../../attract_mode.c#L198) | [attract_mode.c](../../attract_mode.c) | 0196-01CD | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$01CE** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **01CE-01CF** | |
| $01D0 | [`print_text_lines`](../../utilities.c#L62) | [utilities.c](../../utilities.c) | 01D0-01E0 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $01E1 | [`l01e1`](../../misc_logic.c#L24) | [misc_logic.c](../../misc_logic.c) | 01E1-01EB | Zelfde adres als: `print_copyright_lines` — controleer welke live is |
| $01E1 | [`print_copyright_lines`](../../utilities.c#L96) | [utilities.c](../../utilities.c) | 01E1-01EB | Zelfde adres als: `l01e1` — controleer welke live is |
| **$01EC** | **Padding (1 bytes of FF)** | **---** | **01EC-01EC** | |
| $01ED | [`draw_row`](../../utilities.c#L107) | [utilities.c](../../utilities.c) | 01ED-01F7 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$01F8** | **Padding (8 bytes of FF)** | **---** | **01F8-01FF** | |
| $0200 | [`add_one_to_mem`](../../utilities.c#L202) | [utilities.c](../../utilities.c) | 0200-0205 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0206 | [`add_bc_to_mem`](../../utilities.c#L217) | [utilities.c](../../utilities.c) | 0206-020E | Geïnlined bij de C-aanroepplekken (o.a. slow-print $01AB); losse functie ongebruikt |
| **$020F** | **Padding (1 bytes of FF)** | **---** | **020F-020F** | |
| $0210 | [`left_one_column`](../../utilities.c#L303) | [utilities.c](../../utilities.c) | 0210-0216 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0217 | [`right_one_column`](../../utilities.c#L312) | [utilities.c](../../utilities.c) | 0217-021D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$021E** | **Padding (2 bytes of FF)** | **---** | **021E-021F** | |
| $0220 | [`add_to_score`](../../utilities.c#L321) | [utilities.c](../../utilities.c) | 0220-0232 | Vervangen door `add_score()` (scoring.c) bij de aanroepplekken $2731/$275C; losse functie ongebruikt |
| **$0233** | **Padding (3 bytes of FF)** | **---** | **0233-0235** | |
| $0236 | [`unused_bcd_subtracter`](../../utilities.c#L153) | [utilities.c](../../utilities.c) | 0236-0252 | Vermoedelijk dode code: niet geraakt door c-phoenix of echte Z80, geen asm-referentie |
| **$0253** | **Padding (5 bytes of FF)** | **---** | **0253-0257** | |
| $0258 | [`compare_bc_to_mem`](../../utilities.c#L234) | [utilities.c](../../utilities.c) | 0258-025F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0260 | [`l0260_subtract_if_enough`](../../utilities.c#L244) | [utilities.c](../../utilities.c) | 0260-0267 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0268** | **Padding (8 bytes of FF)** | **---** | **0268-026F** | |
| $0270 | [`l0270_subtract_from_memory`](../../utilities.c#L259) | [utilities.c](../../utilities.c) | 0270-0276 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0277 | [`l0277_subtract_to_memory`](../../utilities.c#L270) | [utilities.c](../../utilities.c) | 0277-027D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$027E** | ***** UNREFERENCED DATA (Bytes: FF FF 7D B9 C C0 7C B8...) ***** | **---** | **027E-0287** | |
| $0288 | [`prompt_for_start_game`](../../attract_mode.c#L293) | [attract_mode.c](../../attract_mode.c) | 0288-02EE | Deels geverifieerd (89.6% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $02CB | [`decrement_coins`](../../attract_mode.c#L366) | [attract_mode.c](../../attract_mode.c) | 02CB-02EF | Deels geverifieerd (80.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $02F0 | [`update_hi_score`](../../state_init.c#L120) | [state_init.c](../../state_init.c) | 02F0-032D | Deels geverifieerd (92.1% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $032E | [`clear_and_print_scores`](../../hw_video_audio.c#L196) | [hw_video_audio.c](../../hw_video_audio.c) | 032E-034E | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$034F** | **Padding (1 bytes of FF)** | **---** | **034F-034F** | |
| $0350 | [`get_player_lives_from_dip`](../../state_init.c#L89) | [state_init.c](../../state_init.c) | 0350-0366 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0367 | [`update_lives_screen`](../../hw_video_audio.c#L216) | [hw_video_audio.c](../../hw_video_audio.c) | 0367-0376 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0377 | [`update_sound_control_ram`](../../hw_video_audio.c#L228) | [hw_video_audio.c](../../hw_video_audio.c) | 0377-037D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$037E** | **Padding (2 bytes of FF)** | **---** | **037E-037F** | |
| $0380 | [`clear_foreground`](../../hw_video_audio.c#L237) | [hw_video_audio.c](../../hw_video_audio.c) | 0380-039D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$039E** | **Padding (2 bytes of FF)** | **---** | **039E-039F** | |
| $03A0 | [`clear_background`](../../hw_video_audio.c#L155) | [hw_video_audio.c](../../hw_video_audio.c) | 03A0-03AF | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $03B0 | [`check_demo_mode_player_and_alien`](../../attract_mode.c#L252) | [attract_mode.c](../../attract_mode.c) | 03B0-03FD | Deels geverifieerd (93.9% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$03FE** | **Padding (2 bytes of FF)** | **---** | **03FE-03FF** | |
| $0400 | [`game_state_machine`](../../game_state_machine.c#L32) | [game_state_machine.c](../../game_state_machine.c) | 0400-041D |  |
| $041E | [`set_bits_video_register`](../../hw_video_audio.c#L252) | [hw_video_audio.c](../../hw_video_audio.c) | 041E-042E | Deels geverifieerd (88.9% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$042F** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **042F-042F** | |
| $0430 | [`state_0_new_game_start`](../../game_state_machine.c#L54) | [game_state_machine.c](../../game_state_machine.c) | 0430-045B, 04A0-04AB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$045C** | **Padding (4 bytes of FF)** | **---** | **045C-045F** | |
| $0460 | [`stars_scroll_down`](../../hw_video_audio.c#L266) | [hw_video_audio.c](../../hw_video_audio.c) | 0460-049D, 067A-06AF | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0460 | [`copy_memory_bank`](../../platform_sdl.c#L95) | [platform_sdl.c](../../platform_sdl.c) | 0460-049D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$049E** | **Padding (2 bytes of FF)** | **---** | **049E-049F** | |
| $04A0 | [`l04a0_change_player_at_attract_mode`](../../game_state_machine.c#L98) | [game_state_machine.c](../../game_state_machine.c) | 04A0-04AB | Deels geverifieerd (83.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $04AC | [`state_1_flashing_score`](../../game_state_machine.c#L132) | [game_state_machine.c](../../game_state_machine.c) | 04AC-04E4, 04E6-04F9, 04FB-0505 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$04E5** | **Padding (1 bytes of FF)** | **---** | **04E5-04E5** | |
| **$04FA** | **Padding (1 bytes of FF)** | **---** | **04FA-04FA** | |
| $04FB | [`delete_digits`](../../utilities.c#L361) | [utilities.c](../../utilities.c) | 04FB-0505 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0506 | [`init_alien_movement_pointers`](../../state_init.c#L46) | [state_init.c](../../state_init.c) | 0506-0514 | Wel aangesloten (state_init.c:81), maar guard-conditie nooit getriggerd door testscripts |
| $0515 | [`state_2_init_game_and_level_data`](../../state_init.c#L70) | [state_init.c](../../state_init.c) | 0515-0531 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0526 | [`l0526`](../../state_init.c#L56) | [state_init.c](../../state_init.c) | 0526-0531 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0532 | [`init_alien_data_new_level`](../../state_init.c#L33) | [state_init.c](../../state_init.c) | 0532-0543 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0544** | **Padding (3 bytes of FF)** | **---** | **0544-0546** | |
| $0547 | [`init_player_data_structure`](../../state_init.c#L26) | [state_init.c](../../state_init.c) | 0547-055A |  |
| **$055B** | **Padding (5 bytes of FF)** | **---** | **055B-055F** | |
| **$0596** | **Padding (2 bytes of FF)** | **---** | **0596-0597** | |
| $05D8 | [`clear_b_bytes_at_hl`](../../utilities.c#L123) | [utilities.c](../../utilities.c) | 05D8-05DF | Geïnlined als memset bij de init-aanroepplekken ($0158/$050B/$0537/$0557); losse functie ongebruikt |
| $05E0 | [`copy_b_bytes_hl_to_de`](../../utilities.c#L137) | [utilities.c](../../utilities.c) | 05E0-05E8 | Geïnlined als memcpy/loops bij de aanroepplekken ($054F/$0592/$32E3); losse functie ongebruikt |
| **$05E9** | **Padding (3 bytes of FF)** | **---** | **05E9-05EB** | |
| $05EC | [`init_alien_control_states`](../../alien_logic.c#L19) | [alien_logic.c](../../alien_logic.c) | 05EC-05F9 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $05FA | [`init_alien_control_states_05fa`](../../alien_logic.c#L207) | [alien_logic.c](../../alien_logic.c) | 05FA-060D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$060E** | **Padding (2 bytes of FF)** | **---** | **060E-060F** | |
| $0610 | [`init_alien_positions`](../../alien_logic.c#L224) | [alien_logic.c](../../alien_logic.c) | 0610-0638 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0639** | **Padding (1 bytes of FF)** | **---** | **0639-0639** | |
| **$064A** | **Padding (6 bytes of FF)** | **---** | **064A-064F** | |
| $0650 | [`copy_init_values_for_16_aliens`](../../alien_logic.c#L249) | [alien_logic.c](../../alien_logic.c) | 0650-0679 | Deels geverifieerd (75.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $06B0 | [`add_planets_to_background`](../../hw_video_audio.c#L356) | [hw_video_audio.c](../../hw_video_audio.c) | 06B0-06E7 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $06E8 | [`print_score_column`](../../utilities.c#L87) | [utilities.c](../../utilities.c) | 06E8-06ED | Geïnlined in state_1_flashing_score (asm-aanroep $04C9); losse functie ongebruikt |
| **$06EE** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **06EE-06EF** | |
| $06F0 | [`update_scroll_register_and_fill_background`](../../hw_video_audio.c#L473) | [hw_video_audio.c](../../hw_video_audio.c) | 06F0-06F8 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $06F0 | [`l06f0`](../../misc_logic.c#L12) | [misc_logic.c](../../misc_logic.c) | 06F0-0701 | Deels geverifieerd (80.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0700 | [`player_data_controller`](../../player_logic.c#L250) | [player_logic.c](../../player_logic.c) | 0700-0717 | Deels geverifieerd (92.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0718 | [`update_screen_objects`](../../sprite_rendering.c#L215) | [sprite_rendering.c](../../sprite_rendering.c) | 0718-071F | Deels geverifieerd (66.7% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0720 | [`bit4_controller`](../../sprite_rendering.c#L150) | [sprite_rendering.c](../../sprite_rendering.c) | 0720-073F | Deels geverifieerd (88.9% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0740 | [`bit3_controller`](../../sprite_rendering.c#L179) | [sprite_rendering.c](../../sprite_rendering.c) | 0740-07EE | Deels geverifieerd (92.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $07DC | [`draw_background_2x2`](../../hw_video_audio.c#L320) | [hw_video_audio.c](../../hw_video_audio.c) | 07DC-07EF | Deels geverifieerd (94.4% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $07F0 | [`l07f0`](../../game_state_machine.c#L118) | [game_state_machine.c](../../game_state_machine.c) | 07F0-07FA | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$07FB** | **Padding (5 bytes of FF)** | **---** | **07FB-07FF** | |
| $0800 | [`state_3_normal_game_play`](../../state_play.c#L237) | [state_play.c](../../state_play.c) | 0800-0833 | Deels geverifieerd (39.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0834 | [`level_0_and_2_aliens_fade_in`](../../state_play.c#L205) | [state_play.c](../../state_play.c) | 0834-0859 | Deels geverifieerd (94.7% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $085A | [`get_animation_chrs_aliens_fade_in`](../../alien_logic.c#L31) | [alien_logic.c](../../alien_logic.c) | 085A-0871 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0872** | **Padding (4 bytes of FF)** | **---** | **0872-0875** | |
| $0876 | [`player_update`](../../player_logic.c#L35) | [player_logic.c](../../player_logic.c) | 0876-0885 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0886 | [`copy_current_to_old_player_data`](../../player_logic.c#L49) | [player_logic.c](../../player_logic.c) | 0886-0897 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0898** | **Padding (8 bytes of FF)** | **---** | **0898-089F** | |
| $08A0 | [`update_player_position_bullet_shield`](../../player_logic.c#L94) | [player_logic.c](../../player_logic.c) | 08A0-08B7 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$08B8** | **Padding (12 bytes of FF)** | **---** | **08B8-08C3** | |
| $08C4 | [`move_player`](../../player_logic.c#L114) | [player_logic.c](../../player_logic.c) | 08C4-08F3 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$08F4** | **Padding (12 bytes of FF)** | **---** | **08F4-08FF** | |
| $0900 | [`update_player_ship_x`](../../player_logic.c#L66) | [player_logic.c](../../player_logic.c) | 0900-0921, 0926-092E | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0922** | **Padding (4 bytes of FF)** | **---** | **0922-0925** | |
| $0926 | [`get_player_ship_animation_frame_values`](../../player_logic.c#L189) | [player_logic.c](../../player_logic.c) | 0926-092E | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$092F** | **Padding (1 bytes of FF)** | **---** | **092F-092F** | |
| $0930 | [`get_assigned_player_bullet_tile`](../../player_logic.c#L168) | [player_logic.c](../../player_logic.c) | 0930-093C | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $093D | [`spawn_player_bullet`](../../player_logic.c#L203) | [player_logic.c](../../player_logic.c) | 093D-0961 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0962** | **Padding (2 bytes of FF)** | **---** | **0962-0963** | |
| $0964 | [`update_player_bullet_y`](../../player_logic.c#L236) | [player_logic.c](../../player_logic.c) | 0964-0975 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $096E | [`l096e_clear_bullet`](../../weapon_collision.c#L21) | [weapon_collision.c](../../weapon_collision.c) | 096E-0975 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0976** | ***** UNREFERENCED DATA (Bytes: FF FF 7E E6) ***** | **---** | **0976-0979** | |
| $097A | [`map_player_ship_position`](../../player_logic.c#L153) | [player_logic.c](../../player_logic.c) | 097A-0995 | Deels geverifieerd (88.2% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$0996** | **Padding (10 bytes of FF)** | **---** | **0996-099F** | |
| $09A0 | [`get_screen_ram_address_for_player_ship`](../../utilities.c#L187) | [utilities.c](../../utilities.c) | 09A0-09B5 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$09B6** | **Padding (4 bytes of FF)** | **---** | **09B6-09B9** | |
| $09BA | [`get_screen_ram_address`](../../utilities.c#L163) | [utilities.c](../../utilities.c) | 09BA-09D1 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$09D2** | **Padding (46 bytes of FF)** | **---** | **09D2-09FF** | |
| **$0A4C** | **Padding (4 bytes of FF)** | **---** | **0A4C-0A4F** | |
| $0A50 | [`alien_data_controller`](../../alien_logic.c#L274) | [alien_logic.c](../../alien_logic.c) | 0A50-0A6B | Deels geverifieerd (93.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0A6C | [`get_screen_ram_address_for_all_aliens`](../../alien_logic.c#L290) | [alien_logic.c](../../alien_logic.c) | 0A6C-0A99 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0A9A** | **Padding (6 bytes of FF)** | **---** | **0A9A-0A9F** | |
| $0AA0 | [`draw_shields`](../../player_logic.c#L294) | [player_logic.c](../../player_logic.c) | 0AA0-0AC1 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0AC2** | **Padding (20 bytes of FF)** | **---** | **0AC2-0AD5** | |
| $0AD6 | [`draw_image_c_by_b`](../../utilities.c#L283) | [utilities.c](../../utilities.c) | 0AD6-0AE9 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0AEA | [`state_4_player_ship_explosion`](../../state_endings.c#L33) | [state_endings.c](../../state_endings.c) | 0AEA-0B0F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0B10** | ***** UNREFERENCED DATA (Bytes: 70 20 C3 E8 20) ***** | **---** | **0B10-0B14** | |
| $0B15 | [`l0b15`](../../state_endings.c#L208) | [state_endings.c](../../state_endings.c) | 0B15-0B2D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0B2E** | ***** UNREFERENCED DATA (Bytes: FF FF FF F0 E0 B0 C0 D0...) ***** | **---** | **0B2E-0B37** | |
| $0B48 | [`shields_expired`](../../player_logic.c#L276) | [player_logic.c](../../player_logic.c) | 0B48-0B5A | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0B5B** | **Padding (5 bytes of FF)** | **---** | **0B5B-0B5F** | |
| $0B60 | [`state_5_game_over_text`](../../state_endings.c#L67) | [state_endings.c](../../state_endings.c) | 0B60-0B9D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0B9E** | **Padding (2 bytes of FF)** | **---** | **0B9E-0B9F** | |
| $0BA0 | [`l0ba0`](../../state_endings.c#L238) | [state_endings.c](../../state_endings.c) | 0BA0-0BB2 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0BB3** | **Padding (7 bytes of FF)** | **---** | **0BB3-0BB9** | |
| $0BBA | [`l0bba`](../../state_endings.c#L256) | [state_endings.c](../../state_endings.c) | 0BBA-0BC4 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0BC5** | **Padding (5 bytes of FF)** | **---** | **0BC5-0BC9** | |
| $0BCA | [`draw_score_average_table_tiles`](../../attract_mode.c#L419) | [attract_mode.c](../../attract_mode.c) | 0BCA-0BF1 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0BF2** | **Padding (14 bytes of FF)** | **---** | **0BF2-0BFF** | |
| $0C00 | [`l0c00_kill_score`](../../weapon_collision.c#L209) | [weapon_collision.c](../../weapon_collision.c) | 0C00-0C23 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0C24** | **Padding (28 bytes of FF)** | **---** | **0C24-0C3F** | |
| $0C40 | [`process_enemy_bombs`](../../weapon_collision.c#L163) | [weapon_collision.c](../../weapon_collision.c) | 0C40-0C51 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0C52** | **Padding (4 bytes of FF)** | **---** | **0C52-0C55** | |
| $0C56 | [`enemy_bullet_movement_and_animation`](../../weapon_collision.c#L119) | [weapon_collision.c](../../weapon_collision.c) | 0C56-0C67 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0C68** | **Padding (3 bytes of FF)** | **---** | **0C68-0C6A** | |
| $0C6B | [`get_screen_ram_address_for_enemy_bullets`](../../weapon_collision.c#L132) | [weapon_collision.c](../../weapon_collision.c) | 0C6B-0C80 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0C81** | **Padding (3 bytes of FF)** | **---** | **0C81-0C83** | |
| $0C84 | [`l0c84_enemy_bullet_movement`](../../weapon_collision.c#L63) | [weapon_collision.c](../../weapon_collision.c) | 0C84-0CB3 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0CB4 | [`l0cb4_check_bullet_hit_player`](../../weapon_collision.c#L30) | [weapon_collision.c](../../weapon_collision.c) | 0CB4-0CD4 | Deels geverifieerd (94.4% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0CC4 | [`l0cc4_player_killed`](../../weapon_collision.c#L51) | [weapon_collision.c](../../weapon_collision.c) | 0CC4-0CD3 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0CD5** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **0CD5-0CD7** | |
| $0CD8 | [`enemy_bullet_data_controller`](../../weapon_collision.c#L148) | [weapon_collision.c](../../weapon_collision.c) | 0CD8-0CEF | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0CF0** | ***** DATA TABLE (Refs: $0D02, $0D04) ***** | **---** | **0CF0-0D1B** | |
| $0D1C | [`alien_movement_update`](../../alien_logic.c#L335) | [alien_logic.c](../../alien_logic.c) | 0D1C-0D67 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0D68** | **Padding (8 bytes of FF)** | **---** | **0D68-0D6F** | |
| $0D70 | [`alien_animation_update`](../../alien_logic.c#L382) | [alien_logic.c](../../alien_logic.c) | 0D70-0DB5, 0DBB-0DC6, 0DCC-0DEE | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0DB6** | **Padding (5 bytes of FF)** | **---** | **0DB6-0DBA** | |
| **$0DC7** | **Padding (5 bytes of FF)** | **---** | **0DC7-0DCB** | |
| **$0DEF** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **0DEF-0DEF** | |
| $0DF0 | [`check_enemy_bullet_to_player_collision`](../../weapon_collision.c#L189) | [weapon_collision.c](../../weapon_collision.c) | 0DF0-0E01 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $0E02 | [`l0e02_unused`](../../weapon_collision.c#L199) | [weapon_collision.c](../../weapon_collision.c) | 0E02-0E0B | Vermoedelijk dode code: niet geraakt door c-phoenix of echte Z80, geen asm-referentie |
| **$0E0C** | **Padding (4 bytes of FF)** | **---** | **0E0C-0E0F** | |
| $0E10 | [`l0e10`](../../weapon_collision.c#L228) | [weapon_collision.c](../../weapon_collision.c) | 0E10-0E36, 0E39-0E6B, 0E58-0E6B, 0E70-0EA0 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0E37** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **0E37-0E38** | |
| **$0E6C** | **Padding (4 bytes of FF)** | **---** | **0E6C-0E6F** | |
| **$0EA1** | **Padding (3 bytes of 00)** | **---** | **0EA1-0EA3** | |
| $0EA4 | [`l0ea4_with_score`](../../weapon_collision.c#L296) | [weapon_collision.c](../../weapon_collision.c) | 0EA4-0EE5 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0EE6** | **Padding (26 bytes of FF)** | **---** | **0EE6-0EFF** | |
| $0F00 | [`l0f00_check_alien_with_player_collision`](../../weapon_collision.c#L375) | [weapon_collision.c](../../weapon_collision.c) | 0F00-0F33, 0F38-0F4E, 0F74-0FB9 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0F34** | **Padding (4 bytes of FF)** | **---** | **0F34-0F37** | |
| **$0F4F** | ***** UNREFERENCED DATA (Bytes: AD 0E FF FF FF) ***** | **---** | **0F4F-0F55** | |
| $0F56 | [`l0f56_screen_ram_collision`](../../weapon_collision.c#L347) | [weapon_collision.c](../../weapon_collision.c) | 0F56-0F71 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$0F72** | **Padding (2 bytes of FF)** | **---** | **0F72-0F73** | |
| **$0FBA** | ***** UNREFERENCED DATA (Bytes: AD 0E FF FF) ***** | **---** | **0FBA-0FBF** | |
| $0FC0 | [`handle_animations_for_killed_aliens`](../../alien_logic.c#L195) | [alien_logic.c](../../alien_logic.c) | 0FC0-0FFF | Deels geverifieerd (88.2% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $0FD8 | [`l0fd8`](../../alien_logic.c#L43) | [alien_logic.c](../../alien_logic.c) | 0FD8-0FEF | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $14E0 | [`l14e0`](../../rom_compat_stubs.c#L15) | [rom_compat_stubs.c](../../rom_compat_stubs.c) | 14E0-14FD | Coin-check-continuatie van de slow-print ($01CA); in C centraal afgehandeld in wait_vblank_coin — stub bewust leeg |
| **$1768** | **Padding (8 bytes of FF)** | **---** | **1768-176F** | |
| $17E0 | [`coin_checking`](../../attract_mode.c#L281) | [attract_mode.c](../../attract_mode.c) | 17E0-17ED | Deels geverifieerd (50.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $1DF0 | [`l1df0`](../../rom_compat_stubs.c#L22) | [rom_compat_stubs.c](../../rom_compat_stubs.c) | 1DF0-1DFF | Deels geverifieerd (27.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $1EE0 | [`l1ee0`](../../attract_mode.c#L583) | [attract_mode.c](../../attract_mode.c) | 1EE0-1EFA | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$1EFB** | **Padding (5 bytes of FF)** | **---** | **1EFB-1EFF** | |
| $2000 | [`l2000_alien_wave_main_loop`](../../alien_wave.c#L220) | [alien_wave.c](../../alien_wave.c) | 2000-202A | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$202B** | ***** UNREFERENCED DATA (Bytes: FF FF FF E6 03 A FE 01...) ***** | **---** | **202B-203F** | |
| $2040 | [`add_galaxies_to_background`](../../hw_video_audio.c#L433) | [hw_video_audio.c](../../hw_video_audio.c) | 2040-208A | Deels geverifieerd (94.5% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2070 | [`l2070`](../../player_explosion.c#L118) | [player_explosion.c](../../player_explosion.c) | 2070-2084 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$20AB** | **Padding (5 bytes of FF)** | **---** | **20AB-20AF** | |
| $20B0 | [`l20b0_player_ship_particles_explosion`](../../player_explosion.c#L76) | [player_explosion.c](../../player_explosion.c) | 20B0-20E2 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$20E3** | ***** UNREFERENCED DATA (Bytes: 20 FF FF FF FF) ***** | **---** | **20E3-20E7** | |
| $20E8 | [`l20e8`](../../player_explosion.c#L32) | [player_explosion.c](../../player_explosion.c) | 20E8-210D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$210E** | **Padding (14 bytes of FF)** | **---** | **210E-211B** | |
| $211C | [`l211c`](../../player_explosion.c#L16) | [player_explosion.c](../../player_explosion.c) | 211C-212C | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$212D** | **Padding (3 bytes of FF)** | **---** | **212D-212F** | |
| $2130 | [`l2130`](../../alien_wave.c#L205) | [alien_wave.c](../../alien_wave.c) | 2130-2145 | Deels geverifieerd (66.7% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2146 | [`l2146`](../../alien_wave.c#L193) | [alien_wave.c](../../alien_wave.c) | 2146-214F | Deels geverifieerd (66.7% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2150 | [`l2150`](../../alien_wave.c#L134) | [alien_wave.c](../../alien_wave.c) | 2150-215F | Deels geverifieerd (75.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2160 | [`l2160`](../../alien_wave.c#L143) | [alien_wave.c](../../alien_wave.c) | 2160-216F | Deels geverifieerd (80.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2170 | [`l2170`](../../alien_wave.c#L153) | [alien_wave.c](../../alien_wave.c) | 2170-217F | Deels geverifieerd (66.7% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2180 | [`l2180`](../../alien_wave.c#L161) | [alien_wave.c](../../alien_wave.c) | 2180-218F | Deels geverifieerd (80.0% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $2190 | [`l2190`](../../alien_wave.c#L171) | [alien_wave.c](../../alien_wave.c) | 2190-21A4 | Deels geverifieerd (83.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $21A5 | [`l21a5`](../../alien_wave.c#L182) | [alien_wave.c](../../alien_wave.c) | 21A5-21B9 | Deels geverifieerd (83.3% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $21BA | [`l21ba`](../../alien_wave.c#L104) | [alien_wave.c](../../alien_wave.c) | 21BA-21CF | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$21D0** | ***** UNREFERENCED DATA (Bytes: 3E 10 32 BA 43 C3 26 05...) ***** | **---** | **21D0-2203** | |
| $2204 | [`l2204`](../../alien_wave.c#L80) | [alien_wave.c](../../alien_wave.c) | 2204-222B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$222C** | **Padding (4 bytes of FF)** | **---** | **222C-222F** | |
| $2230 | [`level_4_6_8_spiral_fill`](../../state_play.c#L119) | [state_play.c](../../state_play.c) | 2230-225F | Live vertaling van L2230 (dode duplicaat `spiral_fill_animation` verwijderd 11 juli 2026) |
| $2260 | [`l2260_spiral_draw`](../../state_play.c#L26) | [state_play.c](../../state_play.c) | 2260-2291 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $2292 | [`l2292_spiral_routine`](../../state_play.c#L84) | [state_play.c](../../state_play.c) | 2292-22B3 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $22B4 | [`level_9_mothership_fade_in`](../../state_play.c#L163) | [state_play.c](../../state_play.c) | 22B4-22C5 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$22C6** | **Padding (4 bytes of FF)** | **---** | **22C6-22C9** | |
| $22CA | [`level_A_mothership_and_aliens_fade_in`](../../state_play.c#L188) | [state_play.c](../../state_play.c) | 22CA-22DD | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$22DE** | ***** UNREFERENCED DATA (Bytes: FF FF 3E 71 32 B9 43 32...) ***** | **---** | **22DE-2339** | |
| $2351 | [`l2351_mothership_animation`](../../mothership_impl.c#L12) | [mothership_impl.c](../../mothership_impl.c) | 2351-23C7 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$23C8** | ***** UNREFERENCED DATA (Bytes: 36 06 2C 36 60 2E 63 36...) ***** | **---** | **23C8-23D5** | |
| $23D6 | [`l23d6`](../../sound_dispatcher.c#L21) | [sound_dispatcher.c](../../sound_dispatcher.c) | 23D6-23FB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$23FC** | **Padding (4 bytes of FF)** | **---** | **23FC-23FF** | |
| $2400 | [`state_6_mother_ship_explosion`](../../state_endings.c#L126) | [state_endings.c](../../state_endings.c) | 2400-244B | Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact) |
| $242C | [`update_counters_for_mothership_explosion`](../../mothership_impl.c#L134) | [mothership_impl.c](../../mothership_impl.c) | 242C-2442 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $244C | [`state_7_mother_ship_score_display`](../../state_endings.c#L179) | [state_endings.c](../../state_endings.c) | 244C-2469 | Deels geverifieerd (94.4% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $246A | [`erase_mothership`](../../mothership_logic.c#L22) | [mothership_logic.c](../../mothership_logic.c) | 246A-2475 | Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact) |
| **$2494** | ***** UNREFERENCED DATA (Bytes: 1F) ***** | **---** | **2494-2494** | |
| $24A0 | [`l24a0`](../../misc_logic.c#L37) | [misc_logic.c](../../misc_logic.c) | 24A0-24BB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$24BC** | ***** UNREFERENCED DATA (Bytes: CD 51 23 CA C9 FF FF FF...) ***** | **---** | **24BC-24C3** | |
| $24C4 | [`l24c4`](../../alien_wave.c#L29) | [alien_wave.c](../../alien_wave.c) | 24C4-24DF | Deels geverifieerd (84.6% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$24E0** | ***** UNREFERENCED DATA (Bytes: 3A AA 43 E6 0F A C0 3A...) ***** | **---** | **24E0-24F1** | |
| $24F2 | [`l24f2`](../../misc_logic.c#L55) | [misc_logic.c](../../misc_logic.c) | 24F2-251C | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$251D** | **Padding (3 bytes of FF)** | **---** | **251D-251F** | |
| $2520 | [`mothership_core_hit_check`](../../mothership_logic.c#L48) | [mothership_logic.c](../../mothership_logic.c) | 2520-254F | Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact) |
| **$2550** | ***** UNREFERENCED DATA (Bytes: 32 80) ***** | **---** | **2550-2551** | |
| $2552 | [`l2552_mothership_explosion_done`](../../state_endings.c#L102) | [state_endings.c](../../state_endings.c) | 2552-255D | Live (bereikt in echte gameplay, zie my_session.txt-fix 9 juli; scripted-coverage-verschil was harnas-artefact) |
| **$255E** | **Padding (2 bytes of FF)** | **---** | **255E-255F** | |
| $2560 | [`l2560`](../../alien_logic.c#L778) | [alien_logic.c](../../alien_logic.c) | 2560-2595 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $2596 | [`l2596`](../../alien_logic.c#L744) | [alien_logic.c](../../alien_logic.c) | 2596-25B6 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $25B7 | [`l25b7`](../../utilities.c#L404) | [utilities.c](../../utilities.c) | 25B7-25FD | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$25FE** | **Padding (2 bytes of FF)** | **---** | **25FE-25FF** | |
| $2600 | [`birds_vertical_movement_update`](../../birds_vertical_movement.c#L112) | [birds_vertical_movement.c](../../birds_vertical_movement.c) | 2600-2664 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$2665** | ***** UNREFERENCED DATA (Bytes: D2 AE 26) ***** | **---** | **2665-2667** | |
| $2668 | [`l2668`](../../birds_vertical_movement.c#L15) | [birds_vertical_movement.c](../../birds_vertical_movement.c) | 2668-26A7 | Deels geverifieerd (93.9% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$26A8** | ***** UNREFERENCED DATA (Bytes: 00 58) ***** | **---** | **26A8-26A9** | |
| $26AA | [`l26aa`](../../birds_vertical_movement.c#L60) | [birds_vertical_movement.c](../../birds_vertical_movement.c) | 26AA-26CC, 2476-2493, 2495-249F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$26CD** | ***** UNREFERENCED DATA (Bytes: C9) ***** | **---** | **26CD-26CF** | |
| $26D0 | [`l26d0`](../../birds_vertical_movement.c#L36) | [birds_vertical_movement.c](../../birds_vertical_movement.c) | 26D0-26FD | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$26FE** | ***** UNREFERENCED DATA (Bytes: FF FF 21 A2 43 7E A7 A...) ***** | **---** | **26FE-27BC** | |
| $27BD | [`l27bd`](../../sound_dispatcher.c#L35) | [sound_dispatcher.c](../../sound_dispatcher.c) | 27BD-27EE | Deels geverifieerd (93.5% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$27EF** | **Padding (17 bytes of FF)** | **---** | **27EF-27FF** | |
| $3000 | [`l3000`](../../alien_wave.c#L255) | [alien_wave.c](../../alien_wave.c) | 3000-3012 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3013** | ***** UNREFERENCED DATA (Bytes: FF FF FF FF FF 32 64 30...) ***** | **---** | **3013-3027** | |
| $3028 | [`l3028`](../../alien_logic.c#L528) | [alien_logic.c](../../alien_logic.c) | 3028-3059, 305C-306D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$305A** | **Padding (2 bytes of FF)** | **---** | **305A-305B** | |
| **$306E** | **Padding (6 bytes of FF)** | **---** | **306E-3073** | |
| $3074 | [`l3074_breakout_delay`](../../alien_logic.c#L501) | [alien_logic.c](../../alien_logic.c) | 3074-30A8 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$30A9** | **Padding (1 bytes of FF)** | **---** | **30A9-30A9** | |
| $30AA | [`get_random_number`](../../utilities.c#L386) | [utilities.c](../../utilities.c) | 30AA-30B8 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$30B9** | ***** UNREFERENCED DATA (Bytes: C0) ***** | **---** | **30B9-30B9** | |
| $30BA | [`l30ba`](../../alien_logic.c#L562) | [alien_logic.c](../../alien_logic.c) | 30BA-30D8, 30E4-310F, 3112-3121 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$30D9** | ***** UNREFERENCED DATA (Bytes: FE 2C 7E A7 A C8 35 DEC...) ***** | **---** | **30D9-30E3** | |
| **$3110** | ***** UNREFERENCED DATA (Bytes: 21 50) ***** | **---** | **3110-3111** | |
| **$3122** | ***** UNREFERENCED DATA (Bytes: 86 ADD A 47) ***** | **---** | **3122-3123** | |
| $3124 | [`l3124`](../../alien_logic.c#L607) | [alien_logic.c](../../alien_logic.c) | 3124-314E | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$314F** | ***** UNREFERENCED DATA (Bytes: 0A 0C 0B 0C 0B 0E 0F 0E...) ***** | **---** | **314F-3159** | |
| $315A | [`l315a`](../../alien_logic.c#L629) | [alien_logic.c](../../alien_logic.c) | 315A-318E, 3192-31AD | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$318F** | **Padding (3 bytes of FF)** | **---** | **318F-3191** | |
| **$31AE** | **Padding (6 bytes of FF)** | **---** | **31AE-31B3** | |
| $31B4 | [`l31b4`](../../alien_logic.c#L662) | [alien_logic.c](../../alien_logic.c) | 31B4-320D, 3210-3228 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$320E** | ***** UNREFERENCED DATA (Bytes: 81 ADD A 6F) ***** | **---** | **320E-320F** | |
| **$3229** | ***** UNREFERENCED DATA (Bytes: C0 21 50) ***** | **---** | **3229-322B** | |
| $322C | [`l322c`](../../alien_logic.c#L718) | [alien_logic.c](../../alien_logic.c) | 322C-325E | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$325F** | ***** UNREFERENCED DATA (Bytes: 3C E6 0F 77 2E) ***** | **---** | **325F-3263** | |
| $3264 | [`l3264`](../../alien_logic.c#L459) | [alien_logic.c](../../alien_logic.c) | 3264-32AF | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $32B0 | [`l32b0`](../../misc_logic.c#L73) | [misc_logic.c](../../misc_logic.c) | 32B0-32EB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$32EC** | ***** UNREFERENCED DATA (Bytes: CD E0 05 CA C3 A0 03 FF...) ***** | **---** | **32EC-32FF** | |
| **$3308** | **Padding (8 bytes of FF)** | **---** | **3308-330F** | |
| $3400 | [`process_birds`](../../bird_logic.c#L27) | [bird_logic.c](../../bird_logic.c) | 3400-3436, 3438-344D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3437** | **Padding (1 bytes of FF)** | **---** | **3437-3437** | |
| **$344E** | **Padding (4 bytes of FF)** | **---** | **344E-3451** | |
| $3452 | [`update_second_bird_bank`](../../bird_wave_behavior.c#L14) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3452-345B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$345C** | **Padding (6 bytes of FF)** | **---** | **345C-3461** | |
| $3462 | [`l3462_no_birds_left`](../../collision_detection.c#L174) | [collision_detection.c](../../collision_detection.c) | 3462-346D | Live (scripted-coverage-verschil was een harnas-artefact) |
| **$346E** | **Padding (6 bytes of FF)** | **---** | **346E-3473** | |
| $3474 | [`draw_first_4_bird_objects`](../../bird_logic.c#L81) | [bird_logic.c](../../bird_logic.c) | 3474-3485 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3486 | [`draw_second_4_bird_objects`](../../bird_logic.c#L93) | [bird_logic.c](../../bird_logic.c) | 3486-3497 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3498 | [`update_first_four_birds`](../../bird_wave_behavior.c#L251) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3498-34A9 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $34AA | [`update_second_four_birds`](../../bird_wave_behavior.c#L261) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 34AA-34BB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$34BC** | **Padding (4 bytes of FF)** | **---** | **34BC-34BF** | |
| $34C0 | [`drawbirdobject`](../../attract_mode.c#L472) | [attract_mode.c](../../attract_mode.c) | 34C0-355D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $34DE | [`draw_bird_shape_34de`](../../attract_mode.c#L557) | [attract_mode.c](../../attract_mode.c) | 34DE-350B | Deels geverifieerd (82.1% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| $350C | [`draw_bird_shape_350c`](../../attract_mode.c#L519) | [attract_mode.c](../../attract_mode.c) | 350C-355D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$355E** | **Padding (2 bytes of FF)** | **---** | **355E-355F** | |
| $3560 | [`refresh_bird_flight_parameters`](../../bird_wave_behavior.c#L270) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3560-359F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$35A0** | ***** UNREFERENCED DATA (Bytes: C9 FF FF FF FF FF FF FF...) ***** | **---** | **35A0-35AF** | |
| $35B0 | [`update_bird_behavior`](../../bird_wave_behavior.c#L218) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 35B0-35DB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$35DC** | **Padding (4 bytes of FF)** | **---** | **35DC-35DF** | |
| $35E0 | [`l35e0_descend`](../../bird_wave_behavior.c#L127) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 35E0-3624 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3625** | **Padding (3 bytes of FF)** | **---** | **3625-3627** | |
| $3628 | [`l3628_climb`](../../bird_wave_behavior.c#L85) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3628-3666 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3667** | ***** UNREFERENCED DATA (Bytes: 77 C9 FF) ***** | **---** | **3667-3669** | |
| $366A | [`l366a_stall`](../../bird_wave_behavior.c#L117) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 366A-3671 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3672 | [`l3672_aim`](../../bird_wave_behavior.c#L47) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3672-3692 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3693** | ***** UNREFERENCED DATA (Bytes: D8 FE) ***** | **---** | **3693-3694** | |
| $3695 | [`l3695_aim_up`](../../bird_wave_behavior.c#L65) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3695-36BB | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$36BC** | ***** UNREFERENCED DATA (Bytes: 77 C9 FF FF) ***** | **---** | **36BC-36BF** | |
| $36C0 | [`l36c0_animate`](../../bird_wave_behavior.c#L165) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 36C0-36C9 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$36CA** | ***** DATA TABLE (Refs: $36CC) ***** | **---** | **36CA-36D1** | |
| $36D2 | [`l36d2_grow`](../../bird_wave_behavior.c#L178) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 36D2-36E6 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$36E7** | **Padding (3 bytes of FF)** | **---** | **36E7-36E9** | |
| $36EA | [`l36ea_grow`](../../bird_wave_behavior.c#L186) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 36EA-3706 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3707** | **Padding (3 bytes of FF)** | **---** | **3707-3709** | |
| **$373F** | **Padding (5 bytes of FF)** | **---** | **373F-3743** | |
| $3744 | [`l3744_restart`](../../bird_wave_behavior.c#L33) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3744-3754 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3755** | **Padding (3 bytes of FF)** | **---** | **3755-3757** | |
| $3758 | [`l3758_bonus_explosion_animation`](../../alien_logic.c#L166) | [alien_logic.c](../../alien_logic.c) | 3758-37CC | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3772 | [`l3758_bonus_explosion_right`](../../alien_logic.c#L114) | [alien_logic.c](../../alien_logic.c) | 3772-3792 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3796 | [`l3796_bonus_explosion_left`](../../alien_logic.c#L100) | [alien_logic.c](../../alien_logic.c) | 3796-37AA | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $37B0 | [`l37b0_print_bonus_score`](../../alien_logic.c#L135) | [alien_logic.c](../../alien_logic.c) | 37B0-37C6 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $37CC | [`l37cc_erase_bonus_explosion`](../../alien_logic.c#L82) | [alien_logic.c](../../alien_logic.c) | 37CC-37E5 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$37E6** | **Padding (26 bytes of FF)** | **---** | **37E6-37FF** | |
| $3800 | [`collision_detection_for_birds`](../../collision_detection.c#L132) | [collision_detection.c](../../collision_detection.c) | 3800-3841, 391C-3922 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3842** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **3842-3843** | |
| $3844 | [`l3844_small_bird_hit`](../../collision_detection.c#L56) | [collision_detection.c](../../collision_detection.c) | 3844-388D, 3894-389C | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$388E** | **Padding (6 bytes of FF)** | **---** | **388E-3893** | |
| **$389D** | **Padding (4 bytes of FF)** | **---** | **389D-38A0** | |
| $38A1 | [`l38a1_erase_bird`](../../collision_detection.c#L20) | [collision_detection.c](../../collision_detection.c) | 38A1-38B5 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$38B6** | ***** UNREFERENCED DATA (Bytes: 35 DEC D1 C9 FF FF FF) ***** | **---** | **38B6-38BB** | |
| $38BC | [`l38bc_large_hit`](../../collision_detection.c#L99) | [collision_detection.c](../../collision_detection.c) | 38BC-38F1 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$38F2** | **Padding (6 bytes of FF)** | **---** | **38F2-38F7** | |
| $38F8 | [`bird_explosion_slot`](../../collision_detection.c#L38) | [collision_detection.c](../../collision_detection.c) | 38F8-391B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3923** | ***** UNREFERENCED DATA (Bytes: C8 35 DEC 2E 8D 7E E6 3F...) ***** | **---** | **3923-392F** | |
| $3930 | [`try_spawn_bird_dive_bomb`](../../bird_wave_behavior.c#L364) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3930-395B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $395C | [`l395c`](../../bird_wave_behavior.c#L337) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 395C-397B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$397C** | **Padding (4 bytes of FF)** | **---** | **397C-397F** | |
| $3980 | [`check_bird_formation_player_collision`](../../bird_wave_behavior.c#L399) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3980-39FD | Deels geverifieerd (93.2% van de range uitgevoerd in byte-exacte runs, 2026-07-12) |
| **$39FE** | **Padding (2 bytes of FF)** | **---** | **39FE-39FF** | |
| $3A00 | [`l3a00`](../../bird_wave_behavior.c#L312) | [bird_wave_behavior.c](../../bird_wave_behavior.c) | 3A00-3A0F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A10 | [`l3a10`](../../sound_dispatcher.c#L265) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A10-3A1C | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A1D | [`l3a1d`](../../sound_dispatcher.c#L72) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A1D-3A2B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A2C | [`l3a2c`](../../sound_dispatcher.c#L62) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A2C-3A3F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A40 | [`l3a40`](../../sound_dispatcher.c#L99) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A40-3A4D | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A4E | [`l3a4e`](../../sound_dispatcher.c#L89) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A4E-3A5F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3A60** | ***** UNREFERENCED DATA (Bytes: 0F 00) ***** | **---** | **3A60-3A61** | |
| $3A62 | [`l3a62`](../../sound_dispatcher.c#L120) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A62-3A77 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A78 | [`l3a78`](../../sound_dispatcher.c#L114) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A78-3A81 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A82 | [`l3a82`](../../sound_dispatcher.c#L134) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A82-3A8F | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3A90 | [`l3a90`](../../sound_dispatcher.c#L143) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A90-3A95 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3A96** | ***** UNREFERENCED DATA (Bytes: ) ***** | **---** | **3A96-3A97** | |
| $3A98 | [`l3a98_scan`](../../sound_dispatcher.c#L154) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3A98-3ACA | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| **$3ACB** | **Padding (5 bytes of FF)** | **---** | **3ACB-3ACF** | |
| $3AD0 | [`l3ad0`](../../sound_dispatcher.c#L186) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3AD0-3AF6 | Live (scripted-coverage-verschil was een harnas-artefact) |
| **$3AF7** | ***** UNREFERENCED DATA (Bytes: 5F) ***** | **---** | **3AF7-3AF7** | |
| $3AF8 | [`l3af8`](../../sound_dispatcher.c#L175) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3AF8-3B00 | Live (scripted-coverage-verschil was een harnas-artefact) |
| $3B02 | [`l3b02`](../../sound_dispatcher.c#L206) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3B02-3B19 | Live (scripted-coverage-verschil was een harnas-artefact) |
| $3B1B | [`l3b1b`](../../sound_dispatcher.c#L224) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3B1B-3B27 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3B28 | [`l3b28`](../../sound_dispatcher.c#L218) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3B28-3B31 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3B33 | [`l3b33`](../../sound_dispatcher.c#L235) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3B33-3B41 | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |
| $3B43 | [`l3b43`](../../sound_dispatcher.c#L247) | [sound_dispatcher.c](../../sound_dispatcher.c) | 3B43-3B5B | Geverifieerd: byte-exacte scripted lockstep + PC-dekking (2026-07-12) |

## C-only Infrastructure / Native Helpers

Deze functies bestaan uitsluitend in de C-poort (bijvoorbeeld voor window creatie, SDL, geluid, of testing) en hebben geen origineel Z80 ROM-adres.

| Function | File |
|---|---|
| [`drawNx2`](../../attract_mode.c#L449) | [attract_mode.c](../../attract_mode.c) |
| [`draw_intro_bird_animation_frame`](../../attract_mode.c#L605) | [attract_mode.c](../../attract_mode.c) |
| [`draw_n_by_2`](../../attract_mode.c#L405) | [attract_mode.c](../../attract_mode.c) |
| [`bird_flight_path`](../../bird_logic.c#L69) | [bird_logic.c](../../bird_logic.c) |
| [`coverage_hit`](../../coverage.c#L67) | [coverage.c](../../coverage.c) |
| [`coverage_is_enabled`](../../coverage.c#L58) | [coverage.c](../../coverage.c) |
| [`coverage_observe_frame`](../../coverage.c#L92) | [coverage.c](../../coverage.c) |
| [`coverage_set_output_path`](../../coverage.c#L49) | [coverage.c](../../coverage.c) |
| [`coverage_write_dump`](../../coverage.c#L192) | [coverage.c](../../coverage.c) |
| [`set_bits_video_register`](../../game_state_machine.c#L107) | [game_state_machine.c](../../game_state_machine.c) |
| [`read_dsw0`](../../hw_video_audio.c#L481) | [hw_video_audio.c](../../hw_video_audio.c) |
| [`read_in0`](../../hw_video_audio.c#L480) | [hw_video_audio.c](../../hw_video_audio.c) |
| [`render_sprites`](../../hw_video_audio.c#L166) | [hw_video_audio.c](../../hw_video_audio.c) |
| [`update_audio_registers`](../../hw_video_audio.c#L180) | [hw_video_audio.c](../../hw_video_audio.c) |
| [`init_global_level_data`](../../init_global_level_data.c#L7) | [init_global_level_data.c](../../init_global_level_data.c) |
| [`build_interpolation`](../../mame_lofi_resampler.c#L15) | [mame_lofi_resampler.c](../../mame_lofi_resampler.c) |
| [`mame_lofi_resampler_init`](../../mame_lofi_resampler.c#L40) | [mame_lofi_resampler.c](../../mame_lofi_resampler.c) |
| [`mothership_barrier_collision`](../../mothership_logic.c#L32) | [mothership_logic.c](../../mothership_logic.c) |
| [`mothership_descent_logic`](../../mothership_logic.c#L12) | [mothership_logic.c](../../mothership_logic.c) |
| [`apply_input_script`](../../platform_sdl.c#L355) | [platform_sdl.c](../../platform_sdl.c) |
| [`bank_swap_to`](../../platform_sdl.c#L67) | [platform_sdl.c](../../platform_sdl.c) |
| [`game_thread_func`](../../platform_sdl.c#L179) | [platform_sdl.c](../../platform_sdl.c) |
| [`get_phoenix_color`](../../platform_sdl.c#L215) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_is_vblank`](../../platform_sdl.c#L54) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_read_dsw`](../../platform_sdl.c#L50) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_read_inputs`](../../platform_sdl.c#L46) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_toggle_palette_bank`](../../platform_sdl.c#L80) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_write_scroll_register`](../../platform_sdl.c#L144) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_write_sound_a`](../../platform_sdl.c#L148) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_write_sound_b`](../../platform_sdl.c#L152) | [platform_sdl.c](../../platform_sdl.c) |
| [`hw_write_video_register`](../../platform_sdl.c#L75) | [platform_sdl.c](../../platform_sdl.c) |
| [`initial_alien_layout_level`](../../platform_sdl.c#L455) | [platform_sdl.c](../../platform_sdl.c) |
| [`input_script_button_mask`](../../platform_sdl.c#L300) | [platform_sdl.c](../../platform_sdl.c) |
| [`load_input_script`](../../platform_sdl.c#L311) | [platform_sdl.c](../../platform_sdl.c) |
| [`main`](../../platform_sdl.c#L476) | [platform_sdl.c](../../platform_sdl.c) |
| [`platform_audio_frame_hook`](../../platform_sdl.c#L165) | [platform_sdl.c](../../platform_sdl.c) |
| [`platform_ram_dump_hook`](../../platform_sdl.c#L431) | [platform_sdl.c](../../platform_sdl.c) |
| [`record_input_event`](../../platform_sdl.c#L411) | [platform_sdl.c](../../platform_sdl.c) |
| [`start_input_recording`](../../platform_sdl.c#L395) | [platform_sdl.c](../../platform_sdl.c) |
| [`stop_input_recording`](../../platform_sdl.c#L420) | [platform_sdl.c](../../platform_sdl.c) |
| [`write_screenshot`](../../platform_sdl.c#L249) | [platform_sdl.c](../../platform_sdl.c) |
| [`add_score`](../../scoring.c#L66) | [scoring.c](../../scoring.c) |
| [`bcd_add`](../../scoring.c#L16) | [scoring.c](../../scoring.c) |
| [`check_coin_event`](../../scoring.c#L202) | [scoring.c](../../scoring.c) |
| [`update_hi_score`](../../scoring.c#L39) | [scoring.c](../../scoring.c) |
| [`update_scores_and_sound`](../../scoring.c#L93) | [scoring.c](../../scoring.c) |
| [`apply_event`](../../sound.c#L136) | [sound.c](../../sound.c) |
| [`clamp_pcm16`](../../sound.c#L149) | [sound.c](../../sound.c) |
| [`queue_event`](../../sound.c#L89) | [sound.c](../../sound.c) |
| [`sound_init`](../../sound.c#L58) | [sound.c](../../sound.c) |
| [`sound_render_frame`](../../sound.c#L161) | [sound.c](../../sound.c) |
| [`sound_set_frame_sample_index`](../../sound.c#L77) | [sound.c](../../sound.c) |
| [`sound_write_control_a`](../../sound.c#L115) | [sound.c](../../sound.c) |
| [`sound_write_control_b`](../../sound.c#L125) | [sound.c](../../sound.c) |
| [`astable_init`](../../sound_discrete.c#L72) | [sound_discrete.c](../../sound_discrete.c) |
| [`build_poly18`](../../sound_discrete.c#L55) | [sound_discrete.c](../../sound_discrete.c) |
| [`effect1_data`](../../sound_discrete.c#L44) | [sound_discrete.c](../../sound_discrete.c) |
| [`effect1_filter_selected`](../../sound_discrete.c#L46) | [sound_discrete.c](../../sound_discrete.c) |
| [`effect1_frequency`](../../sound_discrete.c#L45) | [sound_discrete.c](../../sound_discrete.c) |
| [`effect2_data`](../../sound_discrete.c#L40) | [sound_discrete.c](../../sound_discrete.c) |
| [`effect2_frequency`](../../sound_discrete.c#L41) | [sound_discrete.c](../../sound_discrete.c) |
| [`noise_c24_discharge`](../../sound_discrete.c#L42) | [sound_discrete.c](../../sound_discrete.c) |
| [`noise_c25_charge`](../../sound_discrete.c#L43) | [sound_discrete.c](../../sound_discrete.c) |
| [`rcdisc4_init`](../../sound_discrete.c#L171) | [sound_discrete.c](../../sound_discrete.c) |
| [`sound_discrete_init`](../../sound_discrete.c#L412) | [sound_discrete.c](../../sound_discrete.c) |
| [`sound_discrete_noise`](../../sound_discrete.c#L382) | [sound_discrete.c](../../sound_discrete.c) |
| [`update_c24`](../../sound_discrete.c#L332) | [sound_discrete.c](../../sound_discrete.c) |
| [`update_c25`](../../sound_discrete.c#L357) | [sound_discrete.c](../../sound_discrete.c) |
| [`rrca`](../../sound_dispatcher.c#L10) | [sound_dispatcher.c](../../sound_dispatcher.c) |
| [`execute_bit3_function`](../../sprite_rendering.c#L77) | [sprite_rendering.c](../../sprite_rendering.c) |
| [`execute_bit4_function`](../../sprite_rendering.c#L13) | [sprite_rendering.c](../../sprite_rendering.c) |
| [`level_1_3_B_player_alive_aliens`](../../state_play.c#L16) | [state_play.c](../../state_play.c) |
| [`level_5_7_birds_fade_in`](../../state_play.c#L149) | [state_play.c](../../state_play.c) |
| [`tms36xx_decay`](../../tms36xx.c#L141) | [tms36xx.c](../../tms36xx.c) |
| [`tms36xx_init`](../../tms36xx.c#L200) | [tms36xx.c](../../tms36xx.c) |
| [`tms36xx_mm6221aa_tune_w`](../../tms36xx.c#L247) | [tms36xx.c](../../tms36xx.c) |
| [`tms36xx_restart`](../../tms36xx.c#L160) | [tms36xx.c](../../tms36xx.c) |
| [`tms36xx_tone`](../../tms36xx.c#L181) | [tms36xx.c](../../tms36xx.c) |
| [`phoenix_init`](../../utilities.c#L375) | [utilities.c](../../utilities.c) |
| [`check_player_ship_collision`](../../weapon_collision.c#L173) | [weapon_collision.c](../../weapon_collision.c) |
| [`copy_current_to_old_enemy_bullet_data`](../../weapon_collision.c#L100) | [weapon_collision.c](../../weapon_collision.c) |
