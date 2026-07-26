# Phoenix Z80 ASM — C Port Cross-Reference

Generated from [Phoenix.asm](Phoenix.asm). Function annotations link to the corresponding C source.

Gegenereerd uit [Phoenix.asm](Phoenix.asm). Functieannotaties verwijzen naar de bijbehorende C-broncode.

```asm
; Source / bron: Computer Archeology - Phoenix
; https://computerarcheology.com/Arcade/Phoenix/
; https://github.com/Sorbas2020/Phoenix

;*****************************************************************************
;*                                                                           *
;* PHOENIX (AMSTAR, SET 1).  Amstar Electronics Corp. 1980                   *
;*                                                                           *
;*****************************************************************************
;* This code refers to the "maincpu" section of the ROM region from ROM set. *
;*                                                                           *
;* ROM region offsets:                                                       *
;*  ic45        $0000-$07FF                                                  *
;*  ic46        $0800-$0FFF                                                  *
;*  ic47        $1000-$17FF                                                  *
;*  ic48        $1800-$1FFF                                                  *
;*  h5-ic49.5a  $2000-$27FF                                                  *
;*  h6-ic50.6a  $2800-$2FFF                                                  *
;*  h7-ic51.7a  $3000-$37FF                                                  *
;*  h8-ic52.8a  $3800-$3FFF                                                  *
;*****************************************************************************
;* 20250330                                                                  *
;* Skipped all unused code and data.                                         *
;* All code and data at original offsets.                                    *
;* Assebled with 'Micro Z80 assembler - uz80as' (v2.02).                     *
;* https://github.com/jorgicor/uz80as                                        *
;* Usage:                                                                    *
;* uz80as.exe -x Phoenix.asm                                                 *
;*****************************************************************************

; ForegroundScreen.
ForegroundScreen       .EQU $4000       ;32*26 bytes for the foreground screen

; General storage.
; Alien-formation attack controller data:
; Drives when and how aliens break out of the base formation to fly their "closed loop" swooping attack patterns.
; The whole structure (`$4350`–`$437F`) is zeroed at level init by the routine at `$32B0`,
; and it's serviced every frame by a 7 way state machine dispatched through the jump table `T3018` (indexed by `Counter93`),
; with each handler reading/updating the behavior state in `$4350`.
M4350                  .EQU $4350       ;Alien behavior state (the state-machine variable, values 0–6)
M4351                  .EQU $4351       ;MSB of next closed loop pattern (into the `T2Exx` / `T3330` pattern tables)
M4352                  .EQU $4352       ;LSB of next closed loop pattern (into the `T2Exx` / `T3330` pattern tables)
M4353                  .EQU $4353       ;Number of aliens doing the closed loop pattern (how many attackers)
M4354                  .EQU $4354       ;LSB pointer to the currently selected lead attacking alien (`$4B50`/`$4B72` grid slot)
M4355                  .EQU $4355       ;Delay counter before the next attack is armed (→ behavior state 1)
M4356                  .EQU $4356       ;Rotating 0–15 "movement start" index (from `$4395`) used to sync aliens
M4357                  .EQU $4357       ;Attack-cycle/escalation counter (0–3); scales attacker count and difficulty
M4358                  .EQU $4358       ;Inter-step timer for the angry downward-push movement pattern
M4359                  .EQU $4359       ;Staggered group countdown timer 1 for phased alien launches
M435A                  .EQU $435A       ;Staggered group countdown timer 2 for phased alien launches
M435B                  .EQU $435B       ;Staggered group countdown timer 3 for phased alien launches

; Flags and counter:
M435E                  .EQU $435E       ;Flag for: 'AliensLeft < 5' ($FF)
M435F                  .EQU $435F       ;8 bit counter for alien movement
PlayerMoved            .EQU $4360       ;Flag for: 'Player moved' ($FF)
BulletTriggered        .EQU $4361       ;Flag for: 'Bullet triggered' ($30) and counter
M4362                  .EQU $4362       ;Flag for: 'Player shield active' and animation counter
ParticleExplosion      .EQU $4363       ;Flag for: 'Particle explosion start' and animation counter
M4364                  .EQU $4364       ;Flag for: 'Enemy hit detected' ($FF) and counter

M4366                  .EQU $4366       ;Flag for: 'Mothership or bird wing hit detected' ($FF)
M4367                  .EQU $4367       ;Flag for: 'Mothership partially faded in' ($FF)
M4368                  .EQU $4368       ;Maturity of the birds. From 'egg' over 'no wings' to 'adult' ($01 to $0F)
M4369                  .EQU $4369       ;Flag for: 'Bonus explosion' ($FF)
M436A                  .EQU $436A       ;Flag for: 'Bonus live added' ($FF) and counter
M436B                  .EQU $436B       ;Flag for: 'Mother ship score display' ($FF) and counter

; Shape of the next bird attack:
; All three are recomputed by `L3560` each time a new bird group is dispatched.
M436D                  .EQU $436D       ;Horizontal start position of the bird group
M436E                  .EQU $436E       ;Bird count / formation-size for the wave
M436F                  .EQU $436F       ;Per-wave random variation seed (keeps successive waves from being identical)

;Explosion slots for animation:
M4370                  .EQU $4370       ;Explosion slot0 animation index
M4371                  .EQU $4371       ;Explosion slot0 BCD score value (last digit is ever 0)
M4372                  .EQU $4372       ;Explosion slot0 MSB screen ram
M4373                  .EQU $4373       ;Explosion slot0 LSB screen ram
M4374                  .EQU $4374       ;Explosion slot1 animation index
M4375                  .EQU $4375       ;Explosion slot1 BCD score value (last digit is ever 0)
M4376                  .EQU $4376       ;Explosion slot1 MSB screen ram
M4377                  .EQU $4377       ;Explosion slot1 LSB screen ram
M4378                  .EQU $4378       ;Bonus explosion slot0 animation index
M4379                  .EQU $4379       ;Bonus explosion slot0 BCD score value (last digit is ever 0)
M437A                  .EQU $437A       ;Bonus explosion slot0 MSB screen ram
M437B                  .EQU $437B       ;Bonus explosion slot0 LSB screen ram
M437C                  .EQU $437C       ;Bonus explosion slot1 animation index
M437D                  .EQU $437D       ;Bonus explosion slot1 BCD score value (last digit is ever 0)
M437E                  .EQU $437E       ;Bonus explosion slot1 MSB screen ram
M437F                  .EQU $437F       ;Bonus explosion slot1 LSB screen ram

;For the score:
M4380                  .EQU $4380       ;Ever set to 0 (prevents overflow)
Score1high             .EQU $4381       ;Player 1 score BCD (high)
Score1mid              .EQU $4382       ;Player 1 score BCD (mid)
Score1low              .EQU $4383       ;Player 1 score BCD (low)
M4384                  .EQU $4384       ;Ever set to 0 (prevents overflow)
Score2high             .EQU $4385       ;Player 2 score BCD (high)
Score2mid              .EQU $4386       ;Player 2 score BCD (mid)
Score2low              .EQU $4387       ;Player 2 score BCD (low)
M4388                  .EQU $4388       ;Ever set to 0 (prevents overflow)
HiScorehigh            .EQU $4389       ;Hi score BCD (high)
HiScoremid             .EQU $438A       ;Hi score BCD (mid)
HiScorelow             .EQU $438B       ;Hi score BCD (low)

;For general purposes:
SoundControlA          .EQU $438C       ;RAM copy of sound device control register A (0x6000)
SoundControlB          .EQU $438D       ;RAM copy of sound device control register B (0x6800)
M438E                  .EQU $438E       ;Bird-wave background-sound phase (advances the melody, low bit drives SoundControlB)
CoinCount              .EQU $438F       ;Number of coins inserted (max is 9)
Player1Lives           .EQU $4390       ;Player 1 number of lives
Player2Lives           .EQU $4391       ;Player 2 number of lives
M4392                  .EQU $4392       ;Ever set to 0 ?
Counter93              .EQU $4393       ;Free running counter during playtime at game level 3
M4394                  .EQU $4394       ;Start value list pointer for alien movement MSB
M4395                  .EQU $4395       ;Start value list pointer for alien movement LSB
M4396                  .EQU $4396       ;Bird-wave background-sound step timer (counts frames per tone vs `T3DE0` duration)
M4397                  .EQU $4397       ;Score "dirty" flag — `0` means score changed this frame -> redraw the digits
M4398                  .EQU $4398       ;16 bit counter (MSB) actual index for slow print at intro splash
M4399                  .EQU $4399       ;16 bit counter (LSB) actual index for slow print at intro splash
Counter9A              .EQU $439A       ;16 bit counter (MSB) for animation
M439B                  .EQU $439B       ;16 bit counter (LSB) for animation and next index for slow print at intro splash
M439C                  .EQU $439C       ;Spiral-fill animation step counter (level 4/6/8 inter-wave fade-in)
M439D                  .EQU $439D       ;Fist two digits of BCD score value for mothership explosion
M439E                  .EQU $439E       ;Mapped player ship position, left part: ($09 to $C0)
M439F                  .EQU $439F       ;Mapped player ship position, right part: ($17 to $C8)
IN0Current             .EQU $43A0       ;Current value of IN0: bit0='coin', bit1='1 player', bit2='2 players', bit4='fire', bit5='right', bit6='left', bit7='shield'
IN0Previous            .EQU $43A1       ;Previous value of IN0
GameOrAttract          .EQU $43A2       ;Attract mode=0, One player game mode=1, Two players game mode=2
GameAndDemoOrSplash    .EQU $43A3       ;Game and demo for player 1=0, Game for player 2=1, Intro splash=2
GameState              .EQU $43A4       ;Game state=0 - 7
CounterA5              .EQU $43A5       ;8 bit counter (e.g.: score flash time)
ShieldCount            .EQU $43A6       ;Counts shield time and controls shield picture. Shields end at C0.
AnimationCounter       .EQU $43A7       ;For mothership's antenna and the alien pilot animation
M43A8                  .EQU $43A8       ;Temporary storage (MSB of pointer to table $1860)
M43A9                  .EQU $43A9       ;Temporary storage (LSB of pointer to table $1860)
M43AA                  .EQU $43AA       ;Mothership-wave frame counter (times antenna/pilot animation and star scroll)
M43AB                  .EQU $43AB       ;Counter for planet trigger
M43AC                  .EQU $43AC       ;Planet vertical spacing increment (added to trigger `$43AB`)
M43AD                  .EQU $43AD       ;Planet X index -> `T1E60` (screen-RAM LSB), incremented per planet
M43AE                  .EQU $43AE       ;Planet X index -> `T1E20` (screen-RAM MSB), incremented per planet
M43AF                  .EQU $43AF       ;`CounterB9` trigger for the next galaxy
M43B0                  .EQU $43B0       ;Galaxy spacing decrement (subtracted from `$43AF`)
M43B1                  .EQU $43B1       ;Galaxy X index -> `T1E80`, incremented per galaxy
M43B2                  .EQU $43B2       ;MSB pointer into the background pattern tables `T1C00`/`T1D00`/`T1F00`
M43B3                  .EQU $43B3       ;LSB pointer into the background pattern tables `T1C00`/`T1D00`/`T1F00`
CounterB4              .EQU $43B4       ;8 bit counter (stars scrolling down, aliens fade in time)
M43B5                  .EQU $43B5       ;Reserved/unused byte always `$FF`
M43B6                  .EQU $43B6       ;End-of-wave countdown timer that advances the game to the next level/round

LevelAndRound          .EQU $43B8       ;Bit0 - 3: game level, bit4 - 7: game round
CounterB9              .EQU $43B9       ;8 bit backwards counter
AliensLeft             .EQU $43BA       ;Number of aliens left in wave (16 at new)
BirdsLeft              .EQU $43BB       ;Number of birds left in wave (8 at new)
M43BC                  .EQU $43BC       ;Reserved/unused byte
M43BD                  .EQU $43BD       ;Low byte of the bonus extra-life score threshold; rewritten (nibble-swapped `BonusLivesAt`) after a bonus is granted
BonusLivesAt           .EQU $43BE       ;Middle byte of the threshold, set from DIP switches to `$30/$40/$50/$60` = 3000/4000/5000/6000 points
M43BF                  .EQU $43BF       ;High byte of the bonus extra-life score threshold

; Player and player bullets, data structure (grid).
PlayerState            .EQU $43C0       ;Player ship control state register
PlayerShape            .EQU $43C1       ;LSB for T1400 player ship character block shapes table
PlayerShipX            .EQU $43C2       ;Player ship, coordinate X ($0C=min.left, $64=default, $C0=max.right)
PlayerShipY            .EQU $43C3       ;Player ship, coordinate Y ($D8)
PlayerBulletState      .EQU $43C4       ;Player bullet, control state register
PlayerBulletShape      .EQU $43C5       ;Player bullet, character code ($50 to $57)
PlayerBulletX          .EQU $43C6       ;Player bullet, coordinate X
PlayerBulletY          .EQU $43C7       ;Player bullet, coordinate Y ($D0=min.bottom, $18=max.top)
AbovePlayerBulletState .EQU $43C8       ;One position above player bullet, control state register
AbovePlayerBulletShape .EQU $43C9       ;One position above player bullet, character code ($50 to $57)
AbovePlayerBulletX     .EQU $43CA       ;One position above player bullet, coordinate X
AbovePlayerBulletY     .EQU $43CB       ;One position above player bullet, coordinate Y

; Alien and bird bullets, data structure (grid).
AlienBullet0State      .EQU $43CC       ;Enemy bullet 0, control state register
AlienBullet0Shape      .EQU $43CD       ;Enemy bullet 0, character code ($58 to $5F)
AlienBullet0X          .EQU $43CE       ;Enemy bullet 0, coordinate X
AlienBullet0Y          .EQU $43CF       ;Enemy bullet 0, coordinate Y
AlienBullet1State      .EQU $43D0       ;Enemy bullet 1, control state register
AlienBullet1Shape      .EQU $43D1       ;Enemy bullet 1, character code ($58 to $5F)
AlienBullet1X          .EQU $43D2       ;Enemy bullet 1, coordinate X
AlienBullet1Y          .EQU $43D3       ;Enemy bullet 1, coordinate Y
AlienBullet2State      .EQU $43D4       ;Enemy bullet 2, control state register
AlienBullet2Shape      .EQU $43D5       ;Enemy bullet 2, character code ($58 to $5F)
AlienBullet2X          .EQU $43D6       ;Enemy bullet 2, coordinate X
AlienBullet2Y          .EQU $43D7       ;Enemy bullet 2, coordinate Y
AlienBullet3State      .EQU $43D8       ;Enemy bullet 3, control state register
AlienBullet3Shape      .EQU $43D9       ;Enemy bullet 3, character code ($58 to $5F)
AlienBullet3X          .EQU $43DA       ;Enemy bullet 3, coordinate X
AlienBullet3Y          .EQU $43DB       ;Enemy bullet 3, coordinate Y
AlienBullet4State      .EQU $43DC       ;Enemy bullet 4, control state register
AlienBullet4Shape      .EQU $43DD       ;Enemy bullet 4, character code ($58 to $5F)
AlienBullet4X          .EQU $43DE       ;Enemy bullet 4, coordinate X
AlienBullet4Y          .EQU $43DF       ;Enemy bullet 4, coordinate Y

; Player and player bullets, data structure (screen ram).
OldPlayerShipMSB       .EQU $43E0       ;Old MSB screen ram: Upper left character of player ship
OldPlayerShipLSB       .EQU $43E1       ;Old LSB screen ram: Upper left character of player ship
PlayerShipMSB          .EQU $43E2       ;MSB screen ram: Upper left character of player ship
PlayerShipLSB          .EQU $43E3       ;LSB screen ram: Upper left character of player ship
PlayerBulletMSB        .EQU $43E4       ;MSB screen ram: Player bullet
PlayerBulletLSB        .EQU $43E5       ;LSB screen ram: Player bullet
AbovePlayerBulletMSB   .EQU $43E6       ;MSB screen ram: One character above player bullet
AbovePlayerBulletLSB   .EQU $43E7       ;LSB screen ram: One character above player bullet
M43E8                  .EQU $43E8       ;MSB of its previous position (erase pointer, refreshed by `L0886`)
M43E9                  .EQU $43E9       ;LSB of its previous position (erase pointer, refreshed by `L0886`)
M43EA                  .EQU $43EA       ;MSB of its current position (draw + collision pointer, recomputed each frame by `L09A0` from `$43CA:$43CB`)
M43EB                  .EQU $43EB       ;LSB of its current position (draw + collision pointer, recomputed each frame by `L09A0` from `$43CA:$43CB`)

; Alien and bird bullets, data structure (screen ram).
OldAlienBullet0MSB     .EQU $43EC       ;Old MSB screen ram: Enemy bullet 0
OldAlienBullet0LSB     .EQU $43ED       ;Old LSB screen ram: Enemy bullet 0
AlienBullet0MSB        .EQU $43EE       ;MSB screen ram: Enemy bullet 0
AlienBullet0LSB        .EQU $43EF       ;LSB screen ram: Enemy bullet 0
OldAlienBullet1MSB     .EQU $43F0       ;Old MSB screen ram: Enemy bullet 1
OldAlienBullet1LSB     .EQU $43F1       ;Old LSB screen ram: Enemy bullet 1
AlienBullet1MSB        .EQU $43F2       ;MSB screen ram: Enemy bullet 1
AlienBullet1LSB        .EQU $43F3       ;LSB screen ram: Enemy bullet 1
OldAlienBullet2MSB     .EQU $43F4       ;Old MSB screen ram: Enemy bullet 2
OldAlienBullet2LSB     .EQU $43F5       ;Old LSB screen ram: Enemy bullet 2
AlienBullet2MSB        .EQU $43F6       ;MSB screen ram: Enemy bullet 2
AlienBullet2LSB        .EQU $43F7       ;LSB screen ram: Enemy bullet 2
OldAlienBullet3MSB     .EQU $43F8       ;Old MSB screen ram: Enemy bullet 3
OldAlienBullet3LSB     .EQU $43F9       ;Old LSB screen ram: Enemy bullet 3
AlienBullet3MSB        .EQU $43FA       ;MSB screen ram: Enemy bullet 3
AlienBullet3LSB        .EQU $43FB       ;LSB screen ram: Enemy bullet 3
OldAlienBullet4MSB     .EQU $43FC       ;Old MSB screen ram: Enemy bullet 4
OldAlienBullet4LSB     .EQU $43FD       ;Old LSB screen ram: Enemy bullet 4
AlienBullet4MSB        .EQU $43FE       ;MSB screen ram: Enemy bullet 4
AlienBullet4LSB        .EQU $43FF       ;LSB screen ram: Enemy bullet 4

; Background screen.
BackgroundScreen       .EQU $4800       ;32*26 bytes for the background screen

; Pointer to alien movement pattern.
M4B50                  .EQU $4B50       ;Alien0 movement pattern table MSB
M4B51                  .EQU $4B51       ;Alien0 movement pattern table LSB
M4B52                  .EQU $4B52       ;Alien1 movement pattern table MSB
M4B53                  .EQU $4B53       ;Alien1 movement pattern table LSB
M4B54                  .EQU $4B54       ;Alien2 movement pattern table MSB
M4B55                  .EQU $4B55       ;Alien2 movement pattern table LSB
M4B56                  .EQU $4B56       ;Alien3 movement pattern table MSB
M4B57                  .EQU $4B57       ;Alien3 movement pattern table LSB
M4B58                  .EQU $4B58       ;Alien4 movement pattern table MSB
M4B59                  .EQU $4B59       ;Alien4 movement pattern table LSB
M4B5A                  .EQU $4B5A       ;Alien5 movement pattern table MSB
M4B5B                  .EQU $4B5B       ;Alien5 movement pattern table LSB
M4B5C                  .EQU $4B5C       ;Alien6 movement pattern table MSB
M4B5D                  .EQU $4B5D       ;Alien6 movement pattern table LSB
M4B5E                  .EQU $4B5E       ;Alien7 movement pattern table MSB
M4B5F                  .EQU $4B5F       ;Alien7 movement pattern table LSB
M4B60                  .EQU $4B60       ;Alien8 movement pattern table MSB
M4B61                  .EQU $4B61       ;Alien8 movement pattern table LSB
M4B62                  .EQU $4B62       ;Alien9 movement pattern table MSB
M4B63                  .EQU $4B63       ;Alien9 movement pattern table LSB
M4B64                  .EQU $4B64       ;AlienA movement pattern table MSB
M4B65                  .EQU $4B65       ;AlienA movement pattern table LSB
M4B66                  .EQU $4B66       ;AlienB movement pattern table MSB
M4B67                  .EQU $4B67       ;AlienB movement pattern table LSB
M4B68                  .EQU $4B68       ;AlienC movement pattern table MSB
M4B69                  .EQU $4B69       ;AlienC movement pattern table LSB
M4B6A                  .EQU $4B6A       ;AlienD movement pattern table MSB
M4B6B                  .EQU $4B6B       ;AlienD movement pattern table LSB
M4B6C                  .EQU $4B6C       ;AlienE movement pattern table MSB
M4B6D                  .EQU $4B6D       ;AlienE movement pattern table LSB
M4B6E                  .EQU $4B6E       ;AlienF movement pattern table MSB
M4B6F                  .EQU $4B6F       ;AlienF movement pattern table LSB

; Alien data structure (grid).
; Used for all levels with the 16 aliens.
; Level: 1, 2, 5 (with mothership), 6, 7, 10(with mothership).
; During 'fade in' phase, the alien control state B is holding the character code!
M4B70                  .EQU $4B70       ;Alien0 control state A
M4B71                  .EQU $4B71       ;Alien0 control state B (LSB for T14xx)
M4B72                  .EQU $4B72       ;Alien0 screen coordinate X
M4B73                  .EQU $4B73       ;Alien0 screen coordinate Y
M4B74                  .EQU $4B74       ;Alien1 control state A
M4B75                  .EQU $4B75       ;Alien1 control state B (LSB for T14xx)
M4B76                  .EQU $4B76       ;Alien1 screen coordinate X
M4B77                  .EQU $4B77       ;Alien1 screen coordinate Y
M4B78                  .EQU $4B78       ;Alien2 control state A
M4B79                  .EQU $4B79       ;Alien2 control state B (LSB for T14xx)
M4B7A                  .EQU $4B7A       ;Alien2 screen coordinate X
M4B7B                  .EQU $4B7B       ;Alien2 screen coordinate Y
M4B7C                  .EQU $4B7C       ;Alien3 control state A
M4B7D                  .EQU $4B7D       ;Alien3 control state B (LSB for T14xx)
M4B7E                  .EQU $4B7E       ;Alien3 screen coordinate X
M4B7F                  .EQU $4B7F       ;Alien3 screen coordinate Y
M4B80                  .EQU $4B80       ;Alien4 control state A
M4B81                  .EQU $4B81       ;Alien4 control state B (LSB for T14xx)
M4B82                  .EQU $4B82       ;Alien4 screen coordinate X
M4B83                  .EQU $4B83       ;Alien4 screen coordinate Y
M4B84                  .EQU $4B84       ;Alien5 control state A
M4B85                  .EQU $4B85       ;Alien5 control state B (LSB for T14xx)
M4B86                  .EQU $4B86       ;Alien5 screen coordinate X
M4B87                  .EQU $4B87       ;Alien5 screen coordinate Y
M4B88                  .EQU $4B88       ;Alien6 control state A
M4B89                  .EQU $4B89       ;Alien6 control state B (LSB for T14xx)
M4B8A                  .EQU $4B8A       ;Alien6 screen coordinate X
M4B8B                  .EQU $4B8B       ;Alien6 screen coordinate Y
M4B8C                  .EQU $4B8C       ;Alien7 control state A
M4B8D                  .EQU $4B8D       ;Alien7 control state B (LSB for T14xx)
M4B8E                  .EQU $4B8E       ;Alien7 screen coordinate X
M4B8F                  .EQU $4B8F       ;Alien7 screen coordinate Y
M4B90                  .EQU $4B90       ;Alien8 control state A
M4B91                  .EQU $4B91       ;Alien8 control state B (LSB for T14xx)
M4B92                  .EQU $4B92       ;Alien8 screen coordinate X
M4B93                  .EQU $4B93       ;Alien8 screen coordinate Y
M4B94                  .EQU $4B94       ;Alien9 control state A
M4B95                  .EQU $4B95       ;Alien9 control state B (LSB for T14xx)
M4B96                  .EQU $4B96       ;Alien9 screen coordinate X
M4B97                  .EQU $4B97       ;Alien9 screen coordinate Y
M4B98                  .EQU $4B98       ;AlienA control state A
M4B99                  .EQU $4B99       ;AlienA control state B (LSB for T14xx)
M4B9A                  .EQU $4B9A       ;AlienA screen coordinate X
M4B9B                  .EQU $4B9B       ;AlienA screen coordinate Y
M4B9C                  .EQU $4B9C       ;AlienB control state A
M4B9D                  .EQU $4B9D       ;AlienB control state B (LSB for T14xx)
M4B9E                  .EQU $4B9E       ;AlienB screen coordinate X
M4B9F                  .EQU $4B9F       ;AlienB screen coordinate Y
M4BA0                  .EQU $4BA0       ;AlienC control state A
M4BA1                  .EQU $4BA1       ;AlienC control state B (LSB for T14xx)
M4BA2                  .EQU $4BA2       ;AlienC screen coordinate X
M4BA3                  .EQU $4BA3       ;AlienC screen coordinate Y
M4BA4                  .EQU $4BA4       ;AlienD control state A
M4BA5                  .EQU $4BA5       ;AlienD control state B (LSB for T14xx)
M4BA6                  .EQU $4BA6       ;AlienD screen coordinate X
M4BA7                  .EQU $4BA7       ;AlienD screen coordinate Y
M4BA8                  .EQU $4BA8       ;AlienE control state A
M4BA9                  .EQU $4BA9       ;AlienE control state B (LSB for T14xx)
M4BAA                  .EQU $4BAA       ;AlienE screen coordinate X
M4BAB                  .EQU $4BAB       ;AlienE screen coordinate Y
M4BAC                  .EQU $4BAC       ;AlienF control state A
M4BAD                  .EQU $4BAD       ;AlienF control state B (LSB for T14xx)
M4BAE                  .EQU $4BAE       ;AlienF screen coordinate X
M4BAF                  .EQU $4BAF       ;AlienF screen coordinate Y

; Bird data structure.
; Used for all levels with the 8 birds.
; Level: 3, 4, 8, 9.
; For the bird animation during intro splash, bird0 memory is used.
B4B70                  .EQU $4B70       ;Bird0 index character block shape
B4B71                  .EQU $4B71       ;Bird0 MSB initial screen address  
B4B72                  .EQU $4B72       ;Bird0 LSB initial screen address  
B4B73                  .EQU $4B73       ;Bird0 animation phase / current shape frame
B4B74                  .EQU $4B74       ;Bird0 movement-step countdown timer
B4B75                  .EQU $4B75       ;Bird0 grid coordinate X 
B4B76                  .EQU $4B76       ;Bird0 horizontal movement step (velocity)
B4B77                  .EQU $4B77       ;Bird0 grid coordinate Y 
B4B78                  .EQU $4B78       ;Bird1 index character block shape 
B4B79                  .EQU $4B79       ;Bird1 MSB initial screen address  
B4B7A                  .EQU $4B7A       ;Bird1 LSB initial screen address  
B4B7B                  .EQU $4B7B       ;Bird1 animation phase / current shape frame
B4B7C                  .EQU $4B7C       ;Bird1 movement-step countdown timer
B4B7D                  .EQU $4B7D       ;Bird1 grid coordinate X 
B4B7E                  .EQU $4B7E       ;Bird1 horizontal movement step (velocity)
B4B7F                  .EQU $4B7F       ;Bird1 grid coordinate Y 
B4B80                  .EQU $4B80       ;Bird2 index character block shape 
B4B81                  .EQU $4B81       ;Bird2 MSB initial screen address  
B4B82                  .EQU $4B82       ;Bird2 LSB initial screen address  
B4B83                  .EQU $4B83       ;Bird2 animation phase / current shape frame
B4B84                  .EQU $4B84       ;Bird2 movement-step countdown timer
B4B85                  .EQU $4B85       ;Bird2 grid coordinate X 
B4B86                  .EQU $4B86       ;Bird2 horizontal movement step (velocity)
B4B87                  .EQU $4B87       ;Bird2 grid coordinate Y 
B4B88                  .EQU $4B88       ;Bird3 index character block shape 
B4B89                  .EQU $4B89       ;Bird3 MSB initial screen address  
B4B8A                  .EQU $4B8A       ;Bird3 LSB initial screen address  
B4B8B                  .EQU $4B8B       ;Bird3 animation phase / current shape frame
B4B8C                  .EQU $4B8C       ;Bird3 movement-step countdown timer
B4B8D                  .EQU $4B8D       ;Bird3 grid coordinate X 
B4B8E                  .EQU $4B8E       ;Bird3 horizontal movement step (velocity)
B4B8F                  .EQU $4B8F       ;Bird3 grid coordinate Y 
B4B90                  .EQU $4B90       ;Bird4 index character block shape 
B4B91                  .EQU $4B91       ;Bird4 MSB initial screen address  
B4B92                  .EQU $4B92       ;Bird4 LSB initial screen address  
B4B93                  .EQU $4B93       ;Bird4 animation phase / current shape frame
B4B94                  .EQU $4B94       ;Bird4 movement-step countdown timer
B4B95                  .EQU $4B95       ;Bird4 grid coordinate X 
B4B96                  .EQU $4B96       ;Bird4 horizontal movement step (velocity)
B4B97                  .EQU $4B97       ;Bird4 grid coordinate Y 
B4B98                  .EQU $4B98       ;Bird5 index character block shape 
B4B99                  .EQU $4B99       ;Bird5 MSB initial screen address  
B4B9A                  .EQU $4B9A       ;Bird5 LSB initial screen address  
B4B9B                  .EQU $4B9B       ;Bird5 animation phase / current shape frame
B4B9C                  .EQU $4B9C       ;Bird5 movement-step countdown timer
B4B9D                  .EQU $4B9D       ;Bird5 grid coordinate X 
B4B9E                  .EQU $4B9E       ;Bird5 horizontal movement step (velocity)
B4B9F                  .EQU $4B9F       ;Bird5 grid coordinate Y 
B4BA0                  .EQU $4BA0       ;Bird6 index character block shape 
B4BA1                  .EQU $4BA1       ;Bird6 MSB initial screen address  
B4BA2                  .EQU $4BA2       ;Bird6 LSB initial screen address  
B4BA3                  .EQU $4BA3       ;Bird6 animation phase / current shape frame
B4BA4                  .EQU $4BA4       ;Bird6 movement-step countdown timer
B4BA5                  .EQU $4BA5       ;Bird6 grid coordinate X 
B4BA6                  .EQU $4BA6       ;Bird6 horizontal movement step (velocity)
B4BA7                  .EQU $4BA7       ;Bird6 grid coordinate Y 
B4BA8                  .EQU $4BA8       ;Bird7 index character block shape 
B4BA9                  .EQU $4BA9       ;Bird7 MSB initial screen address  
B4BAA                  .EQU $4BAA       ;Bird7 LSB initial screen address  
B4BAB                  .EQU $4BAB       ;Bird7 animation phase / current shape frame
B4BAC                  .EQU $4BAC       ;Bird7 movement-step countdown timer
B4BAD                  .EQU $4BAD       ;Bird7 grid coordinate X 
B4BAE                  .EQU $4BAE       ;Bird7 horizontal movement step (velocity)
B4BAF                  .EQU $4BAF       ;Bird7 grid coordinate Y 

; Alien data structure (screen ram)
M4BB0                  .EQU $4BB0       ;Old MSB screen ram adress alien0
M4BB1                  .EQU $4BB1       ;Old LSB screen ram adress alien0
M4BB2                  .EQU $4BB2       ;MSB screen ram adress alien0
M4BB3                  .EQU $4BB3       ;LSB screen ram adress alien0
M4BB4                  .EQU $4BB4       ;Old MSB screen ram adress alien1
M4BB5                  .EQU $4BB5       ;Old LSB screen ram adress alien1
M4BB6                  .EQU $4BB6       ;MSB screen ram adress alien1
M4BB7                  .EQU $4BB7       ;LSB screen ram adress alien1
M4BB8                  .EQU $4BB8       ;Old MSB screen ram adress alien2
M4BB9                  .EQU $4BB9       ;Old LSB screen ram adress alien2
M4BBA                  .EQU $4BBA       ;MSB screen ram adress alien2
M4BBB                  .EQU $4BBB       ;LSB screen ram adress alien2
M4BBC                  .EQU $4BBC       ;Old MSB screen ram adress alien3
M4BBD                  .EQU $4BBD       ;Old LSB screen ram adress alien3
M4BBE                  .EQU $4BBE       ;MSB screen ram adress alien3
M4BBF                  .EQU $4BBF       ;LSB screen ram adress alien3
M4BC0                  .EQU $4BC0       ;Old MSB screen ram adress alien4
M4BC1                  .EQU $4BC1       ;Old LSB screen ram adress alien4
M4BC2                  .EQU $4BC2       ;MSB screen ram adress alien4
M4BC3                  .EQU $4BC3       ;LSB screen ram adress alien4
M4BC4                  .EQU $4BC4       ;Old MSB screen ram adress alien5
M4BC5                  .EQU $4BC5       ;Old LSB screen ram adress alien5
M4BC6                  .EQU $4BC6       ;MSB screen ram adress alien5
M4BC7                  .EQU $4BC7       ;LSB screen ram adress alien5
M4BC8                  .EQU $4BC8       ;Old MSB screen ram adress alien6
M4BC9                  .EQU $4BC9       ;Old LSB screen ram adress alien6
M4BCA                  .EQU $4BCA       ;MSB screen ram adress alien6
M4BCB                  .EQU $4BCB       ;LSB screen ram adress alien6
M4BCC                  .EQU $4BCC       ;Old MSB screen ram adress alien7
M4BCD                  .EQU $4BCD       ;Old LSB screen ram adress alien7
M4BCE                  .EQU $4BCE       ;MSB screen ram adress alien7
M4BCF                  .EQU $4BCF       ;LSB screen ram adress alien7
M4BD0                  .EQU $4BD0       ;Old MSB screen ram adress alien8
M4BD1                  .EQU $4BD1       ;Old LSB screen ram adress alien8
M4BD2                  .EQU $4BD2       ;MSB screen ram adress alien8
M4BD3                  .EQU $4BD3       ;LSB screen ram adress alien8
M4BD4                  .EQU $4BD4       ;Old MSB screen ram adress alien9
M4BD5                  .EQU $4BD5       ;Old LSB screen ram adress alien9
M4BD6                  .EQU $4BD6       ;MSB screen ram adress alien9
M4BD7                  .EQU $4BD7       ;LSB screen ram adress alien9
M4BD8                  .EQU $4BD8       ;Old MSB screen ram adress alienA
M4BD9                  .EQU $4BD9       ;Old LSB screen ram adress alienA
M4BDA                  .EQU $4BDA       ;MSB screen ram adress alienA
M4BDB                  .EQU $4BDB       ;LSB screen ram adress alienA
M4BDC                  .EQU $4BDC       ;Old MSB screen ram adress alienB
M4BDD                  .EQU $4BDD       ;Old LSB screen ram adress alienB
M4BDE                  .EQU $4BDE       ;MSB screen ram adress alienB
M4BDF                  .EQU $4BDF       ;LSB screen ram adress alienB
M4BE0                  .EQU $4BE0       ;Old MSB screen ram adress alienC
M4BE1                  .EQU $4BE1       ;Old LSB screen ram adress alienC
M4BE2                  .EQU $4BE2       ;MSB screen ram adress alienC
M4BE3                  .EQU $4BE3       ;LSB screen ram adress alienC
M4BE4                  .EQU $4BE4       ;Old MSB screen ram adress alienD
M4BE5                  .EQU $4BE5       ;Old LSB screen ram adress alienD
M4BE6                  .EQU $4BE6       ;MSB screen ram adress alienD
M4BE7                  .EQU $4BE7       ;LSB screen ram adress alienD
M4BE8                  .EQU $4BE8       ;Old MSB screen ram adress alienE
M4BE9                  .EQU $4BE9       ;Old LSB screen ram adress alienE
M4BEA                  .EQU $4BEA       ;MSB screen ram adress alienE
M4BEB                  .EQU $4BEB       ;LSB screen ram adress alienE
M4BEC                  .EQU $4BEC       ;Old MSB screen ram adress alienF
M4BED                  .EQU $4BED       ;Old LSB screen ram adress alienF
M4BEE                  .EQU $4BEE       ;MSB screen ram adress alienF
M4BEF                  .EQU $4BEF       ;LSB screen ram adress alienF

; Bird extended storage
; Used for all levels with the 8 birds.
B4BC0                  .EQU $4BC0       ;saved PlayerBulletState
B4BC1                  .EQU $4BC1       ;saved PlayerBulletShape
B4BC2                  .EQU $4BC2       ;saved PlayerBulletX
B4BC3                  .EQU $4BC3       ;saved PlayerBulletY
B4BC4                  .EQU $4BC4       ;saved AbovePlayerBulletMSB
B4BC5                  .EQU $4BC5       ;saved AbovePlayerBulletLSB

B4BD1                  .EQU $4BD1       ;Descent turnaround depth threshold (formation reverses when `$4BD2` passes it)
B4BD2                  .EQU $4BD2       ;Vertical scroll phase 0–31 of the bird formation (derived from `CounterB9`; master index) (0..31)
B4BD3                  .EQU $4BD3       ;Countdown timer between bird attack launches
B4BD4                  .EQU $4BD4       ;Attack sub-pattern selector (0–3, from random `$436F`) for one of four attack variants
B4BD5                  .EQU $4BD5       ;Descent step/speed value (feeds the `$3ED0` dither scroll rate)
B4BD6                  .EQU $4BD6       ;Combined scroll-phase + active-bird center index (indexes `$3EE0` curve & `T3DE0` sound)
B4BD7                  .EQU $4BD7       ;Active-bird vertical spread — computed but not consumed (vestigial)

B4BED                  .EQU $4BED       ;Unused RAM (cleared at level init, never referenced)
B4BEE                  .EQU $4BEE       ;Unused RAM (cleared at level init, never referenced)
B4BEF                  .EQU $4BEF       ;Unused RAM (cleared at level init, never referenced)

; Stack
Stack                  .EQU $4BF0       ;Stack space 4BF0:4BFF

;HW
videoRegister          .EQU $5000       ;Lower bit selects the RAM bank
scrollRegister         .EQU $5800       ;Screen scrolling
SOUNDCTLA              .EQU $6000       ;Sound control A
SOUNDCTLB              .EQU $6800       ;Sound control B
IN0                    .EQU $7000       ;Player inputs
DSW0                   .EQU $7800       ;DIP switch settings

;*****************************************************************************
; ic45
;*****************************************************************************
```
> [!NOTE]
> **Ported to C:** [`phoenix_main_loop`](../hw_video_audio.c#L123) in `hw_video_audio.c` (ASM: `0000-004F`)

```asm
                       .ORG $0000
```

### L0000:

```asm
                       NOP                         ; Start/restart and interrupts end up at 0008
                       NOP                         ;
                       NOP                         ;
                       NOP                         ;
                       NOP                         ;
                       NOP                         ;
                       NOP                         ;
                       NOP                         ;
; 
                       LD      SP,$4BFF            ; Top-ish of RAM
                       LD      H,videoRegister >> 8
                       LD      (HL),$00            ; Select the first bank of RAM
                       CALL    InitSoundScreen     ; Turn sound off and clear both screen areas
                       LD      HL,T1800            ; Screen draw info
                       LD      C,$03               ; 3 columns (rotated to 3 rows)
                       CALL    PrintTextLines      ; Draw the first 3 rows of the background (scores and coins)

;*****************************************************************************
;* Main loop begin
;*****************************************************************************
```

### MainLoop:

```asm
                       CALL    WaitVBlankCoin      ; Wait for VBlank and count any coins
                       LD      A,(GameOrAttract)   ;
                       AND     A                   ; updates the zero flag
                       JP      Z,L002D             ; if 'Attract mode'
; Game mode
                       CALL    GameStateMachine    ; controls the flow of the game.
                       CALL    UpdateScoresAndSound
                       JP      MainLoop            ; Back to top of main loop
; Attract mode (no sound, no scoreing, no manual steering)
```

### L002D:

```asm
                       LD      A,$0F               ; 0000_1111 mute the sound chip TMS36XX
                       LD      H,SOUNDCTLA >> 8    ; 60xx sound A
                       LD      (HL),A              ;
                       LD      H,SOUNDCTLB >> 8    ; 68xx sound B
                       LD      (HL),A              ;
                       CALL    UpdateSoundControlRAM
                       NOP                         ;
                       CALL    CoinChecking        ;
                       AND     A                   ; updates the zero flag
                       JP      Z,L0046             ; No credits ... continue splash
                       CALL    PromptForStartGame  ;
                       JP      MainLoop            ; Back to top of main loop
; Continue splash 
```

### L0046:

```asm
                       CALL    SplashAndDemo       ;
                       JP      MainLoop            ; Back to top of main loop
;*****************************************************************************
;* Main loop end
;*****************************************************************************

```
> [!NOTE]
> **Ported to C:** [`init_sound_screen`](../hw_video_audio.c#L94) in `hw_video_audio.c` (ASM: `0050-006A`)

```asm
                       .ORG $0050
;*****************************************************************************
;* Initialize the sound (off) and screen (clear)
;*****************************************************************************
```

### InitSoundScreen:

```asm
                       LD      H,SOUNDCTLB >> 8    ; 68xx sound B
                       LD      (HL),$00            ; Sound off
                       LD      H,SOUNDCTLA >> 8    ; 60xx sound A
                       LD      (HL),$00            ; Sound off
                       LD      H,scrollRegister >> 8
                       LD      (HL),$00            ; First memory bank
                       CALL    ClearRAMBank        ; Clear the bank (includes screen)
                       LD      H,videoRegister >> 8
                       LD      (HL),$01            ; Second memory bank
                       CALL    ClearRAMBank        ; Clear the bank (includes screen)
                       LD      H,videoRegister >> 8
                       LD      (HL),$00            ; Back to first memory bank
                       RET                         ; Done

;*****************************************************************************
;* Clear a RAM Bank (bank 0 or 1)
;* Set the lower bit of the video register to pick the bank before calling.
;* 4000 - 4BF8
;* We call this function, which means we don't want to clear the return on the stack.
;* That's why we start clearing at 4BF8 instead of 4BFF.
;* Since screen memory is part of this bank, we are clearing the screen too.
;*****************************************************************************
```

### ClearRAMBank:

```asm
                       LD      HL,$4BF8            ; Highest point ... skip the top of the stack
                       LD      A,$3F               ; Stop when H reaches 3F
```

### L0070:

```asm
                       LD      (HL),$00            ; Clear the memory
                       DEC     HL                  ; Point to next
                       CP      H                   ; All done?
                       JP      NZ,L0070            ; No ... go back for all
                       RET                         ; Done

;*****************************************************************************
;* Slow printing the static texts and filling the scroll register
;* with background tiles.
;* Only used at attract mode during the intro splash.
;*****************************************************************************
```

### SlowPrintScrollRegisterUpdate:

```asm
                       CALL    SlowPrintScoreAverageTable
                       JP      L06F0               ; update scroll register and fill background

```
> [!NOTE]
> **Ported to C:** [`wait_vblank_coin`](../hw_video_audio.c#L30) in `hw_video_audio.c` (ASM: `0080-00B5`)

```asm
                       .ORG $0080
;*****************************************************************************
;* Wait for the vertical blanking and then handle coin counting
;*****************************************************************************
```

### WaitVBlankCoin:

```asm
                       LD      H,DSW0 >> 8         ; 78xx DSW0 Check ...
                       LD      A,(HL)              ; ... screen blanking flag
                       AND     $80                 ; Wait for it ...
                       JP      Z,WaitVBlankCoin    ; ... to set
; 
```

### L0088:

```asm
                       LD      A,(HL)              ; Check screen blanking flag
                       AND     $80                 ; Wait for it ...
                       JP      NZ,L0088            ; ... to clear (0=in blanking)
                       LD      H,IN0 >> 8          ; 70xx IN0 Current value ...
                       LD      A,(HL)              ; ... of IN0 inputs
                       LD      HL,IN0Current       ; Value from ...
                       LD      B,(HL)              ; ... last read
                       LD      (HL),A              ; Store new value
                       INC     L                   ; To 43A1
                       LD      (HL),B              ; Store old value
                       LD      L,$9B               ; Bump the ...
                       CALL    AddOneToMem         ; ... ?? counter
                       LD      L,$8F               ; Get number ...
                       LD      A,(HL)              ; ... of coins
;
; !! There are two digits for "coins" on the screen, but only the one's digit is
; !! changed. Once you get to 9, the code stops counting. It takes the coin
; !! from you, but it doesn't give you credit.
;
                       CP      $09                 ; Already 9?
                       RET     Z                   ; Yes ... nothing more to check
                       JP      NC,L0000            ; More than 9? OOPS -- soft reset
                       LD      B,$01               ; Coin bit of the input register
                       CALL    CheckInputBits      ; Has the coin input gone from 1 to 0?
                       RET     Z                   ; No ... no coins inserted ... done
                       LD      L,$8F               ; Add one ...
                       INC     (HL)                ; ... to coin count
                       LD      A,(HL)              ; Current value ...
                       ADD     $20                 ; ... to number tile
                       LD      ($4142),A           ; Change number of coins on screen
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`check_input_bits`](../utilities.c#L16) in `utilities.c` (ASM: `00BB-00C3`)

```asm
                       .ORG $00BB
;*****************************************************************************
;* Check to see if a particular bit(s) in the input register has changed
;* from 1 to 0 since last we checked. Return NZ if transitioned from 1 to 0.
;*****************************************************************************
```

### CheckInputBits:

```asm
                       LD      HL,IN0Current       ; Get current ...
                       LD      A,(HL)              ; ... input value
                       CPL                         ; Flip the current bits
                       AND     B                   ; Mask off all but the ones we are checking
                       INC     L                   ; Point to last input value
                       AND     (HL)                ; Zero unles new bit is 0 and old is 1
                       RET                         ; Return state

;*****************************************************************************
;* Prints the number pointed to by HL (points to the end of the number) to the screen pointed
;* to by DE (points to the end of the screen area). B is the number of digits to print.
;*****************************************************************************
```

### PrintNumber:

```asm
                       LD      A,(HL)              ; Get the two digits
                       AND     $0F                 ; Keep the LSB
                       OR      $20                 ; Offset to number tile
                       LD      (DE),A              ; Store the number tile to screen memory
                       CALL    LeftOneColumn       ; next screen position
                       DEC     B                   ; All done?
                       RET     Z                   ; Yes ... out
                       LD      A,(HL)              ; Keep the ...
                       RRCA                        ; ...
                       RRCA                        ; ...
                       RRCA                        ; ...
                       RRCA                        ; ...
                       AND     $0F                 ; ... LSB
                       OR      $20                 ; Offset to number tile
                       LD      (DE),A              ; Store the number tile to screen memory
                       CALL    LeftOneColumn       ; next screen position
                       DEC     HL                  ; Next data position
                       DEC     B                   ; All digits done?
                       JP      NZ,PrintNumber      ; No ... keep going
                       RET                         ; Yes ... out

```
> [!NOTE]
> **Ported to C:** [`splash_and_demo`](../attract_mode.c#L32) in `attract_mode.c` (ASM: `00E3-013A, 0140-0172`)

```asm
                       .ORG $00E3
;*****************************************************************************
;* Handles the intro splash and the game demo.
;*****************************************************************************
```

### SplashAndDemo:

```asm
                       LD      HL,M4399            ; starts with 0
                       CALL    AddOneToMem         ; increases it by one
                       LD      BC,$0001            ;
                       CALL    CompareBCtoMem      ;
                       JP      Z,PrintCopyright    ; do if Counter98 is >= 00 01
                       LD      BC,$0002            ;
                       LD      DE,$011F            ; used as delay counter
                       CALL    SubtractIfEnough    ;
                       JP      NC,SlowPrintScoreAverageTable    ; do if Counter98 is >= 00 02
                       LD      BC,$0120            ; for a longer break
                       CALL    CompareBCtoMem      ;
                       JP      Z,DrawScoreAverageTableTiles     ; do if Counter98 is >= 01 20
                       LD      C,$B0               ; for a short break
                       CALL    CompareBCtoMem      ;
                       JP      Z,PrintCopyright    ; do if Counter98 is >= 01 B0
                       LD      C,$B8               ;
                       CALL    CompareBCtoMem      ;
                       JP      Z,InitGlobalLevelData            ; do if Counter98 is >= 01 B8
                       LD      C,$C0               ; for a short break
                       LD      DE,$02DF            ;
                       CALL    SubtractIfEnough    ;
                       JP      NC,SlowPrintScrollRegisterUpdate ; do if Counter98 is >= 01 C0
                       LD      BC,$0300            ;
                       LD      DE,$03AF            ;
                       CALL    SubtractIfEnough    ;
                       JP      NC,DrawIntroBirdAnimationFrame   ; do if Counter98 is >= 03 00
                       LD      BC,$03E6            ;
                       LD      DE,$FFFF            ;
                       CALL    SubtractIfEnough    ;
                       JP      NC,GameDemo         ; do if Counter98 is >= 03 E6
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`clear_fore_and_background`](../attract_mode.c#L113) in `attract_mode.c` (ASM: `0140-0172`)

```asm
                       .ORG $0140
;*****************************************************************************
;* Clears foreground and background but leaves the 3 score rows.
;*****************************************************************************
```

### ClearForeAndBackground:

```asm
                       CALL    ClearBackground     ; Clear the background
                       CALL    WaitVBlankCoin      ; Wait for VBlank
                       CALL    ClearForeground     ; Clear the foreground (leave the 3 score rows)
                       LD      HL,GameAndDemoOrSplash
                       LD      (HL),$02            ; set to: 'Intro splash'
                       INC     L                   ; GameState
                       LD      (HL),$00            ; to 0
                       NOP                         ; Old command removed or space for a future replace patch
                       NOP                         ; ..
                       NOP                         ; ..
                       LD      L,$B8               ; LevelAndRound, $43B9, AliensLeft, BirdsLeft, $43BC, $43BD, BonusLivesAt, $43BF to 0
                       LD      B,$08               ; number of bytes to clear
                       CALL    ClearBbytesAtHL     ;
                       LD      L,$BA               ; Set AliensLeft
                       LD      (HL),$10            ; to 16 aliens left in wave
                       LD      L,$BE               ;
                       LD      A,(DSW0)            ; 78xx DSW0, get DIP switch settings
                       AND     $0C                 ; mask out 0000_1100 the Bonus lives
                       RLCA                        ; rotate left ..
                       RLCA                        ; .. to 0011_0000
                       ADD     $30                 ; -> $30,$40,$50,$60
                       LD      (HL),A              ; save to BonusLivesAt = 3000/4000/5000/6000 pts (BCD)
                       LD      H,scrollRegister >> 8
                       LD      (HL),$00            ; init screen scrolling
                       CALL    WaitVBlankCoin      ;
                       RET                         ;

;*****************************************************************************
;* Used for the game demo during attract mode.
;* Returning the bits for feeding the IN0Current for the simulated player inputs.
;* Resulting values are depending on $4398:$4399 .
;* Counter value goes from $03E6 to $1510 during the demo.
;* 1010_1110...move left
;* 1100_1110...move right
;* 1111_1110...push fire
;* 0111_1110...push shield
;*****************************************************************************
```

### GetPlayerInputsForDemo:

```asm
                       LD      A,(HL)              ; get $4399 (LSB from 16 bit counter)
                       AND     $7F                 ; mask out 0111_1111, (counter goes from 00 to $7F)
                       LD      B,$CE               ; return : 1100_1110...move right
                       CP      $1F                 ; 1st trigger point of demo
                       RET     C                   ; return if greater
                       LD      B,$FE               ; 1111_1110...push fire
                       RET     Z                   ; return if equal
                       LD      B,$AE               ; 1010_1110...move left
                       CP      $5F                 ; 2nd trigger point of demo
                       RET     C                   ; return if greater
                       LD      B,$FE               ; 1111_1110...push fire
                       RET     Z                   ; return if equal
                       LD      B,$CE               ; 1100_1110...move right
                       CP      $7F                 ; 3rd trigger point of demo
                       RET     C                   ; return if greater
                       LD      B,$FE               ; 1111_1110...push fire
                       DEC     L                   ;
                       LD      A,(HL)              ; get $4398 (MSB from 16 bit counter)
                       CP      $09                 ; 4rd trigger point of demo
                       RET     NZ                  ; return if not equal
                       LD      B,$7E               ; 0111_1110...push shield
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`slow_print_score_average_table`](../attract_mode.c#L198) in `attract_mode.c` (ASM: `0196-01CD`)

```asm
                       .ORG $0196
;*****************************************************************************
;* Slow printing the static texts for the score average table
;* and the big letters of the Phoenix title. Prints ONE character per call,
;* driven by Counter98 ($4398:$4399). Attract-mode only.
;* In: HL = $4399 (Counter98 LSB).
;*****************************************************************************
```

### SlowPrintScoreAverageTable:

```asm
                       LD      A,(HL)              ; get actual index for slow print ($4399)
                       AND     $1F                 ; mask out 0001_1111
                       CP      $06                 ; reached state 6 ?
                       RET     C                   ; no..return
                       LD      E,A                 ; save the state
                       LD      A,(HL)              ; get actual index for slow print ($4399)
                       AND     $E0                 ; mask out 1110_0000
                       LD      C,A                 ; save bits 5,6,7
                       DEC     L                   ;
                       LD      B,(HL)              ; get zero reference from $4398
                       LD      L,$A8               ; ..and..
                       LD      (HL),B              ; save it to $43A8
                       INC     L                   ;
                       LD      (HL),C              ; save bits 5,6,7 to $43A9
                       LD      BC,T1860            ; data block starting with 'INSERT  COIN' text
                       CALL    AddBCtoMem          ; stores MSB LSB
                       LD      A,(HL)              ;
                       DEC     L                   ;
                       LD      H,(HL)              ;
                       LD      L,A                 ;
                       LD      A,E                 ;
                       LD      D,(HL)              ; get the data
                       INC     L                   ;
                       LD      E,(HL)              ;
                       DEC     L                   ;
                       LD      C,A                 ;
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      A,C                 ;
                       SUB     $06                 ;
                       LD      C,A                 ;
                       JP      Z,L01C8             ;
```

### L01C1:

```asm
                       CALL    RightOneColumn      ; move to next screen position
                       DEC     C                   ;
                       JP      NZ,L01C1            ;
```

### L01C8:

```asm
                       LD      A,(HL)              ;
                       LD      (DE),A              ; print one character on the screen
                       JP      L14E0               ; check for coin event

```
> [!NOTE]
> **Ported to C:** [`print_text_lines`](../utilities.c#L62) in `utilities.c` (ASM: `01D0-01E0`)

```asm
                       .ORG $01D0
;*****************************************************************************
;* Print the top 3 lines (scores, lives, coins)
;*****************************************************************************
```

### PrintTextLines:

```asm
                       LD      D,(HL)              ; Get ...
                       INC     L                   ; ... the ...
                       LD      E,(HL)              ; ... screen coord
                       LD      A,L                 ; Add 5 ...
                       ADD     $05                 ; ... go get ...
                       LD      L,A                 ; ... data
                       LD      B,$1A               ; 26 columns
                       CALL    DrawRow             ; Draw next row
                       DEC     C                   ; All lines done?
                       JP      NZ,PrintTextLines   ; No ... draw all rows
                       RET                         ; Done

;*****************************************************************************
;* Print the copyright lines (bottom 3 lines)
;*****************************************************************************
```

### PrintCopyright:

```asm
                       CALL    ClearForeAndBackground
```

### L01E4:

```asm
                       LD      HL,T1960            ; "PHOENIX ... U.S.A"
                       LD      C,$03               ; 3 lines at the bottom
                       JP      PrintTextLines      ; Print the copyright

```
> [!NOTE]
> **Ported to C:** [`draw_row`](../utilities.c#L107) in `utilities.c` (ASM: `01ED-01F7`)

```asm
                       .ORG $01ED
;*****************************************************************************
;* Remember the screen is rotated.
;* This draws a column in screen memory (row on the screen)
;*****************************************************************************
```

### DrawRow:

```asm
                       LD      A,(HL)              ; Copy the data ...
                       LD      (DE),A              ; .. to the screen
                       INC     HL                  ; Next in data
                       CALL    RightOneColumn      ; Move DE to next row
                       DEC     B                   ; All drawn?
                       JP      NZ,DrawRow          ; Draw them all
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`add_one_to_mem`](../utilities.c#L202) in `utilities.c` (ASM: `0200-0205`)

```asm
                       .ORG $0200
;*****************************************************************************
;* Two-byte +1 to (HL-1) : (HL).
;*****************************************************************************
```

### AddOneToMem:

```asm
                       INC     (HL)                ; Add one to LSB
                       RET     NZ                  ; We didn't overflow ... done
                       DEC     L                   ; Back up to MSB
                       INC     (HL)                ; Carry into the MSB
                       INC     L                   ; Restore point to LSB
                       RET                         ; Done

;*****************************************************************************
;* Two-byte addition. BC is added to (HL-1) : (HL).
;*****************************************************************************
```

### AddBCtoMem:

```asm
                       LD      A,(HL)              ; Get the lower byte
                       ADD     A,C                 ; Add C to the lower
                       LD      (HL),A              ; Store the new lower
                       DEC     L                   ; Back up to upper byte
                       LD      A,(HL)              ; Add B and carry ...
                       ADC     A,B                 ; ... to upper byte
                       LD      (HL),A              ; Store the new upper byte
                       INC     L                   ; Restore pointer to LSB
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`left_one_column`](../utilities.c#L303) in `utilities.c` (ASM: `0210-0216`)

```asm
                       .ORG $0210
;*****************************************************************************
;* Add 32 (left one column on the rotated screen) to DE (two bytes)
;*****************************************************************************
```

### LeftOneColumn:

```asm
                       LD      A,E                 ; Add ...
                       ADD     $20                 ; ... 32 to ...
                       LD      E,A                 ; ... E
                       RET     NC                  ; No carry ... we are done
                       INC     D                   ; Carry into D
                       RET                         ; Done

;*****************************************************************************
;* Subtract 32 (right one column on the rotated screen) from DE (two bytes)
;*****************************************************************************
```

### RightOneColumn:

```asm
                       LD      A,E                 ; Subtract ...
                       SUB     $20                 ; ... 32 from ...
                       LD      E,A                 ; ... E
                       RET     NC                  ; No borrow ... we are done
                       DEC     D                   ; Borrow from D
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`add_to_score`](../utilities.c#L321) in `utilities.c` (ASM: `0220-0232`)

```asm
                       .ORG $0220
;*****************************************************************************
;* 3-byte (6 digit) BCD addition. Add BC*10 to (HL-2):(HL-1):(HL).
;* The games keeps the lowest digit of the scores to 0.
;*****************************************************************************
```

### AddToScore:

```asm
                       XOR     A                   ; !! Pointless. We are about to change A and the flags
                       LD      A,(HL)              ; Lowest 2 digits
                       ADD     A,C                 ; Add C to score
                       DAA                         ; Adjust for binary coded decimal
                       LD      (HL),A              ; Update lowest 2 digits
                       DEC     L                   ; Point to middle 2 digits
                       LD      A,(HL)              ; Add B to ...
                       ADC     A,B                 ; ... score
                       DAA                         ; Adjust for BCD
                       LD      (HL),A              ; Store the middle 2 digits
                       DEC     L                   ; Point to the upper 2 digits
                       LD      A,(HL)              ; Add in ...
                       ADC     $00                 ; ... any carry
                       DAA                         ; Adjust for binary coded decimal
                       LD      (HL),A              ; Store the upper 2 digits
                       INC     L                   ; Restore ...
                       INC     L                   ; ... pointer
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`compare_bc_to_mem`](../utilities.c#L234) in `utilities.c` (ASM: `0258-025F`)

```asm
                       .ORG $0258
;*****************************************************************************
;* Two byte compare of BC to memory at (HL-1):(HL)
;*****************************************************************************
```

### CompareBCtoMem:

```asm
                       LD      A,(HL)              ; Value from memory
                       CP      C                   ; Are the lower values the same?
                       RET     NZ                  ; No ... return not-zero
                       DEC     L                   ; Point to MSB
                       LD      A,(HL)              ; Get the MSB value
                       INC     L                   ; Restore the pointer
                       CP      B                   ; Compare the MSBs
                       RET                         ; Return the flags

;*****************************************************************************
;* Subtract DE from memory if memory is greater/equal to BC.
;*****************************************************************************
```

### SubtractIfEnough:

```asm
                       CALL    SubtractFromMemory  ; Try subtraction. Is memory larger (or equal) to BC?
                       RET     C                   ; No ... ignore request
                       CALL    SubtractToMemory    ; Yes ... subtract DE from memory
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`l0270_subtract_from_memory`](../utilities.c#L259) in `utilities.c` (ASM: `0270-0276`)

```asm
                       .ORG $0270
;*****************************************************************************
;* Two byte subtraction of memory from BC. BC = BC -  (HL-1):(HL)
;*****************************************************************************
```

### SubtractFromMemory:

```asm
                       LD      A,(HL)              ; Get the low byte
                       SUB     C                   ; Subtract from C
                       DEC     L                   ; Point to upper byte
                       LD      A,(HL)              ; Get the upper byte
                       SBC     B                   ; Subtract from B (with borrow)
                       INC     L                   ; Restore pointer
                       RET                         ; Done

;*****************************************************************************
;* Two byte subtraction of DE from memory. (HL-1):(HL) = (HL-1):(HL) - DE
;*****************************************************************************
```

### SubtractToMemory:

```asm
                       LD      A,E                 ; Lower byte
                       SUB     (HL)                ; Subtract it from memory
                       DEC     L                   ; Point to upper byte
                       LD      A,D                 ; Value to A
                       SBC     (HL)                ; Subtract upper byte from memory (with borrow)
                       INC     L                   ; Restore pointer
                       RET                         ; Done

                       .ORG $0280
;*****************************************************************************
;* Two byte compare of HL to BC
;*****************************************************************************
```

### CompareHLtoBC:

```asm
                       LD      A,L                 ; Compare lower ...
                       CP      C                   ; ... bytes
                       RET     NZ                  ; Not the same ... return NZ
                       LD      A,H                 ; Compare upper ...
                       CP      B                   ; ... bytes
                       RET                         ; Return the check

```
> [!NOTE]
> **Ported to C:** [`prompt_for_start_game`](../attract_mode.c#L293) in `attract_mode.c` (ASM: `0288-02EE`)

```asm
                       .ORG $0288
;*****************************************************************************
;* Start game screen
;*****************************************************************************
```

### PromptForStartGame:

```asm
                       CALL    ClearForeAndBackground
                       LD      HL,T19C0            ; 
                       LD      C,$02               ; print two lines: 'PUSH ONLY...1PLAYER BUTTON'
                       CALL    PrintTextLines      ;
                       LD      C,$02               ;
                       CALL    CoinChecking        ;
                       CP      $02                 ; 2 player mode possible if credit > 1
                       JP      C,L02A7             ;
                       LD      HL,T1BA0            ;
                       LD      C,$01               ; print one line: '1 OR 2PLAYERS BUTTON'
                       CALL    PrintTextLines      ;
                       LD      C,$06               ;
```

### L02A7:

```asm
                       LD      A,(IN0)             ; 70xx IN0  Get the bits...
                       CPL                         ; ...for the two...
                       AND     C                   ; ...start buttons and...
                       RET     Z                   ; ...ret if no start button was pressed.
                       CALL    DecrementCoins      ; (GameOrAttract will be affected here as well)
                       CALL    UpdateHiScore       ;
                       CALL    ClearAndPrintScores ;
                       CALL    GetPlayerLivesFromDip
                       CALL    ClearForeAndBackground
                       LD      H,videoRegister >> 8
                       LD      (HL),$01            ;
                       CALL    ClearForeAndBackground
                       LD      H,videoRegister >> 8
                       LD      (HL),$00            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`decrement_coins`](../attract_mode.c#L366) in `attract_mode.c` (ASM: `02CB-02EF`)

```asm
                       .ORG $02CB
;*****************************************************************************
;* Coin handling
;*****************************************************************************
```

### DecrementCoins:

```asm
                       LD      C,$01               ; Value for 'one player game mode'
                       CP      $02                 ; A register holds the value of start buttons
                       JP      Z,L02D4             ; jump if 'start 1' was pressed.
                       LD      C,$02               ; Value for 'two players game mode'
```

### L02D4:

```asm
                       LD      HL,GameOrAttract    ; 
                       LD      (HL),C              ; set it to 1 or 2 and leave the attract mode.
                       LD      A,(DSW0)            ; 78xx DSW0
                       AND     $10                 ; mask for coinage 0001_0000
                       JP      Z,L02E3             ;
                       LD      A,C                 ;
                       RLCA                        ; Multiply by 2
                       LD      C,A                 ;
```

### L02E3:

```asm
                       LD      L,CoinCount & $FF   ; LSB of CoinCount
                       LD      A,(HL)              ; get CoinCount value
                       SUB     C                   ; decrement coins
                       LD      (HL),A              ; save it
                       ADD     $20                 ; map value to character code
                       LD      (ForegroundScreen+$142),A ; updates the number of coins on the screen
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`update_hi_score`](../state_init.c#L120) in `state_init.c` (ASM: `02F0-032D`)

```asm
                       .ORG $02F0
;*****************************************************************************
;* Copy the score to hi score if greater
;*****************************************************************************
```

### UpdateHiScore:

```asm
                       LD      DE,Score1low        ; score of player 1
                       LD      HL,HiScorelow       ; current hi score
                       CALL    L0314               ;
                       CALL    NC,L0320            ;
                       LD      E,Score2low & $FF   ; LSB of Score2low
                       LD      L,HiScorelow & $FF  ; LSB of HiScorelow
                       CALL    L0314               ;
                       CALL    NC,L0320            ;
                       LD      L,HiScorelow & $FF  ; LSB of HiScorelow
                       LD      DE,$4141            ; High-score Screen coordinates (LSB)
                       LD      B,$06               ; 6 digits
                       CALL    PrintNumber         ; Print the 6-digit number
                       RET                         ; Done

                       .ORG $0314
;*****************************************************************************
;* Generic 3 byte BCD comparator
;*****************************************************************************
```

### L0314:

```asm
                       LD      A,(DE)              ;
                       SUB     (HL)                ;
                       DEC     E                   ;
                       DEC     L                   ;
                       LD      A,(DE)              ;
                       SBC     (HL)                ;
                       DEC     E                   ;
                       DEC     L                   ;
                       LD      A,(DE)              ;
                       SBC     (HL)                ;
                       RET                         ;

                       .ORG $0320
```

### L0320:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`clear_and_print_scores`](../hw_video_audio.c#L196) in `hw_video_audio.c` (ASM: `032E-034E`)

```asm
                       .ORG $032E
;*****************************************************************************
;* Update of the score values on screen.
;*****************************************************************************
```

### ClearAndPrintScores:

```asm
                       LD      HL,M4380            ; Clear scores..
```

### L0331:

```asm
                       LD      (HL),$00            ; ..from $4380..
                       INC     HL                  ;
                       LD      A,L                 ;
                       CP      $88                 ; ..to $4387
                       JP      NZ,L0331            ;
                       LD      L,Score1low & $FF   ; print player 1 score
                       LD      DE,$4261            ; Score1 screen coordinates (LSB)
                       LD      B,$06               ; 6 digits
                       CALL    PrintNumber         ;
                       LD      L,Score2low & $FF   ; print player 2 score
                       LD      DE,$4021            ; Score2 screen coordinates (LSB)
                       LD      B,$06               ; 6 digits
                       CALL    PrintNumber         ;
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`get_player_lives_from_dip`](../state_init.c#L89) in `state_init.c` (ASM: `0350-0366`)

```asm
                       .ORG $0350
;*****************************************************************************
;* Gets the DIP switch settings for player lives.
;*****************************************************************************
```

### GetPlayerLivesFromDip:

```asm
                       LD      A,(DSW0)            ; 78xx DSW0, get DIP switch settings
                       AND     $03                 ; mask out 0000_0011 number of lives
                       ADD     $03                 ; to get : 03, 04, 05 or 06
                       LD      B,A                 ;
                       LD      HL,Player1Lives     ;
                       LD      (HL),B              ; save it
                       LD      L,GameOrAttract & $FF
                       LD      A,(HL)              ; load GameOrAttract and ..
                       CP      $01                 ; check if one or two players mode
                       JP      Z,UpdateLivesScreen ;
                       LD      L,Player2Lives & $FF
                       LD      (HL),B              ; save it to Player2Lives

;*****************************************************************************
;* Updates the number of lives on the screen
;*****************************************************************************
```

### UpdateLivesScreen:

```asm
                       LD      L,Player1Lives & $FF
                       LD      A,(HL)              ; load Player1Lives
                       OR      $20                 ; map value to character code
                       LD      (ForegroundScreen+$2A2),A ; number of lives, for player 1 at screen ram
                       INC     L                   ;
                       LD      A,(HL)              ; load Player2Lives
                       OR      $20                 ; map value to character code
                       LD      (ForegroundScreen+$62),A ; number of lives, for player 2 at screen ram
                       RET                         ;

;*****************************************************************************
;* Update the sound control RAM registers
;*****************************************************************************
```

### UpdateSoundControlRAM:

```asm
                       LD      HL,SoundControlA    ;
                       LD      (HL),A              ;
                       INC     L                   ; and update ..
                       LD      (HL),A              ; .. SoundControlB
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`clear_foreground`](../hw_video_audio.c#L237) in `hw_video_audio.c` (ASM: `0380-039D`)

```asm
                       .ORG $0380
;*****************************************************************************
;* Clears the foreground except for the top 3 rows (the scores)
;*****************************************************************************
```

### ClearForeground:

```asm
                       LD      HL,ForegroundScreen+$33F       ; End of foreground screen
                       LD      DE,$001F            ; 00 for clear and 1F for finding end of a column
                       LD      BC,$033F            ; 03 for leaving top 3 rows and 3F for find the beginning of screen memory
```

### L0389:

```asm
                       LD      (HL),D              ; Clear the screen
                       DEC     HL                  ; Next location
                       LD      (HL),D              ; Clear the screen
                       DEC     HL                  ; Next location
                       LD      A,L                 ; Keep lower 5 ...
                       AND     E                   ; ... bits (32 bytes in a column)
                       CP      B                   ; At the top of the column?
                       JP      NZ,L0389            ; No ... keep clearing the column
                       LD      (HL),D              ; Clear the 4th column from the top
                       DEC     HL                  ; To ...
                       DEC     HL                  ; ... top ...
                       DEC     HL                  ; ... of the ...
                       DEC     HL                  ; ... row
                       LD      A,H                 ; Have we reached ...
                       CP      C                   ; ... 3FFF ?
                       JP      NZ,L0389            ; No ... clear all columns
                       RET                         ; Done

```
> [!NOTE]
> **Ported to C:** [`clear_background`](../hw_video_audio.c#L155) in `hw_video_audio.c` (ASM: `03A0-03AF`)

```asm
                       .ORG $03A0
;*****************************************************************************
;* Clears the background screen.
;*****************************************************************************
```

### ClearBackground:

```asm
                       LD      HL,BackgroundScreen+$33F       ; End of background screen memory
                       LD      DE,$0047            ; 00 for clear and 47 to find the beginning of screen memory
```

### L03A6:

```asm
                       LD      (HL),D              ; Clear the screen
                       DEC     HL                  ; Next location
                       LD      (HL),D              ; Clear the screen
                       DEC     HL                  ; Next location
                       LD      A,H                 ; Have we reached ...
                       CP      E                   ; HL = 47FF ?
                       JP      NZ,L03A6            ; No ... keep clearing
                       RET                         ; Done

;*****************************************************************************
;* The game demo is using the real game code with simulated player inputs.
;* The timeline of the game demo, as part of the attract mode,
;* is covered by a 16 bit counter $4398:$4399.
;* 1st demo from value: $03E6 to $07A0.
;* 2nd demo from value: $0800 to $0B60.
;* 3rd demo from value: $0C00 to $1510.
;*****************************************************************************
```

### GameDemo:

```asm
                       LD      BC,$07A0            ;
                       CALL    SubtractFromMemory  ;
                       JP      C,L03CE             ;
                       CALL    CompareBCtoMem      ;
                       JP      Z,L03EB             ;
                       LD      BC,$0B60            ;
                       CALL    SubtractFromMemory  ;
                       JP      C,L03CE             ;
                       CALL    CompareBCtoMem      ;
                       JP      Z,L03E2             ;
```

### L03CE:

```asm
                       CALL    GetPlayerInputsForDemo
                       LD      HL,IN0Current       ;
                       LD      A,(HL)              ;
                       AND     $01                 ; mask out real button presses, but leave the coin event.
                       OR      B                   ; feed the IN0Current with movement data
                       LD      (HL),A              ; for the game demo.
                       JP      GameStateMachine    ;

                       .ORG $03E2
;*****************************************************************************
;* Changing the game demo level at attract mode.
;*****************************************************************************
```

### L03E2:

```asm
                       LD      BC,$0108            ; Next interval game state is 1, set LevelAndRound to 1st round, level 8 (mothership wave)
                       LD      DE,$1000            ; set AliensLeft to 1 and BirdsLeft to 0 ?
                       JP      L03F1               ; 

;*****************************************************************************
;* Changing the game demo level at attract mode.
;*****************************************************************************
```

### L03EB:

```asm
                       LD      BC,$0104            ;
                       LD      DE,$0008            ;
```

### L03F1:

```asm
                       LD      HL,GameState        ; Next interval game state ...
                       LD      (HL),B              ; ... is 1 (flashing of score)
                       LD      L,$B8               ;
                       LD      (HL),C              ; set LevelAndRound to 1st round, level 4 (blue birds wave)
                       LD      L,$BA               ;
                       LD      (HL),D              ; set AliensLeft to 0
                       INC     L                   ;
                       LD      (HL),E              ; set BirdsLeft to 8
                       RET                         ;

                       .ORG $0400
;*****************************************************************************
;* Game state machine.
;* Jump to function by number in GameState.
;*****************************************************************************
```

### GameStateMachine:

```asm
                       LD      HL,T040E            ; Jump table
                       LD      A,(GameState)       ;
                       RLCA                        ; *2
                       ADD     A,L                 ; Offset ...
                       LD      L,A                 ; ... into the table
                       LD      A,(HL)              ; MSB of destination
                       INC     L                   ; Get the
                       LD      L,(HL)              ; ... LSB of destination
                       LD      H,A                 ; Now point to function
                       JP      (HL)                ; Jump to function

; Notice these addresses are MSB:LSB (backwards from the processor's endianness)
```

### T040E:

```asm
                       .MSFIRST
                       .DW L0430                   ; game state 0: called once at 'new game start'
                       .DW L04AC                   ; game state 1: called for each frame during 'flashing of score1 or 2'
                       .DW L0515                   ; game state 2: called once for initialization of game and level data
                       .DW L0800                   ; game state 3: called for each frame of normal game play
                       .DW L0AEA                   ; game state 4: called for each frame of 'player ship partikel explosion'
                       .DW L0B60                   ; game state 5: called for each frame during 'GAME OVER' text
                       .DW L2400                   ; game state 6: called for each frame during 'mother ship partikel explosion'
                       .DW L244C                   ; game state 7: called for each frame during 'mother ship score display'

;*****************************************************************************
;* Set lower bits of video register,
;* for the color palette, memory bank, and the screen flipping at cocktail mode.
;*****************************************************************************
```

### SetBitsVideoRegister:

```asm
                       LD      A,(GameAndDemoOrSplash)
                       AND     $01                 ; mask out 0000_0001 for 'memory bank'
                       LD      B,A                 ;
                       LD      A,(LevelAndRound)   ;
                       AND     $02                 ; masc out 0000_0010 for 'color palette'
                       OR      B                   ; set the bits at...
                       LD      (videoRegister),A   ; 50xx video register
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`state_0_new_game_start`](../game_state_machine.c#L54) in `game_state_machine.c` (ASM: `0430-045B, 04A0-04AB`)

```asm
                       .ORG $0430
;*****************************************************************************
;* Game state 0.
;* New game start.
;*****************************************************************************
```

### L0430:

```asm
                       LD      HL,GameState        ; Next interval game state ...
                       LD      (HL),$01            ; ... is 1 (flashing of score)
                       INC     L                   ;
                       LD      (HL),$80            ; Set value for CounterA5 (score flash time)
                       LD      L,GameAndDemoOrSplash & $FF   ; save the value of..
                       LD      A,(HL)              ; .. GameAndDemoOrSplash
                       LD      (HL),$00            ; set it to game demo / game play
                       CP      $02                 ;
                       RET     Z                   ; return if it was 'Intro splash' before.
                       LD      (HL),A              ; set GameAndDemoOrSplash to 'Game and demo for player 1'
                       DEC     L                   ;
                       LD      A,(HL)              ; get GameOrAttract
                       CP      $01                 ;
                       RET     Z                   ; return if 'One player game mode'
                       INC     L                   ;
                       LD      A,(HL)              ; get GameAndDemoOrSplash
                       AND     A                   ; updates the zero flag
                       JP      Z,L04A0             ; if 'Game and demo'
                       LD      L,$90               ;
                       LD      A,(HL)              ; get Player1Lives
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; return if no lives left.
                       LD      L,$A3               ;
                       LD      (HL),$00            ; set GameAndDemoOrSplash to 'Game and demo for player 1'
                       LD      BC,$0100            ; from bank 1 to bank 0
                       CALL    CopyMemoryBank      ; to toggle the player
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`stars_scroll_down`](../hw_video_audio.c#L266) in `hw_video_audio.c` (ASM: `0460-049D, 067A-06AF`)

> [!NOTE]
> **Ported to C:** [`copy_memory_bank`](../platform_sdl.c#L90) in `platform_sdl.c` (ASM: `0460-049D`)

```asm
                       .ORG $0460
;*****************************************************************************
;* Copy memory bank to bank.
;* B = from-bank number, C = to-bank number.  Copies three regions:
;*   1) the foreground playfield (from $4320)
;*      This loop walks the screen in the display's native (rotated) order:
;*      It copies a 4 byte group (`E & 3` inner loop), then snaps `E` to
;*      its `$x0` boundary and subtracts `$20` to jump to the group one screen line earlier,
;*      when that underflows it decrements the page (`DEC D`).
;*      It marches through pages `$43 -> $42 -> $41 -> $40` and stops when `D` reaches `$3F`
;*      (i.e. below `$4000`). Net effect: the visible playfield is transferred between banks.
;*   2) the game-state/score block  $4380-$43B7
;*      A straight linear copy (`INC E` until `$B8`). This carries the two players' scores
;*      (`$4380`–`$4387`) plus the level/round and assorted counters in that block.
;*   3) the object buffer          $4BC0-$4BFF
;*      Another linear copy that runs until `E` wraps from `$FF` to `$00`.
;*      This preserves the in progress object/bird buffer.
;* Role in the game:
;* `CopyMemoryBank` is what makes alternating two player play possible:
;* at each turn boundary the game flips the "current player" flag and calls this routine
;* to move the departing player's screen and state into their bank while bringing
;* the incoming player's bank live (the register ends on `C`). The three regions cover
;* exactly what must persist across turns — the visible screen, the score/level/counter block,
;* and the object buffer — so each player resumes precisely where they left off.
;*****************************************************************************
```

### CopyMemoryBank:

```asm
                       LD      HL,videoRegister    ; 50xx video register
                       LD      DE,ForegroundScreen+$320; 1st row 1st line
;----- Region 1: the visible foreground screen --------------------------------
```

### L0466:

```asm
                       LD      (HL),B              ;
                       LD      A,(DE)              ;
                       LD      (HL),C              ;
                       LD      (DE),A              ;
                       INC     E                   ;
                       LD      A,E                 ;
                       AND     $03                 ;
                       JP      NZ,L0466            ;
                       LD      A,E                 ;
                       AND     $F0                 ;
                       SUB     $20                 ;
                       LD      E,A                 ;
                       JP      NC,L0466            ;
                       DEC     D                   ;
                       LD      A,D                 ;
                       CP      $3F                 ;
                       JP      NZ,L0466            ;
                       LD      DE,M4380            ;
;----- Region 2: game-state + score block $4380-$43B7 -------------------------
```

### L0484:

```asm
                       LD      (HL),B              ;
                       LD      A,(DE)              ;
                       LD      (HL),C              ;
                       LD      (DE),A              ;
                       INC     E                   ;
                       LD      A,E                 ;
                       CP      $B8                 ;
                       JP      NZ,L0484            ;
                       LD      DE,M4BC0            ;
;----- Region 3: object buffer $4BC0-$4BFF ------------------------------------
```

### L0492:

```asm
                       LD      (HL),B              ;
                       LD      A,(DE)              ;
                       LD      (HL),C              ;
                       LD      (DE),A              ;
                       INC     E                   ;
                       LD      A,E                 ;
                       CP      $00                 ;
                       JP      NZ,L0492            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l04a0_change_player_at_attract_mode`](../game_state_machine.c#L98) in `game_state_machine.c` (ASM: `04A0-04AB`)

```asm
                       .ORG $04A0
;*****************************************************************************
;* Changing the player at attract mode.
;*****************************************************************************
```

### L04A0:

```asm
                       LD      L,$A3               ; set GameAndDemoOrSplash
                       LD      (HL),$01            ; to 'Game for player 2'
                       LD      BC,$0001            ; from bank 0 to bank 1
                       CALL    CopyMemoryBank      ; to toggle the player
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`state_1_flashing_score`](../game_state_machine.c#L132) in `game_state_machine.c` (ASM: `04AC-04E4, 04E6-04F9, 04FB-0505`)

```asm
                       .ORG $04AC
;*****************************************************************************
;* Game state 1.
;* Flashing of score1 or 2.
;*****************************************************************************
```

### L04AC:

```asm
                       LD      HL,CounterA5        ;
                       DEC     (HL)                ; decrement counter
                       LD      A,(HL)              ; save value
                       DEC     L                   ; HL=A3A4 next game state ..
                       LD      (HL),$02            ; .. is 2
                       AND     A                   ; ret if ..
                       RET     Z                   ; counter 0
                       LD      (HL),$01            ; set game state to 1
                       CP      $7F                 ; 0111_1111
                       JP      Z,L07F0             ;
                       LD      L,$9A               ;
                       LD      (HL),$00            ; reset Counter9A MSB
                       INC     L                   ; and ..
                       LD      (HL),$00            ; LSB
                       AND     $08                 ; 0000_1000
                       JP      NZ,L04E6            ;
                       CALL    L06E8               ;
                       NOP                         ;
                       LD      HL,GameAndDemoOrSplash
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       LD      L,$83               ; LSB of Score1low adress
                       LD      DE,$4261            ; screen ram addr. of lowest score digit player 1
                       JP      Z,L04DF             ; 
                       LD      L,$87               ; LSB of Score2low adress
                       LD      DE,$4021            ; screen ram addr. of lowest score digit player 2
```

### L04DF:

```asm
                       LD      B,$06               ; number of digits to print
                       CALL    PrintNumber         ;
                       RET                         ;

                       .ORG $04E6
```

### L04E6:

```asm
                       LD      HL,GameAndDemoOrSplash
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       LD      DE,$4261            ; screen ram addr. of lowest score digit player 1
                       JP      Z,L04F4             ;
                       LD      DE,$4021            ; screen ram addr. of lowest score digit player 2
```

### L04F4:

```asm
                       LD      B,$06               ; number of digits to delete
                       CALL    L04FB               ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`delete_digits`](../utilities.c#L361) in `utilities.c` (ASM: `04FB-0505`)

```asm
                       .ORG $04FB
```

### L04FB:

```asm
                       LD      A,$00               ; delete ..
                       LD      (DE),A              ; ..one digit
                       CALL    LeftOneColumn       ;
                       DEC     B                   ; decrement number of digits
                       JP      NZ,L04FB            ; ..until
                       RET                         ; ..done

;*****************************************************************************
;* Clear $4392 to $4397 and
;* init start value list pointer for alien movement MSB $4394
;*****************************************************************************
```

### L0506:

```asm
                       LD      HL,M4392            ;
                       LD      B,$06               ; number of bytes to clear
                       CALL    ClearBbytesAtHL     ;
                       LD      A,(M4B50)           ;
                       LD      (M4394),A           ;
                       RET                         ;

;*****************************************************************************
;* Game state 2.
;* Initialization of game and level data.
;*****************************************************************************
```

### L0515:

```asm
                       CALL    SetBitsVideoRegister; set color palette according to LevelAndRound
                       LD      HL,GameState        ; Next interval game state ...
                       LD      (HL),$03            ; ... is 3 (normal game play)
                       CALL    InitGlobalLevelData ;
                       CALL    InitPlayerDataStructure
                       CALL    L09A0               ; get screen ram adress for player ship position
```

### L0526:

```asm
                       CALL    L0532               ; init alien data for a new level and round
                       CALL    L0A6C               ; get screen ram adress for all aliens
                       CALL    L0506               ; clear 4392 to 4397, init 4394
                       JP      L32B0               ;

;*****************************************************************************
;* Init alien data for a new level and round
;*****************************************************************************
```

### L0532:

```asm
                       LD      HL,M4B50            ;
                       LD      B,$A0               ; clear $4B50 to $4BEF
                       CALL    ClearBbytesAtHL     ;
                       CALL    InitAlienControlStates
                       CALL    L0650               ; copy init values for 16 aliens to $4B50-$4B6F
                       CALL    InitAlienPositions  ; load alien screen coordinates (X,Y grid), for a new level and round
                       RET                         ;

                       .ORG $0547
;*****************************************************************************
;* Copy 32 byte from $0560 to $43C0 Player and bullets data structure (grid)
;* and clear 32 bytes of player and bullets data structure (screen ram).
;*****************************************************************************
```

### InitPlayerDataStructure:

```asm
                       LD      HL,T0560            ;
                       LD      DE,PlayerState      ; base of data structure (grid)
                       LD      B,$20               ;
                       CALL    CopyBbytesHLtoDE    ;
                       LD      HL,OldPlayerShipMSB ;
                       LD      B,$20               ;
                       CALL    ClearBbytesAtHL     ;
                       RET                         ;

                       .ORG $0560
; Data copied to $43C0-$43DF
; Default values for player and bullets data structure (grid).
```

### T0560:

```asm
                       .DB $0C, $10, $64, $D8       ; PlayerState, PlayerShape, PlayerShipX, PlayerShipY
                       .DB $00, $50, $00, $D0       ; PlayerBulletState, PlayerBulletShape, PlayerBulletX, PlayerBulletY
                       .DB $00, $50, $00, $D0       ; AbovePlayerBulletState, AbovePlayerBulletShape, AbovePlayerBulletX, AbovePlayerBulletY
                       .DB $00, $58, $00, $20       ; AlienBullet0State, AlienBullet0Shape, AlienBullet0X, AlienBullet0Y
                       .DB $00, $58, $00, $20       ; AlienBullet1State, AlienBullet1Shape, AlienBullet1X, AlienBullet1Y
                       .DB $00, $58, $00, $20       ; AlienBullet2State, AlienBullet2Shape, AlienBullet2X, AlienBullet2Y
                       .DB $00, $58, $00, $20       ; AlienBullet3State, AlienBullet3Shape, AlienBullet3X, AlienBullet3Y
                       .DB $00, $58, $00, $20       ; AlienBullet4State, AlienBullet4Shape, AlienBullet4X, AlienBullet4Y

;*****************************************************************************
;* Init of global level data, dependent on level and round.
;*****************************************************************************
```

### InitGlobalLevelData:

```asm
                       LD      HL,T0598            ;
                       LD      A,(LevelAndRound)   ;
                       AND     $0F                 ;
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      L,(HL)              ;
                       LD      H,$05               ;
                       LD      DE,M43AB            ;
                       LD      B,$0C               ; number of bytes to copy
                       CALL    CopyBbytesHLtoDE    ;
                       RET                         ;

                       .ORG $0598
; Table for the global level data, over game levels.
; Bit0 - bit3 of $43B8 is the table index.
; Data will be fetched two times. Once before and once after the 'spiral fill' animation.
```

### T0598:

```asm
                       .DB T05A8 & $FF, T05A8 & $FF    ;init values for 1st alien wave (pointer to $05A8, $05A8)
                       .DB T05C0 & $FF, T05C0 & $FF    ;init values for 2st alien wave (pointer to $05C0, $05C0)
                       .DB T05A8 & $FF, T05A8 & $FF    ;init values for blue birds wave (pointer to $05A8, $05A8)
                       .DB T05A8 & $FF, T05A8 & $FF    ;init values for pink birds wave (pointer to $05A8, $05A8)
                       .DB T05B4 & $FF, T05CC & $FF    ;init values for mothership wave (pointer to $05B4, $05CC)
                       .DB T05B4 & $FF, T05B4 & $FF    ;init values for mothership wave (pointer to $05B4, $05B4)
                       .DB T05A8 & $FF, T05A8 & $FF    ;not used? pointer to $05A8, $05A8
                       .DB T05A8 & $FF, T05A8 & $FF    ;not used? pointer to $05A8, $05A8
;
; e.g.:counter values, timer values, T1C00, T1D00, T1F00, ..
; Data copied to $43AB-$43B6
```

### T05A8:

```asm
                       .DB $80, $7F, $00, $00, $40, $3F, $00, T1C00 >> 8, T1C00 & $FF, $FF, $FF, $FF
```

### T05B4:

```asm
                       .DB $60, $5F, $01, $02, $30, $2F, $00, T1C00 >> 8, T1C00 & $FF, $C0, $FF, $FF
```

### T05C0:

```asm
                       .DB $80, $7F, $03, $04, $40, $3F, $00, T1F00 >> 8, T1F00 & $FF, $A0, $FF, $FF
```

### T05CC:

```asm
                       .DB $60, $60, $05, $06, $50, $30, $00, T1D00 >> 8, T1D00 & $FF, $48, $FF, $FF

;*****************************************************************************
;* Clears B memories starting at HL.
;*****************************************************************************
```

### ClearBbytesAtHL:

```asm
                       XOR     A                   ; A=0
```

### L05D9:

```asm
                       LD      (HL),A              ; store
                       INC     HL                  ; next
                       DEC     B                   ; decrease counter.
                       JP      NZ,L05D9            ;
                       RET                         ;

;*****************************************************************************
;* Copy number of bytes (B register) from DE to HL.
;*****************************************************************************
```

### CopyBbytesHLtoDE:

```asm
                       LD      A,(HL)              ; Copy to HL ...
                       LD      (DE),A              ; ... from DE
                       INC     HL                  ; Next destination
                       INC     DE                  ; Next source
                       DEC     B                   ; All done?
                       JP      NZ,CopyBbytesHLtoDE ; no ... keep going
                       RET                         ; Out

```
> [!NOTE]
> **Ported to C:** [`init_alien_control_states`](../alien_logic.c#L19) in `alien_logic.c` (ASM: `05EC-05F9`)

```asm
                       .ORG $05EC
;*****************************************************************************
;* Init all alien control states for a given level and round.
;*****************************************************************************
```

### InitAlienControlStates:

```asm
                       LD      HL,T1500            ;
                       LD      A,(LevelAndRound)   ;
                       AND     $0F                 ;
                       RLCA                        ; Multiply by 2
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      D,(HL)              ;
                       INC     HL                  ;
                       LD      E,(HL)              ;
;
```

### L05FA:

```asm
                       LD      HL,M4B70            ;
                       LD      A,(AliensLeft)      ;
                       LD      B,A                 ;
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if no AliensLeft
;
```

### L0603:

```asm
                       LD      (HL),D              ; set control state A
                       INC     L                   ;
                       LD      (HL),E              ; set control state B
                       INC     L                   ;
                       INC     L                   ;
                       INC     L                   ;
                       DEC     B                   ; number of aliens left
                       JP      NZ,L0603            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`init_alien_positions`](../alien_logic.c#L224) in `alien_logic.c` (ASM: `0610-0638`)

```asm
                       .ORG $0610
;*****************************************************************************
;* Load alien screen coordinates for a given level and round to $4B70 - $4BAF.
;*****************************************************************************
```

### InitAlienPositions:

```asm
                       LD      HL,T063A            ;
                       LD      A,(LevelAndRound)   ;
                       RRCA                        ;
                       AND     $0F                 ; mask out 0000_1111
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       NOP                         ; Old command removed or space for a future replace patch
                       NOP                         ; ..
                       NOP                         ; ..
                       LD      L,(HL)              ;
                       LD      H,T1540 >> 8        ; MSB for T1540-T15E0
                       LD      DE,M4B72            ;
                       LD      A,(AliensLeft)      ;
                       LD      B,A                 ;
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if no AliensLeft
;
```

### L062A:

```asm
                       LD      A,(HL)              ; get value from table
                       LD      (DE),A              ; save to alien screen coordinate
                       INC     HL                  ;
                       INC     DE                  ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ;
                       INC     HL                  ;
                       INC     DE                  ;
                       INC     DE                  ;
                       INC     DE                  ;
                       DEC     B                   ;
                       JP      NZ,L062A            ; loop for all AliensLeft
                       RET                         ;

                       .ORG $063A
; Init data for 1st game round.
; LSB's for T1560, T1540, T15E0.
```

### T063A:

```asm
                       .DB T1560 & $FF, T1540 & $FF, T15E0 & $FF, T15E0 & $FF, T15E0 & $FF, T15E0 & $FF, $FF, $FF
; Init data for 2nd game round.
; LSB's for T15C0, T15A0, T1580.
                       .DB T15C0 & $FF, T15A0 & $FF, T1580 & $FF, T1580 & $FF, T1580 & $FF, T1580 & $FF, $FF, $FF

```
> [!NOTE]
> **Ported to C:** [`copy_init_values_for_16_aliens`](../alien_logic.c#L249) in `alien_logic.c` (ASM: `0650-0679`)

```asm
                       .ORG $0650
;*****************************************************************************
;* Copy init values for 16 aliens to $4B50-$4B6F (Pointer to alien movement pattern)
;*****************************************************************************
```

### L0650:

```asm
                       LD      HL,T1520            ;
                       LD      A,(LevelAndRound)   ;
                       AND     $0F                 ; mask out 0000_1111
                       RLCA                        ; Multiply by 2
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      D,(HL)              ;
                       INC     HL                  ;
                       LD      E,(HL)              ;
                       LD      HL,M4B50            ;
                       LD      A,(AliensLeft)      ;
                       LD      B,A                 ;
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if no AliensLeft
```

### L0667:

```asm
                       LD      (HL),D              ;
                       INC     L                   ;
                       LD      (HL),E              ;
                       INC     L                   ;
                       DEC     B                   ;
                       JP      NZ,L0667            ; loop for all AliensLeft
                       RET                         ;

                       .ORG $067A
;*****************************************************************************
;* Scroll down the background screen one pixel.
;*****************************************************************************
```

### StarsScrollDown:

```asm
                       LD      HL,CounterB9        ;
                       LD      A,(HL)              ;
                       DEC     (HL)                ; decrement the backwards counter
                       LD      (scrollRegister),A  ; 58xx scroll register
                       AND     $07                 ; mask out 0000_0111
                       RET     NZ                  ; continue after 8 pixels...
; Fill the background with stars or mothership.
                       LD      BC,$2047            ;
                       LD      DE,$4B21            ; get character from the background screen (1st row, 2nd line)
                       LD      A,(HL)              ; get $43B9 free running 8 bit backwards counter value
                       RRCA                        ;
                       RRCA                        ;
                       RRCA                        ;
                       AND     $1F                 ; mask out 0001_1111
                       ADD     A,E                 ;
                       LD      E,A                 ;
                       LD      L,$B2               ;
                       LD      A,(HL)              ; get $43B2 (MSB of T1C00 or T1D00 or T1F00)
                       INC     L                   ;
                       LD      L,(HL)              ; get $43B3 (LSB of T1C00 or T1D00 or T1F00)
                       LD      H,A                 ;
```

### L0699:

```asm
                       LD      A,(HL)              ;
                       LD      (DE),A              ; to background screen
                       INC     L                   ;
                       LD      A,E                 ;
                       SUB     B                   ;
                       LD      E,A                 ;
                       JP      NC,L0699            ;
                       DEC     D                   ;
                       LD      A,D                 ;
                       CP      C                   ;
                       JP      NZ,L0699            ;
                       LD      A,L                 ;
                       LD      (M43B3),A           ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`add_planets_to_background`](../hw_video_audio.c#L356) in `hw_video_audio.c` (ASM: `06B0-06E7`)

```asm
                       .ORG $06B0
;*****************************************************************************
;* Fill the background with (2x2) planets.
;* Reads the MSB from `T1E20`, then reaches `T1E40` simply by adding `$20`
;* to the same pointer (`$1E20 + $20 = $1E40`) — which is the clearest proof that `T1E40` is the LSB companion of `T1E20`.
;* So `DE = (T1E20[i] << 8) | T1E40[i]`, then the LSB gets a scroll dependent offset added (derived from `CounterB9 >> 3`)
;* so the planet drifts down as the star background scrolls. `DE` ends up somewhere in `$4800`–`$4BFF` (the background screen).
;* The graphic itself is then chosen via `T1E60 -> T1E00` and drawn by `L07DC`.
;* The routine only fires when `CounterB9` matches the planet counter (`$43AB`),
;* so as the background scrolls a new planet is dropped in at successive slots,
;* the slot index (masked to `$1F`) cycles through all 32 `T1E20`/`T1E40` positions.
;*****************************************************************************
```

### AddPlanetsToBackground:

```asm
                       LD      HL,M43AB            ; counter value for (2x2) planets
                       LD      A,(CounterB9)       ;
                       LD      C,A                 ;
                       CP      (HL)                ;
                       RET     NZ                  ;
                       LD      A,(HL)              ;
                       INC     L                   ;
                       ADD     A,(HL)              ;
                       DEC     L                   ;
                       LD      (HL),A              ;
                       INC     L                   ;
                       INC     L                   ;
                       INC     (HL)                ;
                       LD      B,(HL)              ;
                       INC     L                   ;
                       INC     (HL)                ;
                       LD      A,(HL)              ;
                       LD      HL,T1E20            ; MSB's of screen ram for planets
                       AND     $1F                 ;
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      D,(HL)              ;
                       ADD     $20                 ;
                       LD      L,A                 ;
                       LD      E,(HL)              ;
                       LD      A,C                 ;
                       RRCA                        ;
                       RRCA                        ;
                       RRCA                        ;
                       AND     $1E                 ;
                       ADD     A,E                 ;
                       ADD     $02                 ;
                       LD      E,A                 ;
                       LD      HL,T1E60            ; LSB's of screen ram for planets
                       LD      A,B                 ;
                       AND     $1F                 ;
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      L,(HL)              ;
                       CALL    L07DC               ; draw the characters at background
                       RET                         ;

;*****************************************************************************
;* Print score column
;*****************************************************************************
```

### L06E8:

```asm
                       LD      HL,T1800            ; base addr. table for 'screen ram adresses and static texts'
                       LD      C,$01               ; 1 column (rotated to 1 row)
                       JP      PrintTextLines      ;

;*****************************************************************************
;* Update scroll register and fill background
;*****************************************************************************
```

### L06F0:

```asm
                       CALL    StarsScrollDown     ;
                       CALL    AddGalaxiesToBackground
                       JP      AddPlanetsToBackground

```
> [!NOTE]
> **Ported to C:** [`player_data_controller`](../player_logic.c#L250) in `player_logic.c` (ASM: `0700-0717`)

```asm
                       .ORG $0700
;*****************************************************************************
;* Controller for player data structure.
;* Handles: PlayerState, OldPlayerShipMSB, PlayerBulletState, PlayerBulletMSB, AbovePlayerBulletState, $43E8
;*****************************************************************************
```

### PlayerDataController:

```asm
                       LD      BC,PlayerState      ; Player data structure (grid)
                       LD      DE,OldPlayerShipMSB ; Player data structure (screen ram)
```

### L0706:

```asm
                       CALL    UpdateScreenObjects ;
                       LD      A,C                 ;
                       ADD     $04                 ;
                       LD      C,A                 ;
                       ADD     $20                 ;
                       LD      E,A                 ;
                       LD      D,B                 ;
                       CP      $EC                 ;
                       JP      NZ,L0706            ; loop until $43EC
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`update_screen_objects`](../sprite_rendering.c#L215) in `sprite_rendering.c` (ASM: `0718-071F`)

```asm
                       .ORG $0718
;*****************************************************************************
;* Draw or delete screen objects dep. on control state of player, alien and bullet.
;*****************************************************************************
```

### UpdateScreenObjects:

```asm
                       CALL    Bit4Controller      ; for deleting screen objects
                       JP      Bit3Controller      ; for drawing screen objects

```
> [!NOTE]
> **Ported to C:** [`bit4_controller`](../sprite_rendering.c#L150) in `sprite_rendering.c` (ASM: `0720-073F`)

```asm
                       .ORG $0720
;*****************************************************************************
;* Handles the bit4 actions for deleting screen objects.
;*****************************************************************************
```

### Bit4Controller:

```asm
                       LD      A,(BC)              ; get value from data structure (grid)
                       LD      H,A                 ; save the bits
                       AND     $10                 ; mask out 0001_0000 (bit4 of control state A)
                       RET     Z                   ; ret if bit not set.
                       LD      A,H                 ; restore the bits
                       AND     $EF                 ; mask out 1110_1111
                       LD      (BC),A              ; save to control state A
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       AND     $07                 ; mask out 0000_0111
                       ADD     $38                 ; add to base for jump table
                       LD      L,A                 ;
                       LD      H,T0735 >> 8        ; MSB for jump table
                       LD      L,(HL)              ;
                       JP      (HL)                ; jump to control function

; LSB jump table:
;.....not used
;........not used
;...........not used
;..............0763..................control state A: 0001_xxxx...Delete 1x1 screen objects.
;.................0779...............control state A: 0011_xxxx...Delete 2x1 screen objects.
;....................not used
;.......................079E.........control state A: 0111_xxxx...Delete 1x2 screen objects.
;..........................07BE......control state A: 1001_xxxx...Delete 2x2 screen objects.
```

### T0735:

```asm
                       .DB $00, $00, $00, L0763 & $FF, L0779 & $FF, $00, L079E & $FF, L07BE & $FF

```
> [!NOTE]
> **Ported to C:** [`bit3_controller`](../sprite_rendering.c#L179) in `sprite_rendering.c` (ASM: `0740-07EE`)

```asm
                       .ORG $0740
;*****************************************************************************
;* Handles the bit3 actions for drawing screen objects.
;*****************************************************************************
```

### Bit3Controller:

```asm
                       LD      A,(BC)              ; get value from data structure (grid)
                       LD      H,A                 ; save it
                       AND     $08                 ; mask out 0000_1000 (bit3 of control state A)
                       RET     Z                   ; ret if bit not set.
                       LD      A,H                 ; restore the bits
                       AND     $07                 ; mask out 0000_0111
                       LD      H,A                 ; save it
                       RRCA                        ; Divide by 8 ..
                       RRCA                        ; ..
                       RRCA                        ; ..
                       OR      H                   ; add original bits
                       OR      $18                 ; set 0001_1000 flag
                       LD      (BC),A              ; set the bits at control state A
                       INC     BC                  ; go to control state B
                       LD      A,H                 ;
                       ADD     $5B                 ; add to base for jump table
                       LD      L,A                 ;
                       LD      H,T0759 >> 8        ; MSB for jump table
                       LD      L,(HL)              ;
                       JP      (HL)                ; jump to control function

; LSB jump table:
;.....not used
;........not used
;...........076D.....................control state A: xxxx_1000...Draw 1x1 screen objects.
;..............0788..................control state A: xxxx_1001...Draw 2x1 screen objects.
;.................not used
;....................07AA............control state A: xxxx_1011...Draw 1x2 screen objects.
;.......................07D2.........control state A: xxxx_1100...Draw 2x2 screen objects.
;..........................not used
```

### T0759:

```asm
                       .DB $00, $00, L076D & $FF, L0788 & $FF, $00, L07AA & $FF, L07D2 & $FF

                       .ORG $0763
;*****************************************************************************
;* Bit4 control function 63:
;* If control state A: 0001_xxxx
;* Delete 1x1 screen objects (bullet, alien).
;*****************************************************************************
```

### L0763:

```asm
                       EX      DE,HL               ;
                       LD      D,(HL)              ; get screen ram adress MSB
                       INC     HL                  ;
                       LD      E,(HL)              ; get screen ram adress LSB
                       DEC     HL                  ; restore pointer
                       XOR     A                   ; A=0
                       LD      (DE),A              ; delete at screen
                       EX      DE,HL               ;
                       RET                         ;

                       .ORG $076D
;*****************************************************************************
;* Bit3 control function 6D:
;* If control state A: xxxx_1000
;* Set alien control state B value to screen ram.
;* Draw 1x1 screen objects (used at 'fade in' animation).
;*****************************************************************************
```

### L076D:

```asm
                       EX      DE,HL               ;
                       INC     HL                  ;
                       INC     HL                  ;
                       LD      D,(HL)              ; get MSB screen ram adress of alien
                       INC     HL                  ;
                       LD      E,(HL)              ; get LSB screen ram adress of alien
                       LD      A,(BC)              ; get alien control state B
                       LD      (DE),A              ; set at screen ram
                       DEC     BC                  ; move to alien control state A
                       RET                         ;

                       .ORG $0779
;*****************************************************************************
;* Bit4 control function 79:
;* If control state A: 0011_xxxx
;* Delete 2x1 screen objects (alien).
;*****************************************************************************
```

### L0779:

```asm
                       EX      DE,HL               ;
                       LD      D,(HL)              ;
                       INC     HL                  ;
                       LD      E,(HL)              ;
                       DEC     HL                  ; restore pointer
                       XOR     A                   ; A=0
                       LD      (DE),A              ; delete at screen, left part
                       CALL    RightOneColumn      ; 
                       XOR     A                   ; A=0
                       LD      (DE),A              ; delete at screen, right part
                       EX      DE,HL               ;
                       RET                         ;

                       .ORG $0788
;*****************************************************************************
;* Bit3 control function 88:
;* If control state A: xxxx_1001
;* Map alien control state B to shape and draw it.
;* Draw 2x1 screen objects (alien).
;*****************************************************************************
```

### L0788:

```asm
                       EX      DE,HL               ;
                       INC     HL                  ;
                       INC     HL                  ;
                       LD      D,(HL)              ;
                       INC     HL                  ;
                       LD      E,(HL)              ;
                       LD      A,(BC)              ; get alien control state B
                       LD      L,A                 ; as offset for...
                       LD      H,T1420 >> 8        ; get alien character block shapes table
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw alien character left part
                       INC     HL                  ; next character
                       CALL    RightOneColumn      ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw alien character right part
                       DEC     BC                  ;
                       RET                         ;

                       .ORG $079E
;*****************************************************************************
;* Bit4 control function 9E:
;* If control state A: 0111_xxxx
;* Delete 1x2 screen objects (alien).
;*****************************************************************************
```

### L079E:

```asm
                       EX      DE,HL               ;
                       LD      D,(HL)              ; get MSB of screen ram
                       INC     HL                  ;
                       LD      E,(HL)              ; get LSB of screen ram
                       DEC     HL                  ; restore pointer
                       XOR     A                   ; A=0
                       LD      (DE),A              ; delete at screen, upper part
                       INC     DE                  ;
                       LD      (DE),A              ; delete at screen, lower part
                       EX      DE,HL               ;
                       RET                         ;

                       .ORG $07AA
;*****************************************************************************
;* Bit3 control function AA:
;* If control state A: xxxx_1011
;* Draw 1x2 screen objects (alien).
;*****************************************************************************
```

### L07AA:

```asm
                       EX      DE,HL               ;
                       INC     HL                  ;
                       INC     HL                  ;
                       LD      D,(HL)              ;
                       INC     HL                  ;
                       LD      E,(HL)              ;
                       LD      A,(BC)              ;
                       LD      L,A                 ;
                       LD      H,T1420 >> 8        ; get alien character block shapes table
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw upper part on screen
                       INC     HL                  ;
                       INC     DE                  ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw lower part on screen
                       DEC     BC                  ;
                       RET                         ;

                       .ORG $07BE
;*****************************************************************************
;* Bit4 control function BE:
;* If control state A: 1001_xxxx
;* Delete 2x2 screen objects (player ship, alien).
;*****************************************************************************
```

### L07BE:

```asm
                       EX      DE,HL               ;
                       LD      D,(HL)              ;
                       INC     HL                  ;
                       LD      E,(HL)              ;
                       DEC     HL                  ;
                       XOR     A                   ; A=0
                       LD      (DE),A              ; delete upper left part
                       INC     DE                  ;
                       LD      (DE),A              ; delete upper right part
                       CALL    RightOneColumn      ;
                       XOR     A                   ; A=0
                       LD      (DE),A              ; delete lower left part
                       DEC     DE                  ;
                       LD      (DE),A              ; delete lower right part
                       EX      DE,HL               ;
                       RET                         ;

                       .ORG $07D2
;*****************************************************************************
;* Bit3 control function D2:
;* If control state A: xxxx_1100
;* Draw 2x2 screen objects (player ship, alien, planets).
;*****************************************************************************
```

### L07D2:

```asm
                       EX      DE,HL               ;
                       INC     HL                  ;
                       INC     HL                  ;
                       LD      D,(HL)              ; get MSB from player data structure (screen ram)
                       INC     HL                  ;
                       LD      E,(HL)              ; get LSB from player data structure (screen ram)
                       LD      A,(BC)              ; get value from player data structure (grid)
                       LD      L,A                 ;
                       LD      H,T1400 >> 8        ; get player ship character block shapes table
```

### L07DC:

```asm
                       LD      A,(HL)              ; Entry point for general draw
                       LD      (DE),A              ; draw upper left part
                       INC     HL                  ;
                       INC     DE                  ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw upper right part
                       INC     HL                  ;
                       DEC     DE                  ;
                       CALL    RightOneColumn      ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw lower left part
                       INC     HL                  ;
                       INC     DE                  ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ; draw lower right part
                       DEC     BC                  ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l07f0`](../game_state_machine.c#L118) in `game_state_machine.c` (ASM: `07F0-07FA`)

```asm
                       .ORG $07F0
;*****************************************************************************
;* Reset scroll register for background at score flash
;*****************************************************************************
```

### L07F0:

```asm
                       LD      A,(CounterB9)       ;
                       LD      (scrollRegister),A  ; 58xx scroll register
                       CALL    ClearForeground     ;
                       JP      SetBitsVideoRegister

;*****************************************************************************
; ic46
;*****************************************************************************
```
> [!NOTE]
> **Ported to C:** [`state_3_normal_game_play`](../state_play.c#L237) in `state_play.c` (ASM: `0800-0833`)

```asm
                       .ORG $0800
;*****************************************************************************
;* Game state 3.
;* Normal game play.
;*****************************************************************************
```

### L0800:

```asm
                       LD      HL,T0814            ;
                       LD      A,(LevelAndRound)   ; bit0 - 3: game level, bit4 - 7: game round
                       RLCA                        ; Multiply by 2 to get a 2 byte offset
                       AND     $1E                 ; mask out 0001_1110 game level
                       ADD     A,L                 ; add offset ...
                       LD      L,A                 ; ... to base of table
                       LD      A,(HL)              ; MSB of destination
                       INC     L                   ; Get the
                       LD      L,(HL)              ; ... LSB of destination
                       LD      H,A                 ; Now point to function
                       JP      (HL)                ; jump to corresponding function according to LevelAndRound.

                       .ORG $0814
```

### T0814:

```asm
                       .MSFIRST
                       .DW L0834       ;Game level 0: called for each frame during stars scrolling down and 'aliens fade in'
                       .DW L2000       ;Game level 1: called for each frame during 'player alife' with aliens, after 'fade in'
                       .DW L0834       ;Game level 2: called for each frame during stars scrolling down and 'aliens fade in'
                       .DW L2000       ;Game level 3: called for each frame during 'player alife' with aliens, after 'fade in'
                       .DW L2230       ;Game level 4: called for each frame during 'spiral fill'
                       .DW L3400       ;Game level 5: called for each frame during birds level including 'fade in'
                       .DW L2230       ;Game level 6: called for each frame during 'spiral fill'
                       .DW L3400       ;Game level 7: called for each frame during birds level including 'fade in'
                       .DW L2230       ;Game level 8: called for each frame during 'spiral fill'
                       .DW L22B4       ;Game level 9: called for each frame during mothership 'fade in'
                       .DW L22CA       ;Game level A: called for each frame during mothership and aliens 'fade in'
                       .DW L2000       ;Game level B: called for each frame during 'player alife' with aliens and mothership, after 'fade in'

```
> [!NOTE]
> **Ported to C:** [`level_0_and_2_aliens_fade_in`](../state_play.c#L205) in `state_play.c` (ASM: `0834-0859`)

```asm
                       .ORG $0834
;*****************************************************************************
;* Game level 0 and 2:
;* Stars scrolling down and 'aliens fade in'
;*****************************************************************************
```

### L0834:

```asm
                       CALL    L06F0               ; update scroll register and fill background
                       LD      HL,CounterB4        ; 
                       DEC     (HL)                ; decrement the counter
                       LD      A,(HL)              ;
                       CP      $15                 ;
                       RET     NC                  ;
                       CALL    GetAnimationChrs    ; for 'aliens fade in'
                       CALL    L05FA               ; init all alien control states
                       CALL    AlienDataController ;
```

### L0848:

```asm
                       LD      HL,CounterB4        ;
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       RET     NZ                  ; if CounterB4 is 0.
                       LD      L,$B8               ;
                       INC     (HL)                ; increment game level $43B8
                       LD      L,$A4               ; Next interval game state ...
                       LD      (HL),$02            ; .. is 2
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`get_animation_chrs_aliens_fade_in`](../alien_logic.c#L31) in `alien_logic.c` (ASM: `085A-0871`)

```asm
                       .ORG $085A
;*****************************************************************************
;* The 'aliens fade in' animation sequence is:
;* 6C, 6D, 6E, 6F, 68, from foreground tiles.
;*****************************************************************************
```

### GetAnimationChrs:

```asm
                       LD      DE,$086C            ;
                       CP      $11                 ;
                       RET     NC                  ;
                       LD      E,$6D               ;
                       CP      $0D                 ;
                       RET     NC                  ;
                       LD      E,$6E               ;
                       CP      $09                 ;
                       RET     NC                  ;
                       LD      E,$6F               ;
                       CP      $05                 ;
                       RET     NC                  ;
                       LD      E,$68               ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`player_update`](../player_logic.c#L35) in `player_logic.c` (ASM: `0876-0885`)

```asm
                       .ORG $0876
;*****************************************************************************
; Updates the player ship, player bullet and the shield.
;*****************************************************************************
```

### PlayerUpdate:

```asm
                       CALL    PlayerDataController     ; draw new / delete old objects
                       CALL    L0886               ; copy current player data to old player data ?
                       CALL    L08A0               ; update player position, bullet and shield
                       CALL    L09A0               ; get screen ram adress for player ship position
                       CALL    L097A               ; map player ship position to $439E $439F
                       RET                         ;

;*****************************************************************************
; Copy current player data to old player data.
;*****************************************************************************
```

### L0886:

```asm
                       LD      HL,M43EB            ;
                       LD      B,$03               ;
```

### L088B:

```asm
                       LD      D,(HL)              ;
                       DEC     HL                  ;
                       LD      E,(HL)              ;
                       DEC     HL                  ;
                       LD      (HL),D              ;
                       DEC     HL                  ;
                       LD      (HL),E              ;
                       DEC     HL                  ;
                       DEC     B                   ;
                       JP      NZ,L088B            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`update_player_position_bullet_shield`](../player_logic.c#L94) in `player_logic.c` (ASM: `08A0-08B7`)

```asm
                       .ORG $08A0
;*****************************************************************************
;* Update player position, bullet and shield
;*****************************************************************************
```

### L08A0:

```asm
                       CALL    MovePlayer          ;
                       LD      HL,PlayerBulletState
                       CALL    L0930               ; get the assigned player bullet tile if fire button was pressed
                       LD      A,(LevelAndRound)   ;
                       AND     $0F                 ; 0000_1111
                       CP      $03                 ;
                       RET     NZ                  ; return if not game level 3 (2nd alien wave)
                       LD      HL,AbovePlayerBulletState
                       CALL    L0930               ; get the assigned player bullet tile if fire button was pressed
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`move_player`](../player_logic.c#L114) in `player_logic.c` (ASM: `08C4-08F3`)

```asm
                       .ORG $08C4
;*****************************************************************************
;* Player ship, shield and bullets handler.
;*****************************************************************************
```

### MovePlayer:

```asm
                       LD      HL,PlayerState      ;
                       LD      A,(HL)              ;
                       AND     $08                 ; mask out 0000_1000
                       JP      Z,DrawShields       ; Draw shields
                       LD      L,$A6               ;
                       LD      A,(HL)              ; get ShieldCount
                       AND     A                   ; updates the zero flag
                       JP      NZ,L08EA            ; if ShieldCount not 0.
                       LD      B,$80               ; 1000_0000 (bit7='shield')
                       CALL    CheckInputBits      ;
                       JP      Z,L08EB             ;
                       LD      L,$62               ;
                       LD      (HL),$40            ; set bit6 at $4362
                       LD      L,$C0               ;
                       LD      A,(HL)              ; get $43C0 PlayerState
                       AND     $F7                 ; mask out 1111_0111
                       LD      (HL),A              ;
                       LD      L,$A6               ;
                       LD      (HL),$FF            ;
```

### L08EA:

```asm
                       DEC     (HL)                ; decrement ShieldCount
```

### L08EB:

```asm
                       LD      L,PlayerShipX & $FF ; LSB of $43C2 PlayerShipX
                       CALL    L0900               ; Update the player ship x coordinate.
                       LD      BC,T1600            ;
                       JP      L0926               ; get player ship animation frame values, mapped with T1600/T1620

```
> [!NOTE]
> **Ported to C:** [`update_player_ship_x`](../player_logic.c#L66) in `player_logic.c` (ASM: `0900-0921, 0926-092E`)

```asm
                       .ORG $0900
;*****************************************************************************
;* Update the player ship x coordinate.
;*****************************************************************************
```

### L0900:

```asm
                       LD      A,(IN0Current)      ;
                       CPL                         ; flip the current bits
                       AND     $60                 ; mask out 0110_0000
                       RET     Z                   ; if no button pressed
                       AND     $40                 ; mask out 0100_0000
                       JP      Z,L0917             ;
                       LD      A,(HL)              ; get $43C2 PlayerShipX
                       CP      $0D                 ;
                       RET     C                   ; if left boundary reached
                       DEC     (HL)                ; 'left' button: dec $43C2 PlayerShipX
                       LD      A,$FF               ;
                       LD      (PlayerMoved),A     ; set 'player moved' flag
                       RET                         ;
```

### L0917:

```asm
                       LD      A,(HL)              ; get $43C2 PlayerShipX
                       CP      $C0                 ;
                       RET     NC                  ; if right boundary reached
                       INC     (HL)                ; 'right' button: inc $43C2 PlayerShipX
                       LD      A,$FF               ;
                       LD      (PlayerMoved),A     ; set 'player moved' flag
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`get_player_ship_animation_frame_values`](../player_logic.c#L189) in `player_logic.c` (ASM: `0926-092E`)

```asm
                       .ORG $0926
;*****************************************************************************
;* Get player ship animation frame values, mapped with T1600/T1620.
;*****************************************************************************
```

### L0926:

```asm
                       LD      A,(HL)              ;
                       AND     $07                 ; mask out 0000_0111
                       ADD     A,C                 ;
                       LD      C,A                 ;
                       LD      A,(BC)              ; get data from table
                       DEC     L                   ;
                       LD      (HL),A              ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`get_assigned_player_bullet_tile`](../player_logic.c#L168) in `player_logic.c` (ASM: `0930-093C`)

```asm
                       .ORG $0930
;*****************************************************************************
;* Get the assigned player bullet tile if fire button was pressed.
;*****************************************************************************
```

### L0930:

```asm
                       LD      A,(HL)              ;
                       AND     $08                 ; mask out 0000_1000
                       JP      NZ,L0964            ; update PlayerBulletY (grid) and PlayerBulletState
                       EX      DE,HL               ;
                       LD      B,$10               ; 0001_0000 (bit4='fire')
                       CALL    CheckInputBits      ;
                       RET     Z                   ; return if button not pressed
                       LD      A,(HL)              ;
                       AND     $EF                 ; mask out 1110_1111
                       LD      (HL),A              ;
                       LD      A,(DE)              ;
                       OR      $08                 ; set bit3 at..
                       LD      (DE),A              ; $43C4 PlayerBulletState
                       INC     DE                  ;
                       INC     DE                  ;
                       LD      A,(PlayerShipX)     ;
                       ADD     $04                 ; mask out 0000_0100
                       LD      (DE),A              ;
                       INC     DE                  ;
                       LD      A,(PlayerShipY)     ; $D8
                       SUB     $08                 ;
                       LD      (DE),A              ;
                       DEC     DE                  ;
                       EX      DE,HL               ;
                       LD      BC,T1620            ; get character for player bullets
                       CALL    L0926               ; get player ship animation frame values, mapped with T1600/T1620
                       LD      A,$30               ; 0011_0000
                       LD      (BulletTriggered),A ; set 'bullet triggered' flag
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`update_player_bullet_y`](../player_logic.c#L236) in `player_logic.c` (ASM: `0964-0975`)

```asm
                       .ORG $0964
;*****************************************************************************
;* Update PlayerBulletY (grid) and PlayerBulletState.
;*****************************************************************************
```

### L0964:

```asm
                       INC     L                   ;
                       INC     L                   ;
                       INC     L                   ;
                       LD      A,(HL)              ; get $43C7 PlayerBulletY (grid)
                       SUB     $08                 ; move bullet ($08 represents the bullet speed)
                       LD      (HL),A              ;
                       CP      $1F                 ; top of the screen reached?
                       RET     NC                  ; if not reached
```

### L096E:

```asm
                       DEC     L                   ;
                       DEC     L                   ;
                       DEC     L                   ;
                       LD      A,(HL)              ; get $43C4 PlayerBulletState
                       AND     $F7                 ; 1111_0111
                       LD      (HL),A              ; del bit3 at PlayerBulletState
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`map_player_ship_position`](../player_logic.c#L153) in `player_logic.c` (ASM: `097A-0995`)

```asm
                       .ORG $097A
;*****************************************************************************
;* Player ship X position mapping.
;*****************************************************************************
```

### L097A:

```asm
                       LD      A,(PlayerShipX)     ;
                       LD      B,A                 ; save it
                       AND     $07                 ; mask out 0000_0111
                       RLCA                        ;
                       LD      HL,T0B38            ; mapping table
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      A,B                 ; restore it
                       SUB     (HL)                ;
                       LD      (M439E),A           ; Mapped player ship position, left part
                       INC     HL                  ;
                       LD      A,B                 ;
                       ADD     A,(HL)              ;
                       LD      (M439F),A           ; Mapped player ship position, right part
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`get_screen_ram_address_for_player_ship`](../utilities.c#L187) in `utilities.c` (ASM: `09A0-09B5`)

```asm
                       .ORG $09A0
;*****************************************************************************
;* Get screen ram adress for player and bullet positions.
;* from: 43C2:43C3, 43C6:43C7, 43CA:43CB
;* ......PlayerShipX
;* ...........PlayerShipY
;* .................PlayerBulletX
;* ......................PlayerBulletY
;* ............................AbovePlayerBulletX
;* .................................AbovePlayerBulletY
;* to:   43E2:43E3, 43E6:43E7, 43EA:43EB
;*****************************************************************************
```

### L09A0:

```asm
                       LD      BC,PlayerShipX      ;
                       LD      DE,PlayerShipMSB    ;
```

### L09A6:

```asm
                       CALL    GetScreenRamAddress ;
                       INC     BC                  ;
                       INC     BC                  ;
                       INC     BC                  ;
                       INC     DE                  ;
                       INC     DE                  ;
                       INC     DE                  ;
                       LD      A,C                 ;
                       CP      $CE                 ; end of data structure
                       JP      NZ,L09A6            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`get_screen_ram_address`](../utilities.c#L163) in `utilities.c` (ASM: `09BA-09D1`)

```asm
                       .ORG $09BA
;*****************************************************************************
;* Mapping of 'grid values' to screen ram address.
;*****************************************************************************
```

### GetScreenRamAddress:

```asm
                       LD      HL,T0A00            ; Screen ram addresses for the top row (left to right)
                       LD      A,(BC)              ; get the coordinate
                       AND     $F8                 ; 1111_1000
                       RRCA                        ; 0111_1100
                       RRCA                        ; 0011_1110
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      A,(HL)              ; get MSB of screen ram address for row
                       LD      (DE),A              ; save it
                       INC     BC                  ;
                       INC     DE                  ;
                       INC     HL                  ; move to LSB for T0A00
                       LD      A,(BC)              ; get the coordinate
                       AND     $F8                 ; 1111_1000
                       RRCA                        ; 0111_1100
                       RRCA                        ; 0011_1110
                       RRCA                        ; 0001_1111
                       ADD     A,(HL)              ; add to LSB of screen ram address for row
                       LD      (DE),A              ; save it
                       RET                         ;

                       .ORG $0A00
; Screen ram addresses for the top row (left to right)
; Notice these addresses are MSB:LSB (backwards from the processors endianness)
; The offset is `(X & $F8) >> 2`, which ranges `$00`…`$3E`.
; The 26 valid columns use offsets `$00`–`$32` (`$0A00`–`$0A33`).
; Any X coordinate large enough to produce offset `$34`–`$3E` lands in your range and reads `$0000`.
; Because the entry is `$0000` for both MSB and the row base LSB,
; the computed destination collapses to address `$0000` (plus a tiny Y offset),
; i.e. low ROM, where writes are simply ignored.
; The result is that an object pushed past the right edge is "drawn" to a harmless null address
; instead of corrupting screen RAM or wrapping onto a visible tile.
```

### T0A00:

```asm
                       .MSFIRST
                       .DW ForegroundScreen+$320  ; Upper left corner of rotated screen
                       .DW ForegroundScreen+$300
                       .DW ForegroundScreen+$2E0
                       .DW ForegroundScreen+$2C0
                       .DW ForegroundScreen+$2A0
                       .DW ForegroundScreen+$280
                       .DW ForegroundScreen+$260
                       .DW ForegroundScreen+$240
                       .DW ForegroundScreen+$220
                       .DW ForegroundScreen+$200
                       .DW ForegroundScreen+$1E0
                       .DW ForegroundScreen+$1C0
                       .DW ForegroundScreen+$1A0
                       .DW ForegroundScreen+$180
                       .DW ForegroundScreen+$160
                       .DW ForegroundScreen+$140
                       .DW ForegroundScreen+$120
                       .DW ForegroundScreen+$100
                       .DW ForegroundScreen+$E0
                       .DW ForegroundScreen+$C0
                       .DW ForegroundScreen+$A0
                       .DW ForegroundScreen+$80
                       .DW ForegroundScreen+$60
                       .DW ForegroundScreen+$40
                       .DW ForegroundScreen+$20
                       .DW ForegroundScreen       ; Upper right corner of rotated screen

; Mapping the 'out of screen' objects,
; that catch coordinates mapping beyond the 26 columns, returning a null (`$0000`) address
; so off screen objects are written to a safe, ignored location rather than drawn as garbage.
                       .DB $00, $00
                       .DB $00, $00
                       .DB $00, $00
                       .DB $00, $00
                       .DB $00, $00
                       .DB $00, $00
;
```

### T0A40:

```asm
                       .DB $AA, $BA, $AB, $BB     ;alien shape #37 (set A)
                       .DB $80, $90, $81, $91     ;alien shape #34 (set A)
```

### T0A48:

```asm
                       .DB $74, $7C, $75, $7D     ;alien pilot shape (set B)

```
> [!NOTE]
> **Ported to C:** [`alien_data_controller`](../alien_logic.c#L274) in `alien_logic.c` (ASM: `0A50-0A6B`)

```asm
                       .ORG $0A50
;*****************************************************************************
;* Handle alien control states for all aliens.
;* This routine has a bug!
;* Loop goes 20 times for 16 aliens. But bit 3 or 4 is not set at
;* UpdateScreenObjects. So luckily no effect.
;* Possible fix would be: 'CP $F0' at $0A63.
;*****************************************************************************
```

### AlienDataController:

```asm
                       LD      BC,M4B70            ; alien data structure (grid)
                       LD      DE,M4BB0            ; alien data structure (screen ram)
```

### L0A56:

```asm
                       PUSH    BC                  ;
                       CALL    UpdateScreenObjects ;
                       POP     BC                  ;
                       LD      A,C                 ;
                       ADD     $04                 ;
                       LD      C,A                 ;
                       ADD     $40                 ;
                       LD      E,A                 ;
                       LD      D,B                 ;
                       AND     A                   ; updates the zero flag (bug)
                       JP      NZ,L0A56            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`get_screen_ram_address_for_all_aliens`](../alien_logic.c#L290) in `alien_logic.c` (ASM: `0A6C-0A99`)

```asm
                       .ORG $0A6C
;*****************************************************************************
;* Get screen ram adress for all aliens.
;*****************************************************************************
```

### L0A6C:

```asm
                       LD      BC,M4B70            ; data structure for alien control and screen coordinate
                       LD      DE,M4BB3            ; data structure for alien screen ram address
```

### L0A72:

```asm
                       PUSH    BC                  ;
                       PUSH    DE                  ;
                       LD      A,(BC)              ;
                       AND     $18                 ; mask out 0001_1000
                       JP      Z,L0A8A             ; if 0 then skip the mapping
                       EX      DE,HL               ;
                       LD      D,(HL)              ;
                       DEC     HL                  ;
                       LD      E,(HL)              ;
                       DEC     HL                  ;
                       LD      (HL),D              ;
                       DEC     HL                  ;
                       LD      (HL),E              ;
                       EX      DE,HL               ;
                       INC     DE                  ;
                       INC     DE                  ;
                       INC     BC                  ;
                       INC     BC                  ;
                       CALL    GetScreenRamAddress ;
```

### L0A8A:

```asm
                       POP     DE                  ;
                       POP     BC                  ;
                       LD      A,C                 ;
                       ADD     $04                 ;
                       LD      C,A                 ;
                       LD      A,E                 ;
                       ADD     $04                 ;
                       LD      E,A                 ;
                       CP      $03                 ;
                       JP      NZ,L0A72            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`draw_shields`](../player_logic.c#L294) in `player_logic.c` (ASM: `0AA0-0AC1`)

```asm
                       .ORG $0AA0
;*****************************************************************************
;* Handler for the player shield.
;*****************************************************************************
```

### DrawShields:

```asm
                       LD      L,PlayerShipMSB & $FF     ; HL=43E2 Player's screen memory location
                       LD      D,(HL)              ; Get the PlayerScreenRamMSB
                       INC     HL                  ; Get the ... PlayerScreenRamLSB
                       LD      E,(HL)              ; ... LSB (ignore any fine bit shifting of the player)
                       CALL    LeftOneColumn       ; Shield pictures begin one column to the left of the ship
                       DEC     DE                  ; Shield pictures begin one row above the ship
                       LD      BC,$0404            ; Shiled images are 4x4
                       LD      L,ShieldCount & $FF ; Decrement the ...
                       DEC     (HL)                ; ... shield counter
                       LD      A,(HL)              ; Current shield counter value
                       LD      HL,FourByFourEmpty  ; Blank 4x4
                       CP      $C0                 ; Shield time done?
                       JP      Z,ShieldsExpired    ; Yes ... turn shields off
                       LD      HL,T1770            ; Four shield-active pictures
                       AND     $0C                 ; Drop lower 2 bits (0000_1100). Images change every 4 ticks.
                       RLCA                        ; Multiply by 4 ...
                       RLCA                        ; ... to get a 16-byte offest (4x4 pictures)
                       ADD     A,L                 ; Point to the ...
                       LD      L,A                 ; ... correct image
                       JP      DrawImageCbyB       ; Draw the new shield image

```
> [!NOTE]
> **Ported to C:** [`draw_image_c_by_b`](../utilities.c#L283) in `utilities.c` (ASM: `0AD6-0AE9`)

```asm
                       .ORG $0AD6
;*****************************************************************************
; B is number of rows
; C is number of columns
; HL is the data
; DE is the pointer to the screen
;*****************************************************************************
```

### DrawImageCbyB:

```asm
                       PUSH    DE                  ; Hold screen pointer
                       PUSH    BC                  ; Hold width/Height
```

### L0AD8:

```asm
                       LD      A,(HL)              ; Character to ...
                       LD      (DE),A              ; ... the screen
                       INC     HL                  ; Next in data
                       INC     DE                  ; Next column on screen
                       DEC     B                   ; All rows done in this column?
                       JP      NZ,L0AD8            ; No ... finish the rows
                       POP     BC                  ; Restore the counters
                       POP     DE                  ; Restore the screen pointer
                       CALL    RightOneColumn      ; Move over one column
                       DEC     C                   ; All columns done?
                       JP      NZ,DrawImageCbyB    ; No ... do all columns
                       RET                         ; Done

;*****************************************************************************
;* Game state 4.
;* Player ship partikel explosion.
;*****************************************************************************
```

### L0AEA:

```asm
                       LD      HL,CounterB9        ;
                       LD      A,(HL)              
                       AND     $F8                 
                       LD      (HL),A              
                       LD      (scrollRegister),A  ; 58xx scroll register
                       LD      L,$E2               
                       LD      D,(HL)              
                       INC     L                   
                       LD      E,(HL)              
                       CALL    LeftOneColumn       ;
                       DEC     DE                  
                       NOP                         
                       LD      L,$A5               
                       DEC     (HL)                
                       LD      A,(HL)              
                       JP      Z,L0B15             ;
                       CP      $20                 
                       JP      C,L0BA0             ;
                       JP      Z,ClearForeground   ;
                       JP      L0BBA               ;

```
> [!NOTE]
> **Ported to C:** [`l0b15`](../state_endings.c#L208) in `state_endings.c` (ASM: `0B15-0B2D`)

```asm
                       .ORG $0B15
;*****************************************************************************
;* The explosion is over — it reloads `CounterA5=5`, decrements that player's life count,
;* refreshes the lives display, and sets `GameState = 0` (new turn / next player start).
;*****************************************************************************
```

### L0B15:

```asm
                       DEC     L                   ;
                       LD      (HL),$05            ;
                       DEC     L                   ;
                       LD      A,(HL)              ;
                       ADD     $90                 ; -> Player1Lives / Player2Lives slot                 
                       LD      L,A                 ;
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       RET     Z                   ;
                       DEC     (HL)                ; lose a life
                       PUSH    HL                  ;
                       CALL    UpdateLivesScreen   ;
                       POP     HL                  ;
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       RET     Z                   ;
                       LD      L,$A4               ; GameState
                       LD      (HL),$00            ; set to: 'new game start'
                       RET                         ;

                       .ORG $0B38
; Player ship X position mapping table
```

### T0B38:

```asm
                       .DB $00, $08
                       .DB $01, $09
                       .DB $02, $0A
                       .DB $03, $0B
                       .DB $03, $0B
                       .DB $02, $0A
                       .DB $01, $09
                       .DB $00, $08

;*****************************************************************************
;* The player shield is expired.
;* Shield and player gets removed from screen.
;* PlayerShipX position is reset.
;*****************************************************************************
```

### ShieldsExpired:

```asm
                       CALL    DrawImageCbyB       ;
                       LD      HL,PlayerState      ;
                       LD      (HL),$0C            
                       INC     L                   
                       LD      (HL),$0C            
                       INC     L                   
                       LD      A,(HL)              
                       AND     $F8                 
                       OR      $03                 
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`state_5_game_over_text`](../state_endings.c#L67) in `state_endings.c` (ASM: `0B60-0B9D`)

```asm
                       .ORG $0B60
;*****************************************************************************
;* Game state 5.
;* 'GAME OVER'.
;*****************************************************************************
```

### L0B60:

```asm
                       LD      HL,CounterA5        ;
                       INC     (HL)                
                       LD      A,(HL)              
                       CP      $40                 
                       JP      Z,ClearBackground   ;
                       LD      HL,T1A00            ; "        GAME  OVER        "
                       LD      C,$01               
                       CP      $80                 
                       JP      NZ,L0B95            ; 
                       LD      HL,GameState        ; Next interval game state ...
                       LD      (HL),$00            ; ... is 0 (new game start)
                       LD      L,$90               
                       LD      A,(HL)              
                       INC     L                   
                       OR      (HL)                
                       RET     NZ                  
                       XOR     A                   ; A=0
                       LD      L,$98               
                       LD      (HL),A              
                       INC     L                   
                       LD      (HL),A              
                       LD      L,$A2               
                       LD      (HL),A              
                       INC     L                   
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   
                       LD      (HL),$00            
                       LD      BC,$0100            ; from bank 1 to bank 0
                       CALL    CopyMemoryBank      ;
                       RET                         
;
```

### L0B95:

```asm
                       CALL    PrintTextLines      ;
                       CALL    L01E4               ; Print the copyright lines
                       JP      L1DF0               ;

```
> [!NOTE]
> **Ported to C:** [`l0ba0`](../state_endings.c#L238) in `state_endings.c` (ASM: `0BA0-0BB2`)

```asm
                       .ORG $0BA0
;*****************************************************************************
;* Late cleanup: clear background, reset scroll on non‑mothership levels.
;*****************************************************************************
```

### L0BA0:

```asm
                       LD      HL,LevelAndRound    ;
                       LD      A,(HL)              ;
                       AND     $0F                 ; mask out 0000_1111
                       CP      $04                 ;
                       RET     C                   ; return if < game level 4 (alien waves)
                       CP      $09                 ;
                       RET     NC                  ; return if > game level 9 (mothership)
                       INC     L                   ; CounterB9
                       XOR     A                   ; A=0
                       LD      (HL),A              ; CounterB9 to 0
                       LD      (scrollRegister),A  ; reset the 58xx scroll register
                       JP      ClearBackground     ;

```
> [!NOTE]
> **Ported to C:** [`l0bba`](../state_endings.c#L256) in `state_endings.c` (ASM: `0BBA-0BC4`)

```asm
                       .ORG $0BBA
;*****************************************************************************
;* Player-ship explosion:
;* Per-frame visual dispatcher.
;* Entered from L0AEA (game state 4) with A = CounterA5 (explosion phase),
;* when CounterA5 >= $20. Selects one task per frame from the low 2 bits,
;* so the three effects are interleaved as the counter runs down:
;*   CounterA5 & 1 == 0   -> L0FC0  killed-alien animation upkeep
;*   CounterA5 & 3 == 01  -> L20E8  draw a 4x4 ship-fragment sprite
;*   CounterA5 & 3 == 11  -> L2070  render the particle field (T2800/T2900)
;* So across consecutive frames the three low bit patterns rotate through the three tasks,
;* letting the game advance the debris field, the fragment sprites,
;* and any in progress killed alien effects without doing all of them in a single frame.
;*****************************************************************************
```

### L0BBA:

```asm
                       LD      B,A                 ;
                       RRCA                        ;
                       JP      NC,L0FC0            ; Handle animations for killed aliens
                       RRCA                        ;
                       LD      A,B                 ;
                       JP      C,L2070             ;
                       JP      L20E8               ;

```
> [!NOTE]
> **Ported to C:** [`draw_score_average_table_tiles`](../attract_mode.c#L419) in `attract_mode.c` (ASM: `0BCA-0BF1`)

```asm
                       .ORG $0BCA
;*****************************************************************************
;* Draws the character tiles for the score average table.
;*****************************************************************************
```

### DrawScoreAverageTableTiles:

```asm
                       LD      HL,$42D0            ; upper left corner screen ram position
                       LD      BC,$FFDF            ; Screen offset constant -33 right one column (-1), up one row (-32)
                       LD      (HL),$64            ; left part of alien shape #3
                       ADD     HL,BC               ;
                       INC     HL                  ;
                       LD      (HL),$65            ; right part of alien shape #3
                       LD      HL,$42F2            ; screen ram position for
                       LD      DE,T0A40            ; T0A40 alien shape #37 and alien shape #34
                       CALL    Draw4x2             ;
                       LD      HL,$4B15            ; screen ram position for
                       LD      DE,T3C00            ; bird shape #24 (Object 3C00)
                       CALL    Draw6x2             ;
                       LD      HL,$4AD8            ; screen ram position for
                       LD      DE,T0A48            ; T0A48 alien pilot shape
                       CALL    Draw2x2             ;
                       RET                         ;

                       .ORG $0C00
;*****************************************************************************
;* Score/bonus selector for a shot flying alien:
;* A flying alien was hit. Choose its explosion / score from its current
;* movement-pattern phase.
;* Entry: HL -> struck alien's screen-X field ($4B72 + 4*index).
;* Per-alien movement-pattern pointers live at $4B50 (2 bytes: MSB,LSB each).
;* Pattern value 7 or 8 (attack/dive apex) -> 200-pt bonus + bonus explosion;
;* any other value -> normal kill.  All paths finish in L0EA4.
;* This routine is the mechanic that rewards shooting an alien at the peak of its swoop/dive,
;* only when the enemy's movement pattern is in phase 7–8 do you get the 200 point bonus
;* and the special bonus explosion, hitting it at any other point in its flight
;* gives the ordinary kill value.
;*****************************************************************************
```

### L0C00:

```asm
                       PUSH    HL                  ; save the alien entry pointer
                       LD      A,L                 ; L = $72,$76,$7A,... (screen-X field of this alien)
                       SUB     $72                 ; -> 0,4,8,... = 4 * alien index
                       RRCA                        ; /2 -> 0,2,4,... = 2 * alien index
                       ADD     $50                 ; -> $50 + 2*index
                       LD      L,A                 ; HL = $4B50 + 2*index (this alien's pattern pointer)
                       LD      A,(HL)              ; get MSB pointer of alien movement pattern
                       INC     L                   ; 
                       LD      L,(HL)              ; get LSB pointer of alien movement pattern
                       LD      H,A                 ; HL = alien's current position in its pattern list
                       LD      DE,$0C04            ; default: D=$0C anim index, E=$04 normal-kill score
                       LD      A,(HL)              ; get movement pattern value (current phase)
                       POP     HL                  ; restore the alien entry pointer
                       CP      $07                 ; 
                       JP      C,L0EA4             ; phase < $07: normal kill
                       CP      $09                 ; 
                       JP      NC,L0EA4            ; phase >= $09: normal kill
; Else phase is $07 or $08 -> BONUS
                       LD      DE,$1020            ; D=$10 anim index, E=$20 bonus explosion score 200
                       LD      A,$FF               ; set bonus explosion flag
                       LD      (M4369),A           ; $4369 = 'bonus explosion'
                       JP      L0EA4               ; kill with the bonus values

```
> [!NOTE]
> **Ported to C:** [`process_enemy_bombs`](../weapon_collision.c#L163) in `weapon_collision.c` (ASM: `0C40-0C51`)

```asm
                       .ORG $0C40
;*****************************************************************************
; Updates the enemy bullets.
;*****************************************************************************
```

### L0C40:

```asm
                       LD      HL,AlienBullet4LSB  ; 
                       LD      B,$05               ; 5 bullet slots
                       CALL    L088B               ; Copy current enemy bullet data to old enemy bullet data
                       CALL    L0C56               ; Enemy bullets movement and animation
                       CALL    L0C6B               ; Get the screen ram address for all enemy bullets
                       CALL    L0CD8               ; Draw or delete the screen objects
                       RET                         ; 

```
> [!NOTE]
> **Ported to C:** [`enemy_bullet_movement_and_animation`](../weapon_collision.c#L119) in `weapon_collision.c` (ASM: `0C56-0C67`)

```asm
                       .ORG $0C56
;*****************************************************************************
;* Enemy bullets movement and animation.
;* Handles all 5 bullet slots.
;*****************************************************************************
```

### L0C56:

```asm
                       LD      HL,AlienBullet0State; 
```

### L0C59:

```asm
                       PUSH    HL                  ; 
                       CALL    L0C84               ; movement and animation of enemy bullet
                       POP     HL                  ; 
                       LD      A,L                 ; 
                       ADD     $04                 ; 
                       LD      L,A                 ; 
                       CP      $E0                 ; 
                       JP      NZ,L0C59            ; loop for 5 enemy bullet slots
                       RET                         ; 

```
> [!NOTE]
> **Ported to C:** [`get_screen_ram_address_for_enemy_bullets`](../weapon_collision.c#L132) in `weapon_collision.c` (ASM: `0C6B-0C80`)

```asm
                       .ORG $0C6B
;*****************************************************************************
;* Get the screen ram address for all enemy bullets.
;*****************************************************************************
```

### L0C6B:

```asm
                       LD      BC,AlienBullet0X    ; 
                       LD      DE,AlienBullet0MSB  ; 
```

### L0C71:

```asm
                       CALL    GetScreenRamAddress ; 
                       INC     BC                  
                       INC     BC                  
                       INC     BC                  
                       INC     DE                  
                       INC     DE                  
                       INC     DE                  
                       LD      A,C                 
                       CP      $E2                 
                       JP      NZ,L0C71            ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l0c84_enemy_bullet_movement`](../weapon_collision.c#L63) in `weapon_collision.c` (ASM: `0C84-0CB3`)

```asm
                       .ORG $0C84
;*****************************************************************************
;* Movement and animation of enemy bullet.
;* They have half the speed of player bullets and a simple animation.
;*****************************************************************************
```

### L0C84:

```asm
                       LD      A,(HL)              
                       AND     $08                 
                       RET     Z                   
                       NOP                         
                       NOP                         
                       INC     L                   
                       LD      A,(HL)              
                       XOR     $04                 
                       LD      (HL),A              
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       ADD     $04                 
                       LD      (HL),A              
                       CP      $F9                 
                       JP      NC,L096E            ; 
                       DEC     L                   
                       CALL    L0CB4               ; 
                       LD      D,H                 
                       LD      A,L                 
                       ADD     $20                 
                       LD      E,A                 
                       EX      DE,HL               
                       LD      B,(HL)              
                       INC     HL                  
                       LD      C,(HL)              
                       LD      A,(BC)              
                       EX      DE,HL               
                       INC     L                   
                       CP      $E8                 
                       JP      NC,L096E            ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l0cb4_check_bullet_hit_player`](../weapon_collision.c#L30) in `weapon_collision.c` (ASM: `0CB4-0CD4`)

```asm
                       .ORG $0CB4
;
```

### L0CB4:

```asm
                       CP      $DC                 ; lower part of screen
                       RET     C                   ; if not reached
                       CP      $E9                 
                       RET     NC                  
                       LD      A,(M439F)           ; Mapped player ship position, right part: ($17 to $C8)
                       CP      (HL)                
                       RET     C                   
                       LD      A,(M439E)           ; Mapped player ship position, left part: ($09 to $C0)
                       CP      (HL)                
                       RET     NC                  

;*****************************************************************************
;* The player ship was hit.
;* MAME cheat code "Invincibility": Set $0CC4 to $C9 (RET).
;*****************************************************************************
```

### L0CC4:

```asm
                       LD      A,$04               ; Next interval game state is 4 (player ship partikel explosion)
                       LD      (GameState),A       ; 
                       LD      A,$60               ; set a new counter value for ...
                       LD      (CounterA5),A       ; 
                       LD      A,$10               ; set flag and counter for ..
                       LD      (ParticleExplosion),A
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`enemy_bullet_data_controller`](../weapon_collision.c#L148) in `weapon_collision.c` (ASM: `0CD8-0CEF`)

```asm
                       .ORG $0CD8
;*****************************************************************************
;* Handle enemy bullet control states for 5 bullet slots,
;* and draw or delete the screen object.
;*****************************************************************************
```

### L0CD8:

```asm
                       LD      BC,AlienBullet0State; data structure (grid)
                       LD      DE,OldAlienBullet0MSB; screen ram
```

### L0CDE:

```asm
                       PUSH    BC                  
                       CALL    UpdateScreenObjects ; 
                       POP     BC                  
                       LD      A,C                 
                       ADD     $04                 
                       LD      C,A                 
                       ADD     $20                 
                       LD      E,A                 
                       LD      D,B                 
                       AND     A                   ; updates the zero flag
                       JP      NZ,L0CDE            ; loop for all bullet slots
                       RET                         

                       .ORG $0CF4
;*****************************************************************************
;* Alien collision on left or right side of player ship.
;*****************************************************************************
```

### L0CF4:

```asm
                       POP     DE                  
                       POP     BC                  
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`alien_movement_update`](../alien_logic.c#L335) in `alien_logic.c` (ASM: `0D1C-0D67`)

```asm
                       .ORG $0D1C
;*****************************************************************************
;* Alien movement update.
;*****************************************************************************
```

### L0D1C:

```asm
                       LD      BC,M4B70            ; 
                       LD      HL,M4B50            ; 
```

### L0D22:

```asm
                       CALL    L0D30               ; 
                       INC     C                   
                       INC     C                   
                       INC     L                   
                       LD      A,$B0               
                       CP      C                   
                       JP      NZ,L0D22            ; 
                       RET                         

                       .ORG $0D30
;
```

### L0D30:

```asm
                       LD      D,(HL)              
                       INC     HL                  
                       LD      A,(BC)              
                       INC     BC                  
                       INC     BC                  
                       AND     $08                 
                       RET     Z                   ; if bit3 of alien control state A, not set
                       LD      E,(HL)              
                       EX      DE,HL               
                       LD      A,(HL)              ; get T1000 (Closed loops pattern table for aliens)
                       RLCA                        ; Multiply by 2
                       ADD     $00                 ; reset all flags
                       LD      L,A                 
                       LD      H,T1700 >> 8        ; get MSB for T1700
                       XOR     A                   ; A=0
                       CP      (HL)                
                       JP      Z,L0D4F             ; 
                       INC     HL                  
                       CP      (HL)                
                       JP      Z,L0D5E             ; 
                       DEC     HL                  
                       LD      A,(BC)              
                       ADD     A,(HL)              
                       LD      (BC),A              
```

### L0D4F:

```asm
                       INC     BC                  
                       INC     HL                  
                       LD      A,(BC)              
                       ADD     A,(HL)              
                       LD      (BC),A              
                       DEC     BC                  
                       AND     $07                 
                       EX      DE,HL               
                       RET     NZ                  
                       INC     (HL)                
                       RET                         

                       .ORG $0D5E
```

### L0D5E:

```asm
                       DEC     HL                  
                       LD      A,(BC)              
                       ADD     A,(HL)              
                       LD      (BC),A              
                       AND     $07                 
                       EX      DE,HL               
                       RET     NZ                  
                       INC     (HL)                
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`alien_animation_update`](../alien_logic.c#L382) in `alien_logic.c` (ASM: `0D70-0DB5, 0DBB-0DC6, 0DCC-0DEE`)

```asm
                       .ORG $0D70
;*****************************************************************************
;* Alien animation update.
;*****************************************************************************
```

### L0D70:

```asm
                       LD      BC,M4B70            ; 
                       LD      HL,M4B50            ; 
```

### L0D76:

```asm
                       CALL    L0D86               ; 
                       LD      A,C                 
                       ADD     $04                 
                       LD      C,A                 
                       LD      A,$B0               
                       CP      C                   
                       JP      NZ,L0D76            ; 
                       RET                         

                       .ORG $0D86
```

### L0D86:

```asm
                       LD      D,(HL)              
                       INC     HL                  
                       LD      E,(HL)              
                       INC     HL                  
                       LD      A,(BC)              
                       AND     $08                 
                       RET     Z                   
                       EX      DE,HL               
                       LD      A,(HL)              ; Closed loops pattern table for aliens
                       AND     A                   ; updates the zero flag
                       CALL    Z,L0DDE             ; 
                       LD      L,A                 
                       RLCA                        ; Multiply by 2
                       ADD     A,L                 
                       ADD     $A0                 
                       LD      L,A                 
                       LD      H,T1600 >> 8        
                       LD      A,(BC)              
                       AND     $F8                 
                       OR      (HL)                
                       LD      (BC),A              
                       INC     BC                  
                       INC     BC                  
                       INC     BC                  
                       INC     HL                  
                       LD      A,(HL)              
                       INC     HL                  
                       RRCA                        
                       JP      C,L0DBB             ; 
                       RRCA                        
                       JP      C,L0DCC             ; 
; 2nd byte of alien animation table is: $04
                       LD      A,(BC)              
                       RRCA                        
                       AND     $03                 
                       ADD     A,(HL)              
                       DEC     BC                  
                       JP      L0DD2               ; 

                       .ORG $0DBB
; 2nd byte of alien animation table is: $01
```

### L0DBB:

```asm
                       LD      A,(BC)              
                       RRCA                        
                       AND     $03                 
                       ADD     A,(HL)              
                       LD      H,A                 
                       DEC     BC                  
                       LD      A,(BC)              
                       AND     $04                 
                       ADD     A,H                 
                       JP      L0DD2               ; 

                       .ORG $0DCC
; 2nd byte of alien animation table is: $02
```

### L0DCC:

```asm
                       DEC     BC                  
                       LD      A,(BC)              
                       RRCA                        
                       AND     $03                 
                       ADD     A,(HL)              
```

### L0DD2:

```asm
                       LD      L,A                 
                       LD      H,T1600 >> 8       ; get data from T1600
                       LD      A,(HL)              
                       DEC     BC                  
                       LD      (BC),A              
                       DEC     BC                  
                       EX      DE,HL               
                       RET                         

                       .ORG $0DDE
; End of movement list reached
```

### L0DDE:

```asm
                       DEC     DE                  
                       DEC     DE                  
                       LD      A,(M4394)           ; 
                       LD      (DE),A              
                       LD      H,A                 
                       INC     DE                  
                       LD      A,(M4395)           ; 
                       LD      (DE),A              
                       LD      L,A                 
                       INC     DE                  
                       LD      A,(HL)              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`check_enemy_bullet_to_player_collision`](../weapon_collision.c#L189) in `weapon_collision.c` (ASM: `0DF0-0E01`)

```asm
                       .ORG $0DF0
;*****************************************************************************
;* Player bullet to alien, collission detection.
;*****************************************************************************
```

### L0DF0:

```asm
                       LD      BC,PlayerBulletState; 
                       LD      HL,AbovePlayerBulletMSB; MSB screen ram: One character above player bullet
                       CALL    L0E10               ; 
                       LD      BC,AbovePlayerBulletState; 
                       LD      HL,M43EA            ; MSB screen ram: Left screen edge, one character above player ship
                       JP      L0E10               ; 

```
> [!NOTE]
> **Ported to C:** [`l0c00_kill_score`](../weapon_collision.c#L214) in `weapon_collision.c` (ASM: `0E10-0E6B, 0E70-0E9D, 0C00-0C23`)

> [!NOTE]
> **Ported to C:** [`l0e10`](../weapon_collision.c#L233) in `weapon_collision.c` (ASM: `0E10-0E36, 0E39-0E6B, 0E58-0E6B, 0E70-0EA0`)

```asm
                       .ORG $0E10
;
```

### L0E10:

```asm
                       LD      A,(BC)              ; get player bullet state
                       AND     $08                 ; mask out 0000_1000
                       RET     Z                   ; if bit3 not set
                       LD      D,(HL)              ; get MSB screen ram adress
                       INC     L                   ;
                       LD      E,(HL)              ; get LSB screen ram adress
                       LD      A,(DE)              ; get character
                       CP      $C0                 ; bullets and alien ($50 - $BF)
                       RET     NC                  ;
                       CP      $60                 ; alien ($60 - $BF)
                       RET     C                   ; if no character
                       CP      $68                 ; alien
                       JP      NC,L0E39            ; 
                       AND     $07                 ; mask out 0000_0111
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       ADD     $40                 ;
                       LD      L,A                 ;
                       LD      H,T1740 >> 8        ; T1740
                       INC     BC                  ;
                       INC     BC                  ;
                       LD      A,(BC)              ;
                       AND     $07                 ;
                       CP      (HL)                ;
                       RET     NC                  ;
                       INC     HL                  ;
                       CP      (HL)                ;
                       RET     C                   ;
                       JP      L0E70               ; 

;*****************************************************************************
;* Player bullet vs FLYING alien (out of formation) collision.
;* Entry (from L0E10): BC -> player-bullet structure (state at +0),
;*                     bullet X at +2, bullet Y at +3.
;* Builds the bullet's target box, then scans all 16 alien slots ($4B70).
;*****************************************************************************
```

### L0E39:

```asm
                       INC     BC                  
                       INC     BC                  
                       LD      A,(BC)              
                       LD      D,A                 
                       INC     BC                  
                       LD      A,(BC)              
                       AND     $F8                 
                       LD      E,A                 
                       LD      HL,M4B70            ; 
;*****************************************************************************
;* Scan every alien slot; test the active ones for a hit.
;*****************************************************************************
```

### L0E45:

```asm
                       LD      A,(HL)              
                       INC     HL                  
                       INC     HL                  
                       AND     $08                 
                       CALL    NZ,L0E58            ; 
                       INC     HL                  
                       INC     HL                  
                       LD      A,$B0               
                       CP      L                   
                       JP      NZ,L0E45            ; 
                       RET                         

                       .ORG $0E58
;*****************************************************************************
;* Bounding-box test for one flying alien.
;* HL -> alien screen X (+2); D = bullet X, E = bullet Y (masked).
;* Box: alienX <= bulletX <= alienX+8  and  alienY-8 < bulletY <= alienY+4.
;* If the bullet falls inside that box, it's a hit and control jumps to `L0C00`
;* (with `HL` still pointing at the alien's `+2` field),
;* which reads the alien's movement pattern phase to choose the score/bonus
;* and then routes to `L0EA4` to blow it up.
;*****************************************************************************
```

### L0E58:

```asm
                       LD      A,D                 
                       CP      (HL)                
                       RET     C                   
                       LD      A,(HL)              
                       ADD     $08                 
                       CP      D                   
                       RET     C                   
                       INC     HL                  
                       LD      A,(HL)              
                       DEC     HL                  
                       ADD     $04                 
                       CP      E                   
                       RET     C                   
                       SUB     $0C                 
                       CP      E                   
                       RET     NC                  
                       JP      L0C00               ; 

                       .ORG $0E70
;
```

### L0E70:

```asm
                       INC     HL                  
                       LD      A,(BC)              
                       AND     $F8                 
                       ADD     A,(HL)              
                       LD      D,A                 
                       INC     BC                  
                       LD      A,(BC)              
                       AND     $F8                 
                       LD      E,A                 
                       LD      HL,M4B70            ; 
```

### L0E7E:

```asm
                       LD      A,(HL)              
                       INC     HL                  
                       INC     HL                  
                       AND     $08                 
                       CALL    NZ,L0E90            ; 
                       INC     HL                  
                       INC     HL                  
                       LD      A,$B0               
                       CP      L                   
                       JP      NZ,L0E7E            ; 
                       RET                         

                       .ORG $0E90
;
```

### L0E90:

```asm
                       LD      A,(HL)              
                       ADD     $02                 
                       CP      D                   
                       RET     C                   
                       SUB     $05                 
                       CP      D                   
                       RET     NC                  
                       INC     HL                  
                       LD      A,(HL)              
                       DEC     HL                  
                       AND     $F8                 
                       CP      E                   
                       RET     NZ                  
                       LD      DE,$0C02            ; E reg. set to: 'bonus explosion score 020'.
                       NOP                         
;*****************************************************************************
;* Kill with the bonus values.
;* `L0EA4` is the common "enemy destroyed" routine:
;* It clears the bullet's and alien's active bits, finds a free bonus explosion animation slot (`$4378`/`$4370`),
;* and uses `D` as the animation index and `E` as the score value.
;* (Compare the sibling entry `L0EA0: LD DE,$0C02` used for in formation kills — same mechanism, different score/anim.)
;*****************************************************************************
```

### L0EA4:

```asm
                       DEC     HL                  
                       DEC     HL                  
                       DEC     BC                  
                       DEC     BC                  
                       DEC     BC                  
                       LD      A,(BC)              
                       AND     $F7                 
                       LD      (BC),A              
```

### L0EAD:

```asm
                       LD      A,(HL)              
                       AND     $F7                 
                       LD      (HL),A              
                       LD      A,L                 
                       ADD     $42                 
                       LD      L,A                 
                       LD      B,(HL)              
                       INC     HL                  
                       LD      C,(HL)              
                       LD      HL,M4378            ; 
                       LD      A,D                 
                       CP      $10                 
                       JP      Z,L0EC3             ; 
                       LD      L,$70               
```

### L0EC3:

```asm
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       JP      Z,L0ED5             ; 
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       JP      Z,L0ED5             ; 
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       INC     L                   
```

### L0ED5:

```asm
                       LD      (HL),D              
                       INC     L                   
                       LD      (HL),E              ; set $4379 (bonus explosion score)
                       INC     L                   
                       LD      (HL),B              
                       INC     L                   
                       LD      (HL),C              
                       LD      L,$64               
                       LD      (HL),$FF            
                       LD      L,$BA               
                       DEC     (HL)                ; decrement AliensLeft
                       POP     HL                  
                       POP     HL                  
                       JP      (HL)                

```
> [!NOTE]
> **Ported to C:** [`l0f00_check_alien_with_player_collision`](../weapon_collision.c#L380) in `weapon_collision.c` (ASM: `0F00-0F33, 0F38-0F4E, 0F74-0FB9`)

```asm
                       .ORG $0F00
;*****************************************************************************
;* 'Alien with player' collision check.
;* MAME cheat code "Invisibility for aliens": Set $0F00 to $C9 (RET)
;* Uses a 2x2 box normally; a 4x4 box when the shield/explosion state is high.
;* This is the counterpart to the bullet vs alien check:
;* It asks "has a diving alien run into the player's ship?".
;* - Box size depends on the shield (`ShieldCount`, `$43A6`).
;*   If it's below `$C0`, `L0F00` uses a 2×2 collision box around the ship.
;*   If it's `$C0` or higher (shield up / ship showing explosion tiles),
;*   it branches to `L0F74`, which uses a larger 4×4 box and a wider vertical band.
;* - `L0F56` is the fast screen test.
;*   Given the ship's screen address and a `cols × rows` size,
;*   It reads each character cell the ship occupies.
;*   If any cell holds an alien glyph (`$60`–`$BF`) it immediately jumps to `L0CF4`
;*   to handle the player being hit.
;*   If it walks the whole box with no alien, it returns with `Z` set ("no collision").
;* - `L0F38` / `L0FA6` identify and kill the offending alien.
;*   After a collision is detected, the caller derives the ship's horizontal bounds (`B`,`C`)
;*   and scans all 16 alien slots at `$4B70`. For each active alien
;*   it checks that the alien's Y is in the player's bottom band
;*   (small box `($D2,$E7)`, big box `($CA,$EF)`) and its X overlaps the ship (`B ≤ X < C`).
;*   On a match it loads the animation/score values into `DE` (`$0D04` small, `$0D02` big),
;*   rewinds `HL` to the alien's control byte, and jumps to `L0EAD`
;*   (the shared "enemy destroyed" tail, same one used by the bullet kill path) to blow the alien up.
;*****************************************************************************
```

### L0F00:

```asm
                       LD      HL,ShieldCount      ; 
                       LD      A,(HL)              ;
                       CP      $C0                 ;
                       JP      NC,L0F74            ; 
                       LD      L,$E2               ;
                       LD      D,(HL)              ; get $43E2 PlayerShipMSB
                       INC     L                   ;
                       LD      E,(HL)              ; get $43E3 PlayerShipLSB
                       LD      BC,$0202            
                       CALL    L0F56               ; 'alien with player' collision check
                       RET     Z                   ; if no collision
                       NOP                         
                       NOP                         
                       LD      HL,M439E            ; Mapped player ship position, left part: ($09 to $C0)
                       LD      A,(HL)              
                       SUB     $06                 
                       LD      B,A                 
                       INC     L                   
                       LD      C,(HL)              
                       LD      HL,M4B70            ; 
```

### L0F23:

```asm
                       LD      A,(HL)              
                       INC     L                   
                       INC     L                   
                       AND     $08                 
                       CALL    NZ,L0F38            ; 
                       INC     L                   
                       INC     L                   
                       LD      A,$B0               
                       CP      L                   
                       JP      NZ,L0F23            ; 
                       RET                         

                       .ORG $0F38
;*****************************************************************************
;* Find the specific colliding alien (small box). HL -> alien screen X (+2).
;* B/C = ship X bounds. Alien Y must be in the bottom band ($D2,$E7).
;*****************************************************************************
```

### L0F38:

```asm
                       INC     L                   
                       LD      A,(HL)              
                       DEC     L                   
                       CP      $D2                 
                       RET     C                   
                       CP      $E7                 
                       RET     NC                  
                       LD      A,(HL)              
                       CP      C                   
                       RET     NC                  
                       CP      B                   
                       RET     C                   
                       CALL    L0CC4               ; 
                       LD      DE,$0D04            
                       DEC     HL                  
                       DEC     HL                  
                       JP      L0EAD               ; 

```
> [!NOTE]
> **Ported to C:** [`l0f56_screen_ram_collision`](../weapon_collision.c#L352) in `weapon_collision.c` (ASM: `0F56-0F71`)

```asm
                       .ORG $0F56
;*****************************************************************************
;* 'Alien with player' collision check.
;* All parts of the player ship object are checked for a collision with aliens.
;*****************************************************************************
```

### L0F56:

```asm
                       PUSH    BC                  ;
                       PUSH    DE                  ;
```

### L0F58:

```asm
                       LD      A,(DE)              ; get upper left character of player ship
                       CP      $60                 ; alien characters ($60 to $BF)
                       JP      C,L0F63             ; if no collision on left side
                       CP      $C0                 ;
                       JP      C,L0CF4             ; if collision on left or right side
```

### L0F63:

```asm
                       INC     DE                  ; get upper right character of player ship
                       DEC     B                   ;
                       JP      NZ,L0F58            ; 
                       POP     DE                  ;
                       POP     BC                  ;
                       CALL    RightOneColumn      ; for lower part of player ship
                       DEC     C                   ;
                       JP      NZ,L0F56            ; 
                       RET                         ;

                       .ORG $0F74
;*****************************************************************************
;* Big-box variant: used when ShieldCount >= $C0 (4x4 box, wider Y band).
;*****************************************************************************
```

### L0F74:

```asm
                       LD      L,$E2               
                       LD      D,(HL)              
                       INC     L                   
                       LD      E,(HL)              
                       CALL    RightOneColumn      ; 
                       DEC     DE                  
                       LD      BC,$0404            
                       CALL    L0F56               ; 
                       RET     Z                   
                       NOP                         
                       NOP                         
                       LD      A,(PlayerShipX)     ; 
                       SUB     $0E                 
                       LD      B,A                 
                       ADD     $2D                 
                       LD      C,A                 
                       LD      HL,M4B70            ; 
```

### L0F92:

```asm
                       LD      A,(HL)              
                       INC     L                   
                       INC     L                   
                       AND     $08                 
                       CALL    NZ,L0FA6            ; 
                       INC     L                   
                       INC     L                   
                       LD      A,$B0               
                       CP      L                   
                       JP      NZ,L0F92            ; 
                       RET                         

                       .ORG $0FA6
;*****************************************************************************
;* Find the specific colliding alien (big box). Y band ($CA,$EF).
;*****************************************************************************
```

### L0FA6:

```asm
                       INC     L                   
                       LD      A,(HL)              
                       DEC     L                   
                       CP      $CA                 
                       RET     C                   
                       CP      $EF                 
                       RET     NC                  
                       LD      A,(HL)              
                       CP      C                   
                       RET     NC                  
                       CP      B                   
                       RET     C                   
                       LD      DE,$0D02            
                       DEC     HL                  
                       DEC     HL                  
                       JP      L0EAD               ; 

```
> [!NOTE]
> **Ported to C:** [`handle_animations_for_killed_aliens`](../alien_logic.c#L195) in `alien_logic.c` (ASM: `0FC0-0FFF`)

```asm
                       .ORG $0FC0
;*****************************************************************************
;* Handle animations for killed aliens.
;* Services 4 explosion slots (4-byte records at $4370/$4374/$4378/$437C):
;*   +0 = animation counter (0 = slot free)
;*   +1 = unused
;*   +2 = screen-RAM MSB
;*   +3 = screen-RAM LSB
;* Slots 0/1 are ordinary alien explosions (L0FD8); slots 2/3 use L3758
;* (the bonus-explosion animator).
;*****************************************************************************
```

### L0FC0:

```asm
                       LD      HL,M4370            ; explosion slot 0
                       CALL    L0FD8               ; advance alien explosion
                       LD      HL,M4374            ; explosion slot 1
                       CALL    L0FD8               ; advance alien explosion
                       LD      HL,M4378            ; slot 2 (bonus explosion counter)
                       CALL    L3758               ; advance bonus explosion
                       LD      HL,M437C            ; slot 3 (bonus explosion)
                       JP      L3758               ; advance bonus explosion (tail-call)
;*****************************************************************************
;* Advance and draw one alien-explosion slot.
;* HL -> slot record (+0 = counter). Returns immediately if the slot is idle.
;*****************************************************************************
```

### L0FD8:

```asm
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   
                       LD      B,(HL)              
                       DEC     (HL)                
                       INC     L                   
                       INC     L                   
                       LD      D,(HL)              
                       INC     L                   
                       LD      E,(HL)              
                       NOP                         
                       CALL    LeftOneColumn       ; 
                       LD      A,B                 
                       AND     $0E                 
                       RRCA                        
                       ADD     $B0                 
                       LD      L,A                 
                       LD      H,$17               
                       LD      L,(HL)              
                       EX      DE,HL               
                       LD      BC,$FFDF            ; Screen offset constant -33 right one column (-1), up one row (-32)
                       JP      Draw3x2             ; 

;*****************************************************************************
; ic47
;*****************************************************************************
                       .ORG $1000
; Pointer table to alien movement list (T1700):
; Value * 2 ==> LSB of T1700
; This is the default movement pattern for the alien formation:
; Right, right, right, right, left, left, left, left,
; left, left, left, left, right, right, right, right,
; end mark. Used at phase 0, 1, 2 and 3.
```

### T1000:

```asm
                       .DB $01, $01, $01, $01, $02, $02, $02, $02
                       .DB $02, $02, $02, $02, $01, $01, $01, $01
                       .DB $00
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF
; Closed loop pattern table part 1:
; Used for single or multiple aliens, depending on the game round.
; Pattern 1
```

### T1020:

```asm
                       .DB $10, $11, $12, $13, $10, $1D, $0D, $0E
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $06, $06
                       .DB $1E, $03, $1F, $05, $1C, $04, $1D, $06
                       .DB $1E, $03, $03, $03, $03, $03, $1F, $1C
                       .DB $1D, $1E, $03, $03, $03, $03, $03, $1F
                       .DB $05, $1C, $04, $1D, $06, $1E, $03, $1F
                       .DB $05, $05, $05, $05, $05, $05, $05, $05
                       .DB $05, $05, $1C, $04, $04, $11, $12, $13
                       .DB $00, $FF, $FF, $FF
; Pattern 2
```

### T1064:

```asm
                       .DB $0B, $1E, $19, $06, $06, $06, $06, $06
                       .DB $06, $1E, $1F, $1C, $1D, $06, $06, $06
                       .DB $06, $06, $1E, $03, $1F, $05, $1C, $04
                       .DB $1D, $06, $06, $1A, $04, $1B, $05, $18
                       .DB $19, $06, $1A, $04, $1B, $05, $05, $1C
                       .DB $04, $1D, $06, $1E, $03, $1F, $05, $05
                       .DB $05, $05, $05, $1C, $1D, $1E, $1F, $05
                       .DB $05, $05, $05, $05, $05, $05, $18, $1F
                       .DB $00, $FF, $FF, $FF
; Pattern 3 (phase 3)
```

### T10A8:

```asm
                       .DB $10, $04, $04, $1D, $0D, $0E, $0B, $0C
                       .DB $0D, $0E, $01, $01, $01, $01, $01, $01
                       .DB $01, $01, $05, $05, $05, $05, $05, $1C
                       .DB $04, $04, $1D, $06, $06, $1E, $03, $03
                       .DB $1F, $05, $05, $05, $1C, $11, $12, $13
                       .DB $00, $FF, $FF, $FF
; Pattern 4
```

### T10D4:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E
                       .DB $0B, $0C, $1A, $1B, $05, $18, $19, $06
                       .DB $0D, $0E, $01, $01, $01, $01, $01, $01
                       .DB $01, $01, $05, $05, $1C, $1B, $05, $05
                       .DB $1C, $04, $1B, $05, $05, $1C, $04, $1B
                       .DB $00, $FF, $FF, $FF
; Pattern 5
```

### T1100:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $09, $09
                       .DB $09, $09, $0A, $0A, $09, $09, $0A, $09
                       .DB $16, $17, $14, $07, $07, $07, $1C, $04
                       .DB $1D, $06, $1E, $03, $1F, $05, $1C, $08
                       .DB $08, $08, $08, $08, $08, $08, $08, $05
                       .DB $05, $05, $05, $00, $FF, $FF, $FF, $FF
; Pattern 6
```

### T1130:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $0A, $0A
                       .DB $0A, $0A, $09, $09, $0A, $0A, $09, $0A
                       .DB $12, $13, $10, $08, $08, $08, $18, $07
                       .DB $07, $07, $07, $05, $1C, $04, $1D, $06
                       .DB $1E, $03, $1F, $07, $07, $07, $07, $05
                       .DB $05, $05, $05, $00, $FF, $FF, $FF, $FF
; Pattern 7
```

### T1160:

```asm
                       .DB $1C, $04, $04, $04, $1D, $06, $0D, $0E
                       .DB $0B, $0C, $06, $06, $1E, $15, $16, $17
                       .DB $14, $19, $06, $1A, $04, $1D, $06, $1E
                       .DB $03, $19, $06, $1A, $04, $1D, $1E, $03
                       .DB $1F, $1C, $04, $1B, $05, $18, $03, $1F
                       .DB $05, $1C, $04, $1B, $05, $18, $03, $15
                       .DB $16, $17, $14, $1F, $05, $05, $05, $05
                       .DB $05, $05, $05, $1C, $04, $1D, $1A, $1B
                       .DB $00, $FF, $FF, $FF
; Pattern 8
```

### T11A4:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E
                       .DB $0B, $0C, $0D, $0E, $02, $02, $02, $02
                       .DB $02, $02, $02, $02, $05, $05, $18, $03
                       .DB $19, $1A, $04, $1B, $05, $18, $03, $1F
                       .DB $05, $18, $03, $1F, $05, $05, $18, $1F
                       .DB $00, $FF, $FF, $FF
; Pattern 9
```

### T11D0:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $06, $06
                       .DB $09, $09, $09, $0A, $09, $09, $0A, $09
                       .DB $09, $09, $06, $1A, $04, $11, $12, $13
                       .DB $10, $08, $08, $08, $07, $07, $07, $08
                       .DB $08, $08, $05, $05, $05, $05, $05, $05
                       .DB $05, $05, $05, $05, $05, $00, $FF, $FF
; Pattern 10
```

### T1200:

```asm
                       .DB $1C, $11, $12, $13, $10, $04, $1D, $0D
                       .DB $0E, $0B, $0C, $0D, $0E, $0B, $0C, $1E
                       .DB $1F, $05, $18, $19, $0D, $0E, $0B, $0C
                       .DB $1E, $1F, $05, $05, $05, $05, $05, $18
                       .DB $19, $0D, $0E, $0B, $0C, $06, $1E, $1F
                       .DB $05, $05, $05, $05, $18, $19, $06, $1E
                       .DB $1F, $05, $05, $05, $05, $05, $05, $05
                       .DB $05, $1C, $04, $04, $1D, $1A, $04, $1B
                       .DB $00, $FF, $FF, $FF
; Pattern 11
```

### T1244:

```asm
                       .DB $18, $03, $03, $19, $06, $06, $06, $06
                       .DB $06, $06, $06, $06, $06, $06, $06, $06
                       .DB $1A, $04, $1B, $05, $1C, $04, $1D, $06
                       .DB $1E, $03, $03, $19, $06, $1A, $04, $04
                       .DB $04, $1B, $05, $18, $03, $03, $1F, $05
                       .DB $1C, $04, $1D, $06, $1A, $04, $1B, $05
                       .DB $05, $05, $05, $05, $05, $05, $05, $05
                       .DB $05, $05, $05, $18, $03, $19, $1E, $1F
                       .DB $00, $FF, $FF, $FF
; Pattern 12
```

### T1288:

```asm
                       .DB $0B, $0C, $1A, $1D, $1E, $03, $19, $06
                       .DB $1A, $04, $04, $1D, $06, $1E, $03, $03
                       .DB $03, $19, $06, $06, $1A, $04, $04, $04
                       .DB $04, $1D, $06, $06, $1E, $03, $03, $03
                       .DB $03, $03, $03, $1F, $05, $05, $1C, $04
                       .DB $04, $04, $04, $1B, $05, $05, $18, $03
                       .DB $03, $03, $1F, $05, $1C, $04, $04, $1B
                       .DB $05, $18, $03, $1F, $1C, $1B, $05, $05
                       .DB $00, $FF,
; Pattern 13
```

### T12CA:

```asm
                       .DB $18, $03, $19, $06, $06, $06, $06, $06
                       .DB $06, $1A, $1D, $1E, $19, $1A, $1D, $06
                       .DB $1E, $19, $06, $1E, $15, $16, $17, $14
                       .DB $07, $07, $07, $08, $08, $08, $08, $05
                       .DB $05, $18, $03, $03, $19, $06, $06, $1A
                       .DB $04, $04, $1B, $08, $08, $08, $08, $05
                       .DB $05, $05, $05, $18, $1F, $00
; Pattern 14
```

### T1300:

```asm
                       .DB $0B, $0C, $0A, $0A, $09, $09, $09, $0A
                       .DB $0A, $09, $09, $09, $0A, $09, $09, $16
                       .DB $17, $14, $07, $07, $07, $08, $08, $08
                       .DB $08, $07, $07, $08, $08, $08, $08, $07
                       .DB $08, $11, $12, $13, $00, $FF, $FF, $FF
; Pattern 15
```

### T1328:

```asm
                       .DB $0B, $0C, $09, $09, $0A, $09, $09, $0A
                       .DB $0A, $0A, $0A, $09, $0A, $0A, $0A, $12
                       .DB $13, $10, $04, $04, $04, $1B, $18, $03
                       .DB $03, $07, $07, $08, $08, $07, $07, $08
                       .DB $08, $07, $07, $07, $07, $07, $00, $FF
                       .DB $FF, $FF, $FF, $FF
; Pattern 16
```

### T1354:

```asm
                       .DB $1C, $11, $12, $13, $10, $1D, $0D, $0E
                       .DB $0B, $0C, $09, $0A, $09, $09, $0A, $09
                       .DB $09, $09, $06, $1A, $04, $1B, $05, $18
                       .DB $03, $19, $09, $09, $0D, $0E, $0B, $0C
                       .DB $0D, $0E, $02, $02, $02, $02, $02, $02
                       .DB $02, $02, $02, $02, $02, $02, $08, $07
                       .DB $07, $08, $07, $07, $08, $08, $07, $07
                       .DB $07, $07, $07, $05, $05, $05, $05, $05
                       .DB $05, $1C, $11, $12, $13, $00, $FF, $FF
; Pattern 17
```

### T139C:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E
                       .DB $0B, $0C, $1A, $1D, $06, $1E, $19, $06
                       .DB $06, $1A, $04, $1B, $1C, $04, $1D, $1A
                       .DB $04, $1B, $1C, $04, $1D, $1A, $04, $1B
                       .DB $05, $18, $07, $07, $07, $08, $08, $07
                       .DB $07, $07, $07, $08, $08, $07, $07, $07
                       .DB $07, $00, $FF, $FF
; Pattern 18
```

### T13D0:

```asm
                       .DB $14, $03, $19, $0D, $0E, $0B, $0C, $0A
                       .DB $0A, $0A, $09, $0A, $0A, $0A, $09, $0A
                       .DB $0A, $0A, $06, $1E, $15, $16, $17, $14
                       .DB $03, $1F, $05, $05, $08, $07, $07, $07
                       .DB $08, $07, $07, $07, $08, $08, $05, $05
                       .DB $05, $05, $05, $00, $FF, $FF, $FF, $FF
; Player ship character block shapes table
; used for fine bit shifting of the player
```

### T1400:

```asm
                       .DB $30, $40, $31, $41     ;frame#1
                       .DB $32, $42, $33, $43     ;frame#2
                       .DB $34, $44, $35, $45     ;frame#3
                       .DB $36, $46, $37, $47     ;frame#4
                       .DB $38, $48, $39, $49     ;frame#5
                       .DB $3A, $4A, $3B, $4B     ;frame#6
                       .DB $3C, $4C, $3D, $4D     ;frame#7
                       .DB $3E, $4E, $3F, $4F     ;frame#8

; Alien character block shapes table ($00=SPACE)
```

### T1420:

```asm
                       .DB $60, $61           ;alien shape #1
                       .DB $62, $63           ;#2
                       .DB $64, $65           ;#3
                       .DB $66, $67           ;#4
                       .DB $69, $00           ;#6
                       .DB $69, $00           ;#6
                       .DB $7A, $7B           ;#28
                       .DB $7A, $7B           ;#28
                       .DB $6B, $00           ;#8
                       .DB $6B, $00           ;#8
                       .DB $8C, $8D           ;#29
                       .DB $8C, $8D           ;#29
                       .DB $68, $00           ;#5
                       .DB $68, $00           ;#5
                       .DB $8A, $9A           ;#30
                       .DB $8A, $9A           ;#30
                       .DB $6A, $00           ;#7
                       .DB $6A, $00           ;#7
                       .DB $8B, $9B           ;#31
                       .DB $8B, $9B           ;#31
                       .DB $68, $00           ;#5
                       .DB $6B, $00           ;#8
                       .DB $6A, $00           ;#7
                       .DB $69, $00           ;#6
                       .DB $76, $77           ;#18
                       .DB $74, $75           ;#19
                       .DB $72, $73           ;#16
                       .DB $70, $71           ;#17
                       .DB $68, $00           ;#5
                       .DB $86, $96           ;#22
                       .DB $69, $00           ;#6
                       .DB $87, $97           ;#21
                       .DB $6A, $00           ;#7
                       .DB $88, $98           ;#20
                       .DB $6B, $00           ;#8
                       .DB $89, $99           ;#23
                       .DB $68, $00           ;#5
                       .DB $00, $00
                       .DB $A2, $B2, $A3, $B3 ;#26
                       .DB $69, $00           ;#6
                       .DB $00, $00
                       .DB $A4, $B4, $A5, $B5 ;#25
                       .DB $6A, $00           ;#7
                       .DB $00, $00
                       .DB $A6, $B6, $A7, $B7 ;#24
                       .DB $6B, $00           ;#8
                       .DB $00, $00
                       .DB $A8, $B8, $A9, $B9 ;#27
                       .DB $FF, $FF, $FF, $FF
                       .DB $8A, $9A           ;#30
                       .DB $00, $00
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
                       .DB $8B, $9B           ;#31
                       .DB $00, $00
                       .DB $FF, $FF, $FF, $FF
                       .DB $8E, $9E, $8F, $9F ;#14
                       .DB $A0, $B0, $A1, $B1 ;#15
                       .DB $00, $00, $00, $00
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
                       .DB $9C, $00           ;#32
                       .DB $00, $00
                       .DB $84, $94, $85, $95 ;#36
                       .DB $82, $92, $83, $93 ;#35
                       .DB $80, $90, $81, $91 ;#34
                       .DB $9D, $00, $00, $00 ;#33
                       .DB $AE, $BE, $AF, $BF ;#39
                       .DB $AC, $BC, $AD, $00 ;#38
                       .DB $AA, $BA, $AB, $BB ;#37

;*****************************************************************************
;* Coin-text fixup, run after each character of the '$18xx' text is printed.
;* If the coinage DIP bit is set, three positions in the "INSERT COIN"
;* block are overwritten with alternate glyphs, otherwise the text is
;* left as printed.
;* In:  A = printed char, HL = source text ptr ($18xx), DE = screen addr.
;* The quirky flag trick:
;* Notice the routine writes to the screen before it tests the match
;* (`LD (HL),$22` sits before `RET Z`). Because `LD (HL),n` doesn't touch the flags,
;* the `RET Z` still reflects the preceding `CP`. So on a non match
;* the "wrong" byte is written but then immediately corrected by the next `LD (HL),...`
;* (and ultimately by `LD (HL),B` at `$14FC`). It's a code size optimization:
;* only the last write that is followed by a taken `RET Z` actually sticks.
;*****************************************************************************
```

### L14E0:

```asm
                       LD      B,A                 ; save the printed character
                       LD      A,(DSW0)            ; 78xx DSW0 (DIP switches)
                       AND     $10                 ; 0001_0000 Coinage
                       RET     Z                   ; coinage bit clear -> keep text as-is
                       EX      DE,HL               ; HL = screen addr, DE = source text ptr
                       LD      A,D                 ; source MSB
                       CP      $18                 ; is this the $18xx text block ?
                       RET     NZ                  ; if not, leave it alone
                       LD      A,E                 ; source LSB (position within text)
                       CP      $95                 ; position $1895 ?
                       LD      (HL),$22            ; overwrite screen char with $22: "2"
                       RET     Z                   ; ...and done if it was $1895
                       CP      $9A                 ; position $189A ?
                       LD      (HL),$13            ; overwrite with $13: "S"
                       RET     Z                   ; ...done if $189A
                       CP      $B5                 ; position $18B5 ?
                       LD      (HL),$24            ; overwrite with $24: "4"
                       RET     Z                   ; ...done if $18B5
                       LD      (HL),B              ; otherwise restore the original character
                       RET                         ;

                       .ORG $1500
; Copied inside $4B70-$4BAF.
; Init values for the alien control states A and B.
```

### T1500:

```asm
                       .DB $08, $6C, $09, $60
                       .DB $08, $6C, $09, $60
                       .DB $08, $6C, $09, $60
                       .DB $08, $6C, $09, $60
                       .DB $08, $6C, $09, $60
                       .DB $08, $6C, $09, $60
                       .DB $08, $6C, $09, $60
                       .DB $09, $60, $09, $60
; Init values for 16 aliens.
; Pointer to alien movement pattern table.
```

### T1520:

```asm
                       .MSFIRST
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
                       .DW T1000
; Level 2 initial screen coordinates for the aliens.
; First byte is X, 2nd byte is Y. There are 16 aliens
; on the level (numbered here 0 - F). The starts are shown
; on the screen below.
;
;      0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 9 9 A A B B C C
;      0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8
;      | | | | | | | | | | | | | | | | | | | | | | | | | |
; 00 - . S C O R E 1 . . H I - S C O R E . . S C O R E 2 .
; 08 - . 0 0 0 0 0 0 . . . 0 0 0 0 0 0 . . . 0 0 0 0 0 0 .
; 10 - . . . * 1 . . . . . C O I N 0 0 . . . . . * 0 . . .
; 18 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 20 - . . . . . . . . . . 0 . . . 1 . . . . . . . . . . .
; 28 - . . . . . . . . . . . . 2 . . . . . . . . . . . . .
; 30 - . . . . . . 8 . . . . . . . . . . . 9 . . . . . . .
; 38 - . . . . A . . . 6 . . . 3 . . . 7 . . . B . . . . .
; 40 - . . . . . . . . . . 4 . . . 5 . . . . . . . . . . .
; 48 - . . . C . . . . . . . . E . . . . . . . . D . . . .
; 50 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 58 - . . . . . . . . . . . . F . . . . . . . . . . . . .
;
```

### T1540:

```asm
                       .DB $50, $20     ; 0 : x,y = 50,20 (decimal 80,32)
                       .DB $70, $20     ; 1
                       .DB $60, $28     ; 2
                       .DB $60, $38     ; 3
                       .DB $50, $40     ; 4
                       .DB $70, $40     ; 5
                       .DB $40, $38     ; 6
                       .DB $80, $38     ; 7
                       .DB $30, $30     ; 8
                       .DB $90, $30     ; 9
                       .DB $20, $38     ; A
                       .DB $A0, $38     ; B
                       .DB $18, $48     ; C
                       .DB $A8, $48     ; D
                       .DB $60, $48     ; E
                       .DB $60, $58     ; F

; Level 1 initial screen coordinates for the aliens.
; Same structure as 1540 above.
;
;      0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 9 9 A A B B C C
;      0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8
;      | | | | | | | | | | | | | | | | | | | | | | | | | |
; 00 - . S C O R E 1 . . H I - S C O R E . . S C O R E 2 .
; 08 - . 0 0 0 0 0 0 . . . 0 0 0 0 0 0 . . . 0 0 0 0 0 0 .
; 10 - . . . * 1 . . . . . C O I N 0 0 . . . . . * 0 . . .
; 18 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 20 - . . . . . . . E . . . . . . . . . F . . . . . . . .
; 28 - . . . . . C . . . . . . . . . . . . . D . . . . . .
; 30 - . . . A . . . . . . . . . . . . . . . . . B . . . .
; 38 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 40 - . . . 8 . . . . . . . . . . . . . . . . . 9 . . . .
; 48 - . . . . . 6 . . . . . . 0 . . . . . . 7 . . . . . .
; 50 - . . . . . . . 4 . . . . . . . . . 5 . . . . . . . .
; 58 - . . . . . . . . . 2 . . 1 . . 3 . . . . . . . . . .
;
```

### T1560:

```asm
                       .DB $60, $48     ; 0
                       .DB $60, $58     ; 1
                       .DB $48, $58     ; 2
                       .DB $78, $58     ; 3
                       .DB $38, $50     ; 4
                       .DB $88, $50     ; 5
                       .DB $28, $48     ; 6
                       .DB $98, $48     ; 7
                       .DB $18, $40     ; 8
                       .DB $A8, $40     ; 9
                       .DB $18, $30     ; A
                       .DB $A8, $30     ; B
                       .DB $28, $28     ; C
                       .DB $98, $28     ; D
                       .DB $38, $20     ; E
                       .DB $88, $20     ; F

;level 10 initial screen coordinates for the aliens.
;      0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 9 9 A A B B C C
;      0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8
;      | | | | | | | | | | | | | | | | | | | | | | | | | |
; 20 - . . . . . . . . . . 1 . 0 . 2 . . . . . . . . . . .
; 28 - . . . . . . . . 3 . . . . . . . 4 . . . . . . . . .
; 30 - . . . . . . 5 . . . . . . . . . . . 6 . . . . . . .
; 38 - . . . . 7 . . . . . . . . . . . . . . . 8 . . . . .
; 40 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 48 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 50 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 58 - . . . . . . E . C . A . 9 . B . D . F . . . . . . .
;
```

### T1580:

```asm
                       .DB $60, $20     ; 0
                       .DB $50, $20     ; 1
                       .DB $70, $20     ; 2
                       .DB $40, $28     ; 3
                       .DB $80, $28     ; 4
                       .DB $30, $30     ; 5
                       .DB $90, $30     ; 6
                       .DB $20, $38     ; 7
                       .DB $A0, $38     ; 8
                       .DB $60, $58     ; 9
                       .DB $50, $58     ; A
                       .DB $70, $58     ; B
                       .DB $40, $58     ; C
                       .DB $80, $58     ; D
                       .DB $30, $58     ; E
                       .DB $90, $58     ; F

;level 7 initial screen coordinates for the aliens.
;      0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 9 9 A A B B C C
;      0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8
;      | | | | | | | | | | | | | | | | | | | | | | | | | |
; 20 - . . . . . . . . . . . . 0 . . . . . . . . . . . . .
; 28 - . . . . . . . . . . 1 . . . 2 . . . . . . . . . . .
; 30 - . . . . . . . . 3 . . . . . . . 4 . . . . . . . . .
; 38 - . . . . . . 5 . . . . . . . . . . . 6 . . . . . . .
; 40 - . . . . 7 . . . . . . . . . . . . . . . 8 . . . . .
; 48 - . . . . . . E . . . . . . . . . . . F . . . . . . .
; 50 - . . . . . . . . C . . . . . . . D . . . . . . . . .
; 58 - . . . . . . . . . . A . 9 . B . . . . . . . . . . .
;
```

### T15A0:

```asm
                       .DB $60, $20     ; 0
                       .DB $50, $28     ; 1
                       .DB $70, $28     ; 2
                       .DB $40, $30     ; 3
                       .DB $80, $30     ; 4
                       .DB $30, $38     ; 5
                       .DB $90, $38     ; 6
                       .DB $20, $40     ; 7
                       .DB $A0, $40     ; 8
                       .DB $60, $58     ; 9
                       .DB $50, $58     ; A
                       .DB $70, $58     ; B
                       .DB $40, $50     ; C
                       .DB $80, $50     ; D
                       .DB $30, $48     ; E
                       .DB $90, $48     ; F

;level 6 initial screen coordinates for the aliens.
;      0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 9 9 A A B B C C
;      0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8
;      | | | | | | | | | | | | | | | | | | | | | | | | | |
; 20 - . . E . . . . . . . . . . . . . . . . . . . F . . .
; 28 - . . . . C . . . . . . . . . . . . . . . D . . . . .
; 30 - . . . . . . A . . . . . . . . . . . B . . . . . . .
; 38 - . . . . . . . . 8 . . . . . . . 9 . . . . . . . . .
; 40 - . . . . . . . . . . 6 . . . 7 . . . . . . . . . . .
; 48 - . . . . . . . . 4 . . . 3 . . . 5 . . . . . . . . .
; 50 - . . . . . . . . . . 1 . . . 2 . . . . . . . . . . .
; 58 - . . . . . . . . . . . . 0 . . . . . . . . . . . . .
;
```

### T15C0:

```asm
                       .DB $60, $58     ; 0
                       .DB $50, $50     ; 1
                       .DB $70, $50     ; 2
                       .DB $60, $48     ; 3
                       .DB $40, $48     ; 4
                       .DB $80, $48     ; 5
                       .DB $50, $40     ; 6
                       .DB $70, $40     ; 7
                       .DB $40, $38     ; 8
                       .DB $80, $38     ; 9
                       .DB $30, $30     ; A
                       .DB $90, $30     ; B
                       .DB $20, $28     ; C
                       .DB $A0, $28     ; D
                       .DB $10, $20     ; E
                       .DB $B0, $20     ; F

;level 5 initial screen coordinates for the aliens.
;      0 0 1 1 2 2 3 3 4 4 5 5 6 6 7 7 8 8 9 9 A A B B C C
;      0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8 0 8
;      | | | | | | | | | | | | | | | | | | | | | | | | | |
; 20 - . . . . . . . . . . . . 0 . . . . . . . . . . . . .
; 28 - . . . . . . . . . . 1 . . . 2 . . . . . . . . . . .
; 30 - . . . . . . . . 3 . . . . . . . 4 . . . . . . . . .
; 38 - . . . . . . 5 . . . . . . . . . . . 6 . . . . . . .
; 40 - . . . . 7 . . . . . . . . . . . . . . . 8 . . . . .
; 48 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 50 - . . . . . . . . . . . . . . . . . . . . . . . . . .
; 58 - . . . . . . . . . . . . . . . . . . . . . . . . . .
```

### T15E0:

```asm
                       .DB $60, $20     ; 0
                       .DB $50, $28     ; 1
                       .DB $70, $28     ; 2
                       .DB $40, $30     ; 3
                       .DB $80, $30     ; 4
                       .DB $30, $38     ; 5
                       .DB $90, $38     ; 6
                       .DB $20, $40     ; 7
                       .DB $A0, $40     ; 8
                       .DB $60, $20     ; 9 (two aliens at same position)
                       .DB $50, $28     ; A (two aliens at same position)
                       .DB $70, $28     ; B (two aliens at same position)
                       .DB $40, $30     ; C (two aliens at same position)
                       .DB $80, $30     ; D (two aliens at same position)
                       .DB $30, $38     ; E (two aliens at same position)
                       .DB $90, $38     ; F (two aliens at same position)

; Pointer table for character block shapes table (T14xx):
```

### T1600:

```asm
                       .DB $10, $14, $18, $1C ; to player ship frame #5, #6, #7, #8
                       .DB $00, $04, $08, $0C ; to player ship frame #1, #2, #3, #4
                       .DB $20, $22, $24, $26 ; to alien shape #1, #2, #3, #4
                       .DB $28, $2A, $2C, $2E ; to alien shape #6, #6, #28, #28
                       .DB $30, $32, $34, $36 ; to alien shape #8, #8, #29, #29
                       .DB $38, $3A, $3C, $3E ; to alien shape #5, #5, #30, #30
                       .DB $40, $42, $44, $46 ; to alien shape #7, #7, #31, #31
                       .DB $5C, $5C, $5E, $5E ; to alien shape #6, #6, #21, #21

; 8 player bullets for the fine bit shifting
; Foreground tiles (no pointer).
```

### T1620:

```asm
                       .DB $50, $51, $52, $53, $54, $55, $56, $57
;
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF

; Pointer table for character block shapes table (T14xx):
                       .DB $48, $48, $50, $50, $4A, $4A, $52, $52, $4C, $4C, $54, $54, $4E, $4E, $56, $56
                       .DB $48, $48, $56, $56, $4E, $4E, $54, $54, $4C, $4C, $52, $52, $4A, $4A, $50, $50
                       .DB $68, $68, $6C, $6C, $70, $70, $74, $74, $78, $78, $7C, $7C, $80, $80, $84, $84
                       .DB $68, $68, $84, $84, $80, $80, $7C, $7C, $78, $78, $74, $74, $70, $70, $6C, $6C
                       .DB $58, $58, $5A, $5A, $5C, $5C, $5E, $5E, $60, $60, $62, $62, $64, $64, $66, $66
                       .DB $78
                       .DB $FF
                       .DB $A0
                       .DB $FF, $FF
                       .DB $A8
                       .DB $FF
                       .DB $AC, $C0
                       .DB $FF
                       .DB $C8
                       .DB $FF, $FF
                       .DB $C4
                       .DB $FF
                       .DB $CC, $D0
                       .DB $FF
                       .DB $D8
                       .DB $FF, $FF
                       .DB $D4
                       .DB $FF
                       .DB $DC
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
;?
                       .DB $01, $02, $08
                       .DB $01, $02, $08
                       .DB $01, $02, $0C
                       .DB $01, $02, $10
                       .DB $03, $04, $14
                       .DB $03, $04, $18
                       .DB $04, $01, $88
                       .DB $04, $01, $90
                       .DB $04, $01, $80
                       .DB $04, $01, $80
                       .DB $03, $04, $70
                       .DB $03, $04, $74
                       .DB $03, $04, $78
                       .DB $03, $04, $7C
                       .DB $FF, $FF, $FF
;?
                       .DB $01, $02, $30
                       .DB $01, $02, $34
                       .DB $01, $02, $38
                       .DB $01, $02, $3C
                       .DB $01, $02, $40
                       .DB $01, $02, $44
                       .DB $01, $02, $48
                       .DB $01, $02, $4C
                       .DB $04, $04, $50
                       .DB $04, $04, $54
                       .DB $04, $04, $58
                       .DB $04, $04, $5C
                       .DB $04, $04, $60
                       .DB $04, $04, $64
                       .DB $04, $04, $68
                       .DB $04, $04, $6C

; Alien movement direction table.
; Positive or negative offset for X and Y.
```

### T1700:

```asm
                       .DB $FF, $FF, $01, $00, $FF, $00, $04, $00, $FC, $00, $00, $FC, $00, $04, $04, $FE ;
                       .DB $FC, $FE, $04, $02, $FC, $02, $00, $04, $00, $04, $00, $04, $00, $04, $FF, $FF ;
                       .DB $FC, $00, $FC, $00, $FC, $00, $FC, $00, $04, $00, $04, $00, $04, $00, $04, $00 ;
                       .DB $04, $FC, $04, $04, $FC, $04, $FC, $FC, $FC, $FC, $FC, $04, $04, $04, $04, $FC ;

; Per-tile hit-window + X-offset table for in-formation aliens:
; Lookup table used in the player-bullet vs. alien collision routine `L0E10`,
; specifically for aliens that are still sitting in the base formation.
; Indexed by the alien tile's character type.
; How the index is formed:
; In `L0E10`, the code reads the character drawn under the bullet.
; After rejecting explosion parts (`≥$C0`), empty cells (`<$60`), and out-of-formation aliens (`≥$68` -> handled by `L0E39`),
; it's left with in-formation foreground tiles `$60`–`$67`.
; Meaning of the 4 bytes:
; Byte 0 — upper bound of the horizontal hit window (`$0E31`): `bulletX & 7` must be < byte 0, else `RET NC` (miss).
; Byte 1 — lower bound of the hit window (`$0E34`): `bulletX & 7` must be >= byte 1, else `RET C` (miss).
;          So bytes 0/1 define the `[byte1, byte0)` pixel-column range inside that 8-pixel tile where the alien graphic is actually solid.
;          (E.g. type 0 = full width `[0,8)`; type 1 = only column 0; type 2 = columns `[1,8)`.)
; Byte 2 — signed X correction (`$0E70`/`L0E70`): added to the bullet's cell-aligned X to reconstruct the screen X of the hit target,
;          which is then used to locate the matching alien object in the alien control table at `M4B70`.
;          Because a formation alien is drawn from several tiles, byte 2 shifts the coordinate from the tile that was hit
;          back to the alien's anchor X, so the correct alien object is found and killed.
; Byte 3 — `$FF`, unused padding.
```

### T1740:

```asm
                       .DB $08, $00, $00, $FF, $01, $00, $F8, $FF, $08, $01, $02, $FF, $04, $00, $FA, $FF ;
                       .DB $08, $01, $04, $FF, $08, $00, $FC, $FF, $08, $05, $06, $FF, $08, $00, $FE, $FF ;

; Parity table and initial number of aliens/birds for levels:
; odd, odd, even (P), even (P), odd, odd, odd, odd
; used with $43B8 LevelAndRound.
```

### T1760:

```asm
                       .DB $10, $10, $88, $88, $10, $10, $10, $10 ;
;
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF ;

```

### T1770:

```asm
                       .DB $EC, $FC, $FD, $F4, $ED, $30, $40, $F5, $EE, $31, $41, $F6, $EF, $FF, $FE, $F7 ; Object 1770 Regular ship, large shields
                       .DB $E8, $F8, $F9, $F0, $E9, $30, $40, $F1, $EA, $31, $41, $F2, $EB, $FB, $FA, $F3 ; Object 1780 Regular ship, small shields
                       .DB $E8, $F8, $F9, $F0, $E9, $E4, $E6, $F1, $EA, $E5, $E7, $F2, $EB, $FB, $FA, $F3 ; Object 1790 Green ship, large shields
                       .DB $00, $00, $00, $00, $00, $E4, $E6, $00, $00, $E5, $E7, $00, $00, $00, $00, $00 ; Object 17A0 Green ship, no shields

;
                       .DB $F0, $CA, $C4, $BE, $B8, $BE, $B8, $BE ; LSB's of the Alien explosion frame sequence (#5,#4,#3,#2,#1,#2,#1,#2) why wrong order?
;
                       .DB $C8, $D8, $C9, $D9, $CA, $DA ; Object 17B8 3x2 Alien explosion frame #1
                       .DB $CB, $DB, $CC, $DC, $CD, $DD ; Object 17BE 3x2 Alien explosion frame #2
                       .DB $C0, $C1, $C1, $C2, $00, $C0 ; Object 17C4 3x2 Alien explosion frame #3
                       .DB $00, $00, $00, $C3, $00, $00 ; Object 17CA 3x2 Alien explosion frame #4
;
```

### T17D0:

```asm
                       .DB $C4, $D4, $C5, $D5, $C3, $C3 ; Object 17D0 3x2 Bonus explosion left part
```

### T17D6:

```asm
                       .DB $C3, $C3, $C6, $D6, $C7, $D7 ; Object 17D6 3x2 Bonus explosion right part

```
> [!NOTE]
> **Ported to C:** [`coin_checking`](../attract_mode.c#L281) in `attract_mode.c` (ASM: `17E0-17ED`)

```asm
                       .ORG $17E0
;
```

### CoinChecking:

```asm
                       LD      A,(DSW0)            ; 78xx DSW0
                       AND     $10                 ; Coinage
                       LD      A,(CoinCount)       ; 
                       RET     Z                   
                       RRCA                        
                       AND     $0F                 
                       RET                         

                       .ORG $17F0
; Used for blank out characters
; and Alien explosion frame #5
```

### FourByFourEmpty:

```asm
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

;*****************************************************************************
; ic48
;*****************************************************************************
; Screen ram adresses and static texts using setA
```

### T1800:

```asm
                       .DB $43, $20
                       .DB $FF, $FF, $FF, $FF
; " SCORE1  HI-SCORE  SCORE2 "
                       .DB $00, $13, $03, $0F, $12, $05, $21, $00, $00, $08, $09, $2B, $13, $03, $0F, $12, $05, $00, $00, $13, $03, $0F, $12, $05, $22, $00

                       .DB $43, $21
                       .DB $FF, $FF, $FF, $FF
; " 000000   000000   000000 "
                       .DB $00, $20, $20, $20, $20, $20, $20, $00, $00, $00, $20, $20, $20, $20, $20, $20, $00, $00, $00, $20, $20, $20, $20, $20, $20, $00

                       .DB $43, $22
                       .DB $FF, $FF, $FF, $FF
; "   %0     COIN00     %0   "
                       .DB $00, $00, $00, $7F, $20, $00, $00, $00, $00, $00, $03, $0F, $09, $0E, $20, $20, $00, $00, $00, $00, $00, $7F, $20, $00, $00, $00

```

### T1860:

```asm
                       .DB $43, $25
                       .DB $FF, $FF, $FF, $FF
; "       INSERT  COIN       "
                       .DB $00, $00, $00, $00, $00, $00, $00, $09, $0E, $13, $05, $12, $14, $00, $00, $03, $0F, $09, $0E, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $27
                       .DB $FF, $FF, $FF, $FF
; "   * 1PLAYER   1COIN  *   "
                       .DB $00, $00, $00, $1F, $00, $21, $10, $0C, $01, $19, $05, $12, $00, $00, $00, $21, $03, $0F, $09, $0E, $00, $00, $1F, $00, $00, $00

                       .DB $43, $29
                       .DB $FF, $FF, $FF, $FF
; "   * 2PLAYERS  2COINS *   "
                       .DB $00, $00, $00, $1F, $00, $22, $10, $0C, $01, $19, $05, $12, $13, $00, $00, $22, $03, $0F, $09, $0E, $13, $00, $1F, $00, $00, $00

                       .DB $43, $2E
                       .DB $FF, $FF, $FF, $FF
; "   SCORE AVERAGE TABLE    "
                       .DB $00, $00, $00, $13, $03, $0F, $12, $05, $00, $01, $16, $05, $12, $01, $07, $05, $00, $14, $01, $02, $0C, $05, $00, $00, $00, $00

                       .DB $43, $30
                       .DB $FF, $FF, $FF, $FF
; "        20 40 80          "
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $22, $20, $00, $24, $20, $00, $28, $20, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $33
                       .DB $FF, $FF, $FF, $FF
; "        200               "
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $22, $20, $20, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $36
                       .DB $FF, $FF, $FF, $FF
; "        50 100 ?[100-800] "
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $25, $20, $00, $21, $20, $20, $00, $2F, $1B, $21, $20, $20, $2B, $28, $20, $20, $1C, $00

                       .DB $43, $39
                       .DB $FF, $FF, $FF, $FF
; "        1000-9000         "
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $21, $20, $20, $20, $2B, $29, $20, $20, $20, $00, $00, $00, $00, $00, $00, $00, $00, $00

```

### T1960:

```asm
                       .DB $43, $3C
                       .DB $00, $00, $32, $21
; "PHOENIX% COPYRIGHT 1980   "
                       .DB $10, $08, $0F, $05, $0E, $09, $18, $7E, $00, $03, $0F, $10, $19, $12, $09, $07, $08, $14, $00, $21, $29, $28, $20, $00, $00, $00

                       .DB $43, $3D
                       .DB $02, $05, $21, $28
; " AMSTAR ELECTRONICS CORP. "
                       .DB $00, $01, $0D, $13, $14, $01
```

### L198C:

```asm
                       .DB $12, $00, $05, $0C, $05, $03, $14, $12, $0F, $0E, $09, $03, $13, $00, $03, $0F, $12, $10, $2A, $00

                       .DB $43, $3E
                       .DB $FF, $FF, $FF, $FF
; "  PHOENIX AZ. U.S.A.      "
                       .DB $00, $00, $10, $08, $0F, $05, $0E, $09, $18, $00, $01, $1A, $2A, $00, $15, $2A, $13, $2A, $01, $2A, $00, $00, $00, $00, $00, $00

```

### T19C0:

```asm
                       .DB $43, $28
                       .DB $FF, $FF, $FF, $FF
; "           PUSH           "
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $10, $15, $13, $08, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $2C
                       .DB $FF, $FF, $FF, $FF
; "    ONLY 1PLAYER BUTTON   "
                       .DB $00, $00, $00, $00, $0F, $0E, $0C, $19, $00, $21, $10, $0C, $01, $19, $05, $12, $00, $02, $15, $14, $14, $0F, $0E, $00, $00, $00

```

### T1A00:

```asm
                       .DB $43, $28
                       .DB $FF, $FF, $FF, $FF
; "        GAME  OVER        "
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $07, $01, $0D, $05, $00, $00, $0F, $16, $05, $12, $00, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $28
                       .DB $00, $FF, $FF, $FF
; "%%%%%%%%                %%"
                       .DB $64, $65, $64, $65, $64, $65, $60, $61, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $78, $79

                       .DB $43, $29
                       .DB $FF, $FF, $FF, $FF
; "%%    %%                %%"
                       .DB $64, $65, $00, $00, $00, $00, $64, $65, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $7C, $7D

                       .DB $43, $2A
                       .DB $FF, $FF, $FF, $FF
; "%%%%%%%%                  "
                       .DB $64, $65, $64, $65, $64, $65, $60, $61, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $2B
                       .DB $FF, $FF, $FF, $FF
; "%%                        "
                       .DB $64, $65, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

                       .DB $43, $2C
                       .DB $FF, $FF, $FF, $FF
; "%% % % %%% %%% %% % % %  %"
                       .DB $64, $65, $00, $68, $00, $68, $00, $68, $68, $68, $00, $68, $64, $65, $00, $62, $63, $00, $68, $00, $68, $00, $68, $00, $00, $68

                       .DB $43, $2D
                       .DB $FF, $FF, $FF, $FF
; "%% % % % % %   %% % % %%%%"
                       .DB $64, $65, $00, $68, $00, $68, $00, $68, $00, $68, $00, $68, $00, $00, $00, $68, $9D, $00, $68, $00, $68, $00, $76, $77, $70, $71

                       .DB $43, $2E
                       .DB $FF, $FF, $FF, $FF
; "%% %%% % % %%% %%%% %  %% "
                       .DB $64, $65, $00, $68, $68, $68, $00, $68, $00, $68, $00, $68, $62, $63, $00, $68, $76, $77, $68, $00, $68, $00, $00, $64, $65, $00

                       .DB $43, $2F
                       .DB $00, $00, $00, $00
; "%% % % % % %   % %% % %%%%"
                       .DB $64, $65, $00, $68, $00, $68, $00, $68, $00, $68, $00, $68, $00, $00, $00, $68, $00, $9D, $68, $00, $68, $00, $74, $75, $72, $73

                       .DB $43, $30
                       .DB $FF, $FF, $FF, $FF
; "%% % % %%% %%% % %% % %  %"
                       .DB $64, $65, $00, $68, $00, $68, $00, $68, $68, $68, $00, $68, $64, $65, $00, $68, $00, $66, $67, $00, $68, $00, $68, $00, $00, $68

; Character block shapes table using setB.
; Parts of the mothership's purple conveyor belt.
; So an ordinary belt hit:
; 1. Consumes the bullet (`AND $F7`).
; 2. Sets the "mother-ship hit" flag `$4366` -> plays the hit sound; no score is awarded.
; 3. Swaps the hit tile for a "damaged" belt tile from `T1B40/T1B48/T1B50`,
;    chosen by the bullet's X position (left/right half) and the tile's low nibble
;     — so the belt visibly chips/breaks apart where you shoot it.
```

### T1B40:

```asm
                       .DB $6C
                       .DB $6D
                       .DB $6E
                       .DB $6F

                       .ORG $1B48
; Replacement tiles
```

### T1B48:

```asm
                       .DB $6C, $6D, $6E, $6F, $64, $65, $66, $67, $63, $FF
                       .DB $63, $61, $67, $FF
                       .DB $67, $65, $6B, $FF
                       .DB $6B, $69, $6F, $FF
                       .DB $6F, $6D

;characters used for explosions using setB
```

### T1B60:

```asm
                       .DB $80, $83, $83, $85, $81, $8C, $8C, $86, $81, $8C, $8C, $86, $82, $84, $84, $87
                       .DB $00, $89, $89, $00, $88, $8D, $8D, $8B, $88, $8D, $8D, $8B, $00, $8A, $8A, $00
                       .DB $00, $00, $00, $00, $00, $80, $85, $00, $00, $82, $87, $00, $00, $00, $00, $00

;adress table for instumentation of explosion
```

### T1B90:

```asm
                       .DB $1B, $80
                       .DB $1B, $70
                       .DB $1B, $60
                       .DB $1B, $70
                       .DB $17, $F0                         ;for deletion
                       .DB $17, $F0                         ;
                       .DB $17, $F0                         ;
                       .DB $17, $F0                         ;

;characters using setA: '1 OR 2 PLAYERS BUTTON'
```

### T1BA0:

```asm
                       .DB $43, $2C                         ; screen ram position
                       .DB $00, $00, $00, $00, $00, $00, $00, $21, $00, $0F, $12, $00, $22, $10
                       .DB $0C, $01, $19, $05, $12, $13, $00, $02, $15, $14, $14, $0F, $0E, $00, $00, $00

;characters using setB for animation of the mothership's
;.....antenna animation and the
;...........alien pilot animation
```

### T1BC0:

```asm
                       .DB $41, $54, $76, $7E   ; frame 0
                       .DB $42, $55, $77, $7F   ;
                       .DB $41, $56, $74, $7C   ; frame 1
                       .DB $42, $57, $75, $7D   ;
                       .DB $44, $51, $72, $7A   ; frame 2
                       .DB $45, $52, $73, $7B   ;
                       .DB $46, $51, $70, $78   ; frame 3
                       .DB $47, $52, $71, $79   ;
                       .DB $41, $51, $70, $78   ; frame 4
                       .DB $42, $52, $71, $79   ;
                       .DB $41, $51, $72, $7A   ; frame 5
                       .DB $42, $52, $73, $7B   ;
                       .DB $41, $51, $74, $7C   ; frame 6
                       .DB $42, $52, $75, $7D   ;
                       .DB $41, $51, $76, $7E   ; frame 7
                       .DB $42, $52, $77, $7F   ;

;part of the starfield (without planets) using setB
; This is a 20x9 tile image used to erase the mothership
```

### T1C00:

```asm
                       .DB $00, $01, $00, $06, $00, $02, $03, $04, $00, $01, $00, $08, $00, $02, $03, $04, $00, $00, $07, $00
                       .DB $01, $02, $00, $09, $00, $03, $04, $00, $00, $03, $04, $00, $00, $01, $00, $02, $00, $03, $0A, $00
                       .DB $04, $00, $00, $01, $02, $00, $06, $00, $03, $04, $00, $00, $01, $00, $02, $00, $03, $00, $04, $00
                       .DB $03, $05, $00, $00, $00, $00, $07, $00, $01, $00, $02, $00, $00, $05, $00, $00, $03, $00, $04, $01
                       .DB $02, $00, $03, $00, $08, $04, $00, $01, $02, $06, $00, $03, $00, $04, $00, $02, $01, $02, $03, $00
                       .DB $05, $00, $00, $04, $00, $01, $02, $00, $00, $03, $04, $0B, $00, $01, $00, $02, $00, $03, $00, $00
                       .DB $04, $00, $00, $09, $00, $00, $02, $00, $07, $00, $00, $01, $00, $00, $02, $00, $00, $03, $00, $08
                       .DB $04, $00, $01, $00, $00, $06, $00, $01, $00, $02, $00, $01, $03, $04, $01, $03, $01, $02, $03, $04
                       .DB $00, $05, $00, $01, $02, $00, $09, $00, $03, $04, $00, $01, $00, $01, $02, $03, $04, $00, $02, $00

; Tail of the star field tile pattern that occupies page `$1C` (`$1C00`–`$1CFF`).
; It's the remaining 76 bytes that complete the 256 byte star page used to paint the whole background.
                       .DB $00, $01, $02, $00, $03, $04, $00, $06, $00, $00, $01, $00
                       .DB $00, $01, $02, $00, $05, $00, $00, $03, $00, $04, $00, $07, $00, $01, $00, $02
                       .DB $00, $00, $03, $00, $04, $00, $04, $00, $0A, $00, $01, $00, $02, $00, $03, $00
                       .DB $01, $00, $07, $00, $02, $00, $03, $04, $00, $05, $00, $01, $00, $02, $00, $00
                       .DB $08, $03, $04, $00, $01, $00, $02, $00, $03, $00, $04, $00, $00, $06, $00, $03

; Mother ship object 26x9 tiles (upside down)
; Object 1D00
; Maybe these are upside down because the mother ship scrolls down from the top
; of the screen. The rows appear in the order given here.
```

### T1D00:

```asm
                       .DB $0C, $0D, $0C, $0F, $07, $07, $01, $00, $00, $4C, $4D, $4E, $4F, $4F, $4E, $4D, $4C, $00, $00, $1F, $0E, $06, $0D, $01, $0E, $05
                       .DB $08, $0C, $0E, $0C, $0A, $00, $00, $4D, $4F, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $4F, $4D, $00, $00, $06, $0B, $0D, $08, $0E
                       .DB $03, $02, $00, $01, $00, $4C, $4F, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $4F, $4C, $00, $09, $07, $0A, $03
                       .DB $04, $00, $0A, $00, $4D, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $4D, $00, $00, $0E, $0F
                       .DB $08, $08, $00, $5C, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $5D, $00, $01, $02
                       .DB $02, $06, $01, $00, $00, $00, $58, $59, $5A, $5B, $5B, $5B, $7E, $7F, $5B, $5B, $5B, $4A, $49, $48, $00, $00, $00, $03, $0E, $0B
                       .DB $0D, $05, $04, $05, $0A, $08, $00, $00, $58, $59, $5A, $4B, $76, $77, $4B, $4A, $49, $48, $00, $00, $01, $03, $0F, $02, $03, $00
                       .DB $00, $03, $03, $07, $02, $0A, $03, $07, $00, $00, $58, $50, $51, $52, $53, $48, $00, $00, $0B, $01, $02, $03, $0F, $0E, $0C, $02
                       .DB $05, $0C, $06, $00, $04, $06, $07, $0E, $0F, $09, $00, $40, $41, $42, $43, $00, $07, $03, $0A, $08, $0D, $00, $09, $0B, $0C, $0A

```
> [!NOTE]
> **Ported to C:** [`l1df0`](../rom_compat_stubs.c#L22) in `rom_compat_stubs.c` (ASM: `1DF0-1DFF`)

```asm
                       .ORG $1DF0
; This is a simple protection against piracy.
```

### L1DF0:

```asm
                       LD      A,(ForegroundScreen+$31D) ; 'A' from 'AMSTAR ..' copyright text
                       SUB     $01                 
                       RET     Z                   
; crash the program and reset.
                       LD      (CoinCount),A       ;
                       NOP                         
                       NOP                         
                       NOP                         
                       NOP                         
                       NOP                         
                       NOP                         
                       NOP                         
;
;data for the 8 (2x2) planets / galaxies from setB
```

### T1E00:

```asm
                       .DB $20, $30, $21, $31
                       .DB $22, $32, $23, $33
                       .DB $24, $34, $25, $35
                       .DB $26, $36, $27, $37
                       .DB $28, $38, $29, $39
                       .DB $2A, $3A, $2B, $3B
                       .DB $2C, $3C, $2D, $3D
                       .DB $2E, $3E, $2F, $3F
;MSB's of screen ram for planets / galaxies
```

### T1E20:

```asm
                       .DB $49, $48, $4A, $4B
                       .DB $4A, $49, $4A, $49
                       .DB $48, $4A, $48, $49
                       .DB $4B, $48, $4A, $48
                       .DB $4A, $49, $4B, $49
                       .DB $4B, $4A, $49, $48
                       .DB $49, $49, $4A, $4A
                       .DB $48, $49, $4A, $48
; The low byte (LSB) half of the background screen destination addresses for the (2×2) planets
```

### T1E40:

```asm
                       .DB $A0, $60, $40, $00
                       .DB $E0, $C0, $C0, $60
                       .DB $80, $20, $60, $40
                       .DB $20, $40, $00, $80
                       .DB $40, $00, $20, $E0
                       .DB $00, $60, $00, $A0
                       .DB $E0, $20, $80, $00
                       .DB $C0, $80, $A0, $E0
;LSB's of screen ram for planets / galaxies
```

### T1E60:

```asm
                       .DB $00, $04, $08, $0C
                       .DB $10, $14, $18, $1C
                       .DB $00, $08, $10, $18
                       .DB $04, $0C, $14, $1C
                       .DB $00, $0C, $18, $04
                       .DB $04, $1C, $08, $14
                       .DB $00, $10, $04, $14
                       .DB $08, $18, $0C, $1C
;data for the 16 (1x1) small galaxies from setB
```

### T1E80:

```asm
                       .DB $10, $11, $12, $13
                       .DB $14, $15, $16, $17
                       .DB $18, $19, $1A, $1B
                       .DB $1C, $1D, $1E, $1F
                       .DB $10, $12, $14, $16
                       .DB $18, $1A, $1C, $1E
                       .DB $11, $13, $15, $17
                       .DB $19, $1B, $1D, $1F
;
```

### T1EA0:

```asm
                       .DB $4A, $4B, $49, $4A
                       .DB $48, $4A, $48, $49
                       .DB $49, $4A, $49, $4B
                       .DB $48, $4B, $4A, $4A
                       .DB $48, $49, $48, $4A
                       .DB $48, $48, $49, $4A
                       .DB $49, $49, $4A, $48
                       .DB $4A, $49, $4B, $48
;
```

### T1EC0:

```asm
                       .DB $00, $20, $60, $40
                       .DB $E0, $80, $20, $60
                       .DB $40, $A0, $00, $00
                       .DB $40, $20, $C0, $20
                       .DB $A0, $80, $E0, $40
                       .DB $60, $C0, $20, $A0
                       .DB $E0, $40, $60, $C0
                       .DB $20, $40, $20, $80

;*****************************************************************************
;* Used for the animation speed at bird intro.
;*****************************************************************************
```

### L1EE0:

```asm
                       LD      DE,ForegroundScreen+$33D ; holding 0
                       LD      BC,$001A            ;
```

### L1EE6:

```asm
                       LD      A,(DE)              ;
                       ADD     A,B                 ;
                       LD      B,A                 ;
                       CALL    RightOneColumn      ;
                       DEC     C                   ;
                       JP      NZ,L1EE6            ;
                       LD      A,(DE)              ;
                       ADD     A,B                 ;
                       ADD     $27                 ;
                       LD      HL,HiScorehigh      ;
                       ADD     A,(HL)              ;
                       LD      (HL),A              ;
                       NOP                         ;
                       RET                         ;

                       .ORG $1F00
;
; Part of the starfield background without planets
```

### T1F00:

```asm
                       .DB $00, $00, $00, $01, $00, $00, $00, $02, $00, $00, $00, $00, $03, $00, $00, $00
                       .DB $00, $04, $00, $00, $00, $00, $01, $00, $00, $00, $05, $00, $02, $00, $03, $00
                       .DB $00, $00, $04, $00, $07, $00, $00, $00, $06, $00, $01, $00, $02, $0C, $00, $03
                       .DB $04, $00, $00, $01, $00, $08, $00, $00, $02, $00, $0C, $03, $04, $0E, $00, $00
                       .DB $00, $01, $02, $00, $0D, $03, $04, $0F, $01, $0C, $07, $0A, $02, $0D, $03, $08
                       .DB $06, $0C, $04, $09, $05, $0F, $01, $02, $0D, $03, $0C, $04, $0D, $05, $0F, $0C
                       .DB $01, $02, $0E, $0C, $03, $0F, $0D, $05, $0E, $0D, $0C, $0F, $0D, $04, $0C, $01
                       .DB $0E, $05, $0F, $0D, $07, $0C, $06, $0E, $0D, $0F, $09, $0C, $0F, $0D, $0E, $0D
                       .DB $02, $0D, $0C, $0F, $05, $0E, $0D, $0C, $0F, $06, $0E, $0F, $0C, $0D, $0F, $0C
                       .DB $06, $0D, $04, $0B, $0C, $0F, $05, $0D, $05, $03, $0E, $07, $0C, $0D, $04, $05
                       .DB $01, $02, $0E, $03, $0C, $04, $0F, $05, $08, $0C, $07, $01, $0D, $04, $0E, $02
                       .DB $0C, $01, $0F, $03, $05, $0D, $00, $0E, $00, $09, $0C, $06, $0D, $00, $01, $02
                       .DB $01, $02, $03, $00, $00, $0D, $00, $0A, $00, $00, $00, $0E, $00, $05, $00, $08
                       .DB $00, $0C, $00, $00, $03, $00, $00, $07, $00, $00, $00, $04, $00, $00, $06, $00
                       .DB $00, $00, $00, $01, $00, $00, $00, $00, $02, $00, $00, $00, $00, $03, $00, $00
                       .DB $00, $04, $00, $05, $00, $00, $00, $00, $00, $01, $00, $00, $00, $00, $02, $00

;*****************************************************************************
; h5-ic49.5a
;*****************************************************************************
;*****************************************************************************
;* Game level 1, 3 and B:
;* 'player alife' with aliens, after 'fade in'
;*****************************************************************************
```

### L2000:

```asm
                       CALL    PlayerUpdate        ; Updates the player ship, player bullet and the shield.
                       CALL    L0DF0               ; alien bullet to player, collission detection ?
                       CALL    L24A0               ; 
                       LD      HL,M435F            ; 8 bit counter for alien movement
                       LD      A,(HL)              ; get value
                       AND     $03                 ; mask out 0000_0011 for count 0 to 3
                       LD      B,A                 ; save the masked counter
                       INC     (HL)                ; increment alien movement counter
                       LD      A,(AliensLeft)      ; 
                       AND     A                   ; updates the zero flag
                       JP      Z,L21BA             ; if no AliensLeft
                       CP      $05                 ;
                       JP      NC,L2130            ; if <= 5 left
                       DEC     L                   ; $435E
                       LD      A,B                 ; get masked counter
                       AND     A                   ; updates the zero flag
                       JP      NZ,L2025            ; if masked counter <> 0
                       LD      (HL),$FF            ; set all bits at $435E
```

### L2025:

```asm
                       LD      A,(HL)              ; get $435E
                       AND     A                   ; updates the zero flag
                       JP      Z,L2130             ; if $435E = 0
                       JP      L2146               ; 

                       .ORG $2030
;
```

### L2030:

```asm
                       AND     $03                 
                       CP      $01                 
                       LD      DE,$1B50            
                       JP      L23AC               ; 

```
> [!NOTE]
> **Ported to C:** [`add_galaxies_to_background`](../hw_video_audio.c#L433) in `hw_video_audio.c` (ASM: `2040-208A`)

```asm
                       .ORG $2040
;*****************************************************************************
;* Add 1x1 small galaxies to background.
;*****************************************************************************
```

### AddGalaxiesToBackground:

```asm
                       LD      HL,M43AF            ; 
                       LD      A,(CounterB9)       ; 
                       LD      C,A                 ;
                       CP      (HL)                ;
                       RET     NZ                  ;
                       LD      A,(HL)              ;
                       INC     L                   ;
                       SUB     (HL)                ;
                       DEC     L                   ;
                       LD      (HL),A              ;
                       INC     L                   ;
                       INC     L                   ;
                       INC     (HL)                ;
                       LD      A,(HL)              ;
                       LD      HL,T1E80            ; data for the 16 (1x1) small galaxies from setB
                       AND     $1F                 ;
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      B,(HL)              ;
                       ADD     $20                 ;
                       LD      L,A                 ;
                       LD      D,(HL)              ;
                       ADD     $20                 ;
                       LD      L,A                 ;
                       LD      E,(HL)              ;
                       LD      A,C                 ;
                       RRCA                        ;
                       RRCA                        ;
                       RRCA                        ;
                       AND     $1F                 ;
                       ADD     A,E                 ;
                       INC     A                   ;
                       LD      E,A                 ;
                       LD      A,B                 ;
                       LD      (DE),A              ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l2070`](../player_explosion.c#L115) in `player_explosion.c` (ASM: `2070-2084`)

```asm
                       .ORG $2070
;*****************************************************************************
;* `L2070`/`L2085` compute the entry offset from the ship position and current phase,
;* so as `CounterA5` counts down the "lit" cells sweep through the field.
;* The ship visibly bursts into scattering particles that then thin out and vanish.
;*****************************************************************************
```

### L2070:

```asm
                       LD      A,E                 
                       SUB     $0A                 
                       ADD     $C0                 
                       LD      C,A                 
                       LD      A,D                 
                       ADC     $00                 
                       LD      B,A                 
                       LD      A,(HL)              
                       LD      DE,T2800            ; get the foreground tiles of the player ship particles explosion
                       LD      HL,T2900            ; and get the control data for it
                       JP      L2085               ; 

                       .ORG $2085
;
```

### L2085:

```asm
                       SUB     $20                 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       NOP                         
                       AND     $E0                 
                       LD      L,A                 
                       LD      A,$E0               
                       SUB     L                   
                       LD      L,A                 
```

### L2091:

```asm
                       LD      A,$3F               
                       SUB     C                   
                       LD      A,$43               
                       SBC     B                   
                       JP      NC,L20B0            ; 
                       INC     HL                  
                       INC     HL                  
                       LD      A,E                 
                       ADD     $10                 
                       LD      E,A                 
                       LD      A,C                 
                       SUB     $20                 
                       LD      C,A                 
                       LD      A,B                 
                       SBC     $00                 
                       LD      B,A                 
                       JP      L2091               ; 

```
> [!NOTE]
> **Ported to C:** [`l20b0_player_ship_particles_explosion`](../player_explosion.c#L74) in `player_explosion.c` (ASM: `20B0-20E2`)

```asm
                       .ORG $20B0
;*****************************************************************************
;* Player ship particles explosion.
;*****************************************************************************
```

### L20B0:

```asm
                       PUSH    BC                  
```

### L20B1:

```asm
                       LD      A,(HL)              
                       EX      (SP),HL             
                       LD      B,$08               
```

### L20B5:

```asm
                       LD      (HL),$00            
                       RRCA                        
                       JP      NC,L20BF            ; 
                       EX      DE,HL               
                       LD      C,(HL)              
                       EX      DE,HL               ; get data from $2800
                       LD      (HL),C              
```

### L20BF:

```asm
                       INC     HL                  
                       INC     DE                  
                       DEC     B                   
                       JP      NZ,L20B5            ; 
                       EX      (SP),HL             
                       INC     HL                  
                       LD      A,L                 
                       RRCA                        
                       JP      C,L20B1             ; 
                       LD      A,L                 
                       AND     $1F                 
                       JP      Z,L20E1             ; 
                       EX      (SP),HL             
                       LD      A,L                 
                       SUB     $30                 
                       LD      L,A                 
                       LD      A,H                 
                       SBC     $00                 
                       LD      H,A                 
                       EX      (SP),HL             
                       CP      $3F                 
                       JP      NZ,L20B1            ; 
```

### L20E1:

```asm
                       POP     BC                  
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l20e8`](../player_explosion.c#L30) in `player_explosion.c` (ASM: `20E8-210D`)

```asm
                       .ORG $20E8
;*****************************************************************************
;* Draw one 4x4 ship-fragment sprite during the player-ship explosion.
;* Entry (from L0BC4): A = CounterA5 phase, DE = ship screen address.
;* Fragment image pointer comes from T1B90; position is scattered using
;* CounterB9 (via L211C) and the phase.
;* Purpose:
;* `L20E8` draws the flying debris sprites of the exploding player ship
;* (fragment image chosen from `T1B90`, scattered by `CounterB9`/phase,
;* `L211C` freezing the scroll).
;*****************************************************************************
```

### L20E8:

```asm
                       LD      B,A                 ; B = phase (CounterA5)
                       LD      A,D                 ; 
                       ADD     $08                 ; nudge the row
                       LD      D,A                 ; 
                       CALL    L211C               ; {code.L211C} clamp scroll during explosion
                       RRCA                        ; 
                       RRCA                        ; scatter offset from CounterB9
                       RRCA                        ; 
                       ADD     A,E                 ; 
                       AND     $1F                 ; 0001_1111 keep within a column
                       LD      C,A                 ; 
                       LD      A,E                 ; 
                       AND     $E0                 ; 1110_0000 column bits
                       OR      C                   ; 
                       LD      E,A                 ; E = scattered LSB
                       LD      A,B                 ; phase
                       RRCA                        ; 
                       RRCA                        ; 
                       AND     $0E                 ; 0000_1110 -> even index 0..14
                       ADD     $90                 ; -> T1B90 entry
                       LD      L,A                 ; 
                       LD      H,$1B               ; HL = T1B90 + index
                       LD      A,(HL)              ; fragment image MSB
                       INC     L                   ; 
                       LD      L,(HL)              ; fragment image LSB
                       LD      H,A                 ; HL = fragment image
                       LD      BC,$0404            ; images are 4x4images are 4x4
                       JP      DrawImageCbyB       ; draw it

```
> [!NOTE]
> **Ported to C:** [`l211c`](../player_explosion.c#L15) in `player_explosion.c` (ASM: `211C-212C`)

```asm
                       .ORG $211C
;*****************************************************************************
;* Clamp the scroll register to $10 while CounterB9 is in ($10,$30).
;*****************************************************************************
```

### L211C:

```asm
                       LD      HL,CounterB9        ; 
                       LD      A,(HL)              
                       CP      $10                 
                       RET     C                   
                       CP      $30                 
                       RET     NC                  
                       LD      A,$10               
                       LD      (HL),A              
                       LD      (scrollRegister),A  ; 58xx scroll register
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l2130`](../alien_wave.c#L204) in `alien_wave.c` (ASM: `2130-2145`)

```asm
                       .ORG $2130
;*****************************************************************************
;* Per-frame update dispatchers for the alien-wave levels.
;* B = frame phase (rotating counter). Each phase runs a different subset of
;* the heavy per-frame work, spreading it across frames.
;* `L2130`/`L2146`/`L21BA` are the game's per frame level dispatchers:
;* A rotating frame phase counter (`B`) selects one of several groups of update calls
;* (`AlienDataController`, `AlienBehaviorUpdate`, `AlienMovementUpdate`,
;* `AlienAnimationUpdate`, `EnemyBulletUpdate`, collision `L0F00`, killed alien anim `L0FC0`,
;* bomb drop `L2560`, mothership housekeeping `L24C4`),
;* so the heavy work is spread over multiple frames.
;*****************************************************************************
```

### L2130:

```asm
                       LD      A,B                 ; frame phase
                       AND     A                   ; updates the zero flag
                       JP      Z,L2150             ; phase 0
                       CP      $01                 ;
                       JP      Z,L2160             ; phase 1
                       CP      $02                 ;
                       JP      Z,L2170             ; phase 2
                       JP      L2180               ; phase 3

```
> [!NOTE]
> **Ported to C:** [`l2146`](../alien_wave.c#L192) in `alien_wave.c` (ASM: `2146-214F`)

```asm
                       .ORG $2146
;*****************************************************************************
;* Game's per frame level dispatcher (even/odd phase)
;*****************************************************************************
```

### L2146:

```asm
                       LD      A,B                 ; 
                       RRCA                        ; test phase bit 0
                       JP      NC,L2190            ; even phase
                       JP      L21A5               ; odd phase

```
> [!NOTE]
> **Ported to C:** [`l2150`](../alien_wave.c#L133) in `alien_wave.c` (ASM: `2150-215F`)

```asm
                       .ORG $2150
;*****************************************************************************
;* Phase 0
;*****************************************************************************
```

### L2150:

```asm
                       CALL    AlienDataController ; draw or delete alien
                       CALL    L3000               ; AlienBehaviorUpdate
                       JP      L0F00               ; 'alien with player' collision check

```
> [!NOTE]
> **Ported to C:** [`l2160`](../alien_wave.c#L142) in `alien_wave.c` (ASM: `2160-216F`)

```asm
                       .ORG $2160
;*****************************************************************************
;* Phase 1
;*****************************************************************************
```

### L2160:

```asm
                       CALL    L24C4               ; background / mothership housekeeping
                       CALL    L0C40               ; EnemyBulletUpdate
                       CALL    L0D1C               ; AlienMovementUpdate
                       JP      L0FC0               ; Handle animations for killed aliens

```
> [!NOTE]
> **Ported to C:** [`l2170`](../alien_wave.c#L152) in `alien_wave.c` (ASM: `2170-217F`)

```asm
                       .ORG $2170
;*****************************************************************************
;* Phase 2
;*****************************************************************************
```

### L2170:

```asm
                       CALL    L0D70               ; AlienAnimationUpdate
                       JP      L2560               ; try to drop a bomb on the player

```
> [!NOTE]
> **Ported to C:** [`l2180`](../alien_wave.c#L160) in `alien_wave.c` (ASM: `2180-218F`)

```asm
                       .ORG $2180
;*****************************************************************************
;* Phase 3
;*****************************************************************************
```

### L2180:

```asm
                       CALL    L24C4               ; background / mothership housekeeping
                       CALL    L0C40               ; EnemyBulletUpdate
                       CALL    L0A6C               ; get screen ram adress for all aliens
                       JP      L0FC0               ; Handle animations for killed aliens

```
> [!NOTE]
> **Ported to C:** [`l2190`](../alien_wave.c#L170) in `alien_wave.c` (ASM: `2190-21A4`)

```asm
                       .ORG $2190
;
```

### L2190:

```asm
                       CALL    AlienDataController ; draw or delete alien
                       CALL    L3000               ; AlienBehaviorUpdate
                       CALL    L0F00               ; 'alien with player' collision check
                       CALL    L2560               ; try to drop a bomb
                       JP      L0C40               ; EnemyBulletUpdate

```
> [!NOTE]
> **Ported to C:** [`l21a5`](../alien_wave.c#L181) in `alien_wave.c` (ASM: `21A5-21B9`)

```asm
                       .ORG $21A5
;
```

### L21A5:

```asm
                       CALL    L0D1C               ; AlienMovementUpdate
                       CALL    L0D70               ; AlienAnimationUpdate
                       CALL    L0A6C               ; get screen ram adress for all aliens
                       CALL    L0FC0               ; Handle animations for killed aliens
                       JP      L24C4               ; background / mothership housekeeping

```
> [!NOTE]
> **Ported to C:** [`l21ba`](../alien_wave.c#L103) in `alien_wave.c` (ASM: `21BA-21CF`)

```asm
                       .ORG $21BA
;*****************************************************************************
;* Mothership-wave dispatcher (and end-of-wave handling).
;*****************************************************************************
```

### L21BA:

```asm
                       LD      A,B                 ;
                       RRCA                        ; test phase bit 0
                       JP      NC,L2204            ; even phase: end-of-wave countdown (L2204)
                       CALL    L0C40               ; EnemyBulletUpdate
                       CALL    L0FC0               ; Handle animations for killed aliens
                       CALL    L24C4               ; mothership housekeeping
                       LD      A,(LevelAndRound)   ; 
                       AND     $0F                 ; mask out 0000_1111
                       CP      $0B                 ;
                       JP      C,L2204             ; if < game level B
                       LD      A,$10               ; 16 aliens for a new wave
                       LD      (AliensLeft),A      ; 
                       JP      L0526               ; init alien data

                       .ORG $21DC
;*****************************************************************************
;* Handles the bird animation at intro.
;* The driver is a single counter, `M4399` 
;* (the "slow-print" timer that advances during the intro splash).
;* Its bits are split into two roles:
;* - `M4399 & 7` -> the bird's animation sub-phase 
;*   (written to bird-object byte +3, `$4B73`).
;*   This cycles the wing position 0–7 within the current shape.
;* - `M4399 >> 3` -> the index into `T233A`, which yields the shape index 
;*   (written to bird-object byte +0, `$4B70`).
;* In other words, each entry in `T233A` is held for 8 timer ticks
;* (one full pass of the low-3-bit phase) before the script advances to the next shape.
;* `T233A` is therefore "the shape every 8 frames", and the low bits provide the in-between wing flapping.
;*****************************************************************************
```

### DrawIntroBirdAnimationFrame:

```asm
                       LD      A,(HL)              ; {ram.M4399} Actual index for slow print at intro splash (starts with $300)
                       NOP                         ;
                       LD      B,A                 ; save it
                       LD      HL,B4B73            ; used as temp memory
                       AND     $07                 ; mask out 0000_0111 in order to count from 0 to 7
                       LD      (HL),A              ; save it
                       DEC     L                   ;
                       LD      (HL),$EF            ; use $4B72 for LSB of screen ram
                       DEC     L                   ;
                       LD      (HL),$49            ; use $4B71 for MSB of screen ram
                       DEC     L                   ; $4B70 (bird0 index character block shape)
                       LD      A,B                 ; restore $4399
                       AND     $F8                 ; mask out 1111_1000
                       RRCA                        ; Divide by 8 ..
                       RRCA                        ; ..
                       RRCA                        ; ..
                       ADD     T233A & $FF         ; LSB of T233A
                       LD      E,A                 ;
                       LD      D,T233A >> 8        ; MSB of T233A
                       LD      A,(DE)              ; get data starting at T233A for animation frame index
                       LD      (HL),A              ; write to $4B70
                       CALL    DrawBirdObject      ; draw the bird at intro
                       JP      L1EE0               ; 

```
> [!NOTE]
> **Ported to C:** [`l2204`](../alien_wave.c#L79) in `alien_wave.c` (ASM: `2204-222B`)

```asm
                       .ORG $2204
;
```

### L2204:

```asm
                       LD      HL,M43B6            ; End-of-wave countdown timer
                       DEC     (HL)                ;
                       LD      A,(HL)              ;
                       CP      $A0                 ;
                       RET     NC                  ;
                       LD      L,$A4               ;
                       LD      (HL),$02            ; set GameState to: 'initialization of game and level data'
                       LD      L,$A6               ;
                       LD      (HL),$00            ; clear ShieldCount
                       LD      L,$B8               ;
                       INC     (HL)                ; increment LevelAndRound
                       LD      A,(HL)              ;
                       AND     $0E                 ; mask out 0000_1110
                       RRCA                        ; divide by 2
                       ADD     T1760 & $FF         ; add to base of table T1760
                       LD      E,A                 ;
                       LD      D,T1760 >> 8        ;
                       INC     L                   ;
                       INC     L                   ;
                       LD      A,(DE)              ; get value from table T1760
                       AND     A                   ; updates the flags
                       JP      P,L222A             ; if not positive.
                       INC     L                   ; use BirdsLeft
                       AND     $7F                 ; mask out 0111_1111
```

### L222A:

```asm
                       LD      (HL),A              ; save to $43BA (AliensLeft) or $43BB (BirdsLeft)
                       JP      ClearForeground     ; 

```
> [!NOTE]
> **Ported to C:** [`level_4_6_8_spiral_fill`](../state_play.c#L119) in `state_play.c` (ASM: `2230-225F`)

```asm
                       .ORG $2230
;*****************************************************************************
;* Game level 4, 6 and 8:
;* Drives the spiral fade-in animation between waves.
;* The animation step counter is incremented every frame,
;* its value indexes the spiral drawing progress,
;* and when the spiral is complete it advances to the next level.
;*****************************************************************************
```

### L2230:

```asm
                       LD      HL,M439C            ; 
                       LD      A,(HL)              ;
                       INC     (HL)                ; advance animation
                       NOP                         ;
                       RRCA                        ;
                       AND     $3F                 ; mask out 0011_1111
                       CP      $0D                 ;
                       JP      Z,L2292             ; 
                       LD      B,$1F               ; The asterisk character
                       JP      C,L2260             ; 
                       LD      B,$00               ; The space character
                       SUB     $0E                 ;
                       CP      $0D                 ;
                       JP      NZ,L2260            ; 
                       LD      HL,LevelAndRound    ; 
                       INC     (HL)                ; increment game level $43B8
                       LD      L,$A4               ; HL=43A4 -- game state
                       LD      (HL),$02            ; Next interval game state is 2: 'init game and level data'
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l2260_spiral_draw`](../state_play.c#L26) in `state_play.c` (ASM: `2260-2291`)

```asm
                       .ORG $2260
;
```

### L2260:

```asm
                       LD      C,A                 ;
                       RRCA                        ;
                       RRCA                        ;
                       RRCA                        ;
                       LD      D,A                 ;
                       AND     $1F                 ;
                       LD      E,A                 ;
                       LD      A,D                 ;
                       AND     $E0                 ;
                       ADD     $B0                 ;
                       LD      L,A                 ;
                       LD      A,E                 ;
                       ADC     $41                 ;
                       LD      H,A                 ;
                       LD      A,L                 ;
                       SUB     C                   ;
                       LD      L,A                 ;
                       LD      A,C                 ;
                       INC     A                   ;
                       LD      C,A                 ;
                       RLCA                        ; Multiply by 2
                       LD      E,A                 ;
;
```

### L227A:

```asm
                       LD      D,C                 ; D is the height counter for each pass
;
```

### L227B:

```asm
                       LD      (HL),B              ; draw the asterisk or space
                       INC     HL                  ; one row down
                       LD      (HL),B              ; another asterisk or space
                       INC     HL                  ; one row down
                       DEC     D                   ; all of this column done?
                       JP      NZ,L227B            ; No ... do all rows
                       LD      A,L                 ; LSB of screen pointer
                       SUB     C                   ; move up ...
                       SUB     C                   ; ... height * 2
                       SUB     $20                 ; Move right one column
                       LD      L,A                 ; New LSB
                       LD      A,H                 ; Borrow into ...
                       SBC     $00                 ; ... the ...
                       LD      H,A                 ; ... MSB
                       DEC     E                   ; All columns done?
                       JP      NZ,L227A            ; no ... do all columns
                       RET                         ; Done
;*****************************************************************************
;* Spiral step
;*****************************************************************************
```

### L2292:

```asm
                       LD      HL,LevelAndRound    ; 
                       LD      A,(HL)              ;
                       AND     $08                 ; mask out 0000_1000
                       JP      Z,L22F0             ; 
;*****************************************************************************
;* Fill the entire background with stars (uses the whole `$1C00`–`$1CFF` page, including `$1CB4`–`$1CFF`).
;* `L2292` copies the star page into background VRAM from `$4B3F` downward, reading `T1C00` with `INC L`
;* (which wraps inside page `$1C`), until it has filled `$4800`–`$4B3F`.
;*****************************************************************************
                       LD      HL,T1C00            ; Background stars to erase mother ship
                       LD      DE,$4B3F            ; End of background screen memory
                       LD      B,$47               ;
```

### L22A3:

```asm
                       LD      A,(HL)              ;
                       LD      (DE),A              ;
                       INC     L                   ;
                       DEC     DE                  ;
                       LD      A,(HL)              ;
                       LD      (DE),A              ;
                       INC     L                   ;
                       DEC     DE                  ;
                       LD      A,B                 ;
                       CP      D                   ;
                       JP      NZ,L22A3            ; 
                       JP      L22E0               ; 

```
> [!NOTE]
> **Ported to C:** [`level_9_mothership_fade_in`](../state_play.c#L163) in `state_play.c` (ASM: `22B4-22C5`)

```asm
                       .ORG $22B4
;*****************************************************************************
;* Game level 9:
;* Mothership 'fade in' animation.
;*****************************************************************************
```

### L22B4:

```asm
                       CALL    StarsScrollDown     ; 
                       LD      HL,CounterB4        ; 
                       DEC     (HL)                ;
                       LD      A,(HL)              ;
                       CP      $28                 ;
                       JP      NZ,L0848            ; 
                       LD      L,$67               ;
                       LD      (HL),$FF            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`level_A_mothership_and_aliens_fade_in`](../state_play.c#L188) in `state_play.c` (ASM: `22CA-22DD`)

```asm
                       .ORG $22CA
;*****************************************************************************
;* Game level A:
;* Mothership and aliens 'fade in'
;*****************************************************************************
```

### L22CA:

```asm
                       LD      HL,CounterB4        ; 
                       LD      A,(HL)              ;
                       CP      $C0                 ;
                       JP      NZ,L0834            ; Stars scrolling down and 'aliens fade in'
                       LD      (HL),$30            ;
                       LD      L,$67               ;
                       LD      (HL),$FF            ;
                       LD      L,$BC               ;
                       LD      (HL),$3F            ;
                       RET                         ;

                       .ORG $22E0
;
```

### L22E0:

```asm
                       LD      A,$71               ; init the ...
;
```

### L22E2:

```asm
                       LD      (CounterB9),A       ; free running 8 bit backwards counter
                       LD      (scrollRegister),A  ; 58xx scroll register
                       RET                         ;

                       .ORG $22F0
;
```

### L22F0:

```asm
                       CALL    ClearBackground     ; 
                       XOR     A                   ; A=0
                       JP      L22E2               ; 

                       .ORG $22FA
;*****************************************************************************
;* Rotate the conveyor belt:
;* How the "rotation" actually works:
;* Each belt tile is a code in `$60`–`$6F`, i.e. `$60 + p` where `p` is a 4-bit phase (0–15)
;* that selects which frame of the belt-link graphic is shown. The routine treats that 4-bit phase as two 2-bit halves.
;* - high half = bits 2–3
;* - low half = bits 0–1
;* Walking up the belt column (`L -= $20` each step), every tile is rebuilt as:
;* new_phase = (previous_tile.low2 << 2) | (current_tile.high2)
;* new_tile  = $60 | new_phase
;* In other words:
;* - a tile's new high 2 bits come from the lower neighbour's old low 2 bits, and
;* - its new low 2 bits come from its own old high 2 bits.
;* That is a 2-bit-per-tile shift register running up the column:
;* Every animation step, the belt-link pattern marches exactly one 2-bit field up the chain.
;* The seed value read from `$488A` feeds a fresh pattern into the bottom of the chain each step,
;* so the motion is continuous and never runs out of pattern.
;* Because the cumulative effect is "every belt segment's pattern shifts one position along the belt each tick",
;* the row of `$60`–`$6F` tiles cycles through their link graphics in lock-step — which the eye reads as the belt rotating/conveying.
;*****************************************************************************
```

### L22FA:

```asm
                       LD      HL,BackgroundScreen+$2AA
                       LD      B,$12               
                       LD      A,(BackgroundScreen+$8A)
                       LD      C,A                 
```

### L2303:

```asm
                       LD      A,C                 
                       AND     $03                 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       LD      D,A                 
                       LD      C,(HL)              
                       LD      A,C                 
                       AND     $0C                 
                       RRCA                        
                       RRCA                        
                       OR      D                   
                       OR      $60                 
                       LD      (HL),A              
                       LD      A,L                 
                       SUB     $20                 
                       LD      L,A                 
                       JP      NC,L231B            ; 
                       DEC     H                   
```

### L231B:

```asm
                       DEC     B                   
                       JP      NZ,L2303            ; 
                       RET                         

                       .ORG $2322
;*****************************************************************************
;* Animation of the mothership's antenna and the alien pilot.
;*****************************************************************************
```

### L2322:

```asm
                       LD      HL,AnimationCounter ; 
                       INC     (HL)                ; increment the animation counter
                       LD      A,(HL)              ;
                       AND     $07                 ; mask out 0000_0111, in order to count from 0 to 7 for 8 frames
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..to get..
                       RLCA                        ; ..the frame data adress (8 characters per frame)
                       ADD     T1BC0 & $FF         ; LSB of T1BC0
                       LD      L,A                 ;
                       LD      H,T1BC0 >> 8        ; MSB of T1BC0
                       LD      DE,BackgroundScreen+$1A6; at the middle of the mothership
                       LD      BC,$0402            ; images are 2x4
                       JP      DrawImageCbyB       ; 
; Intro-splash bird animation script table:
; A list of bird shape indices that, played in order, make the attract-mode bird grow
; from a twinkling star into a full flapping Phoenix and then shrink back.
; Used at `DrawIntroBirdAnimationFrame` (`$21DC`).
; The mapping is a two-level lookup:
; M4399  --(>>3)-->  T233A[i] = shape index
;                      |
;                      +--(*8)--+--(+ M4399&7 phase)--> T3E08 entry --> bird tile-block address
; So `T233A` is essentially a tiny animation timeline.
; The index `M4399 >> 3` walks through it, each step lasting 8 ticks (during which `M4399 & 7` animates the wings),
; turning the abstract growth/flap/shrink choreography into concrete shape indices that `DrawBirdObject` renders.
; The trailing `FF` signals the end of the script (it's the sentinel the surrounding intro logic uses to know the sequence is finished).
```

### T233A:

```asm
                       .DB $01, $02, $03, $04, $05, $06, $07, $0A, $07, $0A, $07, $0A, $07, $0A, $07, $0A
                       .DB $09, $08, $04, $03, $02, $01, $FF

;*****************************************************************************
;* Mother-ship collision routine:
;* During the mother-ship levels (game level ≥ 8), `L2000` -> `L24A0` calls `L2351`.
;* It looks up the tile at the (scroll-adjusted) bullet position 
;* and explicitly tests for the `$4C`–`$4F` group.
;*****************************************************************************
```

### L2351:

```asm
                       LD      A,(DE)              
                       AND     $08                 
                       RET     Z                   
                       LD      A,(HL)              
                       INC     L                   
                       LD      L,(HL)              
                       ADD     $08                 
                       LD      H,A                 
                       LD      A,(CounterB9)       ; 
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       ADD     A,L                 
                       AND     $1F                 
                       LD      B,A                 
                       LD      A,L                 
                       AND     $E0                 
                       OR      B                   
                       LD      L,A                 
                       LD      A,(HL)              
                       LD      B,A                 
                       AND     $FC                 
                       CP      $4C                 
                       JP      Z,L237B             ; 
                       AND     $F0                 
                       CP      $60                 
                       JP      Z,L2398             ; 
                       RET                         
;*****************************************************************************
;* The mothership's protective shield was hit by a player bullet.
;* Shield erosion.
;* So a hit on a `$4C`–`$4F` tile does the following, with no score awarded:
;* 1. The bullet is consumed (`AND $F7` clears the active bit) — the shot stops there; it does not punch through.
;* 2. A "mother-ship hit" is registered (`$4366 = $FF`), which drives the hit sound effect.
;* 3. The tile is decremented one step: `$4F -> $4E -> $4D -> $4C -> $4B`.
;*    Because the four tiles are an increasing-density gradient, each shot visually "chips" the curved armour one notch thinner.
;* 4. When a tile erodes to `$4B` it's cleared to `$00` (that chunk of shield is gone).
;*    If the tile behind it is the solid hull `$5E`, that hull tile is turned into a fresh `$4F`,
;*    i.e. the next layer of hull becomes the new erodible shield edge.
;*****************************************************************************
```

### L237B:

```asm
                       LD      A,(DE)              
                       AND     $F7                 
                       LD      (DE),A              
                       LD      A,$FF               
                       LD      (M4366),A           ; 
                       LD      A,B                 
                       DEC     A                   
                       LD      (HL),A              
                       CP      $4B                 
                       RET     NZ                  
                       LD      (HL),$00            
                       DEC     L                   
                       LD      A,(HL)              
                       CP      $5E                 
                       RET     NZ                  
                       LD      (HL),$4F            
                       RET                         

                       .ORG $2398
;*****************************************************************************
;* Belt-hit handler:
;*****************************************************************************
```

### L2398:

```asm
                       LD      A,(DE)              
                       AND     $F7                 
                       LD      (DE),A              
                       INC     E                   
                       INC     E                   
                       LD      A,(DE)              
                       AND     $04                 
                       LD      A,B                 
                       JP      NZ,L2030            ; 
                       AND     $0C                 
                       CP      $04                 
                       LD      DE,$1B40            
```

### L23AC:

```asm
                       JP      Z,L23C0             ; 
                       LD      A,B                 
                       AND     $0F                 
                       ADD     A,E                 
                       LD      E,A                 
                       LD      A,(DE)              
                       LD      (HL),A              
                       LD      A,$FF               
                       LD      (M4366),A           ; 
                       RET                         

                       .ORG $23C0
;*****************************************************************************
;* The mothership will be destroyed if an alien pilot is hit.
;* If the hit lands on the belt segment directly in front of the alien pilot,
;* `L23AC` takes the `JP Z,L23C0` branch instead, which checks whether the tile behind
;* is a pilot tile (`$70`-range) and, if so, destroys the mother ship.
;*****************************************************************************
```

### L23C0:

```asm
                       DEC     L                   
                       LD      A,(HL)              
                       AND     $F0                 
                       CP      $70                 
                       RET     NZ                  
                       LD      HL,GameState        ; Next interval game state ...
                       LD      (HL),$06            ; ... is 6 (mother ship partikel explosion)
                       INC     L                   
                       LD      (HL),$60            
                       LD      L,$63               
                       LD      (HL),$FF            
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l23d6`](../sound_dispatcher.c#L21) in `sound_dispatcher.c` (ASM: `23D6-23FB`)

```asm
                       .ORG $23D6
;*****************************************************************************
;* Background sound update.
;*****************************************************************************
```

### L23D6:

```asm
                       LD      HL,LevelAndRound    ; 
                       LD      A,(HL)              ;
                       AND     $0F                 ; mask out 0000_1111
                       CP      $01                 ;
                       JP      Z,L3A98             ; if game level is 1 (1st alien wave)
                       CP      $03                 ;
                       JP      Z,L3A98             ; if game level is 3 (2nd alien wave)
                       CP      $05                 ;
                       JP      Z,L3AD0             ; if game level is 5 (1st bird wave)
                       CP      $07                 ;
                       JP      Z,L3AD0             ; if game level is 7 (2nd bird wave)
                       CP      $09                 ;
                       RET     C                   ; if game level is 9 (mothership 'fade in')
                       CP      $0B                 ;
                       JP      C,L3B02             ; if game level is B (mothership)
                       CALL    L3B02               ; Background sound for level B (mothership)
                       JP      L3A98               ; Background sound for the alien waves

```
> [!NOTE]
> **Ported to C:** [`state_6_mother_ship_explosion`](../state_endings.c#L126) in `state_endings.c` (ASM: `2400-244B`)

```asm
                       .ORG $2400
;*****************************************************************************
;* Game state 6.
;* Mother ship partikel explosion.
;*****************************************************************************
```

### L2400:

```asm
                       CALL    L242C               ; 
                       JP      Z,L2552             ; 
                       CP      $20                 
                       JP      C,EraseMothership   ; 
                       JP      Z,L2520             ; Calculation and display of the bonus score for mothership explosion
                       LD      B,A                 
                       RRCA                        
                       NOP                         
                       LD      A,B                 
                       JP      NC,L20E8            ; 
                       LD      A,E                 
                       SUB     $05                 
                       ADD     $C0                 
                       LD      C,A                 
                       LD      A,D                 
                       ADC     $00                 
                       LD      B,A                 
                       LD      A,(HL)              
                       LD      DE,T2A00            ; get the foreground tiles of the mothership particles explosion
                       LD      HL,T2B00            ; get the control data
                       JP      L2085               ; 

```
> [!NOTE]
> **Ported to C:** [`update_counters_for_mothership_explosion`](../mothership_impl.c#L134) in `mothership_impl.c` (ASM: `242C-2442`)

```asm
                       .ORG $242C
;
```

### L242C:

```asm
                       LD      HL,CounterB9        ; 
                       LD      A,(HL)              
                       AND     $F8                 
                       LD      (HL),A              
                       LD      (scrollRegister),A  ; 58xx scroll register
                       LD      DE,$41C6            
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       LD      B,A                 
                       LD      A,E                 
                       SUB     B                   
                       AND     $1F                 
                       LD      B,A                 
                       LD      A,E                 
                       AND     $E0                 
                       OR      B                   
                       LD      E,A                 
                       LD      L,$A5               
                       DEC     (HL)                
                       LD      A,(HL)              
                       RET                         

;*****************************************************************************
;* Game state 7.
;* Mother ship score display.
;*****************************************************************************
```

### L244C:

```asm
                       LD      HL,CounterA5        ; 
                       DEC     (HL)                ;
                       LD      A,(HL)              ;
                       RRCA                        ;
                       JP      C,L06F0             ; update scroll register and fill background
                       AND     A                   ; updates the zero flag
                       RET     NZ                  ;
                       DEC     L                   ;
                       LD      (HL),$02            ;
                       LD      L,$B8               ;
                       LD      A,(HL)              ;
                       AND     $F0                 ;
                       ADD     $10                 ; go to next round and ..
                       LD      (HL),A              ; .. store at LevelAndRound $43B8
                       LD      L,$BA               ;
                       LD      (HL),$10            ; set AliensLeft to 16
                       JP      ClearForeground     ; 

```
> [!NOTE]
> **Ported to C:** [`erase_mothership`](../mothership_logic.c#L22) in `mothership_logic.c` (ASM: `246A-2475`)

```asm
                       .ORG $246A
;*****************************************************************************
;* EraseMothership:
;*****************************************************************************
```

### EraseMothership:

```asm
                       LD      BC,$0914            ; 20x9 image
                       LD      DE,$4AC6            ; Screen coordinate of mother ship
                       LD      HL,$1C00            ; Background stars to erase the mother ship
                       JP      DrawImageCbyB       ; Erase the mother ship
;
```

### L2476:

```asm
                       LD      A,B                 
                       ADD     A,C                 
                       CALL    L2495               ; 
                       LD      L,$D3               
                       LD      (HL),A              
                       LD      HL,BirdsLeft        ; 
                       LD      A,$08               ; number of birds
                       SUB     (HL)                ;
                       RLCA                        ; Multiply by 2
                       LD      L,$9A               
                       ADD     A,(HL)              
                       RLCA                        ; Multiply by 2
                       LD      B,A                 
; Attack timing / launch slot
                       LD      L,$6F               ; $436F (random)
                       LD      A,(HL)              
                       AND     $1E                 
                       ADD     A,B                 ; B from (8-BirdsLeft) & Counter9A
                       LD      (M4BD1),A           ; descent turnaround threshold (max depth)
                       RET                         

                       .ORG $2495
;
```

### L2495:

```asm
                       ADD     A,B                 
                       DEC     C                   
                       RET     Z                   
                       ADD     A,B                 
                       DEC     C                   
                       RET     Z                   
                       ADD     A,B                 
                       DEC     C                   
                       RET     Z                   
                       ADD     A,A                 
                       RET                         
;
```

### L24A0:

```asm
                       LD      A,(LevelAndRound)   ; 
                       AND     $0F                 ; mask out 0000_1111
                       CP      $08                 ;
                       RET     C                   ; return if game level < 8
                       LD      DE,PlayerBulletState
                       LD      HL,AbovePlayerBulletMSB
                       CALL    L2351               ; 
                       LD      A,(Counter9A+$1)    ; 
                       AND     $03                 ; mask out 0000_0011
                       CP      $03                 ;
                       RET     NZ                  ; return if <> 3
                       JP      L24F2               ; 

```
> [!NOTE]
> **Ported to C:** [`l24c4`](../alien_wave.c#L29) in `alien_wave.c` (ASM: `24C4-24DF`)

```asm
                       .ORG $24C4
;*****************************************************************************
;* The mother-ship level handlers (`L2130`/`L2146`/`L21BA`/`L21C5`) all call `L24C4` every frame.
;* `L24C4` bumps a frame counter (`$43AA`) and time-slices two animations:
;* The antenna/pilot animation `L2322` runs on 3 of every 4 frames,
;* and the belt rotation `L22FA` runs on the 4th.
;*****************************************************************************
```

### L24C4:

```asm
                       LD      A,(LevelAndRound)   ; 
                       AND     $0F                 ; mask out 0000_1111
                       CP      $08                 ;
                       JP      C,L06F0             ; update scroll register and fill background if game level < 8
                       CALL    L24E0               ; 
                       LD      HL,M43AA            ; 
                       INC     (HL)                ;
                       LD      A,(HL)              ;
                       AND     $03                 ; mask out 0000_0011
                       JP      Z,L22FA             ; if $43AA <> 3
                       JP      L2322               ; Animation of the mothership's antenna and the alien pilot

```
> [!WARNING]
> **Unreferenced Gap / TODO** (ASM: `24E0-24F1`)

```asm
                       .ORG $24E0
;
```

### L24E0:

```asm
                       LD      A,(M43AA)           ; 
                       AND     $0F                 
                       RET     NZ                  
                       LD      A,(CounterB9)       ; 
                       CP      $A0                 
                       RET     C                   
                       JP      StarsScrollDown     ; 

```
> [!NOTE]
> **Ported to C:** [`l24f2`](../misc_logic.c#L53) in `misc_logic.c` (ASM: `24F2-251C`)

```asm
                       .ORG $24F2
;*****************************************************************************
;* Mother ship bomb attack (reached from L24A0 on level >= 8, when
;* Counter9A+1 & 3 == 3). Randomly targets the player's column, then fires.
;* Purpose:
;* On mother ship levels this fires a bomb only when a random number happens
;* to line up horizontally with the player ship (a "semi aimed" attack,
;* further rate limited by the `Counter9A` gate). It builds the bomb's `B`=X / `C`=Y
;* (Y derived from the scroll counter) and jumps into the shared spawner `L25B7`.
;* The two `PUSH HL` match the two `POP HL` that `L25B7`/`L25E0` do on exit.
;*****************************************************************************
```

### L24F2:

```asm
                       CALL    GetRandomNumber     ; 
                       ADD     $60                 
                       NOP                         
                       LD      B,A                 
                       LD      HL,Counter9A+$1    ; 
                       AND     $0E                 
                       AND     (HL)                
                       RET     NZ                  
                       LD      A,(M439E)           ; 
                       CP      B                   
                       RET     NC                  
                       LD      A,(M439F)           ; 
                       CP      B                   
                       RET     C                   
                       LD      A,B                 
                       SUB     $04                 
                       LD      B,A                 
                       LD      A,(CounterB9)       ; 
                       CPL                         
                       INC     A                   
                       AND     $F8                 
                       ADD     $48                 
                       LD      C,A                 
                       PUSH    HL                  
                       PUSH    HL                  
                       JP      L25B7               ; 

```
> [!NOTE]
> **Ported to C:** [`mothership_core_hit_check`](../mothership_logic.c#L48) in `mothership_logic.c` (ASM: `2520-254F`)

```asm
                       .ORG $2520
;*****************************************************************************
;* The 'alien pilot' at mothership was hit.
;* Calculation and display of the bonus score for mothership explosion.
;*****************************************************************************
```

### L2520:

```asm
                       PUSH    DE                  ;
                       CALL    ClearForeground     ; remove all but the rest of the mothership
                       POP     DE                  ;
                       LD      A,(CounterB9)       ; get value from 8 bit backwards counter
                       ADD     $60                 ; use it for a ...
                       RRCA                        ; ... score value
                       LD      B,A                 ; save it
                       LD      A,(LevelAndRound)   ; 
                       AND     $F0                 ; mask out 1111_0000 (bit4 - 7: game round)
                       ADD     A,B                 ; add score value
                       LD      B,$90               ;
                       JP      C,L253D             ; 
                       CP      $90                 ;
                       JP      NC,L253D            ; 
                       LD      B,A                 ;
```

### L253D:

```asm
                       XOR     A                   ; A=0
                       LD      A,B                 ;
                       DAA                         ; adjust for BCD
                       LD      HL,M439D            ; 
                       LD      (HL),A              ; set value for fist two digits of BCD score
                       INC     L                   ;
                       LD      (HL),$00            ; last two digits of BCD score set to '00'
                       LD      A,E                 ; get LSB of screen ram...
                       SUB     $5E                 ; ...
                       LD      E,A                 ; ...
                       LD      B,$04               ; number of digits to print
                       JP      PrintNumber         ; score for mothership explosion

```
> [!NOTE]
> **Ported to C:** [`l2552_mothership_explosion_done`](../state_endings.c#L102) in `state_endings.c` (ASM: `2552-255D`)

```asm
                       .ORG $2552
;
```

### L2552:

```asm
                       LD      L,$A4               ;
                       LD      (HL),$07            
                       INC     L                   
                       LD      (HL),$40            
                       LD      L,$6B               
                       LD      (HL),$FF            
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l2560`](../alien_logic.c#L778) in `alien_logic.c` (ASM: `2560-2595`)

```asm
                       .ORG $2560
;*****************************************************************************
;* Alien bomb-drop: pick a group of 8 aliens, find one lined up with the
;* player at attack depth, and fire an enemy bullet at it.
;* Purpose:
;* `L2560` is the alien bomb drop selector. 
;* It picks one of two 8 alien groups (alternating on `Counter93`),
;* computes the player's horizontal window (`B`,`C`) and the required attack depth `D`
;* (scaled by the attack escalation counter `$4357`), then scans the group with `L2596`.
;*****************************************************************************
```

### L2560:

```asm
                       LD      HL,Counter93            ; 
                       LD      A,(HL)              
                       AND     $01                 
                       RLCA                        ; Multiply by 32 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       ADD     $70                 
                       LD      L,A                 
                       LD      H,$4B               
                       LD      E,$08               
                       LD      A,(M4357)           ; 
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       NOP                         
                       ADD     $AD                 
                       LD      D,A                 
                       LD      A,(M439F)           ; 
                       ADD     $03                 
                       LD      C,A                 
                       LD      A,(M439E)           ; 
                       SUB     $0A                 
                       LD      B,A                 
```

### L2588:

```asm
                       PUSH    HL                  
                       CALL    L2596               ; 
                       POP     HL                  
                       LD      A,L                 
                       ADD     $04                 
                       LD      L,A                 
                       DEC     E                   
                       JP      NZ,L2588            ; 
                       RET                         
;*****************************************************************************
;* Per-alien attack candidacy test. HL -> alien entry.
;* Must be active, valid shape, horizontally over the player, and deep enough.
;* `L2596` accepts an alien that is active, a valid shape, horizontally over the player,
;* and deep enough on screen. When one qualifies it loads its position into `B`/`C` and drops into `L25B7`.
;*****************************************************************************
```

### L2596:

```asm
                       LD      A,(HL)              
                       AND     $08                 
                       RET     Z                   
                       INC     L                   
                       LD      A,(HL)              
                       CP      $08                 
                       RET     Z                   
                       CP      $88                 
                       RET     NC                  
                       INC     L                   
                       LD      A,(HL)              
                       CP      B                   
                       RET     C                   
                       CP      C                   
                       RET     NC                  
                       INC     L                   
                       LD      A,(HL)              
                       CP      D                   
                       RET     NC                  
                       CP      $80                 
                       RET     C                   
                       NOP                         
                       NOP                         
                       NOP                         
                       NOP                         
                       NOP                         
                       LD      C,A                 
                       DEC     L                   
                       LD      B,(HL)              
;*****************************************************************************
;* Fire the enemy bullet (shared by alien and mother-ship attacks):
;* Finds a free enemy-bullet slot (max 3/4/5 depending on round) and,
;* if one exists, activates it at `(B,C)`; if all slots are busy
;* it returns up two stack levels (cancelling the scan for this frame).
;*****************************************************************************
```

### L25B7:

```asm
                       LD      A,(LevelAndRound)   ; 
                       LD      D,$03               ;
                       CP      $10                 ; 0001_0000
                       JP      C,L25CA             ; if game round < 1
                       LD      D,$04               ;
                       CP      $20                 ; 0010_0000
                       JP      C,L25CA             ; if game round < 2
                       LD      D,$05               ;
```

### L25CA:

```asm
                       LD      HL,AlienBullet0State
```

### L25CD:

```asm
                       LD      A,(HL)              ;
                       AND     $08                 ; mask out 0000_1000
                       JP      Z,L25E0             ; 
                       LD      A,L                 
                       ADD     $04                 
                       LD      L,A                 
                       DEC     D                   
                       JP      NZ,L25CD            ; 
                       POP     HL                  
                       POP     HL                  
                       RET                         

                       .ORG $25E0
;*****************************************************************************
;* Bullet spawner:
;* It fills that slot — marking it active, computing a bullet character/type from the position,
;* and storing the X/Y. The paired `POP HL` at the ends unwind the two dummy
;* stack frames the callers pushed, so control returns cleanly
;* regardless of whether a bullet was actually fired.
;*****************************************************************************
```

### L25E0:

```asm
                       LD      A,B                 
                       ADD     $04                 
                       LD      B,A                 
                       LD      A,C                 
                       ADD     $0C                 
                       LD      C,A                 
                       LD      (HL),$08            
                       INC     L                   
                       LD      A,B                 
                       RRCA                        
                       AND     $03                 
                       LD      D,A                 
                       LD      A,C                 
                       AND     $04                 
                       ADD     A,D                 
                       ADD     $58                 
                       LD      (HL),A              
                       INC     L                   
                       LD      (HL),B              
                       INC     L                   
                       LD      (HL),C              
                       POP     HL                  
                       POP     HL                  
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`birds_vertical_movement_update`](../birds_vertical_movement.c#L112) in `birds_vertical_movement.c` (ASM: `2600-2664`)

```asm
                       .ORG $2600
;*****************************************************************************
;* Birds vertical movement update (with 58xx scroll register).
;*****************************************************************************
```

### L2600:

```asm
                       NOP                         ; Old command removed or space for a future replace patch
                       NOP                         ; ..
                       NOP                         ; ..
                       NOP                         ; ..
                       NOP                         ; ..
                       LD      A,(CounterB9)       ; 
                       CPL                         
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       AND     $1F                 
                       LD      HL,M4BD2            ; 
                       LD      (HL),A              
                       INC     L                   
                       LD      A,(M4BD1)           ; 
                       CP      (HL)                
                       JP      C,L2650             ; 
                       LD      A,(M4BD5)           ; 
                       LD      D,A                 
                       AND     $03                 
                       LD      E,A                 
                       LD      A,(Counter9A+$1)    ; 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       AND     $0C                 
                       ADD     A,E                 
                       ADD     $D0                 
                       LD      L,A                 
                       LD      H,$3E               
                       LD      A,D                 
                       RRCA                        
                       RRCA                        
                       AND     $07                 
                       ADD     A,(HL)              
                       LD      D,A                 
                       LD      A,(CounterB9)       ; 
                       SUB     D                   
```

### L2639:

```asm
                       LD      (CounterB9),A       ; 
                       LD      (scrollRegister),A  ; 58xx scroll register
                       LD      A,(Counter9A+$1)    ; 
                       RRCA                        
                       JP      NC,L26D0            ; 
                       CALL    L2668               ; 
                       JP      L26AA               ; 

                       .ORG $2650
;
```

### L2650:

```asm
                       INC     L                   ;
                       LD      A,(Counter9A+$1)    ; 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       AND     $0C                 
                       ADD     A,(HL)              
                       ADD     $D0                 
                       LD      L,A                 
                       LD      H,$3E               
                       LD      A,(CounterB9)       ; 
                       ADD     A,(HL)              
                       JP      L2639               ; 
                       JP      NC,L26AE            ; 

;
```

### L2668:

```asm
                       LD      A,(M436E)           ; 
                       NOP                         
                       LD      B,A                 
                       LD      A,(Counter9A)       ; 
                       CP      $18                 
                       JP      C,L2676             ; 
                       INC     B                   
```

### L2676:

```asm
                       CP      $10                 
                       JP      C,L267C             ; 
                       INC     B                   
```

### L267C:

```asm
                       LD      A,(AliensLeft)      ; 
                       CP      $03                 
                       JP      NC,L2685            ; 
                       INC     B                   
```

### L2685:

```asm
                       LD      A,(M4BD6)           ; 
                       ADD     $E0                 
                       LD      L,A                 
                       LD      H,$3E               
                       LD      A,B                 
                       CP      (HL)                
                       JP      C,L2693             ; 
                       LD      A,(HL)              
```

### L2693:

```asm
                       LD      D,A                 
                       LD      A,(BirdsLeft)       ; 
                       CP      $04                 
                       JP      NC,L269D            ; 
                       INC     D                   
```

### L269D:

```asm
                       CP      $02                 
                       JP      NC,L26A3            ; 
                       INC     D                   
```

### L26A3:

```asm
                       LD      A,D                 
                       LD      (M4BD5),A           ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l26aa`](../birds_vertical_movement.c#L60) in `birds_vertical_movement.c` (ASM: `26AA-26CC, 2476-2493, 2495-249F`)

```asm
                       .ORG $26AA
```

### L26AA:

```asm
                       LD      HL,M4BD3            ; countdown timer between bird attacks ("bird extended storage")
                       LD      A,(HL)              
```

### L26AE:

```asm
                       DEC     (HL)                
                       AND     A                   ; updates the zero flag
                       RET     NZ                  
                       INC     (HL)                
                       LD      L,$D6               
                       LD      A,(HL)              
                       CP      $16                 
                       RET     NC                  
                       CP      $08                 
                       RET     C                   
                       INC     L                   
                       SUB     (HL)                
                       RLCA                        ; Multiply by 2
                       LD      B,A                 
; Attack sub-pattern selector
                       LD      A,(M436F)           ; 
                       AND     $03                 
                       LD      L,$D4               
                       LD      (HL),A              
                       CPL                         
                       AND     $03                 
                       INC     A                   
                       LD      C,A                 
                       JP      L2476               ; 

```
> [!NOTE]
> **Ported to C:** [`l26d0`](../birds_vertical_movement.c#L36) in `birds_vertical_movement.c` (ASM: `26D0-26FD`)

```asm
                       .ORG $26D0
;
```

### L26D0:

```asm
                       LD      HL,M4BA8            ; 
                       LD      BC,$0800            
                       LD      DE,$8000            
```

### L26D9:

```asm
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       JP      Z,L26E5             ; 
                       LD      A,D                 
                       RLCA                        ; Multiply by 2
                       JP      NC,L26E4            ; 
                       LD      D,C                 
```

### L26E4:

```asm
                       LD      E,C                 
```

### L26E5:

```asm
                       INC     C                   
                       LD      A,L                 
                       SUB     B                   
                       LD      L,A                 
                       CP      $68                 
                       JP      NZ,L26D9            ; 
                       LD      A,(M4BD2)           ; 
                       ADD     A,D                 
                       ADD     A,E                 
                       AND     $1F                 
                       LD      (M4BD6),A           ; 
                       LD      A,E                 
                       SUB     D                   
                       LD      (M4BD7),A           ; 
                       RET                         

                       .ORG $2700
;*****************************************************************************
;* Handles the scoring, and the update of sound control HW.
;*****************************************************************************
```

### UpdateScoresAndSound:

```asm
                       LD      HL,GameOrAttract    ; 
                       LD      A,(HL)              ; get it
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if GameOrAttract is 'Attract mode'.
                       INC     L                   ;
                       LD      A,(HL)              ; get GameAndDemoOrSplash
                       AND     $01                 ; mask out 0000_0001 'Game for player 2'
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       ADD     $83                 ;
                       LD      L,A                 ;
                       LD      A,$FF               ;
                       LD      (M4397),A           ; 
                       LD      DE,M4370            ; 
```

### L2717:

```asm
                       CALL    L2748               ; add score values for all enemies hit.
                       INC     E                   ;
                       INC     E                   ;
                       INC     E                   ;
                       LD      A,E                 ;
                       CP      $80                 ; from $4370 to $4380
                       JP      NZ,L2717            ; 
                       LD      E,$9D               ;
                       LD      A,(GameState)       ; 
                       CP      $06                 ;
                       JP      NZ,L2739            ; 
                       LD      A,(DE)              ;
                       LD      B,A                 ;
                       LD      C,$00               ;
                       CALL    AddToScore          ; 
                       XOR     A                   ; A=0
                       LD      (DE),A              ;
                       LD      (M4397),A           ; 
```

### L2739:

```asm
                       LD      A,(M4397)           ; 
                       AND     A                   ; updates the zero flag
                       CALL    Z,L2768             ; if $4397 is 0.
                       CALL    UpdateSoundControlHW
                       JP      L3A10               ; 

                       .ORG $2748
;*****************************************************************************
;* Add score values for enemies hit.
;*****************************************************************************
```

### L2748:

```asm
                       LD      A,(DE)              ; get $4370
                       INC     E                   ;
                       CP      $01                 ;
                       RET     NZ                  ; if not 1
                       LD      A,(DE)              ;
                       AND     A                   ; updates the zero flag
                       RET     Z                   ;
                       RRCA                        ; enemy has been hit
                       RRCA                        ;
                       RRCA                        ;
                       RRCA                        ;
                       LD      B,A                 ;
                       AND     $F0                 ;
                       LD      C,A                 ;
                       LD      A,B                 ;
                       AND     $0F                 ;
                       LD      B,A                 ;
                       CALL    AddToScore          ; 
                       XOR     A                   ; Clear A Reg.
                       LD      (DE),A              ; clear the temp. score storage and ...
                       LD      (M4397),A           ; ... the first two digits of BCD score value
                       RET                         ;

                       .ORG $2768
;*****************************************************************************
;* Score-display
;* Together with `$43BE` (`BonusLivesAt`), these make a contiguous 3 byte BCD value
;* (`$43BD` = low, `$43BE` = middle, `$43BF` = high).
;* `$43BE` is loaded from the DIP switches to `$30/$40/$50/$60`,
;* the "extra ship at 3000/4000/5000/6000 points" setting,
;* and `$43BD`/`$43BF` are its companion digit bytes (zeroed at init).
;* This 3-byte threshold is checked against the player's score,
;* using the 3 byte BCD compare `L0314`.
;*****************************************************************************
```

### L2768:

```asm
                       PUSH    HL                  
                       LD      DE,$4261            ; end of the screen area of player 1 score
                       LD      B,$06               ; number of digits to print
                       LD      A,(GameAndDemoOrSplash)
                       AND     A                   ; updates the zero flag
                       JP      Z,$2778             ; if GameAndDemoOrSplash is 'Game and demo for player 1'
                       LD      DE,$4021            ; end of the screen area of player 2 score
                       CALL    PrintNumber         ; update the score on screen
                       POP     HL                  
                       LD      DE,M43BD            ; 
                       EX      DE,HL               
                       LD      A,(HL)              
                       INC     L                   
                       OR      (HL)                
                       RET     Z                   
                       INC     L                   
                       EX      DE,HL               
                       CALL    L0314               ; 
                       RET     NC                  
                       LD      A,(GameAndDemoOrSplash)
                       ADD     $90                 
                       LD      L,A                 
                       INC     (HL)                
                       CALL    UpdateLivesScreen   ; 
                       LD      A,$FF               
                       LD      (M436A),A           ; 
                       LD      L,$BE               
                       LD      A,(HL)              
                       LD      (HL),$00            
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       DEC     L                   
                       LD      (HL),A              
                       RET                         

                       .ORG $27A8
;*****************************************************************************
;* Update the sound control hardware registers
;*****************************************************************************
```

### UpdateSoundControlHW:

```asm
                       LD      HL,SoundControlA    ; ..
                       LD      A,(HL)              ; .. to
                       LD      (SOUNDCTLA),A       ; 60xx sound A
                       INC     L                   ; SoundControlB ..
                       LD      A,(HL)              ; .. to
                       LD      (SOUNDCTLB),A       ; 68xx sound B
                       OR      $0F                 ; 0000_1111
                       LD      (HL),A              ;
                       DEC     L                   ;
                       LD      (HL),$0F            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l27bd`](../sound_dispatcher.c#L34) in `sound_dispatcher.c` (ASM: `27BD-27EE`)

```asm
                       .ORG $27BD
;*****************************************************************************
;* Sound for player bullet or ship explosion.
;*****************************************************************************
```

### L27BD:

```asm
                       LD      HL,ParticleExplosion
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       JP      NZ,L27E2            ; if player ship was hit.
                       LD      L,$61               
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   
                       CP      $19                 
                       JP      NC,L27D8            ; 
                       DEC     (HL)                
                       LD      L,$8C               
                       LD      A,(HL)              
                       OR      $40                 
                       LD      (HL),A              
                       RET                         

                       .ORG $27D8
```

### L27D8:

```asm
                       LD      (HL),$18            
                       LD      L,$8C               
                       LD      A,(HL)              
                       AND     $BF                 
                       LD      (HL),A              
                       RET                         

                       .ORG $27E2
;*****************************************************************************
;* Sound for player ship explosion.
;*****************************************************************************
```

### L27E2:

```asm
                       CP      $40                 
                       JP      C,L27E9             ; 
                       LD      (HL),$40            
```

### L27E9:

```asm
                       DEC     (HL)                
                       LD      L,$8C               
                       LD      (HL),$8F            
                       RET                         

;*****************************************************************************
; h6-ic50.6a
;*****************************************************************************
                       .ORG $2800
; Foreground tiles of the player ship particles explosion:
; This is the character code to draw in each cell of the explosion field.
; Non zero bytes are the debris glyphs (`E0 E1 E2`, `C1 C2 C3`, `3D 3B 30 32 42 5A 4D 4F`, ...).
; `00` means "no particle in this cell".
```

### T2800:

```asm
                       .DB $00, $32, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $42, $42
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $E1, $00, $00, $E2, $00, $00
                       .DB $32, $00, $00, $00, $00, $00, $00, $00, $00, $E0, $00, $00, $40, $00, $00, $C3
                       .DB $00, $00, $00, $00, $00, $00, $DF, $00, $00, $E2, $00, $00, $E0, $00, $E1, $00
                       .DB $00, $30, $00, $00, $00, $00, $DE, $00, $00, $00, $C2, $00, $40, $00, $E0, $00
                       .DB $00, $00, $00, $30, $00, $30, $00, $5A, $00, $00, $E1, $00, $40, $00, $E2, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $30, $C1, $3E, $00, $E0, $00, $40, $C2, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $5A, $C1, $3E, $C8, $D8, $00, $00
                       .DB $E0, $E1, $C2, $E2, $E0, $00, $E1, $00, $C2, $00, $E2, $CE, $CA, $DA, $00, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $CF, $CF, $C3, $3F, $C2, $41, $E0, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $DE, $00, $3F, $00, $C2, $41, $00, $E1, $00
                       .DB $00, $00, $00, $00, $00, $3D, $DF, $3D, $00, $00, $E1, $00, $41, $00, $00, $C2
                       .DB $00, $00, $00, $3D, $00, $00, $00, $00, $00, $E0, $00, $00, $41, $00, $00, $E2
                       .DB $00, $00, $3D, $00, $00, $00, $00, $00, $E2, $00, $00, $00, $00, $4F, $00, $E0
                       .DB $00, $3B, $00, $00, $00, $00, $00, $00, $00, $C2, $00, $00, $00, $4F, $00, $00
                       .DB $00, $00, $3B, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $4D, $4D

; Control data of the player ship particles explosion:
; `T2900` is paired 1:1 with `T2800` and holds a 1 bit per cell "draw/erase" flag.
; The renderer `L2070`->`L2085`->`L20B0` selects a phase offset into both tables,
; then processes cells 8 at a time: it clears each screen cell, rotates a control byte,
; and only where a bit is set does it stamp the matching `T2800` tile.
```

### T2900:

```asm
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $20, $00, $38
                       .DB $00, $34, $00, $28, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $10, $00, $02, $00, $00
                       .DB $00, $01, $00, $00, $12, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $10, $00, $00, $80, $48, $00, $04
                       .DB $40, $08, $00, $50, $00, $00, $80, $10, $00, $00, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $10, $00, $00, $20, $44, $00, $00, $00, $02
                       .DB $10, $00, $00, $04, $00, $48, $20, $00, $00, $10, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $10, $00, $00, $00, $44, $08, $00, $00, $01, $00, $00
                       .DB $08, $00, $00, $02, $00, $00, $00, $84, $08, $00, $00, $20, $00, $00, $00, $00
                       .DB $00, $00, $00, $20, $00, $00, $00, $42, $02, $00, $80, $00, $00, $00, $00, $00
                       .DB $04, $00, $00, $01, $00, $00, $00, $00, $00, $82, $04, $00, $00, $20, $00, $00
                       .DB $00, $40, $00, $00, $01, $82, $00, $00, $40, $00, $00, $00, $00, $00, $00, $00
                       .DB $02, $00, $00, $00, $80, $00, $00, $00, $00, $00, $00, $81, $02, $00, $00, $40
                       .DB $02, $80, $00, $04, $00, $00, $40, $00, $00, $00, $00, $00, $00, $00, $00, $00
                       .DB $01, $00, $00, $00, $00, $00, $40, $00, $00, $00, $00, $00, $00, $02, $04, $08

; Foreground tiles of the mothership particles explosion
```

### T2A00:

```asm
                       .DB $00, $00, $00, $00, $00, $00, $00, $D2, $00, $00, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $DE, $00, $5E, $E0, $00, $00, $E1, $00, $00, $00, $00
                       .DB $00, $00, $C1, $00, $00, $CF, $53, $E2, $00, $D2, $E0, $00, $00, $D0, $00, $00
                       .DB $00, $00, $00, $DE, $00, $CE, $53, $E1, $D1, $E3, $00, $E1, $D3, $00, $00, $00
                       .DB $00, $00, $CF, $C0, $DE, $DF, $53, $D3, $E2, $00, $E2, $D2, $00, $5E, $E2, $00
                       .DB $00, $00, $00, $CE, $C1, $C2, $DE, $D2, $E1, $E3, $D1, $00, $D2, $00, $00, $00
                       .DB $00, $00, $00, $00, $DF, $DE, $C2, $CF, $E0, $D0, $E2, $E1, $C2, $C3, $00, $00
                       .DB $DF, $DE, $CF, $CE, $DF, $DE, $CF, $C8, $D8, $5E, $CE, $00, $CF, $DE, $DF, $CE
                       .DB $E0, $E3, $E2, $E1, $00, $E0, $D1, $CA, $DA, $D1, $D2, $D3, $D0, $D1, $D2, $D3
                       .DB $00, $00, $00, $00, $E3, $D2, $CE, $D2, $E2, $E0, $D3, $D1, $D3, $00, $00, $00
                       .DB $00, $00, $00, $E2, $D3, $CF, $DF, $E1, $D0, $E3, $E1, $D2, $00, $00, $00, $00
                       .DB $00, $00, $E1, $D0, $DE, $00, $DE, $E2, $00, $D3, $53, $E2, $5E, $C1, $C0, $00
                       .DB $00, $00, $00, $DF, $00, $00, $CF, $5E, $D1, $D2, $00, $53, $E3, $00, $00, $00
                       .DB $00, $00, $CE, $00, $CF, $00, $CE, $D2, $D2, $00, $53, $00, $5E, $E0, $00, $00
                       .DB $00, $00, $00, $00, $00, $DE, $00, $E1, $D3, $00, $E2, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $00, $00, $5E, $D0, $00, $00, $00, $00, $00, $00, $00

; Control data of the mothership particles explosion
```

### T2B00:

```asm
                       .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $80, $01, $40, $02, $80, $05
                       .DB $A0, $01, $40, $02, $00, $01, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $00, $00, $80, $00, $00, $01, $20, $04, $00, $01, $40, $12
                       .DB $48, $02, $80, $01, $20, $04, $00, $00, $00, $01, $00, $00, $00, $00, $00, $00
                       .DB $00, $00, $00, $00, $80, $00, $00, $02, $10, $08, $00, $01, $80, $04, $A0, $21
                       .DB $84, $05, $20, $02, $80, $01, $10, $08, $00, $00, $00, $01, $00, $00, $00, $00
                       .DB $00, $00, $80, $00, $00, $04, $08, $10, $00, $01, $40, $00, $40, $0A, $10, $40
                       .DB $02, $08, $40, $00, $10, $04, $80, $02, $08, $10, $00, $00, $00, $01, $00, $00
                       .DB $80, $00, $00, $08, $04, $20, $00, $02, $20, $00, $20, $14, $00, $01, $08, $80
                       .DB $01, $10, $80, $02, $20, $00, $08, $04, $80, $02, $04, $20, $00, $00, $00, $01
                       .DB $01, $01, $01, $01, $01, $04, $20, $00, $10, $28, $80, $02, $04, $00, $00, $04
                       .DB $20, $20, $00, $04, $40, $01, $10, $00, $04, $08, $80, $04, $00, $00, $00, $00
                       .DB $00, $00, $00, $08, $20, $00, $88, $10, $00, $44, $00, $00, $00, $10, $02, $00
                       .DB $08, $40, $00, $00, $00, $08, $40, $00, $08, $01, $00, $10, $80, $04, $00, $00
                       .DB $00, $00, $20, $00, $84, $20, $00, $08, $00, $00, $00, $00, $00, $20, $01, $00
                       .DB $04, $80, $00, $00, $00, $00, $00, $10, $40, $00, $04, $01, $00, $00, $80, $00

; Closed loop pattern table part 2:
; Used for single or multiple aliens, depending on the game round.
; Pattern 18
```

### T2C00:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $06, $06, $1E
                       .DB $03, $03, $1F, $05, $05, $1C, $04, $04, $04, $1D, $06, $06, $1A, $04, $04, $04
                       .DB $1B, $05, $05, $05, $05, $18, $1F, $07, $07, $07, $07, $07, $07, $07, $07, $07
                       .DB $00, $FF, $FF, $FF
; Pattern 19
```

### T2C34:

```asm
                       .DB $05, $05, $1C, $04, $1D, $0A, $0A, $0A, $0A, $0A, $0A, $06
                       .DB $06, $1E, $03, $03, $1F, $05, $1C, $04, $04, $1D, $0A, $06, $06, $1E, $03, $03
                       .DB $1F, $05, $1C, $04, $04, $1D, $0A, $06, $06, $1E, $03, $03, $1F, $05, $1C, $04
                       .DB $04, $1D, $0A, $06, $1E, $03, $1F, $05, $1C, $04, $1D, $06, $1E, $03, $03, $03
                       .DB $03, $15, $16, $17, $01, $01, $05, $05, $01, $01, $05, $05, $01, $01, $05, $05
                       .DB $01, $01, $05, $05, $02, $02, $18, $07, $07, $07, $00, $FF, $FF, $FF, $FF, $FF
; Pattern 20 (phase 3)
```

### T2C90:

```asm
                       .DB $1C, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1D
                       .DB $06, $06, $06, $06, $06, $06, $06, $1E, $03, $03, $03, $03, $03, $03, $1F, $05
                       .DB $05, $05, $05, $1C, $04, $04, $1D, $06, $09, $09, $09, $1E, $03, $07, $07, $08
                       .DB $08, $07, $07, $08, $07, $00, $FF, $FF
; Pattern 21 (phase 3)
```

### T2CC8:

```asm
                       .DB $05, $05, $05, $05, $1C, $04, $04, $04
                       .DB $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1D, $09, $09, $09, $09
                       .DB $0A, $0A, $0A, $09, $0A, $0A, $06, $1E, $03, $03, $03, $1F, $05, $05, $18, $03
                       .DB $19, $06, $06, $1E, $03, $03, $1F, $05, $05, $05, $05, $05, $05, $05, $00, $FF
; Pattern 22
```

### T2D00:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $06, $1E, $03, $03, $03, $03, $03, $03, $03, $03
                       .DB $03, $03, $03, $03, $03, $03, $1F, $05, $05, $1C, $04, $04, $04, $04, $04, $04
                       .DB $04, $04, $04, $04, $1D, $06, $06, $1E, $03, $03, $03, $03, $03, $03, $1F, $05
                       .DB $05, $05, $05, $05, $1C, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1B
                       .DB $00, $FF, $FF, $FF
; Pattern 23 (phase 3)
```

### T2D44:

```asm
                       .DB $05, $05, $05, $18, $03, $03, $03, $03, $03, $03, $03, $03
                       .DB $03, $19, $06, $06, $1A, $04, $04, $1B, $05, $05, $18, $03, $03, $03, $03, $03
                       .DB $03, $03, $19, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $1A, $04, $04
                       .DB $1B, $05, $05, $1C, $04, $04, $1D, $06, $06, $1A, $04, $04, $1B, $05, $05, $05
                       .DB $05, $05, $05, $05, $00, $FF, $FF, $FF
; Pattern 24 (phase 3)
```

### T2D88:

```asm
                       .DB $1C, $04, $04, $1D, $06, $06, $09, $0A
                       .DB $0A, $09, $09, $09, $16, $17, $14, $03, $03, $03, $1F, $05, $05, $1C, $04, $04
                       .DB $1D, $06, $06, $1E, $03, $03, $03, $03, $07, $07, $08, $08, $07, $07, $05, $05
                       .DB $1C, $04, $04, $04, $04, $04, $04, $04, $1D, $1A, $04, $1B, $00, $FF, $FF, $FF
; Pattern 25 (phase 3)
```

### T2DC0:

```asm
                       .DB $14, $03, $03, $19, $06, $0A, $0A, $09, $09, $09, $0A, $12, $13, $10, $11, $12
                       .DB $13, $10, $11, $12, $13, $10, $04, $04, $04, $04, $1B, $05, $18, $03, $19, $06
                       .DB $1A, $04, $1B, $05, $18, $07, $07, $07, $08, $08, $07, $07, $07, $03, $03, $19
                       .DB $0D, $0E, $00, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
; Pattern 26
; Used for all aliens.
; This is the 'Angry movement pattern A'.
; At the end of that sequence, the alien formation is further down
; and the 'phase' is increased by 1.
```

### T2E00:

```asm
                       .DB $0B, $0C, $0D, $0E, $02, $02, $02, $02, $0B, $0C, $0D, $0E, $01, $01, $14, $15
                       .DB $16, $17, $01, $01, $05, $05, $05, $05, $02, $02, $02, $02, $00, $FF, $FF, $FF
; Pattern, 27 (phase 3)
```

### T2E20:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E, $02, $02, $02, $02, $02, $02, $02, $02
                       .DB $05, $05, $01, $05, $05, $01, $05, $05, $01, $05, $05, $01, $00, $FF, $FF, $FF
; Pattern 28
; Used for all aliens.
; This is the 'Angry movement pattern B'.
; At the end of that sequence, the alien formation is further down
; and the 'phase' is increased by 1.
```

### T2E40:

```asm
                       .DB $0B, $0C, $0D, $0E, $01, $01, $01, $18, $03, $19, $06, $06, $1A, $04, $1B, $05
                       .DB $18, $03, $19, $06, $06, $1A, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1B
                       .DB $05, $05, $05, $01, $01, $01, $01, $01, $00, $FF, $FF, $FF
; Pattern, 29 (phase 3)
```

### T2E6C:

```asm
                       .DB $0B, $0C, $0D, $0E
                       .DB $01, $01, $0B, $0C, $0D, $0E, $01, $01, $05, $05, $05, $05, $01, $01, $0B, $0C
                       .DB $0D, $0E, $01, $01, $07, $08, $08, $07, $08, $08, $08, $07, $00, $FF, $FF, $FF
; Pattern, 30
```

### T2E90:

```asm
                       .DB $14, $15, $16, $17, $14, $15, $16, $17, $14, $03, $03, $03, $03, $03, $03, $03
                       .DB $03, $03, $03, $03, $03, $19, $09, $0A, $0A, $09, $09, $0A, $0A, $12, $13, $08
                       .DB $08, $07, $07, $08, $08, $08, $08, $04, $04, $04, $11, $12, $13, $10, $11, $12
                       .DB $13, $00, $FF, $FF
; Pattern, 31
```

### T2EC4:

```asm
                       .DB $10, $11, $12, $13, $10, $11, $12, $13, $10, $04, $04, $04
                       .DB $04, $04, $04, $04, $04, $04, $0A, $0A, $0A, $09, $0A, $09, $0A, $09, $16, $17
                       .DB $14, $03, $03, $03, $07, $07, $07, $07, $03, $19, $06, $1A, $04, $1B, $05, $18
                       .DB $07, $07, $07, $07, $00, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
; Pattern, 32
```

### T2F00:

```asm
                       .DB $05, $1C, $04, $1D, $06, $06, $06, $06, $06, $09, $09, $09, $0A, $0A, $0A, $09
                       .DB $09, $16, $17, $14, $1F, $05, $18, $03, $19, $06, $1E, $03, $1F, $05, $18, $03
                       .DB $19, $06, $1E, $03, $1F, $05, $05, $1C, $08, $08, $08, $08, $08, $08, $08, $08
                       .DB $00, $FF, $FF, $FF
; Pattern, 33
```

### T2F34:

```asm
                       .DB $05, $18, $03, $19, $06, $06, $06, $06, $0A, $0A, $09, $09
                       .DB $0A, $0A, $09, $0A, $0A, $12, $13, $10, $1B, $05, $1C, $04, $1D, $1E, $1F, $1C
                       .DB $04, $1D, $06, $1A, $04, $04, $1B, $05, $18, $07, $07, $07, $07, $08, $07, $07
                       .DB $07, $07, $00, $FF
; Pattern, 34
```

### T2F64:

```asm
                       .DB $0B, $0C, $0D, $0E, $0B, $0C, $1E, $03, $19, $06, $1E, $03
                       .DB $19, $06, $1E, $03, $19, $06, $1E, $1F, $1C, $1D, $1E, $03, $03, $03, $1F, $05
                       .DB $18, $03, $19, $06, $1E, $03, $1F, $05, $08, $08, $08, $08, $08, $08, $08, $07
                       .DB $07, $08, $08, $08, $08, $08, $00, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
; Pattern, 35
```

### T2FA0:

```asm
                       .DB $05, $05, $18, $03, $03, $03, $03, $03, $03, $03, $03, $19, $06, $06, $06, $06
                       .DB $06, $06, $06, $1A, $04, $1B, $05, $18, $03, $03, $03, $03, $19, $06, $06, $06
                       .DB $1A, $04, $1B, $05, $18, $03, $03, $03, $03, $19, $06, $06, $06, $1A, $04, $1B
                       .DB $05, $18, $03, $03, $03, $03, $19, $06, $06, $06, $1A, $04, $1B, $05, $18, $03
                       .DB $03, $19, $06, $06, $1A, $11, $12, $13, $02, $02, $02, $05, $05, $02, $02, $02
                       .DB $05, $05, $02, $02, $02, $05, $1C, $08, $08, $07, $07, $08, $08, $08, $00, $FF

;*****************************************************************************
; h7-ic51.7a
;*****************************************************************************

;*****************************************************************************
;* AlienBehaviorUpdate.
;* This is the 'core of the matter'!
;* The 'core of the matter': drives every alien attack pattern and the
;* randomized selection. One sub-task runs per frame, chosen round-robin by
;* Counter93 (0-7) via jump table T3018. The sub-tasks cooperate through the
;* behavior state machine at $4350 and the control block $4350-$435B.
;* The selected patterns do always fit on the screen,
;* even if the alien formation is further down. (phase 1, 2, 3)
;*****************************************************************************
```

### L3000:

```asm
                       LD      HL,Counter93        ; 
                       LD      A,(HL)              ; load and save ram value
                       INC     (HL)                ; increment Counter93
                       AND     $07                 ; masc out 0000_0111 the saved value in order to count from 0 to 7
                       LD      HL,T3018            ; base of jump table
                       RLCA                        ; Multiply by 2 to get a 2 byte offset
                       ADD     A,L                 ;
                       LD      L,A                 ;
                       LD      A,(HL)              ; get MSB from jump table
                       INC     HL                  ;
                       LD      L,(HL)              ; get LSB from jump table
                       LD      H,A                 ;
                       JP      (HL)                ; jump to the corresponding function
;*****************************************************************************
;* Sub-task 7: Do nothing.
;*****************************************************************************
```

### L3012:

```asm
                       RET                         ;

                       .ORG $3018
;
```

### T3018:

```asm
                       .MSFIRST
                       .DW L3264 ; 0 -> L3264  install chosen pattern / rotate start pointer
                       .DW L3028 ; 1 -> L3028  'Angry movement A/B' (push formation down)
                       .DW L30BA ; 2 -> L30BA  tick attack-delay + group timers
                       .DW L3124 ; 3 -> L3124  decide how many aliens attack
                       .DW L315A ; 4 -> L315A  pick a random alien to attack
                       .DW L31B4 ; 5 -> L31B4  choose the closed-loop swoop pattern
                       .DW L322C ; 6 -> L322C  confirm pattern start across the grid
                       .DW L3012 ; 7 -> L3012  (nop)

;*****************************************************************************
;* Sub-task 1: 'Angry movement pattern A/B' (pattern 26/28).
;* Every $4358 frames, escalate $4357 and re-arm the downward-push pattern
;* (T2E00/T2E40), so the formation creeps further down the screen.
;*****************************************************************************
```

### L3028:

```asm
                       LD      HL,M4357            ; 
                       LD      A,(HL)              
                       CP      $03                 
                       RET     NC                  ; if >= 3
                       LD      L,$50               
                       LD      A,(HL)              ; get $4350
                       CP      $04                 
                       RET     NC                  ; if >= 4
                       LD      L,$58               
                       LD      A,(HL)              ; get $4358
                       AND     A                   ; updates the zero flag
                       JP      Z,L305C             ; 
                       DEC     (HL)                ; $4358
                       RET     NZ                  
                       DEC     L                   
                       INC     (HL)                ; $4357
                       LD      L,$50               
                       LD      (HL),$04            ; set $4350
                       LD      L,$53               
                       LD      (HL),$10            ; set $4353
                       INC     L                   
                       LD      (HL),$50            ; set $4354
                       LD      L,$51               
                       LD      (HL),$2E            ; set $4351
                       INC     L                   
                       LD      (HL),$00            ; clear $4352
                       LD      A,(PlayerShipX)     ; 
                       RRCA                        
                       RET     C                   
                       LD      (HL),$40            ; set $4352
                       RET                         

                       .ORG $305C
;*****************************************************************************
;* End of movement pattern reached. Get the next start pointer.
;*****************************************************************************
```

### L305C:

```asm
                       CALL    L3074               ; 
                       LD      HL,M4357            ; 
                       LD      A,(HL)              ; get $4357
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       NOP                         ;
                       NOP                         ;
                       ADD     A,C                 ;
                       ADD     $07                 ;
                       LD      L,$58               ;
                       LD      (HL),A              ; store to $4358
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l3074_breakout_delay`](../alien_logic.c#L501) in `alien_logic.c` (ASM: `3074-30A8`)

```asm
                       .ORG $3074
;*****************************************************************************
;* Build a scaled random magnitude in C from round, level, aliens-left and
;* a random number. Used to size timer spans and attacker counts.
;*****************************************************************************
```

### L3074:

```asm
                       LD      HL,LevelAndRound    ; 
                       LD      A,(HL)              
                       RRCA                        
                       NOP                         
                       AND     $07                 ; 0000_0111
                       LD      B,A                 
                       LD      A,$07               
                       SUB     B                   
                       LD      C,A                 
                       LD      A,(HL)              ; get LevelAndRound
                       CP      $80                 
                       JP      C,L3089             ; 
                       LD      A,$70               
```

### L3089:

```asm
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       AND     $07                 
                       LD      B,A                 
                       LD      A,$07               
                       SUB     B                   
                       ADD     A,C                 
                       LD      C,A                 
                       LD      A,(AliensLeft)      ; 
                       SUB     $05                 
                       JP      NC,L309F            ; 
                       LD      A,$10               
```

### L309F:

```asm
                       ADD     A,C                 
                       LD      C,A                 
                       CALL    GetRandomNumber     ; 
                       AND     $07                 
                       ADD     A,C                 
                       LD      C,A                 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`get_random_number`](../utilities.c#L386) in `utilities.c` (ASM: `30AA-30B8`)

```asm
                       .ORG $30AA
;*****************************************************************************
;* Free running counter ($439B) and the X position of the player ship ($43C2)
;* is the base for a pseudo random number.
;* Returns A-register: $00 to $0F.
;*****************************************************************************
```

### GetRandomNumber:

```asm
                       LD      HL,Counter9A+$1     ; 
                       LD      A,(HL)              ;
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       AND     $07                 ; mask out 0000_0111 in order to count from 0 to 7
                       LD      L,$C2               ; get $43C2 PlayerShipX
                       ADD     A,(HL)              ; add to counter value
                       AND     $0F                 ; mask out 0000_1111
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`l30ba`](../alien_logic.c#L562) in `alien_logic.c` (ASM: `30BA-30D8, 30E4-310F, 3112-3121`)

```asm
                       .ORG $30BA
;*****************************************************************************
;* Sub-task 2: tick the three staggered group timers and the attack delay.
;* When the delay $4355 expires (in state 0) begin a new attack (state 1).
;*****************************************************************************
```

### L30BA:

```asm
                       LD      HL,M4358            ; 
                       CALL    L30DA               ; for $4359
                       CALL    L30DA               ; for $435A
                       CALL    L30DA               ; for $435B
                       LD      L,$50               
                       LD      A,(HL)              ; get $4350
                       AND     A                   ; updates the zero flag
                       RET     NZ                  ; if <> 0
                       LD      L,$55               
                       LD      A,(HL)              ; get $4355
                       AND     A                   ; updates the zero flag
                       JP      Z,L30E4             ; if 0
                       DEC     (HL)                
                       RET     NZ                  
                       LD      L,$50               
                       LD      (HL),$01            
                       RET                         

                       .ORG $30DA
;*****************************************************************************
;* Tick one timer (does not go below 0).
;*****************************************************************************
```

### L30DA:

```asm
                       INC     L                   
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if 4359, 435A, 435B = 0
                       DEC     (HL)                
                       RET                         

                       .ORG $30E4
;*****************************************************************************
;* Recompute the attack delay $4355 and reload the 3 group timers.
;*****************************************************************************
```

### L30E4:

```asm
                       CALL    L3074               ; 
                       LD      HL,Counter9A        ; 
                       LD      A,(HL)              
                       CP      $10                 
                       JP      C,L30F2             ; 
                       LD      A,$0F               
```

### L30F2:

```asm
                       LD      B,A                 
                       LD      A,$0F               
                       SUB     B                   
                       ADD     A,C                 
                       LD      C,A                 
                       LD      B,$01               
                       LD      L,$58               
                       CALL    L3112               ; for $4359
                       CALL    L3112               ; for $435A
                       CALL    L3112               ; for $435B
                       LD      A,C                 
                       RRCA                        
                       RRCA                        
                       AND     $3F                 ; 0011_1111
                       ADD     $01                 
                       LD      L,$55               
                       LD      (HL),A              ; set $4355
                       RET                         

                       .ORG $3112
;*****************************************************************************
;* Reload one group timer (only if it is currently 0).
;*****************************************************************************
```

### L3112:

```asm
                       INC     L                   
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     NZ                  ; if <> 0
                       LD      A,C                 
                       RRCA                        
                       AND     $7F                 ; 0111_1111
                       LD      C,A                 
                       LD      A,B                 
                       AND     A                   ; updates the zero flag
                       RET     Z                   
                       DEC     B                   
                       LD      (HL),$0C            
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3124`](../alien_logic.c#L607) in `alien_logic.c` (ASM: `3124-314E`)

```asm
                       .ORG $3124
;*****************************************************************************
;* Sub-task 3: in state 1, advance to state 2 and compute the number of
;* aliens that will fly the swoop ($4353), from round + random, reduced as
;* the escalation counter $4357 grows.
;*****************************************************************************
```

### L3124:

```asm
                       LD      HL,M4350            ; 
                       LD      A,(HL)              
                       CP      $01                 
                       RET     NZ                  ; if <> 1
                       LD      (HL),$02            ; set $4350
                       LD      L,$B8               
                       LD      A,(HL)              ; get LevelAndRound
                       RRCA                        
                       RRCA                        
                       AND     $0F                 
                       ADD     $05                 
                       CP      $11                 
                       JP      C,L313D             ; 
                       LD      A,$05               
```

### L313D:

```asm
                       LD      L,$57               
                       SUB     (HL)                
                       LD      B,A                 
                       CALL    GetRandomNumber     ; 
                       INC     A                   
                       CP      B                   
                       JP      C,L314B             ; 
                       LD      A,$01               
```

### L314B:

```asm
                       LD      L,$53               
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l315a`](../alien_logic.c#L629) in `alien_logic.c` (ASM: `315A-318E, 3192-31AD`)

```asm
                       .ORG $315A
;*****************************************************************************
;* Sub-task 4: in state 2, scan the 16-alien grid from a random offset for
;* an active alien whose control bytes match the current start pointer.
;* The first match is recorded in $4354 and state advances to 3.
;*****************************************************************************
```

### L315A:

```asm
                       LD      HL,M4350            ; 
                       LD      A,(HL)              
                       CP      $02                 
                       RET     NZ                  ; if <> 2
                       CALL    GetRandomNumber     ; 
                       NOP                         
                       LD      B,A                 
                       RLCA                        ; Multiply by 2
                       ADD     $50                 
                       LD      L,A                 
                       LD      H,$4B               
                       LD      A,B                 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ;
                       ADD     $70                 
                       LD      E,A                 
                       LD      D,$4B               
                       LD      C,$10               
                       LD      A,C                 
                       SUB     B                   
                       LD      B,A                 
```

### L3179:

```asm
                       CALL    L3192               ; 
                       INC     DE                  
                       INC     DE                  
                       INC     DE                  
                       INC     DE                  
                       INC     HL                  
                       INC     HL                  
                       DEC     B                   
                       JP      NZ,L318A            ; 
                       LD      E,$70               
                       LD      L,$50               
```

### L318A:

```asm
                       DEC     C                   
                       JP      NZ,L3179            ; 
                       RET                         

                       .ORG $3192
;*****************************************************************************
;* Match test: active alien whose control bytes equal the start pointer.
;*****************************************************************************
```

### L3192:

```asm
                       LD      A,(DE)              
                       AND     $08                 
                       RET     Z                   
                       LD      A,(M4394)           ; 
                       CP      (HL)                
                       RET     NZ                  
                       LD      A,(M4356)           ; 
                       INC     L                   
                       LD      B,(HL)              
                       DEC     L                   
                       CP      B                   
                       RET     NZ                  
                       LD      A,L                 
                       LD      (M4354),A           ; 
                       LD      A,$03               
                       LD      (M4350),A           ; 
                       POP     HL                  
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l31b4`](../alien_logic.c#L662) in `alien_logic.c` (ASM: `31B4-320D, 3210-3228`)

```asm
                       .ORG $31B4
;*****************************************************************************
;* Sub-task 5: in state 3, choose the closed-loop swoop pattern for the
;* selected alien based on its position relative to the player (T3300),
;* its row/phase (L3210 + T3310) and a random pick (T3330). Pattern pointer
;* is stored at $4351/$4352 and state advances to 5.
;*****************************************************************************
```

### L31B4:

```asm
                       LD      A,(M4350)           ; 
                       CP      $03                 
                       RET     NZ                  ; if <> 3
                       LD      A,(M4354)           ; 
                       SUB     $50                 
                       RLCA                        ; Multiply by 2
                       ADD     $72                 
                       LD      L,A                 
                       LD      H,$4B               
                       LD      B,(HL)              
                       INC     L                   
                       LD      D,(HL)              
                       LD      A,(PlayerShipX)     ; 
                       LD      C,$04               
                       CP      B                   
                       JP      NC,L31D6            ; 
                       LD      C,A                 
                       LD      A,B                 
                       LD      B,C                 
                       LD      C,$00               
```

### L31D6:

```asm
                       SUB     B                   
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       AND     $07                 
                       ADD     $00                 ; LSB for table T3300
                       LD      L,A                 
                       LD      H,$33               ; get MSB for table T3300
                       LD      A,(HL)              
                       ADD     A,C                 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       LD      C,A                 
                       NOP                         
                       NOP                         
                       NOP                         
                       LD      A,(M4357)           ; 
                       LD      B,A                 
                       CALL    L3210               ; 
                       LD      A,C                 
                       ADD     A,B                 
                       ADD     $10                 ; LSB for table T3310
                       LD      L,A                 
                       LD      H,$33               ; get MSB for table T3310
                       LD      C,(HL)              
                       CALL    GetRandomNumber     ; 
                       AND     $06                 
                       ADD     A,C                 
                       LD      L,A                 
                       LD      H,$33               ; get MSB for table T3330 (base adresses of closed loops pattern tables for aliens)
                       LD      A,(HL)              
                       INC     L                   
                       LD      B,(HL)              
                       LD      HL,M4350            ; 
                       LD      (HL),$05            
                       INC     L                   
                       LD      (HL),A              
                       INC     L                   
                       LD      (HL),B              
                       RET                         

                       .ORG $3210
;*****************************************************************************
;* Get the attack phase at Reg. B (0..3) from the alien Y (only when one attacker).
;*****************************************************************************
```

### L3210:

```asm
                       LD      A,(M4353)           ; Number of aliens doing the closed loop pattern
                       CP      $01                 ; 
                       RET     NZ                  ; only meaningful for 1
                       LD      A,D                 ; alien screen coordinate Y
                       LD      B,$00               ; return B = phase 0
                       CP      $58                 ; 
                       RET     C                   ; if alien screen coordinate Y < $58
                       LD      B,$01               ; return B = phase 1
                       CP      $78                 ; 
                       RET     C                   ; if alien screen coordinate Y < $78
                       LD      B,$02               ; return B = phase 2
                       CP      $98                 ; 
                       RET     C                   ; if alien screen coordinate Y < $98
                       LD      B,$03               ; return B = phase 3
                       RET                         ; 

```
> [!NOTE]
> **Ported to C:** [`l322c`](../alien_logic.c#L718) in `alien_logic.c` (ASM: `322C-325E`)

```asm
                       .ORG $322C
;*****************************************************************************
;* Sub-task 6: in state 4 (angry path), verify all active aliens carry the
;* start pointer, then advance to state 6.
;*****************************************************************************
```

### L322C:

```asm
                       LD      A,(M4350)           ; 
                       CP      $04                 
                       RET     NZ                  ; if <> 4
                       LD      HL,M4B50            ; Pointer to alien movement pattern
                       LD      DE,M4B70            ; Alien data structure (grid)
                       LD      A,(M4356)           ; 
                       LD      C,A                 
                       LD      A,(M4394)           ; 
                       LD      B,A                 
```

### L3240:

```asm
                       LD      A,(DE)              
                       AND     $08                 
                       JP      Z,L324E             ; 
                       LD      A,(HL)              
                       CP      B                   
                       RET     NZ                  
                       INC     L                   
                       LD      A,(HL)              
                       DEC     L                   
                       CP      C                   
                       RET     NZ                  
```

### L324E:

```asm
                       INC     L                   
                       INC     L                   
                       LD      A,E                 
                       ADD     $04                 
                       LD      E,A                 
                       CP      $B0                 
                       JP      NZ,L3240            ; 
                       LD      A,$06               
                       LD      (M4350),A           ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3264`](../alien_logic.c#L459) in `alien_logic.c` (ASM: `3264-32AF`)

```asm
                       .ORG $3264
;*****************************************************************************
;* Sub-task 0: rotate the 'start value list' pointer $4356 (0-15). If a
;* pattern is fully prepared (state >= 5), reset to state 0 and write the
;* chosen closed-loop pattern pointer into the movement slots ($4B50) of the
;* matching aliens - launching the actual swoop.
;*****************************************************************************
```

### L3264:

```asm
                       LD      HL,M4395            ; 
                       LD      A,(HL)              ;
                       LD      (M4356),A           ; 
                       INC     A                   
                       AND     $0F                 ; 0000_1111
                       LD      (HL),A              
                       LD      L,$50               
                       LD      A,(HL)              ; get $4350
                       CP      $05                 
                       RET     C                   ; if < 5
                       LD      (HL),$00            ; clear $4350
                       LD      L,$53               
                       LD      C,(HL)              ; get $4353
                       INC     L                   
                       LD      L,(HL)              ; get $4354
                       LD      H,$4B               
                       LD      A,(M4356)           ; 
                       LD      D,A                 
                       LD      A,(M4394)           ; 
                       LD      E,A                 
                       LD      A,L                 
                       SUB     $50                 
                       RRCA                        
                       LD      B,A                 
                       LD      A,$10               
                       SUB     B                   
                       LD      B,A                 
```

### L328F:

```asm
                       LD      A,(HL)              
                       INC     L                   
                       CP      E                   
                       JP      NZ,L32A4            ; 
                       LD      A,(HL)              
                       CP      D                   
                       JP      NZ,L32A4            ; 
                       DEC     L                   
                       LD      A,(M4351)           ; 
                       LD      (HL),A              
                       INC     L                   
                       LD      A,(M4352)           ; 
                       LD      (HL),A              
```

### L32A4:

```asm
                       INC     L                   
                       DEC     B                   
                       JP      NZ,L32AB            ; 
                       LD      L,$50               
```

### L32AB:

```asm
                       DEC     C                   
                       JP      NZ,L328F            ; 
                       RET                         

;*****************************************************************************
;* Bird-level init:
;* First clears `$4B70`–`$4BAF`, then copies `BirdsLeft × 8` bytes from table T3F80
;* into the object array, choosing the source block by level.
;* So when a full wave starts (`BirdsLeft = 8`, `C = $40`),
;* the source LSB resolves to `$80` -> it copies the whole table starting at `$3F80` into `$4B70`,
;* meaning `$3F80`–`$3F87` becomes the live control block of bird #0 at `$4B70`.
;* (If fewer birds are present, both source and destination are offset toward the end of their respective arrays,
;* so the remaining birds are taken from the tail of the table.)
;* The `LevelAndRound` bit test redirects the source to `$3FC0` for levels 4/9.
;* After the copy, these objects are driven by the bird routines — e.g. `DrawFirst4BirdObjects`/`DrawSecond4BirdObjects`
;* and `L35B0`, all of which iterate the array in 8 byte steps (`ADD $08`) over `$4B70`–`$4BAF`, confirming the 8 byte-per-bird structure.
;*****************************************************************************
```

### L32B0:

```asm
                       LD      HL,M4350            ; 
                       LD      B,$30               ; 4350 to 437F
                       CALL    ClearBbytesAtHL     ; 
                       LD      L,$9A               ;
                       LD      B,$04               ; 439A to 439D
                       CALL    ClearBbytesAtHL     ; 
                       LD      A,(BirdsLeft)       ; 
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if no BirdsLeft
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       LD      C,A                 
                       LD      HL,M4B70            ; 
                       LD      B,$40               
                       CALL    ClearBbytesAtHL     ; 
                       LD      D,$4B               
                       LD      H,$3F               
                       LD      A,$40               
                       SUB     C                   
                       ADD     $70                 
                       LD      E,A                 
                       ADD     $10                 
                       LD      L,A                 
                       LD      B,C                 
                       LD      A,(LevelAndRound)   ; 
                       RRCA                        
                       RRCA                        
                       JP      NC,CopyBbytesHLtoDE ; 
                       LD      A,L                 
                       ADD     $40                 
                       LD      L,A                 
                       JP      CopyBbytesHLtoDE    ; 

                       .ORG $3300
; Maps "distance from player" -> T3310 group.
```

### T3300:

```asm
                       .DB $00, $01, $02, $02, $03, $03, $03, $03
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF

; Pointer table for T3330.
; T1160, T1020, T1020, T10A8
; T1160, T1020, T1020, T2C90...
; The random values (0, 2, 4 or 6) are added in order to
; address the rest of T3330.
```

### T3310:

```asm
                       .DB $88, $90, $98, $A0, $68, $70, $78, $80, $48, $50, $58, $60, $48, $30, $38, $40
                       .DB $88, $90, $98, $A0, $A8, $B0, $B8, $C0, $C8, $D0, $D8, $E0, $C8, $E8, $F0, $F8

; Base adresses of closed loop pattern tables for aliens:
; The actual flight paths the aliens follow.
; T1130, T2C00, T2FA0...
```

### T3330:

```asm
                       .MSFIRST
                       .DW T1130, T2C00, T2FA0, T2C00, T2EC4, T2FA0, T2F34, T2FA0
                       .DW T2CC8, T2EC4, T2E20, T2EC4, T1130, T139C, T13D0, T2C00
                       .DW T1130, T1328, T2C00, T2F34, T11A4, T2C90, T2F34, T2FA0
                       .DW T2C90, T2CC8, T2E20, T2EC4, T1160, T1354, T139C, T13D0
                       .DW T1020, T1064, T11A4, T1328, T1020, T11A4, T1200, T2F34
                       .DW T2C90, T2CC8, T2DC0, T2E20, T1160, T1244, T1288, T1354
                       .DW T1020, T1064, T1200, T1244, T1020, T1200, T1020, T1200
                       .DW T10A8, T2D88, T10A8, T2DC0, T11D0, T12CA, T1300, T1354
                       .DW T1020, T1064, T10D4, T1300, T1020, T10D4, T1200, T2F00
                       .DW T2D00, T2D44, T2D88, T2E6C, T1100, T11D0, T12CA, T2F64
                       .DW T1100, T1300, T2F64, T2F00, T10D4, T2D00, T2F00, T2C34
                       .DW T2D00, T2D44, T2E6C, T2E90, T1100, T2C34, T2F64, T2F64
                       .DW T2E90, T2F00, T2C34, T2C34, T2D44, T2E6C, T2E90, T2E90

;*****************************************************************************
;* Game level 7
;* birds level including 'fade in'
;*****************************************************************************
```

### L3400:

```asm
                       CALL    PlayerUpdate        ; Updates the player ship, player bullet and the shield.
                       CALL    L3800               ; Collision detection for birds
                       CALL    L2600               ; birds vertical movement update (with 58xx scroll register)
                       CALL    L3800               ; Collision detection for birds
                       CALL    L3980               ; 
                       LD      A,(BirdsLeft)       ; 
                       AND     A                   ; updates the zero flag
                       JP      Z,L3462             ; if no BirdsLeft.
                       CP      $04                 ;
                       JP      NC,L3438            ; 
                       CALL    DrawFirst4BirdObjects ; including the horizontal movement update
                       CALL    DrawSecond4BirdObjects ; including the horizontal movement update
                       CALL    L3560               ; 
                       CALL    L3498               ; 
                       CALL    L34AA               ; 
                       LD      A,(Counter9A+$1)    ; 
                       RRCA                        
                       JP      C,L0FC0             ; Handle animations for killed aliens
                       CALL    L3930               ; 
                       JP      L0C40               ; 

                       .ORG $3438
;
```

### L3438:

```asm
                       LD      A,(Counter9A+$1)    ; 
                       RRCA                        
                       JP      C,L3452             ; 
                       CALL    DrawFirst4BirdObjects
                       CALL    L3560               ; 
                       CALL    L3498               ; 
                       CALL    L3930               ; 
                       JP      L0C40               ; 

```
> [!NOTE]
> **Ported to C:** [`update_second_bird_bank`](../bird_wave_behavior.c#L14) in `bird_wave_behavior.c` (ASM: `3452-345B`)

```asm
                       .ORG $3452
;
```

### L3452:

```asm
                       CALL    DrawSecond4BirdObjects
                       CALL    L3560               ; 
                       CALL    L34AA               ; 
                       JP      L0FC0               ; Handle animations for killed aliens

```
> [!NOTE]
> **Ported to C:** [`l3462_no_birds_left`](../collision_detection.c#L174) in `collision_detection.c` (ASM: `3462-346D`)

```asm
                       .ORG $3462
;
```

### L3462:

```asm
                       LD      A,(Counter9A+$1)    ; 
                       RRCA                        
                       RET     C                   
                       CALL    L0C40               ; 
                       CALL    L0FC0               ; Handle animations for killed aliens
                       JP      L2204               ; 

```
> [!NOTE]
> **Ported to C:** [`draw_first_4_bird_objects`](../bird_logic.c#L81) in `bird_logic.c` (ASM: `3474-3485`)

```asm
                       .ORG $3474
;*****************************************************************************
;* Draw bird objects 0 to 3.
;* Including the horizontal movement update.
;*****************************************************************************
```

### DrawFirst4BirdObjects:

```asm
                       LD      HL,B4B70            ; 
;
```

### L3477:

```asm
                       PUSH    HL                  ;
                       CALL    DrawBirdObject      ; 
                       POP     HL                  ;
                       LD      A,L                 ;
                       ADD     $08                 ; go to next bird object
                       LD      L,A                 ;
                       CP      $90                 ; for bird0 to bird3
                       JP      NZ,L3477            ; 
                       RET                         ;

;*****************************************************************************
;* Draw bird objects 4 to 7.
;* Including the horizontal movement update.
;*****************************************************************************
```

### DrawSecond4BirdObjects:

```asm
                       LD      HL,B4B90            ; 
;
```

### L3489:

```asm
                       PUSH    HL                  ;
                       CALL    DrawBirdObject      ; 
                       POP     HL                  ;
                       LD      A,L                 ;
                       ADD     $08                 ; go to next bird object
                       LD      L,A                 ;
                       CP      $B0                 ; for bird4 to bird7
                       JP      NZ,L3489            ; 
                       RET                         ;

;
```

### L3498:

```asm
                       LD      HL,B4B70            ; 
;
```

### L349B:

```asm
                       PUSH    HL                  ;
                       CALL    L35B0               ; 
                       POP     HL                  ;
                       LD      A,L                 ;
                       ADD     $08                 ; go to next bird object
                       LD      L,A                 ;
                       CP      $90                 ; for bird 0 to bird3
                       JP      NZ,L349B            ; 
                       RET                         ;

;
```

### L34AA:

```asm
                       LD      HL,B4B90            ; 
;
```

### L34AD:

```asm
                       PUSH    HL                  ;
                       CALL    L35B0               ; 
                       POP     HL                  ;
                       LD      A,L                 ;
                       ADD     $08                 ; go to next bird object
                       LD      L,A                 ;
                       CP      $B0                 ; for bird4 to bird7
                       JP      NZ,L34AD            ; 
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`drawbirdobject`](../attract_mode.c#L472) in `attract_mode.c` (ASM: `34C0-355D`)

```asm
                       .ORG $34C0
;*****************************************************************************
;* Draw a given bird object.
;* Input HL is the data structur of one bird object.
;* (For the 8 birds: $4B70, $4B78, $4B80, $4B88, $4B90, $4B98, $4BA0, $4BA8)
;*****************************************************************************
```

### DrawBirdObject:

```asm
                       LD      A,(HL)              ; HL=$4B70 (or $4B78,...)
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if 0
                       LD      B,A                 ; save it
                       ADD     $C0                 ; add to base for table T3EC0
                       LD      E,A                 ; save it
                       LD      D,$3E               ; MSB for T3EC0
                       LD      A,(DE)              ; get data starting from $3EC1
                       LD      C,A                 ;
                       INC     L                   ;
                       LD      D,(HL)              ; get $4B71 MSB of screen ram
                       INC     L                   ;
                       LD      E,(HL)              ; get $4B72 LSB of screen ram
                       INC     L                   ;
                       LD      A,B                 ; restore it
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       ADD     A,(HL)              ; and add to $4B73 alien0 screen coordinate Y
                       AND     $7E                 ; mask out 0111_1110
                       LD      L,A                 ;
                       LD      H,$3E               ;
                       LD      A,(HL)              ; get MSB from address table for bird character block shapes (T3E08)
                       INC     L                   ;
                       LD      L,(HL)              ; get LSB
                       LD      H,A                 ;
```

### L34DE:

```asm
                       LD      A,D                 ;
                       CP      $4B                 ; MSB of screen ram
                       JP      NZ,L350C            ; if value is not equal $4B
                       LD      A,E                 ;
                       CP      $50                 ;
                       JP      C,L350C             ; 
                       LD      B,$08               ;
                       INC     L                   ;
                       INC     L                   ;
                       SUB     $20                 ;
                       LD      E,A                 ;
                       CP      $50                 ;
                       JP      C,L3509             ; 
                       LD      B,$10               ;
                       INC     L                   ;
                       INC     L                   ;
                       SUB     $20                 ;
                       LD      E,A                 ;
                       CP      $50                 ;
                       JP      C,L3509             ; 
                       LD      B,$18               ;
                       INC     L                   ;
                       INC     L                   ;
                       SUB     $20                 ;
                       LD      E,A                 ;
;
```

### L3509:

```asm
                       LD      A,C                 ;
                       ADD     A,B                 ;
                       LD      C,A                 ;
;
```

### L350C:

```asm
                       LD      B,$35               ; MSB of return address for the draw shape entry.
                       PUSH    BC                  ;
                       LD      BC,$FFDF            ; Screen offset constant -33 right one column (-1), up one row (-32)
                       EX      DE,HL               ;
                       LD      (HL),$00            ; delete character on screen
                       INC     HL                  ;
                       LD      (HL),$00            ; delete character on screen
                       ADD     HL,BC               ;
                       RET                         ; jumps to draw shape entry.

                       .ORG $3520
;*****************************************************************************
;* Draw a shape.
;* Entry dep. on size of shape: 2x2,3x2,4x2,5x2,6x2,7x2.
;*****************************************************************************
```

### Draw7x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
```

### Draw6x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
```

### Draw5x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
```

### Draw4x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
```

### Draw3x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
```

### Draw2x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
```

### Draw1x2:

```asm
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       INC     HL                  ;
                       LD      A,(DE)              ;
                       LD      (HL),A              ;
                       INC     DE                  ;
                       ADD     HL,BC               ;
;
```

### L3558:

```asm
                       LD      (HL),$00            ;
                       INC     HL                  ;
                       LD      (HL),$00            ;
                       RET                         ;

```
> [!NOTE]
> **Ported to C:** [`refresh_bird_flight_parameters`](../bird_wave_behavior.c#L270) in `bird_wave_behavior.c` (ASM: `3560-359F`)

```asm
                       .ORG $3560
;*****************************************************************************
;* Bird-launch setup:
;* Decides the parameters of the next incoming bird group.
;* Builds a random horizontal jitter, then composes an index from the current game state.
;* The index is `bit5(timing) | round(bits 3 4) | (BirdsLeft 1)(bits 1 2)`,
;* which spans `$00`–`$3E` in steps of 2 -> addresses `$3E80`–`$3EBE`.
;* So the table is 32 two byte entries, selected by:
;* - Game round (`LevelAndRound`, clamped at round 4) -> one of 4 difficulty groups
;* - Birds remaining (`BirdsLeft 1`, clamped to 0–3) -> entry within the group
;* - A timing bit from `Counter9A` -> alternates between the two halves of the table
;* They're then consumed by the bird movement/attack code.
;*****************************************************************************
```

### L3560:

```asm
                       CALL    GetRandomNumber     ; 
                       LD      B,A                 ;
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       LD      C,A                 ;
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       OR      B                   
                       LD      (M436F),A           ; 
                       LD      A,(LevelAndRound)   ; 
                       CP      $40                 ;
                       JP      C,L3577             ; if game round < 4
                       LD      A,$30               
```

### L3577:

```asm
                       AND     $30                 
                       RRCA                        
                       LD      B,A                 
                       LD      A,(BirdsLeft)       ; 
                       DEC     A                   
                       CP      $04                 
                       JP      C,L3586             ; 
                       LD      A,$03               
```

### L3586:

```asm
                       RLCA                        ; Multiply by 2
                       OR      B                   
                       LD      B,A                 
                       LD      A,(Counter9A)       ; 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       AND     $20                 ; mask out 0010_0000
                       OR      B                   
                       ADD     $80                 
                       LD      L,A                 
                       LD      H,$3E               
                       LD      A,(HL)              ; data from table T3E80
                       LD      (M436E),A           ; 
                       INC     L                   
                       LD      A,(HL)              ; data from table T3E80
                       ADD     A,C                 
                       AND     $F8                 
                       LD      (M436D),A           ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`update_bird_behavior`](../bird_wave_behavior.c#L218) in `bird_wave_behavior.c` (ASM: `35B0-35DB`)

```asm
                       .ORG $35B0
;*****************************************************************************
;* The dispatch trick:
;* `L35B0` is called with `HL` -> the bird's record.
;* It reads the state index at record offset +0, then (crucially) advances `HL`
;* to offset +4 and passes that pointer along.
;* It then looks up `T3F00 + index*8` and pushes four 16 bit values, then does `RET`.
;*****************************************************************************
```

### L35B0:

```asm
                       LD      A,(HL)              ; get index character block shape
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if index is 0
                       LD      B,A                 ; save index to B
                       INC     L                   ;
                       INC     L                   ;
                       INC     L                   ;
                       INC     L                   ;
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       JP      Z,L35BE             ; 
                       DEC     (HL)                ;
```

### L35BE:

```asm
                       EX      DE,HL               ;
                       PUSH    DE                  ;
                       LD      A,B                 ; load index
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       LD      L,A                 ;
                       LD      H,$3F               ; MSB of table T3F00 for stack manipulation
                       LD      B,(HL)              ; get 1st byte
                       INC     HL                  ;
                       LD      C,(HL)              ; get 2nd byte
                       PUSH    BC                  ; to stack
                       INC     HL                  ;
                       LD      B,(HL)              ; get 3rd byte
                       INC     HL                  ;
                       LD      C,(HL)              ; get 4rd byte
                       PUSH    BC                  ; to stack
                       INC     HL                  ;
                       LD      B,(HL)              ; get MSB of 1st address
                       INC     HL                  ;
                       LD      C,(HL)              ; get LSB of 1st address
                       PUSH    BC                  ; to stack
                       INC     HL                  ;
                       LD      B,(HL)              ; get MSB of 2nd address
                       INC     HL                  ;
                       LD      C,(HL)              ; get LSB of 2nd address
                       PUSH    BC                  ; to stack
                       EX      DE,HL               ;
                       RET                         ; calls the 2nd address
;*****************************************************************************
;* Because the 2nd address was pushed last, `RET` jumps there first. So the sequence is:
;* 1. `RET` -> 2nd address (`$35E0` or `$36C0`) runs first, with `HL` = bird record +4.
;*    These are the movement / animation routines. They do their work and finish with their own `RET`.
;* 2. That `RET` pops the next stack item — the 1st address (`$36CC`, `$36D2`, `$36EA`, or `$370A`)
;*     — and jumps there. These are the state transition routines.
;*     They begin by popping the two constants and the bird pointer back off the stack.
;*****************************************************************************

```
> [!NOTE]
> **Ported to C:** [`l35e0_descend`](../bird_wave_behavior.c#L127) in `bird_wave_behavior.c` (ASM: `35E0-3624`)

```asm
                       .ORG $35E0
; called by $35B0
```

### L35E0:

```asm
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       CP      $10                 
                       JP      NC,L3628            ; 
                       LD      B,A                 
                       DEC     L                   
                       ADD     A,(HL)              
                       LD      (HL),A              
                       DEC     L                   
                       DEC     L                   
                       LD      A,B                 
                       ADD     A,(HL)              
                       LD      (HL),A              
                       CP      $08                 
                       JP      C,L366A             ; 
                       AND     $07                 
                       LD      (HL),A              
                       DEC     L                   
                       LD      A,(HL)              
                       SUB     $20                 
                       LD      (HL),A              
                       JP      NC,L3604            ; 
                       DEC     L                   
                       DEC     (HL)                
                       INC     L                   
```

### L3604:

```asm
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       LD      C,(HL)              
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       DEC     L                   
                       LD      (HL),$10            
                       SUB     C                   
                       JP      Z,L3672             ; 
                       DEC     A                   
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       AND     $1F                 
                       CP      B                   
                       INC     A                   
                       LD      (HL),A              
                       RET     C                   
                       LD      A,(M436E)           ; 
                       LD      (HL),A              
                       CP      B                   
                       RET     Z                   
                       INC     B                   
                       LD      (HL),B              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3628_climb`](../bird_wave_behavior.c#L85) in `bird_wave_behavior.c` (ASM: `3628-3666`)

```asm
                       .ORG $3628
```

### L3628:

```asm
                       AND     $0F                 
                       JP      Z,L3744             ; 
                       LD      B,A                 
                       DEC     L                   
                       LD      A,(HL)              
                       SUB     B                   
                       LD      (HL),A              
                       DEC     L                   
                       DEC     L                   
                       LD      A,(HL)              
                       SUB     B                   
                       LD      (HL),A              
                       JP      NC,L3695            ; 
                       AND     $07                 
                       LD      (HL),A              
                       DEC     L                   
                       LD      A,(HL)              
                       ADD     $20                 
                       LD      (HL),A              
                       JP      NC,L3648            ; 
                       DEC     L                   
                       INC     (HL)                
                       INC     L                   
```

### L3648:

```asm
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       INC     L                   
                       INC     L                   
                       SUB     (HL)                
                       RRCA                        
                       RRCA                        
                       RRCA                        
                       AND     $1F                 
                       CP      B                   
                       INC     A                   
                       DEC     L                   
                       JP      C,L3663             ; 
                       LD      A,(M436E)           ; 
                       CP      B                   
                       JP      Z,L3663             ; 
                       LD      A,B                 
                       INC     A                   
```

### L3663:

```asm
                       OR      $10                 
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l366a_stall`](../bird_wave_behavior.c#L117) in `bird_wave_behavior.c` (ASM: `366A-3671`)

```asm
                       .ORG $366A
;
```

### L366A:

```asm
                       LD      A,B                 
                       AND     A                   ; updates the zero flag
                       RET     NZ                  
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       INC     (HL)                
                       RET                         
;
```

### L3672:

```asm
                       DEC     L                   
                       LD      B,(HL)              
                       INC     L                   
                       INC     L                   
                       LD      A,(PlayerShipX)     ; 
                       AND     $F8                 
                       CP      B                   
                       JP      NC,L3680            ; 
                       LD      B,A                 
```

### L3680:

```asm
                       LD      A,(M436D)           ; 
                       LD      C,A                 
                       ADD     $08                 
                       LD      (M436D),A           ; 
                       LD      A,B                 
                       SUB     C                   
                       LD      (HL),$08            
                       RET     C                   
                       CP      $08                 
                       RET     C                   
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3695_aim_up`](../bird_wave_behavior.c#L65) in `bird_wave_behavior.c` (ASM: `3695-36BB`)

```asm
                       .ORG $3695
;
```

### L3695:

```asm
                       INC     L                   
                       INC     L                   
                       LD      B,(HL)              
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       CP      B                   
                       RET     NZ                  
                       DEC     L                   
                       LD      (HL),$00            
                       INC     L                   
                       LD      A,(PlayerShipX)     ; 
                       AND     $F8                 
                       CP      B                   
                       JP      C,L36AB             ; 
                       LD      B,A                 
; for the mirrored launch direction.
```

### L36AB:

```asm
                       LD      A,(M436D)           ; 
                       ADD     $08                 
                       LD      (M436D),A           ; 
                       ADD     A,B                 
                       LD      (HL),$C8            
                       RET     C                   
                       CP      $C8                 
                       RET     NC                  
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l36c0_animate`](../bird_wave_behavior.c#L165) in `bird_wave_behavior.c` (ASM: `36C0-36C9`)

```asm
                       .ORG $36C0
; called by $35B0
```

### L36C0:

```asm
                       LD      A,(HL)              ;
                       RRCA                        ;
                       RET     C                   ;
                       DEC     L                   
                       LD      A,(HL)              
                       INC     A                   
                       AND     $07                 
                       LD      (HL),A              
                       RET                         

                       .ORG $36CC
; called by $35B0
```

### L36CC:

```asm
                       POP     DE                  
                       POP     BC                  
                       POP     HL                  
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l36d2_grow`](../bird_wave_behavior.c#L178) in `bird_wave_behavior.c` (ASM: `36D2-36E6`)

```asm
                       .ORG $36D2
; called by $35B0
```

### L36D2:

```asm
                       POP     DE                  ;
                       POP     BC                  ;
                       POP     HL                  ;
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       RET     NZ                  ;
                       LD      (HL),B              
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       LD      (HL),D              
                       LD      A,(M4368)           ; 
                       OR      $01                 
                       LD      (M4368),A           ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l36ea_grow`](../bird_wave_behavior.c#L186) in `bird_wave_behavior.c` (ASM: `36EA-3706`)

```asm
                       .ORG $36EA
; called by $35B0
```

### L36EA:

```asm
                       POP     DE                  
                       POP     BC                  
                       POP     HL                  
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     NZ                  
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       AND     $0F                 
                       RET     NZ                  
                       DEC     L                   
                       DEC     L                   
                       LD      (HL),B              
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       LD      (HL),D              
                       LD      A,(M4368)           ; 
                       OR      $02                 
                       LD      (M4368),A           ; 
                       RET                         

                       .ORG $370A
;*****************************************************************************
; called by $35B0
;* `L370A` is one of the four 1st address (state transition) handlers,
;* selected by table entries `6`, `7`, `A`, and `F`.
;* It runs after the frame's movement handler and decides whether the bird
;* has finished its current growth phase; if so, it advances the bird to
;* its next state and records progress in the global bird maturity flags `$4368`.
;* Bird record fields it touches (relative to the +4 pointer it receives):
;* offset +0 (via `-4`) = state index (the `T3F00` selector / character block shape),
;* offset +4 = phase timer, offset +6 = sub counter.
;* Step by step:
;* 1. Recover parameters (`$370A`–`$370C`): pops the two `T3F00` constants for this state
;*    into `DE`/`BC` and the bird pointer into `HL`.
;* 2. Gate on completion (`$370D`–`$3715`): if the phase timer (offset +4) is still non zero,
;*    or the low nibble of the sub counter (offset +6) is non zero,
;*    the bird hasn't finished this growth phase yet, so it returns and leaves the state unchanged.
;* 3. Default transition (`$3716`–`$371D`): once idle, it programs the *next* state
;*    — new phase timer = `B` (table byte +0), new state index = `D` (table byte +2).
;* 4. Record maturity (`$371E`–`$3723`): sets bit 2 (`$04`) of the global bird maturity flags at `$4368`.
;* 5. Optional randomized branch (`$3726`–`$373E`): it samples the per wave random seed `$436F`,
;*    masks it with table byte +3 (`E`) and tests the high nibble. If that misses (`RET NZ` not taken),
;*    it *overrides* the transition — state index becomes `E & $0F`, phase timer becomes `C` (table byte +1)
;*    — and sets an additional maturity bit 3 (`$08`).
;* In other words, `L370A` is the "this bird has finished growing one stage" handler:
;* it either promotes the bird to a fixed next shape or, with a seed driven probability,
;* diverts it to an alternate shape, and it ticks up the flock's maturity progress in `$4368`
;* so the wave logic knows how far the birds have developed. The sibling handlers work the same way
;* but set different maturity bits: `L36D2` sets bit 0 (`$01`), `L36EA` sets bit 1 (`$02`),
;* and `L36CC` is the plain "pop and return" terminator with no transition.
;*****************************************************************************
```

### L370A:

```asm
                       POP     DE                  
                       POP     BC                  
                       POP     HL                  
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     NZ                  
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       AND     $0F                 
                       RET     NZ                  
                       DEC     L                   
                       DEC     L                   
                       LD      (HL),B              
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       LD      (HL),D              
                       LD      A,(M4368)           ; 
                       OR      $04                 
                       LD      (M4368),A           ; 
                       LD      A,(M436F)           ; 
                       AND     E                   
                       AND     $F0                 
                       RET     NZ                  
                       LD      A,E                 
                       AND     $0F                 
                       LD      (HL),A              
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       LD      (HL),C              
                       LD      A,(M4368)           ; 
                       OR      $08                 
                       LD      (M4368),A           ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3744_restart`](../bird_wave_behavior.c#L33) in `bird_wave_behavior.c` (ASM: `3744-3754`)

```asm
                       .ORG $3744
```

### L3744:

```asm
                       LD      (HL),$11            
                       DEC     L                   
                       DEC     (HL)                
                       DEC     L                   
                       DEC     L                   
                       LD      (HL),$07            
                       DEC     L                   
                       LD      A,(HL)              
                       ADD     $20                 
                       LD      (HL),A              
                       RET     NC                  
                       DEC     L                   
                       INC     (HL)                
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3758_bonus_explosion_animation`](../alien_logic.c#L166) in `alien_logic.c` (ASM: `3758-37CC`)

```asm
                       .ORG $3758
;
```

### L3758:

```asm
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if 0
                       DEC     (HL)                
                       JP      Z,L37CC             ; 
                       LD      A,(HL)              
                       RRCA                        
                       JP      NC,L37B0            ; Prints the score value in the middle of the bonus explosion
                       LD      A,$0F               
                       SUB     (HL)                
                       AND     $0E                 ; mask out 0000_1110
                       RLCA                        ; Multiply by 16 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       INC     L                   
                       INC     L                   
                       LD      D,(HL)              
                       INC     L                   
                       LD      E,(HL)              
                       PUSH    AF                  
                       PUSH    DE                  
                       LD      BC,$FFDF            ; Screen offset constant -33 right one column (-1), up one row (-32)
                       CALL    L3796               ; left part of bonus explosion animation
                       POP     DE                  
                       POP     AF                  
                       CPL                         
                       LD      L,A                 
                       LD      H,$FF               
                       INC     HL                  
                       ADD     HL,DE               
                       EX      DE,HL               
                       LD      HL,$BFA0            
                       ADD     HL,DE               
                       RET     NC                  
                       EX      DE,HL               
                       LD      DE,T17D6            ; (Bonus explosion right part)
                       LD      (HL),$00            
                       INC     HL                  
                       LD      (HL),$00            
                       ADD     HL,BC               
                       JP      Draw3x2             ; 

```
> [!NOTE]
> **Ported to C:** [`l3796_bonus_explosion_left`](../alien_logic.c#L100) in `alien_logic.c` (ASM: `3796-37AA`)

```asm
                       .ORG $3796
;*****************************************************************************
;* Draws the left part of bonus explosion animation.
;*****************************************************************************
```

### L3796:

```asm
                       ADD     $60                 
                       LD      L,A                 
                       LD      H,$00               
                       JP      NC,L379F            ; 
                       INC     H                   
```

### L379F:

```asm
                       ADD     HL,DE               
                       EX      DE,HL               
                       LD      HL,$BCC0            
                       ADD     HL,DE               
                       RET     C                   
                       EX      DE,HL               
                       LD      DE,T17D0            ; (Bonus explosion left part)
                       JP      Draw3x2             ; 

```
> [!NOTE]
> **Ported to C:** [`l37b0_print_bonus_score`](../alien_logic.c#L135) in `alien_logic.c` (ASM: `37B0-37C6`)

```asm
                       .ORG $37B0
;*****************************************************************************
;* Prints the score value in the middle of the bonus explosion animation.
;* First two digits are from $4379. Last digit is ever 0.
;*****************************************************************************
```

### L37B0:

```asm
                       INC     L                   ;
                       LD      A,(HL)              ;
                       DAA                         ;
                       LD      (HL),A              ;
                       INC     L                   ;
                       LD      D,(HL)              ;
                       INC     L                   ;
                       LD      E,(HL)              ;
                       DEC     L                   ;
                       DEC     L                   ;
                       NOP                         ;
                       CALL    RightOneColumn      ; 
                       LD      A,$20               ; character code for '0' (the right digit of bonus score)
                       LD      (DE),A              ; write to screen ram (upper left corner of object 17D6)
                       CALL    LeftOneColumn       ; 
                       LD      B,$02               ; for the left two digits
                       JP      PrintNumber         ; score value for bonus explosion

```
> [!NOTE]
> **Ported to C:** [`l37cc_erase_bonus_explosion`](../alien_logic.c#L82) in `alien_logic.c` (ASM: `37CC-37E5`)

```asm
                       .ORG $37CC
;
```

### L37CC:

```asm
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       LD      A,(HL)              
                       AND     $1F                 
                       ADD     $20                 
                       LD      L,A                 
                       LD      H,$43               
                       LD      BC,$FFDF            ; Screen offset constant -33 right one column (-1), up one row (-32)
                       LD      DE,$001A            
```

### L37DD:

```asm
                       LD      (HL),D              
                       INC     HL                  
                       LD      (HL),D              
                       ADD     HL,BC               
                       DEC     E                   
                       JP      NZ,L37DD            ; 
                       RET                         

;*****************************************************************************
; h8-ic52.8a
;*****************************************************************************

```
> [!NOTE]
> **Ported to C:** [`collision_detection_for_birds`](../collision_detection.c#L132) in `collision_detection.c` (ASM: `3800-3841, 391C-3922`)

```asm
                       .ORG $3800
;*****************************************************************************
;* Collision detection for birds.
;* The routine computes a shape index `B = displayedChar − $90`,
;* and loads the bullet's pixel column bit into `C` from `T3E00[PlayerBulletX & 7]`.
;* It then does two mask tests against the same `C`.
;*****************************************************************************
```

### L3800:

```asm
                       LD      A,(PlayerBulletState)
                       AND     $08                 
                       RET     Z                   
                       LD      A,(AbovePlayerBulletMSB)
                       ADD     $08                 
                       LD      D,A                 
                       LD      A,(M4BD2)           ; 
                       LD      E,A                 
                       LD      A,(AbovePlayerBulletLSB)
                       AND     $E0                 
                       LD      B,A                 
                       LD      A,(AbovePlayerBulletLSB)
                       SUB     E                   
                       NOP                         
                       AND     $1F                 
                       OR      B                   
                       LD      E,A                 
                       LD      A,(DE)              
                       SUB     $90                 
                       RET     C                   
                       LD      B,A                 
                       LD      A,(PlayerBulletX)   ; 
                       AND     $07                 
                       ADD     $00                 
                       LD      L,A                 
                       LD      H,$3E               
                       LD      C,(HL)              
                       LD      A,E                 
                       AND     $0E                 
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       LD      E,A                 
                       LD      A,$A8               
                       SUB     E                   
                       LD      E,A                 
                       LD      D,$4B               
                       LD      A,B                 
                       CP      $50                 
                       CALL    C,L3844             ; 
                       JP      L391C               ; 

;*****************************************************************************
;* A bird has been hit
;*****************************************************************************
```

### L3844:

```asm
                       ADD     $60                 ; LSB of table T3B60
                       LD      L,A                 
                       LD      H,$3B               ; MSB of table T3B60
                       LD      A,(HL)              
                       AND     C                   
                       RET     Z                   
                       CALL    L38A1               ; 
                       EX      DE,HL               
                       LD      A,(HL)              
                       LD      (HL),$00            
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       LD      D,(HL)              
                       POP     HL                  
                       LD      HL,BirdsLeft        ; 
                       DEC     (HL)                ; decrement number of BirdsLeft
                       CP      $0B                 
                       JP      C,L3894             ; 
                       LD      E,A                 
                       LD      A,$FF               ; set bonus explosion flag
                       LD      (M4369),A           ; 
                       LD      HL,M4378            ; 
                       LD      BC,$1010            ; C reg. set to: 'bonus explosion score 100'.
                       LD      A,E                 
                       CP      $0F                 
                       JP      Z,L38FB             ; 
                       LD      A,D                 
                       RRCA                        
                       AND     $7C                 
                       ADD     $30                 
                       LD      C,A                 
                       LD      A,E                 
                       CP      $0E                 
                       JP      Z,L38FB             ; 
                       LD      A,C                 
                       RRCA                        
                       LD      C,A                 
                       LD      A,E                 
                       CP      $0C                 
                       JP      NC,L38FB            ; 
                       LD      A,C                 
                       RRCA                        
                       LD      C,A                 
                       JP      L38FB               ; 

                       .ORG $3894
;
```

### L3894:

```asm
                       LD      BC,$0D05            
                       LD      A,$FF               
                       LD      (M4364),A           ; 
                       JP      L38F8               ; 

```
> [!NOTE]
> **Ported to C:** [`l38a1_erase_bird`](../collision_detection.c#L20) in `collision_detection.c` (ASM: `38A1-38B5`)

```asm
                       .ORG $38A1
;*****************************************************************************
;* Clears the hit cell and even contains the game's copy protection check that
;* reads the "R" of "AMSTAR ELECTRONICS CORP." — corrupting the bird graphics if patched.
;*****************************************************************************
```

### L38A1:

```asm
                       PUSH    DE                  
                       LD      C,$20               
                       EX      DE,HL               
                       INC     HL                  
                       LD      D,(HL)              
                       INC     HL                  
                       LD      E,(HL)              
;*****************************************************************************
;* This is a simple protection against piracy !
;* Changing this single letter will result in a disturbing graphics garbage,
;* when you hit a bird.
;*****************************************************************************
                       LD      A,(L198C)           ; First letter 'R' from: " AMSTAR ELECTRONICS CORP. "
                       ADD     $DE                 ; 1101_1110
                       LD      L,A                 
                       LD      H,$17               ; HL=$17F0 (FourByFourEmpty:)
                       CALL    L34DE               ; 
                       POP     DE                  
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l38bc_large_hit`](../collision_detection.c#L99) in `collision_detection.c` (ASM: `38BC-38F1`)

```asm
                       .ORG $38BC
;*****************************************************************************
;* Test the wing mask
;*****************************************************************************
```

### L38BC:

```asm
                       ADD     $B0                 
                       LD      L,A                 
                       LD      H,$3B               
                       LD      A,(HL)              
                       AND     C                   
                       RET     Z                   
                       CALL    L38A1               ; 
                       LD      A,(DE)              
                       SUB     $0B                 
                       JP      C,L38E9             ; 
                       CP      $03                 
                       JP      NC,L38E9            ; 
                       LD      B,A                 
                       LD      H,D                 
                       LD      A,E                 
                       ADD     $05                 
                       LD      L,A                 
                       LD      A,(PlayerBulletX)   ; 
                       CP      (HL)                
                       RLA                         
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       AND     $04                 
                       OR      B                   
                       ADD     $B8                 
                       LD      L,A                 
                       LD      H,$3D               
                       LD      A,(HL)              
                       LD      (DE),A              
;*****************************************************************************
;* A bird's wing was hit
;*****************************************************************************
```

### L38E9:

```asm
                       LD      A,$FF               
                       LD      (M4366),A           ; 
                       LD      BC,$0702            
                       JP      L38F8               ; 

```
> [!NOTE]
> **Ported to C:** [`bird_explosion_slot`](../collision_detection.c#L38) in `collision_detection.c` (ASM: `38F8-391B`)

```asm
                       .ORG $38F8
;
```

### L38F8:

```asm
                       LD      HL,M4370            ; 
```

### L38FB:

```asm
                       XOR     A                   ; A=0
                       CP      (HL)                
                       JP      Z,L3906             ; 
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       INC     L                   
                       CP      (HL)                
                       RET     NZ                  
```

### L3906:

```asm
                       LD      (HL),B              
                       INC     L                   
                       LD      (HL),C              
                       INC     L                   
                       LD      A,(AbovePlayerBulletMSB)
                       LD      (HL),A              
                       INC     L                   
                       LD      A,(AbovePlayerBulletLSB)
                       LD      (HL),A              
                       LD      A,(PlayerBulletState)
                       AND     $F7                 
                       LD      (PlayerBulletState),A
                       RET                         

;*****************************************************************************
;* Wing mask (`$3BB0`+B) — `L38BC`, reached from `L391C` when `B >= $20`.
;*****************************************************************************
```

### L391C:

```asm
                       LD      A,B                 
                       CP      $20                 
                       JP      NC,L38BC            ; 
                       RET                         

;*****************************************************************************
;* Trigger the melody chip for 'Elise',
;* if flag for: 'mother ship score display' is set.
;*****************************************************************************
```

### L3923:

```asm
                       RET     Z                   
                       DEC     (HL)                
                       LD      L,$8D               
                       LD      A,(HL)              
                       AND     $3F                 
                       OR      $80                 
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`try_spawn_bird_dive_bomb`](../bird_wave_behavior.c#L364) in `bird_wave_behavior.c` (ASM: `3930-395B`)

```asm
                       .ORG $3930
;*****************************************************************************
;* Bird bomb-drop dispatcher:
;* For the birds currently in the active scroll band (from T3DC0),
;* check which sit over the player and have them drop a bomb.
;* The active-object window (start index + count) comes from `T3DC0`
;* indexed by the scroll phase; the player danger window `(B,C)`
;* is the player's mapped X position widened by `D` (from `L3A00`).
;*****************************************************************************
```

### L3930:

```asm
                       LD      A,(M4BD2)           ; 
                       AND     $1E                 
                       ADD     T3DC0 & $FF         ; LSB of table T3DC0
                       LD      L,A                 
                       LD      H,T3DC0 >> 8        ; MSB of table T3DC0
                       LD      E,(HL)              
                       INC     L                   
                       LD      L,(HL)              
                       LD      H,$4B               
                       CALL    L3A00               ; 
                       LD      A,(M439F)           ; 
                       ADD     A,D                 
                       LD      C,A                 
                       LD      A,(M439E)           ; 
                       SUB     D                   
                       LD      B,A                 
```

### L394C:

```asm
                       PUSH    HL                  
                       CALL    L395C               ; 
                       POP     HL                  
                       LD      A,L                 
                       ADD     $08                 
                       LD      L,A                 
                       DEC     E                   
                       JP      NZ,L394C            ; 
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l395c`](../bird_wave_behavior.c#L337) in `bird_wave_behavior.c` (ASM: `395C-397B`)

```asm
                       .ORG $395C
;*****************************************************************************
;* Per-bird bomb test:
;* HL -> bird object.  B/C = player danger window (left/right).
;*****************************************************************************
```

### L395C:

```asm
                       LD      A,(HL)              
                       CP      $05                 
                       RET     C                   
                       LD      A,L                 
                       ADD     $05                 
                       LD      L,A                 
                       LD      A,(HL)              
                       CP      B                   
                       RET     C                   
                       CP      C                   
                       RET     NC                  
                       SUB     $04                 
                       LD      B,A                 
                       DEC     L                   
                       DEC     L                   
                       DEC     L                   
                       LD      A,(M4BD2)           ; 
                       ADD     A,(HL)              
                       AND     $1F                 
                       RLCA                        ; Multiply by 8 ..
                       RLCA                        ; ..
                       RLCA                        ; ..
                       ADD     $08                 
                       LD      C,A                 
                       JP      L25B7               ; 

```
> [!NOTE]
> **Ported to C:** [`check_bird_formation_player_collision`](../bird_wave_behavior.c#L399) in `bird_wave_behavior.c` (ASM: `3980-39FD`)

```asm
                       .ORG $3980
;*****************************************************************************
;* Player shield vs. bird collision sweep:
;* Active while the formation is in a vertical band.
;* Borrows the player-bullet vars to probe a column above the ship,
;* destroying birds the shield touches, then ticks the shield timer.
;*****************************************************************************
```

### L3980:

```asm
                       LD      A,(M4BD2)           ; 
                       SUB     $0C                 
                       RET     C                   
                       CP      $10                 
                       RET     NC                  
;*****************************************************************************
;* --- save the real player bullet state into the $4BC0 buffer ---
;*****************************************************************************
                       LD      HL,PlayerBulletState
                       LD      DE,M4BC0            ; 
                       LD      B,$04               
                       CALL    CopyBbytesHLtoDE    ; 
                       LD      L,$E6               
                       LD      B,$02               
                       CALL    CopyBbytesHLtoDE    ; 
;*****************************************************************************
;* --- aim the probe at the player ship and force it "active" ---
;*****************************************************************************
                       LD      L,$E2               
                       LD      DE,AbovePlayerBulletMSB
                       LD      B,$02               
                       CALL    CopyBbytesHLtoDE    ; 
                       LD      L,$C4               
                       LD      (HL),$08            
                       LD      DE,M439E            ; 
                       LD      A,(Counter9A+$1)    ; 
                       RRCA                        
                       JP      C,L39BF             ; 
                       INC     E                   
                       LD      L,$E7               
                       LD      A,(HL)              
                       SUB     $20                 
                       LD      (HL),A              
                       DEC     L                   
                       LD      A,(HL)              
                       SBC     $00                 
                       LD      (HL),A              
```

### L39BF:

```asm
                       LD      A,(DE)              
                       LD      (PlayerBulletX),A   ; 
;*****************************************************************************
;* --- Use (the sweep)
;* After saving, the routine forces `PlayerBulletState` active (`$39A7: LD (HL),$08`),
;* seeds the aim X, and repeatedly calls the bird collision routine `L3800`
;* while stepping the "above-player bullet" address down one row at a time — checking up to ~`$1D` rows for a hit.
;*****************************************************************************
```

### L39C3:

```asm
                       CALL    L3800               ; Collision detection for birds
                       LD      HL,PlayerBulletState
                       LD      A,(HL)              
                       AND     $08                 
                       JP      Z,L39F0             ; 
                       LD      HL,AbovePlayerBulletLSB
                       INC     (HL)                
                       LD      A,(HL)              
                       AND     $1F                 
                       CP      $1D                 
                       JP      C,L39C3             ; 
;*****************************************************************************
;* --- Restore buffer
;* When the sweep finishes (or the shield branch at `L39F0` completes),
;* the saved bytes are copied back, returning the player bullet to exactly its previous state
;*****************************************************************************
```

### L39DB:

```asm
                       LD      HL,M4BC0            ; 
                       LD      DE,PlayerBulletState
                       LD      B,$04               
                       CALL    CopyBbytesHLtoDE    ; 
                       LD      E,$E6               
                       LD      B,$02               
                       JP      CopyBbytesHLtoDE    ; 

                       .ORG $39F0
;*****************************************************************************
;* Shield timer upkeep (entered on a hit):
;*****************************************************************************
```

### L39F0:

```asm
                       LD      L,$A6               
                       LD      A,(HL)              
                       CP      $C0                 
                       JP      C,L0CC4             ; 
                       SUB     $01                 
                       LD      (HL),A              
                       JP      L39DB               ; 

```
> [!NOTE]
> **Ported to C:** [`l3a00`](../bird_wave_behavior.c#L312) in `bird_wave_behavior.c` (ASM: `3A00-3A0F`)

```asm
                       .ORG $3A00
;*****************************************************************************
;* Frame gate + danger-window width:
;* Returns D = half-width of the player "danger" window
;* (wider when fewer birds remain -> more aggressive bombing).
;* On alternate frames, pops L3930's return address so the
;* whole bomb scan is skipped this frame (throttles bombing).
;* The `POP HL` / `RET` trick at `$3A0E` is the key detail:
;* when the gate "fails", it removes `L3930`'s own continuation (`$3942`)
;* from the stack and returns one level higher, so on those frames `L3930`
;* performs no bomb-drop scan at all.
;*****************************************************************************
```

### L3A00:

```asm
                       LD      A,(BirdsLeft)       ; 
                       SUB     $0C                 
                       CPL                         
                       INC     A                   
                       LD      D,A                 
                       LD      A,(Counter9A+$1)    ; 
                       RRCA                        
                       RRCA                        
                       RET     C                   
                       POP     HL                  
                       RET                         

;*****************************************************************************
;* Update all synth sounds and melody trigger data.
;*****************************************************************************
```

### L3A10:

```asm
                       LD      HL,LevelAndRound    ; 
                       LD      A,(HL)              ; get it
                       AND     A                   ; updates the zero flag
                       JP      NZ,L3B43            ; if LevelAndRound is not 0.
                       LD      L,$8D               ; set SoundControlB for...
                       LD      (HL),$CF            ; ... 1100_1111 triggers Tune3 -- ESTUDIO (Phoenix theme song)
                       RET                         ;
;
```

### L3A1D:

```asm
                       LD      HL,M4369            ; 
                       LD      A,(HL)              ;
                       AND     A                   ; updates the zero flag
                       JP      Z,L3A40             ; if $4369 is 0.
                       CP      $20                 
                       JP      C,L3A2C             ; 
                       LD      (HL),$20            
```

### L3A2C:

```asm
                       DEC     (HL)                
                       LD      A,(HL)              
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       NOP                         
                       CPL                         
                       AND     $0E                 
                       LD      L,$8D               
                       LD      (HL),A              
                       LD      L,$68               
                       LD      (HL),$00            
                       LD      L,$66               
                       LD      (HL),$00            
                       RET                         

;*****************************************************************************
;* Enemy hit sound during explosion animation.
;*****************************************************************************
```

### L3A40:

```asm
                       LD      L,$64               
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       JP      Z,L3A62             ; 
                       CP      $10                 
                       JP      C,L3A4E             ; 
                       LD      (HL),$10            
```

### L3A4E:

```asm
                       DEC     (HL)                
                       LD      A,(HL)              
                       RRCA                        
                       NOP                         
                       NOP                         
                       CPL                         
                       AND     $07                 
                       OR      $10                 
                       LD      L,$8C               
                       LD      (HL),A              
                       LD      L,$66               
                       LD      (HL),$00            
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3a62`](../sound_dispatcher.c#L119) in `sound_dispatcher.c` (ASM: `3A62-3A77`)

```asm
                       .ORG $3A62
;*****************************************************************************
;* Bird wing hit sound.
;*****************************************************************************
```

### L3A62:

```asm
                       LD      L,$66               
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   
                       CP      $10                 
                       JP      C,L3A78             ; 
                       LD      (HL),$10            
                       LD      A,(LevelAndRound)   ; 
                       AND     $08                 
                       JP      Z,L3A78             ; 
                       LD      (HL),$05            
```

### L3A78:

```asm
                       DEC     (HL)                
                       LD      L,$8C               
                       LD      A,(HL)              
                       AND     $08                 
                       OR      $04                 
                       LD      (HL),A              
                       RET                         
;
```

### L3A82:

```asm
                       LD      HL,Counter9A        ; 
                       LD      A,(HL)              
                       CP      $03                 
                       RET     C                   
                       LD      L,$8D               
                       LD      A,(HL)              
                       AND     $3F                 
                       LD      (HL),A              
                       RET                         
;
```

### L3A90:

```asm
                       LD      HL,M436B            ; 
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       JP      L3923               ; 

;*****************************************************************************
;* Background sound for the alien waves.
;* At least one of the aliens is doing a closed loop pattern.
;* Sound data is derived from alien control state B.
;*****************************************************************************
```

### L3A98:

```asm
                       LD      HL,M4B70            ; 
                       LD      BC,$0800            
                       LD      DE,$03B0            
```

### L3AA1:

```asm
                       LD      A,(HL)              
                       INC     L                   
                       AND     B                   
                       JP      Z,L3AAE             ; 
                       LD      A,(HL)              
                       CP      $28                 
                       JP      C,L3AAE             ; 
                       INC     C                   
```

### L3AAE:

```asm
                       LD      A,L                 
                       ADD     A,D                 
                       LD      L,A                 
                       CP      E                   
                       JP      NZ,L3AA1            ; 
                       LD      A,C                 
                       AND     A                   ; updates the zero flag
                       RET     Z                   
                       CP      $08                 
                       JP      C,L3ABF             ; 
                       LD      A,$08               
```

### L3ABF:

```asm
                       ADD     $25                 
                       LD      C,A                 
                       LD      HL,SoundControlA    ; 
                       LD      A,(HL)              
                       AND     $C0                 ; mask out 1100_0000
                       OR      C                   
                       LD      (HL),A              ; trigger sound control A
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3ad0`](../sound_dispatcher.c#L185) in `sound_dispatcher.c` (ASM: `3AD0-3AF6`)

```asm
                       .ORG $3AD0
;*****************************************************************************
;* Background sound for the bird waves:
;* Counts frames for the current tone;
;* it's compared against a per-phase duration taken from `T3DE0`
;* (indexed by the formation scroll phase `B4BD6`),
;* and when the duration is reached it resets to 0, which advances `$438E` to the next note.
;*****************************************************************************
```

### L3AD0:

```asm
                       LD      HL,M438E            ; Bird-wave background-sound phase
                       LD      A,(HL)              ; 
                       AND     $01                 ; 0000_0001 phase bit
                       RLCA                        ; Multiply by 4 ..
                       RLCA                        ; ..
                       OR      $20                 ; 0010_0000
                       LD      B,A                 ; 
                       DEC     L                   ; 
                       LD      A,(HL)              ; $438D SoundControlB
                       AND     $C0                 ; 1100_0000
                       OR      B                   ; set bits
                       LD      (HL),A              ; at SoundControlB
                       LD      L,$96               ; $4396 bird-wave background-sound step timer
                       LD      A,(HL)              ; 
                       INC     (HL)                ; 
                       AND     A                   ; updates the zero flag
                       JP      Z,L3AF8             ; 
                       LD      A,(M4BD6)           ; 
                       ADD     $E0                 ; LSB of table T3DE0 Background sound data for the bird waves.
                       LD      E,A                 ; 
                       LD      D,$3D               ; MSB of table T3DE0 Background sound data for the bird waves.
                       LD      A,(DE)              ; 
                       CP      (HL)                ; 
                       RET     NC                  ; 
                       LD      (HL),$00            ; 
                       RET                         ; 

```
> [!NOTE]
> **Ported to C:** [`l3af8`](../sound_dispatcher.c#L174) in `sound_dispatcher.c` (ASM: `3AF8-3B00`)

```asm
                       .ORG $3AF8
;
```

### L3AF8:

```asm
                       LD      L,$8E               ; $438E Bird-wave background-sound phase/state
                       INC     (HL)                ; advance the tone phase
                       DEC     L                   ; SoundControlB
                       LD      A,(HL)              ; 
                       OR      $10                 ; set 0001_0000
                       LD      (HL),A              ; at SoundControlB
                       RET                         ; 

```
> [!NOTE]
> **Ported to C:** [`l3b02`](../sound_dispatcher.c#L205) in `sound_dispatcher.c` (ASM: `3B02-3B19`)

```asm
                       .ORG $3B02
;*****************************************************************************
;* Background sound for level B (mothership).
;* Sound data is derived from Counter9A+1.
;*****************************************************************************
```

### L3B02:

```asm
                       LD      HL,Counter9A        ; 
                       LD      A,(HL)              
                       CP      $02                 
                       RET     NC                  
                       INC     L                   
                       LD      A,(HL)              
                       LD      B,A                 
                       AND     $60                 
                       LD      L,$8D               
                       LD      (HL),$0A            
                       RET     NZ                  
                       LD      A,B                 
                       AND     $02                 
                       ADD     $1C                 
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3b1b`](../sound_dispatcher.c#L223) in `sound_dispatcher.c` (ASM: `3B1B-3B27`)

```asm
                       .ORG $3B1B
;*****************************************************************************
;* Ringtone sound for the player shield.
;* Sound data is derived from player shield animation counter.
;*****************************************************************************
```

### L3B1B:

```asm
                       LD      HL,M4362            ; 
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if $4362 is 0.
                       CP      $40                 
                       JP      C,L3B28             ; 
                       LD      (HL),$40            
```

### L3B28:

```asm
                       DEC     (HL)                
                       LD      A,(HL)              
                       AND     $06                 
                       RLCA                        ; Multiply by 2
                       NOP                         
                       LD      L,$8D               
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3b33`](../sound_dispatcher.c#L234) in `sound_dispatcher.c` (ASM: `3B33-3B41`)

```asm
                       .ORG $3B33
;*****************************************************************************
;* Play the sound for 'Bonus live added'.
;*****************************************************************************
```

### L3B33:

```asm
                       LD      HL,M436A            ; 
                       LD      A,(HL)              
                       AND     A                   ; updates the zero flag
                       RET     Z                   ; if $436A is 0.
                       DEC     (HL)                
                       AND     $08                 
                       OR      $07                 
                       LD      L,$8D               
                       LD      (HL),A              
                       RET                         

```
> [!NOTE]
> **Ported to C:** [`l3b43`](../sound_dispatcher.c#L246) in `sound_dispatcher.c` (ASM: `3B43-3B5B`)

```asm
                       .ORG $3B43
;*****************************************************************************
;* Update all synth sounds and melody triggers.
;*****************************************************************************
```

### L3B43:

```asm
                       LD      HL,GameState        ; 
                       LD      A,(HL)              ;
                       CP      $03                 ; is 'normal game play' ?
                       CALL    Z,L23D6             ; if yes, do the background sound.
                       CALL    L3B33               ; Sound for 'Bonus live added'.
                       CALL    L3B1B               ; Ringtone sound for the player shield.
                       CALL    L3A1D               ; 
                       CALL    L27BD               ; Sound for player bullet or ship explosion.
                       CALL    L3A82               ; 
                       JP      L3A90               ; Trigger melody

                       .ORG $3B60
; Per-character horizontal hit-mask table for bird collision used at $3844.
; It's the lookup that lets the player's bullet hit a bird only
; where the bird's graphic tile actually has solid pixels, rather than treating the whole 8-pixel character cell as solid.
; Body mask table:
```

### T3B60:

```asm
                       .DB $1F, $7C, $F0, $01, $C0
                       .DB $07, $7F, $FC, $F0, $07, $C0, $1F, $FF, $FC, $03, $F0
                       .DB $0F, $C0, $3F, $FC, $1F, $F0, $07, $FE, $3F, $F8, $0F, $FF, $FF, $FC, $1F, $FF
                       .DB $FC, $1F, $FC, $1F, $F0, $7F, $F0, $7F, $C0, $FF, $01, $C0, $FF, $01, $00, $FF
                       .DB $07, $00, $FF, $07, $FC, $1F, $FC, $1F, $F0, $7F, $F0, $7F, $C0, $FF, $01, $C0
                       .DB $FF, $01, $00, $FF, $07, $FF, $07, $FC, $1F, $F8, $0F, $F0, $C0, $03, $FF, $FF
                       .DB $03, $E0, $03, $E0, $0F, $80, $0F, $00, $3C, $00, $1E, $3F, $00, $FC, $F0, $00
                       .DB $7F, $FE, $00, $F0, $03, $E0, $00, $00, $0F, $80, $00, $00, $3F, $00, $FE, $30
                       .DB $00, $06, $FF, $00, $F8, $00, $00, $03, $E0, $00, $E0, $08, $20, $04, $C0, $01
                       .DB $E0, $03, $F8, $0F, $07, $E0, $3F, $03, $FF, $FF, $FF, $3F, $FC, $FF, $F8, $FF
                       .DB $FF, $07, $E0, $1F, $F0, $FF, $FC, $FF, $07, $1E, $FC, $1F, $1F, $7F, $FF, $FF
;bird character block shapes table (using character set B)
```

### T3C00:

```asm
                       .DB $E8, $00, $E9, $00, $C4, $C6, $C5, $C7, $EA, $00, $EB, $00, $00, $00       ;bird shape #24 Object 3C00
                       .DB $EC, $00, $E9, $00, $C8, $CA, $C9, $CB, $EA, $00, $ED, $00, $00, $00       ;#28 Object 3C0E
                       .DB $EE, $00, $EF, $00, $CC, $CF, $CD, $D0, $CE, $D1, $F0, $00, $F1, $00       ;#29 Object 3C1C
                       .DB $F2, $00, $EF, $00, $D2, $00, $D3, $D5, $D4, $D6, $F0, $00, $F3, $00       ;#30 Object 3C2A
                       .DB $E8, $00, $E9, $00, $C4, $C6, $C5, $C7, $00, $00                   ;#24 without right wing Object 3C38
                       .DB $EC, $00, $E9, $00, $C8, $CA, $C9, $CB, $00, $00                   ;#28 without right wing Object 3C42
                       .DB $EE, $00, $EF, $00, $CC, $CF, $CD, $D0, $DD, $D1                   ;#29 without right wing and regrowing ($DD) Object 3C4C
                       .DB $F2, $00, $EF, $00, $D2, $00, $D3, $D5, $DD, $D6                   ;#30 without right wing and regrowing ($DD) Object 3C56
                       .DB $00, $00, $00, $00, $C4, $C6, $C5, $C7, $EA, $00, $EB, $00, $00, $00       ;#24 without left wing Object 3C60
                       .DB $00, $00, $00, $00, $DB, $CA, $C9, $CB, $EA, $00, $ED, $00, $00, $00       ;#28 without left wing and regrowing ($DB) Object 3C6E
                       .DB $00, $00, $00, $00, $DC, $CF, $CD, $D0, $CE, $D1, $F0, $00, $F1, $00       ;#29 without left wing and regrowing ($DC) Object 3C7C
                       .DB $00, $00, $00, $00, $00, $00, $D3, $D5, $D4, $D6, $F0, $00, $F3, $00       ;#30 without left wing Object 3C8A
                       .DB $00, $00, $00, $00, $C4, $C6, $C5, $C7, $00, $00                   ;#24 without left and right wing Object 3C98
                       .DB $00, $00, $00, $00, $DB, $CA, $C9, $CB, $00, $00                   ;#28 without left and right wing and regrowing ($DB) Object 3CA2
                       .DB $00, $00, $00, $00, $DC, $CF, $CD, $D0, $DD, $D1                   ;#29 without left and right wing and regrowing ($DC,$DD) Object 3CAC
                       .DB $00, $00, $00, $00, $00, $00, $D3, $D5, $DD, $D6                   ;#30 without left and right wing and regrowing ($DD) Object 3CB6
                       .DB $00, $00, $DE, $E2, $AB, $B2, $AC, $B3, $DF, $E3, $00, $00             ;#21 Object 3CC0
                       .DB $00, $00, $00, $E5, $B4, $B6, $B5, $B7, $E4, $E6, $00, $00             ;#25 Object 3CCC
                       .DB $00, $00, $00, $00, $B8, $BB, $B9, $BC, $BA, $BD, $00, $00             ;#26 Object 3CD8
                       .DB $00, $00, $00, $00, $BE, $C1, $BF, $C2, $C0, $C3, $00, $E7             ;#27 Object 3CE4
                       .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF ;not used
                       .DB $00, $00, $FA, $FC, $D7, $D9, $D8, $DA, $FB, $FD, $00, $00             ;#22 Object 3D00
                       .DB $F4, $F6, $F5, $00, $C4, $C6, $C5, $C7, $F7, $00, $F8, $F9             ;#23 Object 3D0C
                       .DB $00, $00, $00, $00, $A7, $A9, $A8, $AA, $00, $00                   ;#17 Object 3D18
                       .DB $00, $00, $00, $00, $AB, $AD, $AC, $AE, $00, $00                   ;#18 Object 3D22
                       .DB $00, $00, $DE, $00, $AB, $B0, $AC, $B1, $DF, $00                   ;#19 Object 3D2C
                       .DB $00, $00, $DE, $E0, $AB, $B2, $AC, $B3, $DF, $E1                   ;#20 Object 3D36
                       .DB $00, $00, $9D, $00, $9E, $00, $00, $00                         ;#12 Object 3D40
                       .DB $00, $00, $9F, $00, $A0, $00, $00, $00                         ;#13 Object 3D48
                       .DB $00, $00, $00, $00, $9C, $00, $00, $00                         ;#11 Object 3D50
                       .DB $00, $00, $00, $00, $A3, $A5, $A4, $A6                         ;#16 Object 3D58
                       .DB $00, $00, $9C, $00, $00, $00                               ;#11 one pos moved to the left Object 3D60
                       .DB $00, $00, $9D, $00, $9E, $00                               ;#12 (but 3x2) Object 3D66
                       .DB $00, $00, $9F, $00, $A0, $00                               ;#13 Object 3D6C
                       .DB $00, $00, $A1, $00, $A2, $00                               ;#14 Object 3D72
                       .DB $00, $00, $96, $00, $00, $00                               ;#7 Object 3D78
                       .DB $00, $00, $97, $00, $93, $00                               ;#8 Object 3D7E
                       .DB $00, $00, $98, $00, $99, $00                               ;#9 Object 3D84
                       .DB $00, $00, $9A, $00, $9B, $00                               ;#10 Object 3D8A
                       .DB $00, $00, $90, $00, $00, $00                               ;#3 Object 3D90
                       .DB $00, $00, $91, $00, $00, $00                               ;#4 Object 3D96
                       .DB $00, $00, $92, $00, $93, $00                               ;#5 Object 3D9C
                       .DB $00, $00, $94, $00, $95, $00                               ;#6 Object 3DA2
                       .DB $00, $00, $01, $00                                     ;like small star Object 3DA8
                       .DB $00, $00, $08, $00                                     ;like medium star Object 3DAC
                       .DB $00, $00, $0A, $00                                     ;like big star Object 3DB0
                       .DB $00, $00, $0B, $00, $0C, $0C, $0E, $FF                         ;group of stars Object 3DB4
                       .DB $0D, $0E, $0D, $FF                                     ;group of stars Object 3DBC

; Scroll-phase -> active-object-window table for the bird wave.
; Used by `L3930`, which runs every frame during the bird attack waves (it's called from the wave loop at `$3431` and `$3448`).
; It defines a sliding, resizing window over the column of bird objects as a function of how far the wave has scrolled down.
; - Phases 0–8: the window starts at the top object (`$4B70`) and grows `6 -> 7 -> 8` as more rows enter the play field.
; - Phases 10–22: the start pointer slides down one object at a time (`$4B78 -> $4B80 -> ... -> $4BA8`),
;                 while the count shrinks `7 -> 6 -> ... -> 1`, modeling the top rows scrolling out / fewer rows remaining active.
; - Phases 24–30: it wraps back to the top (`$4B70`) and grows again `2 -> 3 -> 4 -> 5`.
```

### T3DC0:

```asm
                       .DB $06, $70         ; phase  0 : count=6, ptr=$4B70
                       .DB $07, $70         ; phase  2 : count=7, ptr=$4B70
                       .DB $08, $70         ; phase  4 : count=8, ptr=$4B70
                       .DB $08, $70         ; phase  6 : count=8, ptr=$4B70
                       .DB $08, $70         ; phase  8 : count=8, ptr=$4B70
                       .DB $07, $78         ; phase 10 : count=7, ptr=$4B78
                       .DB $06, $80         ; phase 12 : count=6, ptr=$4B80
                       .DB $05, $88         ; phase 14 : count=5, ptr=$4B88
                       .DB $04, $90         ; phase 16 : count=4, ptr=$4B90
                       .DB $03, $98         ; phase 18 : count=3, ptr=$4B98
                       .DB $02, $A0         ; phase 20 : count=2, ptr=$4BA0
                       .DB $01, $A8         ; phase 22 : count=1, ptr=$4BA8
                       .DB $02, $70         ; phase 24 : count=2, ptr=$4B70
                       .DB $03, $70         ; phase 26 : count=3, ptr=$4B70
                       .DB $04, $70         ; phase 28 : count=4, ptr=$4B70
                       .DB $05, $70         ; phase 30 : count=5, ptr=$4B70

; Background sound data for the bird waves.
; Slowly ascending and descending tones.
```

### T3DE0:

```asm
                       .DB $40, $40, $40, $40, $40, $40, $40, $34, $2C, $26, $20, $1C, $18, $14, $12, $0F
                       .DB $0D, $0B, $09, $08, $07, $06, $05, $04, $03, $02, $02, $02, $02, $02, $02, $02

; Column bit `C` look up table for `PlayerBulletX & 7`
```

### T3E00:

```asm
                       .DB $01, $02, $04, $08, $10, $20, $40, $80

;address table for bird character block shapes (grouped by animation pattern)
```

### T3E08:

```asm
                       .DB $3D, $A8 ;like small star                  2x2
                       .DB $3D, $AC ;like medium star                 2x2
                       .DB $3D, $B0 ;like big star                    2x2

                       .DB $3D, $B4 ;group of stars

;growing up
                       .DB $3D, $90 ;#3                               3x2
                       .DB $3D, $96 ;#4                               3x2
                       .DB $3D, $9C ;#5                               3x2
                       .DB $3D, $A2 ;#6                               3x2
                       .DB $3D, $78 ;#7                               3x2
                       .DB $3D, $7E ;#8                               3x2
                       .DB $3D, $84 ;#9                               3x2
                       .DB $3D, $8A ;#10                              3x2
                       .DB $3D, $60 ;#11 one pos moved to the left    3x2
                       .DB $3D, $66 ;#12 (but 3x2)                    3x2
                       .DB $3D, $6C ;#13                              3x2
                       .DB $3D, $72 ;#14                              3x2

                       .DB $3D, $40 ;#12                              4x2
                       .DB $3D, $48 ;#13                              4x2
                       .DB $3D, $50 ;#11                              4x2
                       .DB $3D, $58 ;#16                              4x2

                       .DB $3D, $18 ;#17                              5x2
                       .DB $3D, $22 ;#18                              5x2
                       .DB $3D, $2C ;#19                              5x2
                       .DB $3D, $36 ;#20                              5x2

                       .DB $3C, $C0 ;#21                              6x2
                       .DB $3D, $00 ;#22                              6x2
                       .DB $3D, $0C ;#23                              6x2

                       .DB $3C, $00 ;#24                              7x2

;get smaller and move to left
                       .DB $3D, $58 ;#16                              4x2
                       .DB $3D, $50 ;#11                              4x2
                       .DB $3D, $48 ;#13                              4x2
                       .DB $3D, $40 ;#12                              4x2

;get smaller
                       .DB $3D, $36 ;#20                              5x2
                       .DB $3D, $2C ;#19                              5x2
                       .DB $3D, $22 ;#18                              5x2
                       .DB $3D, $18 ;#17                              5x2

;wings going down
                       .DB $3C, $00 ;#24                              7x2
                       .DB $3D, $0C ;#23                              6x2
                       .DB $3D, $00 ;#22                              6x2
                       .DB $3C, $C0 ;#21                              6x2

;wings up and move to right
                       .DB $3C, $00 ;#24                              7x2
                       .DB $3C, $0E ;#28                              7x2
                       .DB $3C, $1C ;#29                              7x2
                       .DB $3C, $2A ;#30                              7x2

;wings up and move to right
                       .DB $3C, $38 ;#24 without right wing           5x2
                       .DB $3C, $42 ;#28 without right wing           5x2
                       .DB $3C, $4C ;#29 without right wing reg.      5x2
                       .DB $3C, $56 ;#30 without right wing reg.      5x2

;wings up and move to right
                       .DB $3C, $60 ;#24 without left wing            7x2
                       .DB $3C, $6E ;#28 without left wing reg.       7x2
                       .DB $3C, $7C ;#29 without left wing reg.       7x2
                       .DB $3C, $8A ;#30 without left wing            7x2

;wings up and move to right
                       .DB $3C, $98 ;#24 without left/right wing      5x2
                       .DB $3C, $A2 ;#28 without left/right wing reg  5x2
                       .DB $3C, $AC ;#29 without left/right wing reg  5x2
                       .DB $3C, $B6 ;#30 without left/right wing reg  5x2

;wings down and move to right
                       .DB $3C, $C0 ;#21                              6x2
                       .DB $3C, $CC ;#25                              6x2
                       .DB $3C, $D8 ;#26                              6x2
                       .DB $3C, $E4 ;#27                              6x2

; Bird-wave launch/spawn configuration table:
; It's read by `L3560`, the routine that sets up a new diving bird group.
; Byte 0:   -> $436E Bird count / formation-size for this dive (values `4`–`8`).
;           It's later used as a target/limit when the bird objects are populated and stepped.
; Byte 1:   (+ random, grid aligned) -> $436D Horizontal start position of the bird group.
;           (base values `$10`–`$60`). As each bird in the group is launched, the code reads $436D,
;           uses it as the X position, and advances it by 8 for the next bird.
```

### T3E80:

```asm
                       .DB $05, $40
                       .DB $05, $20
                       .DB $04, $30
                       .DB $04, $10
; 
                       .DB $06, $48
                       .DB $06, $28
                       .DB $05, $38
                       .DB $05, $18
; 
                       .DB $07, $50
                       .DB $07, $30
                       .DB $06, $40
                       .DB $06, $20
; 
                       .DB $08, $58
                       .DB $08, $38
                       .DB $07, $48
                       .DB $07, $28
; 
                       .DB $06, $10
                       .DB $05, $20
                       .DB $05, $30
                       .DB $05, $40
; 
                       .DB $08, $18
                       .DB $07, $28
                       .DB $07, $38
                       .DB $06, $48
; 
                       .DB $08, $20
                       .DB $07, $30
                       .DB $07, $40
                       .DB $07, $50
; 
                       .DB $08, $30
                       .DB $08, $40
                       .DB $08, $50
                       .DB $08, $60

; LSB table for draw routine ($3520) entry.
; $3548, $3540, aso...
; for: 7x2, 7x3, 7x3, 7x3, 7x4, 7x5, 7x6, 7x4, 7x5, 7x6, 7x7, 7x5, 7x7, 7x5, 7x4.
```

### T3EC0:

```asm
                       .DB $FF
                       .DB $48, $40, $40, $40, $38, $30, $28, $38, $30, $28, $20, $30, $20, $30, $28

; Vertical scrolling/descent motion of the birds attack formation.
; Consumed by the bird vertical-movement routine `L2600` and its helper `L2668`.
; Dithered vertical-scroll increment table:
; Used to generate fractional (sub-pixel) scroll speeds for the formation's descent. In `L2600`.
; - The index is `row + column`, where the *row* (`0/4/8/12`) is the animation-frame parity from `Counter9A+1`,
;   and the column (`0–3`) is the descent sub-phase `B4BD5 & 3`.
; - The value (only ever `0` or `1`) is added to the coarse speed `(B4BD5>>2)&7`
;   to form the per-frame scroll delta, which is then subtracted from `CounterB9` and written to the hardware scroll register `$5800`.
; This lets the game realise non-integer average descent rates (e.g. an effective 3 1/2 px/frame) by alternating between `n` and `n+1` across frames/sub-phases,
; giving smooth variable-speed scrolling. (The alternate path `L2650` reuses the same table but adds to `CounterB9` for the return/upward motion.)
```

### T3ED0:

```asm
                       .DB $01, $01, $01, $01
                       .DB $00, $00, $01, $01
                       .DB $00, $01, $01, $01
                       .DB $00, $00, $00, $01

; Descent-speed clamp curve table:
; This 32-byte block is indexed by `B4BD6` (a 0–31 value) and acts as a per-position speed limit on the computed descent step in `L2668`.
; `B4BD6` is computed in `L26D0`/`$26EE` as `(B4BD2 + D + E) & $1F` after scanning the live bird objects (`M4BA8…`).
; So it encodes the formation's current vertical scroll phase combined with how many birds remain and where they are.
; The table value caps `B` (a step candidate derived from `M436E`, the wave timer `Counter9A`, and `AliensLeft`),
; and the clamped result becomes `B4BD5` — which is exactly the value Part 1 uses to pick the scroll increment.
; The values trace a speed envelope across the descent: `5->4->3->2->1->0`, a flat `0` hold, 
; then a gradual rise `1->2->...->8` and back to `6`.
; In effect it makes the swooping formation decelerate to a stop, pause, then accelerate again as it moves through the screen.
```

### T3EE0:

```asm
                       .DB $05, $04, $03, $02, $01, $00
                       .DB $00, $00, $00, $00, $01, $01
                       .DB $01, $01, $02, $02
                       .DB $02, $02, $03, $03
                       .DB $03, $04, $04, $04
                       .DB $05, $05, $06, $06
                       .DB $07, $08, $07, $06

; A stack built coroutine dispatcher:
; Register contents and address for stack manipulation 
; used at level 3,4,8,9.
; T3F00 is a 16 * 8 byte per state descriptor table for the level 3/4/8/9 birds.
; Each entry holds two register constant words plus two routine addresses
; (a movement handler and a transition handler).
; `L35B0` dispatches it with a stack trick: it pushes the bird pointer, the two constants,
; and both addresses, then `RET`s — running the movement routine first,
; which `RET`s into the transition routine, which pops the constants and returns to the caller.
; It's an indirect double call built entirely on the stack.
```

### T3F00:

```asm
                       .MSFIRST
; for bird index to character block shape (0)
                       .DB $FF, $FF, $FF, $FF   ; not used
                       .DB $FF, $FF         ; not used
                       .DB $FF, $FF,        ; not used
; for bird index to character block shape (1)
                       .DB $20, $FF, $02, $FF   ;BC and DE register contents
                       .DW L36D2         ;address to call
                       .DW L36C0         ;address to call
; for bird index to character block shape (2)
                       .DB $20, $FF, $03, $FF   ;
                       .DW L36D2         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (3)
                       .DB $30, $FF, $04, $FF   ;
                       .DW L36D2         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (4)
                       .DB $10, $FF, $05, $FF   ;
                       .DW L36EA         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (5)
                       .DB $10, $FF, $06, $FF   ;
                       .DW L36EA         ;address
                       .DW L36C0         ;address
; for bird index to character block shape (6)
                       .DB $10, $60, $07, $1F   ;
                       .DW L370A         ;address
                       .DW L36C0         ;address
; for bird index to character block shape (7)
                       .DB $F0, $10, $0B, $1A   ;
                       .DW L370A         ;address
                       .DW L36C0         ;address
; for bird index to character block shape (8)
                       .DB $40, $FF, $04, $FF   ;
                       .DW L36EA,        ;address
                       .DW L36C0         ;address
; for bird index to character block shape (9)
                       .DB $10, $FF, $08, $FF   ;
                       .DW L36EA         ;address
                       .DW L36C0         ;address
; for bird index to character block shape (A)
                       .DB $40, $10, $0F, $17   ;
                       .DW L370A         ;address
                       .DW L36C0         ;address
; for bird index to character block shape (B)
                       .DB $10, $FF, $0A, $FF   ;
                       .DW L36EA         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (C)
                       .DB $FF, $FF, $FF, $FF   ;
                       .DW L36CC         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (D)
                       .DB $FF, $FF, $FF, $FF   ;
                       .DW L36CC         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (E)
                       .DB $10, $FF, $06, $FF   ;
                       .DW L36EA         ;address
                       .DW L35E0         ;address
; for bird index to character block shape (F)
                       .DB $10, $10, $07, $79   ;
                       .DW L370A         ;address
                       .DW L35E0         ;address

;
;level 3 and 8 initial data for the 8 birds.
;data will be copied to $4B70-$4BAF
;..........................:index to first character block shape
;...............................:MSB of initial screen address
;....................................:LSB of the initial screen address
;.........................................:animation phase / current shape frame
;..............................................:movement-step countdown timer
;...................................................: grid coordinate x
;........................................................:horizontal movement step (velocity)
;.............................................................: grid coordinate y
```

### T3F80:

```asm
                       .DB $01, $48, $EE, $00, $10, $B0, $10, $20       ; 0
                       .DB $01, $49, $2C, $00, $10, $A0, $00, $B0       ; 1
                       .DB $01, $49, $6A, $00, $10, $90, $00, $B8       ; 2
                       .DB $01, $49, $A8, $00, $10, $80, $00, $C0       ; 3
                       .DB $01, $49, $E6, $00, $10, $70, $00, $C8       ; 4
                       .DB $01, $4A, $24, $00, $10, $60, $00, $C8       ; 5
                       .DB $01, $4A, $62, $00, $10, $50, $00, $C8       ; 6
                       .DB $01, $4A, $A0, $00, $10, $40, $00, $C8       ; 7

;level 4 and 9 initial data for the 8 birds.
                       .DB $01, $4A, $CE, $00, $10, $38, $00, $B0       ; 0
                       .DB $01, $48, $CC, $00, $10, $B8, $10, $20       ; 1
                       .DB $01, $4A, $CA, $00, $10, $38, $00, $B8       ; 2
                       .DB $01, $48, $C8, $00, $10, $B8, $10, $18       ; 3
                       .DB $01, $4A, $C6, $00, $10, $38, $00, $C0       ; 4
                       .DB $01, $48, $C4, $00, $10, $B8, $10, $10       ; 5
                       .DB $01, $4A, $C2, $00, $10, $38, $00, $C8       ; 6
                       .DB $01, $48, $C0, $00, $10, $B8, $10, $08       ; 7
;********************************************************************
;* End                                                              *
;********************************************************************
.END
```