# Phoenix C-Port - The "Stub Hunter" Graph

This visualization is je ultieme "To-Do" lijstje voor het porten!

In plaats van de hele codebase te laten zien, heb ik een extreem strak filter toegepast: 
- De rode box aan de rechterkant ("STUBS TO REFACTOR") bevat de nog gemarkeerde ROM-compatibiliteitsstubs.
- De groene blokken aan de linkerkant tonen **uitsluitend** de actieve C-functies die op dit moment één van die stubs aanroepen.
- De rode pijlen visualiseren exact waar je actieve logica nog afhankelijk is van onvertaalde code.

### Wat valt direct op?
1. **Dode Stubs (Geen inkomende pijlen)**: Je ziet direct dat stubs zoals `l00b6`, `l0e9e` en `l2748` los zweven in de rode box. Dit bevestigt jouw eerdere vermoeden in sessie 3: **deze stubs hebben helemaal geen actieve callers meer in je C-code!** Ze zijn hoogstwaarschijnlijk overbodig en kunnen veilig opgeruimd of nader onderzocht worden.
2. **De Hotspots**: Je ziet dat `platform_sdl.c` (Core Architecture) en `attract_mode.c` (Game State) nog harde rode pijlen hebben naar specifieke stubs (zoals `l3452` of `l0ba0`). Dit zijn je volgende targets om uit te spitten!

![Stub Hunter Graph](./stub_hunter_callgraph.svg)
