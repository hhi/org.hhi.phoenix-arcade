# C Functions per File

## [alien_logic.c](../../alien_logic.c)

| Function | ASM Range(s) |
|---|---|
| [`init_alien_control_states`](../../alien_logic.c#L19) | 05EC-05F9 |
| [`get_animation_chrs_aliens_fade_in`](../../alien_logic.c#L31) | 085A-0871 |
| [`l0fd8`](../../alien_logic.c#L43) | 0FD8-0FEF |
| [`l37cc_erase_bonus_explosion`](../../alien_logic.c#L82) | 37CC-37E5 |
| [`l3796_bonus_explosion_left`](../../alien_logic.c#L100) | 3796-37AA |
| [`l3758_bonus_explosion_right`](../../alien_logic.c#L114) | 3772-3792 |
| [`l37b0_print_bonus_score`](../../alien_logic.c#L135) | 37B0-37C6 |
| [`l3758_bonus_explosion_animation`](../../alien_logic.c#L166) | 3758-37CC |
| [`handle_animations_for_killed_aliens`](../../alien_logic.c#L195) | 0FC0-0FFF |
| [`init_alien_control_states_05fa`](../../alien_logic.c#L207) | 05FA-060D |
| [`init_alien_positions`](../../alien_logic.c#L224) | 0610-0638 |
| [`copy_init_values_for_16_aliens`](../../alien_logic.c#L249) | 0650-0679 |
| [`alien_data_controller`](../../alien_logic.c#L274) | 0A50-0A6B |
| [`get_screen_ram_address_for_all_aliens`](../../alien_logic.c#L290) | 0A6C-0A99 |
| [`alien_movement_update`](../../alien_logic.c#L335) | 0D1C-0D67 |
| [`alien_animation_update`](../../alien_logic.c#L382) | 0D70-0DB5, 0DBB-0DC6, 0DCC-0DEE |
| [`l3264`](../../alien_logic.c#L459) | 3264-32AF |
| [`l3074_breakout_delay`](../../alien_logic.c#L501) | 3074-30A8 |
| [`l3028`](../../alien_logic.c#L528) | 3028-3059, 305C-306D |
| [`l30ba`](../../alien_logic.c#L562) | 30BA-30D8, 30E4-310F, 3112-3121 |
| [`l3124`](../../alien_logic.c#L607) | 3124-314E |
| [`l315a`](../../alien_logic.c#L629) | 315A-318E, 3192-31AD |
| [`l31b4`](../../alien_logic.c#L662) | 31B4-320D, 3210-3228 |
| [`l322c`](../../alien_logic.c#L718) | 322C-325E |
| [`l2596`](../../alien_logic.c#L744) | 2596-25B6 |
| [`l2560`](../../alien_logic.c#L778) | 2560-2595 |

## [alien_wave.c](../../alien_wave.c)

| Function | ASM Range(s) |
|---|---|
| [`l24c4`](../../alien_wave.c#L29) | 24C4-24DF |
| [`l2204`](../../alien_wave.c#L79) | 2204-222B |
| [`l21ba`](../../alien_wave.c#L103) | 21BA-21CF |
| [`l2150`](../../alien_wave.c#L133) | 2150-215F |
| [`l2160`](../../alien_wave.c#L142) | 2160-216F |
| [`l2170`](../../alien_wave.c#L152) | 2170-217F |
| [`l2180`](../../alien_wave.c#L160) | 2180-218F |
| [`l2190`](../../alien_wave.c#L170) | 2190-21A4 |
| [`l21a5`](../../alien_wave.c#L181) | 21A5-21B9 |
| [`l2146`](../../alien_wave.c#L192) | 2146-214F |
| [`l2130`](../../alien_wave.c#L204) | 2130-2145 |
| [`l2000_alien_wave_main_loop`](../../alien_wave.c#L219) | 2000-202A |
| [`l3000`](../../alien_wave.c#L254) | 3000-3012 |

## [attract_mode.c](../../attract_mode.c)

| Function | ASM Range(s) |
|---|---|
| [`splash_and_demo`](../../attract_mode.c#L32) | 00E3-013A, 0140-0172 |
| [`clear_fore_and_background`](../../attract_mode.c#L113) | 0140-0172 |
| [`get_player_inputs_for_demo`](../../attract_mode.c#L169) | 0173-0195 |
| [`slow_print_score_average_table`](../../attract_mode.c#L198) | 0196-01CD |
| [`slow_print_scroll_register_update`](../../attract_mode.c#L241) | 0078-007D |
| [`check_demo_mode_player_and_alien`](../../attract_mode.c#L252) | 03B0-03FD |
| [`coin_checking`](../../attract_mode.c#L281) | 17E0-17ED |
| [`prompt_for_start_game`](../../attract_mode.c#L293) | 0288-02EE |
| [`decrement_coins`](../../attract_mode.c#L366) | 02CB-02EF |
| [`draw_n_by_2`](../../attract_mode.c#L405) | Unknown / None |
| [`draw_score_average_table_tiles`](../../attract_mode.c#L419) | 0BCA-0BF1 |
| [`drawNx2`](../../attract_mode.c#L449) | Unknown / None |
| [`drawbirdobject`](../../attract_mode.c#L472) | 34C0-355D |
| [`draw_bird_shape_350c`](../../attract_mode.c#L519) | 350C-355D |
| [`draw_bird_shape_34de`](../../attract_mode.c#L557) | 34DE-350B |
| [`l1ee0`](../../attract_mode.c#L583) | 1EE0-1EFA |
| [`draw_intro_bird_animation_frame`](../../attract_mode.c#L606) | Unknown / None |

## [bird_logic.c](../../bird_logic.c)

| Function | ASM Range(s) |
|---|---|
| [`process_birds`](../../bird_logic.c#L27) | 3400-3436, 3438-344D |
| [`bird_flight_path`](../../bird_logic.c#L69) | Unknown / None |
| [`draw_first_4_bird_objects`](../../bird_logic.c#L81) | 3474-3485 |
| [`draw_second_4_bird_objects`](../../bird_logic.c#L93) | 3486-3497 |

## [bird_wave_behavior.c](../../bird_wave_behavior.c)

| Function | ASM Range(s) |
|---|---|
| [`update_second_bird_bank`](../../bird_wave_behavior.c#L14) | 3452-345B |
| [`l3744_restart`](../../bird_wave_behavior.c#L33) | 3744-3754 |
| [`l3672_aim`](../../bird_wave_behavior.c#L47) | 3672-3692 |
| [`l3695_aim_up`](../../bird_wave_behavior.c#L65) | 3695-36BB |
| [`l3628_climb`](../../bird_wave_behavior.c#L85) | 3628-3666 |
| [`l366a_stall`](../../bird_wave_behavior.c#L117) | 366A-3671 |
| [`l35e0_descend`](../../bird_wave_behavior.c#L127) | 35E0-3624 |
| [`l36c0_animate`](../../bird_wave_behavior.c#L165) | 36C0-36C9 |
| [`l36d2_grow`](../../bird_wave_behavior.c#L178) | 36D2-36E6 |
| [`l36ea_grow`](../../bird_wave_behavior.c#L186) | 36EA-3706 |
| [`update_bird_behavior`](../../bird_wave_behavior.c#L218) | 35B0-35DB |
| [`update_first_four_birds`](../../bird_wave_behavior.c#L251) | 3498-34A9 |
| [`update_second_four_birds`](../../bird_wave_behavior.c#L261) | 34AA-34BB |
| [`refresh_bird_flight_parameters`](../../bird_wave_behavior.c#L270) | 3560-359F |
| [`l3a00`](../../bird_wave_behavior.c#L312) | 3A00-3A0F |
| [`l395c`](../../bird_wave_behavior.c#L337) | 395C-397B |
| [`try_spawn_bird_dive_bomb`](../../bird_wave_behavior.c#L364) | 3930-395B |
| [`check_bird_formation_player_collision`](../../bird_wave_behavior.c#L399) | 3980-39FD |

## [birds_vertical_movement.c](../../birds_vertical_movement.c)

| Function | ASM Range(s) |
|---|---|
| [`l2668`](../../birds_vertical_movement.c#L15) | 2668-26A7 |
| [`l26d0`](../../birds_vertical_movement.c#L36) | 26D0-26FD |
| [`l26aa`](../../birds_vertical_movement.c#L60) | 26AA-26CC, 2476-2493, 2495-249F |
| [`birds_vertical_movement_update`](../../birds_vertical_movement.c#L112) | 2600-2664 |

## [collision_detection.c](../../collision_detection.c)

| Function | ASM Range(s) |
|---|---|
| [`l38a1_erase_bird`](../../collision_detection.c#L20) | 38A1-38B5 |
| [`bird_explosion_slot`](../../collision_detection.c#L38) | 38F8-391B |
| [`l3844_small_bird_hit`](../../collision_detection.c#L56) | 3844-388D, 3894-389C |
| [`l38bc_large_hit`](../../collision_detection.c#L99) | 38BC-38F1 |
| [`collision_detection_for_birds`](../../collision_detection.c#L132) | 3800-3841, 391C-3922 |
| [`l3462_no_birds_left`](../../collision_detection.c#L174) | 3462-346D |

## [coverage.c](../../coverage.c)

| Function | ASM Range(s) |
|---|---|
| [`coverage_set_output_path`](../../coverage.c#L49) | Unknown / None |
| [`coverage_is_enabled`](../../coverage.c#L58) | Unknown / None |
| [`coverage_hit`](../../coverage.c#L67) | Unknown / None |
| [`coverage_observe_frame`](../../coverage.c#L92) | Unknown / None |
| [`coverage_write_dump`](../../coverage.c#L192) | Unknown / None |

## [game_state_machine.c](../../game_state_machine.c)

| Function | ASM Range(s) |
|---|---|
| [`game_state_machine`](../../game_state_machine.c#L31) | Unknown / None |
| [`state_0_new_game_start`](../../game_state_machine.c#L54) | 0430-045B, 04A0-04AB |
| [`l04a0_change_player_at_attract_mode`](../../game_state_machine.c#L98) | 04A0-04AB |
| [`set_bits_video_register`](../../game_state_machine.c#L107) | Unknown / None |
| [`l07f0`](../../game_state_machine.c#L118) | 07F0-07FA |
| [`state_1_flashing_score`](../../game_state_machine.c#L132) | 04AC-04E4, 04E6-04F9, 04FB-0505 |

## [hw_video_audio.c](../../hw_video_audio.c)

| Function | ASM Range(s) |
|---|---|
| [`wait_vblank_coin`](../../hw_video_audio.c#L30) | 0080-00B5 |
| [`clear_ram_bank`](../../hw_video_audio.c#L76) | 006B-0077 |
| [`init_sound_screen`](../../hw_video_audio.c#L94) | 0050-006A |
| [`phoenix_main_loop`](../../hw_video_audio.c#L123) | 0000-004F |
| [`clear_background`](../../hw_video_audio.c#L155) | 03A0-03AF |
| [`render_sprites`](../../hw_video_audio.c#L166) | Unknown / None |
| [`update_audio_registers`](../../hw_video_audio.c#L180) | Unknown / None |
| [`clear_and_print_scores`](../../hw_video_audio.c#L196) | 032E-034E |
| [`update_lives_screen`](../../hw_video_audio.c#L216) | 0367-0376 |
| [`update_sound_control_ram`](../../hw_video_audio.c#L228) | 0377-037D |
| [`clear_foreground`](../../hw_video_audio.c#L237) | 0380-039D |
| [`set_bits_video_register`](../../hw_video_audio.c#L252) | 041E-042E |
| [`stars_scroll_down`](../../hw_video_audio.c#L266) | 0460-049D, 067A-06AF |
| [`draw_background_2x2`](../../hw_video_audio.c#L320) | 07DC-07EF |
| [`add_planets_to_background`](../../hw_video_audio.c#L356) | 06B0-06E7 |
| [`add_galaxies_to_background`](../../hw_video_audio.c#L433) | 2040-208A |
| [`update_scroll_register_and_fill_background`](../../hw_video_audio.c#L473) | 06F0-06F8 |
| [`read_in0`](../../hw_video_audio.c#L480) | Unknown / None |
| [`read_dsw0`](../../hw_video_audio.c#L481) | Unknown / None |

## [init_global_level_data.c](../../init_global_level_data.c)

| Function | ASM Range(s) |
|---|---|
| [`init_global_level_data`](../../init_global_level_data.c#L7) | Unknown / None |

## [mame_lofi_resampler.c](../../mame_lofi_resampler.c)

| Function | ASM Range(s) |
|---|---|
| [`build_interpolation`](../../mame_lofi_resampler.c#L15) | Unknown / None |
| [`mame_lofi_resampler_init`](../../mame_lofi_resampler.c#L40) | Unknown / None |

## [misc_logic.c](../../misc_logic.c)

| Function | ASM Range(s) |
|---|---|
| [`l06f0`](../../misc_logic.c#L11) | 06F0-0701 |
| [`l01e1`](../../misc_logic.c#L23) | 01E1-01EB |
| [`l24a0`](../../misc_logic.c#L36) | 24A0-24BB |
| [`l24f2`](../../misc_logic.c#L53) | 24F2-251C |
| [`l32b0`](../../misc_logic.c#L71) | 32B0-32EB |

## [mothership_impl.c](../../mothership_impl.c)

| Function | ASM Range(s) |
|---|---|
| [`l2351_mothership_animation`](../../mothership_impl.c#L12) | 2351-23C7 |
| [`update_counters_for_mothership_explosion`](../../mothership_impl.c#L134) | 242C-2442 |

## [mothership_logic.c](../../mothership_logic.c)

| Function | ASM Range(s) |
|---|---|
| [`mothership_descent_logic`](../../mothership_logic.c#L12) | Unknown / None |
| [`erase_mothership`](../../mothership_logic.c#L22) | 246A-2475 |
| [`mothership_barrier_collision`](../../mothership_logic.c#L32) | Unknown / None |
| [`mothership_core_hit_check`](../../mothership_logic.c#L48) | 2520-254F |

## [platform_sdl.c](../../platform_sdl.c)

| Function | ASM Range(s) |
|---|---|
| [`hw_read_inputs`](../../platform_sdl.c#L41) | Unknown / None |
| [`hw_read_dsw`](../../platform_sdl.c#L45) | Unknown / None |
| [`hw_is_vblank`](../../platform_sdl.c#L49) | Unknown / None |
| [`bank_swap_to`](../../platform_sdl.c#L62) | Unknown / None |
| [`hw_write_video_register`](../../platform_sdl.c#L70) | Unknown / None |
| [`hw_toggle_palette_bank`](../../platform_sdl.c#L75) | Unknown / None |
| [`copy_memory_bank`](../../platform_sdl.c#L90) | 0460-049D |
| [`hw_write_scroll_register`](../../platform_sdl.c#L139) | Unknown / None |
| [`hw_write_sound_a`](../../platform_sdl.c#L143) | Unknown / None |
| [`hw_write_sound_b`](../../platform_sdl.c#L147) | Unknown / None |
| [`platform_audio_frame_hook`](../../platform_sdl.c#L160) | Unknown / None |
| [`game_thread_func`](../../platform_sdl.c#L174) | Unknown / None |
| [`compute_channel`](../../platform_sdl.c#L195) | Unknown / None |
| [`clamp_byte`](../../platform_sdl.c#L210) | Unknown / None |
| [`init_phoenix_palette`](../../platform_sdl.c#L221) | Unknown / None |
| [`get_phoenix_color`](../../platform_sdl.c#L249) | Unknown / None |
| [`write_screenshot`](../../platform_sdl.c#L284) | Unknown / None |
| [`input_script_button_mask`](../../platform_sdl.c#L335) | Unknown / None |
| [`load_input_script`](../../platform_sdl.c#L346) | Unknown / None |
| [`apply_input_script`](../../platform_sdl.c#L390) | Unknown / None |
| [`start_input_recording`](../../platform_sdl.c#L430) | Unknown / None |
| [`record_input_event`](../../platform_sdl.c#L446) | Unknown / None |
| [`stop_input_recording`](../../platform_sdl.c#L455) | Unknown / None |
| [`platform_ram_dump_hook`](../../platform_sdl.c#L466) | Unknown / None |
| [`main`](../../platform_sdl.c#L490) | Unknown / None |

## [player_explosion.c](../../player_explosion.c)

| Function | ASM Range(s) |
|---|---|
| [`l211c`](../../player_explosion.c#L15) | 211C-212C |
| [`l20e8`](../../player_explosion.c#L30) | 20E8-210D |
| [`l20b0_player_ship_particles_explosion`](../../player_explosion.c#L74) | 20B0-20E2 |
| [`l2070`](../../player_explosion.c#L115) | 2070-2084 |

## [player_logic.c](../../player_logic.c)

| Function | ASM Range(s) |
|---|---|
| [`player_update`](../../player_logic.c#L35) | 0876-0885 |
| [`copy_current_to_old_player_data`](../../player_logic.c#L49) | 0886-0897 |
| [`update_player_ship_x`](../../player_logic.c#L66) | 0900-0921, 0926-092E |
| [`update_player_position_bullet_shield`](../../player_logic.c#L94) | 08A0-08B7 |
| [`move_player`](../../player_logic.c#L114) | 08C4-08F3 |
| [`map_player_ship_position`](../../player_logic.c#L153) | 097A-0995 |
| [`get_assigned_player_bullet_tile`](../../player_logic.c#L168) | 0930-093C |
| [`get_player_ship_animation_frame_values`](../../player_logic.c#L189) | 0926-092E |
| [`spawn_player_bullet`](../../player_logic.c#L203) | 093D-0961 |
| [`update_player_bullet_y`](../../player_logic.c#L236) | 0964-0975 |
| [`player_data_controller`](../../player_logic.c#L250) | 0700-0717 |
| [`shields_expired`](../../player_logic.c#L276) | 0B48-0B5A |
| [`draw_shields`](../../player_logic.c#L294) | 0AA0-0AC1 |

## [rom_compat_stubs.c](../../rom_compat_stubs.c)

| Function | ASM Range(s) |
|---|---|
| [`l00b6`](../../rom_compat_stubs.c#L8) | 00B6-00B7 |
| [`l14e0`](../../rom_compat_stubs.c#L15) | 14E0-14FD |
| [`l1df0`](../../rom_compat_stubs.c#L22) | 1DF0-1DFF |

## [scoring.c](../../scoring.c)

| Function | ASM Range(s) |
|---|---|
| [`bcd_add`](../../scoring.c#L16) | Unknown / None |
| [`update_hi_score`](../../scoring.c#L39) | Unknown / None |
| [`add_score`](../../scoring.c#L66) | Unknown / None |
| [`update_scores_and_sound`](../../scoring.c#L93) | Unknown / None |
| [`check_coin_event`](../../scoring.c#L202) | Unknown / None |

## [sound.c](../../sound.c)

| Function | ASM Range(s) |
|---|---|
| [`sound_init`](../../sound.c#L58) | Unknown / None |
| [`sound_set_frame_sample_index`](../../sound.c#L77) | Unknown / None |
| [`queue_event`](../../sound.c#L89) | Unknown / None |
| [`sound_write_control_a`](../../sound.c#L115) | Unknown / None |
| [`sound_write_control_b`](../../sound.c#L125) | Unknown / None |
| [`apply_event`](../../sound.c#L136) | Unknown / None |
| [`clamp_pcm16`](../../sound.c#L149) | Unknown / None |
| [`sound_render_frame`](../../sound.c#L161) | Unknown / None |

## [sound_discrete.c](../../sound_discrete.c)

| Function | ASM Range(s) |
|---|---|
| [`effect2_data`](../../sound_discrete.c#L40) | Unknown / None |
| [`effect2_frequency`](../../sound_discrete.c#L41) | Unknown / None |
| [`noise_c24_discharge`](../../sound_discrete.c#L42) | Unknown / None |
| [`noise_c25_charge`](../../sound_discrete.c#L43) | Unknown / None |
| [`effect1_data`](../../sound_discrete.c#L44) | Unknown / None |
| [`effect1_frequency`](../../sound_discrete.c#L45) | Unknown / None |
| [`effect1_filter_selected`](../../sound_discrete.c#L46) | Unknown / None |
| [`build_poly18`](../../sound_discrete.c#L55) | Unknown / None |
| [`astable_init`](../../sound_discrete.c#L72) | Unknown / None |
| [`rcdisc4_init`](../../sound_discrete.c#L171) | Unknown / None |
| [`update_c24`](../../sound_discrete.c#L332) | Unknown / None |
| [`update_c25`](../../sound_discrete.c#L357) | Unknown / None |
| [`sound_discrete_noise`](../../sound_discrete.c#L382) | Unknown / None |
| [`sound_discrete_init`](../../sound_discrete.c#L412) | Unknown / None |

## [sound_dispatcher.c](../../sound_dispatcher.c)

| Function | ASM Range(s) |
|---|---|
| [`rrca`](../../sound_dispatcher.c#L10) | Unknown / None |
| [`l23d6`](../../sound_dispatcher.c#L21) | 23D6-23FB |
| [`l27bd`](../../sound_dispatcher.c#L34) | 27BD-27EE |
| [`l3a2c`](../../sound_dispatcher.c#L61) | 3A2C-3A3F |
| [`l3a1d`](../../sound_dispatcher.c#L71) | 3A1D-3A2B |
| [`l3a4e`](../../sound_dispatcher.c#L88) | 3A4E-3A5F |
| [`l3a40`](../../sound_dispatcher.c#L98) | 3A40-3A4D |
| [`l3a78`](../../sound_dispatcher.c#L113) | 3A78-3A81 |
| [`l3a62`](../../sound_dispatcher.c#L119) | 3A62-3A77 |
| [`l3a82`](../../sound_dispatcher.c#L133) | 3A82-3A8F |
| [`l3a90`](../../sound_dispatcher.c#L142) | 3A90-3A95 |
| [`l3a98_scan`](../../sound_dispatcher.c#L153) | 3A98-3ACA |
| [`l3af8`](../../sound_dispatcher.c#L174) | 3AF8-3B00 |
| [`l3ad0`](../../sound_dispatcher.c#L185) | 3AD0-3AF6 |
| [`l3b02`](../../sound_dispatcher.c#L205) | 3B02-3B19 |
| [`l3b28`](../../sound_dispatcher.c#L217) | 3B28-3B31 |
| [`l3b1b`](../../sound_dispatcher.c#L223) | 3B1B-3B27 |
| [`l3b33`](../../sound_dispatcher.c#L234) | 3B33-3B41 |
| [`l3b43`](../../sound_dispatcher.c#L246) | 3B43-3B5B |
| [`l3a10`](../../sound_dispatcher.c#L264) | 3A10-3A1C |

## [sprite_rendering.c](../../sprite_rendering.c)

| Function | ASM Range(s) |
|---|---|
| [`execute_bit4_function`](../../sprite_rendering.c#L13) | Unknown / None |
| [`execute_bit3_function`](../../sprite_rendering.c#L77) | Unknown / None |
| [`bit4_controller`](../../sprite_rendering.c#L150) | 0720-073F |
| [`bit3_controller`](../../sprite_rendering.c#L179) | 0740-07EE |
| [`update_screen_objects`](../../sprite_rendering.c#L215) | 0718-071F |

## [state_endings.c](../../state_endings.c)

| Function | ASM Range(s) |
|---|---|
| [`state_4_player_ship_explosion`](../../state_endings.c#L33) | 0AEA-0B0F |
| [`state_5_game_over_text`](../../state_endings.c#L67) | 0B60-0B9D |
| [`l2552_mothership_explosion_done`](../../state_endings.c#L102) | 2552-255D |
| [`state_6_mother_ship_explosion`](../../state_endings.c#L126) | 2400-244B |
| [`state_7_mother_ship_score_display`](../../state_endings.c#L179) | 244C-2469 |
| [`l0b15`](../../state_endings.c#L208) | 0B15-0B2D |
| [`l0ba0`](../../state_endings.c#L238) | 0BA0-0BB2 |
| [`l0bba`](../../state_endings.c#L256) | 0BBA-0BC4 |

## [state_init.c](../../state_init.c)

| Function | ASM Range(s) |
|---|---|
| [`init_player_data_structure`](../../state_init.c#L25) | Unknown / None |
| [`init_alien_data_new_level`](../../state_init.c#L33) | 0532-0543 |
| [`init_alien_movement_pointers`](../../state_init.c#L46) | 0506-0514 |
| [`l0526`](../../state_init.c#L56) | 0526-0531 |
| [`state_2_init_game_and_level_data`](../../state_init.c#L70) | 0515-0531 |
| [`get_player_lives_from_dip`](../../state_init.c#L89) | 0350-0366 |
| [`update_hi_score`](../../state_init.c#L120) | 02F0-032D |

## [state_play.c](../../state_play.c)

| Function | ASM Range(s) |
|---|---|
| [`level_1_3_B_player_alive_aliens`](../../state_play.c#L16) | Unknown / None |
| [`l2260_spiral_draw`](../../state_play.c#L26) | 2260-2291 |
| [`l2292_spiral_routine`](../../state_play.c#L84) | 2292-22B3 |
| [`level_4_6_8_spiral_fill`](../../state_play.c#L119) | 2230-225F |
| [`level_5_7_birds_fade_in`](../../state_play.c#L149) | Unknown / None |
| [`level_9_mothership_fade_in`](../../state_play.c#L163) | 22B4-22C5 |
| [`level_A_mothership_and_aliens_fade_in`](../../state_play.c#L188) | 22CA-22DD |
| [`level_0_and_2_aliens_fade_in`](../../state_play.c#L205) | 0834-0859 |
| [`state_3_normal_game_play`](../../state_play.c#L237) | 0800-0833 |

## [tms36xx.c](../../tms36xx.c)

| Function | ASM Range(s) |
|---|---|
| [`tms36xx_decay`](../../tms36xx.c#L141) | Unknown / None |
| [`tms36xx_restart`](../../tms36xx.c#L160) | Unknown / None |
| [`tms36xx_tone`](../../tms36xx.c#L181) | Unknown / None |
| [`tms36xx_init`](../../tms36xx.c#L200) | Unknown / None |
| [`tms36xx_mm6221aa_tune_w`](../../tms36xx.c#L247) | Unknown / None |

## [utilities.c](../../utilities.c)

| Function | ASM Range(s) |
|---|---|
| [`check_input_bits`](../../utilities.c#L16) | 00BB-00C3 |
| [`print_number`](../../utilities.c#L30) | 00C4-00E1 |
| [`print_text_lines`](../../utilities.c#L62) | 01D0-01E0 |
| [`print_score_column`](../../utilities.c#L87) | 06E8-06ED |
| [`print_copyright_lines`](../../utilities.c#L96) | 01E1-01EB |
| [`draw_row`](../../utilities.c#L107) | 01ED-01F7 |
| [`clear_b_bytes_at_hl`](../../utilities.c#L123) | 05D8-05DF |
| [`copy_b_bytes_hl_to_de`](../../utilities.c#L137) | 05E0-05E8 |
| [`unused_bcd_subtracter`](../../utilities.c#L153) | 0236-0252 |
| [`get_screen_ram_address`](../../utilities.c#L163) | 09BA-09D1 |
| [`get_screen_ram_address_for_player_ship`](../../utilities.c#L187) | 09A0-09B5 |
| [`add_one_to_mem`](../../utilities.c#L202) | 0200-0205 |
| [`add_bc_to_mem`](../../utilities.c#L217) | 0206-020E |
| [`compare_bc_to_mem`](../../utilities.c#L234) | 0258-025F |
| [`l0260_subtract_if_enough`](../../utilities.c#L244) | 0260-0267 |
| [`l0270_subtract_from_memory`](../../utilities.c#L259) | 0270-0276 |
| [`l0277_subtract_to_memory`](../../utilities.c#L270) | 0277-027D |
| [`draw_image_c_by_b`](../../utilities.c#L283) | 0AD6-0AE9 |
| [`left_one_column`](../../utilities.c#L303) | 0210-0216 |
| [`right_one_column`](../../utilities.c#L312) | 0217-021D |
| [`add_to_score`](../../utilities.c#L321) | 0220-0232 |
| [`delete_digits`](../../utilities.c#L361) | 04FB-0505 |
| [`phoenix_init`](../../utilities.c#L375) | Unknown / None |
| [`get_random_number`](../../utilities.c#L386) | 30AA-30B8 |
| [`l25b7`](../../utilities.c#L404) | 25B7-25FD |

## [weapon_collision.c](../../weapon_collision.c)

| Function | ASM Range(s) |
|---|---|
| [`l096e_clear_bullet`](../../weapon_collision.c#L21) | 096E-0975 |
| [`l0cb4_check_bullet_hit_player`](../../weapon_collision.c#L30) | 0CB4-0CD4 |
| [`l0cc4_player_killed`](../../weapon_collision.c#L51) | 0CC4-0CD3 |
| [`l0c84_enemy_bullet_movement`](../../weapon_collision.c#L63) | 0C84-0CB3 |
| [`copy_current_to_old_enemy_bullet_data`](../../weapon_collision.c#L100) | Unknown / None |
| [`enemy_bullet_movement_and_animation`](../../weapon_collision.c#L119) | 0C56-0C67 |
| [`get_screen_ram_address_for_enemy_bullets`](../../weapon_collision.c#L132) | 0C6B-0C80 |
| [`enemy_bullet_data_controller`](../../weapon_collision.c#L148) | 0CD8-0CEF |
| [`process_enemy_bombs`](../../weapon_collision.c#L163) | 0C40-0C51 |
| [`check_player_ship_collision`](../../weapon_collision.c#L173) | Unknown / None |
| [`check_enemy_bullet_to_player_collision`](../../weapon_collision.c#L189) | 0DF0-0E01 |
| [`l0e02_unused`](../../weapon_collision.c#L199) | 0E02-0E0B |
| [`l0c00_kill_score`](../../weapon_collision.c#L214) | 0E10-0E6B, 0E70-0E9D, 0C00-0C23 |
| [`l0e10`](../../weapon_collision.c#L233) | 0E10-0E36, 0E39-0E6B, 0E58-0E6B, 0E70-0EA0 |
| [`l0ea4_with_score`](../../weapon_collision.c#L301) | 0EA4-0EE5 |
| [`l0f56_screen_ram_collision`](../../weapon_collision.c#L352) | 0F56-0F71 |
| [`l0f00_check_alien_with_player_collision`](../../weapon_collision.c#L380) | 0F00-0F33, 0F38-0F4E, 0F74-0FB9 |

