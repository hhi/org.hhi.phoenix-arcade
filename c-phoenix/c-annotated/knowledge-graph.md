# Phoenix Knowledge Graph

`knowledge-graph.json` is de machineleesbare kern van deze documentatieset. Hij bevat zeven soorten nodes:

- `c-function` — een functie die werkelijk in de C-port staat;
- `asm-routine` — een ASM-range die direct boven de C-functie is geannoteerd;
- `ram-slot` — een RAM-adres dat in de bestaande documentatie wordt genoemd;
- `rom-pattern` — een gevisualiseerd Cluster A- of Cluster B-patroon met ROM-adres en aantal stappen.
- `game-state` — een benoemde game state of level pattern uit `game_constants.h`;
- `claim` — een afzonderlijke technische bewering met bron, status en gerelateerde nodes;
- `table-asset` — een ROM-tabel of asset uit `phoenix_tables.h`.

De graph legt alleen automatisch afleidbare relaties vast:

- `implements`: C-functie → geannoteerde ASM-routine;
- `calls`: C-functie → C-functie, uitsluitend wanneer de naam uniek binnen de port is.
- `uses-table`: C-functie → ROM-tabel/asset;
- `handles-state`: C-functie → benoemde game state of level pattern;
- `asserts`: claim → de nodes waarop de claim betrekking heeft.

Markdown en SVG's blijven de leesbare weergaven. Hun paden staan als bewijs bij nodes; zij worden niet zonder expliciete bron als feit in de graph opgenomen.

De bron voor semantische claims is [`knowledge-claims.json`](knowledge-claims.json). Dit kleine, handgeredigeerde register is bewust gescheiden van de generator: een claim is pas onderdeel van de graph wanneer hij een expliciete bron, status en relaties heeft.

## Bijwerken en controleren

```sh
python3 tools/generate_knowledge_graph.py
python3 tools/validate_knowledge_graph.py
python3 tools/validate_documentation.py
```

De prioriteit van bronnen is: **Z80 ASM/ROM → C-port → geannoteerde documentatie → visualisaties**. `confirmed` betekent direct aanwezig in de C-port of een C-ASM-annotatie; `derived` betekent afgeleid uit tabellen of SVG-metadata; `documented` betekent dat de bestaande documentatie het adres noemt, zonder dat de generator daar een semantische betekenis aan toekent.
