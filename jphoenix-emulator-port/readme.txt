JPhoenix Desktop starten
=========================

Open een terminal in deze projectmap en voer uit:

    make run

Dit compileert de game en start hem daarna.

Alternatief: start de LibGDX/LWJGL3-frontend met:

    make run-libgdx

Hiervoor is JDK 17 of nieuwer nodig. De eerste run downloadt de vastgezette
Gradle- en LibGDX-afhankelijkheden.

Zorg dat program.rom, graphics.rom en proms.rom in deze projectmap staan.
proms.rom bevat eerst IC40 en daarna IC41, elk 256 bytes.
Het optionele bestand hiscore.sav wordt hier ook gelezen en opgeslagen.
De game controleert grootte en SHA-256 van alle drie hardwarebestanden en stopt bij
een ontbrekend, beschadigd of afwijkend bestand.

RAM-dump (standaard uit)
========================

De RAM-dump is alleen bedoeld voor debugging en portvergelijking.
Activeer hem voor bijvoorbeeld 600 frames met:

    make
    java -Dphoenix.ramdump=ramdump.bin -Dphoenix.ramdump.frames=600 -cp build/classes PhoenixDesktop

Laat -Dphoenix.ramdump.frames weg voor de standaardduur van 3600 frames.
Start opnieuw met "make run" om de game zonder RAM-dump te draaien.
De dump kan niet tijdens het spelen worden in- of uitgeschakeld.

Ieder record bevat een big-endian framenummer van 4 bytes, gevolgd door
3072 bytes RAM uit 0x4000-0x4bff. Een bestaande dump wordt overschreven.

Save states
===========

Druk tijdens het spelen op F5 om de volledige emulatiestaat op te slaan in
jphoenix.state. Druk op F9 om die state weer te laden. Dit werkt in zowel de
standaard AWT-frontend als de LibGDX-frontend.

Het bestand is geversioneerd, aan de vereiste ROM-hashes gekoppeld en met CRC32
beveiligd. Een onvolledig, beschadigd of incompatibel bestand wordt geweigerd.
