# C-Phoenix-status

Engelse versie: [STATUS.md](STATUS.md).

## Huidige stand

C-Phoenix is functioneel compleet. De poort is vergeleken met de
Java-referentie-emulator tijdens de attract-cyclus, actief spel, een
mothership-kill met de volgende ronde en twee-speler-bankwisselingen. Het
project bevat ook geluid en MAME-accurate kleuren.

De laatste scripted-lockstep-batch rapporteert 57 van 57 schone scenario's. De
gedeelde C-gamecore heeft geen directe of indirecte programma-ROM-reads: de 50
gecatalogiseerde dataregio's staan als benoemde, geteste tabellen in
`phoenix_tables.c`.

## Open observaties

Dit is een speelobservatie, geen bevestigde fout.

1. **Korte hapering in de muziek bij de start van een ronde.** Tijdens het
   opkomen van de muziek kan de besturing al reageren, terwijl schip en vogels
   nog niet zichtbaar zijn. In die fase hapert de muziek soms kort. Dit moet
   nog reproduceerbaar worden vastgelegd en vergeleken met de Java-emulator.

## Gecontroleerd bereik

- 57 scripted scenario's zijn voor de spelstaat record-voor-record schoon.
- 176 functies zijn via byte-exacte runs grondig geverifieerd; 38 hebben
  gedeeltelijke dekking door dispatch- of hardwareconfiguratietakken.
- Drie ROM-routines zijn bekende dode code: `l00b6`, `l0e02_unused` en
  `unused_bcd_subtracter`.
- Oude duplicaatstubs zijn verwijderd nadat elk ROM-bereik aan de levende
  implementatie was gekoppeld.

Zie [mapping/c_functions_by_address.md](mapping/c_functions_by_address.md)
voor de functie-mapping en
[mapping/lockstep_verified.json](mapping/lockstep_verified.json) voor de
machineleesbare verificatiegegevens.

## Verificatie herhalen

Gebruik [tools/lockstep/PROCEDURE.md](../tools/lockstep/PROCEDURE.md) voor de
herhaalbare lockstep-workflow. Scripted vergelijkingen vereisen bij jphoenix
`-Dphoenix.inputclock=poll`. Vergelijk regio `4000-4BE5`; de bytes daarboven
zijn Z80-stackresidu dat C-Phoenix bewust niet reproduceert.
