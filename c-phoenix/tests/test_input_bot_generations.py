"""Search-control tests for `tools/input_bot.py mutate --generations`.

These exercise the search loop, not the emulator: `run_emulator` is replaced by
a stub that scores a candidate by how many events it contains. That isolates
exactly what `--generations` changed - which seed each candidate is mutated
from, and when that seed is allowed to move - and lets the tests run anywhere,
including on a machine with no SDL2 and no built binary.

The emulator contract itself is unchanged and is covered by actually running
the bot; see tools/input-bot-howto.md.
"""

import importlib.util
import json
import random
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("input_bot", ROOT / "tools" / "input_bot.py")
ib = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ib)


class StubbedBot(unittest.TestCase):
    """Shared fixture: the bot with its emulator replaced by a stub."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="input-bot-test-")
        self.tmp = Path(self._tmp.name)
        self.seed = self.tmp / "seed.txt"
        self.seed.write_text("\n".join(f"{f} p1_left press" for f in range(0, 400, 40)) + "\n")

        # every candidate the search built, recorded as the seed it came from
        self.seeds_used: list[list] = []
        self._real_candidate = ib.generated_candidate

        def spy(seed_events, *a, **k):
            self.seeds_used.append(list(seed_events))
            return self._real_candidate(seed_events, *a, **k)

        def stub_emulator(args, coverage_path):
            text = Path(args.script).read_text()
            events = sum(1 for l in text.splitlines() if l and not l.startswith("#"))
            coverage_path.write_text(json.dumps(
                {"summary": {"gameplay_frames": events * 4}, "hits": {}, "game_states": {}}))
            return subprocess.CompletedProcess([], 0, "", "")

        ib.generated_candidate = spy
        ib.run_emulator = stub_emulator

    def tearDown(self):
        ib.generated_candidate = self._real_candidate
        self._tmp.cleanup()

    def search(self, generations, random_seed=7, iterations=4):
        self.seeds_used.clear()
        args = ib.build_parser().parse_args([
            "mutate", "--seed", str(self.seed), "--frames", "400",
            "--iterations", str(iterations), "--generations", str(generations),
            "--random-seed", str(random_seed), "--keep", "2",
            "--output-dir", str(self.tmp / f"out-{generations}-{random_seed}"),
        ])
        self.assertEqual(args.func(args), 0)
        return [len(s) for s in self.seeds_used]


class GenerationSearchTests(StubbedBot):
    def test_single_generation_is_a_flat_search(self):
        """The default must keep behaving as it always did: one seed, N samples."""
        sizes = self.search(generations=1)
        self.assertEqual(len(sizes), 4)
        self.assertEqual(len(set(sizes)), 1, f"seed changed mid-search: {sizes}")

    def test_seed_is_constant_within_a_generation(self):
        sizes = self.search(generations=3)
        self.assertEqual(len(sizes), 12)
        for gen, chunk in enumerate((sizes[0:4], sizes[4:8], sizes[8:12]), start=1):
            self.assertEqual(len(set(chunk)), 1, f"generation {gen} re-seeded mid-round: {chunk}")

    def test_seed_improves_and_never_regresses(self):
        """Elitism: a round that finds nothing better must keep the old seed."""
        sizes = self.search(generations=3)
        per_gen = [sizes[0], sizes[4], sizes[8]]
        self.assertGreater(per_gen[1], per_gen[0], "generation 2 should start from a better seed")
        for earlier, later in zip(per_gen, per_gen[1:]):
            self.assertGreaterEqual(later, earlier, f"seed went backwards: {per_gen}")

    def test_same_random_seed_reproduces_the_same_search(self):
        self.assertEqual(self.search(3, random_seed=11), self.search(3, random_seed=11))

    def test_different_random_seed_explores_differently(self):
        self.assertNotEqual(self.search(3, random_seed=11), self.search(3, random_seed=12))


class OutputGuardTests(StubbedBot):
    """The default --output-dir is the committed corpus, so a run must not
    silently replace a vetted fixture that happens to share rank and score."""

    def run_into(self, out: Path, force=False, random_seed=7):
        argv = ["mutate", "--seed", str(self.seed), "--frames", "400",
                "--iterations", "3", "--random-seed", str(random_seed),
                "--keep", "2", "--output-dir", str(out)]
        if force:
            argv.append("--force")
        args = ib.build_parser().parse_args(argv)
        return args.func(args)

    def test_refuses_to_replace_a_differing_file(self):
        out = self.tmp / "corpus"
        self.assertEqual(self.run_into(out), 0)
        victim = sorted(out.glob("*.txt"))[0]
        victim.write_text("# a vetted fixture someone curated\n", encoding="utf-8")

        self.assertEqual(self.run_into(out), 3, "should have refused")
        self.assertEqual(victim.read_text(encoding="utf-8"),
                         "# a vetted fixture someone curated\n",
                         "the existing file was overwritten anyway")

    def test_force_replaces_it(self):
        out = self.tmp / "corpus-force"
        self.assertEqual(self.run_into(out), 0)
        victim = sorted(out.glob("*.txt"))[0]
        victim.write_text("# stale\n", encoding="utf-8")
        self.assertEqual(self.run_into(out, force=True), 0)
        self.assertNotEqual(victim.read_text(encoding="utf-8"), "# stale\n")

    def test_default_output_dir_is_not_the_committed_corpus(self):
        """Omitting --output-dir must not write into the vetted script corpus.

        Every example that forgets the flag lands on this default, so the
        default itself has to be the safe one.
        """
        default = ib.build_parser().parse_args(
            ["mutate", "--seed", str(self.seed)]).output_dir
        self.assertNotIn("context/input-scripts", str(default))

    def test_identical_rerun_is_allowed(self):
        """Re-running the same command must not be treated as a collision."""
        out = self.tmp / "corpus-idem"
        self.assertEqual(self.run_into(out), 0)
        self.assertEqual(self.run_into(out), 0, "an identical rewrite was refused")


class MutationCarryOverTests(unittest.TestCase):
    """Whether a mode carries the seed forward at all.

    --generations only compounds if the mutator keeps what made the previous
    winner good. The earlier tests proved the search hands the winner to the
    mutator; these pin down what the mutator then does with it, which is the
    property that actually decides whether generations help.

    The seed markers are shield presses well past --mutate-after: no generator
    emits those at those frames by chance, so a survivor really is the seed's.
    """

    SEED = [(f, "shield", "press") for f in (400, 900, 1500, 2400, 3200)]
    MUTATE_AFTER = 220

    def survivors(self, mode, trial):
        cand = ib.generated_candidate(self.SEED, 4000, random.Random(trial),
                                      self.MUTATE_AFTER, mode)
        return sum(1 for f, b, a in self.SEED
                   if any(bb == b and aa == a and abs(ff - f) <= 18 for ff, bb, aa in cand))

    def test_jitter_carries_the_seed_forward(self):
        for trial in range(5):
            self.assertGreaterEqual(
                self.survivors("jitter", trial), 3,
                "jitter is the mode --generations relies on; it must keep the seed's tail")

    def test_regenerate_discards_the_seed_tail(self):
        for trial in range(5):
            self.assertEqual(
                self.survivors("regenerate", trial), 0,
                "if this ever starts keeping the tail, drop the warning in mutate()")

    def test_sweep_discards_the_seed_tail(self):
        for trial in range(5):
            self.assertEqual(self.survivors("sweep", trial), 0)


if __name__ == "__main__":
    unittest.main()


class GameplayScoringTests(unittest.TestCase):
    """A `_gameplay` target changes what the score rewards.

    A real six-generation run against `level_transition` scored ~1.26M on a
    replay where max_level was 0x0B but max_gameplay_level was 0x01: the
    attract demo had reached round 11 while the player never left round 1, and
    87% of the score came from that demo. `wants_gameplay_progress()` is what
    prevents this, so pin its effect down here rather than rediscover it in a
    log.
    """

    def coverage(self, max_level, max_gameplay, attract=4000, gameplay=2000):
        return {
            "summary": {
                "max_level_and_round": max_level,
                "max_gameplay_level_and_round": max_gameplay,
                "attract_frames": attract,
                "gameplay_frames": gameplay,
                "mothership_frames": 500,
                "mothership_gameplay_frames": 0,
            },
            "hits": {}, "game_states": {},
        }

    def test_attract_progress_dominates_without_a_gameplay_target(self):
        """The trap: a demo that got to round 11 outscores real play at round 1."""
        demo_ran_far = ib.coverage_score(self.coverage(0x0B, 0x01), ["level_transition"])
        player_got_far = ib.coverage_score(self.coverage(0x01, 0x01), ["level_transition"])
        self.assertGreater(demo_ran_far - player_got_far, 900_000,
                           "attract-mode levels should still be worth ~100k each here")

    def test_a_gameplay_target_ignores_attract_progress(self):
        """With the flip, only what the player reached counts."""
        demo_ran_far = ib.coverage_score(self.coverage(0x0B, 0x01), ["bird_wave_gameplay"])
        player_got_far = ib.coverage_score(self.coverage(0x01, 0x01), ["bird_wave_gameplay"])
        self.assertEqual(demo_ran_far, player_got_far,
                         "a gameplay target must not reward the demo running longer")

    def test_a_gameplay_target_rewards_real_progress(self):
        low = ib.coverage_score(self.coverage(0x0B, 0x01), ["bird_wave_gameplay"])
        high = ib.coverage_score(self.coverage(0x0B, 0x05), ["bird_wave_gameplay"])
        self.assertGreater(high - low, 500_000, "gameplay levels are worth 150k each")

    def test_a_gameplay_target_penalises_idling_in_attract(self):
        busy = ib.coverage_score(self.coverage(0x0B, 0x05, attract=500), ["bird_wave_gameplay"])
        idle = ib.coverage_score(self.coverage(0x0B, 0x05, attract=5000), ["bird_wave_gameplay"])
        self.assertGreater(busy - idle, 4000,
                           "the full attract penalty should apply, not a quarter of it")
