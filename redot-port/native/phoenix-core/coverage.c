#include "coverage.h"
#include <stdio.h>
#include <string.h>

#define MAX_COVERAGE_ENTRIES 512

typedef struct {
    const char* name;
    unsigned long hits;
    int first_frame;
    int last_frame;
} CoverageEntry;

static const char* g_coverage_output_path = NULL;
static CoverageEntry g_entries[MAX_COVERAGE_ENTRIES];
static int g_entry_count = 0;

static unsigned long g_total_frames = 0;
static int g_first_frame = 0;
static int g_last_frame = 0;
static unsigned long g_game_state_hits[8];
static unsigned long g_level_hits[16];
static int g_first_game_state_frame[8];
static int g_first_level_frame[16];
static uint8_t g_max_level_and_round = 0;
static uint8_t g_max_gameplay_level_and_round = 0;
static unsigned long g_level_transitions = 0;
static unsigned long g_player_deaths = 0;
static unsigned long g_game_overs = 0;
static unsigned long g_enemy_bullet_active_frames = 0;
static unsigned long g_player_bullet_active_frames = 0;
static unsigned long g_bird_wave_frames = 0;
static unsigned long g_mothership_frames = 0;
static unsigned long g_bird_wave_gameplay_frames = 0;
static unsigned long g_mothership_gameplay_frames = 0;
static unsigned long g_attract_frames = 0;
static unsigned long g_gameplay_frames = 0;
static unsigned long g_player1_frames = 0;
static unsigned long g_player2_frames = 0;
static unsigned long g_intro_splash_frames = 0;
static bool g_have_previous = false;
static uint8_t g_prev_game_state = 0;
static uint8_t g_prev_level_and_round = 0;

/*
 * Enables coverage collection by selecting the JSON output path. A NULL path
 * leaves all coverage calls as cheap no-ops for normal gameplay runs.
 */
void coverage_set_output_path(const char* path) {
    g_coverage_output_path = path;
}

/*
 * Reports whether the current run should accumulate and write coverage data.
 * This keeps instrumentation calls in gameplay code side-effect-free unless a
 * caller explicitly requested --coverage-dump.
 */
bool coverage_is_enabled(void) {
    return g_coverage_output_path != NULL;
}

/*
 * Records a named instrumentation point. Names are stable strings owned by
 * call sites; the table stores pointers and counts first/last observed frames
 * for input-bot target scoring.
 */
void coverage_hit(const char* name) {
    if (!coverage_is_enabled() || name == NULL) return;

    for (int i = 0; i < g_entry_count; i++) {
        if (strcmp(g_entries[i].name, name) == 0) {
            g_entries[i].hits++;
            g_entries[i].last_frame = g_last_frame;
            return;
        }
    }

    if (g_entry_count >= MAX_COVERAGE_ENTRIES) return;
    CoverageEntry* e = &g_entries[g_entry_count++];
    e->name = name;
    e->hits = 1;
    e->first_frame = g_last_frame;
    e->last_frame = g_last_frame;
}

/*
 * Samples RAM-derived progress metrics once per dumped frame. The counters are
 * intentionally high-level: game states, level/round progress, player bank,
 * bullets, bird waves, mothership activity, and state transitions used by the
 * replay mutator.
 */
void coverage_observe_frame(int frame, const PhoenixState* s) {
    if (!coverage_is_enabled() || s == NULL) return;

    if (g_total_frames == 0) {
        g_first_frame = frame;
    }
    g_total_frames++;
    g_last_frame = frame;

    uint8_t game_state = s->GameState;
    if (game_state < 8) {
        if (g_game_state_hits[game_state] == 0) {
            g_first_game_state_frame[game_state] = frame;
        }
        g_game_state_hits[game_state]++;
    }

    uint8_t level = s->LevelAndRound & 0x0F;
    if (g_level_hits[level] == 0) {
        g_first_level_frame[level] = frame;
    }
    g_level_hits[level]++;

    if (s->LevelAndRound > g_max_level_and_round) {
        g_max_level_and_round = s->LevelAndRound;
    }

    if (s->GameOrAttract == 0) {
        g_attract_frames++;
    } else {
        g_gameplay_frames++;
        if (s->LevelAndRound > g_max_gameplay_level_and_round) {
            g_max_gameplay_level_and_round = s->LevelAndRound;
        }
    }
    if (s->GameAndDemoOrSplash == 0) {
        g_player1_frames++;
    } else if (s->GameAndDemoOrSplash == 1) {
        g_player2_frames++;
    } else if (s->GameAndDemoOrSplash == 2) {
        g_intro_splash_frames++;
    }

    if (g_have_previous) {
        if (s->LevelAndRound != g_prev_level_and_round) {
            g_level_transitions++;
        }
        if (g_prev_game_state != 4 && game_state == 4) {
            g_player_deaths++;
        }
        if (g_prev_game_state != 5 && game_state == 5) {
            g_game_overs++;
        }
    }
    g_have_previous = true;
    g_prev_game_state = game_state;
    g_prev_level_and_round = s->LevelAndRound;

    if ((s->EnemyBullet0State | s->EnemyBullet1State | s->EnemyBullet2State |
         s->EnemyBullet3State | s->EnemyBullet4State) & 0x08) {
        g_enemy_bullet_active_frames++;
    }
    if ((s->PlayerBulletState | s->AbovePlayerBulletState) & 0x08) {
        g_player_bullet_active_frames++;
    }
    if (level == 0x05 || level == 0x07) {
        g_bird_wave_frames++;
        if (s->GameOrAttract != 0) {
            g_bird_wave_gameplay_frames++;
        }
    }
    if (level >= 0x09 && level <= 0x0B) {
        g_mothership_frames++;
        if (s->GameOrAttract != 0) {
            g_mothership_gameplay_frames++;
        }
    }
}

/*
 * Writes a compact JSON object for fixed numeric domains such as game states
 * and levels. Entries with zero hits remain present so downstream tools can
 * compare runs without schema probing.
 */
static void write_map(FILE* f, const char* name, const unsigned long* hits,
                      const int* first_frames, int count) {
    fprintf(f, "  \"%s\": {\n", name);
    for (int i = 0; i < count; i++) {
        if (i > 0) fprintf(f, ",\n");
        fprintf(f, "    \"%X\": {\"hits\": %lu, \"first_frame\": %d}",
                i, hits[i], hits[i] == 0 ? 0 : first_frames[i]);
    }
    fprintf(f, "\n  }");
}

/*
 * Emits the final coverage JSON document consumed by tools/input_bot.py. This
 * is called at shutdown, after the last frame observation, and includes both
 * aggregate progress metrics and explicit named instrumentation hits.
 */
void coverage_write_dump(void) {
    if (!coverage_is_enabled()) return;

    FILE* f = fopen(g_coverage_output_path, "w");
    if (!f) {
        printf("Coverage dump failed to open %s\n", g_coverage_output_path);
        return;
    }

    fprintf(f, "{\n");
    fprintf(f, "  \"frames\": {\"total\": %lu, \"first\": %d, \"last\": %d},\n",
            g_total_frames, g_first_frame, g_last_frame);
    fprintf(f, "  \"summary\": {\n");
    fprintf(f, "    \"max_level_and_round\": %u,\n", g_max_level_and_round);
    fprintf(f, "    \"max_gameplay_level_and_round\": %u,\n", g_max_gameplay_level_and_round);
    fprintf(f, "    \"level_transitions\": %lu,\n", g_level_transitions);
    fprintf(f, "    \"player_deaths\": %lu,\n", g_player_deaths);
    fprintf(f, "    \"game_overs\": %lu,\n", g_game_overs);
    fprintf(f, "    \"attract_frames\": %lu,\n", g_attract_frames);
    fprintf(f, "    \"gameplay_frames\": %lu,\n", g_gameplay_frames);
    fprintf(f, "    \"player1_frames\": %lu,\n", g_player1_frames);
    fprintf(f, "    \"player2_frames\": %lu,\n", g_player2_frames);
    fprintf(f, "    \"intro_splash_frames\": %lu,\n", g_intro_splash_frames);
    fprintf(f, "    \"enemy_bullet_active_frames\": %lu,\n", g_enemy_bullet_active_frames);
    fprintf(f, "    \"player_bullet_active_frames\": %lu,\n", g_player_bullet_active_frames);
    fprintf(f, "    \"bird_wave_frames\": %lu,\n", g_bird_wave_frames);
    fprintf(f, "    \"bird_wave_gameplay_frames\": %lu,\n", g_bird_wave_gameplay_frames);
    fprintf(f, "    \"mothership_frames\": %lu,\n", g_mothership_frames);
    fprintf(f, "    \"mothership_gameplay_frames\": %lu\n", g_mothership_gameplay_frames);
    fprintf(f, "  },\n");
    write_map(f, "game_states", g_game_state_hits, g_first_game_state_frame, 8);
    fprintf(f, ",\n");
    write_map(f, "levels", g_level_hits, g_first_level_frame, 16);
    fprintf(f, ",\n");
    fprintf(f, "  \"hits\": {\n");
    for (int i = 0; i < g_entry_count; i++) {
        CoverageEntry* e = &g_entries[i];
        fprintf(f, "    \"%s\": {\"hits\": %lu, \"first_frame\": %d, \"last_frame\": %d}%s\n",
                e->name, e->hits, e->first_frame, e->last_frame,
                i == g_entry_count - 1 ? "" : ",");
    }
    fprintf(f, "  }\n");
    fprintf(f, "}\n");
    fclose(f);
    printf("Coverage dump complete (%d hit entries, %lu frames): %s\n",
           g_entry_count, g_total_frames, g_coverage_output_path);
}
