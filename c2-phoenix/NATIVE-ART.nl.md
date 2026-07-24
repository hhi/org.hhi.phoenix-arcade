# Native C2 Originele Sprites In Hi-Res

Engelse versie: [NATIVE-ART.md](NATIVE-ART.md).

Native C2 bewaart de originele Phoenix-spritevormen, animatieframes en
kleurtoewijzing zonder terug te vallen op afwijkende vectorfiguren. Hij
gebruikt voor ieder oorspronkelijk foreground- en backgroundkarakter een
afzonderlijke 16x16 C2-glyph, in plaats van de originele 8x8-bitmap tijdens
runtime rechtstreeks te renderen. Elke glyph heeft vlakke, volledig opaak uit
de PROM afgeleide kleurvlakken. Daardoor blijven de vogels, aliens, het schip
en projectielen herkenbaar Phoenix, maar
zijn ze scherper en beter leesbaar op een modern scherm.

## Buildatlas, Geen Runtime-ROM

`make c2` voert [generate_hires_sprite_assets.py](tools/generate_hires_sprite_assets.py)
uit wanneer de brondata verandert. Het script leest de samengestelde
`graphics.rom`- en `proms.rom`-images en
en genereert `native/c2_hires_sprite_assets.h` met:

- afzonderlijke 16x16 C2-hi-resglyphs voor ieder oorspronkelijk foreground- en backgroundkarakter;
- de RGB-waarden die uit de originele kleur-PROMs worden berekend.

De uiteindelijke C2-binary leest geen `gfx_mem`, `palette_prom_a` of
`palette_prom_b`. De gegenereerde atlas is een C2-buildartefact met de
afgeleide spritegegevens. `make native-check` bewaakt die runtimegrens.

## Weergave En Animatie

| Familie | Bron in C2 | Hi-res weergave |
| --- | --- | --- |
| Spelerschip, aliens, kogels, teksten en explosies | Actuele `ForegroundScreen`-tileindices plus de C2-foregroundglyphatlas | Een afzonderlijke 16x16 glyph per karakter. Een veldbrede pixel-artcompositor voegt aangrenzende karakters samen voor het schalen, zodat ronde en diagonale contouren niet op karaktergrenzen breken. |
| Vogels | Actuele `BackgroundScreen`-compositie en de C2-backgroundglyphatlas | De gedeelde spelkern heeft `DrawBirdObject` al uitgevoerd; C2 voegt de resulterende tiles voor het tekenen samen. Zo blijven de originele animatie, overlap en wisovergangen per frame behouden, met zachtere vogelcontouren. |
| Kleur | De bestaande Phoenix kleur-PROMformule tijdens atlasgeneratie | Dezelfde palette-bank en tilekleurrol als de oorspronkelijke renderer. |

De gedeelde gamecore blijft de enige bron voor beweging, timing, botsing,
score, levels en zichtbare speelvelddata. Deze renderer voegt geen visuele
objecten toe en verandert geen speltoestand.

De compositor verzint geen sterren, vectorfiguren of nieuwe objecten. Hij
gebruikt uitsluitend de zichtbare foreground/background-tilemasks en hun uit de
PROM afgeleide kleuren. De uiteindelijke dekking van één hi-respixel verzacht
alleen buitenste diagonale hoeken; de sprite-interieurs blijven opaak.

## Verificatie

`make native-check` verifieert dat de C2-binary geen graphics- of
kleur-PROMsymbolen bevat. `make native-compare` vergelijkt een headless
C2-replay met een JPhoenix-referentiedump. Zo blijft de sprite-upwaardering
gescheiden van het lockstepbewijs voor de spelstaat.
