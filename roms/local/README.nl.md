# Phoenix ROM Chip-dumps (Lokaal)

English version: [README.md](README.md).

Deze map is de beoogde plaats om je eigen fysieke Phoenix
Amstar-chipdumps (`ic45`, `ic46`, `mmi6301.ic40`, enz. — zie de tabel in
[`../README.md`](../README.md)) in te plaatsen. Standaard is de map
leeg; het is de standaard `ROM_DIR` voor `make romcheck` / `make
rombuild`, en die commando's verwachten dat de chipbestanden er al
staan (of elders via `ROM_DIR=<path>`) wanneer je ze draait.

Alles hierin behalve deze README staat in `.gitignore` (zie `.gitignore`
in deze map): de chipbytes zijn auteursrechtelijk beschermde ROM-inhoud
en mogen nooit gecommit worden. Vul deze map zelf met je eigen, legaal
verkregen dump; de repository levert hier niets voor aan.
