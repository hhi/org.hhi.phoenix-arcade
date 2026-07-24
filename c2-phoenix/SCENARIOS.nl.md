# C2-Phoenix scenariodekking

Engelse versie: [SCENARIOS.md](SCENARIOS.md).

Deze pagina legt vast waartegen het huidige semantische C2-contract werkelijk
is uitgevoerd. Dit is scenario-bewijs, niet de bewering dat elk Phoenix-object
of elke spelregel al is gemodelleerd.

## 1. `bird-investigation`

De interactieve opname staat in
[`c-phoenix/context/input-scripts/bird-investigation.txt`](../c-phoenix/context/input-scripts/bird-investigation.txt).
Maak de gekoppelde lockstep-dumps opnieuw vanaf de monorepo-root:

```sh
make -C c-phoenix tracerun \
  COMPARE_SCRIPT=context/input-scripts/bird-investigation.txt \
  COMPARE_FRAMES=13935 \
  COMPARE_NAME=bird-investigation \
  COMPARE_STOP_AFTER=999999
```

Controleer daarna vanuit `c2-phoenix/` de semantische C2-dekking en de
C2-naar-C2-pariteit:

```sh
make summary SCENARIO=bird-investigation \
  SUMMARY_ARGS='--require-kind alien --require-kind bird --require-kind mothership --require-kind player_explosion --require-kind shield_segments --require-event impact_observed --require-event score_changed --require-event lives_changed'
make compare SCENARIO=bird-investigation
```

Vastgelegd resultaat: 13.934 C-Phoenix-records; actieve speler- en vijandelijke
kogels, aliens, vogels, vogel-/spelerontploffingen, schildsegmenten en
mothershipstatus. Er zijn score-, levens-, level/round-, speltoestand-,
activatie/deactivatie- en waargenomen-impact-events. De semantische vergelijking
heeft 13.934 gedeelde records, 2.530 alleen-referentierecords, nul alleen-port-
records en geen verschillen in de gedeelde records. De referentiestaart staat
expliciet als uitlijningscontext in het resultaat en wordt niet stilzwijgend
weggelaten.

## 2. `last-grown-bird`

Dit is de gecureerde twee-spelertrace. De invoerfixture en scenarionotities
staan in [de C-Phoenix-tracedirectory](../c-phoenix/context/traces/two_player_last_grown_bird_compare/README.nl.md).
De opgenomen dumps staan gecomprimeerd in Git. Maak tijdelijke kopieën voor
C2-gebruik:

```sh
gzip -dc ../c-phoenix/context/traces/two_player_last_grown_bird_compare/j-last-grown-bird.bin.gz > /tmp/ref_last-grown-bird.bin
gzip -dc ../c-phoenix/context/traces/two_player_last_grown_bird_compare/c-last-grown-bird.bin.gz > /tmp/port_last-grown-bird.bin
make summary SCENARIO=last-grown-bird \
  SUMMARY_ARGS='--require-kind bird --require-event impact_observed'
make compare SCENARIO=last-grown-bird
```

Vastgelegd resultaat: 8.999 C-Phoenix-records; spelers `intro`, `player1` en
`player2`; alien-, vogel-, ontploffings-, scheeps- en projectielfamilies; en
score-, levens-, toestand-, level/round-, activatie/deactivatie- en
waargenomen-impact-events. De semantische vergelijking heeft 8.422 gedeelde
records, geen alleen-referentierecords, 577 alleen-port-records en geen
verschillen in de gedeelde records.

## Resultaten lezen

`make summary` bewijst dat een object- of eventfamilie in een geëxporteerde
opname voorkwam. `make compare` controleert dat semantische JPhoenix- en
C-Phoenix-frames voor gekoppelde records gelijk zijn. Geen van beide commando's
bewijst op zichzelf ROM-getrouw spelgedrag; lockstep-RAMvergelijking blijft de
onafhankelijke equivalentiecontrole.

De huidige renderer tekent alleen objecten met gedocumenteerde zichtankers. De
mothership heeft semantische fase/status, maar geen onafhankelijk vastgestelde
gridcoördinaat. Daarom staat hij in het zijpaneel en niet op een verzonnen plek
op het canvas.
