#!/usr/bin/env python3
"""Generate the per-target and per-option reference for the input bot.

The how-to groups the targets into six rows, so most of them share one
sentence with four or eight others - which leaves exactly the questions you
have when choosing one unanswered. This builds a page that discusses every
target and every command-line option individually, from two sources that
cannot drift out of date:

  * the ``TARGETS`` table in ``input_bot.py`` - each entry is a lambda that
    states precisely which coverage counter must pass which threshold.
  * ``build_parser()``                        - every option, with its default
    and its help text, read straight off the argparse definitions.

The one thing a machine cannot supply is *why you would pick a target*, so
that sentence is written by hand below. Adding a target to input_bot.py
without adding its purpose here makes this script fail rather than quietly
emit a page with a hole in it.

Usage:  python3 c-phoenix/tools/generate_input_bot_reference.py [--outdir DIR]
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent
BOT = HERE / "input_bot.py"

FUNC_RE = re.compile(r"^[A-Za-z_][\w \t\*]*\b(\w+)\s*\([^;]*\)\s*\{", re.M)
# the argument is not always a plain literal: attract_mode.c picks between two
# names with a ternary, so take every string literal in the call, not the first
PROBE_RE = re.compile(r"coverage_hit\(([^;]*?)\)\s*;", re.S)
LIT_RE = re.compile(r'"([^"]+)"')
# hit(c, "x") / summary(c, "x") / game_state_seen(c, "x") inside a TARGETS lambda
READS_RE = re.compile(r'\b(hit|summary|game_state_seen)\(c,\s*"([^"]+)"\)')

# Order of presentation. Everything in TARGETS must appear in exactly one group.
GROUPS = [
    ("start", ("Starting a game and two-player mode",
               "Een spel starten en tweespelermodus")),
    ("player", ("The player: shooting, shield, dying",
                "De speler: schieten, schild, sterven")),
    ("progress", ("Getting further into the game",
                  "Verder komen in het spel")),
    ("enemies", ("Aliens and birds",
                 "Aliens en vogels")),
    ("mothership", ("The mothership, phase by phase",
                    "Het moederschip, fase voor fase")),
    ("score", ("Score", "Score")),
]

# name -> (group, english purpose, dutch purpose)
PURPOSE = {
    "coin_accepted": ("start",
        "A coin was accepted. The shortest possible check that input reaches the machine at all.",
        "Er is een munt geaccepteerd. De kortst mogelijke controle dat invoer de machine überhaupt bereikt."),
    "two_player_game_started": ("start",
        "A two-player game was started. Only says the game began, not that both players actually played.",
        "Er is een tweespelerspel gestart. Zegt alleen dat het spel begon, niet dat beide spelers ook echt speelden."),
    "player_2_bank_initialized": ("start",
        "Player two's separate RAM bank was set up. Proves the port keeps two independent game states, not one.",
        "De aparte RAM-bank van speler twee is opgezet. Bewijst dat de port twee onafhankelijke speltoestanden bijhoudt, geen één."),
    "two_player_turn_switch": ("start",
        "Play actually handed over from one player to the other. This is the real two-player test; the two above are its preconditions.",
        "Het spel is werkelijk overgedragen van de ene speler aan de andere. Dit is de echte tweespelertest; de twee hierboven zijn de voorwaarden ervoor."),

    "player_bullet_fired": ("player",
        "The player fired at least one shot. A smoke test: if this misses, the replay never got out of the attract screen.",
        "De speler heeft minstens één schot gelost. Een rooktest: mist dit, dan kwam de replay nooit voorbij het attract-scherm."),
    "shield_used": ("player",
        "The shield button was pressed. Needed for anything that studies the 4x4 shield sprite or its collision handling.",
        "De schildknop is ingedrukt. Nodig voor alles wat de 4x4-schildsprite of de botsingsafhandeling ervan bestudeert."),
    "enemy_bullets_active": ("player",
        "Enemy fire was in the air. Distinct from the player dying: it only means the enemy shot back.",
        "Er was vijandelijk vuur onderweg. Anders dan sterven: het betekent alleen dat de vijand terugschoot."),
    "player_death": ("player",
        "The player lost a life. One life - the game may well continue afterwards.",
        "De speler verloor een leven. Eén leven — het spel kan daarna gewoon doorgaan."),
    "game_over": ("player",
        "All lives were lost and the game ended. Use this, not player_death, when you need the ending sequence itself.",
        "Alle levens waren op en het spel eindigde. Gebruik dit, niet player_death, als je de eindsequentie zelf nodig hebt."),

    "level_transition": ("progress",
        "The game moved from one round to the next at least once. The cheapest proof that progression works at all.",
        "Het spel ging minstens één keer van de ene ronde naar de volgende. Het goedkoopste bewijs dat voortgang überhaupt werkt."),
    "gameplay_level_5": ("progress",
        "Reached round 5 in real play. The first level where the search usually needs more than one generation.",
        "Ronde 5 gehaald in echt spel. Het eerste level waarvoor de zoektocht meestal meer dan één generatie nodig heeft."),
    "gameplay_level_7": ("progress",
        "Reached round 7 in real play.",
        "Ronde 7 gehaald in echt spel."),
    "gameplay_level_8": ("progress",
        "Reached round 8 in real play.",
        "Ronde 8 gehaald in echt spel."),
    "gameplay_level_9": ("progress",
        "Reached round 9 in real play. The deepest built-in target; expect to need --generations and a long --frames.",
        "Ronde 9 gehaald in echt spel. Het diepste ingebouwde target; reken op --generations en een lange --frames."),

    "alien_kill": ("enemies",
        "An alien was destroyed and scored. Scoring is part of the condition, so a hit that awards nothing does not count.",
        "Een alien is vernietigd en scoorde punten. Scoren hoort bij de voorwaarde, dus een treffer die niets oplevert telt niet mee."),
    "bird_hit": ("enemies",
        "Any bird or egg was hit, at any growth stage. Deliberately broad - use it to reach the bird phase, not to pin down which bird.",
        "Er is een vogel of ei geraakt, in welk groeistadium dan ook. Bewust breed — gebruik het om de vogelfase te bereiken, niet om vast te leggen welke vogel."),
    "grown_bird_bonus_explosion": ("enemies",
        "A fully grown bird was destroyed and paid its bonus. The narrow counterpart of bird_hit.",
        "Een volgroeide vogel is vernietigd en keerde zijn bonus uit. De smalle tegenhanger van bird_hit."),
    "bird_wave_entry": ("enemies",
        "A bird wave appeared on screen - including during the attract demo, where nobody is playing.",
        "Er verscheen een vogelgolf op het scherm — ook tijdens de attract-demo, waar niemand speelt."),
    "bird_wave_gameplay": ("enemies",
        "A bird wave appeared while a game was actually being played. Use this one for fixtures; bird_wave_entry can be satisfied by the demo.",
        "Er verscheen een vogelgolf terwijl er werkelijk gespeeld werd. Gebruik deze voor fixtures; bird_wave_entry kan al door de demo worden afgevinkt."),

    "mothership_active": ("mothership",
        "The mothership was on screen - attract mode counts. Rarely what you want on its own.",
        "Het moederschip stond op het scherm — attract-modus telt mee. Zelden wat je op zichzelf wilt."),
    "mothership_active_gameplay": ("mothership",
        "The mothership was on screen during real play. This is the one to build a mothership fixture on.",
        "Het moederschip stond op het scherm tijdens echt spel. Hierop bouw je een moederschip-fixture."),
    "mothership_tile_hit": ("mothership",
        "Any hull tile of the mothership was shot away. Broad: it does not say which part of the hull.",
        "Er is een romptegel van het moederschip weggeschoten. Breed: het zegt niet welk deel van de romp."),
    "mothership_tile_4c_hit": ("mothership",
        "Character 0x4C was hit specifically - the smooth outer hull. See the hull sheet in animations/*/animation-sequences.md.",
        "Specifiek karakter 0x4C is geraakt — de gladde buitenromp. Zie de rompsheet in animations/*/animation-sequences.md."),
    "mothership_tile_60_hit": ("mothership",
        "Character 0x60 was hit specifically - the engine row along the widest part of the hull. Harder to reach than 0x4C, and scored much higher.",
        "Specifiek karakter 0x60 is geraakt — de motorrij langs het breedste deel van de romp. Moeilijker te bereiken dan 0x4C, en veel hoger gescoord."),
    "mothership_core_window": ("mothership",
        "The hull opened far enough to expose the core. A precondition for the kill, not the kill itself.",
        "De romp ging ver genoeg open om de kern bloot te leggen. Een voorwaarde voor de kill, niet de kill zelf."),
    "mothership_core_gate_70": ("mothership",
        "The core gate at $70 was seen open - the narrow moment in which the mothership can actually be destroyed.",
        "De kernpoort op $70 stond open — het smalle moment waarop het moederschip werkelijk vernietigd kan worden."),
    "mothership_explosion": ("mothership",
        "The mothership was destroyed, or game state 6 was entered. The end of the phased chain above.",
        "Het moederschip is vernietigd, of speltoestand 6 is bereikt. Het einde van de fasereeks hierboven."),

    "bonus_life_awarded": ("score",
        "Score actually crossed the bonus-life threshold. Combine with the two-player targets for the planned 2P bonus-life fixture.",
        "De score is werkelijk over de bonuslevendrempel gegaan. Combineer met de tweespelertargets voor de geplande 2P-bonuslevenfixture."),
}

T = {
    "en": dict(
        title="Input Bot Reference: Every Target and Every Option",
        intro=("What each target means, what it takes to reach it, and what every command-line "
               "option does. Generated by `tools/generate_input_bot_reference.py` from the "
               "`TARGETS` table and the argparse definitions in `input_bot.py` — do not edit by "
               "hand. For the workflow itself see [input-bot-howto.md](input-bot-howto.md)."),
        tcount="Targets", ocount="Options",
        th_t="Target", th_m="What it means", th_c="Condition in the code",
        th_w="Measured in",
        chain_h="How a target is decided",
        chain=("Nothing here inspects the picture on screen. A target is decided from two "
               "different kinds of evidence the port emits while it plays:\n\n"
               "1. **Probes.** A `coverage_hit(\"name\")` call sits inside the translated "
               "routine, at the exact branch where the event happens. It proves the port "
               "*executed that path* — not that a button was pressed. `two_player_turn_switch`, "
               "for instance, only fires on the branch that hands play back from player two, "
               "and only when `GameOrAttract == 0x02`, so the attract demo cannot satisfy it.\n"
               "2. **Frame sampling.** `coverage_observe_frame()` runs once per frame and reads "
               "the game state, producing counters such as `mothership_gameplay_frames`. Some "
               "values are derived rather than probed: `player_deaths` is *game state changed "
               "to 4*, `level_transitions` is *LevelAndRound changed*.\n\n"
               "A probe proves the code went there; a frame counter proves the state existed. "
               "Both are written to the file named by `--coverage-dump=`, and the conditions "
               "below read that file.\n\n"
               "This measures the **C port**. That the original ROM takes the same branch is "
               "not shown here — that is what the lockstep comparison is for. It also means a "
               "new target cannot be invented from the outside: it needs a probe in the C "
               "source or a counter in the sampler first."),
        opts="Command-line options", th_o="Option", th_d="Default", th_h="What it does",
        no_default="required", flag="flag",
        back="Back to [tools/README.md](README.md)."),
    "nl": dict(
        title="Input-bot-referentie: elk target en elke optie",
        intro=("Wat elk target betekent, wat er nodig is om het te halen, en wat elke "
               "opdrachtregeloptie doet. Gegenereerd door `tools/generate_input_bot_reference.py` "
               "uit de `TARGETS`-tabel en de argparse-definities in `input_bot.py` — niet met de "
               "hand aanpassen. Voor de werkwijze zelf, zie "
               "[input-bot-howto.nl.md](input-bot-howto.nl.md)."),
        tcount="Targets", ocount="Opties",
        th_t="Target", th_m="Wat het betekent", th_c="Voorwaarde in de code",
        th_w="Gemeten in",
        chain_h="Hoe een target wordt vastgesteld",
        chain=("Niets hier kijkt naar het beeld op het scherm. Een target wordt vastgesteld uit "
               "twee soorten bewijs die de port tijdens het spelen afgeeft:\n\n"
               "1. **Sondes.** Een aanroep `coverage_hit(\"naam\")` staat in de vertaalde "
               "routine, precies op de tak waar de gebeurtenis plaatsvindt. Het bewijst dat de "
               "port *die weg heeft afgelegd* — niet dat er een knop is ingedrukt. "
               "`two_player_turn_switch` vuurt bijvoorbeeld alleen op de tak die het spel "
               "teruggeeft vanaf speler twee, en alleen als `GameOrAttract == 0x02`, zodat de "
               "attract-demo hem niet kan afvinken.\n"
               "2. **Frame-sampling.** `coverage_observe_frame()` draait één keer per frame en "
               "leest de spelstatus uit; daar komen tellers als `mothership_gameplay_frames` "
               "vandaan. Sommige waarden zijn afgeleid in plaats van gemeten: `player_deaths` "
               "is *spelstatus werd 4*, `level_transitions` is *LevelAndRound veranderde*.\n\n"
               "Een sonde bewijst dat de code er langskwam; een frame-teller bewijst dat de "
               "toestand er was. Beide worden weggeschreven naar het bestand achter "
               "`--coverage-dump=`, en de voorwaarden hieronder lezen dat bestand.\n\n"
               "Dit meet de **C-port**. Dat de originele ROM dezelfde tak neemt, blijkt hier "
               "niet uit — daarvoor is de lockstep-vergelijking. Het betekent ook dat een nieuw "
               "target niet van buitenaf te bedenken is: er moet eerst een sonde in de C-bron "
               "of een teller in de sampler bij."),
        opts="Opdrachtregelopties", th_o="Optie", th_d="Standaard", th_h="Wat het doet",
        no_default="verplicht", flag="vlag",
        back="Terug naar [tools/README.nl.md](README.nl.md)."),
}


def load_bot():
    spec = importlib.util.spec_from_file_location("input_bot", BOT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def target_conditions() -> dict[str, str]:
    """The source text of every TARGETS lambda, keyed by target name.

    Read with ast rather than a regex: several entries wrap across lines, and
    a regex that copes with that also happily matches the wrong thing.
    """
    src = BOT.read_text()
    tree = ast.parse(src)
    for node in tree.body:
        if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "TARGETS":
            out = {}
            for key, value in zip(node.value.keys, node.value.values):
                body = value.body if isinstance(value, ast.Lambda) else value
                text = ast.get_source_segment(src, body) or ""
                out[key.value] = " ".join(text.split())
            return out
    raise SystemExit("TARGETS not found in input_bot.py")


def probe_sites() -> dict[str, str]:
    """Where each coverage_hit("name") probe sits, as `file.c: function()`.

    A target string is only ever true because some line of the port called
    coverage_hit with it. Resolving that here means the page says where the
    measurement is taken, not merely what it is called.
    """
    out: dict[str, str] = {}
    for path in sorted(PROJECT.glob("*.c")):
        if path.name == "coverage.c":
            continue                      # the counter, not a measuring point
        src = path.read_text(errors="ignore")
        starts = [(m.start(), m[1]) for m in FUNC_RE.finditer(src)]
        for m in PROBE_RE.finditer(src):
            names = LIT_RE.findall(m[1])
            if not names:
                continue
            fn = None
            for pos, label in starts:
                if pos < m.start():
                    fn = label
                else:
                    break
            where = f"`{path.name}` → `{fn}()`" if fn else f"`{path.name}`"
            for name in names:
                out.setdefault(name, where)
    return out


def measured_in(condition: str, probes: dict[str, str], lang: str) -> str:
    """Resolve a target's condition to the place its data is produced."""
    sampler = ("per-frame sampler in `coverage.c`" if lang == "en"
               else "frame-sampler in `coverage.c`")
    unknown = "—"
    seen: list[str] = []
    for kind, key in READS_RE.findall(condition):
        if kind == "hit":
            where = probes.get(key, unknown)
        else:
            where = sampler
        if where not in seen:
            seen.append(where)
    return ", ".join(seen) if seen else unknown


def options(mod):
    """Every subcommand's options, straight off the argparse definitions."""
    parser = mod.build_parser()
    subs = [a for a in parser._actions if isinstance(a, argparse._SubParsersAction)]
    out = []
    for name, sub in subs[0].choices.items():
        rows = []
        for act in sub._actions:
            if not act.option_strings or act.dest == "help":
                continue
            rows.append((", ".join(act.option_strings), act.default,
                         (act.help or "").strip(), act.nargs == 0))
        out.append((name, rows))
    return out


def render(conds, opts, probes, lang) -> str:
    t = T[lang]
    total = sum(len(rows) for _, rows in opts)
    out = [f"# {t['title']}", "", t["intro"], "",
           f"**{t['tcount']}: {len(conds)}** · **{t['ocount']}: {total}**", "", "---", "",
           f"## {t['chain_h']}", "", t["chain"], "", "---", ""]

    for gid, titles in GROUPS:
        names = sorted(n for n, v in PURPOSE.items() if v[0] == gid)
        if not names:
            continue
        out += [f"## {titles[0 if lang == 'en' else 1]}", "",
                f"| {t['th_t']} | {t['th_m']} | {t['th_c']} | {t['th_w']} |",
                "| --- | --- | --- | --- |"]
        for n in names:
            why = PURPOSE[n][1 if lang == "en" else 2]
            cond = conds[n].replace("|", "\\|")
            out.append(f"| `{n}` | {why} | `{cond}` | {measured_in(conds[n], probes, lang)} |")
        out += [""]

    out += ["---", "", f"## {t['opts']}", ""]
    for name, rows in opts:
        out += [f"### `input_bot.py {name}`", "",
                f"| {t['th_o']} | {t['th_d']} | {t['th_h']} |", "| --- | --- | --- |"]
        for flags, default, help_, is_flag in rows:
            if is_flag:
                d = t["flag"]
            elif default is None:
                d = t["no_default"]
            else:
                d = f"`{default}`"
            out.append(f"| `{flags}` | {d} | {help_.replace('|', chr(92) + '|')} |")
        out += [""]

    out += ["---", "", t["back"], ""]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", type=Path, default=HERE)
    args = ap.parse_args()

    mod = load_bot()
    conds = target_conditions()

    # the whole point of generating this: a new target cannot slip in unexplained
    missing = sorted(set(conds) - set(PURPOSE))
    stale = sorted(set(PURPOSE) - set(conds))
    if missing:
        raise SystemExit("no purpose written for: " + ", ".join(missing)
                         + "\nAdd it to PURPOSE in " + __file__)
    if stale:
        raise SystemExit("PURPOSE describes targets that no longer exist: " + ", ".join(stale))
    for gid, _ in GROUPS:
        pass
    known = {g for g, _ in GROUPS}
    bad = sorted(n for n, v in PURPOSE.items() if v[0] not in known)
    if bad:
        raise SystemExit("unknown group for: " + ", ".join(bad))

    opts = options(mod)
    probes = probe_sites()
    for lang in ("en", "nl"):
        name = f"input-bot-reference{'' if lang == 'en' else '.nl'}.md"
        (args.outdir / name).write_text(render(conds, opts, probes, lang), encoding="utf-8")
        print("wrote", args.outdir / name)
    print(f"{len(conds)} targets, {sum(len(r) for _, r in opts)} options")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
