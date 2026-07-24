# Geassembleerde Phoenix ROM-images (Lokaal)

English version: [README.md](README.md).

Deze map bevat de geassembleerde `program.rom`, `graphics.rom` en
`proms.rom`, gegenereerd door `make rombuild ROM_DIR=/path/to/chips`
(zie [`../README.md`](../README.md)). Het is de standaard
`ROM_OUTPUT_DIR` voor `rombuild` en de standaard `ROM_DIR` waaruit
`make -C jphoenix-emulator-port run` laadt.

Alles hierin behalve deze README staat in `.gitignore` (zie `.gitignore`
in deze map): de geassembleerde images zijn auteursrechtelijk beschermde
ROM-inhoud en mogen nooit gecommit worden. Draai `make rombuild` om ze
(opnieuw) te genereren uit je eigen chipdump in [`../local/`](../local/).
