# Semantisch-framecontract v1

English version: [SEMANTIC-FRAME.md](SEMANTIC-FRAME.md).

De export is een JSON-document met schema
`org.hhi.phoenix.c2.semantic-frame/v1`. Een frame bevat een framenummer,
spelcontext en een lijst semantische objecten.

```json
{
  "frame": 945,
  "sequence": 0,
  "timeline": {"tick": 123},
  "game": {"player": "player1", "level": 1, "round": 0,
           "state": "normal_gameplay",
           "scores": {"player1": 1200, "player2": 0},
           "lives": {"player1": 3, "player2": 3}},
  "objects": [
    {"key": "alien:0", "kind": "alien", "slot": 0,
     "active": true, "position": {"x": 71, "y": 32},
     "appearance": {"family": "alien", "variant": "standard",
                    "motion": "active"}}
  ]
}
```

Het coördinaatsysteem is een logisch speelveld van 208 bij 256, met de
oorsprong linksboven. `position` ontbreekt wanneer een object geen bekende
zichtbare ankerpositie heeft. Posities zijn al presentatiecoördinaten;
gebruikers mogen ze niet uitleggen als RAM-bytes, schermadressen of
sprite-offsets.

`sequence` is de exportvolgorde en is de vergelijkingssleutel voor gepaarde
lockstep-dumps. `timeline.tick` is logische tijdcontext; deze mag zich
herhalen en is geen unieke uitlijnsleutel. Gebruikers mogen de waarde niet
uitleggen als adres of instructieteller.

`kind` is `player_ship`, `player_bullet`, `above_player_bullet`,
`enemy_bullet`, `alien`, `bird`, `bird_explosion`, `player_explosion`,
`mothership` of `shield_segments`. Effecten zonder vastgestelde zichtbare
ankerpositie behouden hun semantische toestand maar hebben geen `position`.
`key` is stabiel per speler, soort en slot. `appearance` is bewust beschrijvend
en kan met willekeurige eigen C2-art of thema worden getekend.

`active` meldt de waargenomen levenscyclus van een objectslot. `visible` is
een afzonderlijke presentatieslissing. Met name een projectiel waarvan het
slot tijdens een speler-doodsovergang zijn laatste positie bewaart, blijft
`active` maar is niet `visible`; C2 mag het niet als bevroren projectiel
tekenen.

Wanneer het volgende semantische frame een projectiel onzichtbaar maakt,
onderdrukt C2 ook de laatste twee zichtbare projectielframes. Daarmee oogt een
terminale coördinaat niet als een pauze bij een botsing of schermrand.

`game.scores` en `game.lives` zijn presentatiewaarden, gedecodeerd uit hun
gedocumenteerde speltoestandsopslag. `events` is een lijst waargenomen
overgangen ten opzichte van het direct voorgaande geëxporteerde frame.
Eventnamen benoemen alleen wat is gezien, zoals `score_changed`,
`lives_changed`, `level_round_changed`, `game_state_changed`,
`object_activated` en `object_deactivated`; zij leiden geen ongedocumenteerde
oorzaak af.

`impact_observed` ontstaat alleen wanneer een actief projectiel en een actieve
nabije alien of vogel in hetzelfde geëxporteerde frame worden gedeactiveerd.
De positie is de laatst bekende doelpositie. Dit is een begrensde
presentatie-afleiding voor de C2-impactflits, geen bewering over een
ROM-collisieroutine.

De brugadapter leidt dit contract af uit de bestaande gevalideerde
trace-decoder. Het contract sluit ruwe slotstatus, adressen, graphicsindices,
PROM-waarden en ROM-herkomst bewust uit.
