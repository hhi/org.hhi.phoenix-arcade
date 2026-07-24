import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROM_DATA = ROOT / "rom_data.c"
TABLES = ROOT / "phoenix_tables.c"


def array_values(source: str, name: str) -> list[int]:
    match = re.search(
        rf"const uint8_t {name}\[[^]]+\] = \{{(.*?)\}};", source, re.DOTALL
    )
    if not match:
        raise AssertionError(f"Missing {name}")
    return [int(value, 0) for value in re.findall(r"0x[0-9A-Fa-f]+|\d+", match.group(1))]


class PhoenixTableTests(unittest.TestCase):
    def test_bird_vertical_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_bird_scroll_steps"), rom[0x3ED0:0x3EE0]
        )
        self.assertEqual(
            array_values(tables, "phoenix_bird_descent_caps"), rom[0x3EE0:0x3F00]
        )

    def test_bullet_pixel_mask_table_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_bullet_pixel_masks"), rom[0x3E00:0x3E08]
        )

    def test_round_and_explosion_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_round_population"), rom[0x1760:0x1768]
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_explosion_frames"), rom[0x17B0:0x17B8]
        )

    def test_bird_hitmask_page_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_bird_hitmask_page"), rom[0x3B00:0x3C00]
        )

    def test_alien_control_init_table_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_alien_control_init_values"),
            rom[0x1500:0x1520],
        )

    def test_alien_layout_pointer_table_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_alien_layout_pointers"), rom[0x1520:0x1540]
        )

    def test_bird_shape_and_formation_tables_match_the_annotated_rom_regions(
        self,
    ) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_bird_shape_pointers"), rom[0x3E00:0x3E80]
        )
        self.assertEqual(
            array_values(tables, "phoenix_bird_formation_params"), rom[0x3E80:0x3EC0]
        )
        self.assertEqual(
            array_values(tables, "phoenix_bird_draw_entries"), rom[0x3EC0:0x3ED0]
        )

    def test_bird_behaviour_scripts_match_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_bird_behaviour_scripts"), rom[0x3F00:0x3F80]
        )

    def test_alien_closed_loop_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_alien_distance_bands"), rom[0x3300:0x3308]
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_pattern_selectors"),
            rom[0x3310:0x3330],
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_closed_loop_pointers"),
            rom[0x3330:0x3400],
        )

    def test_alien_shape_offset_and_direction_tables_match_the_annotated_rom_regions(
        self,
    ) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_alien_shape_offset_page"),
            rom[0x1600:0x1700],
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_direction_vectors"),
            rom[0x1700:0x1740],
        )

    def test_explosion_particle_page_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_explosion_particle_page"),
            rom[0x2800:0x2C00],
        )

    def test_egg_dive_and_sound_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_egg_transformation_types"),
            rom[0x3DB8:0x3DC0],
        )
        self.assertEqual(
            array_values(tables, "phoenix_bird_dive_spawn_positions"),
            rom[0x3DC0:0x3DE0],
        )
        self.assertEqual(
            array_values(tables, "phoenix_bird_sound_cadence"), rom[0x3DE0:0x3E00]
        )

    def test_bird_erase_selector_and_mothership_pointers_match_the_annotated_rom_regions(
        self,
    ) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        match = re.search(
            r"const uint8_t phoenix_bird_erase_shape_selector = (0x[0-9A-Fa-f]+);",
            tables,
        )
        self.assertIsNotNone(match)
        self.assertEqual(int(match.group(1), 0), rom[0x198C])

        self.assertEqual(
            array_values(tables, "phoenix_mothership_explosion_pointers"),
            rom[0x1B40:0x1BA0],
        )

    def test_alien_movement_pattern_clusters_match_the_annotated_rom_regions(
        self,
    ) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_alien_movement_cluster_a"),
            rom[0x1000:0x1400],
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_movement_cluster_b"),
            rom[0x2C00:0x3000],
        )

    def test_alien_position_layout_tables_match_the_annotated_rom_regions(
        self,
    ) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_alien_position_layout_page"),
            rom[0x1500:0x1600],
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_position_pointer_table"),
            rom[0x063A:0x064A],
        )

    def test_formation_hit_window_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_formation_hit_window"),
            rom[0x1740:0x1760],
        )

    def test_attract_mode_fixed_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_score_table_tiles_a"), rom[0x0A40:0x0A4C]
        )
        self.assertEqual(
            array_values(tables, "phoenix_score_table_tiles_b"), rom[0x3C00:0x3C0C]
        )
        self.assertEqual(
            array_values(tables, "phoenix_intro_bird_anim_frames"),
            rom[0x233A:0x235A],
        )

    def test_score_average_text_page_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_score_average_text_page"),
            rom[0x1860:0x1B60],
        )

    def test_print_text_lines_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_attract_text_page"), rom[0x1800:0x1860]
        )
        self.assertEqual(
            array_values(tables, "phoenix_players_button_text"), rom[0x1BA0:0x1BC0]
        )

    def test_centralized_local_tables_match_the_annotated_rom_regions(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_player_init_data"), rom[0x0560:0x0580]
        )
        self.assertEqual(
            array_values(tables, "phoenix_player_x_position_mapping"),
            rom[0x0B38:0x0B48],
        )

    def test_bird_shape_data_page_matches_the_annotated_rom_region(self) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_bird_shape_data_page"), rom[0x3C00:0x3DB8]
        )

    def test_generic_rom_copy_helper_tables_match_the_annotated_rom_regions(
        self,
    ) -> None:
        rom = array_values(ROM_DATA.read_text(encoding="ascii"), "prg_mem")
        tables = TABLES.read_text(encoding="ascii")

        self.assertEqual(
            array_values(tables, "phoenix_level_data_pointer_table"),
            rom[0x0598:0x05A8],
        )
        self.assertEqual(
            array_values(tables, "phoenix_level_data_page"), rom[0x05A8:0x05D8]
        )
        self.assertEqual(
            array_values(tables, "phoenix_screen_ram_address_table"),
            rom[0x0A00:0x0A40],
        )
        self.assertEqual(
            array_values(tables, "phoenix_sprite_character_block_shapes"),
            rom[0x1400:0x1501],
        )
        self.assertEqual(
            array_values(tables, "phoenix_shield_table"), rom[0x1770:0x17B0]
        )
        self.assertEqual(
            array_values(tables, "phoenix_shield_and_drawnx2_shapes"),
            rom[0x17B8:0x1800],
        )
        self.assertEqual(
            array_values(tables, "phoenix_alien_wave_animation_shapes"),
            rom[0x1BC0:0x1C00],
        )
        self.assertEqual(
            array_values(tables, "phoenix_starfield_page"), rom[0x1C00:0x1D00]
        )
        self.assertEqual(
            array_values(tables, "phoenix_mothership_tile_page"), rom[0x1D00:0x1E00]
        )
        self.assertEqual(
            array_values(tables, "phoenix_starfield_no_planets_page"),
            rom[0x1F00:0x2000],
        )
        self.assertEqual(
            array_values(tables, "phoenix_planet_shape_page"), rom[0x1E00:0x1E20]
        )
        self.assertEqual(
            array_values(tables, "phoenix_planet_galaxy_page"), rom[0x1E20:0x1EE0]
        )
        self.assertEqual(
            array_values(tables, "phoenix_bird_data_alt_page"), rom[0x3F80:0x4000]
        )


if __name__ == "__main__":
    unittest.main()
