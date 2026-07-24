# Gecureerde Referentietraces

Deze map is bedoeld voor kleine, gecureerde traces die een concrete
portingbevinding documenteren en nuttig zijn om bij de source tree te bewaren.

Engelse documentatie: [README.md](README.md).

Wel bewaren:

- korte instruction-level of object-level traces met een geschreven conclusie;
- traces die een vertaalde routine, RAM-veld of historische bugfix uitleggen;
- genoeg command/source-context om de observatie te reproduceren.

Niet bewaren:

- bulk RAM-dumps, framedumps, screenshots of gegenereerde HTML-viewers;
- verkennende logs zonder samengevatte bevinding;
- machine-lokale paden of ROM-assets.

Gebruik `/tmp` of de genegeerde root-map `traces/` voor wegwerp-output.

## Gecureerde Cases

- `two_player_last_grown_bird_compare/` - jphoenix-vs-C-Phoenix
  RAM/objectvergelijking voor de 2-player replay waarin player 1 een laatste
  volgroeide vogel tegenover zich heeft.

Gebruik [semantic-case-template.nl.md](semantic-case-template.nl.md) voor een
nieuwe case die de betekenis van een RAM-veld, bit of routine onderbouwt.
De volledige werkwijze en een uitgewerkt vogelvoorbeeld staan in
[semantic-lockstep-howto.nl.md](semantic-lockstep-howto.nl.md).

Voor het genereren, openen en interpreteren van de interactieve objectweergave
staat een afzonderlijke werkinstructie in
[visual-tracer-howto.nl.md](visual-tracer-howto.nl.md).

Voor de volledige, gebruiksvriendelijke opname- tot tracerpijplijn staat de
target-voor-target werkinstructie in
[replay-tracer-pipeline-howto.nl.md](replay-tracer-pipeline-howto.nl.md).
