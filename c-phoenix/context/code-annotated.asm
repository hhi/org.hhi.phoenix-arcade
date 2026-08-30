; Generated from Phoenix.lst, program.rom, and asm-annotations.yaml.

L0000:
0000: 00              NOP ; Start/restart and interrupts end up at 0008
0001: 00              NOP
0002: 00              NOP
0003: 00              NOP
0004: 00              NOP
0005: 00              NOP
0006: 00              NOP
0007: 00              NOP
0008: 31 FF 4B        LD      SP,$4BFF ; {ram.Stack} Top-ish of RAM
000B: 26 50           LD      H,videoRegister >> 8 ; 50xx video register
000D: 36 00           LD      (HL),$00 ; Select the first bank of RAM
000F: CD 50 00        CALL    InitSoundScreen ; {code.InitSoundScreen} Turn sound off and clear both screen areas
0012: 21 00 18        LD      HL,T1800 ; {+code.T1800} Screen draw info
0015: 0E 03           LD      C,$03 ; 3 columns (rotated to 3 rows)
0017: CD D0 01        CALL    PrintTextLines ; {code.PrintTextLines} Draw the first 3 rows of the background (scores and coins)
MainLoop:
001A: CD 80 00        CALL    WaitVBlankCoin ; {code.WaitVBlankCoin} Wait for VBlank and count any coins
001D: 3A A2 43        LD      A,(GameOrAttract) ; {ram.GameOrAttract}
0020: A7              AND     A ; updates the zero flag
0021: CA 2D 00        JP      Z,L002D ; {code.L002D} if 'Attract mode'
0024: CD 00 04        CALL    GameStateMachine ; {code.GameStateMachine} controls the flow of the game.
0027: CD 00 27        CALL    UpdateScoresAndSound ; {code.UpdateScoresAndSound} updates scores and lives on screen, and sound HW
002A: C3 1A 00        JP      MainLoop ; {code.MainLoop} Back to top of main loop
L002D:
002D: 3E 0F           LD      A,$0F ; 0000_1111 mute the sound chip TMS36XX
002F: 26 60           LD      H,SOUNDCTLA >> 8 ; 60xx sound A
0031: 77              LD      (HL),A
0032: 26 68           LD      H,SOUNDCTLB >> 8 ; 68xx sound B
0034: 77              LD      (HL),A
0035: CD 77 03        CALL    UpdateSoundControlRAM ; {code.UpdateSoundControlRAM}
0038: 00              NOP
0039: CD E0 17        CALL    CoinChecking ; {code.CoinChecking}
003C: A7              AND     A ; updates the zero flag
003D: CA 46 00        JP      Z,L0046 ; {code.L0046} No credits ... continue splash
0040: CD 88 02        CALL    PromptForStartGame ; {code.PromptForStartGame}
0043: C3 1A 00        JP      MainLoop ; {code.MainLoop} Back to top of main loop
L0046:
0046: CD E3 00        CALL    SplashAndDemo ; {code.SplashAndDemo}
0049: C3 1A 00        JP      MainLoop ; {code.MainLoop} Back to top of main loop
004C: FF              .DB $FF
004D: FF              .DB $FF
004E: FF              .DB $FF
004F: FF              .DB $FF
InitSoundScreen:
0050: 26 68           LD      H,SOUNDCTLB >> 8 ; 68xx sound B
0052: 36 00           LD      (HL),$00 ; Sound off
0054: 26 60           LD      H,SOUNDCTLA >> 8 ; 60xx sound A
0056: 36 00           LD      (HL),$00 ; Sound off
0058: 26 58           LD      H,scrollRegister >> 8 ; 58xx scroll register
005A: 36 00           LD      (HL),$00 ; First memory bank
005C: CD 6B 00        CALL    ClearRAMBank ; {code.ClearRAMBank} Clear the bank (includes screen)
005F: 26 50           LD      H,videoRegister >> 8 ; 50xx video register
0061: 36 01           LD      (HL),$01 ; Second memory bank
0063: CD 6B 00        CALL    ClearRAMBank ; {code.ClearRAMBank} Clear the bank (includes screen)
0066: 26 50           LD      H,videoRegister >> 8 ; 50xx video register
0068: 36 00           LD      (HL),$00 ; Back to first memory bank
006A: C9              RET ; Done
ClearRAMBank:
006B: 21 F8 4B        LD      HL,$4BF8 ; {+ram.Stack} Highest point ... skip the top of the stack
006E: 3E 3F           LD      A,$3F ; Stop when H reaches 3F
L0070:
0070: 36 00           LD      (HL),$00 ; Clear the memory
0072: 2B              DEC     HL ; Point to next
0073: BC              CP      H ; All done?
0074: C2 70 00        JP      NZ,L0070 ; {code.L0070} No ... go back for all
0077: C9              RET ; Done
SlowPrintScrollRegisterUpdate:
0078: CD 96 01        CALL    SlowPrintScoreAverageTable ; {code.SlowPrintScoreAverageTable}
007B: C3 F0 06        JP      L06F0 ; {code.L06F0} update scroll register and fill background
007E: FF              .DB $FF
007F: FF              .DB $FF
WaitVBlankCoin:
0080: 26 78           LD      H,DSW0 >> 8 ; 78xx DSW0 Check ...
0082: 7E              LD      A,(HL) ; ... screen blanking flag
0083: E6 80           AND     $80 ; Wait for it ...
0085: CA 80 00        JP      Z,WaitVBlankCoin ; {code.WaitVBlankCoin} ... to set
L0088:
0088: 7E              LD      A,(HL) ; Check screen blanking flag
0089: E6 80           AND     $80 ; Wait for it ...
008B: C2 88 00        JP      NZ,L0088 ; {code.L0088} ... to clear (0=in blanking)
008E: 26 70           LD      H,IN0 >> 8 ; 70xx IN0 Current value ...
0090: 7E              LD      A,(HL) ; ... of IN0 inputs
0091: 21 A0 43        LD      HL,IN0Current ; {+ram.IN0Current} Value from ...
0094: 46              LD      B,(HL) ; ... last read
0095: 77              LD      (HL),A ; Store new value
0096: 2C              INC     L ; To 43A1 IN0Previous
0097: 70              LD      (HL),B ; Store old value
0098: 2E 9B           LD      L,$9B ; Bump the Counter9A+1
009A: CD 00 02        CALL    AddOneToMem ; {code.AddOneToMem}
009D: 2E 8F           LD      L,$8F ; Get CoinCount
009F: 7E              LD      A,(HL)
00A0: FE 09           CP      $09 ; Already 9?
00A2: C8              RET     Z ; Yes ... nothing more to check
00A3: D2 00 00        JP      NC,L0000 ; {code.L0000} More than 9? OOPS -- soft reset
00A6: 06 01           LD      B,$01 ; Coin bit of the input register
00A8: CD BB 00        CALL    CheckInputBits ; {code.CheckInputBits} Has the coin input gone from 1 to 0?
00AB: C8              RET     Z ; No ... no coins inserted ... done
00AC: 2E 8F           LD      L,$8F ; Add one ...
00AE: 34              INC     (HL) ; ... to coin count
00AF: 7E              LD      A,(HL) ; Current value ...
00B0: C6 20           ADD     $20 ; ... to number tile
00B2: 32 42 41        LD      ($4142),A ; {-} Change number of coins on screen
00B5: C9              RET ; Done
00B6: 00              .DB $00
00B7: C9              .DB $C9
00B8: FF              .DB $FF
00B9: FF              .DB $FF
00BA: FF              .DB $FF
CheckInputBits:
00BB: 21 A0 43        LD      HL,IN0Current ; {+ram.IN0Current} Get current ...
00BE: 7E              LD      A,(HL) ; ... input value
00BF: 2F              CPL ; Flip the current bits
00C0: A0              AND     B ; Mask off all but the ones we are checking
00C1: 2C              INC     L ; Point to last input value
00C2: A6              AND     (HL) ; Zero unles new bit is 0 and old is 1
00C3: C9              RET ; Return state
PrintNumber:
00C4: 7E              LD      A,(HL) ; Get the two digits
00C5: E6 0F           AND     $0F ; Keep the LSB
00C7: F6 20           OR      $20 ; Offset to number tile
00C9: 12              LD      (DE),A ; Store the number tile to screen memory
00CA: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn} next screen position
00CD: 05              DEC     B ; All done?
00CE: C8              RET     Z ; Yes ... out
00CF: 7E              LD      A,(HL) ; Keep the ...
00D0: 0F              RRCA ; ...
00D1: 0F              RRCA ; ...
00D2: 0F              RRCA ; ...
00D3: 0F              RRCA ; ...
00D4: E6 0F           AND     $0F ; ... LSB
00D6: F6 20           OR      $20 ; Offset to number tile
00D8: 12              LD      (DE),A ; Store the number tile to screen memory
00D9: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn} next screen position
00DC: 2B              DEC     HL ; Next data position
00DD: 05              DEC     B ; All digits done?
00DE: C2 C4 00        JP      NZ,PrintNumber ; {code.PrintNumber} No ... keep going
00E1: C9              RET ; Yes ... out
00E2: FF              .DB $FF
SplashAndDemo:
00E3: 21 99 43        LD      HL,M4399 ; {+ram.Counter98+1} starts with 0
00E6: CD 00 02        CALL    AddOneToMem ; {code.AddOneToMem} increases it by one
00E9: 01 01 00        LD      BC,$0001
00EC: CD 58 02        CALL    CompareBCtoMem ; {code.CompareBCtoMem}
00EF: CA E1 01        JP      Z,PrintCopyright ; {code.PrintCopyright} do if Counter98 is >= 00 01
00F2: 01 02 00        LD      BC,$0002
00F5: 11 1F 01        LD      DE,$011F ; used as delay counter
00F8: CD 60 02        CALL    SubtractIfEnough ; {code.SubtractIfEnough}
00FB: D2 96 01        JP      NC,SlowPrintScoreAverageTable ; {code.SlowPrintScoreAverageTable} do if Counter98 is >= 00 02
00FE: 01 20 01        LD      BC,$0120 ; for a longer break
0101: CD 58 02        CALL    CompareBCtoMem ; {code.CompareBCtoMem}
0104: CA CA 0B        JP      Z,DrawScoreAverageTableTiles ; {code.DrawScoreAverageTableTiles} do if Counter98 is >= 01 20
0107: 0E B0           LD      C,$B0 ; for a short break
0109: CD 58 02        CALL    CompareBCtoMem ; {code.CompareBCtoMem}
010C: CA E1 01        JP      Z,PrintCopyright ; {code.PrintCopyright} do if Counter98 is >= 01 B0
010F: 0E B8           LD      C,$B8
0111: CD 58 02        CALL    CompareBCtoMem ; {code.CompareBCtoMem}
0114: CA 80 05        JP      Z,InitGlobalLevelData ; {code.InitGlobalLevelData} do if Counter98 is >= 01 B8
0117: 0E C0           LD      C,$C0 ; for a short break
0119: 11 DF 02        LD      DE,$02DF
011C: CD 60 02        CALL    SubtractIfEnough ; {code.SubtractIfEnough}
011F: D2 78 00        JP      NC,SlowPrintScrollRegisterUpdate ; {code.SlowPrintScrollRegisterUpdate} do if Counter98 is >= 01 C0
0122: 01 00 03        LD      BC,$0300
0125: 11 AF 03        LD      DE,$03AF
0128: CD 60 02        CALL    SubtractIfEnough ; {code.SubtractIfEnough}
012B: D2 DC 21        JP      NC,DrawIntroBirdAnimationFrame ; {code.DrawIntroBirdAnimationFrame} do if Counter98 is >= 03 00
012E: 01 E6 03        LD      BC,$03E6
0131: 11 FF FF        LD      DE,$FFFF
0134: CD 60 02        CALL    SubtractIfEnough ; {code.SubtractIfEnough}
0137: D2 B0 03        JP      NC,GameDemo ; {code.GameDemo} do if Counter98 is >= 03 E6
013A: C9              RET
013B: FF              .DB $FF
013C: FF              .DB $FF
013D: FF              .DB $FF
013E: FF              .DB $FF
013F: FF              .DB $FF
ClearForeAndBackground:
0140: CD A0 03        CALL    ClearBackground ; {code.ClearBackground} Clear the background
0143: CD 80 00        CALL    WaitVBlankCoin ; {code.WaitVBlankCoin} Wait for VBlank
0146: CD 80 03        CALL    ClearForeground ; {code.ClearForeground} Clear the foreground (leave the 3 score rows)
0149: 21 A3 43        LD      HL,GameAndDemoOrSplash ; {+ram.GameAndDemoOrSplash}
014C: 36 02           LD      (HL),$02 ; set to: 'Intro splash'
014E: 2C              INC     L ; GameState
014F: 36 00           LD      (HL),$00 ; to 0
0151: 00              NOP ; Old command removed or space for a future replace patch
0152: 00              NOP ; ..
0153: 00              NOP ; ..
0154: 2E B8           LD      L,$B8 ; {ram.M43BC} {ram.M43BD} {ram.M43BF} LevelAndRound, CounterB9, AliensLeft, BirdsLeft, $43BC, $43BD, BonusLivesAt, $43BF to 0
0156: 06 08           LD      B,$08 ; number of bytes to clear
0158: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
015B: 2E BA           LD      L,$BA ; Set AliensLeft
015D: 36 10           LD      (HL),$10 ; to 16 aliens left in wave
015F: 2E BE           LD      L,$BE ; BonusLivesAt
0161: 3A 00 78        LD      A,(DSW0) ; {hard.DSW0} 78xx DSW0, get DIP switch settings
0164: E6 0C           AND     $0C ; mask out 0000_1100 the Bonus lives
0166: 07              RLCA ; rotate left ..
0167: 07              RLCA ; .. to 0011_0000
0168: C6 30           ADD     $30 ; $30, $40, $50, or $60
016A: 77              LD      (HL),A ; save to BonusLivesAt
016B: 26 58           LD      H,scrollRegister >> 8 ; 58xx scroll register
016D: 36 00           LD      (HL),$00 ; init screen scrolling
016F: CD 80 00        CALL    WaitVBlankCoin ; {code.WaitVBlankCoin}
0172: C9              RET
GetPlayerInputsForDemo:
0173: 7E              LD      A,(HL) ; get Counter98+1 (LSB from 16 bit counter)
0174: E6 7F           AND     $7F ; mask out 0111_1111, (counter goes from 00 to $7F)
0176: 06 CE           LD      B,$CE ; return : 1100_1110...move right
0178: FE 1F           CP      $1F ; 1st trigger point of demo
017A: D8              RET     C ; return if greater
017B: 06 FE           LD      B,$FE ; 1111_1110...push fire
017D: C8              RET     Z ; return if equal
017E: 06 AE           LD      B,$AE ; 1010_1110...move left
0180: FE 5F           CP      $5F ; 2nd trigger point of demo
0182: D8              RET     C ; return if greater
0183: 06 FE           LD      B,$FE ; 1111_1110...push fire
0185: C8              RET     Z ; return if equal
0186: 06 CE           LD      B,$CE ; 1100_1110...move right
0188: FE 7F           CP      $7F ; 3rd trigger point of demo
018A: D8              RET     C ; return if greater
018B: 06 FE           LD      B,$FE ; 1111_1110...push fire
018D: 2D              DEC     L
018E: 7E              LD      A,(HL) ; get Counter98 (MSB from 16 bit counter)
018F: FE 09           CP      $09 ; 4rd trigger point of demo
0191: C0              RET     NZ ; return if not equal
0192: 06 7E           LD      B,$7E ; 0111_1110...push shield
0194: C9              RET
0195: FF              .DB $FF
SlowPrintScoreAverageTable:
0196: 7E              LD      A,(HL) ; {ram.Counter98} get actual index for slow print ($4399)
0197: E6 1F           AND     $1F ; mask out 0001_1111
0199: FE 06           CP      $06 ; reached state 6 ?
019B: D8              RET     C ; no..return
019C: 5F              LD      E,A ; save the state
019D: 7E              LD      A,(HL) ; {ram.Counter98} get actual index for slow print ($4399)
019E: E6 E0           AND     $E0 ; mask out 1110_0000
01A0: 4F              LD      C,A ; save bits 5,6,7
01A1: 2D              DEC     L
01A2: 46              LD      B,(HL) ; {ram.Counter98} get zero reference from $4398
01A3: 2E A8           LD      L,$A8 ; ..and..
01A5: 70              LD      (HL),B ; {ram.M43A8} save it to $43A8
01A6: 2C              INC     L
01A7: 71              LD      (HL),C ; {ram.M43A9} save bits 5,6,7 to $43A9
01A8: 01 60 18        LD      BC,T1860 ; {+code.T1860} data block starting with 'INSERT  COIN' text
01AB: CD 06 02        CALL    AddBCtoMem ; {code.AddBCtoMem} stores MSB LSB
01AE: 7E              LD      A,(HL)
01AF: 2D              DEC     L
01B0: 66              LD      H,(HL)
01B1: 6F              LD      L,A
01B2: 7B              LD      A,E
01B3: 56              LD      D,(HL) ; get the data
01B4: 2C              INC     L
01B5: 5E              LD      E,(HL)
01B6: 2D              DEC     L
01B7: 4F              LD      C,A
01B8: 85              ADD     A,L
01B9: 6F              LD      L,A
01BA: 79              LD      A,C
01BB: D6 06           SUB     $06
01BD: 4F              LD      C,A
01BE: CA C8 01        JP      Z,L01C8 ; {code.L01C8}
L01C1:
01C1: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn} move to next screen position
01C4: 0D              DEC     C
01C5: C2 C1 01        JP      NZ,L01C1 ; {code.L01C1}
L01C8:
01C8: 7E              LD      A,(HL)
01C9: 12              LD      (DE),A ; print one character on the screen
01CA: C3 E0 14        JP      L14E0 ; {code.L14E0} check for coin event
01CD: C2              .DB $C2 ; {}
01CE: C0              .DB $C0
01CF: 01              .DB $01
PrintTextLines:
01D0: 56              LD      D,(HL) ; Get ...
01D1: 2C              INC     L ; ... the ...
01D2: 5E              LD      E,(HL) ; ... screen coord
01D3: 7D              LD      A,L ; Add 5 ...
01D4: C6 05           ADD     $05 ; ... go get ...
01D6: 6F              LD      L,A ; ... data
01D7: 06 1A           LD      B,$1A ; 26 columns
01D9: CD ED 01        CALL    DrawRow ; {code.DrawRow} Draw next row
01DC: 0D              DEC     C ; All lines done?
01DD: C2 D0 01        JP      NZ,PrintTextLines ; {code.PrintTextLines} No ... draw all rows
01E0: C9              RET ; Done
PrintCopyright:
01E1: CD 40 01        CALL    ClearForeAndBackground ; {code.ClearForeAndBackground}
L01E4:
01E4: 21 60 19        LD      HL,T1960 ; {+code.T1960} "PHOENIX ... U.S.A"
01E7: 0E 03           LD      C,$03 ; 3 lines at the bottom
01E9: C3 D0 01        JP      PrintTextLines ; {code.PrintTextLines} Print the copyright
01EC: FF              .DB $FF
DrawRow:
01ED: 7E              LD      A,(HL) ; Copy the data ...
01EE: 12              LD      (DE),A ; .. to the screen
01EF: 23              INC     HL ; Next in data
01F0: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn} Move DE to next row
01F3: 05              DEC     B ; All drawn?
01F4: C2 ED 01        JP      NZ,DrawRow ; {code.DrawRow} Draw them all
01F7: C9              RET ; Done
01F8: FF              .DB $FF
01F9: FF              .DB $FF
01FA: FF              .DB $FF
01FB: FF              .DB $FF
01FC: FF              .DB $FF
01FD: FF              .DB $FF
01FE: FF              .DB $FF
01FF: FF              .DB $FF
AddOneToMem:
0200: 34              INC     (HL) ; Add one to LSB
0201: C0              RET     NZ ; We didn't overflow ... done
0202: 2D              DEC     L ; Back up to MSB
0203: 34              INC     (HL) ; Carry into the MSB
0204: 2C              INC     L ; Restore point to LSB
0205: C9              RET ; Done
AddBCtoMem:
0206: 7E              LD      A,(HL) ; Get the lower byte
0207: 81              ADD     A,C ; Add C to the lower
0208: 77              LD      (HL),A ; Store the new lower
0209: 2D              DEC     L ; Back up to upper byte
020A: 7E              LD      A,(HL) ; Add B and carry ...
020B: 88              ADC     A,B ; ... to upper byte
020C: 77              LD      (HL),A ; Store the new upper byte
020D: 2C              INC     L ; Restore pointer to LSB
020E: C9              RET ; Done
020F: FF              .DB $FF
LeftOneColumn:
0210: 7B              LD      A,E ; Add ...
0211: C6 20           ADD     $20 ; ... 32 to ...
0213: 5F              LD      E,A ; ... E
0214: D0              RET     NC ; No carry ... we are done
0215: 14              INC     D ; Carry into D
0216: C9              RET ; Done
RightOneColumn:
0217: 7B              LD      A,E ; Subtract ...
0218: D6 20           SUB     $20 ; ... 32 from ...
021A: 5F              LD      E,A ; ... E
021B: D0              RET     NC ; No borrow ... we are done
021C: 15              DEC     D ; Borrow from D
021D: C9              RET ; Done
021E: FF              .DB $FF
021F: FF              .DB $FF
AddToScore:
0220: AF              XOR     A ; !! Pointless. We are about to change A and the flags
0221: 7E              LD      A,(HL) ; Lowest 2 digits
0222: 81              ADD     A,C ; Add C to score
0223: 27              DAA ; Adjust for binary coded decimal
0224: 77              LD      (HL),A ; Update lowest 2 digits
0225: 2D              DEC     L ; Point to middle 2 digits
0226: 7E              LD      A,(HL) ; Add B to ...
0227: 88              ADC     A,B ; ... score
0228: 27              DAA ; Adjust for BCD
0229: 77              LD      (HL),A ; Store the middle 2 digits
022A: 2D              DEC     L ; Point to the upper 2 digits
022B: 7E              LD      A,(HL) ; Add in ...
022C: CE 00           ADC     $00 ; ... any carry
022E: 27              DAA ; Adjust for binary coded decimal
022F: 77              LD      (HL),A ; Store the upper 2 digits
0230: 2C              INC     L ; Restore ...
0231: 2C              INC     L ; ... pointer
0232: C9              RET ; Done
0233: FF              .DB $FF
0234: FF              .DB $FF
0235: FF              .DB $FF
0236: 37              .DB $37 ; Take ...
0237: 3E              .DB $3E ; ... the BCD ...
0238: 99              .DB $99
0239: CE              .DB $CE ; ... add-complement ...
023A: 00              .DB $00
023B: 91              .DB $91 ; ... of C
023C: 86              .DB $86 ; Lower two digits
023D: 27              .DB $27 ; Adjust for BCD
023E: 77              .DB $77 ; Update lower two digits
023F: 2D              .DB $2D ; Point to middle digits
0240: 3E              .DB $3E ; Take the BCD ...
0241: 99              .DB $99
0242: CE              .DB $CE ; ... add-complement ...
0243: 00              .DB $00
0244: 90              .DB $90 ; ... of C
0245: 86              .DB $86 ; Middle two digits
0246: 27              .DB $27 ; Adjust for BCD
0247: 77              .DB $77 ; Update middle two digits
0248: 2D              .DB $2D ; Point to upper digits
0249: 3E              .DB $3E ; Take the BCD add-complement ...
024A: 99              .DB $99
024B: CE              .DB $CE ; ... of any carry
024C: 00              .DB $00
024D: 86              .DB $86 ; Upper two digits
024E: 27              .DB $27 ; Adjust for BCD
024F: 77              .DB $77 ; Update upper two digits
0250: 2C              .DB $2C ; Restore ...
0251: 2C              .DB $2C ; ... pointer
0252: C9              .DB $C9 ; Done
0253: FF              .DB $FF
0254: FF              .DB $FF
0255: FF              .DB $FF
0256: FF              .DB $FF
0257: FF              .DB $FF
CompareBCtoMem:
0258: 7E              LD      A,(HL) ; Value from memory
0259: B9              CP      C ; Are the lower values the same?
025A: C0              RET     NZ ; No ... return not-zero
025B: 2D              DEC     L ; Point to MSB
025C: 7E              LD      A,(HL) ; Get the MSB value
025D: 2C              INC     L ; Restore the pointer
025E: B8              CP      B ; Compare the MSBs
025F: C9              RET ; Return the flags
SubtractIfEnough:
0260: CD 70 02        CALL    SubtractFromMemory ; {code.SubtractFromMemory} Try subtraction. Is memory larger (or equal) to BC?
0263: D8              RET     C ; No ... ignore request
0264: CD 77 02        CALL    SubtractToMemory ; {code.SubtractToMemory} Yes ... subtract DE from memory
0267: C9              RET ; Done
0268: FF              .DB $FF
0269: FF              .DB $FF
026A: FF              .DB $FF
026B: FF              .DB $FF
026C: FF              .DB $FF
026D: FF              .DB $FF
026E: FF              .DB $FF
026F: FF              .DB $FF
SubtractFromMemory:
0270: 7E              LD      A,(HL) ; Get the low byte
0271: 91              SUB     C ; Subtract from C
0272: 2D              DEC     L ; Point to upper byte
0273: 7E              LD      A,(HL) ; Get the upper byte
0274: 98              SBC     B ; Subtract from B (with borrow)
0275: 2C              INC     L ; Restore pointer
0276: C9              RET ; Done
SubtractToMemory:
0277: 7B              LD      A,E ; Lower byte
0278: 96              SUB     (HL) ; Subtract it from memory
0279: 2D              DEC     L ; Point to upper byte
027A: 7A              LD      A,D ; Value to A
027B: 9E              SBC     (HL) ; Subtract upper byte from memory (with borrow)
027C: 2C              INC     L ; Restore pointer
027D: C9              RET ; Done
027E: FF              .DB $FF
027F: FF              .DB $FF
CompareHLtoBC:
0280: 7D              LD      A,L ; Compare lower ...
0281: B9              CP      C ; ... bytes
0282: C0              RET     NZ ; Not the same ... return NZ
0283: 7C              LD      A,H ; Compare upper ...
0284: B8              CP      B ; ... bytes
0285: C9              RET ; Return the check
0286: FF              .DB $FF
0287: FF              .DB $FF
PromptForStartGame:
0288: CD 40 01        CALL    ClearForeAndBackground ; {code.ClearForeAndBackground}
028B: 21 C0 19        LD      HL,T19C0 ; {+code.T19C0}
028E: 0E 02           LD      C,$02 ; print two lines: 'PUSH ONLY...1PLAYER BUTTON'
0290: CD D0 01        CALL    PrintTextLines ; {code.PrintTextLines}
0293: 0E 02           LD      C,$02
0295: CD E0 17        CALL    CoinChecking ; {code.CoinChecking}
0298: FE 02           CP      $02 ; 2 player mode possible if credit > 1
029A: DA A7 02        JP      C,L02A7 ; {code.L02A7}
029D: 21 A0 1B        LD      HL,T1BA0 ; {+code.T1BA0}
02A0: 0E 01           LD      C,$01 ; print one line: '1 OR 2PLAYERS BUTTON'
02A2: CD D0 01        CALL    PrintTextLines ; {code.PrintTextLines}
02A5: 0E 06           LD      C,$06
L02A7:
02A7: 3A 00 70        LD      A,(IN0) ; {hard.IN0} 70xx IN0  Get the bits...
02AA: 2F              CPL ; ...for the two...
02AB: A1              AND     C ; ...start buttons and...
02AC: C8              RET     Z ; ...ret if no start button was pressed.
02AD: CD CB 02        CALL    DecrementCoins ; {code.DecrementCoins} (GameOrAttract will be affected here as well)
02B0: CD F0 02        CALL    UpdateHiScore ; {code.UpdateHiScore}
02B3: CD 2E 03        CALL    ClearAndPrintScores ; {code.ClearAndPrintScores}
02B6: CD 50 03        CALL    GetPlayerLivesFromDip ; {code.GetPlayerLivesFromDip}
02B9: CD 40 01        CALL    ClearForeAndBackground ; {code.ClearForeAndBackground}
02BC: 26 50           LD      H,videoRegister >> 8 ; 50xx video register
02BE: 36 01           LD      (HL),$01
02C0: CD 40 01        CALL    ClearForeAndBackground ; {code.ClearForeAndBackground}
02C3: 26 50           LD      H,videoRegister >> 8 ; 50xx video register
02C5: 36 00           LD      (HL),$00
02C7: C9              RET
02C8: FF              .DB $FF
02C9: FF              .DB $FF
02CA: FF              .DB $FF
DecrementCoins:
02CB: 0E 01           LD      C,$01 ; Value for 'one player game mode'
02CD: FE 02           CP      $02 ; A register holds the value of start buttons
02CF: CA D4 02        JP      Z,L02D4 ; {code.L02D4} jump if 'start 1' was pressed.
02D2: 0E 02           LD      C,$02 ; Value for 'two players game mode'
L02D4:
02D4: 21 A2 43        LD      HL,GameOrAttract ; {+ram.GameOrAttract}
02D7: 71              LD      (HL),C ; set it to 1 or 2 and leave the attract mode.
02D8: 3A 00 78        LD      A,(DSW0) ; {hard.DSW0} 78xx DSW0
02DB: E6 10           AND     $10 ; mask for coinage 0001_0000
02DD: CA E3 02        JP      Z,L02E3 ; {code.L02E3}
02E0: 79              LD      A,C
02E1: 07              RLCA ; Multiply by 2
02E2: 4F              LD      C,A
L02E3:
02E3: 2E 8F           LD      L,CoinCount & $FF ; LSB of CoinCount
02E5: 7E              LD      A,(HL) ; get CoinCount value
02E6: 91              SUB     C ; decrement coins
02E7: 77              LD      (HL),A ; save it
02E8: C6 20           ADD     $20 ; map value to character code
02EA: 32 42 41        LD      (ForegroundScreen+$142),A ; {ram.ForegroundScreen+142} updates the number of coins on the screen
02ED: C9              RET
02EE: FF              .DB $FF
02EF: FF              .DB $FF
UpdateHiScore:
02F0: 11 83 43        LD      DE,Score1low ; {+ram.Score1low} score of player 1
02F3: 21 8B 43        LD      HL,HiScorelow ; {+ram.HiScorelow} current hi score
02F6: CD 14 03        CALL    L0314 ; {code.L0314}
02F9: D4 20 03        CALL    NC,L0320 ; {code.L0320}
02FC: 1E 87           LD      E,Score2low & $FF ; LSB of Score2low
02FE: 2E 8B           LD      L,HiScorelow & $FF ; LSB of HiScorelow
0300: CD 14 03        CALL    L0314 ; {code.L0314}
0303: D4 20 03        CALL    NC,L0320 ; {code.L0320}
0306: 2E 8B           LD      L,HiScorelow & $FF ; LSB of HiScorelow
0308: 11 41 41        LD      DE,$4141 ; {+ram.ForegroundScreen+141} High-score Screen coordinates (LSB)
030B: 06 06           LD      B,$06 ; 6 digits
030D: CD C4 00        CALL    PrintNumber ; {code.PrintNumber} Print the 6-digit number
0310: C9              RET ; Done
0311: FF              .DB $FF
0312: FF              .DB $FF
0313: FF              .DB $FF
L0314:
0314: 1A              LD      A,(DE)
0315: 96              SUB     (HL)
0316: 1D              DEC     E
0317: 2D              DEC     L
0318: 1A              LD      A,(DE)
0319: 9E              SBC     (HL)
031A: 1D              DEC     E
031B: 2D              DEC     L
031C: 1A              LD      A,(DE)
031D: 9E              SBC     (HL)
031E: C9              RET
031F: FF              .DB $FF
L0320:
0320: 1A              LD      A,(DE)
0321: 77              LD      (HL),A
0322: 13              INC     DE
0323: 23              INC     HL
0324: 1A              LD      A,(DE)
0325: 77              LD      (HL),A
0326: 13              INC     DE
0327: 23              INC     HL
0328: 1A              LD      A,(DE)
0329: 77              LD      (HL),A
032A: C9              RET
032B: FF              .DB $FF
032C: FF              .DB $FF
032D: FF              .DB $FF
ClearAndPrintScores:
032E: 21 80 43        LD      HL,M4380 ; {+ram.M4380} Clear scores..
L0331:
0331: 36 00           LD      (HL),$00 ; {ram.M4380} ..from $4380..
0333: 23              INC     HL
0334: 7D              LD      A,L
0335: FE 88           CP      $88 ; {ram.Score2low} ..to $4387
0337: C2 31 03        JP      NZ,L0331 ; {code.L0331}
033A: 2E 83           LD      L,Score1low & $FF ; print player 1 score
033C: 11 61 42        LD      DE,$4261 ; {+ram.ForegroundScreen+261} Score1 screen coordinates (LSB)
033F: 06 06           LD      B,$06 ; 6 digits
0341: CD C4 00        CALL    PrintNumber ; {code.PrintNumber}
0344: 2E 87           LD      L,Score2low & $FF ; print player 2 score
0346: 11 21 40        LD      DE,$4021 ; {+ram.ForegroundScreen+21} Score2 screen coordinates (LSB)
0349: 06 06           LD      B,$06 ; 6 digits
034B: CD C4 00        CALL    PrintNumber ; {code.PrintNumber}
034E: C9              RET ; Done
034F: FF              .DB $FF
GetPlayerLivesFromDip:
0350: 3A 00 78        LD      A,(DSW0) ; {hard.DSW0} 78xx DSW0, get DIP switch settings
0353: E6 03           AND     $03 ; mask out 0000_0011 number of lives
0355: C6 03           ADD     $03 ; to get : 03, 04, 05 or 06
0357: 47              LD      B,A
0358: 21 90 43        LD      HL,Player1Lives ; {+ram.Player1Lives}
035B: 70              LD      (HL),B ; save it
035C: 2E A2           LD      L,GameOrAttract & $FF ; LSB of GameOrAttract
035E: 7E              LD      A,(HL) ; load GameOrAttract and ..
035F: FE 01           CP      $01 ; check if one or two players mode
0361: CA 67 03        JP      Z,UpdateLivesScreen ; {code.UpdateLivesScreen}
0364: 2E 91           LD      L,Player2Lives & $FF ; LSB of Player2Lives
0366: 70              LD      (HL),B ; save it to Player2Lives
UpdateLivesScreen:
0367: 2E 90           LD      L,Player1Lives & $FF ; LSB of Player1Lives
0369: 7E              LD      A,(HL) ; load Player1Lives
036A: F6 20           OR      $20 ; map value to character code
036C: 32 A2 42        LD      (ForegroundScreen+$2A2),A ; {ram.ForegroundScreen+2A2} number of lives, for player 1 at screen ram
036F: 2C              INC     L
0370: 7E              LD      A,(HL) ; load Player2Lives
0371: F6 20           OR      $20 ; map value to character code
0373: 32 62 40        LD      (ForegroundScreen+$62),A ; {ram.ForegroundScreen+62} number of lives, for player 2 at screen ram
0376: C9              RET
UpdateSoundControlRAM:
0377: 21 8C 43        LD      HL,SoundControlA ; {+ram.SoundControlA}
037A: 77              LD      (HL),A
037B: 2C              INC     L ; and update ..
037C: 77              LD      (HL),A ; .. SoundControlB
037D: C9              RET
037E: FF              .DB $FF
037F: FF              .DB $FF
ClearForeground:
0380: 21 3F 43        LD      HL,ForegroundScreen+$33F ; {+ram.ForegroundScreen+33F} End of foreground screen
0383: 11 1F 00        LD      DE,$001F ; 00 for clear and 1F for finding end of a column
0386: 01 3F 03        LD      BC,$033F ; 03 for leaving top 3 rows and 3F for find the beginning of screen memory
L0389:
0389: 72              LD      (HL),D ; Clear the screen
038A: 2B              DEC     HL ; Next location
038B: 72              LD      (HL),D ; Clear the screen
038C: 2B              DEC     HL ; Next location
038D: 7D              LD      A,L ; Keep lower 5 ...
038E: A3              AND     E ; ... bits (32 bytes in a column)
038F: B8              CP      B ; At the top of the column?
0390: C2 89 03        JP      NZ,L0389 ; {code.L0389} No ... keep clearing the column
0393: 72              LD      (HL),D ; Clear the 4th column from the top
0394: 2B              DEC     HL ; To ...
0395: 2B              DEC     HL ; ... top ...
0396: 2B              DEC     HL ; ... of the ...
0397: 2B              DEC     HL ; ... row
0398: 7C              LD      A,H ; Have we reached ...
0399: B9              CP      C ; ... 3FFF ?
039A: C2 89 03        JP      NZ,L0389 ; {code.L0389} No ... clear all columns
039D: C9              RET ; Done
039E: FF              .DB $FF
039F: FF              .DB $FF
ClearBackground:
03A0: 21 3F 4B        LD      HL,BackgroundScreen+$33F ; {+ram.BackgroundScreen+33F} End of background screen memory
03A3: 11 47 00        LD      DE,$0047 ; 00 for clear and 47 to find the beginning of screen memory
L03A6:
03A6: 72              LD      (HL),D ; Clear the screen
03A7: 2B              DEC     HL ; Next location
03A8: 72              LD      (HL),D ; Clear the screen
03A9: 2B              DEC     HL ; Next location
03AA: 7C              LD      A,H ; Have we reached ...
03AB: BB              CP      E ; HL = 47FF ?
03AC: C2 A6 03        JP      NZ,L03A6 ; {code.L03A6} No ... keep clearing
03AF: C9              RET ; Done
GameDemo:
03B0: 01 A0 07        LD      BC,$07A0
03B3: CD 70 02        CALL    SubtractFromMemory ; {code.SubtractFromMemory}
03B6: DA CE 03        JP      C,L03CE ; {code.L03CE}
03B9: CD 58 02        CALL    CompareBCtoMem ; {code.CompareBCtoMem}
03BC: CA EB 03        JP      Z,L03EB ; {code.L03EB}
03BF: 01 60 0B        LD      BC,$0B60
03C2: CD 70 02        CALL    SubtractFromMemory ; {code.SubtractFromMemory}
03C5: DA CE 03        JP      C,L03CE ; {code.L03CE}
03C8: CD 58 02        CALL    CompareBCtoMem ; {code.CompareBCtoMem}
03CB: CA E2 03        JP      Z,L03E2 ; {code.L03E2}
L03CE:
03CE: CD 73 01        CALL    GetPlayerInputsForDemo ; {code.GetPlayerInputsForDemo}
03D1: 21 A0 43        LD      HL,IN0Current ; {+ram.IN0Current}
03D4: 7E              LD      A,(HL)
03D5: E6 01           AND     $01 ; mask out real button presses, but leave the coin event.
03D7: B0              OR      B ; feed the IN0Current with movement data
03D8: 77              LD      (HL),A ; for the game demo.
03D9: C3 00 04        JP      GameStateMachine ; {code.GameStateMachine}
03DC: C3              .DB $C3 ; {code.GameStateMachine}
03DD: 00              .DB $00
03DE: 04              .DB $04
03DF: FF              .DB $FF
03E0: FF              .DB $FF
03E1: FF              .DB $FF
L03E2:
03E2: 01 08 01        LD      BC,$0108 ; Next interval game state is 1, set LevelAndRound to 1st round, level 8 (mothership wave)
03E5: 11 00 10        LD      DE,$1000 ; set AliensLeft to 1 and BirdsLeft to 0 ?
03E8: C3 F1 03        JP      L03F1 ; {code.L03F1}
L03EB:
03EB: 01 04 01        LD      BC,$0104
03EE: 11 08 00        LD      DE,$0008
L03F1:
03F1: 21 A4 43        LD      HL,GameState ; {+ram.GameState} Next interval game state ...
03F4: 70              LD      (HL),B ; ... is 1 (flashing of score)
03F5: 2E B8           LD      L,$B8
03F7: 71              LD      (HL),C ; set LevelAndRound to 1st round, level 4 (blue birds wave)
03F8: 2E BA           LD      L,$BA
03FA: 72              LD      (HL),D ; set AliensLeft to 0
03FB: 2C              INC     L
03FC: 73              LD      (HL),E ; set BirdsLeft to 8
03FD: C9              RET
03FE: FF              .DB $FF
03FF: FF              .DB $FF
GameStateMachine:
0400: 21 0E 04        LD      HL,T040E ; {+code.T040E} Jump table
0403: 3A A4 43        LD      A,(GameState) ; {ram.GameState}
0406: 07              RLCA ; *2
0407: 85              ADD     A,L ; Offset ...
0408: 6F              LD      L,A ; ... into the table
0409: 7E              LD      A,(HL) ; MSB of destination
040A: 2C              INC     L ; Get the
040B: 6E              LD      L,(HL) ; ... LSB of destination
040C: 67              LD      H,A ; Now point to function
040D: E9              JP      (HL) ; Jump to function
T040E:
040E: 04 30           .DW L0430 ; game state 0: called once at 'new game start'
0410: 04 AC           .DW L04AC ; game state 1: called for each frame during 'flashing of score1 or 2'
0412: 05 15           .DW L0515 ; game state 2: called once for initialization of game and level data
0414: 08 00           .DW L0800 ; game state 3: called for each frame of normal game play
0416: 0A EA           .DW L0AEA ; game state 4: called for each frame of 'player ship partikel explosion'
0418: 0B 60           .DW L0B60 ; game state 5: called for each frame during 'GAME OVER' text
041A: 24 00           .DW L2400 ; game state 6: called for each frame during 'mother ship partikel explosion'
041C: 24 4C           .DW L244C ; game state 7: called for each frame during 'mother ship score display'
SetBitsVideoRegister:
041E: 3A A3 43        LD      A,(GameAndDemoOrSplash) ; {ram.GameAndDemoOrSplash}
0421: E6 01           AND     $01 ; mask out 0000_0001 for 'memory bank'
0423: 47              LD      B,A
0424: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
0427: E6 02           AND     $02 ; masc out 0000_0010 for 'color palette'
0429: B0              OR      B ; set the bits at...
042A: 32 00 50        LD      (videoRegister),A ; {hard.videoRegister} 50xx video register
042D: C9              RET
042E: 18              .DB $18 ; {}
042F: 05              .DB $05
L0430:
0430: 21 A4 43        LD      HL,GameState ; {+ram.GameState} Next interval game state ...
0433: 36 01           LD      (HL),$01 ; ... is 1 (flashing of score)
0435: 2C              INC     L
0436: 36 80           LD      (HL),$80 ; Set value for CounterA5 (score flash time)
0438: 2E A3           LD      L,GameAndDemoOrSplash & $FF ; save the value of..
043A: 7E              LD      A,(HL) ; .. GameAndDemoOrSplash
043B: 36 00           LD      (HL),$00 ; set it to game demo / game play
043D: FE 02           CP      $02
043F: C8              RET     Z ; return if it was 'Intro splash' before.
0440: 77              LD      (HL),A ; set GameAndDemoOrSplash to 'Game and demo for player 1'
0441: 2D              DEC     L
0442: 7E              LD      A,(HL) ; get GameOrAttract
0443: FE 01           CP      $01
0445: C8              RET     Z ; return if 'One player game mode'
0446: 2C              INC     L
0447: 7E              LD      A,(HL) ; get GameAndDemoOrSplash
0448: A7              AND     A ; updates the zero flag
0449: CA A0 04        JP      Z,L04A0 ; {code.L04A0} if 'Game and demo'
044C: 2E 90           LD      L,$90
044E: 7E              LD      A,(HL) ; get Player1Lives
044F: A7              AND     A ; updates the zero flag
0450: C8              RET     Z ; return if no lives left.
0451: 2E A3           LD      L,$A3
0453: 36 00           LD      (HL),$00 ; set GameAndDemoOrSplash to 'Game and demo for player 1'
0455: 01 00 01        LD      BC,$0100 ; from bank 1 to bank 0
0458: CD 60 04        CALL    CopyMemoryBank ; {code.CopyMemoryBank} to toggle the player
045B: C9              RET
045C: FF              .DB $FF
045D: FF              .DB $FF
045E: FF              .DB $FF
045F: FF              .DB $FF
CopyMemoryBank:
0460: 21 00 50        LD      HL,videoRegister ; 50xx video register
0463: 11 20 43        LD      DE,ForegroundScreen+$320 ; {+ram.ForegroundScreen+320} 1st row 1st line
L0466:
0466: 70              LD      (HL),B
0467: 1A              LD      A,(DE)
0468: 71              LD      (HL),C
0469: 12              LD      (DE),A
046A: 1C              INC     E
046B: 7B              LD      A,E
046C: E6 03           AND     $03 ; 0000_0011
046E: C2 66 04        JP      NZ,L0466 ; {code.L0466}
0471: 7B              LD      A,E
0472: E6 F0           AND     $F0 ; 1111_0000
0474: D6 20           SUB     $20
0476: 5F              LD      E,A
0477: D2 66 04        JP      NC,L0466 ; {code.L0466}
047A: 15              DEC     D
047B: 7A              LD      A,D
047C: FE 3F           CP      $3F
047E: C2 66 04        JP      NZ,L0466 ; {code.L0466}
0481: 11 80 43        LD      DE,M4380 ; {+ram.M4380}
L0484:
0484: 70              LD      (HL),B
0485: 1A              LD      A,(DE)
0486: 71              LD      (HL),C
0487: 12              LD      (DE),A
0488: 1C              INC     E
0489: 7B              LD      A,E
048A: FE B8           CP      $B8
048C: C2 84 04        JP      NZ,L0484 ; {code.L0484}
048F: 11 C0 4B        LD      DE,M4BC0 ; {!+ram.B4BC0}
L0492:
0492: 70              LD      (HL),B
0493: 1A              LD      A,(DE)
0494: 71              LD      (HL),C
0495: 12              LD      (DE),A
0496: 1C              INC     E
0497: 7B              LD      A,E
0498: FE 00           CP      $00
049A: C2 92 04        JP      NZ,L0492 ; {code.L0492}
049D: C9              RET
049E: FF              .DB $FF
049F: FF              .DB $FF
L04A0:
04A0: 2E A3           LD      L,$A3 ; set GameAndDemoOrSplash
04A2: 36 01           LD      (HL),$01 ; to 'Game for player 2'
04A4: 01 01 00        LD      BC,$0001 ; from bank 0 to bank 1
04A7: CD 60 04        CALL    CopyMemoryBank ; {code.CopyMemoryBank} to toggle the player
04AA: C9              RET
04AB: FF              .DB $FF
L04AC:
04AC: 21 A5 43        LD      HL,CounterA5 ; {+ram.CounterA5}
04AF: 35              DEC     (HL) ; decrement counter
04B0: 7E              LD      A,(HL) ; save value
04B1: 2D              DEC     L ; HL=A3A4 next game state ..
04B2: 36 02           LD      (HL),$02 ; .. is 2
04B4: A7              AND     A ; ret if ..
04B5: C8              RET     Z ; counter 0
04B6: 36 01           LD      (HL),$01 ; set game state to 1
04B8: FE 7F           CP      $7F ; 0111_1111
04BA: CA F0 07        JP      Z,L07F0 ; {code.L07F0}
04BD: 2E 9A           LD      L,$9A
04BF: 36 00           LD      (HL),$00 ; reset Counter9A MSB
04C1: 2C              INC     L ; and ..
04C2: 36 00           LD      (HL),$00 ; LSB
04C4: E6 08           AND     $08 ; 0000_1000
04C6: C2 E6 04        JP      NZ,L04E6 ; {code.L04E6}
04C9: CD E8 06        CALL    L06E8 ; {code.L06E8}
04CC: 00              NOP
04CD: 21 A3 43        LD      HL,GameAndDemoOrSplash ; {+ram.GameAndDemoOrSplash}
04D0: 7E              LD      A,(HL)
04D1: A7              AND     A ; updates the zero flag
04D2: 2E 83           LD      L,$83 ; LSB of Score1low adress
04D4: 11 61 42        LD      DE,$4261 ; {+ram.ForegroundScreen+261} screen ram addr. of lowest score digit player 1
04D7: CA DF 04        JP      Z,L04DF ; {code.L04DF}
04DA: 2E 87           LD      L,$87 ; LSB of Score2low adress
04DC: 11 21 40        LD      DE,$4021 ; {+ram.ForegroundScreen+21} screen ram addr. of lowest score digit player 2
L04DF:
04DF: 06 06           LD      B,$06 ; number of digits to print
04E1: CD C4 00        CALL    PrintNumber ; {code.PrintNumber}
04E4: C9              RET
04E5: FF              .DB $FF
L04E6:
04E6: 21 A3 43        LD      HL,GameAndDemoOrSplash ; {+ram.GameAndDemoOrSplash}
04E9: 7E              LD      A,(HL)
04EA: A7              AND     A ; updates the zero flag
04EB: 11 61 42        LD      DE,$4261 ; {+ram.ForegroundScreen+261} screen ram addr. of lowest score digit player 1
04EE: CA F4 04        JP      Z,L04F4 ; {code.L04F4}
04F1: 11 21 40        LD      DE,$4021 ; {+ram.ForegroundScreen+21} screen ram addr. of lowest score digit player 2
L04F4:
04F4: 06 06           LD      B,$06 ; number of digits to delete
04F6: CD FB 04        CALL    L04FB ; {code.L04FB}
04F9: C9              RET
04FA: FF              .DB $FF
L04FB:
04FB: 3E 00           LD      A,$00 ; delete ..
04FD: 12              LD      (DE),A ; ..one digit
04FE: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn}
0501: 05              DEC     B ; decrement number of digits
0502: C2 FB 04        JP      NZ,L04FB ; {code.L04FB} ..until
0505: C9              RET ; ..done
L0506:
0506: 21 92 43        LD      HL,M4392 ; {+ram.M4392}
0509: 06 06           LD      B,$06 ; number of bytes to clear
050B: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
050E: 3A 50 4B        LD      A,(M4B50) ; {+ram.M4B50} get alien movement pattern table MSB
0511: 32 94 43        LD      (M4394),A ; {+ram.M4394} save start value list pointer for alien movement MSB
0514: C9              RET
L0515:
0515: CD 1E 04        CALL    SetBitsVideoRegister ; {code.SetBitsVideoRegister} set color palette according to LevelAndRound
0518: 21 A4 43        LD      HL,GameState ; {+ram.GameState} Next interval game state ...
051B: 36 03           LD      (HL),$03 ; ... is 3 (normal game play)
051D: CD 80 05        CALL    InitGlobalLevelData ; {code.InitGlobalLevelData}
0520: CD 47 05        CALL    InitPlayerDataStructure ; {code.InitPlayerDataStructure}
0523: CD A0 09        CALL    L09A0 ; {code.L09A0} get screen ram adress for player ship position
L0526:
0526: CD 32 05        CALL    L0532 ; {code.L0532} init alien data for a new level and round
0529: CD 6C 0A        CALL    L0A6C ; {code.L0A6C} get screen ram adress for all aliens
052C: CD 06 05        CALL    L0506 ; {code.L0506} clear $4392 to $4397, init $4394
052F: C3 B0 32        JP      L32B0 ; {code.L32B0}
L0532:
0532: 21 50 4B        LD      HL,M4B50 ; {+ram.M4B50}
0535: 06 A0           LD      B,$A0 ; {ram.M4B50} {ram.B4BEF} clear $4B50 to $4BEF
0537: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
053A: CD EC 05        CALL    InitAlienControlStates ; {code.InitAlienControlStates}
053D: CD 50 06        CALL    L0650 ; {code.L0650} {ram.M4B50} {ram.M4B6F} copy init values for 16 aliens to $4B50-$4B6F
0540: CD 10 06        CALL    InitAlienPositions ; {code.InitAlienPositions} load alien screen coordinates (X,Y grid), for a new level and round
0543: C9              RET
0544: FF              .DB $FF
0545: FF              .DB $FF
0546: FF              .DB $FF
InitPlayerDataStructure:
0547: 21 60 05        LD      HL,T0560 ; {+code.T0560}
054A: 11 C0 43        LD      DE,PlayerState ; {+ram.PlayerState} base of data structure (grid)
054D: 06 20           LD      B,$20
054F: CD E0 05        CALL    CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
0552: 21 E0 43        LD      HL,OldPlayerShipMSB ; {+ram.OldPlayerShipMSB}
0555: 06 20           LD      B,$20
0557: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
055A: C9              RET
055B: FF              .DB $FF
055C: FF              .DB $FF
055D: FF              .DB $FF
055E: FF              .DB $FF
055F: FF              .DB $FF
T0560:
0560: 0C 10 64 D8     .DB $0C, $10, $64, $D8 ; PlayerState, PlayerShape, PlayerShipX, PlayerShipY
0564: 00 50 00 D0     .DB $00, $50, $00, $D0 ; PlayerBulletState, PlayerBulletShape, PlayerBulletX, PlayerBulletY
0568: 00 50 00 D0     .DB $00, $50, $00, $D0 ; AbovePlayerBulletState, AbovePlayerBulletShape, AbovePlayerBulletX, AbovePlayerBulletY
056C: 00 58 00 20     .DB $00, $58, $00, $20 ; EnemyBullet0State, EnemyBullet0Shape, EnemyBullet0X, EnemyBullet0Y
0570: 00 58 00 20     .DB $00, $58, $00, $20 ; EnemyBullet1State, EnemyBullet1Shape, EnemyBullet1X, EnemyBullet1Y
0574: 00 58 00 20     .DB $00, $58, $00, $20 ; EnemyBullet2State, EnemyBullet2Shape, EnemyBullet2X, EnemyBullet2Y
0578: 00 58 00 20     .DB $00, $58, $00, $20 ; EnemyBullet3State, EnemyBullet3Shape, EnemyBullet3X, EnemyBullet3Y
057C: 00 58 00 20     .DB $00, $58, $00, $20 ; EnemyBullet4State, EnemyBullet4Shape, EnemyBullet4X, EnemyBullet4Y
InitGlobalLevelData:
0580: 21 98 05        LD      HL,T0598 ; {+code.T0598}
0583: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
0586: E6 0F           AND     $0F ; 0000_1111
0588: 85              ADD     A,L
0589: 6F              LD      L,A
058A: 6E              LD      L,(HL)
058B: 26 05           LD      H,$05
058D: 11 AB 43        LD      DE,M43AB ; {+ram.M43AB}
0590: 06 0C           LD      B,$0C ; number of bytes to copy
0592: CD E0 05        CALL    CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
0595: C9              RET
0596: FF              .DB $FF
0597: FF              .DB $FF
T0598:
0598: A8 A8           .DB T05A8 & $FF, T05A8 & $FF ; init values for 1st alien wave (pointer to $05A8, $05A8)
059A: C0 C0           .DB T05C0 & $FF, T05C0 & $FF ; init values for 2st alien wave (pointer to $05C0, $05C0)
059C: A8 A8           .DB T05A8 & $FF, T05A8 & $FF ; init values for blue birds wave (pointer to $05A8, $05A8)
059E: A8 A8           .DB T05A8 & $FF, T05A8 & $FF ; init values for pink birds wave (pointer to $05A8, $05A8)
05A0: B4 CC           .DB T05B4 & $FF, T05CC & $FF ; init values for mothership wave (pointer to $05B4, $05CC)
05A2: B4 B4           .DB T05B4 & $FF, T05B4 & $FF ; init values for mothership wave (pointer to $05B4, $05B4)
05A4: A8 A8           .DB T05A8 & $FF, T05A8 & $FF ; not used? pointer to $05A8, $05A8
05A6: A8 A8           .DB T05A8 & $FF, T05A8 & $FF ; not used? pointer to $05A8, $05A8
T05A8:
05A8: 80 7F 00 00     .DB $80, $7F, $00, $00, $40, $3F, $00, T1C00 >> 8, T1C00 & $FF, $FF, $FF, $FF
05AC: 40 3F 00 1C
05B0: 00 FF FF FF
T05B4:
05B4: 60 5F 01 02     .DB $60, $5F, $01, $02, $30, $2F, $00, T1C00 >> 8, T1C00 & $FF, $C0, $FF, $FF
05B8: 30 2F 00 1C
05BC: 00 C0 FF FF
T05C0:
05C0: 80 7F 03 04     .DB $80, $7F, $03, $04, $40, $3F, $00, T1F00 >> 8, T1F00 & $FF, $A0, $FF, $FF
05C4: 40 3F 00 1F
05C8: 00 A0 FF FF
T05CC:
05CC: 60 60 05 06     .DB $60, $60, $05, $06, $50, $30, $00, T1D00 >> 8, T1D00 & $FF, $48, $FF, $FF
05D0: 50 30 00 1D
05D4: 00 48 FF FF
ClearBbytesAtHL:
05D8: AF              XOR     A ; A=0
L05D9:
05D9: 77              LD      (HL),A ; store
05DA: 23              INC     HL ; next
05DB: 05              DEC     B ; decrease counter.
05DC: C2 D9 05        JP      NZ,L05D9 ; {code.L05D9}
05DF: C9              RET
CopyBbytesHLtoDE:
05E0: 7E              LD      A,(HL) ; Copy to HL ...
05E1: 12              LD      (DE),A ; ... from DE
05E2: 23              INC     HL ; Next destination
05E3: 13              INC     DE ; Next source
05E4: 05              DEC     B ; All done?
05E5: C2 E0 05        JP      NZ,CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE} no ... keep going
05E8: C9              RET ; Out
05E9: FF              .DB $FF
05EA: FF              .DB $FF
05EB: FF              .DB $FF
InitAlienControlStates:
05EC: 21 00 15        LD      HL,T1500 ; {+code.T1500}
05EF: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
05F2: E6 0F           AND     $0F ; 0000_1111
05F4: 07              RLCA ; Multiply by 2
05F5: 85              ADD     A,L
05F6: 6F              LD      L,A
05F7: 56              LD      D,(HL)
05F8: 23              INC     HL
05F9: 5E              LD      E,(HL)
L05FA:
05FA: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
05FD: 3A BA 43        LD      A,(AliensLeft) ; {ram.AliensLeft}
0600: 47              LD      B,A
0601: A7              AND     A ; updates the zero flag
0602: C8              RET     Z ; if no AliensLeft
L0603:
0603: 72              LD      (HL),D ; set control state A
0604: 2C              INC     L
0605: 73              LD      (HL),E ; set control state B
0606: 2C              INC     L
0607: 2C              INC     L
0608: 2C              INC     L
0609: 05              DEC     B ; number of aliens left
060A: C2 03 06        JP      NZ,L0603 ; {code.L0603}
060D: C9              RET
060E: FF              .DB $FF
060F: FF              .DB $FF
InitAlienPositions:
0610: 21 3A 06        LD      HL,T063A ; {+code.T063A}
0613: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
0616: 0F              RRCA
0617: E6 0F           AND     $0F ; mask out 0000_1111
0619: 85              ADD     A,L
061A: 6F              LD      L,A
061B: 00              NOP ; Old command removed or space for a future replace patch
061C: 00              NOP ; ..
061D: 00              NOP ; ..
061E: 6E              LD      L,(HL)
061F: 26 15           LD      H,T1540 >> 8 ; MSB for T1540-T15E0
0621: 11 72 4B        LD      DE,M4B72 ; {+ram.M4B72}
0624: 3A BA 43        LD      A,(AliensLeft) ; {ram.AliensLeft}
0627: 47              LD      B,A
0628: A7              AND     A ; updates the zero flag
0629: C8              RET     Z ; if no AliensLeft
L062A:
062A: 7E              LD      A,(HL) ; get value from table
062B: 12              LD      (DE),A ; save to alien screen coordinate
062C: 23              INC     HL
062D: 13              INC     DE
062E: 7E              LD      A,(HL)
062F: 12              LD      (DE),A
0630: 23              INC     HL
0631: 13              INC     DE
0632: 13              INC     DE
0633: 13              INC     DE
0634: 05              DEC     B
0635: C2 2A 06        JP      NZ,L062A ; {code.L062A} loop for all AliensLeft
0638: C9              RET
0639: FF              .DB $FF
T063A:
063A: 60 40 E0 E0     .DB T1560 & $FF, T1540 & $FF, T15E0 & $FF, T15E0 & $FF, T15E0 & $FF, T15E0 & $FF, $FF, $FF
063E: E0 E0 FF FF
0642: C0 A0 80 80     .DB T15C0 & $FF, T15A0 & $FF, T1580 & $FF, T1580 & $FF, T1580 & $FF, T1580 & $FF, $FF, $FF
0646: 80 80 FF FF
064A: FF              .DB $FF
064B: FF              .DB $FF
064C: FF              .DB $FF
064D: FF              .DB $FF
064E: FF              .DB $FF
064F: FF              .DB $FF
L0650:
0650: 21 20 15        LD      HL,T1520 ; {+code.T1520}
0653: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
0656: E6 0F           AND     $0F ; mask out 0000_1111
0658: 07              RLCA ; Multiply by 2
0659: 85              ADD     A,L
065A: 6F              LD      L,A
065B: 56              LD      D,(HL)
065C: 23              INC     HL
065D: 5E              LD      E,(HL)
065E: 21 50 4B        LD      HL,M4B50 ; {+ram.M4B50}
0661: 3A BA 43        LD      A,(AliensLeft) ; {ram.AliensLeft}
0664: 47              LD      B,A
0665: A7              AND     A ; updates the zero flag
0666: C8              RET     Z ; if no AliensLeft
L0667:
0667: 72              LD      (HL),D
0668: 2C              INC     L
0669: 73              LD      (HL),E
066A: 2C              INC     L
066B: 05              DEC     B
066C: C2 67 06        JP      NZ,L0667 ; {code.L0667} loop for all AliensLeft
066F: C9              RET
0670: 21              .DB $21 ; {+ram.M43B1}
0671: B1              .DB $B1
0672: 43              .DB $43
0673: 46              .DB $46
0674: 2E              .DB $2E
0675: B9              .DB $B9
0676: 4E              .DB $4E ; get CounterB9 (free running 8 bit backwards) counter value
0677: 79              .DB $79
0678: 90              .DB $90
0679: 77              .DB $77
StarsScrollDown:
067A: 21 B9 43        LD      HL,CounterB9 ; {+ram.CounterB9}
067D: 7E              LD      A,(HL)
067E: 35              DEC     (HL) ; decrement the backwards counter
067F: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
0682: E6 07           AND     $07 ; mask out 0000_0111
0684: C0              RET     NZ ; continue after 8 pixels...
0685: 01 47 20        LD      BC,$2047
0688: 11 21 4B        LD      DE,$4B21 ; {+ram.BackgroundScreen+321} get character from the background screen (1st row, 2nd line)
068B: 7E              LD      A,(HL) ; {ram.CounterB9} get $43B9 free running 8 bit backwards counter value
068C: 0F              RRCA
068D: 0F              RRCA
068E: 0F              RRCA
068F: E6 1F           AND     $1F ; mask out 0001_1111
0691: 83              ADD     A,E
0692: 5F              LD      E,A
0693: 2E B2           LD      L,$B2
0695: 7E              LD      A,(HL) ; {ram.M43B2} get $43B2 (MSB of T1C00 or T1D00 or T1F00)
0696: 2C              INC     L
0697: 6E              LD      L,(HL) ; {ram.M43B3} get $43B3 (LSB of T1C00 or T1D00 or T1F00)
0698: 67              LD      H,A
L0699:
0699: 7E              LD      A,(HL)
069A: 12              LD      (DE),A ; to background screen
069B: 2C              INC     L
069C: 7B              LD      A,E
069D: 90              SUB     B
069E: 5F              LD      E,A
069F: D2 99 06        JP      NC,L0699 ; {code.L0699}
06A2: 15              DEC     D
06A3: 7A              LD      A,D
06A4: B9              CP      C
06A5: C2 99 06        JP      NZ,L0699 ; {code.L0699}
06A8: 7D              LD      A,L
06A9: 32 B3 43        LD      (M43B3),A ; {ram.M43B3}
06AC: C9              RET
06AD: FF              .DB $FF
06AE: FF              .DB $FF
06AF: FF              .DB $FF
AddPlanetsToBackground:
06B0: 21 AB 43        LD      HL,M43AB ; {+ram.M43AB} counter value for (2x2) planets
06B3: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
06B6: 4F              LD      C,A
06B7: BE              CP      (HL)
06B8: C0              RET     NZ
06B9: 7E              LD      A,(HL)
06BA: 2C              INC     L
06BB: 86              ADD     A,(HL)
06BC: 2D              DEC     L
06BD: 77              LD      (HL),A
06BE: 2C              INC     L
06BF: 2C              INC     L
06C0: 34              INC     (HL)
06C1: 46              LD      B,(HL)
06C2: 2C              INC     L
06C3: 34              INC     (HL)
06C4: 7E              LD      A,(HL)
06C5: 21 20 1E        LD      HL,T1E20 ; {+code.T1E20} MSB's of screen ram for planets
06C8: E6 1F           AND     $1F ; 0001_1111
06CA: 85              ADD     A,L
06CB: 6F              LD      L,A
06CC: 56              LD      D,(HL)
06CD: C6 20           ADD     $20
06CF: 6F              LD      L,A
06D0: 5E              LD      E,(HL)
06D1: 79              LD      A,C
06D2: 0F              RRCA
06D3: 0F              RRCA
06D4: 0F              RRCA
06D5: E6 1E           AND     $1E ; 0001_1111
06D7: 83              ADD     A,E
06D8: C6 02           ADD     $02
06DA: 5F              LD      E,A
06DB: 21 60 1E        LD      HL,T1E60 ; {+code.T1E60} LSB's of screen ram for planets
06DE: 78              LD      A,B
06DF: E6 1F           AND     $1F ; 0001_1111
06E1: 85              ADD     A,L
06E2: 6F              LD      L,A
06E3: 6E              LD      L,(HL)
06E4: CD DC 07        CALL    L07DC ; {code.L07DC} draw the characters at background
06E7: C9              RET
L06E8:
06E8: 21 00 18        LD      HL,T1800 ; {+code.T1800} base addr. table for 'screen ram adresses and static texts'
06EB: 0E 01           LD      C,$01 ; 1 column (rotated to 1 row)
06ED: C3 D0 01        JP      PrintTextLines ; {code.PrintTextLines}
L06F0:
06F0: CD 7A 06        CALL    StarsScrollDown ; {code.StarsScrollDown}
06F3: CD 40 20        CALL    AddGalaxiesToBackground ; {code.AddGalaxiesToBackground}
06F6: C3 B0 06        JP      AddPlanetsToBackground ; {code.AddPlanetsToBackground}
06F9: FF              .DB $FF
06FA: FF              .DB $FF
06FB: FF              .DB $FF
06FC: FF              .DB $FF
06FD: FF              .DB $FF
06FE: FF              .DB $FF
06FF: FF              .DB $FF
PlayerDataController:
0700: 01 C0 43        LD      BC,PlayerState ; {+ram.PlayerState} Player data structure (grid)
0703: 11 E0 43        LD      DE,OldPlayerShipMSB ; {+ram.OldPlayerShipMSB} Player data structure (screen ram)
L0706:
0706: CD 18 07        CALL    UpdateScreenObjects ; {code.UpdateScreenObjects}
0709: 79              LD      A,C
070A: C6 04           ADD     $04
070C: 4F              LD      C,A
070D: C6 20           ADD     $20
070F: 5F              LD      E,A
0710: 50              LD      D,B
0711: FE EC           CP      $EC
0713: C2 06 07        JP      NZ,L0706 ; {code.L0706} loop until $43EC
0716: C9              RET
0717: C9              .DB $C9
UpdateScreenObjects:
0718: CD 20 07        CALL    Bit4Controller ; {code.Bit4Controller} for deleting screen objects
071B: C3 40 07        JP      Bit3Controller ; {code.Bit3Controller} for drawing screen objects
071E: E6              .DB $E6
071F: EF              .DB $EF
Bit4Controller:
0720: 0A              LD      A,(BC) ; get value from data structure (grid)
0721: 67              LD      H,A ; save the bits
0722: E6 10           AND     $10 ; mask out 0001_0000 (bit4 of control state A)
0724: C8              RET     Z ; ret if bit not set.
0725: 7C              LD      A,H ; restore the bits
0726: E6 EF           AND     $EF ; mask out 1110_1111
0728: 02              LD      (BC),A ; save to control state A
0729: 07              RLCA ; Multiply by 8 ..
072A: 07              RLCA ; ..
072B: 07              RLCA ; ..
072C: E6 07           AND     $07 ; mask out 0000_0111
072E: C6 38           ADD     $38 ; add to base for jump table
0730: 6F              LD      L,A
0731: 26 07           LD      H,T0735 >> 8 ; MSB for jump table
0733: 6E              LD      L,(HL)
0734: E9              JP      (HL) ; jump to control function
T0735:
0735: 6C FF 8A 63 79 FF 9E BE .DB $6C, $FF, $8A, L0763 & $FF, L0779 & $FF, $FF, L079E & $FF, L07BE & $FF
073D: FF              .DB $FF
073E: FF              .DB $FF
073F: FF              .DB $FF
Bit3Controller:
0740: 0A              LD      A,(BC) ; get value from data structure (grid)
0741: 67              LD      H,A ; save it
0742: E6 08           AND     $08 ; mask out 0000_1000 (bit3 of control state A)
0744: C8              RET     Z ; ret if bit not set.
0745: 7C              LD      A,H ; restore the bits
0746: E6 07           AND     $07 ; mask out 0000_0111
0748: 67              LD      H,A ; save it
0749: 0F              RRCA ; Divide by 8 ..
074A: 0F              RRCA ; ..
074B: 0F              RRCA ; ..
074C: B4              OR      H ; add original bits
074D: F6 18           OR      $18 ; set 0001_1000 flag
074F: 02              LD      (BC),A ; set the bits at control state A
0750: 03              INC     BC ; go to control state B
0751: 7C              LD      A,H
0752: C6 5B           ADD     $5B ; add to base for jump table
0754: 6F              LD      L,A
0755: 26 07           LD      H,T0759 >> 8 ; MSB for jump table
0757: 6E              LD      L,(HL)
0758: E9              JP      (HL) ; jump to control function
T0759:
0759: 5E 0A 6D 88 FF AA D2 FF .DB $5E, $0A, L076D & $FF, L0788 & $FF, $FF, L07AA & $FF, L07D2 & $FF, $FF
0761: FF              .DB $FF
0762: FF              .DB $FF
L0763:
0763: EB              EX      DE,HL
0764: 56              LD      D,(HL) ; get screen ram adress MSB
0765: 23              INC     HL
0766: 5E              LD      E,(HL) ; get screen ram adress LSB
0767: 2B              DEC     HL ; restore pointer
0768: AF              XOR     A ; A=0
0769: 12              LD      (DE),A ; delete at screen
076A: EB              EX      DE,HL
076B: C9              RET
076C: EB              .DB $EB
L076D:
076D: EB              EX      DE,HL
076E: 23              INC     HL
076F: 23              INC     HL
0770: 56              LD      D,(HL) ; get MSB screen ram adress of alien
0771: 23              INC     HL
0772: 5E              LD      E,(HL) ; get LSB screen ram adress of alien
0773: 0A              LD      A,(BC) ; get alien control state B
0774: 12              LD      (DE),A ; set at screen ram
0775: 0B              DEC     BC ; move to alien control state A
0776: C9              RET
0777: 12              .DB $12
0778: 23              .DB $23
L0779:
0779: EB              EX      DE,HL
077A: 56              LD      D,(HL)
077B: 23              INC     HL
077C: 5E              LD      E,(HL)
077D: 2B              DEC     HL ; restore pointer
077E: AF              XOR     A ; A=0
077F: 12              LD      (DE),A ; delete at screen, left part
0780: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
0783: AF              XOR     A ; A=0
0784: 12              LD      (DE),A ; delete at screen, right part
0785: EB              EX      DE,HL
0786: C9              RET
0787: 23              .DB $23
L0788:
0788: EB              EX      DE,HL
0789: 23              INC     HL
078A: 23              INC     HL
078B: 56              LD      D,(HL)
078C: 23              INC     HL
078D: 5E              LD      E,(HL)
078E: 0A              LD      A,(BC) ; get alien control state B
078F: 6F              LD      L,A ; as offset for...
0790: 26 14           LD      H,T1420 >> 8 ; get T14xx alien character block shapes table
0792: 7E              LD      A,(HL)
0793: 12              LD      (DE),A ; draw alien character left part
0794: 23              INC     HL ; next character
0795: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
0798: 7E              LD      A,(HL)
0799: 12              LD      (DE),A ; draw alien character right part
079A: 0B              DEC     BC
079B: C9              RET
079C: FF              .DB $FF
079D: EB              .DB $EB
L079E:
079E: EB              EX      DE,HL
079F: 56              LD      D,(HL) ; get MSB of screen ram
07A0: 23              INC     HL
07A1: 5E              LD      E,(HL) ; get LSB of screen ram
07A2: 2B              DEC     HL ; restore pointer
07A3: AF              XOR     A ; A=0
07A4: 12              LD      (DE),A ; delete at screen, upper part
07A5: 13              INC     DE
07A6: 12              LD      (DE),A ; delete at screen, lower part
07A7: EB              EX      DE,HL
07A8: C9              RET
07A9: FF              .DB $FF
L07AA:
07AA: EB              EX      DE,HL
07AB: 23              INC     HL
07AC: 23              INC     HL
07AD: 56              LD      D,(HL)
07AE: 23              INC     HL
07AF: 5E              LD      E,(HL)
07B0: 0A              LD      A,(BC)
07B1: 6F              LD      L,A
07B2: 26 14           LD      H,T1420 >> 8 ; get T1420 alien character block shapes table
07B4: 7E              LD      A,(HL)
07B5: 12              LD      (DE),A ; draw upper part on screen
07B6: 23              INC     HL
07B7: 13              INC     DE
07B8: 7E              LD      A,(HL)
07B9: 12              LD      (DE),A ; draw lower part on screen
07BA: 0B              DEC     BC
07BB: C9              RET
07BC: 23              .DB $23
07BD: 13              .DB $13
L07BE:
07BE: EB              EX      DE,HL
07BF: 56              LD      D,(HL)
07C0: 23              INC     HL
07C1: 5E              LD      E,(HL)
07C2: 2B              DEC     HL
07C3: AF              XOR     A ; A=0
07C4: 12              LD      (DE),A ; delete upper left part
07C5: 13              INC     DE
07C6: 12              LD      (DE),A ; delete upper right part
07C7: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
07CA: AF              XOR     A ; A=0
07CB: 12              LD      (DE),A ; delete lower left part
07CC: 1B              DEC     DE
07CD: 12              LD      (DE),A ; delete lower right part
07CE: EB              EX      DE,HL
07CF: C9              RET
07D0: CD              .DB $CD
07D1: 4C              .DB $4C
L07D2:
07D2: EB              EX      DE,HL
07D3: 23              INC     HL
07D4: 23              INC     HL
07D5: 56              LD      D,(HL) ; get MSB from player data structure (screen ram)
07D6: 23              INC     HL
07D7: 5E              LD      E,(HL) ; get LSB from player data structure (screen ram)
07D8: 0A              LD      A,(BC) ; get value from player data structure (grid)
07D9: 6F              LD      L,A
07DA: 26 14           LD      H,T1400 >> 8 ; get T14xx player ship character block shapes table
L07DC:
07DC: 7E              LD      A,(HL) ; Entry point for general draw
07DD: 12              LD      (DE),A ; draw upper left part
07DE: 23              INC     HL
07DF: 13              INC     DE
07E0: 7E              LD      A,(HL)
07E1: 12              LD      (DE),A ; draw upper right part
07E2: 23              INC     HL
07E3: 1B              DEC     DE
07E4: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
07E7: 7E              LD      A,(HL)
07E8: 12              LD      (DE),A ; draw lower left part
07E9: 23              INC     HL
07EA: 13              INC     DE
07EB: 7E              LD      A,(HL)
07EC: 12              LD      (DE),A ; draw lower right part
07ED: 0B              DEC     BC
07EE: C9              RET
07EF: FF              .DB $FF
L07F0:
07F0: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
07F3: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
07F6: CD 80 03        CALL    ClearForeground ; {code.ClearForeground}
07F9: C3 1E 04        JP      SetBitsVideoRegister ; {code.SetBitsVideoRegister}
07FC: FF              .DB $FF
07FD: FF              .DB $FF
07FE: FF              .DB $FF
07FF: FF              .DB $FF
L0800:
0800: 21 14 08        LD      HL,T0814 ; {+code.T0814}
0803: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound} bit0 - 3: game level, bit4 - 7: game round
0806: 07              RLCA ; Multiply by 2 to get a 2 byte offset
0807: E6 1E           AND     $1E ; mask out 0001_1110 game level
0809: 85              ADD     A,L ; add offset ...
080A: 6F              LD      L,A ; ... to base of table
080B: 7E              LD      A,(HL) ; MSB of destination
080C: 2C              INC     L ; Get the
080D: 6E              LD      L,(HL) ; ... LSB of destination
080E: 67              LD      H,A ; Now point to function
080F: E9              JP      (HL) ; jump to corresponding function according to LevelAndRound.
0810: FF              .DB $FF
0811: FF              .DB $FF
0812: FF              .DB $FF
0813: FF              .DB $FF
T0814:
0814: 08 34           .DW L0834 ; Game level 0: called for each frame during stars scrolling down and 'aliens fade in' {code.level_0_and_2_aliens_fade_in} $0834
0816: 20 00           .DW L2000 ; Game level 1: called for each frame during 'player alife' with aliens, after 'fade in' {code.l2000_alien_wave_main_loop} $2000
0818: 08 34           .DW L0834 ; Game level 2: called for each frame during stars scrolling down and 'aliens fade in' {code.level_0_and_2_aliens_fade_in} $0834
081A: 20 00           .DW L2000 ; Game level 3: called for each frame during 'player alife' with aliens, after 'fade in' {code.l2000_alien_wave_main_loop} $2000
081C: 22 30           .DW L2230 ; Game level 4: called for each frame during 'spiral fill' {code.spiral_fill_animation} $2230
081E: 34 00           .DW L3400 ; Game level 5: called for each frame during birds level including 'fade in' {code.process_birds} $3400
0820: 22 30           .DW L2230 ; Game level 6: called for each frame during 'spiral fill' {code.spiral_fill_animation} $2230
0822: 34 00           .DW L3400 ; Game level 7: called for each frame during birds level including 'fade in' {code.process_birds} $3400
0824: 22 30           .DW L2230 ; Game level 8: called for each frame during 'spiral fill' {code.spiral_fill_animation} $2230
0826: 22 B4           .DW L22B4 ; Game level 9: called for each frame during mothership 'fade in' {code.level_9_mothership_fade_in} $22B4
0828: 22 CA           .DW L22CA ; Game level A: called for each frame during mothership and aliens 'fade in' {code.level_A_mothership_and_aliens_fade_in} $22CA
082A: 20 00           .DW L2000 ; Game level B: called for each frame during 'player alife' with aliens and mothership, after 'fade in' {code.l2000_alien_wave_main_loop} $2000
082C: 22              .DB $22 ; not used in this context
082D: 4C              .DB $4C
082E: 22              .DB $22 ; not used in this context
082F: 4C              .DB $4C
0830: 22              .DB $22 ; not used in this context
0831: 4C              .DB $4C
0832: 22              .DB $22 ; not used in this context
0833: 4C              .DB $4C
L0834:
0834: CD F0 06        CALL    L06F0 ; {code.L06F0} update scroll register and fill background
0837: 21 B4 43        LD      HL,CounterB4 ; {+ram.CounterB4}
083A: 35              DEC     (HL) ; decrement the counter
083B: 7E              LD      A,(HL)
083C: FE 15           CP      $15
083E: D0              RET     NC
083F: CD 5A 08        CALL    GetAnimationChrs ; {code.GetAnimationChrs} for 'aliens fade in'
0842: CD FA 05        CALL    L05FA ; {code.L05FA} init all alien control states
0845: CD 50 0A        CALL    AlienDataController ; {code.AlienDataController}
L0848:
0848: 21 B4 43        LD      HL,CounterB4 ; {+ram.CounterB4}
084B: 7E              LD      A,(HL)
084C: A7              AND     A ; updates the zero flag
084D: C0              RET     NZ ; if CounterB4 is 0.
084E: 2E B8           LD      L,$B8 ; LevelAndRound
0850: 34              INC     (HL) ; increment game level
0851: 2E A4           LD      L,$A4 ; Next interval game state ...
0853: 36 02           LD      (HL),$02 ; .. is 2
0855: C9              RET
0856: FF              .DB $FF
0857: FF              .DB $FF
0858: FF              .DB $FF
0859: FF              .DB $FF
GetAnimationChrs:
085A: 11 6C 08        LD      DE,$086C
085D: FE 11           CP      $11
085F: D0              RET     NC
0860: 1E 6D           LD      E,$6D
0862: FE 0D           CP      $0D
0864: D0              RET     NC
0865: 1E 6E           LD      E,$6E
0867: FE 09           CP      $09
0869: D0              RET     NC
086A: 1E 6F           LD      E,$6F
086C: FE 05           CP      $05
086E: D0              RET     NC
086F: 1E 68           LD      E,$68
0871: C9              RET
0872: FF              .DB $FF
0873: FF              .DB $FF
0874: FF              .DB $FF
0875: FF              .DB $FF
PlayerUpdate:
0876: CD 00 07        CALL    PlayerDataController ; {code.PlayerDataController}
0879: CD 86 08        CALL    L0886 ; {code.L0886} copy current player data to old player data
087C: CD A0 08        CALL    L08A0 ; {code.L08A0} update player position, bullet and shield
087F: CD A0 09        CALL    L09A0 ; {code.L09A0} get screen ram adress for player ship position
0882: CD 7A 09        CALL    L097A ; {code.L097A} map player ship position to $439E $439F
0885: C9              RET
L0886:
0886: 21 EB 43        LD      HL,M43EB ; {+ram.M43EB}
0889: 06 03           LD      B,$03
L088B:
088B: 56              LD      D,(HL)
088C: 2B              DEC     HL
088D: 5E              LD      E,(HL)
088E: 2B              DEC     HL
088F: 72              LD      (HL),D
0890: 2B              DEC     HL
0891: 73              LD      (HL),E
0892: 2B              DEC     HL
0893: 05              DEC     B
0894: C2 8B 08        JP      NZ,L088B ; {code.L088B}
0897: C9              RET
0898: FF              .DB $FF
0899: FF              .DB $FF
089A: FF              .DB $FF
089B: FF              .DB $FF
089C: FF              .DB $FF
089D: FF              .DB $FF
089E: FF              .DB $FF
089F: FF              .DB $FF
L08A0:
08A0: CD C4 08        CALL    MovePlayer ; {code.MovePlayer}
08A3: 21 C4 43        LD      HL,PlayerBulletState ; {+ram.PlayerBulletState}
08A6: CD 30 09        CALL    L0930 ; {code.L0930} get the assigned player bullet tile if fire button was pressed
08A9: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
08AC: E6 0F           AND     $0F ; 0000_1111
08AE: FE 03           CP      $03
08B0: C0              RET     NZ ; return if not game level 3 (2nd alien wave)
08B1: 21 C8 43        LD      HL,AbovePlayerBulletState ; {+ram.AbovePlayerBulletState}
08B4: CD 30 09        CALL    L0930 ; {code.L0930} get the assigned player bullet tile if fire button was pressed
08B7: C9              RET
08B8: FF              .DB $FF
08B9: FF              .DB $FF
08BA: FF              .DB $FF
08BB: FF              .DB $FF
08BC: FF              .DB $FF
08BD: FF              .DB $FF
08BE: FF              .DB $FF
08BF: FF              .DB $FF
08C0: FF              .DB $FF
08C1: FF              .DB $FF
08C2: FF              .DB $FF
08C3: FF              .DB $FF
MovePlayer:
08C4: 21 C0 43        LD      HL,PlayerState ; {+ram.PlayerState}
08C7: 7E              LD      A,(HL)
08C8: E6 08           AND     $08 ; mask out 0000_1000
08CA: CA A0 0A        JP      Z,DrawShields ; {code.DrawShields} Draw shields
08CD: 2E A6           LD      L,$A6
08CF: 7E              LD      A,(HL) ; get ShieldCount
08D0: A7              AND     A ; updates the zero flag
08D1: C2 EA 08        JP      NZ,L08EA ; {code.L08EA} if ShieldCount not 0.
08D4: 06 80           LD      B,$80 ; 1000_0000 (bit7='shield')
08D6: CD BB 00        CALL    CheckInputBits ; {code.CheckInputBits}
08D9: CA EB 08        JP      Z,L08EB ; {code.L08EB}
08DC: 2E 62           LD      L,$62
08DE: 36 40           LD      (HL),$40 ; {ram.M4362} set bit6 at $4362
08E0: 2E C0           LD      L,$C0
08E2: 7E              LD      A,(HL) ; {ram.PlayerState} get $43C0 PlayerState
08E3: E6 F7           AND     $F7 ; mask out 1111_0111
08E5: 77              LD      (HL),A
08E6: 2E A6           LD      L,$A6 ; ShieldCount
08E8: 36 FF           LD      (HL),$FF
L08EA:
08EA: 35              DEC     (HL) ; decrement ShieldCount
L08EB:
08EB: 2E C2           LD      L,PlayerShipX & $FF ; {ram.PlayerShipX} LSB of $43C2 PlayerShipX
08ED: CD 00 09        CALL    L0900 ; {code.L0900} Update the player ship x coordinate.
08F0: 01 00 16        LD      BC,T1600 ; {+code.T1600}
08F3: C3 26 09        JP      L0926 ; {code.L0926} get player ship animation frame values, mapped with T1600/T1620
08F6: FF              .DB $FF
08F7: FF              .DB $FF
08F8: FF              .DB $FF
08F9: FF              .DB $FF
08FA: FF              .DB $FF
08FB: FF              .DB $FF
08FC: FF              .DB $FF
08FD: FF              .DB $FF
08FE: FF              .DB $FF
08FF: FF              .DB $FF
L0900:
0900: 3A A0 43        LD      A,(IN0Current) ; {ram.IN0Current}
0903: 2F              CPL ; flip the current bits
0904: E6 60           AND     $60 ; mask out 0110_0000
0906: C8              RET     Z ; if no button pressed
0907: E6 40           AND     $40 ; mask out 0100_0000
0909: CA 17 09        JP      Z,L0917 ; {code.L0917}
090C: 7E              LD      A,(HL) ; {ram.PlayerShipX} get $43C2 PlayerShipX
090D: FE 0D           CP      $0D
090F: D8              RET     C ; if left boundary reached
0910: 35              DEC     (HL) ; {ram.PlayerShipX} 'left' button: dec $43C2 PlayerShipX
0911: 3E FF           LD      A,$FF
0913: 32 60 43        LD      (PlayerMoved),A ; {ram.PlayerMoved} set 'player moved' flag
0916: C9              RET
L0917:
0917: 7E              LD      A,(HL) ; {ram.PlayerShipX} get $43C2 PlayerShipX
0918: FE C0           CP      $C0
091A: D0              RET     NC ; if right boundary reached
091B: 34              INC     (HL) ; {ram.PlayerShipX} 'right' button: inc $43C2 PlayerShipX
091C: 3E FF           LD      A,$FF
091E: 32 60 43        LD      (PlayerMoved),A ; {ram.PlayerMoved} set 'player moved' flag
0921: C9              RET
0922: FF              .DB $FF
0923: FF              .DB $FF
0924: FF              .DB $FF
0925: FF              .DB $FF
L0926:
0926: 7E              LD      A,(HL)
0927: E6 07           AND     $07 ; mask out 0000_0111
0929: 81              ADD     A,C
092A: 4F              LD      C,A
092B: 0A              LD      A,(BC) ; get data from table
092C: 2D              DEC     L
092D: 77              LD      (HL),A
092E: C9              RET
092F: FF              .DB $FF
L0930:
0930: 7E              LD      A,(HL)
0931: E6 08           AND     $08 ; mask out 0000_1000
0933: C2 64 09        JP      NZ,L0964 ; {code.L0964} update PlayerBulletY (grid) and PlayerBulletState
0936: EB              EX      DE,HL
0937: 06 10           LD      B,$10 ; 0001_0000 (bit4='fire')
0939: CD BB 00        CALL    CheckInputBits ; {code.CheckInputBits}
093C: C8              RET     Z ; return if button not pressed
093D: 7E              LD      A,(HL)
093E: E6 EF           AND     $EF ; mask out 1110_1111
0940: 77              LD      (HL),A
0941: 1A              LD      A,(DE)
0942: F6 08           OR      $08 ; set bit3 at..
0944: 12              LD      (DE),A ; {ram.PlayerBulletState} $43C4 PlayerBulletState
0945: 13              INC     DE
0946: 13              INC     DE
0947: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
094A: C6 04           ADD     $04 ; mask out 0000_0100
094C: 12              LD      (DE),A
094D: 13              INC     DE
094E: 3A C3 43        LD      A,(PlayerShipY) ; {ram.PlayerShipY} $D8
0951: D6 08           SUB     $08
0953: 12              LD      (DE),A
0954: 1B              DEC     DE
0955: EB              EX      DE,HL
0956: 01 20 16        LD      BC,T1620 ; {+code.T1620} get character for player bullets
0959: CD 26 09        CALL    L0926 ; {code.L0926} get player ship animation frame values, mapped with T1600/T1620
095C: 3E 30           LD      A,$30 ; 0011_0000
095E: 32 61 43        LD      (BulletTriggered),A ; {ram.BulletTriggered} set 'bullet triggered' flag
0961: C9              RET
0962: FF              .DB $FF
0963: FF              .DB $FF
L0964:
0964: 2C              INC     L
0965: 2C              INC     L
0966: 2C              INC     L
0967: 7E              LD      A,(HL) ; {ram.PlayerBulletY} get $43C7 PlayerBulletY (grid)
0968: D6 08           SUB     $08 ; move bullet ($08 represents the bullet speed)
096A: 77              LD      (HL),A
096B: FE 1F           CP      $1F ; top of the screen reached?
096D: D0              RET     NC ; if not reached
L096E:
096E: 2D              DEC     L
096F: 2D              DEC     L
0970: 2D              DEC     L
0971: 7E              LD      A,(HL) ; {ram.PlayerBulletState} get $43C4 PlayerBulletState
0972: E6 F7           AND     $F7 ; 1111_0111
0974: 77              LD      (HL),A ; del bit3 at PlayerBulletState
0975: C9              RET
0976: FF              .DB $FF
0977: FF              .DB $FF
0978: 7E              .DB $7E
0979: E6              .DB $E6
L097A:
097A: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
097D: 47              LD      B,A ; save it
097E: E6 07           AND     $07 ; mask out 0000_0111
0980: 07              RLCA
0981: 21 38 0B        LD      HL,T0B38 ; {+code.T0B38} mapping table
0984: 85              ADD     A,L
0985: 6F              LD      L,A
0986: 78              LD      A,B ; restore it
0987: 96              SUB     (HL)
0988: 32 9E 43        LD      (M439E),A ; {ram.M439E} Mapped player ship position, left part
098B: 23              INC     HL
098C: 78              LD      A,B
098D: 86              ADD     A,(HL)
098E: 32 9F 43        LD      (M439F),A ; {ram.M439F} Mapped player ship position, right part
0991: C9              RET
0992: 32              .DB $32 ; {ram.M439F}
0993: 9F              .DB $9F
0994: 43              .DB $43
0995: C9              .DB $C9
0996: FF              .DB $FF
0997: FF              .DB $FF
0998: FF              .DB $FF
0999: FF              .DB $FF
099A: FF              .DB $FF
099B: FF              .DB $FF
099C: FF              .DB $FF
099D: FF              .DB $FF
099E: FF              .DB $FF
099F: FF              .DB $FF
L09A0:
09A0: 01 C2 43        LD      BC,PlayerShipX ; {+ram.PlayerShipX}
09A3: 11 E2 43        LD      DE,PlayerShipMSB ; {+ram.PlayerShipMSB}
L09A6:
09A6: CD BA 09        CALL    GetScreenRamAddress ; {code.GetScreenRamAddress}
09A9: 03              INC     BC
09AA: 03              INC     BC
09AB: 03              INC     BC
09AC: 13              INC     DE
09AD: 13              INC     DE
09AE: 13              INC     DE
09AF: 79              LD      A,C
09B0: FE CE           CP      $CE ; end of data structure
09B2: C2 A6 09        JP      NZ,L09A6 ; {code.L09A6}
09B5: C9              RET
09B6: FF              .DB $FF
09B7: FF              .DB $FF
09B8: FF              .DB $FF
09B9: FF              .DB $FF
GetScreenRamAddress:
09BA: 21 00 0A        LD      HL,T0A00 ; {+code.T0A00} Screen ram addresses for the top row (left to right)
09BD: 0A              LD      A,(BC) ; get the coordinate
09BE: E6 F8           AND     $F8 ; 1111_1000
09C0: 0F              RRCA ; 0111_1100
09C1: 0F              RRCA ; 0011_1110
09C2: 85              ADD     A,L
09C3: 6F              LD      L,A
09C4: 7E              LD      A,(HL) ; get MSB of screen ram address for row
09C5: 12              LD      (DE),A ; save it
09C6: 03              INC     BC
09C7: 13              INC     DE
09C8: 23              INC     HL ; move to LSB for T0A00
09C9: 0A              LD      A,(BC) ; get the coordinate
09CA: E6 F8           AND     $F8 ; 1111_1000
09CC: 0F              RRCA ; 0111_1100
09CD: 0F              RRCA ; 0011_1110
09CE: 0F              RRCA ; 0001_1111
09CF: 86              ADD     A,(HL) ; add to LSB of screen ram address for row
09D0: 12              LD      (DE),A ; save it
09D1: C9              RET
09D2: FF              .DB $FF
09D3: FF              .DB $FF
09D4: FF              .DB $FF
09D5: FF              .DB $FF
09D6: FF              .DB $FF
09D7: FF              .DB $FF
09D8: FF              .DB $FF
09D9: FF              .DB $FF
09DA: FF              .DB $FF
09DB: FF              .DB $FF
09DC: FF              .DB $FF
09DD: FF              .DB $FF
09DE: FF              .DB $FF
09DF: FF              .DB $FF
09E0: FF              .DB $FF
09E1: FF              .DB $FF
09E2: FF              .DB $FF
09E3: FF              .DB $FF
09E4: FF              .DB $FF
09E5: FF              .DB $FF
09E6: FF              .DB $FF
09E7: FF              .DB $FF
09E8: FF              .DB $FF
09E9: FF              .DB $FF
09EA: FF              .DB $FF
09EB: FF              .DB $FF
09EC: FF              .DB $FF
09ED: FF              .DB $FF
09EE: FF              .DB $FF
09EF: FF              .DB $FF
09F0: FF              .DB $FF
09F1: FF              .DB $FF
09F2: FF              .DB $FF
09F3: FF              .DB $FF
09F4: FF              .DB $FF
09F5: FF              .DB $FF
09F6: FF              .DB $FF
09F7: FF              .DB $FF
09F8: FF              .DB $FF
09F9: FF              .DB $FF
09FA: FF              .DB $FF
09FB: FF              .DB $FF
09FC: FF              .DB $FF
09FD: FF              .DB $FF
09FE: FF              .DB $FF
09FF: FF              .DB $FF
T0A00:
0A00: 43 20           .DW ForegroundScreen+$320 ; ForegroundScreen+$320 (Upper left corner of rotated screen)
0A02: 43 00           .DW ForegroundScreen+$300 ; ForegroundScreen+$300
0A04: 42 E0           .DW ForegroundScreen+$2E0 ; ForegroundScreen+$2E0
0A06: 42 C0           .DW ForegroundScreen+$2C0 ; ForegroundScreen+$2C0
0A08: 42 A0           .DW ForegroundScreen+$2A0 ; ForegroundScreen+$2A0
0A0A: 42 80           .DW ForegroundScreen+$280 ; ForegroundScreen+$280
0A0C: 42 60           .DW ForegroundScreen+$260 ; ForegroundScreen+$260
0A0E: 42 40           .DW ForegroundScreen+$240 ; ForegroundScreen+$240
0A10: 42 20           .DW ForegroundScreen+$220 ; ForegroundScreen+$220
0A12: 42 00           .DW ForegroundScreen+$200 ; ForegroundScreen+$200
0A14: 41 E0           .DW ForegroundScreen+$1E0 ; ForegroundScreen+$1E0
0A16: 41 C0           .DW ForegroundScreen+$1C0 ; ForegroundScreen+$1C0
0A18: 41 A0           .DW ForegroundScreen+$1A0 ; ForegroundScreen+$1A0
0A1A: 41 80           .DW ForegroundScreen+$180 ; ForegroundScreen+$180
0A1C: 41 60           .DW ForegroundScreen+$160 ; ForegroundScreen+$160
0A1E: 41 40           .DW ForegroundScreen+$140 ; ForegroundScreen+$140
0A20: 41 20           .DW ForegroundScreen+$120 ; ForegroundScreen+$120
0A22: 41 00           .DW ForegroundScreen+$100 ; ForegroundScreen+$100
0A24: 40 E0           .DW ForegroundScreen+$E0 ; ForegroundScreen+$E0
0A26: 40 C0           .DW ForegroundScreen+$C0 ; ForegroundScreen+$C0
0A28: 40 A0           .DW ForegroundScreen+$A0 ; ForegroundScreen+$A0
0A2A: 40 80           .DW ForegroundScreen+$80 ; ForegroundScreen+$80
0A2C: 40 60           .DW ForegroundScreen+$60 ; ForegroundScreen+$60
0A2E: 40 40           .DW ForegroundScreen+$40 ; ForegroundScreen+$40
0A30: 40 20           .DW ForegroundScreen+$20 ; ForegroundScreen+$20
0A32: 40 00           .DW ForegroundScreen ; ForegroundScreen (Upper right corner of rotated screen)
0A34: 00 00           .DB $00, $00
0A36: 00 00           .DB $00, $00
0A38: 00 00           .DB $00, $00
0A3A: 00 00           .DB $00, $00
0A3C: 00 00           .DB $00, $00
0A3E: 00 00           .DB $00, $00
T0A40:
0A40: AA BA AB BB     .DB $AA, $BA, $AB, $BB ; alien shape #37 (set A)
0A44: 80 90 81 91     .DB $80, $90, $81, $91 ; alien shape #34 (set A)
T0A48:
0A48: 74 7C 75 7D     .DB $74, $7C, $75, $7D ; alien pilot shape (set B)
0A4C: FF              .DB $FF
0A4D: FF              .DB $FF
0A4E: FF              .DB $FF
0A4F: FF              .DB $FF
AlienDataController:
0A50: 01 70 4B        LD      BC,M4B70 ; {+ram.M4B70} alien data structure (grid)
0A53: 11 B0 4B        LD      DE,M4BB0 ; {+ram.M4BB0} alien data structure (screen ram)
L0A56:
0A56: C5              PUSH    BC
0A57: CD 18 07        CALL    UpdateScreenObjects ; {code.UpdateScreenObjects}
0A5A: C1              POP     BC
0A5B: 79              LD      A,C
0A5C: C6 04           ADD     $04
0A5E: 4F              LD      C,A
0A5F: C6 40           ADD     $40
0A61: 5F              LD      E,A
0A62: 50              LD      D,B
0A63: A7              AND     A ; updates the zero flag
0A64: C2 56 0A        JP      NZ,L0A56 ; {code.L0A56}
0A67: C9              RET
0A68: FF              .DB $FF
0A69: FF              .DB $FF
0A6A: FF              .DB $FF
0A6B: FF              .DB $FF
L0A6C:
0A6C: 01 70 4B        LD      BC,M4B70 ; {+ram.M4B70} data structure for alien control and screen coordinate
0A6F: 11 B3 4B        LD      DE,M4BB3 ; {+ram.M4BB3} data structure for alien screen ram address
L0A72:
0A72: C5              PUSH    BC
0A73: D5              PUSH    DE
0A74: 0A              LD      A,(BC)
0A75: E6 18           AND     $18 ; mask out 0001_1000
0A77: CA 8A 0A        JP      Z,L0A8A ; {code.L0A8A} if 0 then skip the mapping
0A7A: EB              EX      DE,HL
0A7B: 56              LD      D,(HL)
0A7C: 2B              DEC     HL
0A7D: 5E              LD      E,(HL)
0A7E: 2B              DEC     HL
0A7F: 72              LD      (HL),D
0A80: 2B              DEC     HL
0A81: 73              LD      (HL),E
0A82: EB              EX      DE,HL
0A83: 13              INC     DE
0A84: 13              INC     DE
0A85: 03              INC     BC
0A86: 03              INC     BC
0A87: CD BA 09        CALL    GetScreenRamAddress ; {code.GetScreenRamAddress}
L0A8A:
0A8A: D1              POP     DE
0A8B: C1              POP     BC
0A8C: 79              LD      A,C
0A8D: C6 04           ADD     $04
0A8F: 4F              LD      C,A
0A90: 7B              LD      A,E
0A91: C6 04           ADD     $04
0A93: 5F              LD      E,A
0A94: FE 03           CP      $03
0A96: C2 72 0A        JP      NZ,L0A72 ; {code.L0A72} loop for all aliens
0A99: C9              RET
0A9A: FF              .DB $FF
0A9B: FF              .DB $FF
0A9C: FF              .DB $FF
0A9D: FF              .DB $FF
0A9E: FF              .DB $FF
0A9F: FF              .DB $FF
DrawShields:
0AA0: 2E E2           LD      L,PlayerShipMSB & $FF ; HL=43E2 Player's screen memory location
0AA2: 56              LD      D,(HL) ; Get the PlayerScreenRamMSB
0AA3: 23              INC     HL ; Get the ... PlayerScreenRamLSB
0AA4: 5E              LD      E,(HL) ; ... LSB (ignore any fine bit shifting of the player)
0AA5: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn} Shield pictures begin one column to the left of the ship
0AA8: 1B              DEC     DE ; Shield pictures begin one row above the ship
0AA9: 01 04 04        LD      BC,$0404 ; Shiled images are 4x4
0AAC: 2E A6           LD      L,ShieldCount & $FF ; Decrement the ...
0AAE: 35              DEC     (HL) ; ... shield counter
0AAF: 7E              LD      A,(HL) ; Current shield counter value
0AB0: 21 F0 17        LD      HL,FourByFourEmpty ; {+code.FourByFourEmpty} Blank 4x4
0AB3: FE C0           CP      $C0 ; Shield time done?
0AB5: CA 48 0B        JP      Z,ShieldsExpired ; {code.ShieldsExpired} Yes ... turn shields off
0AB8: 21 70 17        LD      HL,T1770 ; {+code.T1770} Four shield-active pictures
0ABB: E6 0C           AND     $0C ; Drop lower 2 bits (0000_1100). Images change every 4 ticks.
0ABD: 07              RLCA ; Multiply by 4 ...
0ABE: 07              RLCA ; ... to get a 16-byte offest (4x4 pictures)
0ABF: 85              ADD     A,L ; Point to the ...
0AC0: 6F              LD      L,A ; ... correct image
0AC1: C3 D6 0A        JP      DrawImageCbyB ; {code.DrawImageCbyB} Draw the new shield image
0AC4: FF              .DB $FF
0AC5: FF              .DB $FF
0AC6: FF              .DB $FF
0AC7: FF              .DB $FF
0AC8: FF              .DB $FF
0AC9: FF              .DB $FF
0ACA: FF              .DB $FF
0ACB: FF              .DB $FF
0ACC: FF              .DB $FF
0ACD: FF              .DB $FF
0ACE: FF              .DB $FF
0ACF: FF              .DB $FF
0AD0: FF              .DB $FF
0AD1: FF              .DB $FF
0AD2: FF              .DB $FF
0AD3: FF              .DB $FF
0AD4: FF              .DB $FF
0AD5: FF              .DB $FF
DrawImageCbyB:
0AD6: D5              PUSH    DE ; Hold screen pointer
0AD7: C5              PUSH    BC ; Hold width/Height
L0AD8:
0AD8: 7E              LD      A,(HL) ; Character to ...
0AD9: 12              LD      (DE),A ; ... the screen
0ADA: 23              INC     HL ; Next in data
0ADB: 13              INC     DE ; Next column on screen
0ADC: 05              DEC     B ; All rows done in this column?
0ADD: C2 D8 0A        JP      NZ,L0AD8 ; {code.L0AD8} No ... finish the rows
0AE0: C1              POP     BC ; Restore the counters
0AE1: D1              POP     DE ; Restore the screen pointer
0AE2: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn} Move over one column
0AE5: 0D              DEC     C ; All columns done?
0AE6: C2 D6 0A        JP      NZ,DrawImageCbyB ; {code.DrawImageCbyB} No ... do all columns
0AE9: C9              RET ; Done
L0AEA:
0AEA: 21 B9 43        LD      HL,CounterB9 ; {+ram.CounterB9}
0AED: 7E              LD      A,(HL)
0AEE: E6 F8           AND     $F8 ; 1111_1000
0AF0: 77              LD      (HL),A
0AF1: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
0AF4: 2E E2           LD      L,$E2 ; PlayerShipMSB
0AF6: 56              LD      D,(HL)
0AF7: 2C              INC     L ; PlayerShipLSB
0AF8: 5E              LD      E,(HL)
0AF9: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn}
0AFC: 1B              DEC     DE
0AFD: 00              NOP
0AFE: 2E A5           LD      L,$A5 ; CounterA5
0B00: 35              DEC     (HL)
0B01: 7E              LD      A,(HL)
0B02: CA 15 0B        JP      Z,L0B15 ; {code.L0B15}
0B05: FE 20           CP      $20
0B07: DA A0 0B        JP      C,L0BA0 ; {code.L0BA0}
0B0A: CA 80 03        JP      Z,ClearForeground ; {code.ClearForeground}
0B0D: C3 BA 0B        JP      L0BBA ; {code.L0BBA}
0B10: 70              .DB $70
0B11: 20              .DB $20
0B12: C3              .DB $C3
0B13: E8              .DB $E8
0B14: 20              .DB $20
L0B15:
0B15: 2D              DEC     L
0B16: 36 05           LD      (HL),$05
0B18: 2D              DEC     L
0B19: 7E              LD      A,(HL)
0B1A: C6 90           ADD     $90
0B1C: 6F              LD      L,A
0B1D: 7E              LD      A,(HL)
0B1E: A7              AND     A ; updates the zero flag
0B1F: C8              RET     Z
0B20: 35              DEC     (HL)
0B21: E5              PUSH    HL
0B22: CD 67 03        CALL    UpdateLivesScreen ; {code.UpdateLivesScreen}
0B25: E1              POP     HL
0B26: 7E              LD      A,(HL)
0B27: A7              AND     A ; updates the zero flag
0B28: C8              RET     Z
0B29: 2E A4           LD      L,$A4 ; GameState
0B2B: 36 00           LD      (HL),$00 ; set to: 'new game start'
0B2D: C9              RET
0B2E: FF              .DB $FF
0B2F: FF              .DB $FF
0B30: FF              .DB $FF
0B31: F0              .DB $F0
0B32: E0              .DB $E0
0B33: B0              .DB $B0
0B34: C0              .DB $C0
0B35: D0              .DB $D0
0B36: C0              .DB $C0
0B37: B0              .DB $B0
T0B38:
0B38: 00 08           .DB $00, $08
0B3A: 01 09           .DB $01, $09
0B3C: 02 0A           .DB $02, $0A
0B3E: 03 0B           .DB $03, $0B
0B40: 03 0B           .DB $03, $0B
0B42: 02 0A           .DB $02, $0A
0B44: 01 09           .DB $01, $09
0B46: 00 08           .DB $00, $08
ShieldsExpired:
0B48: CD D6 0A        CALL    DrawImageCbyB ; {code.DrawImageCbyB}
0B4B: 21 C0 43        LD      HL,PlayerState ; {+ram.PlayerState}
0B4E: 36 0C           LD      (HL),$0C ; 0000_1100
0B50: 2C              INC     L ; PlayerShape
0B51: 36 0C           LD      (HL),$0C ; 0000_1100
0B53: 2C              INC     L ; PlayerShipX
0B54: 7E              LD      A,(HL) ; get
0B55: E6 F8           AND     $F8 ; 1111_1000
0B57: F6 03           OR      $03 ; 0000_0011
0B59: 77              LD      (HL),A ; reset PlayerShipX
0B5A: C9              RET
0B5B: FF              .DB $FF
0B5C: FF              .DB $FF
0B5D: FF              .DB $FF
0B5E: FF              .DB $FF
0B5F: FF              .DB $FF
L0B60:
0B60: 21 A5 43        LD      HL,CounterA5 ; {+ram.CounterA5}
0B63: 34              INC     (HL)
0B64: 7E              LD      A,(HL)
0B65: FE 40           CP      $40
0B67: CA A0 03        JP      Z,ClearBackground ; {code.ClearBackground}
0B6A: 21 00 1A        LD      HL,T1A00 ; {+code.T1A00} "        GAME  OVER        "
0B6D: 0E 01           LD      C,$01
0B6F: FE 80           CP      $80
0B71: C2 95 0B        JP      NZ,L0B95 ; {code.L0B95}
0B74: 21 A4 43        LD      HL,GameState ; {+ram.GameState} Next interval game state ...
0B77: 36 00           LD      (HL),$00 ; ... is 0 (new game start)
0B79: 2E 90           LD      L,$90 ; Player1Lives
0B7B: 7E              LD      A,(HL)
0B7C: 2C              INC     L ; Player2Lives
0B7D: B6              OR      (HL)
0B7E: C0              RET     NZ
0B7F: AF              XOR     A ; A=0
0B80: 2E 98           LD      L,$98 ; Counter98
0B82: 77              LD      (HL),A
0B83: 2C              INC     L ; Counter98+1
0B84: 77              LD      (HL),A
0B85: 2E A2           LD      L,$A2 ; GameOrAttract
0B87: 77              LD      (HL),A
0B88: 2C              INC     L ; GameAndDemoOrSplash
0B89: 7E              LD      A,(HL)
0B8A: A7              AND     A ; updates the zero flag
0B8B: C8              RET     Z
0B8C: 36 00           LD      (HL),$00
0B8E: 01 00 01        LD      BC,$0100 ; from bank 1 to bank 0
0B91: CD 60 04        CALL    CopyMemoryBank ; {code.CopyMemoryBank}
0B94: C9              RET
L0B95:
0B95: CD D0 01        CALL    PrintTextLines ; {code.PrintTextLines} "        GAME  OVER        "
0B98: CD E4 01        CALL    L01E4 ; {code.L01E4} print the copyright lines
0B9B: C3 F0 1D        JP      L1DF0 ; {code.L1DF0} protection against piracy
0B9E: FF              .DB $FF
0B9F: FF              .DB $FF
L0BA0:
0BA0: 21 B8 43        LD      HL,LevelAndRound ; {+ram.LevelAndRound}
0BA3: 7E              LD      A,(HL)
0BA4: E6 0F           AND     $0F ; mask out 0000_1111
0BA6: FE 04           CP      $04
0BA8: D8              RET     C ; return if < game level 4 (alien waves)
0BA9: FE 09           CP      $09
0BAB: D0              RET     NC ; return if > game level 9 (mothership)
0BAC: 2C              INC     L ; CounterB9
0BAD: AF              XOR     A ; A=0
0BAE: 77              LD      (HL),A ; CounterB9 to 0
0BAF: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} reset the 58xx scroll register
0BB2: C3 A0 03        JP      ClearBackground ; {code.ClearBackground}
0BB5: FF              .DB $FF
0BB6: FF              .DB $FF
0BB7: FF              .DB $FF
0BB8: FF              .DB $FF
0BB9: FF              .DB $FF
L0BBA:
0BBA: 47              LD      B,A
0BBB: 0F              RRCA
0BBC: D2 C0 0F        JP      NC,L0FC0 ; {code.L0FC0} Handle animations for killed aliens
0BBF: 0F              RRCA
0BC0: 78              LD      A,B
0BC1: DA 70 20        JP      C,L2070 ; {code.L2070}
0BC4: C3 E8 20        JP      L20E8 ; {code.L20E8}
0BC7: FF              .DB $FF
0BC8: FF              .DB $FF
0BC9: FF              .DB $FF
DrawScoreAverageTableTiles:
0BCA: 21 D0 42        LD      HL,$42D0 ; {+ram.ForegroundScreen+2D0} upper left corner screen ram position
0BCD: 01 DF FF        LD      BC,$FFDF ; Screen offset constant -33 right one column (-1), up one row (-32)
0BD0: 36 64           LD      (HL),$64 ; left part of alien shape #3
0BD2: 09              ADD     HL,BC
0BD3: 23              INC     HL
0BD4: 36 65           LD      (HL),$65 ; right part of alien shape #3
0BD6: 21 F2 42        LD      HL,$42F2 ; {+ram.ForegroundScreen+2F2} screen ram position for
0BD9: 11 40 0A        LD      DE,T0A40 ; {+code.T0A40} alien shape #37 and alien shape #34
0BDC: CD 38 35        CALL    Draw4x2 ; {code.Draw4x2}
0BDF: 21 15 4B        LD      HL,$4B15 ; {+ram.BackgroundScreen+315} screen ram position for
0BE2: 11 00 3C        LD      DE,T3C00 ; {+code.T3C00} bird shape #24 ([Object 3C00](bgtiles.md#object-3c00))
0BE5: CD 28 35        CALL    Draw6x2 ; {code.Draw6x2}
0BE8: 21 D8 4A        LD      HL,$4AD8 ; {+ram.BackgroundScreen+2D8} screen ram position for
0BEB: 11 48 0A        LD      DE,T0A48 ; {+code.T0A48} alien pilot shape
0BEE: CD 48 35        CALL    Draw2x2 ; {code.Draw2x2}
0BF1: C9              RET
0BF2: FF              .DB $FF
0BF3: FF              .DB $FF
0BF4: FF              .DB $FF
0BF5: FF              .DB $FF
0BF6: FF              .DB $FF
0BF7: FF              .DB $FF
0BF8: FF              .DB $FF
0BF9: FF              .DB $FF
0BFA: FF              .DB $FF
0BFB: FF              .DB $FF
0BFC: FF              .DB $FF
0BFD: FF              .DB $FF
0BFE: FF              .DB $FF
0BFF: FF              .DB $FF
L0C00:
0C00: E5              PUSH    HL
0C01: 7D              LD      A,L
0C02: D6 72           SUB     $72
0C04: 0F              RRCA
0C05: C6 50           ADD     $50
0C07: 6F              LD      L,A
0C08: 7E              LD      A,(HL) ; get MSB pointer of alien movement pattern
0C09: 2C              INC     L
0C0A: 6E              LD      L,(HL) ; get LSB pointer of alien movement pattern
0C0B: 67              LD      H,A
0C0C: 11 04 0C        LD      DE,$0C04
0C0F: 7E              LD      A,(HL) ; get movement pattern value
0C10: E1              POP     HL
0C11: FE 07           CP      $07
0C13: DA A4 0E        JP      C,L0EA4 ; {code.L0EA4} if < $07
0C16: FE 09           CP      $09
0C18: D2 A4 0E        JP      NC,L0EA4 ; {code.L0EA4} if >= $09
0C1B: 11 20 10        LD      DE,$1020 ; set E reg. for bonus explosion score 200
0C1E: 3E FF           LD      A,$FF ; set bonus explosion flag
0C20: 32 69 43        LD      (M4369),A ; {ram.M4369}
0C23: C3 A4 0E        JP      L0EA4 ; {code.L0EA4}
0C26: FF              .DB $FF
0C27: FF              .DB $FF
0C28: FF              .DB $FF
0C29: FF              .DB $FF
0C2A: FF              .DB $FF
0C2B: FF              .DB $FF
0C2C: FF              .DB $FF
0C2D: FF              .DB $FF
0C2E: FF              .DB $FF
0C2F: FF              .DB $FF
0C30: FF              .DB $FF
0C31: FF              .DB $FF
0C32: FF              .DB $FF
0C33: FF              .DB $FF
0C34: FF              .DB $FF
0C35: FF              .DB $FF
0C36: FF              .DB $FF
0C37: FF              .DB $FF
0C38: FF              .DB $FF
0C39: FF              .DB $FF
0C3A: FF              .DB $FF
0C3B: FF              .DB $FF
0C3C: FF              .DB $FF
0C3D: FF              .DB $FF
0C3E: FF              .DB $FF
0C3F: FF              .DB $FF
EnemyBulletUpdate:
0C40: 21 FF 43        LD      HL,AlienBullet4LSB ; {+ram.EnemyBullet4LSB}
0C43: 06 05           LD      B,$05 ; 5 bullet slots
0C45: CD 8B 08        CALL    L088B ; {code.L088B} Copy current enemy bullet data to old enemy bullet data.
0C48: CD 56 0C        CALL    L0C56 ; {code.L0C56} Enemy bullets movement and animation
0C4B: CD 6B 0C        CALL    L0C6B ; {code.L0C6B} Get the screen ram address for all enemy bullets
0C4E: CD D8 0C        CALL    L0CD8 ; {code.EnemyBulletDataController} Draw or delete the screen objects
0C51: C9              RET
0C52: FF              .DB $FF
0C53: FF              .DB $FF
0C54: FF              .DB $FF
0C55: FF              .DB $FF
L0C56:
0C56: 21 CC 43        LD      HL,AlienBullet0State ; {+ram.EnemyBullet0State}
L0C59:
0C59: E5              PUSH    HL
0C5A: CD 84 0C        CALL    L0C84 ; {code.L0C84} movement and animation of enemy bullet
0C5D: E1              POP     HL
0C5E: 7D              LD      A,L
0C5F: C6 04           ADD     $04
0C61: 6F              LD      L,A
0C62: FE E0           CP      $E0
0C64: C2 59 0C        JP      NZ,L0C59 ; {code.L0C59} loop for 5 enemy bullet slots
0C67: C9              RET
0C68: FF              .DB $FF
0C69: FF              .DB $FF
0C6A: FF              .DB $FF
L0C6B:
0C6B: 01 CE 43        LD      BC,AlienBullet0X ; {+ram.EnemyBullet0X}
0C6E: 11 EE 43        LD      DE,AlienBullet0MSB ; {+ram.EnemyBullet0MSB}
L0C71:
0C71: CD BA 09        CALL    GetScreenRamAddress ; {code.GetScreenRamAddress}
0C74: 03              INC     BC
0C75: 03              INC     BC
0C76: 03              INC     BC
0C77: 13              INC     DE
0C78: 13              INC     DE
0C79: 13              INC     DE
0C7A: 79              LD      A,C
0C7B: FE E2           CP      $E2
0C7D: C2 71 0C        JP      NZ,L0C71 ; {code.L0C71} loop for 5 enemy bullet slots
0C80: C9              RET
0C81: FF              .DB $FF
0C82: FF              .DB $FF
0C83: FF              .DB $FF
L0C84:
0C84: 7E              LD      A,(HL) ; get enemy bullet control state
0C85: E6 08           AND     $08 ; 0000_1000
0C87: C8              RET     Z ; if bit 3 not set
0C88: 00              NOP
0C89: 00              NOP
0C8A: 2C              INC     L
0C8B: 7E              LD      A,(HL) ; get enemy bullet character code
0C8C: EE 04           XOR     $04 ; toggle 0000_0100 for animation: $58/$5C, $59/$5D, ...
0C8E: 77              LD      (HL),A ; set new character code
0C8F: 2C              INC     L
0C90: 2C              INC     L
0C91: 7E              LD      A,(HL) ; get enemy bullet coordinate Y
0C92: C6 04           ADD     $04 ; move bullet down
0C94: 77              LD      (HL),A
0C95: FE F9           CP      $F9 ; bottom of screen
0C97: D2 6E 09        JP      NC,L096E ; {code.L096E} if bottom of screen reached
0C9A: 2D              DEC     L ; enemy bullet coordinate X
0C9B: CD B4 0C        CALL    L0CB4 ; {code.L0CB4}
0C9E: 54              LD      D,H
0C9F: 7D              LD      A,L
0CA0: C6 20           ADD     $20 ; move to EnemyBullet(x)MSB
0CA2: 5F              LD      E,A
0CA3: EB              EX      DE,HL
0CA4: 46              LD      B,(HL) ; get EnemyBullet(x)MSB
0CA5: 23              INC     HL
0CA6: 4E              LD      C,(HL) ; get EnemyBullet(x)LSB
0CA7: 0A              LD      A,(BC)
0CA8: EB              EX      DE,HL
0CA9: 2C              INC     L
0CAA: FE E8           CP      $E8
0CAC: D2 6E 09        JP      NC,L096E ; {code.L096E} if >= $E8 (fgtiles upper part of player shield)
0CAF: C9              RET
0CB0: FF              .DB $FF
0CB1: FF              .DB $FF
0CB2: FF              .DB $FF
0CB3: FF              .DB $FF
L0CB4:
0CB4: FE DC           CP      $DC ; lower part of screen
0CB6: D8              RET     C ; if not reached
0CB7: FE E9           CP      $E9
0CB9: D0              RET     NC
0CBA: 3A 9F 43        LD      A,(M439F) ; {ram.M439F} Mapped player ship position, right part: ($17 to $C8)
0CBD: BE              CP      (HL)
0CBE: D8              RET     C
0CBF: 3A 9E 43        LD      A,(M439E) ; {ram.M439E} Mapped player ship position, left part: ($09 to $C0)
0CC2: BE              CP      (HL)
0CC3: D0              RET     NC
L0CC4:
0CC4: 3E 04           LD      A,$04 ; Next interval game state is 4 (player ship partikel explosion)
0CC6: 32 A4 43        LD      (GameState),A ; {ram.GameState}
0CC9: 3E 60           LD      A,$60 ; set a new counter value for ...
0CCB: 32 A5 43        LD      (CounterA5),A ; {ram.CounterA5}
0CCE: 3E 10           LD      A,$10 ; set flag and counter for ..
0CD0: 32 63 43        LD      (ParticleExplosion),A ; {ram.ParticleExplosion}
0CD3: C9              RET
0CD4: FF              .DB $FF
0CD5: FF              .DB $FF
0CD6: FF              .DB $FF
0CD7: FF              .DB $FF
EnemyBulletDataController:
0CD8: 01 CC 43        LD      BC,AlienBullet0State ; {+ram.EnemyBullet0State} data structure (grid)
0CDB: 11 EC 43        LD      DE,OldAlienBullet0MSB ; {+ram.OldEnemyBullet0MSB} screen ram
L0CDE:
0CDE: C5              PUSH    BC
0CDF: CD 18 07        CALL    UpdateScreenObjects ; {code.UpdateScreenObjects}
0CE2: C1              POP     BC
0CE3: 79              LD      A,C
0CE4: C6 04           ADD     $04
0CE6: 4F              LD      C,A
0CE7: C6 20           ADD     $20
0CE9: 5F              LD      E,A
0CEA: 50              LD      D,B
0CEB: A7              AND     A ; updates the zero flag
0CEC: C2 DE 0C        JP      NZ,L0CDE ; {code.L0CDE} loop for all bullet slots
0CEF: C9              RET
0CF0: FF              .DB $FF
0CF1: FF              .DB $FF
0CF2: FF              .DB $FF
0CF3: FF              .DB $FF
L0CF4:
0CF4: D1              POP     DE
0CF5: C1              POP     BC
0CF6: C9              RET
0CF7: FF              .DB $FF
0CF8: FF              .DB $FF
0CF9: FF              .DB $FF
0CFA: FF              .DB $FF
0CFB: FF              .DB $FF
0CFC: FF              .DB $FF
0CFD: FF              .DB $FF
0CFE: FF              .DB $FF
0CFF: FF              .DB $FF
0D00: FF              .DB $FF
0D01: FF              .DB $FF
0D02: FF              .DB $FF
0D03: FF              .DB $FF
0D04: FF              .DB $FF
0D05: FF              .DB $FF
0D06: FF              .DB $FF
0D07: FF              .DB $FF
0D08: 21              .DB $21 ; {+ram.Counter93}
0D09: 93              .DB $93
0D0A: 43              .DB $43
0D0B: 34              .DB $34
0D0C: 7E              .DB $7E
0D0D: E6              .DB $E6
0D0E: 07              .DB $07
0D0F: C0              .DB $C0
0D10: 2C              .DB $2C
0D11: 2C              .DB $2C
0D12: 7E              .DB $7E
0D13: 3C              .DB $3C
0D14: E6              .DB $E6
0D15: 0F              .DB $0F
0D16: 77              .DB $77
0D17: C9              .DB $C9
0D18: FF              .DB $FF
0D19: FF              .DB $FF
0D1A: FF              .DB $FF
0D1B: FF              .DB $FF
AlienMovementUpdate:
0D1C: 01 70 4B        LD      BC,M4B70 ; {+ram.M4B70} Alien control state A
0D1F: 21 50 4B        LD      HL,M4B50 ; {+ram.M4B50} Alien movement pattern table
L0D22:
0D22: CD 30 0D        CALL    L0D30 ; {code.L0D30}
0D25: 0C              INC     C
0D26: 0C              INC     C
0D27: 2C              INC     L
0D28: 3E B0           LD      A,$B0
0D2A: B9              CP      C
0D2B: C2 22 0D        JP      NZ,L0D22 ; {code.L0D22} loop for 16 aliens
0D2E: C9              RET
0D2F: FF              .DB $FF
L0D30:
0D30: 56              LD      D,(HL) ; get MSB of pointer for alien movement pattern
0D31: 23              INC     HL
0D32: 0A              LD      A,(BC) ; get alien control state A
0D33: 03              INC     BC
0D34: 03              INC     BC
0D35: E6 08           AND     $08 ; 0000_1000
0D37: C8              RET     Z ; if bit3 of alien control state A, not set
0D38: 5E              LD      E,(HL) ; get LSB of pointer for alien movement pattern
0D39: EB              EX      DE,HL
0D3A: 7E              LD      A,(HL) ; get pointer to movement list (T1000)
0D3B: 07              RLCA ; multiply by 2 to get a 2 byte offset at T1700
0D3C: C6 00           ADD     $00 ; reset all flags
0D3E: 6F              LD      L,A ; get LSB for movement direction table (T1700)
0D3F: 26 17           LD      H,T1700 >> 8 ; get MSB for movement direction table (T1700)
0D41: AF              XOR     A ; A=0
0D42: BE              CP      (HL) ; check for end marker
0D43: CA 4F 0D        JP      Z,L0D4F ; {code.L0D4F} if end reached
0D46: 23              INC     HL ; value for Y movement
0D47: BE              CP      (HL) ; check for Y movement
0D48: CA 5E 0D        JP      Z,L0D5E ; {code.L0D5E} if no Y movement
0D4B: 2B              DEC     HL ; value for X movement
0D4C: 0A              LD      A,(BC) ; get alien screen coordinate X
0D4D: 86              ADD     A,(HL) ; add both
0D4E: 02              LD      (BC),A ; save
L0D4F:
0D4F: 03              INC     BC ; alien screen coordinate Y
0D50: 23              INC     HL ; Y from alien movement direction table (T1700)
0D51: 0A              LD      A,(BC) ; get alien screen coordinate Y
0D52: 86              ADD     A,(HL) ; add both
0D53: 02              LD      (BC),A ; save
0D54: 0B              DEC     BC ; alien screen coordinate X
0D55: E6 07           AND     $07 ; 0000_0111
0D57: EB              EX      DE,HL
0D58: C0              RET     NZ ; if grid border not reached
0D59: 34              INC     (HL) ; next movement list pointer (T1000)
0D5A: C9              RET
0D5B: FF              .DB $FF
0D5C: FF              .DB $FF
0D5D: FF              .DB $FF
L0D5E:
0D5E: 2B              DEC     HL ; value for X movement
0D5F: 0A              LD      A,(BC) ; get Alien screen coordinate X
0D60: 86              ADD     A,(HL) ; add both
0D61: 02              LD      (BC),A ; save
0D62: E6 07           AND     $07 ; 0000_0111
0D64: EB              EX      DE,HL
0D65: C0              RET     NZ ; if grid border not reached
0D66: 34              INC     (HL) ; next movement list pointer (T1000)
0D67: C9              RET
0D68: FF              .DB $FF
0D69: FF              .DB $FF
0D6A: FF              .DB $FF
0D6B: FF              .DB $FF
0D6C: FF              .DB $FF
0D6D: FF              .DB $FF
0D6E: FF              .DB $FF
0D6F: FF              .DB $FF
AlienAnimationUpdate:
0D70: 01 70 4B        LD      BC,M4B70 ; {+ram.M4B70} Alien control state A
0D73: 21 50 4B        LD      HL,M4B50 ; {+ram.M4B50} Alien movement pattern table
L0D76:
0D76: CD 86 0D        CALL    L0D86 ; {code.L0D86}
0D79: 79              LD      A,C
0D7A: C6 04           ADD     $04
0D7C: 4F              LD      C,A
0D7D: 3E B0           LD      A,$B0
0D7F: B9              CP      C
0D80: C2 76 0D        JP      NZ,L0D76 ; {code.L0D76} loop for 16 aliens
0D83: C9              RET
0D84: FF              .DB $FF
0D85: FF              .DB $FF
L0D86:
0D86: 56              LD      D,(HL) ; get MSB of pointer for alien movement pattern
0D87: 23              INC     HL
0D88: 5E              LD      E,(HL) ; get LSB of pointer for alien movement pattern
0D89: 23              INC     HL
0D8A: 0A              LD      A,(BC) ; get alien control state A
0D8B: E6 08           AND     $08 ; 0000_1000
0D8D: C8              RET     Z ; if bit3 of alien control state A, not set
0D8E: EB              EX      DE,HL
0D8F: 7E              LD      A,(HL) ; get pointer to movement list (T1000)
0D90: A7              AND     A ; updates the zero flag
0D91: CC DE 0D        CALL    Z,L0DDE ; {code.L0DDE} if end of movement list reached
0D94: 6F              LD      L,A ; get pointer to movement list
0D95: 07              RLCA ; multiply by ..
0D96: 85              ADD     A,L ; .. 3, to get a 3 byte offset at T16A0
0D97: C6 A0           ADD     $A0 ; LSB of T16A0
0D99: 6F              LD      L,A
0D9A: 26 16           LD      H,T1600 >> 8 ; MSB of T16A0
0D9C: 0A              LD      A,(BC) ; get alien control state A
0D9D: E6 F8           AND     $F8 ; 1111_1000
0D9F: B6              OR      (HL) ; 1st byte of alien animation table
0DA0: 02              LD      (BC),A ; set alien control state A
0DA1: 03              INC     BC
0DA2: 03              INC     BC
0DA3: 03              INC     BC ; alien screen coordinate Y
0DA4: 23              INC     HL
0DA5: 7E              LD      A,(HL) ; get 2nd byte of alien animation table
0DA6: 23              INC     HL ; 3rd byte of alien animation table
0DA7: 0F              RRCA ; divide by 2
0DA8: DA BB 0D        JP      C,L0DBB ; {code.L0DBB} if 2nd byte is: $01
0DAB: 0F              RRCA ; divide by 2
0DAC: DA CC 0D        JP      C,L0DCC ; {code.L0DCC} if 2nd byte is: $02
0DAF: 0A              LD      A,(BC) ; get alien screen coordinate Y
0DB0: 0F              RRCA ; divide by 2
0DB1: E6 03           AND     $03 ; 0000_0011
0DB3: 86              ADD     A,(HL) ; add with 3rd byte of alien animation table
0DB4: 0B              DEC     BC ; alien screen coordinate X
0DB5: C3 D2 0D        JP      L0DD2 ; {code.L0DD2}
0DB8: FF              .DB $FF
0DB9: FF              .DB $FF
0DBA: FF              .DB $FF
L0DBB:
0DBB: 0A              LD      A,(BC) ; get alien screen coordinate Y
0DBC: 0F              RRCA ; divide by 2
0DBD: E6 03           AND     $03 ; 0000_0011
0DBF: 86              ADD     A,(HL) ; add with 3rd byte of alien animation table
0DC0: 67              LD      H,A ; save
0DC1: 0B              DEC     BC
0DC2: 0A              LD      A,(BC) ; get alien screen coordinate X
0DC3: E6 04           AND     $04 ; 0000_0100
0DC5: 84              ADD     A,H ; add with 3rd byte of alien animation table
0DC6: C3 D2 0D        JP      L0DD2 ; {code.L0DD2}
0DC9: FF              .DB $FF
0DCA: FF              .DB $FF
0DCB: FF              .DB $FF
L0DCC:
0DCC: 0B              DEC     BC
0DCD: 0A              LD      A,(BC) ; get alien screen coordinate X
0DCE: 0F              RRCA ; divide by 2
0DCF: E6 03           AND     $03 ; 0000_0011
0DD1: 86              ADD     A,(HL) ; add with 3rd byte of alien animation table
L0DD2:
0DD2: 6F              LD      L,A ; LSB for T1600
0DD3: 26 16           LD      H,T1600 >> 8 ; MSB for T1600
0DD5: 7E              LD      A,(HL) ; get data from T1600
0DD6: 0B              DEC     BC
0DD7: 02              LD      (BC),A ; set alien control state B (LSB for T14xx)
0DD8: 0B              DEC     BC ; alien control state A
0DD9: EB              EX      DE,HL
0DDA: C9              RET
0DDB: FF              .DB $FF
0DDC: FF              .DB $FF
0DDD: FF              .DB $FF
L0DDE:
0DDE: 1B              DEC     DE
0DDF: 1B              DEC     DE
0DE0: 3A 94 43        LD      A,(M4394) ; {ram.M4394} get start value list pointer for alien movement MSB
0DE3: 12              LD      (DE),A ; save alien movement pattern table MSB
0DE4: 67              LD      H,A
0DE5: 13              INC     DE
0DE6: 3A 95 43        LD      A,(M4395) ; {ram.M4395} get start value list pointer for alien movement LSB
0DE9: 12              LD      (DE),A ; save alien movement pattern table LSB
0DEA: 6F              LD      L,A
0DEB: 13              INC     DE
0DEC: 7E              LD      A,(HL) ; get value from pointer table to alien movement list
0DED: C9              RET
0DEE: FF              .DB $FF
0DEF: FF              .DB $FF
L0DF0:
0DF0: 01 C4 43        LD      BC,PlayerBulletState ; {+ram.PlayerBulletState}
0DF3: 21 E6 43        LD      HL,AbovePlayerBulletMSB ; {+ram.AbovePlayerBulletMSB} MSB screen ram: One character above player bullet
0DF6: CD 10 0E        CALL    L0E10 ; {code.L0E10}
0DF9: 01 C8 43        LD      BC,AbovePlayerBulletState ; {+ram.AbovePlayerBulletState}
0DFC: 21 EA 43        LD      HL,M43EA ; {+ram.M43EA} MSB screen ram: Left screen edge, one character above player ship
0DFF: C3 10 0E        JP      L0E10 ; {code.L0E10}
0E02: 01              .DB $01 ; {+ram.EnemyBullet0State}
0E03: CC              .DB $CC
0E04: 43              .DB $43
0E05: 21              .DB $21 ; {+ram.EnemyBullet0MSB}
0E06: EE              .DB $EE
0E07: 43              .DB $43
0E08: CD              .DB $CD ; {code.L0E10}
0E09: 10              .DB $10
0E0A: 0E              .DB $0E
0E0B: C9              .DB $C9
0E0C: FF              .DB $FF
0E0D: FF              .DB $FF
0E0E: FF              .DB $FF
0E0F: FF              .DB $FF
L0E10:
0E10: 0A              LD      A,(BC) ; ?
0E11: E6 08           AND     $08 ; mask out 0000_1000
0E13: C8              RET     Z ; if bit3 not set
0E14: 56              LD      D,(HL) ; get MSB screen ram adress
0E15: 2C              INC     L
0E16: 5E              LD      E,(HL) ; get LSB screen ram adress
0E17: 1A              LD      A,(DE) ; get character
0E18: FE C0           CP      $C0 ; bullets and alien ($50 - $BF)
0E1A: D0              RET     NC
0E1B: FE 60           CP      $60 ; alien ($60 - $BF)
0E1D: D8              RET     C ; if no character
0E1E: FE 68           CP      $68 ; alien
0E20: D2 39 0E        JP      NC,L0E39 ; {code.L0E39} if >= $68 (fgtiles aliens out of formation)
0E23: E6 07           AND     $07 ; mask out 0000_0111
0E25: 07              RLCA ; Multiply by 4 ..
0E26: 07              RLCA ; ..
0E27: C6 40           ADD     $40
0E29: 6F              LD      L,A
0E2A: 26 17           LD      H,T1740 >> 8 ; T1740
0E2C: 03              INC     BC
0E2D: 03              INC     BC
0E2E: 0A              LD      A,(BC)
0E2F: E6 07           AND     $07 ; 0000_0111
0E31: BE              CP      (HL)
0E32: D0              RET     NC
0E33: 23              INC     HL
0E34: BE              CP      (HL)
0E35: D8              RET     C
0E36: C3 70 0E        JP      L0E70 ; {code.L0E70}
L0E39:
0E39: 03              INC     BC
0E3A: 03              INC     BC
0E3B: 0A              LD      A,(BC)
0E3C: 57              LD      D,A
0E3D: 03              INC     BC
0E3E: 0A              LD      A,(BC)
0E3F: E6 F8           AND     $F8 ; 1111_1000
0E41: 5F              LD      E,A
0E42: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
L0E45:
0E45: 7E              LD      A,(HL)
0E46: 23              INC     HL
0E47: 23              INC     HL
0E48: E6 08           AND     $08 ; 0000_1000
0E4A: C4 58 0E        CALL    NZ,L0E58 ; {code.L0E58}
0E4D: 23              INC     HL
0E4E: 23              INC     HL
0E4F: 3E B0           LD      A,$B0
0E51: BD              CP      L
0E52: C2 45 0E        JP      NZ,L0E45 ; {code.L0E45}
0E55: C9              RET
0E56: FF              .DB $FF
0E57: FF              .DB $FF
L0E58:
0E58: 7A              LD      A,D
0E59: BE              CP      (HL)
0E5A: D8              RET     C
0E5B: 7E              LD      A,(HL)
0E5C: C6 08           ADD     $08
0E5E: BA              CP      D
0E5F: D8              RET     C
0E60: 23              INC     HL
0E61: 7E              LD      A,(HL)
0E62: 2B              DEC     HL
0E63: C6 04           ADD     $04
0E65: BB              CP      E
0E66: D8              RET     C
0E67: D6 0C           SUB     $0C
0E69: BB              CP      E
0E6A: D0              RET     NC
0E6B: C3 00 0C        JP      L0C00 ; {code.L0C00}
0E6E: FF              .DB $FF
0E6F: FF              .DB $FF
L0E70:
0E70: 23              INC     HL
0E71: 0A              LD      A,(BC)
0E72: E6 F8           AND     $F8 ; 1111_1000
0E74: 86              ADD     A,(HL)
0E75: 57              LD      D,A
0E76: 03              INC     BC
0E77: 0A              LD      A,(BC)
0E78: E6 F8           AND     $F8 ; 1111_1000
0E7A: 5F              LD      E,A
0E7B: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
L0E7E:
0E7E: 7E              LD      A,(HL)
0E7F: 23              INC     HL
0E80: 23              INC     HL
0E81: E6 08           AND     $08 ; 0000_1000
0E83: C4 90 0E        CALL    NZ,L0E90 ; {code.L0E90}
0E86: 23              INC     HL
0E87: 23              INC     HL
0E88: 3E B0           LD      A,$B0
0E8A: BD              CP      L
0E8B: C2 7E 0E        JP      NZ,L0E7E ; {code.L0E7E}
0E8E: C9              RET
0E8F: FF              .DB $FF
L0E90:
0E90: 7E              LD      A,(HL)
0E91: C6 02           ADD     $02
0E93: BA              CP      D
0E94: D8              RET     C
0E95: D6 05           SUB     $05
0E97: BA              CP      D
0E98: D0              RET     NC
0E99: 23              INC     HL
0E9A: 7E              LD      A,(HL)
0E9B: 2B              DEC     HL
0E9C: E6 F8           AND     $F8 ; 1111_1000
0E9E: BB              CP      E
0E9F: C0              RET     NZ
0EA0: 11 02 0C        LD      DE,$0C02 ; E reg. set to: 'bonus explosion score 020'.
0EA3: 00              NOP
L0EA4:
0EA4: 2B              DEC     HL
0EA5: 2B              DEC     HL ; move to alien X control state A
0EA6: 0B              DEC     BC
0EA7: 0B              DEC     BC
0EA8: 0B              DEC     BC ; move to PlayerBulletState
0EA9: 0A              LD      A,(BC)
0EAA: E6 F7           AND     $F7 ; 1111_0111
0EAC: 02              LD      (BC),A
L0EAD:
0EAD: 7E              LD      A,(HL)
0EAE: E6 F7           AND     $F7 ; 1111_0111
0EB0: 77              LD      (HL),A
0EB1: 7D              LD      A,L
0EB2: C6 42           ADD     $42 ; move to MSB screen ram adress alien X
0EB4: 6F              LD      L,A
0EB5: 46              LD      B,(HL) ; get MSB screen ram adress alien X
0EB6: 23              INC     HL
0EB7: 4E              LD      C,(HL) ; get LSB screen ram adress alien X
0EB8: 21 78 43        LD      HL,M4378 ; {+ram.M4378} Animation counter for the bonus explosion
0EBB: 7A              LD      A,D
0EBC: FE 10           CP      $10
0EBE: CA C3 0E        JP      Z,L0EC3 ; {code.L0EC3}
0EC1: 2E 70           LD      L,$70
L0EC3:
0EC3: 7E              LD      A,(HL)
0EC4: A7              AND     A ; updates the zero flag
0EC5: CA D5 0E        JP      Z,L0ED5 ; {code.L0ED5}
0EC8: 2C              INC     L
0EC9: 2C              INC     L
0ECA: 2C              INC     L
0ECB: 2C              INC     L
0ECC: 7E              LD      A,(HL)
0ECD: A7              AND     A ; updates the zero flag
0ECE: CA D5 0E        JP      Z,L0ED5 ; {code.L0ED5}
0ED1: 2C              INC     L
0ED2: 2C              INC     L
0ED3: 2C              INC     L
0ED4: 2C              INC     L
L0ED5:
0ED5: 72              LD      (HL),D
0ED6: 2C              INC     L
0ED7: 73              LD      (HL),E ; {ram.M4379} set $4379 (bonus explosion score)
0ED8: 2C              INC     L
0ED9: 70              LD      (HL),B
0EDA: 2C              INC     L
0EDB: 71              LD      (HL),C
0EDC: 2E 64           LD      L,$64
0EDE: 36 FF           LD      (HL),$FF
0EE0: 2E BA           LD      L,$BA ; AliensLeft
0EE2: 35              DEC     (HL) ; decrement it
0EE3: E1              POP     HL
0EE4: E1              POP     HL
0EE5: E9              JP      (HL) ; to: $0DF9, $0027, $2199, $2006
0EE6: FF              .DB $FF
0EE7: FF              .DB $FF
0EE8: FF              .DB $FF
0EE9: FF              .DB $FF
0EEA: FF              .DB $FF
0EEB: FF              .DB $FF
0EEC: FF              .DB $FF
0EED: FF              .DB $FF
0EEE: FF              .DB $FF
0EEF: FF              .DB $FF
0EF0: FF              .DB $FF
0EF1: FF              .DB $FF
0EF2: FF              .DB $FF
0EF3: FF              .DB $FF
0EF4: FF              .DB $FF
0EF5: FF              .DB $FF
0EF6: FF              .DB $FF
0EF7: FF              .DB $FF
0EF8: FF              .DB $FF
0EF9: FF              .DB $FF
0EFA: FF              .DB $FF
0EFB: FF              .DB $FF
0EFC: FF              .DB $FF
0EFD: FF              .DB $FF
0EFE: FF              .DB $FF
0EFF: FF              .DB $FF
L0F00:
0F00: 21 A6 43        LD      HL,ShieldCount ; {+ram.ShieldCount}
0F03: 7E              LD      A,(HL)
0F04: FE C0           CP      $C0
0F06: D2 74 0F        JP      NC,L0F74 ; {code.L0F74} if >= $C0 (fgtiles all explosion parts)
0F09: 2E E2           LD      L,$E2
0F0B: 56              LD      D,(HL) ; {ram.PlayerShipMSB} get $43E2 PlayerShipMSB
0F0C: 2C              INC     L
0F0D: 5E              LD      E,(HL) ; {ram.PlayerShipLSB} get $43E3 PlayerShipLSB
0F0E: 01 02 02        LD      BC,$0202
0F11: CD 56 0F        CALL    L0F56 ; {code.L0F56} 'alien with player' collision check
0F14: C8              RET     Z ; if no collision
0F15: 00              NOP
0F16: 00              NOP
0F17: 21 9E 43        LD      HL,M439E ; {+ram.M439E} Mapped player ship position, left part: ($09 to $C0)
0F1A: 7E              LD      A,(HL)
0F1B: D6 06           SUB     $06
0F1D: 47              LD      B,A
0F1E: 2C              INC     L
0F1F: 4E              LD      C,(HL)
0F20: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
L0F23:
0F23: 7E              LD      A,(HL)
0F24: 2C              INC     L
0F25: 2C              INC     L
0F26: E6 08           AND     $08 ; 0000_1000
0F28: C4 38 0F        CALL    NZ,L0F38 ; {code.L0F38}
0F2B: 2C              INC     L
0F2C: 2C              INC     L
0F2D: 3E B0           LD      A,$B0
0F2F: BD              CP      L
0F30: C2 23 0F        JP      NZ,L0F23 ; {code.L0F23}
0F33: C9              RET
0F34: FF              .DB $FF
0F35: FF              .DB $FF
0F36: FF              .DB $FF
0F37: FF              .DB $FF
L0F38:
0F38: 2C              INC     L
0F39: 7E              LD      A,(HL)
0F3A: 2D              DEC     L
0F3B: FE D2           CP      $D2
0F3D: D8              RET     C
0F3E: FE E7           CP      $E7
0F40: D0              RET     NC
0F41: 7E              LD      A,(HL)
0F42: B9              CP      C
0F43: D0              RET     NC
0F44: B8              CP      B
0F45: D8              RET     C
0F46: CD C4 0C        CALL    L0CC4 ; {code.L0CC4}
0F49: 11 04 0D        LD      DE,$0D04
0F4C: 2B              DEC     HL
0F4D: 2B              DEC     HL
0F4E: C3 AD 0E        JP      L0EAD ; {code.L0EAD}
0F51: AD              .DB $AD
0F52: 0E              .DB $0E
0F53: FF              .DB $FF
0F54: FF              .DB $FF
0F55: FF              .DB $FF
L0F56:
0F56: C5              PUSH    BC
0F57: D5              PUSH    DE
L0F58:
0F58: 1A              LD      A,(DE) ; get upper left character of player ship
0F59: FE 60           CP      $60 ; alien characters ($60 to $BF)
0F5B: DA 63 0F        JP      C,L0F63 ; {code.L0F63} if no collision on left side
0F5E: FE C0           CP      $C0
0F60: DA F4 0C        JP      C,L0CF4 ; {code.L0CF4} if collision on left or right side
L0F63:
0F63: 13              INC     DE ; get upper right character of player ship
0F64: 05              DEC     B
0F65: C2 58 0F        JP      NZ,L0F58 ; {code.L0F58}
0F68: D1              POP     DE
0F69: C1              POP     BC
0F6A: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn} for lower part of player ship
0F6D: 0D              DEC     C
0F6E: C2 56 0F        JP      NZ,L0F56 ; {code.L0F56}
0F71: C9              RET
0F72: FF              .DB $FF
0F73: FF              .DB $FF
L0F74:
0F74: 2E E2           LD      L,$E2 ; PlayerShipMSB
0F76: 56              LD      D,(HL)
0F77: 2C              INC     L ; PlayerShipLSB
0F78: 5E              LD      E,(HL)
0F79: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
0F7C: 1B              DEC     DE
0F7D: 01 04 04        LD      BC,$0404
0F80: CD 56 0F        CALL    L0F56 ; {code.L0F56}
0F83: C8              RET     Z
0F84: 00              NOP
0F85: 00              NOP
0F86: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
0F89: D6 0E           SUB     $0E
0F8B: 47              LD      B,A
0F8C: C6 2D           ADD     $2D
0F8E: 4F              LD      C,A
0F8F: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
L0F92:
0F92: 7E              LD      A,(HL)
0F93: 2C              INC     L
0F94: 2C              INC     L
0F95: E6 08           AND     $08 ; 0000_1000
0F97: C4 A6 0F        CALL    NZ,L0FA6 ; {code.L0FA6}
0F9A: 2C              INC     L
0F9B: 2C              INC     L
0F9C: 3E B0           LD      A,$B0
0F9E: BD              CP      L
0F9F: C2 92 0F        JP      NZ,L0F92 ; {code.L0F92}
0FA2: C9              RET
0FA3: FF              .DB $FF
0FA4: FF              .DB $FF
0FA5: FF              .DB $FF
L0FA6:
0FA6: 2C              INC     L
0FA7: 7E              LD      A,(HL)
0FA8: 2D              DEC     L
0FA9: FE CA           CP      $CA
0FAB: D8              RET     C
0FAC: FE EF           CP      $EF
0FAE: D0              RET     NC
0FAF: 7E              LD      A,(HL)
0FB0: B9              CP      C
0FB1: D0              RET     NC
0FB2: B8              CP      B
0FB3: D8              RET     C
0FB4: 11 02 0D        LD      DE,$0D02
0FB7: 2B              DEC     HL
0FB8: 2B              DEC     HL
0FB9: C3 AD 0E        JP      L0EAD ; {code.L0EAD}
0FBC: AD              .DB $AD
0FBD: 0E              .DB $0E
0FBE: FF              .DB $FF
0FBF: FF              .DB $FF
L0FC0:
0FC0: 21 70 43        LD      HL,M4370 ; {+ram.M4370}
0FC3: CD D8 0F        CALL    L0FD8 ; {code.L0FD8}
0FC6: 21 74 43        LD      HL,M4374 ; {+ram.M4374}
0FC9: CD D8 0F        CALL    L0FD8 ; {code.L0FD8}
0FCC: 21 78 43        LD      HL,M4378 ; {+ram.M4378}
0FCF: CD 58 37        CALL    L3758 ; {code.L3758}
0FD2: 21 7C 43        LD      HL,M437C ; {+ram.M437C}
0FD5: C3 58 37        JP      L3758 ; {code.L3758}
L0FD8:
0FD8: 7E              LD      A,(HL)
0FD9: A7              AND     A ; updates the zero flag
0FDA: C8              RET     Z
0FDB: 46              LD      B,(HL)
0FDC: 35              DEC     (HL)
0FDD: 2C              INC     L
0FDE: 2C              INC     L
0FDF: 56              LD      D,(HL)
0FE0: 2C              INC     L
0FE1: 5E              LD      E,(HL)
0FE2: 00              NOP
0FE3: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn}
0FE6: 78              LD      A,B
0FE7: E6 0E           AND     $0E ; 0000_1110
0FE9: 0F              RRCA
0FEA: C6 B0           ADD     $B0
0FEC: 6F              LD      L,A
0FED: 26 17           LD      H,$17
0FEF: 6E              LD      L,(HL)
0FF0: EB              EX      DE,HL
0FF1: 01 DF FF        LD      BC,$FFDF ; Screen offset constant -33 right one column (-1), up one row (-32)
0FF4: C3 40 35        JP      Draw3x2 ; {code.Draw3x2}
0FF7: 68              .DB $68
0FF8: 3E              .DB $3E
0FF9: 05              .DB $05
0FFA: 32              .DB $32 ; {ram.M4396}
0FFB: 96              .DB $96
0FFC: 43              .DB $43
0FFD: C3              .DB $C3 ; {code.L0EA4}
0FFE: A4              .DB $A4
0FFF: 0E              .DB $0E
T1000:
1000: 01 01 01 01     .DB $01, $01, $01, $01, $02, $02, $02, $02
1004: 02 02 02 02
1008: 02 02 02 02     .DB $02, $02, $02, $02, $01, $01, $01, $01
100C: 01 01 01 01
1010: 00              .DB $00
1011: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
1015: FF FF FF FF
1019: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF
101D: FF FF FF
T1020:
1020: 10 11 12 13     .DB $10, $11, $12, $13, $10, $1D, $0D, $0E
1024: 10 1D 0D 0E
1028: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $06, $06
102C: 0B 0C 06 06
1030: 1E 03 1F 05     .DB $1E, $03, $1F, $05, $1C, $04, $1D, $06
1034: 1C 04 1D 06
1038: 1E 03 03 03     .DB $1E, $03, $03, $03, $03, $03, $1F, $1C
103C: 03 03 1F 1C
1040: 1D 1E 03 03     .DB $1D, $1E, $03, $03, $03, $03, $03, $1F
1044: 03 03 03 1F
1048: 05 1C 04 1D     .DB $05, $1C, $04, $1D, $06, $1E, $03, $1F
104C: 06 1E 03 1F
1050: 05 05 05 05     .DB $05, $05, $05, $05, $05, $05, $05, $05
1054: 05 05 05 05
1058: 05 05 1C 04     .DB $05, $05, $1C, $04, $04, $11, $12, $13
105C: 04 11 12 13
1060: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T1064:
1064: 0B 1E 19 06     .DB $0B, $1E, $19, $06, $06, $06, $06, $06
1068: 06 06 06 06
106C: 06 1E 1F 1C     .DB $06, $1E, $1F, $1C, $1D, $06, $06, $06
1070: 1D 06 06 06
1074: 06 06 1E 03     .DB $06, $06, $1E, $03, $1F, $05, $1C, $04
1078: 1F 05 1C 04
107C: 1D 06 06 1A     .DB $1D, $06, $06, $1A, $04, $1B, $05, $18
1080: 04 1B 05 18
1084: 19 06 1A 04     .DB $19, $06, $1A, $04, $1B, $05, $05, $1C
1088: 1B 05 05 1C
108C: 04 1D 06 1E     .DB $04, $1D, $06, $1E, $03, $1F, $05, $05
1090: 03 1F 05 05
1094: 05 05 05 1C     .DB $05, $05, $05, $1C, $1D, $1E, $1F, $05
1098: 1D 1E 1F 05
109C: 05 05 05 05     .DB $05, $05, $05, $05, $05, $05, $18, $1F
10A0: 05 05 18 1F
10A4: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T10A8:
10A8: 10 04 04 1D     .DB $10, $04, $04, $1D, $0D, $0E, $0B, $0C
10AC: 0D 0E 0B 0C
10B0: 0D 0E 01 01     .DB $0D, $0E, $01, $01, $01, $01, $01, $01
10B4: 01 01 01 01
10B8: 01 01 05 05     .DB $01, $01, $05, $05, $05, $05, $05, $1C
10BC: 05 05 05 1C
10C0: 04 04 1D 06     .DB $04, $04, $1D, $06, $06, $1E, $03, $03
10C4: 06 1E 03 03
10C8: 1F 05 05 05     .DB $1F, $05, $05, $05, $1C, $11, $12, $13
10CC: 1C 11 12 13
10D0: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T10D4:
10D4: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E
10D8: 0B 0C 0D 0E
10DC: 0B 0C 1A 1B     .DB $0B, $0C, $1A, $1B, $05, $18, $19, $06
10E0: 05 18 19 06
10E4: 0D 0E 01 01     .DB $0D, $0E, $01, $01, $01, $01, $01, $01
10E8: 01 01 01 01
10EC: 01 01 05 05     .DB $01, $01, $05, $05, $1C, $1B, $05, $05
10F0: 1C 1B 05 05
10F4: 1C 04 1B 05     .DB $1C, $04, $1B, $05, $05, $1C, $04, $1B
10F8: 05 1C 04 1B
10FC: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T1100:
1100: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $09, $09
1104: 0B 0C 09 09
1108: 09 09 0A 0A     .DB $09, $09, $0A, $0A, $09, $09, $0A, $09
110C: 09 09 0A 09
1110: 16 17 14 07     .DB $16, $17, $14, $07, $07, $07, $1C, $04
1114: 07 07 1C 04
1118: 1D 06 1E 03     .DB $1D, $06, $1E, $03, $1F, $05, $1C, $08
111C: 1F 05 1C 08
1120: 08 08 08 08     .DB $08, $08, $08, $08, $08, $08, $08, $05
1124: 08 08 08 05
1128: 05 05 05 00     .DB $05, $05, $05, $00, $FF, $FF, $FF, $FF
112C: FF FF FF FF
T1130:
1130: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $0A, $0A
1134: 0B 0C 0A 0A
1138: 0A 0A 09 09     .DB $0A, $0A, $09, $09, $0A, $0A, $09, $0A
113C: 0A 0A 09 0A
1140: 12 13 10 08     .DB $12, $13, $10, $08, $08, $08, $18, $07
1144: 08 08 18 07
1148: 07 07 07 05     .DB $07, $07, $07, $05, $1C, $04, $1D, $06
114C: 1C 04 1D 06
1150: 1E 03 1F 07     .DB $1E, $03, $1F, $07, $07, $07, $07, $05
1154: 07 07 07 05
1158: 05 05 05 00     .DB $05, $05, $05, $00, $FF, $FF, $FF, $FF
115C: FF FF FF FF
T1160:
1160: 1C 04 04 04     .DB $1C, $04, $04, $04, $1D, $06, $0D, $0E
1164: 1D 06 0D 0E
1168: 0B 0C 06 06     .DB $0B, $0C, $06, $06, $1E, $15, $16, $17
116C: 1E 15 16 17
1170: 14 19 06 1A     .DB $14, $19, $06, $1A, $04, $1D, $06, $1E
1174: 04 1D 06 1E
1178: 03 19 06 1A     .DB $03, $19, $06, $1A, $04, $1D, $1E, $03
117C: 04 1D 1E 03
1180: 1F 1C 04 1B     .DB $1F, $1C, $04, $1B, $05, $18, $03, $1F
1184: 05 18 03 1F
1188: 05 1C 04 1B     .DB $05, $1C, $04, $1B, $05, $18, $03, $15
118C: 05 18 03 15
1190: 16 17 14 1F     .DB $16, $17, $14, $1F, $05, $05, $05, $05
1194: 05 05 05 05
1198: 05 05 05 1C     .DB $05, $05, $05, $1C, $04, $1D, $1A, $1B
119C: 04 1D 1A 1B
11A0: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T11A4:
11A4: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E
11A8: 0B 0C 0D 0E
11AC: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $02, $02, $02, $02
11B0: 02 02 02 02
11B4: 02 02 02 02     .DB $02, $02, $02, $02, $05, $05, $18, $03
11B8: 05 05 18 03
11BC: 19 1A 04 1B     .DB $19, $1A, $04, $1B, $05, $18, $03, $1F
11C0: 05 18 03 1F
11C4: 05 18 03 1F     .DB $05, $18, $03, $1F, $05, $05, $18, $1F
11C8: 05 05 18 1F
11CC: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T11D0:
11D0: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $06, $06
11D4: 0B 0C 06 06
11D8: 09 09 09 0A     .DB $09, $09, $09, $0A, $09, $09, $0A, $09
11DC: 09 09 0A 09
11E0: 09 09 06 1A     .DB $09, $09, $06, $1A, $04, $11, $12, $13
11E4: 04 11 12 13
11E8: 10 08 08 08     .DB $10, $08, $08, $08, $07, $07, $07, $08
11EC: 07 07 07 08
11F0: 08 08 05 05     .DB $08, $08, $05, $05, $05, $05, $05, $05
11F4: 05 05 05 05
11F8: 05 05 05 05     .DB $05, $05, $05, $05, $05, $00, $FF, $FF
11FC: 05 00 FF FF
T1200:
1200: 1C 11 12 13     .DB $1C, $11, $12, $13, $10, $04, $1D, $0D
1204: 10 04 1D 0D
1208: 0E 0B 0C 0D     .DB $0E, $0B, $0C, $0D, $0E, $0B, $0C, $1E
120C: 0E 0B 0C 1E
1210: 1F 05 18 19     .DB $1F, $05, $18, $19, $0D, $0E, $0B, $0C
1214: 0D 0E 0B 0C
1218: 1E 1F 05 05     .DB $1E, $1F, $05, $05, $05, $05, $05, $18
121C: 05 05 05 18
1220: 19 0D 0E 0B     .DB $19, $0D, $0E, $0B, $0C, $06, $1E, $1F
1224: 0C 06 1E 1F
1228: 05 05 05 05     .DB $05, $05, $05, $05, $18, $19, $06, $1E
122C: 18 19 06 1E
1230: 1F 05 05 05     .DB $1F, $05, $05, $05, $05, $05, $05, $05
1234: 05 05 05 05
1238: 05 1C 04 04     .DB $05, $1C, $04, $04, $1D, $1A, $04, $1B
123C: 1D 1A 04 1B
1240: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T1244:
1244: 18 03 03 19     .DB $18, $03, $03, $19, $06, $06, $06, $06
1248: 06 06 06 06
124C: 06 06 06 06     .DB $06, $06, $06, $06, $06, $06, $06, $06
1250: 06 06 06 06
1254: 1A 04 1B 05     .DB $1A, $04, $1B, $05, $1C, $04, $1D, $06
1258: 1C 04 1D 06
125C: 1E 03 03 19     .DB $1E, $03, $03, $19, $06, $1A, $04, $04
1260: 06 1A 04 04
1264: 04 1B 05 18     .DB $04, $1B, $05, $18, $03, $03, $1F, $05
1268: 03 03 1F 05
126C: 1C 04 1D 06     .DB $1C, $04, $1D, $06, $1A, $04, $1B, $05
1270: 1A 04 1B 05
1274: 05 05 05 05     .DB $05, $05, $05, $05, $05, $05, $05, $05
1278: 05 05 05 05
127C: 05 05 05 18     .DB $05, $05, $05, $18, $03, $19, $1E, $1F
1280: 03 19 1E 1F
1284: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T1288:
1288: 0B 0C 1A 1D     .DB $0B, $0C, $1A, $1D, $1E, $03, $19, $06
128C: 1E 03 19 06
1290: 1A 04 04 1D     .DB $1A, $04, $04, $1D, $06, $1E, $03, $03
1294: 06 1E 03 03
1298: 03 19 06 06     .DB $03, $19, $06, $06, $1A, $04, $04, $04
129C: 1A 04 04 04
12A0: 04 1D 06 06     .DB $04, $1D, $06, $06, $1E, $03, $03, $03
12A4: 1E 03 03 03
12A8: 03 03 03 1F     .DB $03, $03, $03, $1F, $05, $05, $1C, $04
12AC: 05 05 1C 04
12B0: 04 04 04 1B     .DB $04, $04, $04, $1B, $05, $05, $18, $03
12B4: 05 05 18 03
12B8: 03 03 1F 05     .DB $03, $03, $1F, $05, $1C, $04, $04, $1B
12BC: 1C 04 04 1B
12C0: 05 18 03 1F     .DB $05, $18, $03, $1F, $1C, $1B, $05, $05
12C4: 1C 1B 05 05
12C8: 00 FF           .DB $00, $FF,
T12CA:
12CA: 18 03 19 06     .DB $18, $03, $19, $06, $06, $06, $06, $06
12CE: 06 06 06 06
12D2: 06 1A 1D 1E     .DB $06, $1A, $1D, $1E, $19, $1A, $1D, $06
12D6: 19 1A 1D 06
12DA: 1E 19 06 1E     .DB $1E, $19, $06, $1E, $15, $16, $17, $14
12DE: 15 16 17 14
12E2: 07 07 07 08     .DB $07, $07, $07, $08, $08, $08, $08, $05
12E6: 08 08 08 05
12EA: 05 18 03 03     .DB $05, $18, $03, $03, $19, $06, $06, $1A
12EE: 19 06 06 1A
12F2: 04 04 1B 08     .DB $04, $04, $1B, $08, $08, $08, $08, $05
12F6: 08 08 08 05
12FA: 05 05 05 18     .DB $05, $05, $05, $18, $1F, $00
12FE: 1F 00
T1300:
1300: 0B 0C 0A 0A     .DB $0B, $0C, $0A, $0A, $09, $09, $09, $0A
1304: 09 09 09 0A
1308: 0A 09 09 09     .DB $0A, $09, $09, $09, $0A, $09, $09, $16
130C: 0A 09 09 16
1310: 17 14 07 07     .DB $17, $14, $07, $07, $07, $08, $08, $08
1314: 07 08 08 08
1318: 08 07 07 08     .DB $08, $07, $07, $08, $08, $08, $08, $07
131C: 08 08 08 07
1320: 08 11 12 13     .DB $08, $11, $12, $13, $00, $FF, $FF, $FF
1324: 00 FF FF FF
T1328:
1328: 0B 0C 09 09     .DB $0B, $0C, $09, $09, $0A, $09, $09, $0A
132C: 0A 09 09 0A
1330: 0A 0A 0A 09     .DB $0A, $0A, $0A, $09, $0A, $0A, $0A, $12
1334: 0A 0A 0A 12
1338: 13 10 04 04     .DB $13, $10, $04, $04, $04, $1B, $18, $03
133C: 04 1B 18 03
1340: 03 07 07 08     .DB $03, $07, $07, $08, $08, $07, $07, $08
1344: 08 07 07 08
1348: 08 07 07 07     .DB $08, $07, $07, $07, $07, $07, $00, $FF
134C: 07 07 00 FF
1350: FF FF FF FF     .DB $FF, $FF, $FF, $FF
T1354:
1354: 1C 11 12 13     .DB $1C, $11, $12, $13, $10, $1D, $0D, $0E
1358: 10 1D 0D 0E
135C: 0B 0C 09 0A     .DB $0B, $0C, $09, $0A, $09, $09, $0A, $09
1360: 09 09 0A 09
1364: 09 09 06 1A     .DB $09, $09, $06, $1A, $04, $1B, $05, $18
1368: 04 1B 05 18
136C: 03 19 09 09     .DB $03, $19, $09, $09, $0D, $0E, $0B, $0C
1370: 0D 0E 0B 0C
1374: 0D 0E 02 02     .DB $0D, $0E, $02, $02, $02, $02, $02, $02
1378: 02 02 02 02
137C: 02 02 02 02     .DB $02, $02, $02, $02, $02, $02, $08, $07
1380: 02 02 08 07
1384: 07 08 07 07     .DB $07, $08, $07, $07, $08, $08, $07, $07
1388: 08 08 07 07
138C: 07 07 07 05     .DB $07, $07, $07, $05, $05, $05, $05, $05
1390: 05 05 05 05
1394: 05 1C 11 12     .DB $05, $1C, $11, $12, $13, $00, $FF, $FF
1398: 13 00 FF FF
T139C:
139C: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E
13A0: 0B 0C 0D 0E
13A4: 0B 0C 1A 1D     .DB $0B, $0C, $1A, $1D, $06, $1E, $19, $06
13A8: 06 1E 19 06
13AC: 06 1A 04 1B     .DB $06, $1A, $04, $1B, $1C, $04, $1D, $1A
13B0: 1C 04 1D 1A
13B4: 04 1B 1C 04     .DB $04, $1B, $1C, $04, $1D, $1A, $04, $1B
13B8: 1D 1A 04 1B
13BC: 05 18 07 07     .DB $05, $18, $07, $07, $07, $08, $08, $07
13C0: 07 08 08 07
13C4: 07 07 07 08     .DB $07, $07, $07, $08, $08, $07, $07, $07
13C8: 08 07 07 07
13CC: 07 00 FF FF     .DB $07, $00, $FF, $FF
T13D0:
13D0: 14 03 19 0D     .DB $14, $03, $19, $0D, $0E, $0B, $0C, $0A
13D4: 0E 0B 0C 0A
13D8: 0A 0A 09 0A     .DB $0A, $0A, $09, $0A, $0A, $0A, $09, $0A
13DC: 0A 0A 09 0A
13E0: 0A 0A 06 1E     .DB $0A, $0A, $06, $1E, $15, $16, $17, $14
13E4: 15 16 17 14
13E8: 03 1F 05 05     .DB $03, $1F, $05, $05, $08, $07, $07, $07
13EC: 08 07 07 07
13F0: 08 07 07 07     .DB $08, $07, $07, $07, $08, $08, $05, $05
13F4: 08 08 05 05
13F8: 05 05 05 00     .DB $05, $05, $05, $00, $FF, $FF, $FF, $FF
13FC: FF FF FF FF
T1400:
1400: 30 40 31 41     .DB $30, $40, $31, $41 ; frame#1
1404: 32 42 33 43     .DB $32, $42, $33, $43 ; frame#2
1408: 34 44 35 45     .DB $34, $44, $35, $45 ; frame#3
140C: 36 46 37 47     .DB $36, $46, $37, $47 ; frame#4
1410: 38 48 39 49     .DB $38, $48, $39, $49 ; frame#5
1414: 3A 4A 3B 4B     .DB $3A, $4A, $3B, $4B ; frame#6
1418: 3C 4C 3D 4D     .DB $3C, $4C, $3D, $4D ; frame#7
141C: 3E 4E 3F 4F     .DB $3E, $4E, $3F, $4F ; frame#8
T1420:
1420: 60 61           .DB $60, $61 ; alien shape #1
1422: 62 63           .DB $62, $63 ; #2
1424: 64 65           .DB $64, $65 ; #3
1426: 66 67           .DB $66, $67 ; #4
1428: 69 00           .DB $69, $00 ; #6
142A: 69 00           .DB $69, $00 ; #6
142C: 7A 7B           .DB $7A, $7B ; #28
142E: 7A 7B           .DB $7A, $7B ; #28
1430: 6B 00           .DB $6B, $00 ; #8
1432: 6B 00           .DB $6B, $00 ; #8
1434: 8C 8D           .DB $8C, $8D ; #29
1436: 8C 8D           .DB $8C, $8D ; #29
1438: 68 00           .DB $68, $00 ; #5
143A: 68 00           .DB $68, $00 ; #5
143C: 8A 9A           .DB $8A, $9A ; #30
143E: 8A 9A           .DB $8A, $9A ; #30
1440: 6A 00           .DB $6A, $00 ; #7
1442: 6A 00           .DB $6A, $00 ; #7
1444: 8B 9B           .DB $8B, $9B ; #31
1446: 8B 9B           .DB $8B, $9B ; #31
1448: 68 00           .DB $68, $00 ; #5
144A: 6B 00           .DB $6B, $00 ; #8
144C: 6A 00           .DB $6A, $00 ; #7
144E: 69 00           .DB $69, $00 ; #6
1450: 76 77           .DB $76, $77 ; #18
1452: 74 75           .DB $74, $75 ; #19
1454: 72 73           .DB $72, $73 ; #16
1456: 70 71           .DB $70, $71 ; #17
1458: 68 00           .DB $68, $00 ; #5
145A: 86 96           .DB $86, $96 ; #22
145C: 69 00           .DB $69, $00 ; #6
145E: 87 97           .DB $87, $97 ; #21
1460: 6A 00           .DB $6A, $00 ; #7
1462: 88 98           .DB $88, $98 ; #20
1464: 6B 00           .DB $6B, $00 ; #8
1466: 89 99           .DB $89, $99 ; #23
1468: 68 00           .DB $68, $00 ; #5
146A: 00 00           .DB $00, $00
146C: A2 B2 A3 B3     .DB $A2, $B2, $A3, $B3 ; #26
1470: 69 00           .DB $69, $00 ; #6
1472: 00 00           .DB $00, $00
1474: A4 B4 A5 B5     .DB $A4, $B4, $A5, $B5 ; #25
1478: 6A 00           .DB $6A, $00 ; #7
147A: 00 00           .DB $00, $00
147C: A6 B6 A7 B7     .DB $A6, $B6, $A7, $B7 ; #24
1480: 6B 00           .DB $6B, $00 ; #8
1482: 00 00           .DB $00, $00
1484: A8 B8 A9 B9     .DB $A8, $B8, $A9, $B9 ; #27
1488: FF FF FF FF     .DB $FF, $FF, $FF, $FF
148C: 8A 9A           .DB $8A, $9A ; #30
148E: 00 00           .DB $00, $00
1490: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
1494: FF FF FF FF
1498: FF FF FF FF
149C: FF FF FF FF
14A0: 8B 9B           .DB $8B, $9B ; #31
14A2: 00 00           .DB $00, $00
14A4: FF FF FF FF     .DB $FF, $FF, $FF, $FF
14A8: 8E 9E 8F 9F     .DB $8E, $9E, $8F, $9F ; #14
14AC: A0 B0 A1 B1     .DB $A0, $B0, $A1, $B1 ; #15
14B0: 00 00 00 00     .DB $00, $00, $00, $00
14B4: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
14B8: FF FF FF FF
14BC: FF FF FF FF
14C0: 9C 00           .DB $9C, $00 ; #32
14C2: 00 00           .DB $00, $00
14C4: 84 94 85 95     .DB $84, $94, $85, $95 ; #36
14C8: 82 92 83 93     .DB $82, $92, $83, $93 ; #35
14CC: 80 90 81 91     .DB $80, $90, $81, $91 ; #34
14D0: 9D 00 00 00     .DB $9D, $00, $00, $00 ; #33
14D4: AE BE AF BF     .DB $AE, $BE, $AF, $BF ; #39
14D8: AC BC AD 00     .DB $AC, $BC, $AD, $00 ; #38
14DC: AA BA AB BB     .DB $AA, $BA, $AB, $BB ; #37
L14E0:
14E0: 47              LD      B,A ; save A
14E1: 3A 00 78        LD      A,(DSW0) ; {hard.DSW0} 78xx DSW0
14E4: E6 10           AND     $10 ; 0001_0000 Coinage
14E6: C8              RET     Z ; return if no coins entered
14E7: EB              EX      DE,HL
14E8: 7A              LD      A,D
14E9: FE 18           CP      $18
14EB: C0              RET     NZ
14EC: 7B              LD      A,E
14ED: FE 95           CP      $95
14EF: 36 22           LD      (HL),$22
14F1: C8              RET     Z
14F2: FE 9A           CP      $9A
14F4: 36 13           LD      (HL),$13
14F6: C8              RET     Z
14F7: FE B5           CP      $B5
14F9: 36 24           LD      (HL),$24
14FB: C8              RET     Z
14FC: 70              LD      (HL),B
14FD: C9              RET
14FE: FF              .DB $FF
14FF: FF              .DB $FF
T1500:
1500: 08 6C 09 60     .DB $08, $6C, $09, $60
1504: 08 6C 09 60     .DB $08, $6C, $09, $60
1508: 08 6C 09 60     .DB $08, $6C, $09, $60
150C: 08 6C 09 60     .DB $08, $6C, $09, $60
1510: 08 6C 09 60     .DB $08, $6C, $09, $60
1514: 08 6C 09 60     .DB $08, $6C, $09, $60
1518: 08 6C 09 60     .DB $08, $6C, $09, $60
151C: 09 60 09 60     .DB $09, $60, $09, $60
T1520:
1520: 10 00           .DW T1000
1522: 10 00           .DW T1000
1524: 10 00           .DW T1000
1526: 10 00           .DW T1000
1528: 10 00           .DW T1000
152A: 10 00           .DW T1000
152C: 10 00           .DW T1000
152E: 10 00           .DW T1000
1530: 10 00           .DW T1000
1532: 10 00           .DW T1000
1534: 10 00           .DW T1000
1536: 10 00           .DW T1000
1538: 10 00           .DW T1000
153A: 10 00           .DW T1000
153C: 10 00           .DW T1000
153E: 10 00           .DW T1000
T1540:
1540: 50 20           .DB $50, $20 ; 0 : x,y = 50,20 (decimal 80,32)
1542: 70 20           .DB $70, $20 ; 1
1544: 60 28           .DB $60, $28 ; 2
1546: 60 38           .DB $60, $38 ; 3
1548: 50 40           .DB $50, $40 ; 4
154A: 70 40           .DB $70, $40 ; 5
154C: 40 38           .DB $40, $38 ; 6
154E: 80 38           .DB $80, $38 ; 7
1550: 30 30           .DB $30, $30 ; 8
1552: 90 30           .DB $90, $30 ; 9
1554: 20 38           .DB $20, $38 ; A
1556: A0 38           .DB $A0, $38 ; B
1558: 18 48           .DB $18, $48 ; C
155A: A8 48           .DB $A8, $48 ; D
155C: 60 48           .DB $60, $48 ; E
155E: 60 58           .DB $60, $58 ; F
T1560:
1560: 60 48           .DB $60, $48 ; 0
1562: 60 58           .DB $60, $58 ; 1
1564: 48 58           .DB $48, $58 ; 2
1566: 78 58           .DB $78, $58 ; 3
1568: 38 50           .DB $38, $50 ; 4
156A: 88 50           .DB $88, $50 ; 5
156C: 28 48           .DB $28, $48 ; 6
156E: 98 48           .DB $98, $48 ; 7
1570: 18 40           .DB $18, $40 ; 8
1572: A8 40           .DB $A8, $40 ; 9
1574: 18 30           .DB $18, $30 ; A
1576: A8 30           .DB $A8, $30 ; B
1578: 28 28           .DB $28, $28 ; C
157A: 98 28           .DB $98, $28 ; D
157C: 38 20           .DB $38, $20 ; E
157E: 88 20           .DB $88, $20 ; F
T1580:
1580: 60 20           .DB $60, $20 ; 0
1582: 50 20           .DB $50, $20 ; 1
1584: 70 20           .DB $70, $20 ; 2
1586: 40 28           .DB $40, $28 ; 3
1588: 80 28           .DB $80, $28 ; 4
158A: 30 30           .DB $30, $30 ; 5
158C: 90 30           .DB $90, $30 ; 6
158E: 20 38           .DB $20, $38 ; 7
1590: A0 38           .DB $A0, $38 ; 8
1592: 60 58           .DB $60, $58 ; 9
1594: 50 58           .DB $50, $58 ; A
1596: 70 58           .DB $70, $58 ; B
1598: 40 58           .DB $40, $58 ; C
159A: 80 58           .DB $80, $58 ; D
159C: 30 58           .DB $30, $58 ; E
159E: 90 58           .DB $90, $58 ; F
T15A0:
15A0: 60 20           .DB $60, $20 ; 0
15A2: 50 28           .DB $50, $28 ; 1
15A4: 70 28           .DB $70, $28 ; 2
15A6: 40 30           .DB $40, $30 ; 3
15A8: 80 30           .DB $80, $30 ; 4
15AA: 30 38           .DB $30, $38 ; 5
15AC: 90 38           .DB $90, $38 ; 6
15AE: 20 40           .DB $20, $40 ; 7
15B0: A0 40           .DB $A0, $40 ; 8
15B2: 60 58           .DB $60, $58 ; 9
15B4: 50 58           .DB $50, $58 ; A
15B6: 70 58           .DB $70, $58 ; B
15B8: 40 50           .DB $40, $50 ; C
15BA: 80 50           .DB $80, $50 ; D
15BC: 30 48           .DB $30, $48 ; E
15BE: 90 48           .DB $90, $48 ; F
T15C0:
15C0: 60 58           .DB $60, $58 ; 0
15C2: 50 50           .DB $50, $50 ; 1
15C4: 70 50           .DB $70, $50 ; 2
15C6: 60 48           .DB $60, $48 ; 3
15C8: 40 48           .DB $40, $48 ; 4
15CA: 80 48           .DB $80, $48 ; 5
15CC: 50 40           .DB $50, $40 ; 6
15CE: 70 40           .DB $70, $40 ; 7
15D0: 40 38           .DB $40, $38 ; 8
15D2: 80 38           .DB $80, $38 ; 9
15D4: 30 30           .DB $30, $30 ; A
15D6: 90 30           .DB $90, $30 ; B
15D8: 20 28           .DB $20, $28 ; C
15DA: A0 28           .DB $A0, $28 ; D
15DC: 10 20           .DB $10, $20 ; E
15DE: B0 20           .DB $B0, $20 ; F
T15E0:
15E0: 60 20           .DB $60, $20 ; 0
15E2: 50 28           .DB $50, $28 ; 1
15E4: 70 28           .DB $70, $28 ; 2
15E6: 40 30           .DB $40, $30 ; 3
15E8: 80 30           .DB $80, $30 ; 4
15EA: 30 38           .DB $30, $38 ; 5
15EC: 90 38           .DB $90, $38 ; 6
15EE: 20 40           .DB $20, $40 ; 7
15F0: A0 40           .DB $A0, $40 ; 8
15F2: 60 20           .DB $60, $20 ; 9 (two aliens at same position)
15F4: 50 28           .DB $50, $28 ; A (two aliens at same position)
15F6: 70 28           .DB $70, $28 ; B (two aliens at same position)
15F8: 40 30           .DB $40, $30 ; C (two aliens at same position)
15FA: 80 30           .DB $80, $30 ; D (two aliens at same position)
15FC: 30 38           .DB $30, $38 ; E (two aliens at same position)
15FE: 90 38           .DB $90, $38 ; F (two aliens at same position)
T1600:
1600: 10 14 18 1C     .DB $10, $14, $18, $1C ; to player ship frame #5, #6, #7, #8
1604: 00 04 08 0C     .DB $00, $04, $08, $0C ; to player ship frame #1, #2, #3, #4
1608: 20 22 24 26     .DB $20, $22, $24, $26 ; to alien shape #1, #2, #3, #4
160C: 28 2A 2C 2E     .DB $28, $2A, $2C, $2E ; to alien shape #6, #6, #28, #28
1610: 30 32 34 36     .DB $30, $32, $34, $36 ; to alien shape #8, #8, #29, #29
1614: 38 3A 3C 3E     .DB $38, $3A, $3C, $3E ; to alien shape #5, #5, #30, #30
1618: 40 42 44 46     .DB $40, $42, $44, $46 ; to alien shape #7, #7, #31, #31
161C: 5C 5C 5E 5E     .DB $5C, $5C, $5E, $5E ; to alien shape #6, #6, #21, #21
T1620:
1620: 50 51 52 53     .DB $50, $51, $52, $53, $54, $55, $56, $57
1624: 54 55 56 57
1628: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
162C: FF FF FF FF
1630: 48 48 50 50     .DB $48, $48, $50, $50, $4A, $4A, $52, $52, $4C, $4C, $54, $54, $4E, $4E, $56, $56 ; to alien shape #5, #5, #18, #18
1634: 4A 4A 52 52      ; to alien shape #8, #8, #19, #19
1638: 4C 4C 54 54      ; to alien shape #7, #7, #16, #16
163C: 4E 4E 56 56      ; to alien shape #6, #6, #17, #17
1640: 48 48 56 56     .DB $48, $48, $56, $56, $4E, $4E, $54, $54, $4C, $4C, $52, $52, $4A, $4A, $50, $50 ; to alien shape #5, #5, #17, #17
1644: 4E 4E 54 54      ; to alien shape #6, #6, #16, #16
1648: 4C 4C 52 52      ; to alien shape #7, #7, #19, #19
164C: 4A 4A 50 50      ; to alien shape #8, #8, #18, #18
1650: 68 68 6C 6C     .DB $68, $68, $6C, $6C, $70, $70, $74, $74, $78, $78, $7C, $7C, $80, $80, $84, $84 ; to alien shape #5, #5, #26, #26
1654: 70 70 74 74      ; to alien shape #6, #6, #25, #25
1658: 78 78 7C 7C      ; to alien shape #7, #7, #24, #24
165C: 80 80 84 84      ; to alien shape #8, #8, #27, #27
1660: 68 68 84 84     .DB $68, $68, $84, $84, $80, $80, $7C, $7C, $78, $78, $74, $74, $70, $70, $6C, $6C ; to alien shape #5, #5, #27, #27
1664: 80 80 7C 7C      ; to alien shape #8, #8, #24, #24
1668: 78 78 74 74      ; to alien shape #7, #7, #25, #25
166C: 70 70 6C 6C      ; to alien shape #6, #6, #26, #26
1670: 58 58 5A 5A     .DB $58, $58, $5A, $5A, $5C, $5C, $5E, $5E, $60, $60, $62, $62, $64, $64, $66, $66 ; to alien shape #5, #5, #22, #22
1674: 5C 5C 5E 5E      ; to alien shape #6, #6, #21, #21
1678: 60 60 62 62      ; to alien shape #7, #7, #20, #20
167C: 64 64 66 66      ; to alien shape #8, #8, #23, #23
1680: 78              .DB $78 ; to alien shape #7, #31, #14, #15
1681: FF              .DB $FF
1682: A0              .DB $A0
1683: FF FF           .DB $FF, $FF
1685: A8              .DB $A8
1686: FF              .DB $FF
1687: AC C0           .DB $AC, $C0
1689: FF              .DB $FF
168A: C8              .DB $C8
168B: FF FF           .DB $FF, $FF
168D: C4              .DB $C4
168E: FF              .DB $FF
168F: CC D0           .DB $CC, $D0
1691: FF              .DB $FF
1692: D8              .DB $D8
1693: FF FF           .DB $FF, $FF
1695: D4              .DB $D4
1696: FF              .DB $FF
1697: DC              .DB $DC
1698: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
169C: FF FF FF FF
T16A0:
16A0: FF FF FF         ; Dummy
16A3: 01 02 08        .DB $01, $02, $08 ; 2x1 screen object, X , T1608
16A6: 01 02 08        .DB $01, $02, $08 ; 2x1 screen object, X , T1608
16A9: 01 02 0C        .DB $01, $02, $0C ; 2x1 screen object, X , T160C
16AC: 01 02 10        .DB $01, $02, $10 ; 2x1 screen object, X , T1610
16AF: 03 04 14        .DB $03, $04, $14 ; 1x2 screen object,  Y, T1614
16B2: 03 04 18        .DB $03, $04, $18 ; 1x2 screen object,  Y, T1618
16B5: 04 01 88        .DB $04, $01, $88 ; 2x2 screen object, XY, T1688
16B8: 04 01 90        .DB $04, $01, $90 ; 2x2 screen object, XY, T1690
16BB: 04 01 80        .DB $04, $01, $80 ; 2x2 screen object, XY, T1680
16BE: 04 01 80        .DB $04, $01, $80 ; 2x2 screen object, XY, T1680
16C1: 03 04 70        .DB $03, $04, $70 ; 1x2 screen object,  Y, T1670
16C4: 03 04 74        .DB $03, $04, $74 ; 1x2 screen object,  Y, T1674
16C7: 03 04 78        .DB $03, $04, $78 ; 1x2 screen object,  Y, T1678
16CA: 03 04 7C        .DB $03, $04, $7C ; 1x2 screen object,  Y, T167C
16CD: FF FF FF        .DB $FF, $FF, $FF ; Dummy
16D0: 01 02 30        .DB $01, $02, $30 ; 2x1 screen object, X , T1630
16D3: 01 02 34        .DB $01, $02, $34 ; 2x1 screen object, X , T1634
16D6: 01 02 38        .DB $01, $02, $38 ; 2x1 screen object, X , T1638
16D9: 01 02 3C        .DB $01, $02, $3C ; 2x1 screen object, X , T163C
16DC: 01 02 40        .DB $01, $02, $40 ; 2x1 screen object, X , T1640
16DF: 01 02 44        .DB $01, $02, $44 ; 2x1 screen object, X , T1644
16E2: 01 02 48        .DB $01, $02, $48 ; 2x1 screen object, X , T1648
16E5: 01 02 4C        .DB $01, $02, $4C ; 2x1 screen object, X , T164C
16E8: 04 04 50        .DB $04, $04, $50 ; 2x2 screen object,  Y, T1650
16EB: 04 04 54        .DB $04, $04, $54 ; 2x2 screen object,  Y, T1654
16EE: 04 04 58        .DB $04, $04, $58 ; 2x2 screen object,  Y, T1658
16F1: 04 04 5C        .DB $04, $04, $5C ; 2x2 screen object,  Y, T165C
16F4: 04 04 60        .DB $04, $04, $60 ; 2x2 screen object,  Y, T1660
16F7: 04 04 64        .DB $04, $04, $64 ; 2x2 screen object,  Y, T1664
16FA: 04 04 68        .DB $04, $04, $68 ; 2x2 screen object,  Y, T1668
16FD: 04 04 6C        .DB $04, $04, $6C ; 2x2 screen object,  Y, T166C
T1700:
1700: FF FF 01 00     .DB $FF, $FF, $01, $00, $FF, $00, $04, $00, $FC, $00, $00, $FC, $00, $04, $04, $FE ; Dummy
1704: FF 00 04 00      ; X-1 (left), Y+0
1708: FC 00 00 FC      ; X-4, Y+0
170C: 00 04 04 FE      ; X+0, Y+4 (down)
1710: FC FE 04 02     .DB $FC, $FE, $04, $02, $FC, $02, $00, $04, $00, $04, $00, $04, $00, $04, $FF, $FF ; X-4, Y-2
1714: FC 02 00 04      ; X-4, Y+2
1718: 00 04 00 04      ; X+0, Y+4
171C: 00 04 FF FF      ; X+0, Y+4
1720: FC 00 FC 00     .DB $FC, $00, $FC, $00, $FC, $00, $FC, $00, $04, $00, $04, $00, $04, $00, $04, $00 ; X-4, Y+0
1724: FC 00 FC 00      ; X-4, Y+0
1728: 04 00 04 00      ; X+4, Y+0
172C: 04 00 04 00      ; X+4, Y+0
1730: 04 FC 04 04     .DB $04, $FC, $04, $04, $FC, $04, $FC, $FC, $FC, $FC, $FC, $04, $04, $04, $04, $FC ; X+4, Y-4
1734: FC 04 FC FC      ; X-4, Y+4
1738: FC FC FC 04      ; X-4, Y-4
173C: 04 04 04 FC      ; X+4, Y+4
T1740:
1740: 08 00 00 FF     .DB $08, $00, $00, $FF, $01, $00, $F8, $FF, $08, $01, $02, $FF, $04, $00, $FA, $FF
1744: 01 00 F8 FF
1748: 08 01 02 FF
174C: 04 00 FA FF
1750: 08 01 04 FF     .DB $08, $01, $04, $FF, $08, $00, $FC, $FF, $08, $05, $06, $FF, $08, $00, $FE, $FF
1754: 08 00 FC FF
1758: 08 05 06 FF
175C: 08 00 FE FF
T1760:
1760: 10 10 88 88     .DB $10, $10, $88, $88, $10, $10, $10, $10
1764: 10 10 10 10
1768: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
176C: FF FF FF FF
T1770:
1770: EC FC FD F4     .DB $EC, $FC, $FD, $F4, $ED, $30, $40, $F5, $EE, $31, $41, $F6, $EF, $FF, $FE, $F7 ; [Object 1770](fgtiles.md#object-1770) Regular ship, large shields
1774: ED 30 40 F5
1778: EE 31 41 F6
177C: EF FF FE F7
1780: E8 F8 F9 F0     .DB $E8, $F8, $F9, $F0, $E9, $30, $40, $F1, $EA, $31, $41, $F2, $EB, $FB, $FA, $F3 ; [Object 1780](fgtiles.md#object-1780) Regular ship, small shields
1784: E9 30 40 F1
1788: EA 31 41 F2
178C: EB FB FA F3
1790: E8 F8 F9 F0     .DB $E8, $F8, $F9, $F0, $E9, $E4, $E6, $F1, $EA, $E5, $E7, $F2, $EB, $FB, $FA, $F3 ; [Object 1790](fgtiles.md#object-1790) Green ship, large shields
1794: E9 E4 E6 F1
1798: EA E5 E7 F2
179C: EB FB FA F3
17A0: 00 00 00 00     .DB $00, $00, $00, $00, $00, $E4, $E6, $00, $00, $E5, $E7, $00, $00, $00, $00, $00 ; [Object 17A0](fgtiles.md#object-17a0) Green ship, no shields
17A4: 00 E4 E6 00
17A8: 00 E5 E7 00
17AC: 00 00 00 00
17B0: F0 CA C4 BE     .DB $F0, $CA, $C4, $BE, $B8, $BE, $B8, $BE ; LSB's of the Alien explosion frame sequence (#5,#4,#3,#2,#1,#2,#1,#2) why wrong order?
17B4: B8 BE B8 BE
17B8: C8 D8 C9 D9     .DB $C8, $D8, $C9, $D9, $CA, $DA ; [Object 17B8](fgtiles.md#object-17b8) 3x2 Alien explosion frame #1
17BC: CA DA
17BE: CB DB CC DC     .DB $CB, $DB, $CC, $DC, $CD, $DD ; [Object 17BE](fgtiles.md#object-17be) 3x2 Alien explosion frame #2
17C2: CD DD
17C4: C0 C1 C1 C2     .DB $C0, $C1, $C1, $C2, $00, $C0 ; [Object 17C4](fgtiles.md#object-17c4) 3x2 Alien explosion frame #3
17C8: 00 C0
17CA: 00 00 00 C3     .DB $00, $00, $00, $C3, $00, $00 ; [Object 17CA](fgtiles.md#object-17ca) 3x2 Alien explosion frame #4
17CE: 00 00
T17D0:
17D0: C4 D4 C5 D5     .DB $C4, $D4, $C5, $D5, $C3, $C3 ; [Object 17D0](fgtiles.md#object-17d0) 3x2 Bonus explosion left part
17D4: C3 C3
T17D6:
17D6: C3 C3 C6 D6     .DB $C3, $C3, $C6, $D6, $C7, $D7 ; [Object 17D6](fgtiles.md#object-17d6) 3x2 Bonus explosion right part
17DA: C7 D7
17DC: FF              .DB $FF
17DD: FF              .DB $FF
17DE: FF              .DB $FF
17DF: FF              .DB $FF
CoinChecking:
17E0: 3A 00 78        LD      A,(DSW0) ; {hard.DSW0} 78xx DSW0
17E3: E6 10           AND     $10 ; 0001_0000 Coinage
17E5: 3A 8F 43        LD      A,(CoinCount) ; {ram.CoinCount}
17E8: C8              RET     Z
17E9: 0F              RRCA
17EA: E6 0F           AND     $0F ; 0000_1111
17EC: C9              RET
17ED: FF              .DB $FF
17EE: FF              .DB $FF
17EF: FF              .DB $FF
FourByFourEmpty:
17F0: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
17F4: 00 00 00 00
17F8: 00 00 00 00
17FC: 00 00 00 00
T1800:
1800: 43 20           .DB $43, $20
1802: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1806: 00 13 03 0F     .DB $00, $13, $03, $0F, $12, $05, $21, $00, $00, $08, $09, $2B, $13, $03, $0F, $12, $05, $00, $00, $13, $03, $0F, $12, $05, $22, $00
180A: 12 05 21 00
180E: 00 08 09 2B
1812: 13 03 0F 12
1816: 05 00 00 13
181A: 03 0F 12 05
181E: 22 00
1820: 43 21           .DB $43, $21
1822: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1826: 00 20 20 20     .DB $00, $20, $20, $20, $20, $20, $20, $00, $00, $00, $20, $20, $20, $20, $20, $20, $00, $00, $00, $20, $20, $20, $20, $20, $20, $00
182A: 20 20 20 00
182E: 00 00 20 20
1832: 20 20 20 20
1836: 00 00 00 20
183A: 20 20 20 20
183E: 20 00
1840: 43 22           .DB $43, $22
1842: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1846: 00 00 00 7F     .DB $00, $00, $00, $7F, $20, $00, $00, $00, $00, $00, $03, $0F, $09, $0E, $20, $20, $00, $00, $00, $00, $00, $7F, $20, $00, $00, $00
184A: 20 00 00 00
184E: 00 00 03 0F
1852: 09 0E 20 20
1856: 00 00 00 00
185A: 00 7F 20 00
185E: 00 00
T1860:
1860: 43 25           .DB $43, $25
1862: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1866: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $09, $0E, $13, $05, $12, $14, $00, $00, $03, $0F, $09, $0E, $00, $00, $00, $00, $00, $00, $00
186A: 00 00 00 09
186E: 0E 13 05 12
1872: 14 00 00 03
1876: 0F 09 0E 00
187A: 00 00 00 00
187E: 00 00
1880: 43 27           .DB $43, $27
1882: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1886: 00 00 00 1F     .DB $00, $00, $00, $1F, $00, $21, $10, $0C, $01, $19, $05, $12, $00, $00, $00, $21, $03, $0F, $09, $0E, $00, $00, $1F, $00, $00, $00
188A: 00 21 10 0C
188E: 01 19 05 12
1892: 00 00 00 21
1896: 03 0F 09 0E
189A: 00 00 1F 00
189E: 00 00
18A0: 43 29           .DB $43, $29
18A2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
18A6: 00 00 00 1F     .DB $00, $00, $00, $1F, $00, $22, $10, $0C, $01, $19, $05, $12, $13, $00, $00, $22, $03, $0F, $09, $0E, $13, $00, $1F, $00, $00, $00
18AA: 00 22 10 0C
18AE: 01 19 05 12
18B2: 13 00 00 22
18B6: 03 0F 09 0E
18BA: 13 00 1F 00
18BE: 00 00
18C0: 43 2E           .DB $43, $2E
18C2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
18C6: 00 00 00 13     .DB $00, $00, $00, $13, $03, $0F, $12, $05, $00, $01, $16, $05, $12, $01, $07, $05, $00, $14, $01, $02, $0C, $05, $00, $00, $00, $00
18CA: 03 0F 12 05
18CE: 00 01 16 05
18D2: 12 01 07 05
18D6: 00 14 01 02
18DA: 0C 05 00 00
18DE: 00 00
18E0: 43 30           .DB $43, $30
18E2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
18E6: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $22, $20, $00, $24, $20, $00, $28, $20, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
18EA: 00 00 00 00
18EE: 22 20 00 24
18F2: 20 00 28 20
18F6: 00 00 00 00
18FA: 00 00 00 00
18FE: 00 00
1900: 43 33           .DB $43, $33
1902: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1906: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $22, $20, $20, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
190A: 00 00 00 00
190E: 22 20 20 00
1912: 00 00 00 00
1916: 00 00 00 00
191A: 00 00 00 00
191E: 00 00
1920: 43 36           .DB $43, $36
1922: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1926: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $25, $20, $00, $21, $20, $20, $00, $2F, $1B, $21, $20, $20, $2B, $28, $20, $20, $1C, $00
192A: 00 00 00 00
192E: 25 20 00 21
1932: 20 20 00 2F
1936: 1B 21 20 20
193A: 2B 28 20 20
193E: 1C 00
1940: 43 39           .DB $43, $39
1942: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1946: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $21, $20, $20, $20, $2B, $29, $20, $20, $20, $00, $00, $00, $00, $00, $00, $00, $00, $00
194A: 00 00 00 00
194E: 21 20 20 20
1952: 2B 29 20 20
1956: 20 00 00 00
195A: 00 00 00 00
195E: 00 00
T1960:
1960: 43 3C           .DB $43, $3C
1962: 00 00 32 21     .DB $00, $00, $32, $21
1966: 10 08 0F 05     .DB $10, $08, $0F, $05, $0E, $09, $18, $7E, $00, $03, $0F, $10, $19, $12, $09, $07, $08, $14, $00, $21, $29, $28, $20, $00, $00, $00
196A: 0E 09 18 7E
196E: 00 03 0F 10
1972: 19 12 09 07
1976: 08 14 00 21
197A: 29 28 20 00
197E: 00 00
1980: 43 3D           .DB $43, $3D
1982: 02 05 21 28     .DB $02, $05, $21, $28
1986: 00 01 0D 13     .DB $00, $01, $0D, $13, $14, $01
198A: 14 01
L198C:
198C: 12 00 05 0C     .DB $12, $00, $05, $0C, $05, $03, $14, $12, $0F, $0E, $09, $03, $13, $00, $03, $0F, $12, $10, $2A, $00
1990: 05 03 14 12
1994: 0F 0E 09 03
1998: 13 00 03 0F
199C: 12 10 2A 00
19A0: 43 3E           .DB $43, $3E
19A2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
19A6: 00 00 10 08     .DB $00, $00, $10, $08, $0F, $05, $0E, $09, $18, $00, $01, $1A, $2A, $00, $15, $2A, $13, $2A, $01, $2A, $00, $00, $00, $00, $00, $00
19AA: 0F 05 0E 09
19AE: 18 00 01 1A
19B2: 2A 00 15 2A
19B6: 13 2A 01 2A
19BA: 00 00 00 00
19BE: 00 00
T19C0:
19C0: 43 28           .DB $43, $28
19C2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
19C6: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $10, $15, $13, $08, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
19CA: 00 00 00 00
19CE: 00 00 00 10
19D2: 15 13 08 00
19D6: 00 00 00 00
19DA: 00 00 00 00
19DE: 00 00
19E0: 43 2C           .DB $43, $2C
19E2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
19E6: 00 00 00 00     .DB $00, $00, $00, $00, $0F, $0E, $0C, $19, $00, $21, $10, $0C, $01, $19, $05, $12, $00, $02, $15, $14, $14, $0F, $0E, $00, $00, $00
19EA: 0F 0E 0C 19
19EE: 00 21 10 0C
19F2: 01 19 05 12
19F6: 00 02 15 14
19FA: 14 0F 0E 00
19FE: 00 00
T1A00:
1A00: 43 28           .DB $43, $28
1A02: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1A06: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $07, $01, $0D, $05, $00, $00, $0F, $16, $05, $12, $00, $00, $00, $00, $00, $00, $00, $00
1A0A: 00 00 00 00
1A0E: 07 01 0D 05
1A12: 00 00 0F 16
1A16: 05 12 00 00
1A1A: 00 00 00 00
1A1E: 00 00
1A20: 43 28           .DB $43, $28
1A22: 00 FF FF FF     .DB $00, $FF, $FF, $FF
1A26: 64 65 64 65     .DB $64, $65, $64, $65, $64, $65, $60, $61, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $78, $79
1A2A: 64 65 60 61
1A2E: 00 00 00 00
1A32: 00 00 00 00
1A36: 00 00 00 00
1A3A: 00 00 00 00
1A3E: 78 79
1A40: 43 29           .DB $43, $29
1A42: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1A46: 64 65 00 00     .DB $64, $65, $00, $00, $00, $00, $64, $65, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $7C, $7D
1A4A: 00 00 64 65
1A4E: 00 00 00 00
1A52: 00 00 00 00
1A56: 00 00 00 00
1A5A: 00 00 00 00
1A5E: 7C 7D
1A60: 43 2A           .DB $43, $2A
1A62: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1A66: 64 65 64 65     .DB $64, $65, $64, $65, $64, $65, $60, $61, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
1A6A: 64 65 60 61
1A6E: 00 00 00 00
1A72: 00 00 00 00
1A76: 00 00 00 00
1A7A: 00 00 00 00
1A7E: 00 00
1A80: 43 2B           .DB $43, $2B
1A82: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1A86: 64 65 00 00     .DB $64, $65, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
1A8A: 00 00 00 00
1A8E: 00 00 00 00
1A92: 00 00 00 00
1A96: 00 00 00 00
1A9A: 00 00 00 00
1A9E: 00 00
1AA0: 43 2C           .DB $43, $2C
1AA2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1AA6: 64 65 00 68     .DB $64, $65, $00, $68, $00, $68, $00, $68, $68, $68, $00, $68, $64, $65, $00, $62, $63, $00, $68, $00, $68, $00, $68, $00, $00, $68
1AAA: 00 68 00 68
1AAE: 68 68 00 68
1AB2: 64 65 00 62
1AB6: 63 00 68 00
1ABA: 68 00 68 00
1ABE: 00 68
1AC0: 43 2D           .DB $43, $2D
1AC2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1AC6: 64 65 00 68     .DB $64, $65, $00, $68, $00, $68, $00, $68, $00, $68, $00, $68, $00, $00, $00, $68, $9D, $00, $68, $00, $68, $00, $76, $77, $70, $71
1ACA: 00 68 00 68
1ACE: 00 68 00 68
1AD2: 00 00 00 68
1AD6: 9D 00 68 00
1ADA: 68 00 76 77
1ADE: 70 71
1AE0: 43 2E           .DB $43, $2E
1AE2: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1AE6: 64 65 00 68     .DB $64, $65, $00, $68, $68, $68, $00, $68, $00, $68, $00, $68, $62, $63, $00, $68, $76, $77, $68, $00, $68, $00, $00, $64, $65, $00
1AEA: 68 68 00 68
1AEE: 00 68 00 68
1AF2: 62 63 00 68
1AF6: 76 77 68 00
1AFA: 68 00 00 64
1AFE: 65 00
1B00: 43 2F           .DB $43, $2F
1B02: 00 00 00 00     .DB $00, $00, $00, $00
1B06: 64 65 00 68     .DB $64, $65, $00, $68, $00, $68, $00, $68, $00, $68, $00, $68, $00, $00, $00, $68, $00, $9D, $68, $00, $68, $00, $74, $75, $72, $73
1B0A: 00 68 00 68
1B0E: 00 68 00 68
1B12: 00 00 00 68
1B16: 00 9D 68 00
1B1A: 68 00 74 75
1B1E: 72 73
1B20: 43 30           .DB $43, $30
1B22: FF FF FF FF     .DB $FF, $FF, $FF, $FF
1B26: 64 65 00 68     .DB $64, $65, $00, $68, $00, $68, $00, $68, $68, $68, $00, $68, $64, $65, $00, $68, $00, $66, $67, $00, $68, $00, $68, $00, $00, $68
1B2A: 00 68 00 68
1B2E: 68 68 00 68
1B32: 64 65 00 68
1B36: 00 66 67 00
1B3A: 68 00 68 00
1B3E: 00 68
T1B40:
1B40: 6C              .DB $6C ; #9
1B41: 6D              .DB $6D ; #10
1B42: 6E              .DB $6E ; #11
1B43: 6F              .DB $6F ; #12
1B44: FF              .DB $FF
1B45: FF              .DB $FF
1B46: FF              .DB $FF
1B47: FF              .DB $FF
T1B48:
1B48: 6C 6D 6E 6F     .DB $6C, $6D, $6E, $6F, $64, $65, $66, $67, $63, $FF
1B4C: 64 65 66 67
1B50: 63 FF
1B52: 63 61 67 FF     .DB $63, $61, $67, $FF
1B56: 67 65 6B FF     .DB $67, $65, $6B, $FF
1B5A: 6B 69 6F FF     .DB $6B, $69, $6F, $FF
1B5E: 6F 6D           .DB $6F, $6D
T1B60:
1B60: 80 83 83 85     .DB $80, $83, $83, $85, $81, $8C, $8C, $86, $81, $8C, $8C, $86, $82, $84, $84, $87
1B64: 81 8C 8C 86
1B68: 81 8C 8C 86
1B6C: 82 84 84 87
1B70: 00 89 89 00     .DB $00, $89, $89, $00, $88, $8D, $8D, $8B, $88, $8D, $8D, $8B, $00, $8A, $8A, $00
1B74: 88 8D 8D 8B
1B78: 88 8D 8D 8B
1B7C: 00 8A 8A 00
1B80: 00 00 00 00     .DB $00, $00, $00, $00, $00, $80, $85, $00, $00, $82, $87, $00, $00, $00, $00, $00
1B84: 00 80 85 00
1B88: 00 82 87 00
1B8C: 00 00 00 00
T1B90:
1B90: 1B 80           .DB $1B, $80
1B92: 1B 70           .DB $1B, $70
1B94: 1B 60           .DB $1B, $60
1B96: 1B 70           .DB $1B, $70
1B98: 17 F0           .DB $17, $F0 ; for deletion
1B9A: 17 F0           .DB $17, $F0
1B9C: 17 F0           .DB $17, $F0
1B9E: 17 F0           .DB $17, $F0
T1BA0:
1BA0: 43 2C           .DB $43, $2C ; screen ram position
1BA2: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $21, $00, $0F, $12, $00, $22, $10
1BA6: 00 00 00 21
1BAA: 00 0F 12 00
1BAE: 22 10
1BB0: 0C 01 19 05     .DB $0C, $01, $19, $05, $12, $13, $00, $02, $15, $14, $14, $0F, $0E, $00, $00, $00
1BB4: 12 13 00 02
1BB8: 15 14 14 0F
1BBC: 0E 00 00 00
T1BC0:
1BC0: 41 54 76 7E     .DB $41, $54, $76, $7E ; frame 0
1BC4: 42 55 77 7F     .DB $42, $55, $77, $7F
1BC8: 41 56 74 7C     .DB $41, $56, $74, $7C ; frame 1
1BCC: 42 57 75 7D     .DB $42, $57, $75, $7D
1BD0: 44 51 72 7A     .DB $44, $51, $72, $7A ; frame 2
1BD4: 45 52 73 7B     .DB $45, $52, $73, $7B
1BD8: 46 51 70 78     .DB $46, $51, $70, $78 ; frame 3
1BDC: 47 52 71 79     .DB $47, $52, $71, $79
1BE0: 41 51 70 78     .DB $41, $51, $70, $78 ; frame 4
1BE4: 42 52 71 79     .DB $42, $52, $71, $79
1BE8: 41 51 72 7A     .DB $41, $51, $72, $7A ; frame 5
1BEC: 42 52 73 7B     .DB $42, $52, $73, $7B
1BF0: 41 51 74 7C     .DB $41, $51, $74, $7C ; frame 6
1BF4: 42 52 75 7D     .DB $42, $52, $75, $7D
1BF8: 41 51 76 7E     .DB $41, $51, $76, $7E ; frame 7
1BFC: 42 52 77 7F     .DB $42, $52, $77, $7F
T1C00:
1C00: 00 01 00 06     .DB $00, $01, $00, $06, $00, $02, $03, $04, $00, $01, $00, $08, $00, $02, $03, $04, $00, $00, $07, $00
1C04: 00 02 03 04
1C08: 00 01 00 08
1C0C: 00 02 03 04
1C10: 00 00 07 00
1C14: 01 02 00 09     .DB $01, $02, $00, $09, $00, $03, $04, $00, $00, $03, $04, $00, $00, $01, $00, $02, $00, $03, $0A, $00
1C18: 00 03 04 00
1C1C: 00 03 04 00
1C20: 00 01 00 02
1C24: 00 03 0A 00
1C28: 04 00 00 01     .DB $04, $00, $00, $01, $02, $00, $06, $00, $03, $04, $00, $00, $01, $00, $02, $00, $03, $00, $04, $00
1C2C: 02 00 06 00
1C30: 03 04 00 00
1C34: 01 00 02 00
1C38: 03 00 04 00
1C3C: 03 05 00 00     .DB $03, $05, $00, $00, $00, $00, $07, $00, $01, $00, $02, $00, $00, $05, $00, $00, $03, $00, $04, $01
1C40: 00 00 07 00
1C44: 01 00 02 00
1C48: 00 05 00 00
1C4C: 03 00 04 01
1C50: 02 00 03 00     .DB $02, $00, $03, $00, $08, $04, $00, $01, $02, $06, $00, $03, $00, $04, $00, $02, $01, $02, $03, $00
1C54: 08 04 00 01
1C58: 02 06 00 03
1C5C: 00 04 00 02
1C60: 01 02 03 00
1C64: 05 00 00 04     .DB $05, $00, $00, $04, $00, $01, $02, $00, $00, $03, $04, $0B, $00, $01, $00, $02, $00, $03, $00, $00
1C68: 00 01 02 00
1C6C: 00 03 04 0B
1C70: 00 01 00 02
1C74: 00 03 00 00
1C78: 04 00 00 09     .DB $04, $00, $00, $09, $00, $00, $02, $00, $07, $00, $00, $01, $00, $00, $02, $00, $00, $03, $00, $08
1C7C: 00 00 02 00
1C80: 07 00 00 01
1C84: 00 00 02 00
1C88: 00 03 00 08
1C8C: 04 00 01 00     .DB $04, $00, $01, $00, $00, $06, $00, $01, $00, $02, $00, $01, $03, $04, $01, $03, $01, $02, $03, $04
1C90: 00 06 00 01
1C94: 00 02 00 01
1C98: 03 04 01 03
1C9C: 01 02 03 04
1CA0: 00 05 00 01     .DB $00, $05, $00, $01, $02, $00, $09, $00, $03, $04, $00, $01, $00, $01, $02, $03, $04, $00, $02, $00
1CA4: 02 00 09 00
1CA8: 03 04 00 01
1CAC: 00 01 02 03
1CB0: 04 00 02 00
1CB4: 00 01 02 00     .DB $00, $01, $02, $00, $03, $04, $00, $06, $00, $00, $01, $00
1CB8: 03 04 00 06
1CBC: 00 00 01 00
1CC0: 00 01 02 00     .DB $00, $01, $02, $00, $05, $00, $00, $03, $00, $04, $00, $07, $00, $01, $00, $02
1CC4: 05 00 00 03
1CC8: 00 04 00 07
1CCC: 00 01 00 02
1CD0: 00 00 03 00     .DB $00, $00, $03, $00, $04, $00, $04, $00, $0A, $00, $01, $00, $02, $00, $03, $00
1CD4: 04 00 04 00
1CD8: 0A 00 01 00
1CDC: 02 00 03 00
1CE0: 01 00 07 00     .DB $01, $00, $07, $00, $02, $00, $03, $04, $00, $05, $00, $01, $00, $02, $00, $00
1CE4: 02 00 03 04
1CE8: 00 05 00 01
1CEC: 00 02 00 00
1CF0: 08 03 04 00     .DB $08, $03, $04, $00, $01, $00, $02, $00, $03, $00, $04, $00, $00, $06, $00, $03
1CF4: 01 00 02 00
1CF8: 03 00 04 00
1CFC: 00 06 00 03
T1D00:
1D00: 0C 0D 0C 0F     .DB $0C, $0D, $0C, $0F, $07, $07, $01, $00, $00, $4C, $4D, $4E, $4F, $4F, $4E, $4D, $4C, $00, $00, $1F, $0E, $06, $0D, $01, $0E, $05
1D04: 07 07 01 00
1D08: 00 4C 4D 4E
1D0C: 4F 4F 4E 4D
1D10: 4C 00 00 1F
1D14: 0E 06 0D 01
1D18: 0E 05
1D1A: 08 0C 0E 0C     .DB $08, $0C, $0E, $0C, $0A, $00, $00, $4D, $4F, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $4F, $4D, $00, $00, $06, $0B, $0D, $08, $0E
1D1E: 0A 00 00 4D
1D22: 4F 5E 5E 5E
1D26: 5E 5E 5E 5E
1D2A: 5E 4F 4D 00
1D2E: 00 06 0B 0D
1D32: 08 0E
1D34: 03 02 00 01     .DB $03, $02, $00, $01, $00, $4C, $4F, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $4F, $4C, $00, $09, $07, $0A, $03
1D38: 00 4C 4F 5E
1D3C: 5E 5E 5E 5E
1D40: 5E 5E 5E 5E
1D44: 5E 5E 5E 4F
1D48: 4C 00 09 07
1D4C: 0A 03
1D4E: 04 00 0A 00     .DB $04, $00, $0A, $00, $4D, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $5E, $4D, $00, $00, $0E, $0F
1D52: 4D 5E 5E 5E
1D56: 5E 5E 5E 5E
1D5A: 5E 5E 5E 5E
1D5E: 5E 5E 5E 5E
1D62: 5E 4D 00 00
1D66: 0E 0F
1D68: 08 08 00 5C     .DB $08, $08, $00, $5C, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $60, $6A, $5D, $00, $01, $02
1D6C: 60 6A 60 6A
1D70: 60 6A 60 6A
1D74: 60 6A 60 6A
1D78: 60 6A 60 6A
1D7C: 60 6A 5D 00
1D80: 01 02
1D82: 02 06 01 00     .DB $02, $06, $01, $00, $00, $00, $58, $59, $5A, $5B, $5B, $5B, $7E, $7F, $5B, $5B, $5B, $4A, $49, $48, $00, $00, $00, $03, $0E, $0B
1D86: 00 00 58 59
1D8A: 5A 5B 5B 5B
1D8E: 7E 7F 5B 5B
1D92: 5B 4A 49 48
1D96: 00 00 00 03
1D9A: 0E 0B
1D9C: 0D 05 04 05     .DB $0D, $05, $04, $05, $0A, $08, $00, $00, $58, $59, $5A, $4B, $76, $77, $4B, $4A, $49, $48, $00, $00, $01, $03, $0F, $02, $03, $00
1DA0: 0A 08 00 00
1DA4: 58 59 5A 4B
1DA8: 76 77 4B 4A
1DAC: 49 48 00 00
1DB0: 01 03 0F 02
1DB4: 03 00
1DB6: 00 03 03 07     .DB $00, $03, $03, $07, $02, $0A, $03, $07, $00, $00, $58, $50, $51, $52, $53, $48, $00, $00, $0B, $01, $02, $03, $0F, $0E, $0C, $02
1DBA: 02 0A 03 07
1DBE: 00 00 58 50
1DC2: 51 52 53 48
1DC6: 00 00 0B 01
1DCA: 02 03 0F 0E
1DCE: 0C 02
1DD0: 05 0C 06 00     .DB $05, $0C, $06, $00, $04, $06, $07, $0E, $0F, $09, $00, $40, $41, $42, $43, $00, $07, $03, $0A, $08, $0D, $00, $09, $0B, $0C, $0A
1DD4: 04 06 07 0E
1DD8: 0F 09 00 40
1DDC: 41 42 43 00
1DE0: 07 03 0A 08
1DE4: 0D 00 09 0B
1DE8: 0C 0A
1DEA: FF              .DB $FF
1DEB: FF              .DB $FF
1DEC: FF              .DB $FF
1DED: FF              .DB $FF
1DEE: FF              .DB $FF
1DEF: FF              .DB $FF
L1DF0:
1DF0: 3A 1D 43        LD      A,(ForegroundScreen+$31D) ; {ram.ForegroundScreen+31D} 'A' from 'AMSTAR ..' copyright text
1DF3: D6 01           SUB     $01
1DF5: C8              RET     Z
1DF6: 32 8F 43        LD      (CoinCount),A ; {ram.CoinCount}
1DF9: 00              NOP
1DFA: 00              NOP
1DFB: 00              NOP
1DFC: 00              NOP
1DFD: 00              NOP
1DFE: 00              NOP
1DFF: 00              NOP
T1E00:
1E00: 20 30 21 31     .DB $20, $30, $21, $31
1E04: 22 32 23 33     .DB $22, $32, $23, $33
1E08: 24 34 25 35     .DB $24, $34, $25, $35
1E0C: 26 36 27 37     .DB $26, $36, $27, $37
1E10: 28 38 29 39     .DB $28, $38, $29, $39
1E14: 2A 3A 2B 3B     .DB $2A, $3A, $2B, $3B
1E18: 2C 3C 2D 3D     .DB $2C, $3C, $2D, $3D
1E1C: 2E 3E 2F 3F     .DB $2E, $3E, $2F, $3F
T1E20:
1E20: 49 48 4A 4B     .DB $49, $48, $4A, $4B
1E24: 4A 49 4A 49     .DB $4A, $49, $4A, $49
1E28: 48 4A 48 49     .DB $48, $4A, $48, $49
1E2C: 4B 48 4A 48     .DB $4B, $48, $4A, $48
1E30: 4A 49 4B 49     .DB $4A, $49, $4B, $49
1E34: 4B 4A 49 48     .DB $4B, $4A, $49, $48
1E38: 49 49 4A 4A     .DB $49, $49, $4A, $4A
1E3C: 48 49 4A 48     .DB $48, $49, $4A, $48
T1E40:
1E40: A0 60 40 00     .DB $A0, $60, $40, $00
1E44: E0 C0 C0 60     .DB $E0, $C0, $C0, $60
1E48: 80 20 60 40     .DB $80, $20, $60, $40
1E4C: 20 40 00 80     .DB $20, $40, $00, $80
1E50: 40 00 20 E0     .DB $40, $00, $20, $E0
1E54: 00 60 00 A0     .DB $00, $60, $00, $A0
1E58: E0 20 80 00     .DB $E0, $20, $80, $00
1E5C: C0 80 A0 E0     .DB $C0, $80, $A0, $E0
T1E60:
1E60: 00 04 08 0C     .DB $00, $04, $08, $0C
1E64: 10 14 18 1C     .DB $10, $14, $18, $1C
1E68: 00 08 10 18     .DB $00, $08, $10, $18
1E6C: 04 0C 14 1C     .DB $04, $0C, $14, $1C
1E70: 00 0C 18 04     .DB $00, $0C, $18, $04
1E74: 04 1C 08 14     .DB $04, $1C, $08, $14
1E78: 00 10 04 14     .DB $00, $10, $04, $14
1E7C: 08 18 0C 1C     .DB $08, $18, $0C, $1C
T1E80:
1E80: 10 11 12 13     .DB $10, $11, $12, $13
1E84: 14 15 16 17     .DB $14, $15, $16, $17
1E88: 18 19 1A 1B     .DB $18, $19, $1A, $1B
1E8C: 1C 1D 1E 1F     .DB $1C, $1D, $1E, $1F
1E90: 10 12 14 16     .DB $10, $12, $14, $16
1E94: 18 1A 1C 1E     .DB $18, $1A, $1C, $1E
1E98: 11 13 15 17     .DB $11, $13, $15, $17
1E9C: 19 1B 1D 1F     .DB $19, $1B, $1D, $1F
T1EA0:
1EA0: 4A 4B 49 4A     .DB $4A, $4B, $49, $4A
1EA4: 48 4A 48 49     .DB $48, $4A, $48, $49
1EA8: 49 4A 49 4B     .DB $49, $4A, $49, $4B
1EAC: 48 4B 4A 4A     .DB $48, $4B, $4A, $4A
1EB0: 48 49 48 4A     .DB $48, $49, $48, $4A
1EB4: 48 48 49 4A     .DB $48, $48, $49, $4A
1EB8: 49 49 4A 48     .DB $49, $49, $4A, $48
1EBC: 4A 49 4B 48     .DB $4A, $49, $4B, $48
T1EC0:
1EC0: 00 20 60 40     .DB $00, $20, $60, $40
1EC4: E0 80 20 60     .DB $E0, $80, $20, $60
1EC8: 40 A0 00 00     .DB $40, $A0, $00, $00
1ECC: 40 20 C0 20     .DB $40, $20, $C0, $20
1ED0: A0 80 E0 40     .DB $A0, $80, $E0, $40
1ED4: 60 C0 20 A0     .DB $60, $C0, $20, $A0
1ED8: E0 40 60 C0     .DB $E0, $40, $60, $C0
1EDC: 20 40 20 80     .DB $20, $40, $20, $80
L1EE0:
1EE0: 11 3D 43        LD      DE,ForegroundScreen+$33D ; {+ram.ForegroundScreen+33D} holding 0
1EE3: 01 1A 00        LD      BC,$001A
L1EE6:
1EE6: 1A              LD      A,(DE)
1EE7: 80              ADD     A,B
1EE8: 47              LD      B,A
1EE9: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
1EEC: 0D              DEC     C
1EED: C2 E6 1E        JP      NZ,L1EE6 ; {code.L1EE6}
1EF0: 1A              LD      A,(DE)
1EF1: 80              ADD     A,B
1EF2: C6 27           ADD     $27
1EF4: 21 89 43        LD      HL,HiScorehigh ; {+ram.HiScorehigh}
1EF7: 86              ADD     A,(HL)
1EF8: 77              LD      (HL),A
1EF9: 00              NOP
1EFA: C9              RET
1EFB: FF              .DB $FF
1EFC: FF              .DB $FF
1EFD: FF              .DB $FF
1EFE: FF              .DB $FF
1EFF: FF              .DB $FF
T1F00:
1F00: 00 00 00 01     .DB $00, $00, $00, $01, $00, $00, $00, $02, $00, $00, $00, $00, $03, $00, $00, $00
1F04: 00 00 00 02
1F08: 00 00 00 00
1F0C: 03 00 00 00
1F10: 00 04 00 00     .DB $00, $04, $00, $00, $00, $00, $01, $00, $00, $00, $05, $00, $02, $00, $03, $00
1F14: 00 00 01 00
1F18: 00 00 05 00
1F1C: 02 00 03 00
1F20: 00 00 04 00     .DB $00, $00, $04, $00, $07, $00, $00, $00, $06, $00, $01, $00, $02, $0C, $00, $03
1F24: 07 00 00 00
1F28: 06 00 01 00
1F2C: 02 0C 00 03
1F30: 04 00 00 01     .DB $04, $00, $00, $01, $00, $08, $00, $00, $02, $00, $0C, $03, $04, $0E, $00, $00
1F34: 00 08 00 00
1F38: 02 00 0C 03
1F3C: 04 0E 00 00
1F40: 00 01 02 00     .DB $00, $01, $02, $00, $0D, $03, $04, $0F, $01, $0C, $07, $0A, $02, $0D, $03, $08
1F44: 0D 03 04 0F
1F48: 01 0C 07 0A
1F4C: 02 0D 03 08
1F50: 06 0C 04 09     .DB $06, $0C, $04, $09, $05, $0F, $01, $02, $0D, $03, $0C, $04, $0D, $05, $0F, $0C
1F54: 05 0F 01 02
1F58: 0D 03 0C 04
1F5C: 0D 05 0F 0C
1F60: 01 02 0E 0C     .DB $01, $02, $0E, $0C, $03, $0F, $0D, $05, $0E, $0D, $0C, $0F, $0D, $04, $0C, $01
1F64: 03 0F 0D 05
1F68: 0E 0D 0C 0F
1F6C: 0D 04 0C 01
1F70: 0E 05 0F 0D     .DB $0E, $05, $0F, $0D, $07, $0C, $06, $0E, $0D, $0F, $09, $0C, $0F, $0D, $0E, $0D
1F74: 07 0C 06 0E
1F78: 0D 0F 09 0C
1F7C: 0F 0D 0E 0D
1F80: 02 0D 0C 0F     .DB $02, $0D, $0C, $0F, $05, $0E, $0D, $0C, $0F, $06, $0E, $0F, $0C, $0D, $0F, $0C
1F84: 05 0E 0D 0C
1F88: 0F 06 0E 0F
1F8C: 0C 0D 0F 0C
1F90: 06 0D 04 0B     .DB $06, $0D, $04, $0B, $0C, $0F, $05, $0D, $05, $03, $0E, $07, $0C, $0D, $04, $05
1F94: 0C 0F 05 0D
1F98: 05 03 0E 07
1F9C: 0C 0D 04 05
1FA0: 01 02 0E 03     .DB $01, $02, $0E, $03, $0C, $04, $0F, $05, $08, $0C, $07, $01, $0D, $04, $0E, $02
1FA4: 0C 04 0F 05
1FA8: 08 0C 07 01
1FAC: 0D 04 0E 02
1FB0: 0C 01 0F 03     .DB $0C, $01, $0F, $03, $05, $0D, $00, $0E, $00, $09, $0C, $06, $0D, $00, $01, $02
1FB4: 05 0D 00 0E
1FB8: 00 09 0C 06
1FBC: 0D 00 01 02
1FC0: 01 02 03 00     .DB $01, $02, $03, $00, $00, $0D, $00, $0A, $00, $00, $00, $0E, $00, $05, $00, $08
1FC4: 00 0D 00 0A
1FC8: 00 00 00 0E
1FCC: 00 05 00 08
1FD0: 00 0C 00 00     .DB $00, $0C, $00, $00, $03, $00, $00, $07, $00, $00, $00, $04, $00, $00, $06, $00
1FD4: 03 00 00 07
1FD8: 00 00 00 04
1FDC: 00 00 06 00
1FE0: 00 00 00 01     .DB $00, $00, $00, $01, $00, $00, $00, $00, $02, $00, $00, $00, $00, $03, $00, $00
1FE4: 00 00 00 00
1FE8: 02 00 00 00
1FEC: 00 03 00 00
1FF0: 00 04 00 05     .DB $00, $04, $00, $05, $00, $00, $00, $00, $00, $01, $00, $00, $00, $00, $02, $00
1FF4: 00 00 00 00
1FF8: 00 01 00 00
1FFC: 00 00 02 00
L2000:
2000: CD 76 08        CALL    PlayerUpdate ; {code.PlayerUpdate} Updates the player ship, player bullet and the shield.
2003: CD F0 0D        CALL    L0DF0 ; {code.L0DF0} alien bullet to player, collission detection ?
2006: CD A0 24        CALL    L24A0 ; {code.L24A0}
2009: 21 5F 43        LD      HL,M435F ; {+ram.M435F} 8 bit counter for alien movement
200C: 7E              LD      A,(HL) ; get value
200D: E6 03           AND     $03 ; mask out 0000_0011 for count 0 to 3
200F: 47              LD      B,A ; save the masked counter
2010: 34              INC     (HL) ; increment alien movement counter
2011: 3A BA 43        LD      A,(AliensLeft) ; {ram.AliensLeft}
2014: A7              AND     A ; updates the zero flag
2015: CA BA 21        JP      Z,L21BA ; {code.L21BA} if no AliensLeft
2018: FE 05           CP      $05
201A: D2 30 21        JP      NC,L2130 ; {code.L2130} if >= 5 left
201D: 2D              DEC     L ; {ram.M435E} $435E
201E: 78              LD      A,B ; get masked counter
201F: A7              AND     A ; updates the zero flag
2020: C2 25 20        JP      NZ,L2025 ; {code.L2025} if masked counter <> 0
2023: 36 FF           LD      (HL),$FF ; {ram.M435E} set all bits at $435E
L2025:
2025: 7E              LD      A,(HL) ; {ram.M435E} get $435E
2026: A7              AND     A ; updates the zero flag
2027: CA 30 21        JP      Z,L2130 ; {code.L2130} if $435E = 0
202A: C3 46 21        JP      L2146 ; {code.L2146}
202D: FF              .DB $FF
202E: FF              .DB $FF
202F: FF              .DB $FF
L2030:
2030: E6 03           AND     $03 ; 0000_0011
2032: FE 01           CP      $01
2034: 11 50 1B        LD      DE,$1B50
2037: C3 AC 23        JP      L23AC ; {code.L23AC}
203A: FF              .DB $FF
203B: FF              .DB $FF
203C: FF              .DB $FF
203D: FF              .DB $FF
203E: FF              .DB $FF
203F: FF              .DB $FF
AddGalaxiesToBackground:
2040: 21 AF 43        LD      HL,M43AF ; {+ram.M43AF}
2043: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
2046: 4F              LD      C,A
2047: BE              CP      (HL)
2048: C0              RET     NZ
2049: 7E              LD      A,(HL)
204A: 2C              INC     L
204B: 96              SUB     (HL)
204C: 2D              DEC     L
204D: 77              LD      (HL),A
204E: 2C              INC     L
204F: 2C              INC     L
2050: 34              INC     (HL)
2051: 7E              LD      A,(HL)
2052: 21 80 1E        LD      HL,T1E80 ; {+code.T1E80} data for the 16 (1x1) small galaxies from setB
2055: E6 1F           AND     $1F ; 0001_1111
2057: 85              ADD     A,L
2058: 6F              LD      L,A
2059: 46              LD      B,(HL)
205A: C6 20           ADD     $20
205C: 6F              LD      L,A
205D: 56              LD      D,(HL)
205E: C6 20           ADD     $20
2060: 6F              LD      L,A
2061: 5E              LD      E,(HL)
2062: 79              LD      A,C
2063: 0F              RRCA
2064: 0F              RRCA
2065: 0F              RRCA
2066: E6 1F           AND     $1F ; 0001_1111
2068: 83              ADD     A,E
2069: 3C              INC     A
206A: 5F              LD      E,A
206B: 78              LD      A,B
206C: 12              LD      (DE),A
206D: C9              RET
206E: C9              .DB $C9
206F: FF              .DB $FF
L2070:
2070: 7B              LD      A,E
2071: D6 0A           SUB     $0A
2073: C6 C0           ADD     $C0
2075: 4F              LD      C,A
2076: 7A              LD      A,D
2077: CE 00           ADC     $00
2079: 47              LD      B,A
207A: 7E              LD      A,(HL)
207B: 11 00 28        LD      DE,T2800 ; {+code.T2800} get the foreground tiles of the player ship particles explosion
207E: 21 00 29        LD      HL,T2900 ; {+code.T2900} and get the control data for it
2081: C3 85 20        JP      L2085 ; {code.L2085}
2084: FF              .DB $FF
L2085:
2085: D6 20           SUB     $20
2087: 07              RLCA ; Multiply by 4 ..
2088: 07              RLCA ; ..
2089: 00              NOP
208A: E6 E0           AND     $E0 ; 1110_0000
208C: 6F              LD      L,A
208D: 3E E0           LD      A,$E0
208F: 95              SUB     L
2090: 6F              LD      L,A
L2091:
2091: 3E 3F           LD      A,$3F
2093: 91              SUB     C
2094: 3E 43           LD      A,$43
2096: 98              SBC     B
2097: D2 B0 20        JP      NC,L20B0 ; {code.L20B0}
209A: 23              INC     HL
209B: 23              INC     HL
209C: 7B              LD      A,E
209D: C6 10           ADD     $10
209F: 5F              LD      E,A
20A0: 79              LD      A,C
20A1: D6 20           SUB     $20
20A3: 4F              LD      C,A
20A4: 78              LD      A,B
20A5: DE 00           SBC     $00
20A7: 47              LD      B,A
20A8: C3 91 20        JP      L2091 ; {code.L2091}
20AB: FF              .DB $FF
20AC: FF              .DB $FF
20AD: FF              .DB $FF
20AE: FF              .DB $FF
20AF: FF              .DB $FF
L20B0:
20B0: C5              PUSH    BC
L20B1:
20B1: 7E              LD      A,(HL)
20B2: E3              EX      (SP),HL
20B3: 06 08           LD      B,$08
L20B5:
20B5: 36 00           LD      (HL),$00
20B7: 0F              RRCA
20B8: D2 BF 20        JP      NC,L20BF ; {code.L20BF}
20BB: EB              EX      DE,HL
20BC: 4E              LD      C,(HL)
20BD: EB              EX      DE,HL ; get data from $2800
20BE: 71              LD      (HL),C
L20BF:
20BF: 23              INC     HL
20C0: 13              INC     DE
20C1: 05              DEC     B
20C2: C2 B5 20        JP      NZ,L20B5 ; {code.L20B5}
20C5: E3              EX      (SP),HL
20C6: 23              INC     HL
20C7: 7D              LD      A,L
20C8: 0F              RRCA
20C9: DA B1 20        JP      C,L20B1 ; {code.L20B1}
20CC: 7D              LD      A,L
20CD: E6 1F           AND     $1F ; 0001_1111
20CF: CA E1 20        JP      Z,L20E1 ; {code.L20E1}
20D2: E3              EX      (SP),HL
20D3: 7D              LD      A,L
20D4: D6 30           SUB     $30
20D6: 6F              LD      L,A
20D7: 7C              LD      A,H
20D8: DE 00           SBC     $00
20DA: 67              LD      H,A
20DB: E3              EX      (SP),HL
20DC: FE 3F           CP      $3F
20DE: C2 B1 20        JP      NZ,L20B1 ; {code.L20B1}
L20E1:
20E1: C1              POP     BC
20E2: C9              RET
20E3: 20              .DB $20
20E4: FF              .DB $FF
20E5: FF              .DB $FF
20E6: FF              .DB $FF
20E7: FF              .DB $FF
L20E8:
20E8: 47              LD      B,A
20E9: 7A              LD      A,D
20EA: C6 08           ADD     $08
20EC: 57              LD      D,A
20ED: CD 1C 21        CALL    L211C ; {code.L211C}
20F0: 0F              RRCA
20F1: 0F              RRCA
20F2: 0F              RRCA
20F3: 83              ADD     A,E
20F4: E6 1F           AND     $1F ; 0001_1111
20F6: 4F              LD      C,A
20F7: 7B              LD      A,E
20F8: E6 E0           AND     $E0 ; 1110_0000
20FA: B1              OR      C
20FB: 5F              LD      E,A
20FC: 78              LD      A,B
20FD: 0F              RRCA
20FE: 0F              RRCA
20FF: E6 0E           AND     $0E ; 0000_1110
2101: C6 90           ADD     $90
2103: 6F              LD      L,A
2104: 26 1B           LD      H,$1B
2106: 7E              LD      A,(HL)
2107: 2C              INC     L
2108: 6E              LD      L,(HL)
2109: 67              LD      H,A
210A: 01 04 04        LD      BC,$0404 ; images are 4x4
210D: C3 D6 0A        JP      DrawImageCbyB ; {code.DrawImageCbyB}
2110: FF              .DB $FF
2111: FF              .DB $FF
2112: FF              .DB $FF
2113: FF              .DB $FF
2114: FF              .DB $FF
2115: FF              .DB $FF
2116: FF              .DB $FF
2117: FF              .DB $FF
2118: FF              .DB $FF
2119: FF              .DB $FF
211A: FF              .DB $FF
211B: FF              .DB $FF
L211C:
211C: 21 B9 43        LD      HL,CounterB9 ; {+ram.CounterB9}
211F: 7E              LD      A,(HL)
2120: FE 10           CP      $10
2122: D8              RET     C
2123: FE 30           CP      $30
2125: D0              RET     NC
2126: 3E 10           LD      A,$10
2128: 77              LD      (HL),A
2129: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
212C: C9              RET
212D: FF              .DB $FF
212E: FF              .DB $FF
212F: FF              .DB $FF
L2130:
2130: 78              LD      A,B ; get masked counter
2131: A7              AND     A ; updates the zero flag
2132: CA 50 21        JP      Z,L2150 ; {code.L2150} if = 0
2135: FE 01           CP      $01
2137: CA 60 21        JP      Z,L2160 ; {code.L2160} if = 1
213A: FE 02           CP      $02
213C: CA 70 21        JP      Z,L2170 ; {code.L2170} if = 2
213F: C3 80 21        JP      L2180 ; {code.L2180} counter = 3
2142: 90              .DB $90
2143: A5              .DB $A5
2144: 50              .DB $50
2145: 60              .DB $60
L2146:
2146: 78              LD      A,B
2147: 0F              RRCA
2148: D2 90 21        JP      NC,L2190 ; {code.L2190}
214B: C3 A5 21        JP      L21A5 ; {code.L21A5}
214E: F0              .DB $F0
214F: F9              .DB $F9
L2150:
2150: CD 50 0A        CALL    AlienDataController ; {code.AlienDataController} draw or delete alien
2153: CD 00 30        CALL    L3000 ; {code.L3000}
2156: C3 00 0F        JP      L0F00 ; {code.L0F00} 'alien with player' collision check
2159: FF              .DB $FF
215A: FF              .DB $FF
215B: FF              .DB $FF
215C: FF              .DB $FF
215D: FF              .DB $FF
215E: FF              .DB $FF
215F: FF              .DB $FF
L2160:
2160: CD C4 24        CALL    L24C4 ; {code.L24C4}
2163: CD 40 0C        CALL    L0C40 ; {code.EnemyBulletUpdate}
2166: CD 1C 0D        CALL    L0D1C ; {code.AlienMovementUpdate}
2169: C3 C0 0F        JP      L0FC0 ; {code.L0FC0} Handle animations for killed aliens
216C: FF              .DB $FF
216D: FF              .DB $FF
216E: FF              .DB $FF
216F: FF              .DB $FF
L2170:
2170: CD 70 0D        CALL    L0D70 ; {code.AlienAnimationUpdate}
2173: C3 60 25        JP      L2560 ; {code.L2560}
2176: FF              .DB $FF
2177: FF              .DB $FF
2178: FF              .DB $FF
2179: FF              .DB $FF
217A: FF              .DB $FF
217B: FF              .DB $FF
217C: FF              .DB $FF
217D: FF              .DB $FF
217E: FF              .DB $FF
217F: FF              .DB $FF
L2180:
2180: CD C4 24        CALL    L24C4 ; {code.L24C4}
2183: CD 40 0C        CALL    L0C40 ; {code.EnemyBulletUpdate}
2186: CD 6C 0A        CALL    L0A6C ; {code.L0A6C} get screen ram adress for all aliens
2189: C3 C0 0F        JP      L0FC0 ; {code.L0FC0} Handle animations for killed aliens
218C: FF              .DB $FF
218D: FF              .DB $FF
218E: FF              .DB $FF
218F: FF              .DB $FF
L2190:
2190: CD 50 0A        CALL    AlienDataController ; {code.AlienDataController} draw or delete alien
2193: CD 00 30        CALL    L3000 ; {code.L3000}
2196: CD 00 0F        CALL    L0F00 ; {code.L0F00} 'alien with player' collision check
2199: CD 60 25        CALL    L2560 ; {code.L2560}
219C: C3 40 0C        JP      L0C40 ; {code.EnemyBulletUpdate}
219F: FF              .DB $FF
21A0: FF              .DB $FF
21A1: FF              .DB $FF
21A2: FF              .DB $FF
21A3: FF              .DB $FF
21A4: FF              .DB $FF
L21A5:
21A5: CD 1C 0D        CALL    L0D1C ; {code.AlienMovementUpdate}
21A8: CD 70 0D        CALL    L0D70 ; {code.AlienAnimationUpdate}
21AB: CD 6C 0A        CALL    L0A6C ; {code.L0A6C} get screen ram adress for all aliens
21AE: CD C0 0F        CALL    L0FC0 ; {code.L0FC0} Handle animations for killed aliens
21B1: C3 C4 24        JP      L24C4 ; {code.L24C4}
21B4: FF              .DB $FF
21B5: FF              .DB $FF
21B6: FF              .DB $FF
21B7: FF              .DB $FF
21B8: FF              .DB $FF
21B9: FF              .DB $FF
L21BA:
21BA: 78              LD      A,B
21BB: 0F              RRCA
21BC: D2 04 22        JP      NC,L2204 ; {code.L2204}
21BF: CD 40 0C        CALL    L0C40 ; {code.EnemyBulletUpdate}
21C2: CD C0 0F        CALL    L0FC0 ; {code.L0FC0} Handle animations for killed aliens
21C5: CD C4 24        CALL    L24C4 ; {code.L24C4}
21C8: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
21CB: E6 0F           AND     $0F ; mask out 0000_1111
21CD: FE 0B           CP      $0B
21CF: DA 04 22        JP      C,L2204 ; {code.L2204} if < game level B
21D2: 3E 10           LD      A,$10 ; 16 aliens for a new wave
21D4: 32 BA 43        LD      (AliensLeft),A ; {ram.AliensLeft}
21D7: C3 26 05        JP      L0526 ; {code.L0526} init alien data
21DA: FF              .DB $FF
21DB: FF              .DB $FF
DrawIntroBirdAnimationFrame:
21DC: 7E              LD      A,(HL) ; {ram.M4399} Actual index for slow print at intro splash (starts with $300)
21DD: 00              NOP
21DE: 47              LD      B,A ; save it
21DF: 21 73 4B        LD      HL,B4B73 ; {!+ram.B4B73} used as temp memory
21E2: E6 07           AND     $07 ; mask out 0000_0111 in order to count from 0 to 7
21E4: 77              LD      (HL),A ; save it
21E5: 2D              DEC     L
21E6: 36 EF           LD      (HL),$EF ; {ram.B4B72} use $4B72 for LSB of screen ram
21E8: 2D              DEC     L
21E9: 36 49           LD      (HL),$49 ; {ram.B4B71} use $4B71 for MSB of screen ram
21EB: 2D              DEC     L ; {ram.B4B70} $4B70 (bird0 index character block shape)
21EC: 78              LD      A,B ; {ram.Counter98} restore $4399
21ED: E6 F8           AND     $F8 ; mask out 1111_1000
21EF: 0F              RRCA ; Divide by 8 ..
21F0: 0F              RRCA ; ..
21F1: 0F              RRCA ; ..
21F2: C6 3A           ADD     T233A & $FF ; LSB of T233A
21F4: 5F              LD      E,A
21F5: 16 23           LD      D,T233A >> 8 ; MSB of T233A
21F7: 1A              LD      A,(DE) ; get data starting at T233A for animation frame index
21F8: 77              LD      (HL),A ; {ram.B4B70} write to $4B70
21F9: CD C0 34        CALL    DrawBirdObject ; {code.DrawBirdObject} draw the bird at intro
21FC: C3 E0 1E        JP      L1EE0 ; {code.L1EE0}
21FF: FF              .DB $FF
2200: FF              .DB $FF
2201: FF              .DB $FF
2202: FF              .DB $FF
2203: FF              .DB $FF
L2204:
2204: 21 B6 43        LD      HL,M43B6 ; {+ram.M43B6}
2207: 35              DEC     (HL)
2208: 7E              LD      A,(HL)
2209: FE A0           CP      $A0
220B: D0              RET     NC
220C: 2E A4           LD      L,$A4 ; GameState
220E: 36 02           LD      (HL),$02 ; set GameState to: 'initialization of game and level data'
2210: 2E A6           LD      L,$A6 ; ShieldCount
2212: 36 00           LD      (HL),$00 ; clear ShieldCount
2214: 2E B8           LD      L,$B8 ; LevelAndRound
2216: 34              INC     (HL) ; increment LevelAndRound
2217: 7E              LD      A,(HL)
2218: E6 0E           AND     $0E ; mask out 0000_1110
221A: 0F              RRCA ; divide by 2
221B: C6 60           ADD     T1760 & $FF ; add to base of table T1760
221D: 5F              LD      E,A
221E: 16 17           LD      D,T1760 >> 8
2220: 2C              INC     L
2221: 2C              INC     L ; AliensLeft
2222: 1A              LD      A,(DE) ; get value from table T1760
2223: A7              AND     A ; updates the flags
2224: F2 2A 22        JP      P,L222A ; {code.L222A} if not positive.
2227: 2C              INC     L ; use BirdsLeft
2228: E6 7F           AND     $7F ; mask out 0111_1111
L222A:
222A: 77              LD      (HL),A ; {ram.AliensLeft} {ram.BirdsLeft} save to $43BA (AliensLeft) or $43BB (BirdsLeft)
222B: C3 80 03        JP      ClearForeground ; {code.ClearForeground}
222E: FF              .DB $FF
222F: FF              .DB $FF
L2230:
2230: 21 9C 43        LD      HL,M439C ; {+ram.M439C}
2233: 7E              LD      A,(HL)
2234: 34              INC     (HL)
2235: 00              NOP
2236: 0F              RRCA
2237: E6 3F           AND     $3F ; mask out 0011_1111
2239: FE 0D           CP      $0D
223B: CA 92 22        JP      Z,L2292 ; {+code.L2292}
223E: 06 1F           LD      B,$1F ; The asterisk character
2240: DA 60 22        JP      C,L2260 ; {+code.L2260}
2243: 06 00           LD      B,$00 ; The space character
2245: D6 0E           SUB     $0E
2247: FE 0D           CP      $0D
2249: C2 60 22        JP      NZ,L2260 ; {+code.L2260}
224C: 21 B8 43        LD      HL,LevelAndRound ; {+ram.LevelAndRound}
224F: 34              INC     (HL) ; {ram.LevelAndRound} increment game level $43B8
2250: 2E A4           LD      L,$A4 ; GameState
2252: 36 02           LD      (HL),$02 ; Next interval game state is 2: 'init game and level data'
2254: C9              RET
2255: 58              .DB $58
2256: 2E              .DB $2E
2257: A4              .DB $A4
2258: 36              .DB $36
2259: 02              .DB $02
225A: C9              .DB $C9
225B: FF              .DB $FF
225C: FF              .DB $FF
225D: FF              .DB $FF
225E: FF              .DB $FF
225F: FF              .DB $FF
L2260:
2260: 4F              LD      C,A
2261: 0F              RRCA
2262: 0F              RRCA
2263: 0F              RRCA
2264: 57              LD      D,A
2265: E6 1F           AND     $1F ; 0001_1111
2267: 5F              LD      E,A
2268: 7A              LD      A,D
2269: E6 E0           AND     $E0 ; 1110_0000
226B: C6 B0           ADD     $B0
226D: 6F              LD      L,A
226E: 7B              LD      A,E
226F: CE 41           ADC     $41
2271: 67              LD      H,A
2272: 7D              LD      A,L
2273: 91              SUB     C
2274: 6F              LD      L,A
2275: 79              LD      A,C
2276: 3C              INC     A
2277: 4F              LD      C,A
2278: 07              RLCA ; Multiply by 2
2279: 5F              LD      E,A
L227A:
227A: 51              LD      D,C ; D is the height counter for each pass
L227B:
227B: 70              LD      (HL),B ; draw the asterisk or space
227C: 23              INC     HL ; one row down
227D: 70              LD      (HL),B ; another asterisk or space
227E: 23              INC     HL ; one row down
227F: 15              DEC     D ; all of this column done?
2280: C2 7B 22        JP      NZ,L227B ; {+code.L227B} No ... do all rows
2283: 7D              LD      A,L ; LSB of screen pointer
2284: 91              SUB     C ; move up ...
2285: 91              SUB     C ; ... height * 2
2286: D6 20           SUB     $20 ; Move right one column
2288: 6F              LD      L,A ; New LSB
2289: 7C              LD      A,H ; Borrow into ...
228A: DE 00           SBC     $00 ; ... the ...
228C: 67              LD      H,A ; ... MSB
228D: 1D              DEC     E ; All columns done?
228E: C2 7A 22        JP      NZ,L227A ; {+code.L227A} no ... do all columns
2291: C9              RET ; Done
L2292:
2292: 21 B8 43        LD      HL,LevelAndRound ; {+ram.LevelAndRound}
2295: 7E              LD      A,(HL)
2296: E6 08           AND     $08 ; mask out 0000_1000
2298: CA F0 22        JP      Z,L22F0 ; {+code.L22F0}
229B: 21 00 1C        LD      HL,T1C00 ; {+code.T1C00} Background stars to erase mother ship
229E: 11 3F 4B        LD      DE,$4B3F ; {+ram.BackgroundScreen+33F} End of background screen memory
22A1: 06 47           LD      B,$47
L22A3:
22A3: 7E              LD      A,(HL)
22A4: 12              LD      (DE),A
22A5: 2C              INC     L
22A6: 1B              DEC     DE
22A7: 7E              LD      A,(HL)
22A8: 12              LD      (DE),A
22A9: 2C              INC     L
22AA: 1B              DEC     DE
22AB: 78              LD      A,B
22AC: BA              CP      D
22AD: C2 A3 22        JP      NZ,L22A3 ; {+code.L22A3}
22B0: C3 E0 22        JP      L22E0 ; {code.L22E0}
22B3: FF              .DB $FF
L22B4:
22B4: CD 7A 06        CALL    StarsScrollDown ; {code.StarsScrollDown}
22B7: 21 B4 43        LD      HL,CounterB4 ; {+ram.CounterB4}
22BA: 35              DEC     (HL) ; decrement CounterB4
22BB: 7E              LD      A,(HL) ; get it
22BC: FE 28           CP      $28
22BE: C2 48 08        JP      NZ,L0848 ; {code.L0848} if counter value not reached
22C1: 2E 67           LD      L,$67
22C3: 36 FF           LD      (HL),$FF ; set flag for 'Mothership partially faded in'.
22C5: C9              RET
22C6: FF              .DB $FF
22C7: FF              .DB $FF
22C8: FF              .DB $FF
22C9: FF              .DB $FF
L22CA:
22CA: 21 B4 43        LD      HL,CounterB4 ; {+ram.CounterB4}
22CD: 7E              LD      A,(HL)
22CE: FE C0           CP      $C0
22D0: C2 34 08        JP      NZ,L0834 ; {code.L0834} Stars scrolling down and 'aliens fade in'
22D3: 36 30           LD      (HL),$30
22D5: 2E 67           LD      L,$67
22D7: 36 FF           LD      (HL),$FF ; set flag for 'Mothership partially faded in'.
22D9: 2E BC           LD      L,$BC
22DB: 36 3F           LD      (HL),$3F
22DD: C9              RET
22DE: FF              .DB $FF
22DF: FF              .DB $FF
L22E0:
22E0: 3E 71           LD      A,$71 ; init the ...
L22E2:
22E2: 32 B9 43        LD      (CounterB9),A ; {ram.CounterB9} free running 8 bit backwards counter
22E5: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
22E8: C9              RET
22E9: FF              .DB $FF
22EA: FF              .DB $FF
22EB: FF              .DB $FF
22EC: FF              .DB $FF
22ED: FF              .DB $FF
22EE: FF              .DB $FF
22EF: FF              .DB $FF
L22F0:
22F0: CD A0 03        CALL    ClearBackground ; {code.ClearBackground}
22F3: AF              XOR     A ; A=0
22F4: C3 E2 22        JP      L22E2 ; {code.L22E2}
22F7: FF              .DB $FF
22F8: FF              .DB $FF
22F9: FF              .DB $FF
L22FA:
22FA: 21 AA 4A        LD      HL,BackgroundScreen+$2AA ; {+ram.BackgroundScreen+2AA}
22FD: 06 12           LD      B,$12
22FF: 3A 8A 48        LD      A,(BackgroundScreen+$8A) ; {ram.BackgroundScreen+8A}
2302: 4F              LD      C,A
L2303:
2303: 79              LD      A,C
2304: E6 03           AND     $03 ; 0000_0011
2306: 07              RLCA ; Multiply by 4 ..
2307: 07              RLCA ; ..
2308: 57              LD      D,A
2309: 4E              LD      C,(HL)
230A: 79              LD      A,C
230B: E6 0C           AND     $0C ; 0000_1100
230D: 0F              RRCA
230E: 0F              RRCA
230F: B2              OR      D
2310: F6 60           OR      $60 ; 0110_0000
2312: 77              LD      (HL),A
2313: 7D              LD      A,L
2314: D6 20           SUB     $20
2316: 6F              LD      L,A
2317: D2 1B 23        JP      NC,L231B ; {code.L231B}
231A: 25              DEC     H
L231B:
231B: 05              DEC     B
231C: C2 03 23        JP      NZ,L2303 ; {code.L2303}
231F: C9              RET
2320: FF              .DB $FF
2321: FF              .DB $FF
L2322:
2322: 21 A7 43        LD      HL,AnimationCounter ; {+ram.AnimationCounter}
2325: 34              INC     (HL) ; increment the animation counter
2326: 7E              LD      A,(HL)
2327: E6 07           AND     $07 ; mask out 0000_0111, in order to count from 0 to 7 for 8 frames
2329: 07              RLCA ; Multiply by 8 ..
232A: 07              RLCA ; ..to get..
232B: 07              RLCA ; ..the frame data adress (8 characters per frame)
232C: C6 C0           ADD     T1BC0 & $FF ; LSB of T1BC0
232E: 6F              LD      L,A
232F: 26 1B           LD      H,T1BC0 >> 8 ; MSB of T1BC0
2331: 11 A6 49        LD      DE,BackgroundScreen+$1A6 ; {+ram.BackgroundScreen+1A6} at the middle of the mothership
2334: 01 02 04        LD      BC,$0402 ; images are 2x4
2337: C3 D6 0A        JP      DrawImageCbyB ; {code.DrawImageCbyB}
T233A:
233A: 01 02 03 04     .DB $01, $02, $03, $04, $05, $06, $07, $0A, $07, $0A, $07, $0A, $07, $0A, $07, $0A
233E: 05 06 07 0A
2342: 07 0A 07 0A
2346: 07 0A 07 0A
234A: 09 08 04 03     .DB $09, $08, $04, $03, $02, $01, $FF
234E: 02 01 FF
L2351:
2351: 1A              LD      A,(DE)
2352: E6 08           AND     $08 ; 0000_1000
2354: C8              RET     Z
2355: 7E              LD      A,(HL)
2356: 2C              INC     L
2357: 6E              LD      L,(HL)
2358: C6 08           ADD     $08
235A: 67              LD      H,A
235B: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
235E: 0F              RRCA
235F: 0F              RRCA
2360: 0F              RRCA
2361: 85              ADD     A,L
2362: E6 1F           AND     $1F ; 0001_1111
2364: 47              LD      B,A
2365: 7D              LD      A,L
2366: E6 E0           AND     $E0 ; 1110_0000
2368: B0              OR      B
2369: 6F              LD      L,A
236A: 7E              LD      A,(HL)
236B: 47              LD      B,A
236C: E6 FC           AND     $FC ; 1111_1100
236E: FE 4C           CP      $4C
2370: CA 7B 23        JP      Z,L237B ; {code.L237B}
2373: E6 F0           AND     $F0 ; 1111_0000
2375: FE 60           CP      $60
2377: CA 98 23        JP      Z,L2398 ; {code.L2398}
237A: C9              RET
L237B:
237B: 1A              LD      A,(DE)
237C: E6 F7           AND     $F7 ; 1111_0111
237E: 12              LD      (DE),A
237F: 3E FF           LD      A,$FF
2381: 32 66 43        LD      (M4366),A ; {ram.M4366}
2384: 78              LD      A,B
2385: 3D              DEC     A
2386: 77              LD      (HL),A
2387: FE 4B           CP      $4B
2389: C0              RET     NZ
238A: 36 00           LD      (HL),$00
238C: 2D              DEC     L
238D: 7E              LD      A,(HL)
238E: FE 5E           CP      $5E
2390: C0              RET     NZ
2391: 36 4F           LD      (HL),$4F
2393: C9              RET
2394: FF              .DB $FF
2395: FF              .DB $FF
2396: FF              .DB $FF
2397: FF              .DB $FF
L2398:
2398: 1A              LD      A,(DE)
2399: E6 F7           AND     $F7 ; 1111_0111
239B: 12              LD      (DE),A
239C: 1C              INC     E
239D: 1C              INC     E
239E: 1A              LD      A,(DE)
239F: E6 04           AND     $04 ; 0000_0100
23A1: 78              LD      A,B
23A2: C2 30 20        JP      NZ,L2030 ; {code.L2030}
23A5: E6 0C           AND     $0C ; 0000_1100
23A7: FE 04           CP      $04
23A9: 11 40 1B        LD      DE,$1B40
L23AC:
23AC: CA C0 23        JP      Z,L23C0 ; {code.L23C0}
23AF: 78              LD      A,B
23B0: E6 0F           AND     $0F ; 0000_1111
23B2: 83              ADD     A,E
23B3: 5F              LD      E,A
23B4: 1A              LD      A,(DE)
23B5: 77              LD      (HL),A
23B6: 3E FF           LD      A,$FF
23B8: 32 66 43        LD      (M4366),A ; {ram.M4366}
23BB: C9              RET
23BC: FF              .DB $FF
23BD: FF              .DB $FF
23BE: FF              .DB $FF
23BF: FF              .DB $FF
L23C0:
23C0: 2D              DEC     L
23C1: 7E              LD      A,(HL)
23C2: E6 F0           AND     $F0 ; 1111_0000
23C4: FE 70           CP      $70
23C6: C0              RET     NZ
23C7: 21 A4 43        LD      HL,GameState ; {+ram.GameState} Next interval game state ...
23CA: 36 06           LD      (HL),$06 ; ... is 6 (mother ship partikel explosion)
23CC: 2C              INC     L ; CounterA5
23CD: 36 60           LD      (HL),$60 ; set counter value for
23CF: 2E 63           LD      L,$63 ; ParticleExplosion
23D1: 36 FF           LD      (HL),$FF ; Set flag for: 'particle explosion start'
23D3: C9              RET
23D4: FF              .DB $FF
23D5: FF              .DB $FF
L23D6:
23D6: 21 B8 43        LD      HL,LevelAndRound ; {+ram.LevelAndRound}
23D9: 7E              LD      A,(HL)
23DA: E6 0F           AND     $0F ; mask out 0000_1111
23DC: FE 01           CP      $01
23DE: CA 98 3A        JP      Z,L3A98 ; {code.L3A98} if game level is 1 (1st alien wave)
23E1: FE 03           CP      $03
23E3: CA 98 3A        JP      Z,L3A98 ; {code.L3A98} if game level is 3 (2nd alien wave)
23E6: FE 05           CP      $05
23E8: CA D0 3A        JP      Z,L3AD0 ; {code.L3AD0} if game level is 5 (1st bird wave)
23EB: FE 07           CP      $07
23ED: CA D0 3A        JP      Z,L3AD0 ; {code.L3AD0} if game level is 7 (2nd bird wave)
23F0: FE 09           CP      $09
23F2: D8              RET     C ; if game level is 9 (mothership 'fade in')
23F3: FE 0B           CP      $0B
23F5: DA 02 3B        JP      C,L3B02 ; {code.L3B02} if game level is B (mothership)
23F8: CD 02 3B        CALL    L3B02 ; {code.L3B02}
23FB: C3 98 3A        JP      L3A98 ; {code.L3A98}
23FE: FF              .DB $FF
23FF: FF              .DB $FF
L2400:
2400: CD 2C 24        CALL    L242C ; {code.L242C}
2403: CA 52 25        JP      Z,L2552 ; {code.L2552}
2406: FE 20           CP      $20
2408: DA 6A 24        JP      C,EraseMothership ; {code.EraseMothership}
240B: CA 20 25        JP      Z,L2520 ; {code.L2520} Calculation and display of the bonus score for mothership explosion
240E: 47              LD      B,A
240F: 0F              RRCA
2410: 00              NOP
2411: 78              LD      A,B
2412: D2 E8 20        JP      NC,L20E8 ; {code.L20E8}
2415: 7B              LD      A,E
2416: D6 05           SUB     $05
2418: C6 C0           ADD     $C0
241A: 4F              LD      C,A
241B: 7A              LD      A,D
241C: CE 00           ADC     $00
241E: 47              LD      B,A
241F: 7E              LD      A,(HL)
2420: 11 00 2A        LD      DE,T2A00 ; {+code.T2A00} get the foreground tiles of the mothership particles explosion
2423: 21 00 2B        LD      HL,T2B00 ; {+code.T2B00} get the control data
2426: C3 85 20        JP      L2085 ; {code.L2085}
2429: FF              .DB $FF
242A: FF              .DB $FF
242B: FF              .DB $FF
L242C:
242C: 21 B9 43        LD      HL,CounterB9 ; {+ram.CounterB9}
242F: 7E              LD      A,(HL)
2430: E6 F8           AND     $F8 ; 1111_1000
2432: 77              LD      (HL),A
2433: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
2436: 11 C6 41        LD      DE,$41C6 ; {+ram.ForegroundScreen+1C6}
2439: 0F              RRCA
243A: 0F              RRCA
243B: 0F              RRCA
243C: 47              LD      B,A
243D: 7B              LD      A,E
243E: 90              SUB     B
243F: E6 1F           AND     $1F ; 0001_1111
2441: 47              LD      B,A
2442: 7B              LD      A,E
2443: E6 E0           AND     $E0 ; 1110_0000
2445: B0              OR      B
2446: 5F              LD      E,A
2447: 2E A5           LD      L,$A5 ; CounterA5
2449: 35              DEC     (HL) ; decrement it
244A: 7E              LD      A,(HL)
244B: C9              RET
L244C:
244C: 21 A5 43        LD      HL,CounterA5 ; {+ram.CounterA5}
244F: 35              DEC     (HL)
2450: 7E              LD      A,(HL)
2451: 0F              RRCA
2452: DA F0 06        JP      C,L06F0 ; {code.L06F0} update scroll register and fill background
2455: A7              AND     A ; updates the zero flag
2456: C0              RET     NZ
2457: 2D              DEC     L
2458: 36 02           LD      (HL),$02
245A: 2E B8           LD      L,$B8 ; LevelAndRound
245C: 7E              LD      A,(HL)
245D: E6 F0           AND     $F0 ; 1111_0000
245F: C6 10           ADD     $10 ; go to next round and ..
2461: 77              LD      (HL),A ; {ram.LevelAndRound} .. store at LevelAndRound $43B8
2462: 2E BA           LD      L,$BA ; AliensLeft
2464: 36 10           LD      (HL),$10 ; set AliensLeft to 16
2466: C3 80 03        JP      ClearForeground ; {code.ClearForeground}
2469: FF              .DB $FF
EraseMothership:
246A: 01 14 09        LD      BC,$0914 ; 20x9 image
246D: 11 C6 4A        LD      DE,$4AC6 ; {+ram.BackgroundScreen+2C6} Screen coordinate of mother ship
2470: 21 00 1C        LD      HL,$1C00 ; Background stars to erase the mother ship
2473: C3 D6 0A        JP      DrawImageCbyB ; {code.DrawImageCbyB} Erase the mother ship
L2476:
2476: 78              LD      A,B
2477: 81              ADD     A,C
2478: CD 95 24        CALL    L2495 ; {code.L2495}
247B: 2E D3           LD      L,$D3 ; {ram.B4BD3} $4BD3 (bird extended storage)
247D: 77              LD      (HL),A
247E: 21 BB 43        LD      HL,BirdsLeft ; {+ram.BirdsLeft}
2481: 3E 08           LD      A,$08 ; number of birds
2483: 96              SUB     (HL)
2484: 07              RLCA ; Multiply by 2
2485: 2E 9A           LD      L,$9A ; Counter9A
2487: 86              ADD     A,(HL)
2488: 07              RLCA ; Multiply by 2
2489: 47              LD      B,A
248A: 2E 6F           LD      L,$6F ; {ram.M436F} $436F
248C: 7E              LD      A,(HL)
248D: E6 1E           AND     $1E ; 0001_1110
248F: 80              ADD     A,B
2490: 32 D1 4B        LD      (M4BD1),A ; {!ram.B4BD1}
2493: C9              RET
2494: 1F              .DB $1F
L2495:
2495: 80              ADD     A,B
2496: 0D              DEC     C
2497: C8              RET     Z
2498: 80              ADD     A,B
2499: 0D              DEC     C
249A: C8              RET     Z
249B: 80              ADD     A,B
249C: 0D              DEC     C
249D: C8              RET     Z
249E: 87              ADD     A,A
249F: C9              RET
L24A0:
24A0: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
24A3: E6 0F           AND     $0F ; mask out 0000_1111
24A5: FE 08           CP      $08
24A7: D8              RET     C ; return if game level < 8
24A8: 11 C4 43        LD      DE,PlayerBulletState ; {+ram.PlayerBulletState}
24AB: 21 E6 43        LD      HL,AbovePlayerBulletMSB ; {+ram.AbovePlayerBulletMSB}
24AE: CD 51 23        CALL    L2351 ; {code.L2351}
24B1: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
24B4: E6 03           AND     $03 ; mask out 0000_0011
24B6: FE 03           CP      $03
24B8: C0              RET     NZ ; return if <> 3
24B9: C3 F2 24        JP      L24F2 ; {code.L24F2}
24BC: CD              .DB $CD ; {code.L2351}
24BD: 51              .DB $51
24BE: 23              .DB $23
24BF: C9              .DB $C9
24C0: FF              .DB $FF
24C1: FF              .DB $FF
24C2: FF              .DB $FF
24C3: FF              .DB $FF
L24C4:
24C4: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
24C7: E6 0F           AND     $0F ; mask out 0000_1111
24C9: FE 08           CP      $08
24CB: DA F0 06        JP      C,L06F0 ; {code.L06F0} update scroll register and fill background if game level < 8
24CE: CD E0 24        CALL    L24E0 ; {code.L24E0}
24D1: 21 AA 43        LD      HL,M43AA ; {+ram.M43AA}
24D4: 34              INC     (HL)
24D5: 7E              LD      A,(HL)
24D6: E6 03           AND     $03 ; mask out 0000_0011
24D8: CA FA 22        JP      Z,L22FA ; {code.L22FA} if $43AA <> 3
24DB: C3 22 23        JP      L2322 ; {code.L2322} Animation of the mothership's antenna and the alien pilot
24DE: 24              .DB $24
24DF: BF              .DB $BF
L24E0:
24E0: 3A AA 43        LD      A,(M43AA) ; {ram.M43AA}
24E3: E6 0F           AND     $0F ; 0000_1111
24E5: C0              RET     NZ
24E6: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
24E9: FE A0           CP      $A0
24EB: D8              RET     C
24EC: C3 7A 06        JP      StarsScrollDown ; {code.StarsScrollDown}
24EF: FA              .DB $FA
24F0: 22              .DB $22
24F1: C3              .DB $C3
L24F2:
24F2: CD AA 30        CALL    GetRandomNumber ; {code.GetRandomNumber}
24F5: C6 60           ADD     $60
24F7: 00              NOP
24F8: 47              LD      B,A
24F9: 21 9B 43        LD      HL,Counter9A+$1 ; {+ram.Counter9A+1}
24FC: E6 0E           AND     $0E ; 0000_1110
24FE: A6              AND     (HL)
24FF: C0              RET     NZ
2500: 3A 9E 43        LD      A,(M439E) ; {ram.M439E}
2503: B8              CP      B
2504: D0              RET     NC
2505: 3A 9F 43        LD      A,(M439F) ; {ram.M439F}
2508: B8              CP      B
2509: D8              RET     C
250A: 78              LD      A,B
250B: D6 04           SUB     $04
250D: 47              LD      B,A
250E: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
2511: 2F              CPL
2512: 3C              INC     A
2513: E6 F8           AND     $F8 ; 1111_1000
2515: C6 48           ADD     $48
2517: 4F              LD      C,A
2518: E5              PUSH    HL
2519: E5              PUSH    HL
251A: C3 B7 25        JP      L25B7 ; {code.L25B7}
251D: FF              .DB $FF
251E: FF              .DB $FF
251F: FF              .DB $FF
L2520:
2520: D5              PUSH    DE
2521: CD 80 03        CALL    ClearForeground ; {code.ClearForeground} remove all but the rest of the mothership
2524: D1              POP     DE
2525: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9} get value from 8 bit backwards counter
2528: C6 60           ADD     $60 ; use it for a ...
252A: 0F              RRCA ; ... score value
252B: 47              LD      B,A ; save it
252C: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
252F: E6 F0           AND     $F0 ; mask out 1111_0000 (bit4 - 7: game round)
2531: 80              ADD     A,B ; add score value
2532: 06 90           LD      B,$90
2534: DA 3D 25        JP      C,L253D ; {code.L253D}
2537: FE 90           CP      $90
2539: D2 3D 25        JP      NC,L253D ; {code.L253D} if >= $90
253C: 47              LD      B,A
L253D:
253D: AF              XOR     A ; A=0
253E: 78              LD      A,B
253F: 27              DAA ; adjust for BCD
2540: 21 9D 43        LD      HL,M439D ; {+ram.M439D}
2543: 77              LD      (HL),A ; set value for fist two digits of BCD score
2544: 2C              INC     L
2545: 36 00           LD      (HL),$00 ; last two digits of BCD score set to '00'
2547: 7B              LD      A,E ; get LSB of screen ram...
2548: D6 5E           SUB     $5E ; ...
254A: 5F              LD      E,A ; ...
254B: 06 04           LD      B,$04 ; number of digits to print
254D: C3 C4 00        JP      PrintNumber ; {code.PrintNumber} score for mothership explosion
2550: 32              .DB $32
2551: 80              .DB $80
L2552:
2552: 2E A4           LD      L,$A4 ; GameState
2554: 36 07           LD      (HL),$07 ; set to 'mother ship score display'
2556: 2C              INC     L ; CounterA5
2557: 36 40           LD      (HL),$40 ; set it
2559: 2E 6B           LD      L,$6B ; {ram.M436B} $436B
255B: 36 FF           LD      (HL),$FF ; set flag for 'mother ship score display'
255D: C9              RET
255E: FF              .DB $FF
255F: FF              .DB $FF
L2560:
2560: 21 93 43        LD      HL,Counter93 ; {+ram.Counter93}
2563: 7E              LD      A,(HL)
2564: E6 01           AND     $01 ; 0000_0001
2566: 07              RLCA ; Multiply by 32 ..
2567: 07              RLCA ; ..
2568: 07              RLCA ; ..
2569: 07              RLCA ; ..
256A: 07              RLCA ; ..
256B: C6 70           ADD     $70
256D: 6F              LD      L,A
256E: 26 4B           LD      H,$4B
2570: 1E 08           LD      E,$08
2572: 3A 57 43        LD      A,(M4357) ; {ram.M4357}
2575: 07              RLCA ; Multiply by 8 ..
2576: 07              RLCA ; ..
2577: 07              RLCA ; ..
2578: 00              NOP
2579: C6 AD           ADD     $AD
257B: 57              LD      D,A
257C: 3A 9F 43        LD      A,(M439F) ; {ram.M439F}
257F: C6 03           ADD     $03
2581: 4F              LD      C,A
2582: 3A 9E 43        LD      A,(M439E) ; {ram.M439E}
2585: D6 0A           SUB     $0A
2587: 47              LD      B,A
L2588:
2588: E5              PUSH    HL
2589: CD 96 25        CALL    L2596 ; {code.L2596}
258C: E1              POP     HL
258D: 7D              LD      A,L
258E: C6 04           ADD     $04
2590: 6F              LD      L,A
2591: 1D              DEC     E
2592: C2 88 25        JP      NZ,L2588 ; {code.L2588}
2595: C9              RET
L2596:
2596: 7E              LD      A,(HL)
2597: E6 08           AND     $08 ; 0000_1000
2599: C8              RET     Z
259A: 2C              INC     L
259B: 7E              LD      A,(HL)
259C: FE 08           CP      $08
259E: C8              RET     Z
259F: FE 88           CP      $88
25A1: D0              RET     NC
25A2: 2C              INC     L
25A3: 7E              LD      A,(HL)
25A4: B8              CP      B
25A5: D8              RET     C
25A6: B9              CP      C
25A7: D0              RET     NC
25A8: 2C              INC     L
25A9: 7E              LD      A,(HL)
25AA: BA              CP      D
25AB: D0              RET     NC
25AC: FE 80           CP      $80
25AE: D8              RET     C
25AF: 00              NOP
25B0: 00              NOP
25B1: 00              NOP
25B2: 00              NOP
25B3: 00              NOP
25B4: 4F              LD      C,A
25B5: 2D              DEC     L
25B6: 46              LD      B,(HL)
L25B7:
25B7: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
25BA: 16 03           LD      D,$03
25BC: FE 10           CP      $10 ; 0001_0000
25BE: DA CA 25        JP      C,L25CA ; {code.L25CA} if game round < 1
25C1: 16 04           LD      D,$04
25C3: FE 20           CP      $20 ; 0010_0000
25C5: DA CA 25        JP      C,L25CA ; {code.L25CA} if game round < 2
25C8: 16 05           LD      D,$05
L25CA:
25CA: 21 CC 43        LD      HL,AlienBullet0State ; {+ram.EnemyBullet0State}
L25CD:
25CD: 7E              LD      A,(HL)
25CE: E6 08           AND     $08 ; mask out 0000_1000
25D0: CA E0 25        JP      Z,L25E0 ; {code.L25E0}
25D3: 7D              LD      A,L
25D4: C6 04           ADD     $04
25D6: 6F              LD      L,A
25D7: 15              DEC     D
25D8: C2 CD 25        JP      NZ,L25CD ; {code.L25CD}
25DB: E1              POP     HL
25DC: E1              POP     HL
25DD: C9              RET
25DE: FF              .DB $FF
25DF: FF              .DB $FF
L25E0:
25E0: 78              LD      A,B
25E1: C6 04           ADD     $04
25E3: 47              LD      B,A
25E4: 79              LD      A,C
25E5: C6 0C           ADD     $0C
25E7: 4F              LD      C,A
25E8: 36 08           LD      (HL),$08
25EA: 2C              INC     L
25EB: 78              LD      A,B
25EC: 0F              RRCA
25ED: E6 03           AND     $03 ; 0000_0011
25EF: 57              LD      D,A
25F0: 79              LD      A,C
25F1: E6 04           AND     $04 ; 0000_0100
25F3: 82              ADD     A,D
25F4: C6 58           ADD     $58
25F6: 77              LD      (HL),A
25F7: 2C              INC     L
25F8: 70              LD      (HL),B
25F9: 2C              INC     L
25FA: 71              LD      (HL),C
25FB: E1              POP     HL
25FC: E1              POP     HL
25FD: C9              RET
25FE: FF              .DB $FF
25FF: FF              .DB $FF
L2600:
2600: 00              NOP ; Old command removed or space for a future replace patch
2601: 00              NOP ; ..
2602: 00              NOP ; ..
2603: 00              NOP ; ..
2604: 00              NOP ; ..
2605: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
2608: 2F              CPL
2609: 0F              RRCA
260A: 0F              RRCA
260B: 0F              RRCA
260C: E6 1F           AND     $1F ; 0001_1111
260E: 21 D2 4B        LD      HL,M4BD2 ; {!+ram.B4BD2}
2611: 77              LD      (HL),A
2612: 2C              INC     L
2613: 3A D1 4B        LD      A,(M4BD1) ; {!ram.B4BD1}
2616: BE              CP      (HL)
2617: DA 50 26        JP      C,L2650 ; {code.L2650}
261A: 3A D5 4B        LD      A,(M4BD5) ; {!ram.B4BD5}
261D: 57              LD      D,A
261E: E6 03           AND     $03 ; 0000_0011
2620: 5F              LD      E,A
2621: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
2624: 07              RLCA ; Multiply by 4 ..
2625: 07              RLCA ; ..
2626: E6 0C           AND     $0C ; 0000_1100
2628: 83              ADD     A,E
2629: C6 D0           ADD     $D0
262B: 6F              LD      L,A
262C: 26 3E           LD      H,$3E
262E: 7A              LD      A,D
262F: 0F              RRCA
2630: 0F              RRCA
2631: E6 07           AND     $07 ; 0000_0111
2633: 86              ADD     A,(HL)
2634: 57              LD      D,A
2635: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
2638: 92              SUB     D
L2639:
2639: 32 B9 43        LD      (CounterB9),A ; {ram.CounterB9}
263C: 32 00 58        LD      (scrollRegister),A ; {hard.scrollRegister} 58xx scroll register
263F: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
2642: 0F              RRCA
2643: D2 D0 26        JP      NC,L26D0 ; {code.L26D0}
2646: CD 68 26        CALL    L2668 ; {code.L2668}
2649: C3 AA 26        JP      L26AA ; {code.L26AA}
264C: C2              .DB $C2
264D: 3A              .DB $3A
264E: 26              .DB $26
264F: 3A              .DB $3A
L2650:
2650: 2C              INC     L
2651: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
2654: 07              RLCA ; Multiply by 4 ..
2655: 07              RLCA ; ..
2656: E6 0C           AND     $0C ; 0000_1100
2658: 86              ADD     A,(HL)
2659: C6 D0           ADD     $D0
265B: 6F              LD      L,A
265C: 26 3E           LD      H,$3E
265E: 3A B9 43        LD      A,(CounterB9) ; {ram.CounterB9}
2661: 86              ADD     A,(HL)
2662: C3 39 26        JP      L2639 ; {code.L2639}
2665: D2 AE 26        JP      NC,L26AE ; {code.L26AE}
L2668:
2668: 3A 6E 43        LD      A,(M436E) ; {ram.M436E}
266B: 00              NOP
266C: 47              LD      B,A
266D: 3A 9A 43        LD      A,(Counter9A) ; {ram.Counter9A}
2670: FE 18           CP      $18
2672: DA 76 26        JP      C,L2676 ; {code.L2676}
2675: 04              INC     B
L2676:
2676: FE 10           CP      $10
2678: DA 7C 26        JP      C,L267C ; {code.L267C}
267B: 04              INC     B
L267C:
267C: 3A BA 43        LD      A,(AliensLeft) ; {ram.AliensLeft}
267F: FE 03           CP      $03
2681: D2 85 26        JP      NC,L2685 ; {code.L2685} if >= $03
2684: 04              INC     B
L2685:
2685: 3A D6 4B        LD      A,(M4BD6) ; {!ram.B4BD6}
2688: C6 E0           ADD     $E0
268A: 6F              LD      L,A
268B: 26 3E           LD      H,$3E
268D: 78              LD      A,B
268E: BE              CP      (HL)
268F: DA 93 26        JP      C,L2693 ; {code.L2693}
2692: 7E              LD      A,(HL)
L2693:
2693: 57              LD      D,A
2694: 3A BB 43        LD      A,(BirdsLeft) ; {ram.BirdsLeft}
2697: FE 04           CP      $04
2699: D2 9D 26        JP      NC,L269D ; {code.L269D} if >= $04
269C: 14              INC     D
L269D:
269D: FE 02           CP      $02
269F: D2 A3 26        JP      NC,L26A3 ; {code.L26A3} if >= $02
26A2: 14              INC     D
L26A3:
26A3: 7A              LD      A,D
26A4: 32 D5 4B        LD      (M4BD5),A ; {!ram.B4BD5}
26A7: C9              RET
26A8: 00              .DB $00
26A9: 58              .DB $58
L26AA:
26AA: 21 D3 4B        LD      HL,M4BD3 ; {!+ram.B4BD3}
26AD: 7E              LD      A,(HL)
L26AE:
26AE: 35              DEC     (HL)
26AF: A7              AND     A ; updates the zero flag
26B0: C0              RET     NZ
26B1: 34              INC     (HL)
26B2: 2E D6           LD      L,$D6 ; {ram.B4BD6} $4BD6
26B4: 7E              LD      A,(HL)
26B5: FE 16           CP      $16
26B7: D0              RET     NC
26B8: FE 08           CP      $08
26BA: D8              RET     C
26BB: 2C              INC     L
26BC: 96              SUB     (HL)
26BD: 07              RLCA ; Multiply by 2
26BE: 47              LD      B,A
26BF: 3A 6F 43        LD      A,(M436F) ; {ram.M436F}
26C2: E6 03           AND     $03 ; 0000_0011
26C4: 2E D4           LD      L,$D4 ; {ram.B4BD4} $4BD4
26C6: 77              LD      (HL),A
26C7: 2F              CPL
26C8: E6 03           AND     $03 ; 0000_0011
26CA: 3C              INC     A
26CB: 4F              LD      C,A
26CC: C3 76 24        JP      L2476 ; {code.L2476}
26CF: C9              .DB $C9
L26D0:
26D0: 21 A8 4B        LD      HL,M4BA8 ; {+ram.M4BA8}
26D3: 01 00 08        LD      BC,$0800
26D6: 11 00 80        LD      DE,$8000
L26D9:
26D9: 7E              LD      A,(HL)
26DA: A7              AND     A ; updates the zero flag
26DB: CA E5 26        JP      Z,L26E5 ; {code.L26E5}
26DE: 7A              LD      A,D
26DF: 07              RLCA ; Multiply by 2
26E0: D2 E4 26        JP      NC,L26E4 ; {code.L26E4}
26E3: 51              LD      D,C
L26E4:
26E4: 59              LD      E,C
L26E5:
26E5: 0C              INC     C
26E6: 7D              LD      A,L
26E7: 90              SUB     B
26E8: 6F              LD      L,A
26E9: FE 68           CP      $68
26EB: C2 D9 26        JP      NZ,L26D9 ; {code.L26D9}
26EE: 3A D2 4B        LD      A,(M4BD2) ; {!ram.B4BD2}
26F1: 82              ADD     A,D
26F2: 83              ADD     A,E
26F3: E6 1F           AND     $1F ; 0001_1111
26F5: 32 D6 4B        LD      (M4BD6),A ; {!ram.B4BD6}
26F8: 7B              LD      A,E
26F9: 92              SUB     D
26FA: 32 D7 4B        LD      (M4BD7),A ; {!ram.B4BD7}
26FD: C9              RET
26FE: FF              .DB $FF
26FF: FF              .DB $FF
UpdateScoresAndSound:
2700: 21 A2 43        LD      HL,GameOrAttract ; {+ram.GameOrAttract}
2703: 7E              LD      A,(HL) ; get it
2704: A7              AND     A ; updates the zero flag
2705: C8              RET     Z ; if GameOrAttract is 'Attract mode'.
2706: 2C              INC     L
2707: 7E              LD      A,(HL) ; get GameAndDemoOrSplash
2708: E6 01           AND     $01 ; mask out 0000_0001 'Game for player 2'
270A: 07              RLCA ; Multiply by 4 ..
270B: 07              RLCA ; ..
270C: C6 83           ADD     $83
270E: 6F              LD      L,A
270F: 3E FF           LD      A,$FF
2711: 32 97 43        LD      (M4397),A ; {ram.M4397}
2714: 11 70 43        LD      DE,M4370 ; {+ram.M4370}
L2717:
2717: CD 48 27        CALL    L2748 ; {code.L2748} add score values for all enemies hit.
271A: 1C              INC     E
271B: 1C              INC     E
271C: 1C              INC     E
271D: 7B              LD      A,E
271E: FE 80           CP      $80 ; {ram.M4370} {ram.M4380} from $4370 to $4380
2720: C2 17 27        JP      NZ,L2717 ; {code.L2717}
2723: 1E 9D           LD      E,$9D
2725: 3A A4 43        LD      A,(GameState) ; {ram.GameState}
2728: FE 06           CP      $06
272A: C2 39 27        JP      NZ,L2739 ; {code.L2739}
272D: 1A              LD      A,(DE)
272E: 47              LD      B,A
272F: 0E 00           LD      C,$00
2731: CD 20 02        CALL    AddToScore ; {code.AddToScore}
2734: AF              XOR     A ; A=0
2735: 12              LD      (DE),A
2736: 32 97 43        LD      (M4397),A ; {ram.M4397}
L2739:
2739: 3A 97 43        LD      A,(M4397) ; {ram.M4397}
273C: A7              AND     A ; updates the zero flag
273D: CC 68 27        CALL    Z,L2768 ; {code.L2768} if $4397 is 0.
2740: CD A8 27        CALL    UpdateSoundControlHW ; {code.UpdateSoundControlHW}
2743: C3 10 3A        JP      L3A10 ; {code.L3A10}
2746: FF              .DB $FF
2747: FF              .DB $FF
L2748:
2748: 1A              LD      A,(DE) ; {ram.M4370} get $4370
2749: 1C              INC     E
274A: FE 01           CP      $01
274C: C0              RET     NZ ; if not 1
274D: 1A              LD      A,(DE)
274E: A7              AND     A ; updates the zero flag
274F: C8              RET     Z
2750: 0F              RRCA ; enemy has been hit
2751: 0F              RRCA
2752: 0F              RRCA
2753: 0F              RRCA
2754: 47              LD      B,A
2755: E6 F0           AND     $F0 ; 1111_0000
2757: 4F              LD      C,A
2758: 78              LD      A,B
2759: E6 0F           AND     $0F ; 0000_1111
275B: 47              LD      B,A
275C: CD 20 02        CALL    AddToScore ; {code.AddToScore}
275F: AF              XOR     A ; Clear A Reg.
2760: 12              LD      (DE),A ; clear the temp. score storage and ...
2761: 32 97 43        LD      (M4397),A ; {ram.M4397} ... the first two digits of BCD score value
2764: C9              RET
2765: FF              .DB $FF
2766: FF              .DB $FF
2767: FF              .DB $FF
L2768:
2768: E5              PUSH    HL
2769: 11 61 42        LD      DE,$4261 ; {+ram.ForegroundScreen+261} end of the screen area of player 1 score
276C: 06 06           LD      B,$06 ; number of digits to print
276E: 3A A3 43        LD      A,(GameAndDemoOrSplash) ; {ram.GameAndDemoOrSplash}
2771: A7              AND     A ; updates the zero flag
2772: CA 78 27        JP      Z,$2778 ; {} if GameAndDemoOrSplash is 'Game and demo for player 1'
2775: 11 21 40        LD      DE,$4021 ; {+ram.ForegroundScreen+21} end of the screen area of player 2 score
2778: CD C4 00        CALL    PrintNumber ; {code.PrintNumber} update the score on screen
277B: E1              POP     HL
277C: 11 BD 43        LD      DE,M43BD ; {+ram.M43BD}
277F: EB              EX      DE,HL
2780: 7E              LD      A,(HL)
2781: 2C              INC     L
2782: B6              OR      (HL)
2783: C8              RET     Z
2784: 2C              INC     L
2785: EB              EX      DE,HL
2786: CD 14 03        CALL    L0314 ; {code.L0314}
2789: D0              RET     NC
278A: 3A A3 43        LD      A,(GameAndDemoOrSplash) ; {ram.GameAndDemoOrSplash}
278D: C6 90           ADD     $90
278F: 6F              LD      L,A
2790: 34              INC     (HL)
2791: CD 67 03        CALL    UpdateLivesScreen ; {code.UpdateLivesScreen}
2794: 3E FF           LD      A,$FF
2796: 32 6A 43        LD      (M436A),A ; {ram.M436A}
2799: 2E BE           LD      L,$BE ; BonusLivesAt
279B: 7E              LD      A,(HL)
279C: 36 00           LD      (HL),$00
279E: 0F              RRCA
279F: 0F              RRCA
27A0: 0F              RRCA
27A1: 0F              RRCA
27A2: 2D              DEC     L ; {ram.M43BD} $43BD
27A3: 77              LD      (HL),A
27A4: C9              RET
27A5: FF              .DB $FF
27A6: FF              .DB $FF
27A7: FF              .DB $FF
UpdateSoundControlHW:
27A8: 21 8C 43        LD      HL,SoundControlA ; {+ram.SoundControlA} ..
27AB: 7E              LD      A,(HL) ; .. to
27AC: 32 00 60        LD      (SOUNDCTLA),A ; {hard.soundControlA} 60xx sound A
27AF: 2C              INC     L ; SoundControlB ..
27B0: 7E              LD      A,(HL) ; .. to
27B1: 32 00 68        LD      (SOUNDCTLB),A ; {hard.soundControlB} 68xx sound B
27B4: F6 0F           OR      $0F ; 0000_1111
27B6: 77              LD      (HL),A
27B7: 2D              DEC     L
27B8: 36 0F           LD      (HL),$0F
27BA: C9              RET
27BB: FF              .DB $FF
27BC: FF              .DB $FF
L27BD:
27BD: 21 63 43        LD      HL,ParticleExplosion ; {+ram.ParticleExplosion}
27C0: 7E              LD      A,(HL)
27C1: A7              AND     A ; updates the zero flag
27C2: C2 E2 27        JP      NZ,L27E2 ; {code.L27E2} if player ship was hit.
27C5: 2E 61           LD      L,$61 ; BulletTriggered
27C7: 7E              LD      A,(HL)
27C8: A7              AND     A ; updates the zero flag
27C9: C8              RET     Z
27CA: FE 19           CP      $19
27CC: D2 D8 27        JP      NC,L27D8 ; {code.L27D8} if >= $19
27CF: 35              DEC     (HL)
27D0: 2E 8C           LD      L,$8C ; SoundControlA
27D2: 7E              LD      A,(HL)
27D3: F6 40           OR      $40 ; 0100_0000
27D5: 77              LD      (HL),A
27D6: C9              RET
27D7: 77              .DB $77
L27D8:
27D8: 36 18           LD      (HL),$18
27DA: 2E 8C           LD      L,$8C ; SoundControlA
27DC: 7E              LD      A,(HL)
27DD: E6 BF           AND     $BF ; 1011_1111
27DF: 77              LD      (HL),A
27E0: C9              RET
27E1: 36              .DB $36
L27E2:
27E2: FE 40           CP      $40
27E4: DA E9 27        JP      C,L27E9 ; {code.L27E9}
27E7: 36 40           LD      (HL),$40
L27E9:
27E9: 35              DEC     (HL)
27EA: 2E 8C           LD      L,$8C ; SoundControlA
27EC: 36 8F           LD      (HL),$8F ; 1000_1111
27EE: C9              RET
27EF: FF              .DB $FF
27F0: FF              .DB $FF
27F1: FF              .DB $FF
27F2: FF              .DB $FF
27F3: FF              .DB $FF
27F4: FF              .DB $FF
27F5: FF              .DB $FF
27F6: FF              .DB $FF
27F7: FF              .DB $FF
27F8: FF              .DB $FF
27F9: FF              .DB $FF
27FA: FF              .DB $FF
27FB: FF              .DB $FF
27FC: FF              .DB $FF
27FD: FF              .DB $FF
27FE: FF              .DB $FF
27FF: FF              .DB $FF
T2800:
2800: 00 32 00 00     .DB $00, $32, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $42, $42
2804: 00 00 00 00
2808: 00 00 00 00
280C: 00 00 42 42
2810: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $E1, $00, $00, $E2, $00, $00
2814: 00 00 00 00
2818: 00 00 E1 00
281C: 00 E2 00 00
2820: 32 00 00 00     .DB $32, $00, $00, $00, $00, $00, $00, $00, $00, $E0, $00, $00, $40, $00, $00, $C3
2824: 00 00 00 00
2828: 00 E0 00 00
282C: 40 00 00 C3
2830: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $DF, $00, $00, $E2, $00, $00, $E0, $00, $E1, $00
2834: 00 00 DF 00
2838: 00 E2 00 00
283C: E0 00 E1 00
2840: 00 30 00 00     .DB $00, $30, $00, $00, $00, $00, $DE, $00, $00, $00, $C2, $00, $40, $00, $E0, $00
2844: 00 00 DE 00
2848: 00 00 C2 00
284C: 40 00 E0 00
2850: 00 00 00 30     .DB $00, $00, $00, $30, $00, $30, $00, $5A, $00, $00, $E1, $00, $40, $00, $E2, $00
2854: 00 30 00 5A
2858: 00 00 E1 00
285C: 40 00 E2 00
2860: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $30, $C1, $3E, $00, $E0, $00, $40, $C2, $00
2864: 00 00 00 30
2868: C1 3E 00 E0
286C: 00 40 C2 00
2870: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $5A, $C1, $3E, $C8, $D8, $00, $00
2874: 00 00 00 00
2878: 00 5A C1 3E
287C: C8 D8 00 00
2880: E0 E1 C2 E2     .DB $E0, $E1, $C2, $E2, $E0, $00, $E1, $00, $C2, $00, $E2, $CE, $CA, $DA, $00, $00
2884: E0 00 E1 00
2888: C2 00 E2 CE
288C: CA DA 00 00
2890: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $CF, $CF, $C3, $3F, $C2, $41, $E0, $00
2894: 00 00 00 00
2898: CF CF C3 3F
289C: C2 41 E0 00
28A0: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $DE, $00, $3F, $00, $C2, $41, $00, $E1, $00
28A4: 00 00 00 DE
28A8: 00 3F 00 C2
28AC: 41 00 E1 00
28B0: 00 00 00 00     .DB $00, $00, $00, $00, $00, $3D, $DF, $3D, $00, $00, $E1, $00, $41, $00, $00, $C2
28B4: 00 3D DF 3D
28B8: 00 00 E1 00
28BC: 41 00 00 C2
28C0: 00 00 00 3D     .DB $00, $00, $00, $3D, $00, $00, $00, $00, $00, $E0, $00, $00, $41, $00, $00, $E2
28C4: 00 00 00 00
28C8: 00 E0 00 00
28CC: 41 00 00 E2
28D0: 00 00 3D 00     .DB $00, $00, $3D, $00, $00, $00, $00, $00, $E2, $00, $00, $00, $00, $4F, $00, $E0
28D4: 00 00 00 00
28D8: E2 00 00 00
28DC: 00 4F 00 E0
28E0: 00 3B 00 00     .DB $00, $3B, $00, $00, $00, $00, $00, $00, $00, $C2, $00, $00, $00, $4F, $00, $00
28E4: 00 00 00 00
28E8: 00 C2 00 00
28EC: 00 4F 00 00
28F0: 00 00 3B 00     .DB $00, $00, $3B, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $4D, $4D
28F4: 00 00 00 00
28F8: 00 00 00 00
28FC: 00 00 4D 4D
T2900:
2900: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $20, $00, $38
2904: 00 00 00 00
2908: 00 00 00 00
290C: 00 20 00 38
2910: 00 34 00 28     .DB $00, $34, $00, $28, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
2914: 00 00 00 00
2918: 00 00 00 00
291C: 00 00 00 00
2920: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $10, $00, $02, $00, $00
2924: 00 00 00 00
2928: 00 00 00 10
292C: 00 02 00 00
2930: 00 01 00 00     .DB $00, $01, $00, $00, $12, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
2934: 12 00 00 00
2938: 00 00 00 00
293C: 00 00 00 00
2940: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $10, $00, $00, $80, $48, $00, $04
2944: 00 00 00 00
2948: 00 10 00 00
294C: 80 48 00 04
2950: 40 08 00 50     .DB $40, $08, $00, $50, $00, $00, $80, $10, $00, $00, $00, $00, $00, $00, $00, $00
2954: 00 00 80 10
2958: 00 00 00 00
295C: 00 00 00 00
2960: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $10, $00, $00, $20, $44, $00, $00, $00, $02
2964: 00 00 00 10
2968: 00 00 20 44
296C: 00 00 00 02
2970: 10 00 00 04     .DB $10, $00, $00, $04, $00, $48, $20, $00, $00, $10, $00, $00, $00, $00, $00, $00
2974: 00 48 20 00
2978: 00 10 00 00
297C: 00 00 00 00
2980: 00 00 00 00     .DB $00, $00, $00, $00, $00, $10, $00, $00, $00, $44, $08, $00, $00, $01, $00, $00
2984: 00 10 00 00
2988: 00 44 08 00
298C: 00 01 00 00
2990: 08 00 00 02     .DB $08, $00, $00, $02, $00, $00, $00, $84, $08, $00, $00, $20, $00, $00, $00, $00
2994: 00 00 00 84
2998: 08 00 00 20
299C: 00 00 00 00
29A0: 00 00 00 20     .DB $00, $00, $00, $20, $00, $00, $00, $42, $02, $00, $80, $00, $00, $00, $00, $00
29A4: 00 00 00 42
29A8: 02 00 80 00
29AC: 00 00 00 00
29B0: 04 00 00 01     .DB $04, $00, $00, $01, $00, $00, $00, $00, $00, $82, $04, $00, $00, $20, $00, $00
29B4: 00 00 00 00
29B8: 00 82 04 00
29BC: 00 20 00 00
29C0: 00 40 00 00     .DB $00, $40, $00, $00, $01, $82, $00, $00, $40, $00, $00, $00, $00, $00, $00, $00
29C4: 01 82 00 00
29C8: 40 00 00 00
29CC: 00 00 00 00
29D0: 02 00 00 00     .DB $02, $00, $00, $00, $80, $00, $00, $00, $00, $00, $00, $81, $02, $00, $00, $40
29D4: 80 00 00 00
29D8: 00 00 00 81
29DC: 02 00 00 40
29E0: 02 80 00 04     .DB $02, $80, $00, $04, $00, $00, $40, $00, $00, $00, $00, $00, $00, $00, $00, $00
29E4: 00 00 40 00
29E8: 00 00 00 00
29EC: 00 00 00 00
29F0: 01 00 00 00     .DB $01, $00, $00, $00, $00, $00, $40, $00, $00, $00, $00, $00, $00, $02, $04, $08
29F4: 00 00 40 00
29F8: 00 00 00 00
29FC: 00 02 04 08
T2A00:
2A00: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $D2, $00, $00, $00, $00, $00, $00, $00, $00
2A04: 00 00 00 D2
2A08: 00 00 00 00
2A0C: 00 00 00 00
2A10: 00 00 00 00     .DB $00, $00, $00, $00, $00, $DE, $00, $5E, $E0, $00, $00, $E1, $00, $00, $00, $00
2A14: 00 DE 00 5E
2A18: E0 00 00 E1
2A1C: 00 00 00 00
2A20: 00 00 C1 00     .DB $00, $00, $C1, $00, $00, $CF, $53, $E2, $00, $D2, $E0, $00, $00, $D0, $00, $00
2A24: 00 CF 53 E2
2A28: 00 D2 E0 00
2A2C: 00 D0 00 00
2A30: 00 00 00 DE     .DB $00, $00, $00, $DE, $00, $CE, $53, $E1, $D1, $E3, $00, $E1, $D3, $00, $00, $00
2A34: 00 CE 53 E1
2A38: D1 E3 00 E1
2A3C: D3 00 00 00
2A40: 00 00 CF C0     .DB $00, $00, $CF, $C0, $DE, $DF, $53, $D3, $E2, $00, $E2, $D2, $00, $5E, $E2, $00
2A44: DE DF 53 D3
2A48: E2 00 E2 D2
2A4C: 00 5E E2 00
2A50: 00 00 00 CE     .DB $00, $00, $00, $CE, $C1, $C2, $DE, $D2, $E1, $E3, $D1, $00, $D2, $00, $00, $00
2A54: C1 C2 DE D2
2A58: E1 E3 D1 00
2A5C: D2 00 00 00
2A60: 00 00 00 00     .DB $00, $00, $00, $00, $DF, $DE, $C2, $CF, $E0, $D0, $E2, $E1, $C2, $C3, $00, $00
2A64: DF DE C2 CF
2A68: E0 D0 E2 E1
2A6C: C2 C3 00 00
2A70: DF DE CF CE     .DB $DF, $DE, $CF, $CE, $DF, $DE, $CF, $C8, $D8, $5E, $CE, $00, $CF, $DE, $DF, $CE
2A74: DF DE CF C8
2A78: D8 5E CE 00
2A7C: CF DE DF CE
2A80: E0 E3 E2 E1     .DB $E0, $E3, $E2, $E1, $00, $E0, $D1, $CA, $DA, $D1, $D2, $D3, $D0, $D1, $D2, $D3
2A84: 00 E0 D1 CA
2A88: DA D1 D2 D3
2A8C: D0 D1 D2 D3
2A90: 00 00 00 00     .DB $00, $00, $00, $00, $E3, $D2, $CE, $D2, $E2, $E0, $D3, $D1, $D3, $00, $00, $00
2A94: E3 D2 CE D2
2A98: E2 E0 D3 D1
2A9C: D3 00 00 00
2AA0: 00 00 00 E2     .DB $00, $00, $00, $E2, $D3, $CF, $DF, $E1, $D0, $E3, $E1, $D2, $00, $00, $00, $00
2AA4: D3 CF DF E1
2AA8: D0 E3 E1 D2
2AAC: 00 00 00 00
2AB0: 00 00 E1 D0     .DB $00, $00, $E1, $D0, $DE, $00, $DE, $E2, $00, $D3, $53, $E2, $5E, $C1, $C0, $00
2AB4: DE 00 DE E2
2AB8: 00 D3 53 E2
2ABC: 5E C1 C0 00
2AC0: 00 00 00 DF     .DB $00, $00, $00, $DF, $00, $00, $CF, $5E, $D1, $D2, $00, $53, $E3, $00, $00, $00
2AC4: 00 00 CF 5E
2AC8: D1 D2 00 53
2ACC: E3 00 00 00
2AD0: 00 00 CE 00     .DB $00, $00, $CE, $00, $CF, $00, $CE, $D2, $D2, $00, $53, $00, $5E, $E0, $00, $00
2AD4: CF 00 CE D2
2AD8: D2 00 53 00
2ADC: 5E E0 00 00
2AE0: 00 00 00 00     .DB $00, $00, $00, $00, $00, $DE, $00, $E1, $D3, $00, $E2, $00, $00, $00, $00, $00
2AE4: 00 DE 00 E1
2AE8: D3 00 E2 00
2AEC: 00 00 00 00
2AF0: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $5E, $D0, $00, $00, $00, $00, $00, $00, $00
2AF4: 00 00 00 5E
2AF8: D0 00 00 00
2AFC: 00 00 00 00
T2B00:
2B00: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $80, $01, $40, $02, $80, $05
2B04: 00 00 00 00
2B08: 00 00 80 01
2B0C: 40 02 80 05
2B10: A0 01 40 02     .DB $A0, $01, $40, $02, $00, $01, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
2B14: 00 01 00 00
2B18: 00 00 00 00
2B1C: 00 00 00 00
2B20: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $80, $00, $00, $01, $20, $04, $00, $01, $40, $12
2B24: 00 00 80 00
2B28: 00 01 20 04
2B2C: 00 01 40 12
2B30: 48 02 80 01     .DB $48, $02, $80, $01, $20, $04, $00, $00, $00, $01, $00, $00, $00, $00, $00, $00
2B34: 20 04 00 00
2B38: 00 01 00 00
2B3C: 00 00 00 00
2B40: 00 00 00 00     .DB $00, $00, $00, $00, $80, $00, $00, $02, $10, $08, $00, $01, $80, $04, $A0, $21
2B44: 80 00 00 02
2B48: 10 08 00 01
2B4C: 80 04 A0 21
2B50: 84 05 20 02     .DB $84, $05, $20, $02, $80, $01, $10, $08, $00, $00, $00, $01, $00, $00, $00, $00
2B54: 80 01 10 08
2B58: 00 00 00 01
2B5C: 00 00 00 00
2B60: 00 00 80 00     .DB $00, $00, $80, $00, $00, $04, $08, $10, $00, $01, $40, $00, $40, $0A, $10, $40
2B64: 00 04 08 10
2B68: 00 01 40 00
2B6C: 40 0A 10 40
2B70: 02 08 40 00     .DB $02, $08, $40, $00, $10, $04, $80, $02, $08, $10, $00, $00, $00, $01, $00, $00
2B74: 10 04 80 02
2B78: 08 10 00 00
2B7C: 00 01 00 00
2B80: 80 00 00 08     .DB $80, $00, $00, $08, $04, $20, $00, $02, $20, $00, $20, $14, $00, $01, $08, $80
2B84: 04 20 00 02
2B88: 20 00 20 14
2B8C: 00 01 08 80
2B90: 01 10 80 02     .DB $01, $10, $80, $02, $20, $00, $08, $04, $80, $02, $04, $20, $00, $00, $00, $01
2B94: 20 00 08 04
2B98: 80 02 04 20
2B9C: 00 00 00 01
2BA0: 01 01 01 01     .DB $01, $01, $01, $01, $01, $04, $20, $00, $10, $28, $80, $02, $04, $00, $00, $04
2BA4: 01 04 20 00
2BA8: 10 28 80 02
2BAC: 04 00 00 04
2BB0: 20 20 00 04     .DB $20, $20, $00, $04, $40, $01, $10, $00, $04, $08, $80, $04, $00, $00, $00, $00
2BB4: 40 01 10 00
2BB8: 04 08 80 04
2BBC: 00 00 00 00
2BC0: 00 00 00 08     .DB $00, $00, $00, $08, $20, $00, $88, $10, $00, $44, $00, $00, $00, $10, $02, $00
2BC4: 20 00 88 10
2BC8: 00 44 00 00
2BCC: 00 10 02 00
2BD0: 08 40 00 00     .DB $08, $40, $00, $00, $00, $08, $40, $00, $08, $01, $00, $10, $80, $04, $00, $00
2BD4: 00 08 40 00
2BD8: 08 01 00 10
2BDC: 80 04 00 00
2BE0: 00 00 20 00     .DB $00, $00, $20, $00, $84, $20, $00, $08, $00, $00, $00, $00, $00, $20, $01, $00
2BE4: 84 20 00 08
2BE8: 00 00 00 00
2BEC: 00 20 01 00
2BF0: 04 80 00 00     .DB $04, $80, $00, $00, $00, $00, $00, $10, $40, $00, $04, $01, $00, $00, $80, $00
2BF4: 00 00 00 10
2BF8: 40 00 04 01
2BFC: 00 00 80 00
T2C00:
2C00: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $0A, $0A, $0A, $0A, $0A, $0A, $0A, $06, $06, $1E
2C04: 0B 0C 0A 0A
2C08: 0A 0A 0A 0A
2C0C: 0A 06 06 1E
2C10: 03 03 1F 05     .DB $03, $03, $1F, $05, $05, $1C, $04, $04, $04, $1D, $06, $06, $1A, $04, $04, $04
2C14: 05 1C 04 04
2C18: 04 1D 06 06
2C1C: 1A 04 04 04
2C20: 1B 05 05 05     .DB $1B, $05, $05, $05, $05, $18, $1F, $07, $07, $07, $07, $07, $07, $07, $07, $07
2C24: 05 18 1F 07
2C28: 07 07 07 07
2C2C: 07 07 07 07
2C30: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T2C34:
2C34: 05 05 1C 04     .DB $05, $05, $1C, $04, $1D, $0A, $0A, $0A, $0A, $0A, $0A, $06
2C38: 1D 0A 0A 0A
2C3C: 0A 0A 0A 06
2C40: 06 1E 03 03     .DB $06, $1E, $03, $03, $1F, $05, $1C, $04, $04, $1D, $0A, $06, $06, $1E, $03, $03
2C44: 1F 05 1C 04
2C48: 04 1D 0A 06
2C4C: 06 1E 03 03
2C50: 1F 05 1C 04     .DB $1F, $05, $1C, $04, $04, $1D, $0A, $06, $06, $1E, $03, $03, $1F, $05, $1C, $04
2C54: 04 1D 0A 06
2C58: 06 1E 03 03
2C5C: 1F 05 1C 04
2C60: 04 1D 0A 06     .DB $04, $1D, $0A, $06, $1E, $03, $1F, $05, $1C, $04, $1D, $06, $1E, $03, $03, $03
2C64: 1E 03 1F 05
2C68: 1C 04 1D 06
2C6C: 1E 03 03 03
2C70: 03 15 16 17     .DB $03, $15, $16, $17, $01, $01, $05, $05, $01, $01, $05, $05, $01, $01, $05, $05
2C74: 01 01 05 05
2C78: 01 01 05 05
2C7C: 01 01 05 05
2C80: 01 01 05 05     .DB $01, $01, $05, $05, $02, $02, $18, $07, $07, $07, $00, $FF, $FF, $FF, $FF, $FF
2C84: 02 02 18 07
2C88: 07 07 00 FF
2C8C: FF FF FF FF
T2C90:
2C90: 1C 04 04 04     .DB $1C, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1D
2C94: 04 04 04 04
2C98: 04 04 04 04
2C9C: 04 04 04 1D
2CA0: 06 06 06 06     .DB $06, $06, $06, $06, $06, $06, $06, $1E, $03, $03, $03, $03, $03, $03, $1F, $05
2CA4: 06 06 06 1E
2CA8: 03 03 03 03
2CAC: 03 03 1F 05
2CB0: 05 05 05 1C     .DB $05, $05, $05, $1C, $04, $04, $1D, $06, $09, $09, $09, $1E, $03, $07, $07, $08
2CB4: 04 04 1D 06
2CB8: 09 09 09 1E
2CBC: 03 07 07 08
2CC0: 08 07 07 08     .DB $08, $07, $07, $08, $07, $00, $FF, $FF
2CC4: 07 00 FF FF
T2CC8:
2CC8: 05 05 05 05     .DB $05, $05, $05, $05, $1C, $04, $04, $04
2CCC: 1C 04 04 04
2CD0: 04 04 04 04     .DB $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1D, $09, $09, $09, $09
2CD4: 04 04 04 04
2CD8: 04 04 04 1D
2CDC: 09 09 09 09
2CE0: 0A 0A 0A 09     .DB $0A, $0A, $0A, $09, $0A, $0A, $06, $1E, $03, $03, $03, $1F, $05, $05, $18, $03
2CE4: 0A 0A 06 1E
2CE8: 03 03 03 1F
2CEC: 05 05 18 03
2CF0: 19 06 06 1E     .DB $19, $06, $06, $1E, $03, $03, $1F, $05, $05, $05, $05, $05, $05, $05, $00, $FF
2CF4: 03 03 1F 05
2CF8: 05 05 05 05
2CFC: 05 05 00 FF
T2D00:
2D00: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $06, $1E, $03, $03, $03, $03, $03, $03, $03, $03
2D04: 0B 0C 06 1E
2D08: 03 03 03 03
2D0C: 03 03 03 03
2D10: 03 03 03 03     .DB $03, $03, $03, $03, $03, $03, $1F, $05, $05, $1C, $04, $04, $04, $04, $04, $04
2D14: 03 03 1F 05
2D18: 05 1C 04 04
2D1C: 04 04 04 04
2D20: 04 04 04 04     .DB $04, $04, $04, $04, $1D, $06, $06, $1E, $03, $03, $03, $03, $03, $03, $1F, $05
2D24: 1D 06 06 1E
2D28: 03 03 03 03
2D2C: 03 03 1F 05
2D30: 05 05 05 05     .DB $05, $05, $05, $05, $1C, $04, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1B
2D34: 1C 04 04 04
2D38: 04 04 04 04
2D3C: 04 04 04 1B
2D40: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T2D44:
2D44: 05 05 05 18     .DB $05, $05, $05, $18, $03, $03, $03, $03, $03, $03, $03, $03
2D48: 03 03 03 03
2D4C: 03 03 03 03
2D50: 03 19 06 06     .DB $03, $19, $06, $06, $1A, $04, $04, $1B, $05, $05, $18, $03, $03, $03, $03, $03
2D54: 1A 04 04 1B
2D58: 05 05 18 03
2D5C: 03 03 03 03
2D60: 03 03 19 06     .DB $03, $03, $19, $06, $06, $06, $06, $06, $06, $06, $06, $06, $06, $1A, $04, $04
2D64: 06 06 06 06
2D68: 06 06 06 06
2D6C: 06 1A 04 04
2D70: 1B 05 05 1C     .DB $1B, $05, $05, $1C, $04, $04, $1D, $06, $06, $1A, $04, $04, $1B, $05, $05, $05
2D74: 04 04 1D 06
2D78: 06 1A 04 04
2D7C: 1B 05 05 05
2D80: 05 05 05 05     .DB $05, $05, $05, $05, $00, $FF, $FF, $FF
2D84: 00 FF FF FF
T2D88:
2D88: 1C 04 04 1D     .DB $1C, $04, $04, $1D, $06, $06, $09, $0A
2D8C: 06 06 09 0A
2D90: 0A 09 09 09     .DB $0A, $09, $09, $09, $16, $17, $14, $03, $03, $03, $1F, $05, $05, $1C, $04, $04
2D94: 16 17 14 03
2D98: 03 03 1F 05
2D9C: 05 1C 04 04
2DA0: 1D 06 06 1E     .DB $1D, $06, $06, $1E, $03, $03, $03, $03, $07, $07, $08, $08, $07, $07, $05, $05
2DA4: 03 03 03 03
2DA8: 07 07 08 08
2DAC: 07 07 05 05
2DB0: 1C 04 04 04     .DB $1C, $04, $04, $04, $04, $04, $04, $04, $1D, $1A, $04, $1B, $00, $FF, $FF, $FF
2DB4: 04 04 04 04
2DB8: 1D 1A 04 1B
2DBC: 00 FF FF FF
T2DC0:
2DC0: 14 03 03 19     .DB $14, $03, $03, $19, $06, $0A, $0A, $09, $09, $09, $0A, $12, $13, $10, $11, $12
2DC4: 06 0A 0A 09
2DC8: 09 09 0A 12
2DCC: 13 10 11 12
2DD0: 13 10 11 12     .DB $13, $10, $11, $12, $13, $10, $04, $04, $04, $04, $1B, $05, $18, $03, $19, $06
2DD4: 13 10 04 04
2DD8: 04 04 1B 05
2DDC: 18 03 19 06
2DE0: 1A 04 1B 05     .DB $1A, $04, $1B, $05, $18, $07, $07, $07, $08, $08, $07, $07, $07, $03, $03, $19
2DE4: 18 07 07 07
2DE8: 08 08 07 07
2DEC: 07 03 03 19
2DF0: 0D 0E 00 FF     .DB $0D, $0E, $00, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
2DF4: FF FF FF FF
2DF8: FF FF FF FF
2DFC: FF FF FF FF
T2E00:
2E00: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $02, $02, $02, $02, $0B, $0C, $0D, $0E, $01, $01, $14, $15
2E04: 02 02 02 02
2E08: 0B 0C 0D 0E
2E0C: 01 01 14 15
2E10: 16 17 01 01     .DB $16, $17, $01, $01, $05, $05, $05, $05, $02, $02, $02, $02, $00, $FF, $FF, $FF
2E14: 05 05 05 05
2E18: 02 02 02 02
2E1C: 00 FF FF FF
T2E20:
2E20: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $0D, $0E, $02, $02, $02, $02, $02, $02, $02, $02
2E24: 0B 0C 0D 0E
2E28: 02 02 02 02
2E2C: 02 02 02 02
2E30: 05 05 01 05     .DB $05, $05, $01, $05, $05, $01, $05, $05, $01, $05, $05, $01, $00, $FF, $FF, $FF
2E34: 05 01 05 05
2E38: 01 05 05 01
2E3C: 00 FF FF FF
T2E40:
2E40: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $01, $01, $01, $18, $03, $19, $06, $06, $1A, $04, $1B, $05
2E44: 01 01 01 18
2E48: 03 19 06 06
2E4C: 1A 04 1B 05
2E50: 18 03 19 06     .DB $18, $03, $19, $06, $06, $1A, $04, $04, $04, $04, $04, $04, $04, $04, $04, $1B
2E54: 06 1A 04 04
2E58: 04 04 04 04
2E5C: 04 04 04 1B
2E60: 05 05 05 01     .DB $05, $05, $05, $01, $01, $01, $01, $01, $00, $FF, $FF, $FF
2E64: 01 01 01 01
2E68: 00 FF FF FF
T2E6C:
2E6C: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E
2E70: 01 01 0B 0C     .DB $01, $01, $0B, $0C, $0D, $0E, $01, $01, $05, $05, $05, $05, $01, $01, $0B, $0C
2E74: 0D 0E 01 01
2E78: 05 05 05 05
2E7C: 01 01 0B 0C
2E80: 0D 0E 01 01     .DB $0D, $0E, $01, $01, $07, $08, $08, $07, $08, $08, $08, $07, $00, $FF, $FF, $FF
2E84: 07 08 08 07
2E88: 08 08 08 07
2E8C: 00 FF FF FF
T2E90:
2E90: 14 15 16 17     .DB $14, $15, $16, $17, $14, $15, $16, $17, $14, $03, $03, $03, $03, $03, $03, $03
2E94: 14 15 16 17
2E98: 14 03 03 03
2E9C: 03 03 03 03
2EA0: 03 03 03 03     .DB $03, $03, $03, $03, $03, $19, $09, $0A, $0A, $09, $09, $0A, $0A, $12, $13, $08
2EA4: 03 19 09 0A
2EA8: 0A 09 09 0A
2EAC: 0A 12 13 08
2EB0: 08 07 07 08     .DB $08, $07, $07, $08, $08, $08, $08, $04, $04, $04, $11, $12, $13, $10, $11, $12
2EB4: 08 08 08 04
2EB8: 04 04 11 12
2EBC: 13 10 11 12
2EC0: 13 00 FF FF     .DB $13, $00, $FF, $FF
T2EC4:
2EC4: 10 11 12 13     .DB $10, $11, $12, $13, $10, $11, $12, $13, $10, $04, $04, $04
2EC8: 10 11 12 13
2ECC: 10 04 04 04
2ED0: 04 04 04 04     .DB $04, $04, $04, $04, $04, $04, $0A, $0A, $0A, $09, $0A, $09, $0A, $09, $16, $17
2ED4: 04 04 0A 0A
2ED8: 0A 09 0A 09
2EDC: 0A 09 16 17
2EE0: 14 03 03 03     .DB $14, $03, $03, $03, $07, $07, $07, $07, $03, $19, $06, $1A, $04, $1B, $05, $18
2EE4: 07 07 07 07
2EE8: 03 19 06 1A
2EEC: 04 1B 05 18
2EF0: 07 07 07 07     .DB $07, $07, $07, $07, $00, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
2EF4: 00 FF FF FF
2EF8: FF FF FF FF
2EFC: FF FF FF FF
T2F00:
2F00: 05 1C 04 1D     .DB $05, $1C, $04, $1D, $06, $06, $06, $06, $06, $09, $09, $09, $0A, $0A, $0A, $09
2F04: 06 06 06 06
2F08: 06 09 09 09
2F0C: 0A 0A 0A 09
2F10: 09 16 17 14     .DB $09, $16, $17, $14, $1F, $05, $18, $03, $19, $06, $1E, $03, $1F, $05, $18, $03
2F14: 1F 05 18 03
2F18: 19 06 1E 03
2F1C: 1F 05 18 03
2F20: 19 06 1E 03     .DB $19, $06, $1E, $03, $1F, $05, $05, $1C, $08, $08, $08, $08, $08, $08, $08, $08
2F24: 1F 05 05 1C
2F28: 08 08 08 08
2F2C: 08 08 08 08
2F30: 00 FF FF FF     .DB $00, $FF, $FF, $FF
T2F34:
2F34: 05 18 03 19     .DB $05, $18, $03, $19, $06, $06, $06, $06, $0A, $0A, $09, $09
2F38: 06 06 06 06
2F3C: 0A 0A 09 09
2F40: 0A 0A 09 0A     .DB $0A, $0A, $09, $0A, $0A, $12, $13, $10, $1B, $05, $1C, $04, $1D, $1E, $1F, $1C
2F44: 0A 12 13 10
2F48: 1B 05 1C 04
2F4C: 1D 1E 1F 1C
2F50: 04 1D 06 1A     .DB $04, $1D, $06, $1A, $04, $04, $1B, $05, $18, $07, $07, $07, $07, $08, $07, $07
2F54: 04 04 1B 05
2F58: 18 07 07 07
2F5C: 07 08 07 07
2F60: 07 07 00 FF     .DB $07, $07, $00, $FF
T2F64:
2F64: 0B 0C 0D 0E     .DB $0B, $0C, $0D, $0E, $0B, $0C, $1E, $03, $19, $06, $1E, $03
2F68: 0B 0C 1E 03
2F6C: 19 06 1E 03
2F70: 19 06 1E 03     .DB $19, $06, $1E, $03, $19, $06, $1E, $1F, $1C, $1D, $1E, $03, $03, $03, $1F, $05
2F74: 19 06 1E 1F
2F78: 1C 1D 1E 03
2F7C: 03 03 1F 05
2F80: 18 03 19 06     .DB $18, $03, $19, $06, $1E, $03, $1F, $05, $08, $08, $08, $08, $08, $08, $08, $07
2F84: 1E 03 1F 05
2F88: 08 08 08 08
2F8C: 08 08 08 07
2F90: 07 08 08 08     .DB $07, $08, $08, $08, $08, $08, $00, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
2F94: 08 08 00 FF
2F98: FF FF FF FF
2F9C: FF FF FF FF
T2FA0:
2FA0: 05 05 18 03     .DB $05, $05, $18, $03, $03, $03, $03, $03, $03, $03, $03, $19, $06, $06, $06, $06
2FA4: 03 03 03 03
2FA8: 03 03 03 19
2FAC: 06 06 06 06
2FB0: 06 06 06 1A     .DB $06, $06, $06, $1A, $04, $1B, $05, $18, $03, $03, $03, $03, $19, $06, $06, $06
2FB4: 04 1B 05 18
2FB8: 03 03 03 03
2FBC: 19 06 06 06
2FC0: 1A 04 1B 05     .DB $1A, $04, $1B, $05, $18, $03, $03, $03, $03, $19, $06, $06, $06, $1A, $04, $1B
2FC4: 18 03 03 03
2FC8: 03 19 06 06
2FCC: 06 1A 04 1B
2FD0: 05 18 03 03     .DB $05, $18, $03, $03, $03, $03, $19, $06, $06, $06, $1A, $04, $1B, $05, $18, $03
2FD4: 03 03 19 06
2FD8: 06 06 1A 04
2FDC: 1B 05 18 03
2FE0: 03 19 06 06     .DB $03, $19, $06, $06, $1A, $11, $12, $13, $02, $02, $02, $05, $05, $02, $02, $02
2FE4: 1A 11 12 13
2FE8: 02 02 02 05
2FEC: 05 02 02 02
2FF0: 05 05 02 02     .DB $05, $05, $02, $02, $02, $05, $1C, $08, $08, $07, $07, $08, $08, $08, $00, $FF
2FF4: 02 05 1C 08
2FF8: 08 07 07 08
2FFC: 08 08 00 FF
L3000:
3000: 21 93 43        LD      HL,Counter93 ; {+ram.Counter93}
3003: 7E              LD      A,(HL) ; load and save ram value
3004: 34              INC     (HL) ; increment Counter93
3005: E6 07           AND     $07 ; masc out 0000_0111 the saved value in order to count from 0 to 7
3007: 21 18 30        LD      HL,T3018 ; {+code.T3018} base of jump table
300A: 07              RLCA ; Multiply by 2 to get a 2 byte offset
300B: 85              ADD     A,L
300C: 6F              LD      L,A
300D: 7E              LD      A,(HL) ; get MSB from jump table
300E: 23              INC     HL
300F: 6E              LD      L,(HL) ; get LSB from jump table
3010: 67              LD      H,A
3011: E9              JP      (HL) ; jump to the corresponding function
L3012:
3012: C9              RET
3013: FF              .DB $FF
3014: FF              .DB $FF
3015: FF              .DB $FF
3016: FF              .DB $FF
3017: FF              .DB $FF
T3018:
3018: 32 64           .DW L3264 ; if Counter93 is 0 {code.l3264} $3264
301A: 30 28           .DW L3028 ; if Counter93 is 1 {code.l3028} $3028
301C: 30 BA           .DW L30BA ; if Counter93 is 2 {code.l30ba} $30BA
301E: 31 24           .DW L3124 ; if Counter93 is 3 {code.l3124} $3124
3020: 31 5A           .DW L315A ; if Counter93 is 4 {code.l315a} $315A
3022: 31 B4           .DW L31B4 ; if Counter93 is 5 {code.l31b4} $31B4
3024: 32 2C           .DW L322C ; if Counter93 is 6 {code.l322c} $322C
3026: 30 12           .DW L3012 ; if Counter93 is 7 {code.L3012} $3012
L3028:
3028: 21 57 43        LD      HL,M4357 ; {+ram.M4357}
302B: 7E              LD      A,(HL)
302C: FE 03           CP      $03
302E: D0              RET     NC ; if >= 3
302F: 2E 50           LD      L,$50
3031: 7E              LD      A,(HL) ; {ram.M4350} get $4350
3032: FE 04           CP      $04
3034: D0              RET     NC ; if >= 4
3035: 2E 58           LD      L,$58
3037: 7E              LD      A,(HL) ; {ram.M4358} get $4358
3038: A7              AND     A ; updates the zero flag
3039: CA 5C 30        JP      Z,L305C ; {code.L305C}
303C: 35              DEC     (HL) ; {ram.M4358} $4358
303D: C0              RET     NZ
303E: 2D              DEC     L
303F: 34              INC     (HL) ; {ram.M4357} $4357
3040: 2E 50           LD      L,$50
3042: 36 04           LD      (HL),$04 ; {ram.M4350} set $4350
3044: 2E 53           LD      L,$53
3046: 36 10           LD      (HL),$10 ; {ram.M4353} set $4353
3048: 2C              INC     L
3049: 36 50           LD      (HL),$50 ; {ram.M4354} set $4354
304B: 2E 51           LD      L,$51
304D: 36 2E           LD      (HL),$2E ; {ram.M4351} set $4351
304F: 2C              INC     L
3050: 36 00           LD      (HL),$00 ; {ram.M4352} clear $4352
3052: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
3055: 0F              RRCA
3056: D8              RET     C
3057: 36 40           LD      (HL),$40 ; {ram.M4352} set $4352
3059: C9              RET
305A: FF              .DB $FF
305B: FF              .DB $FF
L305C:
305C: CD 74 30        CALL    L3074 ; {code.L3074}
305F: 21 57 43        LD      HL,M4357 ; {+ram.M4357}
3062: 7E              LD      A,(HL) ; {ram.M4357} get $4357
3063: 07              RLCA ; Multiply by 4 ..
3064: 07              RLCA ; ..
3065: 00              NOP
3066: 00              NOP
3067: 81              ADD     A,C
3068: C6 07           ADD     $07
306A: 2E 58           LD      L,$58
306C: 77              LD      (HL),A ; {ram.M4358} store to $4358
306D: C9              RET
306E: FF              .DB $FF
306F: FF              .DB $FF
3070: FF              .DB $FF
3071: FF              .DB $FF
3072: FF              .DB $FF
3073: FF              .DB $FF
L3074:
3074: 21 B8 43        LD      HL,LevelAndRound ; {+ram.LevelAndRound}
3077: 7E              LD      A,(HL)
3078: 0F              RRCA
3079: 00              NOP
307A: E6 07           AND     $07 ; 0000_0111
307C: 47              LD      B,A
307D: 3E 07           LD      A,$07
307F: 90              SUB     B
3080: 4F              LD      C,A
3081: 7E              LD      A,(HL) ; get LevelAndRound
3082: FE 80           CP      $80
3084: DA 89 30        JP      C,L3089 ; {code.L3089}
3087: 3E 70           LD      A,$70
L3089:
3089: 0F              RRCA
308A: 0F              RRCA
308B: 0F              RRCA
308C: 0F              RRCA
308D: E6 07           AND     $07 ; 0000_0111
308F: 47              LD      B,A
3090: 3E 07           LD      A,$07
3092: 90              SUB     B
3093: 81              ADD     A,C
3094: 4F              LD      C,A
3095: 3A BA 43        LD      A,(AliensLeft) ; {ram.AliensLeft}
3098: D6 05           SUB     $05
309A: D2 9F 30        JP      NC,L309F ; {code.L309F}
309D: 3E 10           LD      A,$10
L309F:
309F: 81              ADD     A,C
30A0: 4F              LD      C,A
30A1: CD AA 30        CALL    GetRandomNumber ; {code.GetRandomNumber}
30A4: E6 07           AND     $07 ; 0000_0111
30A6: 81              ADD     A,C
30A7: 4F              LD      C,A
30A8: C9              RET
30A9: FF              .DB $FF
GetRandomNumber:
30AA: 21 9B 43        LD      HL,Counter9A+$1 ; {+ram.Counter9A+1}
30AD: 7E              LD      A,(HL)
30AE: 07              RLCA ; Multiply by 8 ..
30AF: 07              RLCA ; ..
30B0: 07              RLCA ; ..
30B1: E6 07           AND     $07 ; mask out 0000_0111 in order to count from 0 to 7
30B3: 2E C2           LD      L,$C2 ; {ram.PlayerShipX} get $43C2 PlayerShipX
30B5: 86              ADD     A,(HL) ; add to counter value
30B6: E6 0F           AND     $0F ; mask out 0000_1111
30B8: C9              RET
30B9: C0              .DB $C0
L30BA:
30BA: 21 58 43        LD      HL,M4358 ; {+ram.M4358}
30BD: CD DA 30        CALL    L30DA ; {code.L30DA} {ram.M4359} for $4359
30C0: CD DA 30        CALL    L30DA ; {code.L30DA} {ram.M435A} for $435A
30C3: CD DA 30        CALL    L30DA ; {code.L30DA} {ram.M435B} for $435B
30C6: 2E 50           LD      L,$50
30C8: 7E              LD      A,(HL) ; {ram.M4350} get $4350
30C9: A7              AND     A ; updates the zero flag
30CA: C0              RET     NZ ; if <> 0
30CB: 2E 55           LD      L,$55
30CD: 7E              LD      A,(HL) ; {ram.M4355} get $4355
30CE: A7              AND     A ; updates the zero flag
30CF: CA E4 30        JP      Z,L30E4 ; {code.L30E4} if 0
30D2: 35              DEC     (HL)
30D3: C0              RET     NZ
30D4: 2E 50           LD      L,$50 ; {ram.M4350} $4350
30D6: 36 01           LD      (HL),$01
30D8: C9              RET
30D9: FE              .DB $FE
L30DA:
30DA: 2C              INC     L
30DB: 7E              LD      A,(HL)
30DC: A7              AND     A ; updates the zero flag
30DD: C8              RET     Z ; if 4359, 435A, 435B = 0
30DE: 35              DEC     (HL)
30DF: C9              RET
30E0: 7E              .DB $7E
30E1: FE              .DB $FE
30E2: 01              .DB $01
30E3: D0              .DB $D0
L30E4:
30E4: CD 74 30        CALL    L3074 ; {code.L3074}
30E7: 21 9A 43        LD      HL,Counter9A ; {+ram.Counter9A}
30EA: 7E              LD      A,(HL)
30EB: FE 10           CP      $10
30ED: DA F2 30        JP      C,L30F2 ; {code.L30F2}
30F0: 3E 0F           LD      A,$0F
L30F2:
30F2: 47              LD      B,A
30F3: 3E 0F           LD      A,$0F
30F5: 90              SUB     B
30F6: 81              ADD     A,C
30F7: 4F              LD      C,A
30F8: 06 01           LD      B,$01
30FA: 2E 58           LD      L,$58 ; {ram.M4358} $4358
30FC: CD 12 31        CALL    L3112 ; {code.L3112} {ram.M4359} for $4359
30FF: CD 12 31        CALL    L3112 ; {code.L3112} {ram.M435A} for $435A
3102: CD 12 31        CALL    L3112 ; {code.L3112} {ram.M435B} for $435B
3105: 79              LD      A,C
3106: 0F              RRCA
3107: 0F              RRCA
3108: E6 3F           AND     $3F ; 0011_1111
310A: C6 01           ADD     $01
310C: 2E 55           LD      L,$55
310E: 77              LD      (HL),A ; {ram.M4355} set $4355
310F: C9              RET
3110: 21              .DB $21
3111: 50              .DB $50
L3112:
3112: 2C              INC     L
3113: 7E              LD      A,(HL)
3114: A7              AND     A ; updates the zero flag
3115: C0              RET     NZ ; if <> 0
3116: 79              LD      A,C
3117: 0F              RRCA
3118: E6 7F           AND     $7F ; 0111_1111
311A: 4F              LD      C,A
311B: 78              LD      A,B
311C: A7              AND     A ; updates the zero flag
311D: C8              RET     Z
311E: 05              DEC     B
311F: 36 0C           LD      (HL),$0C
3121: C9              RET
3122: 86              .DB $86
3123: 47              .DB $47
L3124:
3124: 21 50 43        LD      HL,M4350 ; {+ram.M4350}
3127: 7E              LD      A,(HL)
3128: FE 01           CP      $01
312A: C0              RET     NZ ; if <> 1
312B: 36 02           LD      (HL),$02 ; {ram.M4350} set $4350
312D: 2E B8           LD      L,$B8
312F: 7E              LD      A,(HL) ; get LevelAndRound
3130: 0F              RRCA
3131: 0F              RRCA
3132: E6 0F           AND     $0F ; 0000_1111
3134: C6 05           ADD     $05
3136: FE 11           CP      $11
3138: DA 3D 31        JP      C,L313D ; {code.L313D}
313B: 3E 05           LD      A,$05
L313D:
313D: 2E 57           LD      L,$57 ; {ram.M4357} $4357
313F: 96              SUB     (HL)
3140: 47              LD      B,A
3141: CD AA 30        CALL    GetRandomNumber ; {code.GetRandomNumber}
3144: 3C              INC     A
3145: B8              CP      B
3146: DA 4B 31        JP      C,L314B ; {code.L314B}
3149: 3E 01           LD      A,$01
L314B:
314B: 2E 53           LD      L,$53 ; {ram.M4353} $4353
314D: 77              LD      (HL),A
314E: C9              RET
314F: 0A              .DB $0A
3150: 0C              .DB $0C
3151: 0B              .DB $0B
3152: 0C              .DB $0C
3153: 0B              .DB $0B
3154: 0E              .DB $0E
3155: 0F              .DB $0F
3156: 0E              .DB $0E
3157: 0F              .DB $0F
3158: FF              .DB $FF
3159: FF              .DB $FF
L315A:
315A: 21 50 43        LD      HL,M4350 ; {+ram.M4350}
315D: 7E              LD      A,(HL)
315E: FE 02           CP      $02
3160: C0              RET     NZ ; if <> 2
3161: CD AA 30        CALL    GetRandomNumber ; {code.GetRandomNumber}
3164: 00              NOP
3165: 47              LD      B,A
3166: 07              RLCA ; Multiply by 2
3167: C6 50           ADD     $50
3169: 6F              LD      L,A
316A: 26 4B           LD      H,$4B
316C: 78              LD      A,B
316D: 07              RLCA ; Multiply by 4 ..
316E: 07              RLCA
316F: C6 70           ADD     $70
3171: 5F              LD      E,A
3172: 16 4B           LD      D,$4B
3174: 0E 10           LD      C,$10
3176: 79              LD      A,C
3177: 90              SUB     B
3178: 47              LD      B,A
L3179:
3179: CD 92 31        CALL    L3192 ; {code.L3192}
317C: 13              INC     DE
317D: 13              INC     DE
317E: 13              INC     DE
317F: 13              INC     DE
3180: 23              INC     HL
3181: 23              INC     HL
3182: 05              DEC     B
3183: C2 8A 31        JP      NZ,L318A ; {code.L318A}
3186: 1E 70           LD      E,$70
3188: 2E 50           LD      L,$50 ; {ram.M4350} $4350
L318A:
318A: 0D              DEC     C
318B: C2 79 31        JP      NZ,L3179 ; {code.L3179}
318E: C9              RET
318F: FF              .DB $FF
3190: FF              .DB $FF
3191: FF              .DB $FF
L3192:
3192: 1A              LD      A,(DE)
3193: E6 08           AND     $08 ; 0000_1000
3195: C8              RET     Z
3196: 3A 94 43        LD      A,(M4394) ; {ram.M4394} get start value list pointer for alien movement MSB
3199: BE              CP      (HL)
319A: C0              RET     NZ
319B: 3A 56 43        LD      A,(M4356) ; {ram.M4356}
319E: 2C              INC     L
319F: 46              LD      B,(HL)
31A0: 2D              DEC     L
31A1: B8              CP      B
31A2: C0              RET     NZ
31A3: 7D              LD      A,L
31A4: 32 54 43        LD      (M4354),A ; {ram.M4354}
31A7: 3E 03           LD      A,$03
31A9: 32 50 43        LD      (M4350),A ; {ram.M4350}
31AC: E1              POP     HL
31AD: C9              RET
31AE: FF              .DB $FF
31AF: FF              .DB $FF
31B0: FF              .DB $FF
31B1: FF              .DB $FF
31B2: FF              .DB $FF
31B3: FF              .DB $FF
L31B4:
31B4: 3A 50 43        LD      A,(M4350) ; {ram.M4350}
31B7: FE 03           CP      $03
31B9: C0              RET     NZ ; if <> 3
31BA: 3A 54 43        LD      A,(M4354) ; {ram.M4354}
31BD: D6 50           SUB     $50
31BF: 07              RLCA ; Multiply by 2
31C0: C6 72           ADD     $72
31C2: 6F              LD      L,A
31C3: 26 4B           LD      H,$4B
31C5: 46              LD      B,(HL)
31C6: 2C              INC     L
31C7: 56              LD      D,(HL)
31C8: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
31CB: 0E 04           LD      C,$04
31CD: B8              CP      B
31CE: D2 D6 31        JP      NC,L31D6 ; {code.L31D6}
31D1: 4F              LD      C,A
31D2: 78              LD      A,B
31D3: 41              LD      B,C
31D4: 0E 00           LD      C,$00
L31D6:
31D6: 90              SUB     B
31D7: 07              RLCA ; Multiply by 8 ..
31D8: 07              RLCA ; ..
31D9: 07              RLCA ; ..
31DA: E6 07           AND     $07 ; 0000_0111
31DC: C6 00           ADD     $00 ; LSB for table T3300
31DE: 6F              LD      L,A
31DF: 26 33           LD      H,$33 ; get MSB for table T3300
31E1: 7E              LD      A,(HL)
31E2: 81              ADD     A,C
31E3: 07              RLCA ; Multiply by 4 ..
31E4: 07              RLCA ; ..
31E5: 4F              LD      C,A
31E6: 00              NOP
31E7: 00              NOP
31E8: 00              NOP
31E9: 3A 57 43        LD      A,(M4357) ; {ram.M4357}
31EC: 47              LD      B,A
31ED: CD 10 32        CALL    L3210 ; {code.L3210}
31F0: 79              LD      A,C
31F1: 80              ADD     A,B
31F2: C6 10           ADD     $10 ; LSB for table T3310
31F4: 6F              LD      L,A
31F5: 26 33           LD      H,$33 ; get MSB for table T3310
31F7: 4E              LD      C,(HL)
31F8: CD AA 30        CALL    GetRandomNumber ; {code.GetRandomNumber}
31FB: E6 06           AND     $06 ; 0000_0110
31FD: 81              ADD     A,C
31FE: 6F              LD      L,A
31FF: 26 33           LD      H,$33 ; get MSB for table T3330 (base adresses of closed loops pattern tables for aliens)
3201: 7E              LD      A,(HL)
3202: 2C              INC     L
3203: 46              LD      B,(HL)
3204: 21 50 43        LD      HL,M4350 ; {+ram.M4350}
3207: 36 05           LD      (HL),$05
3209: 2C              INC     L
320A: 77              LD      (HL),A
320B: 2C              INC     L
320C: 70              LD      (HL),B
320D: C9              RET
320E: 81              .DB $81
320F: 6F              .DB $6F
L3210:
3210: 3A 53 43        LD      A,(M4353) ; {ram.M4353}
3213: FE 01           CP      $01
3215: C0              RET     NZ ; if <> 1
3216: 7A              LD      A,D
3217: 06 00           LD      B,$00
3219: FE 58           CP      $58
321B: D8              RET     C
321C: 06 01           LD      B,$01
321E: FE 78           CP      $78
3220: D8              RET     C
3221: 06 02           LD      B,$02
3223: FE 98           CP      $98
3225: D8              RET     C
3226: 06 03           LD      B,$03
3228: C9              RET
3229: C0              .DB $C0
322A: 21              .DB $21
322B: 50              .DB $50
L322C:
322C: 3A 50 43        LD      A,(M4350) ; {ram.M4350}
322F: FE 04           CP      $04
3231: C0              RET     NZ ; if <> 4
3232: 21 50 4B        LD      HL,M4B50 ; {+ram.M4B50} Pointer to alien movement pattern
3235: 11 70 4B        LD      DE,M4B70 ; {+ram.M4B70} Alien data structure (grid)
3238: 3A 56 43        LD      A,(M4356) ; {ram.M4356}
323B: 4F              LD      C,A
323C: 3A 94 43        LD      A,(M4394) ; {ram.M4394} get start value list pointer for alien movement MSB
323F: 47              LD      B,A
L3240:
3240: 1A              LD      A,(DE)
3241: E6 08           AND     $08 ; 0000_1000
3243: CA 4E 32        JP      Z,L324E ; {code.L324E}
3246: 7E              LD      A,(HL)
3247: B8              CP      B
3248: C0              RET     NZ
3249: 2C              INC     L
324A: 7E              LD      A,(HL)
324B: 2D              DEC     L
324C: B9              CP      C
324D: C0              RET     NZ
L324E:
324E: 2C              INC     L
324F: 2C              INC     L
3250: 7B              LD      A,E
3251: C6 04           ADD     $04
3253: 5F              LD      E,A
3254: FE B0           CP      $B0
3256: C2 40 32        JP      NZ,L3240 ; {code.L3240}
3259: 3E 06           LD      A,$06
325B: 32 50 43        LD      (M4350),A ; {ram.M4350}
325E: C9              RET
325F: 3C              .DB $3C
3260: E6              .DB $E6
3261: 0F              .DB $0F
3262: 77              .DB $77
3263: 2E              .DB $2E
L3264:
3264: 21 95 43        LD      HL,M4395 ; {+ram.M4395}
3267: 7E              LD      A,(HL) ; get start value list pointer for alien movement LSB
3268: 32 56 43        LD      (M4356),A ; {ram.M4356}
326B: 3C              INC     A
326C: E6 0F           AND     $0F ; 0000_1111
326E: 77              LD      (HL),A
326F: 2E 50           LD      L,$50
3271: 7E              LD      A,(HL) ; {ram.M4350} get $4350
3272: FE 05           CP      $05
3274: D8              RET     C ; if < 5
3275: 36 00           LD      (HL),$00 ; {ram.M4350} clear $4350
3277: 2E 53           LD      L,$53
3279: 4E              LD      C,(HL) ; {ram.M4353} get $4353
327A: 2C              INC     L
327B: 6E              LD      L,(HL) ; {ram.M4354} get $4354
327C: 26 4B           LD      H,$4B
327E: 3A 56 43        LD      A,(M4356) ; {ram.M4356}
3281: 57              LD      D,A
3282: 3A 94 43        LD      A,(M4394) ; {ram.M4394} get start value list pointer for alien movement MSB
3285: 5F              LD      E,A
3286: 7D              LD      A,L
3287: D6 50           SUB     $50
3289: 0F              RRCA
328A: 47              LD      B,A
328B: 3E 10           LD      A,$10
328D: 90              SUB     B
328E: 47              LD      B,A
L328F:
328F: 7E              LD      A,(HL)
3290: 2C              INC     L
3291: BB              CP      E
3292: C2 A4 32        JP      NZ,L32A4 ; {code.L32A4}
3295: 7E              LD      A,(HL)
3296: BA              CP      D
3297: C2 A4 32        JP      NZ,L32A4 ; {code.L32A4}
329A: 2D              DEC     L
329B: 3A 51 43        LD      A,(M4351) ; {ram.M4351}
329E: 77              LD      (HL),A
329F: 2C              INC     L
32A0: 3A 52 43        LD      A,(M4352) ; {ram.M4352}
32A3: 77              LD      (HL),A
L32A4:
32A4: 2C              INC     L
32A5: 05              DEC     B
32A6: C2 AB 32        JP      NZ,L32AB ; {code.L32AB}
32A9: 2E 50           LD      L,$50 ; {ram.M4350} $4350
L32AB:
32AB: 0D              DEC     C
32AC: C2 8F 32        JP      NZ,L328F ; {code.L328F}
32AF: C9              RET
L32B0:
32B0: 21 50 43        LD      HL,M4350 ; {+ram.M4350}
32B3: 06 30           LD      B,$30 ; 4350 to 437F
32B5: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
32B8: 2E 9A           LD      L,$9A ; Counter9A
32BA: 06 04           LD      B,$04 ; 439A to 439D
32BC: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
32BF: 3A BB 43        LD      A,(BirdsLeft) ; {ram.BirdsLeft}
32C2: A7              AND     A ; updates the zero flag
32C3: C8              RET     Z ; if no BirdsLeft
32C4: 07              RLCA ; Multiply by 8 ..
32C5: 07              RLCA ; ..
32C6: 07              RLCA ; ..
32C7: 4F              LD      C,A
32C8: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
32CB: 06 40           LD      B,$40
32CD: CD D8 05        CALL    ClearBbytesAtHL ; {code.ClearBbytesAtHL}
32D0: 16 4B           LD      D,$4B
32D2: 26 3F           LD      H,$3F
32D4: 3E 40           LD      A,$40
32D6: 91              SUB     C
32D7: C6 70           ADD     $70
32D9: 5F              LD      E,A
32DA: C6 10           ADD     $10
32DC: 6F              LD      L,A
32DD: 41              LD      B,C
32DE: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
32E1: 0F              RRCA
32E2: 0F              RRCA
32E3: D2 E0 05        JP      NC,CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
32E6: 7D              LD      A,L
32E7: C6 40           ADD     $40
32E9: 6F              LD      L,A
32EA: C3 E0 05        JP      CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
32ED: CD              .DB $CD ; {code.CopyBbytesHLtoDE}
32EE: E0              .DB $E0
32EF: 05              .DB $05
32F0: C3              .DB $C3 ; {code.ClearBackground}
32F1: A0              .DB $A0
32F2: 03              .DB $03
32F3: FF              .DB $FF
32F4: FF              .DB $FF
32F5: FF              .DB $FF
32F6: FF              .DB $FF
32F7: FF              .DB $FF
32F8: FF              .DB $FF
32F9: FF              .DB $FF
32FA: FF              .DB $FF
32FB: FF              .DB $FF
32FC: FF              .DB $FF
32FD: FF              .DB $FF
32FE: FF              .DB $FF
32FF: FF              .DB $FF
T3300:
3300: 00 01 02 02     .DB $00, $01, $02, $02, $03, $03, $03, $03
3304: 03 03 03 03
3308: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
330C: FF FF FF FF
T3310:
3310: 88 90 98 A0     .DB $88, $90, $98, $A0, $68, $70, $78, $80, $48, $50, $58, $60, $48, $30, $38, $40
3314: 68 70 78 80
3318: 48 50 58 60
331C: 48 30 38 40
3320: 88 90 98 A0     .DB $88, $90, $98, $A0, $A8, $B0, $B8, $C0, $C8, $D0, $D8, $E0, $C8, $E8, $F0, $F8
3324: A8 B0 B8 C0
3328: C8 D0 D8 E0
332C: C8 E8 F0 F8
T3330:
3330: 11 30 2C 00     .DW T1130, T2C00, T2FA0, T2C00, T2EC4, T2FA0, T2F34, T2FA0
3334: 2F A0 2C 00
3338: 2E C4 2F A0
333C: 2F 34 2F A0
3340: 2C C8 2E C4     .DW T2CC8, T2EC4, T2E20, T2EC4, T1130, T139C, T13D0, T2C00
3344: 2E 20 2E C4
3348: 11 30 13 9C
334C: 13 D0 2C 00
3350: 11 30 13 28     .DW T1130, T1328, T2C00, T2F34, T11A4, T2C90, T2F34, T2FA0
3354: 2C 00 2F 34
3358: 11 A4 2C 90
335C: 2F 34 2F A0
3360: 2C 90 2C C8     .DW T2C90, T2CC8, T2E20, T2EC4, T1160, T1354, T139C, T13D0
3364: 2E 20 2E C4
3368: 11 60 13 54
336C: 13 9C 13 D0
3370: 10 20 10 64     .DW T1020, T1064, T11A4, T1328, T1020, T11A4, T1200, T2F34
3374: 11 A4 13 28
3378: 10 20 11 A4
337C: 12 00 2F 34
3380: 2C 90 2C C8     .DW T2C90, T2CC8, T2DC0, T2E20, T1160, T1244, T1288, T1354
3384: 2D C0 2E 20
3388: 11 60 12 44
338C: 12 88 13 54
3390: 10 20 10 64     .DW T1020, T1064, T1200, T1244, T1020, T1200, T1020, T1200
3394: 12 00 12 44
3398: 10 20 12 00
339C: 10 20 12 00
33A0: 10 A8 2D 88     .DW T10A8, T2D88, T10A8, T2DC0, T11D0, T12CA, T1300, T1354
33A4: 10 A8 2D C0
33A8: 11 D0 12 CA
33AC: 13 00 13 54
33B0: 10 20 10 64     .DW T1020, T1064, T10D4, T1300, T1020, T10D4, T1200, T2F00
33B4: 10 D4 13 00
33B8: 10 20 10 D4
33BC: 12 00 2F 00
33C0: 2D 00 2D 44     .DW T2D00, T2D44, T2D88, T2E6C, T1100, T11D0, T12CA, T2F64
33C4: 2D 88 2E 6C
33C8: 11 00 11 D0
33CC: 12 CA 2F 64
33D0: 11 00 13 00     .DW T1100, T1300, T2F64, T2F00, T10D4, T2D00, T2F00, T2C34
33D4: 2F 64 2F 00
33D8: 10 D4 2D 00
33DC: 2F 00 2C 34
33E0: 2D 00 2D 44     .DW T2D00, T2D44, T2E6C, T2E90, T1100, T2C34, T2F64, T2F64
33E4: 2E 6C 2E 90
33E8: 11 00 2C 34
33EC: 2F 64 2F 64
33F0: 2E 90 2F 00     .DW T2E90, T2F00, T2C34, T2C34, T2D44, T2E6C, T2E90, T2E90
33F4: 2C 34 2C 34
33F8: 2D 44 2E 6C
33FC: 2E 90 2E 90
L3400:
3400: CD 76 08        CALL    PlayerUpdate ; {code.PlayerUpdate} Updates the player ship, player bullet and the shield.
3403: CD 00 38        CALL    L3800 ; {code.L3800} Collision detection for birds
3406: CD 00 26        CALL    L2600 ; {code.L2600} birds vertical movement update (with 58xx scroll register)
3409: CD 00 38        CALL    L3800 ; {code.L3800} Collision detection for birds
340C: CD 80 39        CALL    L3980 ; {code.L3980}
340F: 3A BB 43        LD      A,(BirdsLeft) ; {ram.BirdsLeft}
3412: A7              AND     A ; updates the zero flag
3413: CA 62 34        JP      Z,L3462 ; {+code.L3462} if no BirdsLeft.
3416: FE 04           CP      $04
3418: D2 38 34        JP      NC,L3438 ; {+code.L3438} if >= $04
341B: CD 74 34        CALL    DrawFirst4BirdObjects ; {code.DrawFirst4BirdObjects} including the horizontal movement update
341E: CD 86 34        CALL    DrawSecond4BirdObjects ; {code.DrawSecond4BirdObjects} including the horizontal movement update
3421: CD 60 35        CALL    L3560 ; {code.L3560}
3424: CD 98 34        CALL    L3498 ; {code.L3498}
3427: CD AA 34        CALL    L34AA ; {code.L34AA}
342A: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
342D: 0F              RRCA
342E: DA C0 0F        JP      C,L0FC0 ; {code.L0FC0} Handle animations for killed aliens
3431: CD 30 39        CALL    L3930 ; {code.L3930}
3434: C3 40 0C        JP      L0C40 ; {code.EnemyBulletUpdate}
3437: FF              .DB $FF
L3438:
3438: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
343B: 0F              RRCA
343C: DA 52 34        JP      C,L3452 ; {+code.L3452}
343F: CD 74 34        CALL    DrawFirst4BirdObjects ; {code.DrawFirst4BirdObjects}
3442: CD 60 35        CALL    L3560 ; {code.L3560}
3445: CD 98 34        CALL    L3498 ; {code.L3498}
3448: CD 30 39        CALL    L3930 ; {code.L3930}
344B: C3 40 0C        JP      L0C40 ; {code.EnemyBulletUpdate}
344E: FF              .DB $FF
344F: FF              .DB $FF
3450: FF              .DB $FF
3451: FF              .DB $FF
L3452:
3452: CD 86 34        CALL    DrawSecond4BirdObjects ; {code.DrawSecond4BirdObjects}
3455: CD 60 35        CALL    L3560 ; {code.L3560}
3458: CD AA 34        CALL    L34AA ; {code.L34AA}
345B: C3 C0 0F        JP      L0FC0 ; {code.L0FC0} Handle animations for killed aliens
345E: FF              .DB $FF
345F: FF              .DB $FF
3460: FF              .DB $FF
3461: FF              .DB $FF
L3462:
3462: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
3465: 0F              RRCA
3466: D8              RET     C
3467: CD 40 0C        CALL    L0C40 ; {code.EnemyBulletUpdate}
346A: CD C0 0F        CALL    L0FC0 ; {code.L0FC0} Handle animations for killed aliens
346D: C3 04 22        JP      L2204 ; {code.L2204}
3470: FF              .DB $FF
3471: FF              .DB $FF
3472: FF              .DB $FF
3473: FF              .DB $FF
DrawFirst4BirdObjects:
3474: 21 70 4B        LD      HL,B4B70 ; {!+ram.B4B70}
L3477:
3477: E5              PUSH    HL
3478: CD C0 34        CALL    DrawBirdObject ; {code.DrawBirdObject}
347B: E1              POP     HL
347C: 7D              LD      A,L
347D: C6 08           ADD     $08 ; go to next bird object
347F: 6F              LD      L,A
3480: FE 90           CP      $90 ; for bird0 to bird3
3482: C2 77 34        JP      NZ,L3477 ; {+code.L3477}
3485: C9              RET
DrawSecond4BirdObjects:
3486: 21 90 4B        LD      HL,B4B90 ; {!+ram.B4B90}
L3489:
3489: E5              PUSH    HL
348A: CD C0 34        CALL    DrawBirdObject ; {code.DrawBirdObject}
348D: E1              POP     HL
348E: 7D              LD      A,L
348F: C6 08           ADD     $08 ; go to next bird object
3491: 6F              LD      L,A
3492: FE B0           CP      $B0 ; for bird4 to bird7
3494: C2 89 34        JP      NZ,L3489 ; {+code.L3489}
3497: C9              RET
L3498:
3498: 21 70 4B        LD      HL,B4B70 ; {!+ram.B4B70}
L349B:
349B: E5              PUSH    HL
349C: CD B0 35        CALL    L35B0 ; {code.L35B0}
349F: E1              POP     HL
34A0: 7D              LD      A,L
34A1: C6 08           ADD     $08 ; go to next bird object
34A3: 6F              LD      L,A
34A4: FE 90           CP      $90 ; for bird 0 to bird3
34A6: C2 9B 34        JP      NZ,L349B ; {+code.L349B}
34A9: C9              RET
L34AA:
34AA: 21 90 4B        LD      HL,B4B90 ; {!+ram.B4B90}
L34AD:
34AD: E5              PUSH    HL
34AE: CD B0 35        CALL    L35B0 ; {code.L35B0}
34B1: E1              POP     HL
34B2: 7D              LD      A,L
34B3: C6 08           ADD     $08 ; go to next bird object
34B5: 6F              LD      L,A
34B6: FE B0           CP      $B0 ; for bird4 to bird7
34B8: C2 AD 34        JP      NZ,L34AD ; {+code.L34AD}
34BB: C9              RET
34BC: FF              .DB $FF
34BD: FF              .DB $FF
34BE: FF              .DB $FF
34BF: FF              .DB $FF
DrawBirdObject:
34C0: 7E              LD      A,(HL) ; {ram.B4B70} {ram.B4B78} HL=$4B70 (or $4B78,...)
34C1: A7              AND     A ; updates the zero flag
34C2: C8              RET     Z ; if 0
34C3: 47              LD      B,A ; save it
34C4: C6 C0           ADD     $C0 ; add to base for table T3EC0
34C6: 5F              LD      E,A ; save it
34C7: 16 3E           LD      D,$3E ; MSB for T3EC0
34C9: 1A              LD      A,(DE) ; get data starting from $3EC1
34CA: 4F              LD      C,A
34CB: 2C              INC     L
34CC: 56              LD      D,(HL) ; {ram.B4B71} get $4B71 MSB of screen ram
34CD: 2C              INC     L
34CE: 5E              LD      E,(HL) ; {ram.B4B72} get $4B72 LSB of screen ram
34CF: 2C              INC     L
34D0: 78              LD      A,B ; restore it
34D1: 07              RLCA ; Multiply by 8 ..
34D2: 07              RLCA ; ..
34D3: 07              RLCA ; ..
34D4: 86              ADD     A,(HL) ; {ram.B4B73} and add to $4B73 alien0 screen coordinate Y
34D5: E6 7E           AND     $7E ; mask out 0111_1110
34D7: 6F              LD      L,A
34D8: 26 3E           LD      H,$3E
34DA: 7E              LD      A,(HL) ; get MSB from address table for bird character block shapes (T3E08)
34DB: 2C              INC     L
34DC: 6E              LD      L,(HL) ; get LSB
34DD: 67              LD      H,A
L34DE:
34DE: 7A              LD      A,D
34DF: FE 4B           CP      $4B ; MSB of screen ram
34E1: C2 0C 35        JP      NZ,L350C ; {+code.L350C} if value is not equal $4B
34E4: 7B              LD      A,E
34E5: FE 50           CP      $50
34E7: DA 0C 35        JP      C,L350C ; {+code.L350C}
34EA: 06 08           LD      B,$08
34EC: 2C              INC     L
34ED: 2C              INC     L
34EE: D6 20           SUB     $20
34F0: 5F              LD      E,A
34F1: FE 50           CP      $50
34F3: DA 09 35        JP      C,L3509 ; {+code.L3509}
34F6: 06 10           LD      B,$10
34F8: 2C              INC     L
34F9: 2C              INC     L
34FA: D6 20           SUB     $20
34FC: 5F              LD      E,A
34FD: FE 50           CP      $50
34FF: DA 09 35        JP      C,L3509 ; {+code.L3509}
3502: 06 18           LD      B,$18
3504: 2C              INC     L
3505: 2C              INC     L
3506: D6 20           SUB     $20
3508: 5F              LD      E,A
L3509:
3509: 79              LD      A,C
350A: 80              ADD     A,B
350B: 4F              LD      C,A
L350C:
350C: 06 35           LD      B,$35 ; MSB of return address for the draw shape entry.
350E: C5              PUSH    BC
350F: 01 DF FF        LD      BC,$FFDF ; Screen offset constant -33 right one column (-1), up one row (-32)
3512: EB              EX      DE,HL
3513: 36 00           LD      (HL),$00 ; delete character on screen
3515: 23              INC     HL
3516: 36 00           LD      (HL),$00 ; delete character on screen
3518: 09              ADD     HL,BC
3519: C9              RET ; jumps to draw shape entry.
351A: FF              .DB $FF
351B: FF              .DB $FF
351C: FF              .DB $FF
351D: FF              .DB $FF
351E: FF              .DB $FF
351F: FF              .DB $FF
Draw7x2:
3520: 1A              LD      A,(DE)
3521: 77              LD      (HL),A
3522: 13              INC     DE
3523: 23              INC     HL
3524: 1A              LD      A,(DE)
3525: 77              LD      (HL),A
3526: 13              INC     DE
3527: 09              ADD     HL,BC
Draw6x2:
3528: 1A              LD      A,(DE)
3529: 77              LD      (HL),A
352A: 13              INC     DE
352B: 23              INC     HL
352C: 1A              LD      A,(DE)
352D: 77              LD      (HL),A
352E: 13              INC     DE
352F: 09              ADD     HL,BC
Draw5x2:
3530: 1A              LD      A,(DE)
3531: 77              LD      (HL),A
3532: 13              INC     DE
3533: 23              INC     HL
3534: 1A              LD      A,(DE)
3535: 77              LD      (HL),A
3536: 13              INC     DE
3537: 09              ADD     HL,BC
Draw4x2:
3538: 1A              LD      A,(DE)
3539: 77              LD      (HL),A
353A: 13              INC     DE
353B: 23              INC     HL
353C: 1A              LD      A,(DE)
353D: 77              LD      (HL),A
353E: 13              INC     DE
353F: 09              ADD     HL,BC
Draw3x2:
3540: 1A              LD      A,(DE)
3541: 77              LD      (HL),A
3542: 13              INC     DE
3543: 23              INC     HL
3544: 1A              LD      A,(DE)
3545: 77              LD      (HL),A
3546: 13              INC     DE
3547: 09              ADD     HL,BC
Draw2x2:
3548: 1A              LD      A,(DE)
3549: 77              LD      (HL),A
354A: 13              INC     DE
354B: 23              INC     HL
354C: 1A              LD      A,(DE)
354D: 77              LD      (HL),A
354E: 13              INC     DE
354F: 09              ADD     HL,BC
Draw1x2:
3550: 1A              LD      A,(DE)
3551: 77              LD      (HL),A
3552: 13              INC     DE
3553: 23              INC     HL
3554: 1A              LD      A,(DE)
3555: 77              LD      (HL),A
3556: 13              INC     DE
3557: 09              ADD     HL,BC
L3558:
3558: 36 00           LD      (HL),$00
355A: 23              INC     HL
355B: 36 00           LD      (HL),$00
355D: C9              RET
355E: FF              .DB $FF
355F: FF              .DB $FF
L3560:
3560: CD AA 30        CALL    GetRandomNumber ; {code.GetRandomNumber}
3563: 47              LD      B,A
3564: 07              RLCA ; Multiply by 4 ..
3565: 07              RLCA ; ..
3566: 4F              LD      C,A
3567: 07              RLCA ; Multiply by 4 ..
3568: 07              RLCA ; ..
3569: B0              OR      B
356A: 32 6F 43        LD      (M436F),A ; {ram.M436F}
356D: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
3570: FE 40           CP      $40
3572: DA 77 35        JP      C,L3577 ; {code.L3577} if game round < 4
3575: 3E 30           LD      A,$30
L3577:
3577: E6 30           AND     $30 ; 0011_0000
3579: 0F              RRCA
357A: 47              LD      B,A
357B: 3A BB 43        LD      A,(BirdsLeft) ; {ram.BirdsLeft}
357E: 3D              DEC     A
357F: FE 04           CP      $04
3581: DA 86 35        JP      C,L3586 ; {code.L3586}
3584: 3E 03           LD      A,$03
L3586:
3586: 07              RLCA ; Multiply by 2
3587: B0              OR      B
3588: 47              LD      B,A
3589: 3A 9A 43        LD      A,(Counter9A) ; {ram.Counter9A}
358C: 07              RLCA ; Multiply by 4 ..
358D: 07              RLCA ; ..
358E: E6 20           AND     $20 ; mask out 0010_0000
3590: B0              OR      B
3591: C6 80           ADD     $80
3593: 6F              LD      L,A
3594: 26 3E           LD      H,$3E
3596: 7E              LD      A,(HL) ; data from table T3E80
3597: 32 6E 43        LD      (M436E),A ; {ram.M436E}
359A: 2C              INC     L
359B: 7E              LD      A,(HL) ; data from table T3E80
359C: 81              ADD     A,C
359D: E6 F8           AND     $F8 ; 1111_1000
359F: 32 6D 43        LD      (M436D),A ; {ram.M436D}
35A2: C9              RET
35A3: FF              .DB $FF
35A4: FF              .DB $FF
35A5: FF              .DB $FF
35A6: FF              .DB $FF
35A7: FF              .DB $FF
35A8: FF              .DB $FF
35A9: FF              .DB $FF
35AA: FF              .DB $FF
35AB: FF              .DB $FF
35AC: FF              .DB $FF
35AD: FF              .DB $FF
35AE: FF              .DB $FF
35AF: FF              .DB $FF
L35B0:
35B0: 7E              LD      A,(HL) ; get index character block shape
35B1: A7              AND     A ; updates the zero flag
35B2: C8              RET     Z ; if index is 0
35B3: 47              LD      B,A ; save index to B
35B4: 2C              INC     L
35B5: 2C              INC     L
35B6: 2C              INC     L
35B7: 2C              INC     L
35B8: 7E              LD      A,(HL)
35B9: A7              AND     A ; updates the zero flag
35BA: CA BE 35        JP      Z,L35BE ; {code.L35BE}
35BD: 35              DEC     (HL)
L35BE:
35BE: EB              EX      DE,HL
35BF: D5              PUSH    DE
35C0: 78              LD      A,B ; load index
35C1: 07              RLCA ; Multiply by 8 ..
35C2: 07              RLCA ; ..
35C3: 07              RLCA ; ..
35C4: 6F              LD      L,A
35C5: 26 3F           LD      H,$3F ; MSB of table T3F00 for stack manipulation
35C7: 46              LD      B,(HL) ; get 1st byte
35C8: 23              INC     HL
35C9: 4E              LD      C,(HL) ; get 2nd byte
35CA: C5              PUSH    BC ; to stack
35CB: 23              INC     HL
35CC: 46              LD      B,(HL) ; get 3rd byte
35CD: 23              INC     HL
35CE: 4E              LD      C,(HL) ; get 4rd byte
35CF: C5              PUSH    BC ; to stack
35D0: 23              INC     HL
35D1: 46              LD      B,(HL) ; get MSB of 1st address
35D2: 23              INC     HL
35D3: 4E              LD      C,(HL) ; get LSB of 1st address
35D4: C5              PUSH    BC ; to stack
35D5: 23              INC     HL
35D6: 46              LD      B,(HL) ; get MSB of 2nd address
35D7: 23              INC     HL
35D8: 4E              LD      C,(HL) ; get LSB of 2nd address
35D9: C5              PUSH    BC ; to stack
35DA: EB              EX      DE,HL
35DB: C9              RET ; calls the 2nd address
35DC: FF              .DB $FF
35DD: FF              .DB $FF
35DE: FF              .DB $FF
35DF: FF              .DB $FF
L35E0:
35E0: 2C              INC     L
35E1: 2C              INC     L
35E2: 7E              LD      A,(HL)
35E3: FE 10           CP      $10
35E5: D2 28 36        JP      NC,L3628 ; {code.L3628} if >= $10
35E8: 47              LD      B,A
35E9: 2D              DEC     L
35EA: 86              ADD     A,(HL)
35EB: 77              LD      (HL),A
35EC: 2D              DEC     L
35ED: 2D              DEC     L
35EE: 78              LD      A,B
35EF: 86              ADD     A,(HL)
35F0: 77              LD      (HL),A
35F1: FE 08           CP      $08
35F3: DA 6A 36        JP      C,L366A ; {code.L366A}
35F6: E6 07           AND     $07 ; 0000_0111
35F8: 77              LD      (HL),A
35F9: 2D              DEC     L
35FA: 7E              LD      A,(HL)
35FB: D6 20           SUB     $20
35FD: 77              LD      (HL),A
35FE: D2 04 36        JP      NC,L3604 ; {code.L3604}
3601: 2D              DEC     L
3602: 35              DEC     (HL)
3603: 2C              INC     L
L3604:
3604: 2C              INC     L
3605: 2C              INC     L
3606: 2C              INC     L
3607: 4E              LD      C,(HL)
3608: 2C              INC     L
3609: 2C              INC     L
360A: 7E              LD      A,(HL)
360B: 2D              DEC     L
360C: 36 10           LD      (HL),$10
360E: 91              SUB     C
360F: CA 72 36        JP      Z,L3672 ; {code.L3672}
3612: 3D              DEC     A
3613: 0F              RRCA
3614: 0F              RRCA
3615: 0F              RRCA
3616: E6 1F           AND     $1F ; 0001_1111
3618: B8              CP      B
3619: 3C              INC     A
361A: 77              LD      (HL),A
361B: D8              RET     C
361C: 3A 6E 43        LD      A,(M436E) ; {ram.M436E}
361F: 77              LD      (HL),A
3620: B8              CP      B
3621: C8              RET     Z
3622: 04              INC     B
3623: 70              LD      (HL),B
3624: C9              RET
3625: FF              .DB $FF
3626: FF              .DB $FF
3627: FF              .DB $FF
L3628:
3628: E6 0F           AND     $0F ; 0000_1111
362A: CA 44 37        JP      Z,L3744 ; {code.L3744}
362D: 47              LD      B,A
362E: 2D              DEC     L
362F: 7E              LD      A,(HL)
3630: 90              SUB     B
3631: 77              LD      (HL),A
3632: 2D              DEC     L
3633: 2D              DEC     L
3634: 7E              LD      A,(HL)
3635: 90              SUB     B
3636: 77              LD      (HL),A
3637: D2 95 36        JP      NC,L3695 ; {code.L3695}
363A: E6 07           AND     $07 ; 0000_0111
363C: 77              LD      (HL),A
363D: 2D              DEC     L
363E: 7E              LD      A,(HL)
363F: C6 20           ADD     $20
3641: 77              LD      (HL),A
3642: D2 48 36        JP      NC,L3648 ; {code.L3648}
3645: 2D              DEC     L
3646: 34              INC     (HL)
3647: 2C              INC     L
L3648:
3648: 2C              INC     L
3649: 2C              INC     L
364A: 2C              INC     L
364B: 7E              LD      A,(HL)
364C: 2C              INC     L
364D: 2C              INC     L
364E: 96              SUB     (HL)
364F: 0F              RRCA
3650: 0F              RRCA
3651: 0F              RRCA
3652: E6 1F           AND     $1F ; 0001_1111
3654: B8              CP      B
3655: 3C              INC     A
3656: 2D              DEC     L
3657: DA 63 36        JP      C,L3663 ; {code.L3663}
365A: 3A 6E 43        LD      A,(M436E) ; {ram.M436E}
365D: B8              CP      B
365E: CA 63 36        JP      Z,L3663 ; {code.L3663}
3661: 78              LD      A,B
3662: 3C              INC     A
L3663:
3663: F6 10           OR      $10 ; 0001_0000
3665: 77              LD      (HL),A
3666: C9              RET
3667: 77              .DB $77
3668: C9              .DB $C9
3669: FF              .DB $FF
L366A:
366A: 78              LD      A,B
366B: A7              AND     A ; updates the zero flag
366C: C0              RET     NZ
366D: 2C              INC     L
366E: 2C              INC     L
366F: 2C              INC     L
3670: 34              INC     (HL)
3671: C9              RET
L3672:
3672: 2D              DEC     L
3673: 46              LD      B,(HL)
3674: 2C              INC     L
3675: 2C              INC     L
3676: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
3679: E6 F8           AND     $F8 ; 1111_1000
367B: B8              CP      B
367C: D2 80 36        JP      NC,L3680 ; {code.L3680}
367F: 47              LD      B,A
L3680:
3680: 3A 6D 43        LD      A,(M436D) ; {ram.M436D}
3683: 4F              LD      C,A
3684: C6 08           ADD     $08
3686: 32 6D 43        LD      (M436D),A ; {ram.M436D}
3689: 78              LD      A,B
368A: 91              SUB     C
368B: 36 08           LD      (HL),$08
368D: D8              RET     C
368E: FE 08           CP      $08
3690: D8              RET     C
3691: 77              LD      (HL),A
3692: C9              RET
3693: D8              .DB $D8
3694: FE              .DB $FE
L3695:
3695: 2C              INC     L
3696: 2C              INC     L
3697: 46              LD      B,(HL)
3698: 2C              INC     L
3699: 2C              INC     L
369A: 7E              LD      A,(HL)
369B: B8              CP      B
369C: C0              RET     NZ
369D: 2D              DEC     L
369E: 36 00           LD      (HL),$00
36A0: 2C              INC     L
36A1: 3A C2 43        LD      A,(PlayerShipX) ; {ram.PlayerShipX}
36A4: E6 F8           AND     $F8 ; 1111_1000
36A6: B8              CP      B
36A7: DA AB 36        JP      C,L36AB ; {code.L36AB}
36AA: 47              LD      B,A
L36AB:
36AB: 3A 6D 43        LD      A,(M436D) ; {ram.M436D}
36AE: C6 08           ADD     $08
36B0: 32 6D 43        LD      (M436D),A ; {ram.M436D}
36B3: 80              ADD     A,B
36B4: 36 C8           LD      (HL),$C8
36B6: D8              RET     C
36B7: FE C8           CP      $C8
36B9: D0              RET     NC
36BA: 77              LD      (HL),A
36BB: C9              RET
36BC: 77              .DB $77
36BD: C9              .DB $C9
36BE: FF              .DB $FF
36BF: FF              .DB $FF
L36C0:
36C0: 7E              LD      A,(HL)
36C1: 0F              RRCA
36C2: D8              RET     C
36C3: 2D              DEC     L
36C4: 7E              LD      A,(HL)
36C5: 3C              INC     A
36C6: E6 07           AND     $07 ; 0000_0111
36C8: 77              LD      (HL),A
36C9: C9              RET
36CA: FF              .DB $FF
36CB: FF              .DB $FF
L36CC:
36CC: D1              POP     DE
36CD: C1              POP     BC
36CE: E1              POP     HL
36CF: C9              RET
36D0: FF              .DB $FF
36D1: FF              .DB $FF
L36D2:
36D2: D1              POP     DE
36D3: C1              POP     BC
36D4: E1              POP     HL
36D5: 7E              LD      A,(HL)
36D6: A7              AND     A ; updates the zero flag
36D7: C0              RET     NZ
36D8: 70              LD      (HL),B
36D9: 2D              DEC     L
36DA: 2D              DEC     L
36DB: 2D              DEC     L
36DC: 2D              DEC     L
36DD: 72              LD      (HL),D
36DE: 3A 68 43        LD      A,(M4368) ; {ram.M4368}
36E1: F6 01           OR      $01 ; 0000_0001
36E3: 32 68 43        LD      (M4368),A ; {ram.M4368}
36E6: C9              RET
36E7: FF              .DB $FF
36E8: FF              .DB $FF
36E9: FF              .DB $FF
L36EA:
36EA: D1              POP     DE
36EB: C1              POP     BC
36EC: E1              POP     HL
36ED: 7E              LD      A,(HL)
36EE: A7              AND     A ; updates the zero flag
36EF: C0              RET     NZ
36F0: 2C              INC     L
36F1: 2C              INC     L
36F2: 7E              LD      A,(HL)
36F3: E6 0F           AND     $0F ; 0000_1111
36F5: C0              RET     NZ
36F6: 2D              DEC     L
36F7: 2D              DEC     L
36F8: 70              LD      (HL),B
36F9: 2D              DEC     L
36FA: 2D              DEC     L
36FB: 2D              DEC     L
36FC: 2D              DEC     L
36FD: 72              LD      (HL),D
36FE: 3A 68 43        LD      A,(M4368) ; {ram.M4368}
3701: F6 02           OR      $02 ; 0000_0010
3703: 32 68 43        LD      (M4368),A ; {ram.M4368}
3706: C9              RET
3707: FF              .DB $FF
3708: FF              .DB $FF
3709: FF              .DB $FF
L370A:
370A: D1              POP     DE
370B: C1              POP     BC
370C: E1              POP     HL
370D: 7E              LD      A,(HL)
370E: A7              AND     A ; updates the zero flag
370F: C0              RET     NZ
3710: 2C              INC     L
3711: 2C              INC     L
3712: 7E              LD      A,(HL)
3713: E6 0F           AND     $0F ; 0000_1111
3715: C0              RET     NZ
3716: 2D              DEC     L
3717: 2D              DEC     L
3718: 70              LD      (HL),B
3719: 2D              DEC     L
371A: 2D              DEC     L
371B: 2D              DEC     L
371C: 2D              DEC     L
371D: 72              LD      (HL),D
371E: 3A 68 43        LD      A,(M4368) ; {ram.M4368}
3721: F6 04           OR      $04 ; 0000_0100
3723: 32 68 43        LD      (M4368),A ; {ram.M4368}
3726: 3A 6F 43        LD      A,(M436F) ; {ram.M436F}
3729: A3              AND     E
372A: E6 F0           AND     $F0 ; 1111_0000
372C: C0              RET     NZ
372D: 7B              LD      A,E
372E: E6 0F           AND     $0F ; 0000_1111
3730: 77              LD      (HL),A
3731: 2C              INC     L
3732: 2C              INC     L
3733: 2C              INC     L
3734: 2C              INC     L
3735: 71              LD      (HL),C
3736: 3A 68 43        LD      A,(M4368) ; {ram.M4368}
3739: F6 08           OR      $08 ; 0000_1000
373B: 32 68 43        LD      (M4368),A ; {ram.M4368}
373E: C9              RET
373F: FF              .DB $FF
3740: FF              .DB $FF
3741: FF              .DB $FF
3742: FF              .DB $FF
3743: FF              .DB $FF
L3744:
3744: 36 11           LD      (HL),$11
3746: 2D              DEC     L
3747: 35              DEC     (HL)
3748: 2D              DEC     L
3749: 2D              DEC     L
374A: 36 07           LD      (HL),$07
374C: 2D              DEC     L
374D: 7E              LD      A,(HL)
374E: C6 20           ADD     $20
3750: 77              LD      (HL),A
3751: D0              RET     NC
3752: 2D              DEC     L
3753: 34              INC     (HL)
3754: C9              RET
3755: FF              .DB $FF
3756: FF              .DB $FF
3757: FF              .DB $FF
L3758:
3758: 7E              LD      A,(HL)
3759: A7              AND     A ; updates the zero flag
375A: C8              RET     Z ; if 0
375B: 35              DEC     (HL)
375C: CA CC 37        JP      Z,L37CC ; {code.L37CC}
375F: 7E              LD      A,(HL)
3760: 0F              RRCA
3761: D2 B0 37        JP      NC,L37B0 ; {code.L37B0} Prints the score value in the middle of the bonus explosion
3764: 3E 0F           LD      A,$0F
3766: 96              SUB     (HL)
3767: E6 0E           AND     $0E ; mask out 0000_1110
3769: 07              RLCA ; Multiply by 16 ..
376A: 07              RLCA ; ..
376B: 07              RLCA ; ..
376C: 07              RLCA ; ..
376D: 2C              INC     L
376E: 2C              INC     L
376F: 56              LD      D,(HL)
3770: 2C              INC     L
3771: 5E              LD      E,(HL)
3772: F5              PUSH    AF
3773: D5              PUSH    DE
3774: 01 DF FF        LD      BC,$FFDF ; Screen offset constant -33 right one column (-1), up one row (-32)
3777: CD 96 37        CALL    L3796 ; {code.L3796} left part of bonus explosion animation
377A: D1              POP     DE
377B: F1              POP     AF
377C: 2F              CPL
377D: 6F              LD      L,A
377E: 26 FF           LD      H,$FF
3780: 23              INC     HL
3781: 19              ADD     HL,DE
3782: EB              EX      DE,HL
3783: 21 A0 BF        LD      HL,$BFA0
3786: 19              ADD     HL,DE
3787: D0              RET     NC
3788: EB              EX      DE,HL
3789: 11 D6 17        LD      DE,T17D6 ; {+code.T17D6} (Bonus explosion right part)
378C: 36 00           LD      (HL),$00
378E: 23              INC     HL
378F: 36 00           LD      (HL),$00
3791: 09              ADD     HL,BC
3792: C3 40 35        JP      Draw3x2 ; {code.Draw3x2}
3795: FF              .DB $FF
L3796:
3796: C6 60           ADD     $60
3798: 6F              LD      L,A
3799: 26 00           LD      H,$00
379B: D2 9F 37        JP      NC,L379F ; {code.L379F}
379E: 24              INC     H
L379F:
379F: 19              ADD     HL,DE
37A0: EB              EX      DE,HL
37A1: 21 C0 BC        LD      HL,$BCC0
37A4: 19              ADD     HL,DE
37A5: D8              RET     C
37A6: EB              EX      DE,HL
37A7: 11 D0 17        LD      DE,T17D0 ; {+code.T17D0} (Bonus explosion left part)
37AA: C3 40 35        JP      Draw3x2 ; {code.Draw3x2}
37AD: FF              .DB $FF
37AE: FF              .DB $FF
37AF: FF              .DB $FF
L37B0:
37B0: 2C              INC     L
37B1: 7E              LD      A,(HL)
37B2: 27              DAA
37B3: 77              LD      (HL),A
37B4: 2C              INC     L
37B5: 56              LD      D,(HL)
37B6: 2C              INC     L
37B7: 5E              LD      E,(HL)
37B8: 2D              DEC     L
37B9: 2D              DEC     L
37BA: 00              NOP
37BB: CD 17 02        CALL    RightOneColumn ; {code.RightOneColumn}
37BE: 3E 20           LD      A,$20 ; character code for '0' (the right digit of bonus score)
37C0: 12              LD      (DE),A ; write to screen ram (upper left corner of object 17D6)
37C1: CD 10 02        CALL    LeftOneColumn ; {code.LeftOneColumn}
37C4: 06 02           LD      B,$02 ; for the left two digits
37C6: C3 C4 00        JP      PrintNumber ; {code.PrintNumber} score value for bonus explosion
37C9: FF              .DB $FF
37CA: FF              .DB $FF
37CB: FF              .DB $FF
L37CC:
37CC: 2C              INC     L
37CD: 2C              INC     L
37CE: 2C              INC     L
37CF: 7E              LD      A,(HL)
37D0: E6 1F           AND     $1F ; 0001_1111
37D2: C6 20           ADD     $20
37D4: 6F              LD      L,A
37D5: 26 43           LD      H,$43
37D7: 01 DF FF        LD      BC,$FFDF ; Screen offset constant -33 right one column (-1), up one row (-32)
37DA: 11 1A 00        LD      DE,$001A
L37DD:
37DD: 72              LD      (HL),D
37DE: 23              INC     HL
37DF: 72              LD      (HL),D
37E0: 09              ADD     HL,BC
37E1: 1D              DEC     E
37E2: C2 DD 37        JP      NZ,L37DD ; {code.L37DD}
37E5: C9              RET
37E6: FF              .DB $FF
37E7: FF              .DB $FF
37E8: FF              .DB $FF
37E9: FF              .DB $FF
37EA: FF              .DB $FF
37EB: FF              .DB $FF
37EC: FF              .DB $FF
37ED: FF              .DB $FF
37EE: FF              .DB $FF
37EF: FF              .DB $FF
37F0: FF              .DB $FF
37F1: FF              .DB $FF
37F2: FF              .DB $FF
37F3: FF              .DB $FF
37F4: FF              .DB $FF
37F5: FF              .DB $FF
37F6: FF              .DB $FF
37F7: FF              .DB $FF
37F8: FF              .DB $FF
37F9: FF              .DB $FF
37FA: FF              .DB $FF
37FB: FF              .DB $FF
37FC: FF              .DB $FF
37FD: FF              .DB $FF
37FE: FF              .DB $FF
37FF: FF              .DB $FF
L3800:
3800: 3A C4 43        LD      A,(PlayerBulletState) ; {ram.PlayerBulletState}
3803: E6 08           AND     $08 ; 0000_1000
3805: C8              RET     Z
3806: 3A E6 43        LD      A,(AbovePlayerBulletMSB) ; {ram.AbovePlayerBulletMSB}
3809: C6 08           ADD     $08
380B: 57              LD      D,A
380C: 3A D2 4B        LD      A,(M4BD2) ; {!ram.B4BD2}
380F: 5F              LD      E,A
3810: 3A E7 43        LD      A,(AbovePlayerBulletLSB) ; {ram.AbovePlayerBulletLSB}
3813: E6 E0           AND     $E0 ; 1110_0000
3815: 47              LD      B,A
3816: 3A E7 43        LD      A,(AbovePlayerBulletLSB) ; {ram.AbovePlayerBulletLSB}
3819: 93              SUB     E
381A: 00              NOP
381B: E6 1F           AND     $1F ; 0001_1111
381D: B0              OR      B
381E: 5F              LD      E,A
381F: 1A              LD      A,(DE)
3820: D6 90           SUB     $90
3822: D8              RET     C
3823: 47              LD      B,A
3824: 3A C6 43        LD      A,(PlayerBulletX) ; {ram.PlayerBulletX}
3827: E6 07           AND     $07 ; 0000_0111
3829: C6 00           ADD     $00
382B: 6F              LD      L,A
382C: 26 3E           LD      H,$3E
382E: 4E              LD      C,(HL)
382F: 7B              LD      A,E
3830: E6 0E           AND     $0E ; 0000_1110
3832: 07              RLCA ; Multiply by 4 ..
3833: 07              RLCA ; ..
3834: 5F              LD      E,A
3835: 3E A8           LD      A,$A8
3837: 93              SUB     E
3838: 5F              LD      E,A
3839: 16 4B           LD      D,$4B
383B: 78              LD      A,B
383C: FE 50           CP      $50
383E: DC 44 38        CALL    C,L3844 ; {code.L3844}
3841: C3 1C 39        JP      L391C ; {code.L391C}
L3844:
3844: C6 60           ADD     $60 ; LSB of table T3B60
3846: 6F              LD      L,A
3847: 26 3B           LD      H,$3B ; MSB of table T3B60
3849: 7E              LD      A,(HL)
384A: A1              AND     C
384B: C8              RET     Z
384C: CD A1 38        CALL    L38A1 ; {code.L38A1}
384F: EB              EX      DE,HL
3850: 7E              LD      A,(HL)
3851: 36 00           LD      (HL),$00
3853: 2C              INC     L
3854: 2C              INC     L
3855: 2C              INC     L
3856: 2C              INC     L
3857: 56              LD      D,(HL)
3858: E1              POP     HL
3859: 21 BB 43        LD      HL,BirdsLeft ; {+ram.BirdsLeft}
385C: 35              DEC     (HL) ; decrement number of BirdsLeft
385D: FE 0B           CP      $0B
385F: DA 94 38        JP      C,L3894 ; {code.L3894}
3862: 5F              LD      E,A
3863: 3E FF           LD      A,$FF ; set bonus explosion flag
3865: 32 69 43        LD      (M4369),A ; {ram.M4369}
3868: 21 78 43        LD      HL,M4378 ; {+ram.M4378}
386B: 01 10 10        LD      BC,$1010 ; C reg. set to: 'bonus explosion score 100'.
386E: 7B              LD      A,E
386F: FE 0F           CP      $0F
3871: CA FB 38        JP      Z,L38FB ; {code.L38FB}
3874: 7A              LD      A,D
3875: 0F              RRCA
3876: E6 7C           AND     $7C ; 0111_1100
3878: C6 30           ADD     $30
387A: 4F              LD      C,A
387B: 7B              LD      A,E
387C: FE 0E           CP      $0E
387E: CA FB 38        JP      Z,L38FB ; {code.L38FB}
3881: 79              LD      A,C
3882: 0F              RRCA
3883: 4F              LD      C,A
3884: 7B              LD      A,E
3885: FE 0C           CP      $0C
3887: D2 FB 38        JP      NC,L38FB ; {code.L38FB} if >= $0C
388A: 79              LD      A,C
388B: 0F              RRCA
388C: 4F              LD      C,A
388D: C3 FB 38        JP      L38FB ; {code.L38FB}
3890: FF              .DB $FF
3891: FF              .DB $FF
3892: FF              .DB $FF
3893: FF              .DB $FF
L3894:
3894: 01 05 0D        LD      BC,$0D05
3897: 3E FF           LD      A,$FF
3899: 32 64 43        LD      (M4364),A ; {ram.M4364}
389C: C3 F8 38        JP      L38F8 ; {code.L38F8}
389F: FF              .DB $FF
38A0: FF              .DB $FF
L38A1:
38A1: D5              PUSH    DE
38A2: 0E 20           LD      C,$20
38A4: EB              EX      DE,HL
38A5: 23              INC     HL
38A6: 56              LD      D,(HL)
38A7: 23              INC     HL
38A8: 5E              LD      E,(HL)
38A9: 3A 8C 19        LD      A,(L198C) ; {code.L198C} First letter 'R' from: " AMSTAR ELECTRONICS CORP. "
38AC: C6 DE           ADD     $DE ; 1101_1110
38AE: 6F              LD      L,A
38AF: 26 17           LD      H,$17 ; HL=$17F0 (FourByFourEmpty:)
38B1: CD DE 34        CALL    L34DE ; {code.L34DE}
38B4: D1              POP     DE
38B5: C9              RET
38B6: 35              .DB $35
38B7: D1              .DB $D1
38B8: C9              .DB $C9
38B9: FF              .DB $FF
38BA: FF              .DB $FF
38BB: FF              .DB $FF
L38BC:
38BC: C6 B0           ADD     $B0
38BE: 6F              LD      L,A
38BF: 26 3B           LD      H,$3B
38C1: 7E              LD      A,(HL)
38C2: A1              AND     C
38C3: C8              RET     Z
38C4: CD A1 38        CALL    L38A1 ; {code.L38A1}
38C7: 1A              LD      A,(DE)
38C8: D6 0B           SUB     $0B
38CA: DA E9 38        JP      C,L38E9 ; {code.L38E9}
38CD: FE 03           CP      $03
38CF: D2 E9 38        JP      NC,L38E9 ; {code.L38E9} if >= $03
38D2: 47              LD      B,A
38D3: 62              LD      H,D
38D4: 7B              LD      A,E
38D5: C6 05           ADD     $05
38D7: 6F              LD      L,A
38D8: 3A C6 43        LD      A,(PlayerBulletX) ; {ram.PlayerBulletX}
38DB: BE              CP      (HL)
38DC: 17              RLA
38DD: 07              RLCA ; Multiply by 4 ..
38DE: 07              RLCA ; ..
38DF: E6 04           AND     $04 ; 0000_0100
38E1: B0              OR      B
38E2: C6 B8           ADD     $B8
38E4: 6F              LD      L,A
38E5: 26 3D           LD      H,$3D
38E7: 7E              LD      A,(HL)
38E8: 12              LD      (DE),A
L38E9:
38E9: 3E FF           LD      A,$FF
38EB: 32 66 43        LD      (M4366),A ; {ram.M4366}
38EE: 01 02 07        LD      BC,$0702
38F1: C3 F8 38        JP      L38F8 ; {code.L38F8}
38F4: FF              .DB $FF
38F5: FF              .DB $FF
38F6: FF              .DB $FF
38F7: FF              .DB $FF
L38F8:
38F8: 21 70 43        LD      HL,M4370 ; {+ram.M4370}
L38FB:
38FB: AF              XOR     A ; A=0
38FC: BE              CP      (HL)
38FD: CA 06 39        JP      Z,L3906 ; {code.L3906}
3900: 2C              INC     L
3901: 2C              INC     L
3902: 2C              INC     L
3903: 2C              INC     L
3904: BE              CP      (HL)
3905: C0              RET     NZ
L3906:
3906: 70              LD      (HL),B
3907: 2C              INC     L
3908: 71              LD      (HL),C
3909: 2C              INC     L
390A: 3A E6 43        LD      A,(AbovePlayerBulletMSB) ; {ram.AbovePlayerBulletMSB}
390D: 77              LD      (HL),A
390E: 2C              INC     L
390F: 3A E7 43        LD      A,(AbovePlayerBulletLSB) ; {ram.AbovePlayerBulletLSB}
3912: 77              LD      (HL),A
3913: 3A C4 43        LD      A,(PlayerBulletState) ; {ram.PlayerBulletState}
3916: E6 F7           AND     $F7 ; 1111_0111
3918: 32 C4 43        LD      (PlayerBulletState),A ; {ram.PlayerBulletState}
391B: C9              RET
L391C:
391C: 78              LD      A,B
391D: FE 20           CP      $20
391F: D2 BC 38        JP      NC,L38BC ; {code.L38BC} if >= $20
3922: C9              RET
L3923:
3923: C8              RET     Z
3924: 35              DEC     (HL) ; {ram.M436B} decrement $436B Counter for: 'mother ship score display'
3925: 2E 8D           LD      L,$8D ; SoundControlB
3927: 7E              LD      A,(HL)
3928: E6 3F           AND     $3F ; 0011_1111
392A: F6 80           OR      $80 ; 1000_0000
392C: 77              LD      (HL),A
392D: C9              RET
392E: C9              .DB $C9
392F: FF              .DB $FF
L3930:
3930: 3A D2 4B        LD      A,(M4BD2) ; {!ram.B4BD2}
3933: E6 1E           AND     $1E ; 0001_1110
3935: C6 C0           ADD     T3DC0 & $FF ; LSB of table T3DC0
3937: 6F              LD      L,A
3938: 26 3D           LD      H,T3DC0 >> 8 ; MSB of table T3DC0
393A: 5E              LD      E,(HL)
393B: 2C              INC     L
393C: 6E              LD      L,(HL)
393D: 26 4B           LD      H,$4B
393F: CD 00 3A        CALL    L3A00 ; {code.L3A00}
3942: 3A 9F 43        LD      A,(M439F) ; {ram.M439F}
3945: 82              ADD     A,D
3946: 4F              LD      C,A
3947: 3A 9E 43        LD      A,(M439E) ; {ram.M439E}
394A: 92              SUB     D
394B: 47              LD      B,A
L394C:
394C: E5              PUSH    HL
394D: CD 5C 39        CALL    L395C ; {code.L395C}
3950: E1              POP     HL
3951: 7D              LD      A,L
3952: C6 08           ADD     $08
3954: 6F              LD      L,A
3955: 1D              DEC     E
3956: C2 4C 39        JP      NZ,L394C ; {code.L394C}
3959: C9              RET
395A: FF              .DB $FF
395B: FF              .DB $FF
L395C:
395C: 7E              LD      A,(HL)
395D: FE 05           CP      $05
395F: D8              RET     C
3960: 7D              LD      A,L
3961: C6 05           ADD     $05
3963: 6F              LD      L,A
3964: 7E              LD      A,(HL)
3965: B8              CP      B
3966: D8              RET     C
3967: B9              CP      C
3968: D0              RET     NC
3969: D6 04           SUB     $04
396B: 47              LD      B,A
396C: 2D              DEC     L
396D: 2D              DEC     L
396E: 2D              DEC     L
396F: 3A D2 4B        LD      A,(M4BD2) ; {!ram.B4BD2}
3972: 86              ADD     A,(HL)
3973: E6 1F           AND     $1F ; 0001_1111
3975: 07              RLCA ; Multiply by 8 ..
3976: 07              RLCA ; ..
3977: 07              RLCA ; ..
3978: C6 08           ADD     $08
397A: 4F              LD      C,A
397B: C3 B7 25        JP      L25B7 ; {code.L25B7}
397E: FF              .DB $FF
397F: FF              .DB $FF
L3980:
3980: 3A D2 4B        LD      A,(M4BD2) ; {!ram.B4BD2}
3983: D6 0C           SUB     $0C
3985: D8              RET     C
3986: FE 10           CP      $10
3988: D0              RET     NC
3989: 21 C4 43        LD      HL,PlayerBulletState ; {+ram.PlayerBulletState}
398C: 11 C0 4B        LD      DE,M4BC0 ; {!+ram.B4BC0}
398F: 06 04           LD      B,$04
3991: CD E0 05        CALL    CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
3994: 2E E6           LD      L,$E6 ; AbovePlayerBulletMSB
3996: 06 02           LD      B,$02
3998: CD E0 05        CALL    CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
399B: 2E E2           LD      L,$E2 ; PlayerShipMSB
399D: 11 E6 43        LD      DE,AbovePlayerBulletMSB ; {+ram.AbovePlayerBulletMSB}
39A0: 06 02           LD      B,$02
39A2: CD E0 05        CALL    CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
39A5: 2E C4           LD      L,$C4 ; PlayerBulletState
39A7: 36 08           LD      (HL),$08
39A9: 11 9E 43        LD      DE,M439E ; {+ram.M439E}
39AC: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
39AF: 0F              RRCA
39B0: DA BF 39        JP      C,L39BF ; {code.L39BF}
39B3: 1C              INC     E
39B4: 2E E7           LD      L,$E7 ; AbovePlayerBulletLSB
39B6: 7E              LD      A,(HL)
39B7: D6 20           SUB     $20
39B9: 77              LD      (HL),A
39BA: 2D              DEC     L ; AbovePlayerBulletMSB
39BB: 7E              LD      A,(HL)
39BC: DE 00           SBC     $00
39BE: 77              LD      (HL),A
L39BF:
39BF: 1A              LD      A,(DE)
39C0: 32 C6 43        LD      (PlayerBulletX),A ; {ram.PlayerBulletX}
L39C3:
39C3: CD 00 38        CALL    L3800 ; {code.L3800} Collision detection for birds
39C6: 21 C4 43        LD      HL,PlayerBulletState ; {+ram.PlayerBulletState}
39C9: 7E              LD      A,(HL)
39CA: E6 08           AND     $08 ; 0000_1000
39CC: CA F0 39        JP      Z,L39F0 ; {code.L39F0}
39CF: 21 E7 43        LD      HL,AbovePlayerBulletLSB ; {+ram.AbovePlayerBulletLSB}
39D2: 34              INC     (HL)
39D3: 7E              LD      A,(HL)
39D4: E6 1F           AND     $1F ; 0001_1111
39D6: FE 1D           CP      $1D
39D8: DA C3 39        JP      C,L39C3 ; {code.L39C3}
L39DB:
39DB: 21 C0 4B        LD      HL,M4BC0 ; {!+ram.B4BC0}
39DE: 11 C4 43        LD      DE,PlayerBulletState ; {+ram.PlayerBulletState}
39E1: 06 04           LD      B,$04
39E3: CD E0 05        CALL    CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
39E6: 1E E6           LD      E,$E6
39E8: 06 02           LD      B,$02
39EA: C3 E0 05        JP      CopyBbytesHLtoDE ; {code.CopyBbytesHLtoDE}
39ED: FF              .DB $FF
39EE: FF              .DB $FF
39EF: FF              .DB $FF
L39F0:
39F0: 2E A6           LD      L,$A6 ; ShieldCount
39F2: 7E              LD      A,(HL)
39F3: FE C0           CP      $C0 ; end of shield time
39F5: DA C4 0C        JP      C,L0CC4 ; {code.L0CC4}
39F8: D6 01           SUB     $01
39FA: 77              LD      (HL),A
39FB: C3 DB 39        JP      L39DB ; {code.L39DB}
39FE: FF              .DB $FF
39FF: FF              .DB $FF
L3A00:
3A00: 3A BB 43        LD      A,(BirdsLeft) ; {ram.BirdsLeft}
3A03: D6 0C           SUB     $0C
3A05: 2F              CPL
3A06: 3C              INC     A
3A07: 57              LD      D,A
3A08: 3A 9B 43        LD      A,(Counter9A+$1) ; {ram.Counter9A+1}
3A0B: 0F              RRCA
3A0C: 0F              RRCA
3A0D: D8              RET     C
3A0E: E1              POP     HL
3A0F: C9              RET
L3A10:
3A10: 21 B8 43        LD      HL,LevelAndRound ; {+ram.LevelAndRound}
3A13: 7E              LD      A,(HL) ; get it
3A14: A7              AND     A ; updates the zero flag
3A15: C2 43 3B        JP      NZ,L3B43 ; {code.L3B43} if LevelAndRound is not 0.
3A18: 2E 8D           LD      L,$8D ; set SoundControlB for...
3A1A: 36 CF           LD      (HL),$CF ; ... 1100_1111 triggers Tune3 -- ESTUDIO (Phoenix theme song)
3A1C: C9              RET
L3A1D:
3A1D: 21 69 43        LD      HL,M4369 ; {+ram.M4369}
3A20: 7E              LD      A,(HL)
3A21: A7              AND     A ; updates the zero flag
3A22: CA 40 3A        JP      Z,L3A40 ; {code.L3A40} if $4369 is 0.
3A25: FE 20           CP      $20
3A27: DA 2C 3A        JP      C,L3A2C ; {code.L3A2C}
3A2A: 36 20           LD      (HL),$20
L3A2C:
3A2C: 35              DEC     (HL)
3A2D: 7E              LD      A,(HL)
3A2E: 07              RLCA ; Multiply by 4 ..
3A2F: 07              RLCA ; ..
3A30: 00              NOP
3A31: 2F              CPL
3A32: E6 0E           AND     $0E ; 0000_1110
3A34: 2E 8D           LD      L,$8D ; SoundControlB
3A36: 77              LD      (HL),A
3A37: 2E 68           LD      L,$68 ; {ram.M4368} $4368
3A39: 36 00           LD      (HL),$00
3A3B: 2E 66           LD      L,$66 ; {ram.M4366} $4366
3A3D: 36 00           LD      (HL),$00
3A3F: C9              RET
L3A40:
3A40: 2E 64           LD      L,$64 ; {ram.M4364} $4364
3A42: 7E              LD      A,(HL)
3A43: A7              AND     A ; updates the zero flag
3A44: CA 62 3A        JP      Z,L3A62 ; {code.L3A62}
3A47: FE 10           CP      $10
3A49: DA 4E 3A        JP      C,L3A4E ; {code.L3A4E}
3A4C: 36 10           LD      (HL),$10
L3A4E:
3A4E: 35              DEC     (HL)
3A4F: 7E              LD      A,(HL)
3A50: 0F              RRCA
3A51: 00              NOP
3A52: 00              NOP
3A53: 2F              CPL
3A54: E6 07           AND     $07 ; 0000_0111
3A56: F6 10           OR      $10 ; 0001_0000
3A58: 2E 8C           LD      L,$8C ; SoundControlA
3A5A: 77              LD      (HL),A
3A5B: 2E 66           LD      L,$66 ; {ram.M4366} $4366
3A5D: 36 00           LD      (HL),$00
3A5F: C9              RET
3A60: 0F              .DB $0F
3A61: 00              .DB $00
L3A62:
3A62: 2E 66           LD      L,$66 ; {ram.M4366} $4366
3A64: 7E              LD      A,(HL)
3A65: A7              AND     A ; updates the zero flag
3A66: C8              RET     Z
3A67: FE 10           CP      $10
3A69: DA 78 3A        JP      C,L3A78 ; {code.L3A78}
3A6C: 36 10           LD      (HL),$10
3A6E: 3A B8 43        LD      A,(LevelAndRound) ; {ram.LevelAndRound}
3A71: E6 08           AND     $08 ; 0000_1000
3A73: CA 78 3A        JP      Z,L3A78 ; {code.L3A78}
3A76: 36 05           LD      (HL),$05
L3A78:
3A78: 35              DEC     (HL)
3A79: 2E 8C           LD      L,$8C ; SoundControlA
3A7B: 7E              LD      A,(HL)
3A7C: E6 08           AND     $08 ; 0000_1000
3A7E: F6 04           OR      $04 ; 0000_0100
3A80: 77              LD      (HL),A
3A81: C9              RET
L3A82:
3A82: 21 9A 43        LD      HL,Counter9A ; {+ram.Counter9A}
3A85: 7E              LD      A,(HL)
3A86: FE 03           CP      $03
3A88: D8              RET     C
3A89: 2E 8D           LD      L,$8D ; SoundControlB
3A8B: 7E              LD      A,(HL)
3A8C: E6 3F           AND     $3F ; 0011_1111
3A8E: 77              LD      (HL),A
3A8F: C9              RET
L3A90:
3A90: 21 6B 43        LD      HL,M436B ; {+ram.M436B}
3A93: 7E              LD      A,(HL)
3A94: A7              AND     A ; updates the zero flag
3A95: C3 23 39        JP      L3923 ; {code.L3923}
L3A98:
3A98: 21 70 4B        LD      HL,M4B70 ; {+ram.M4B70}
3A9B: 01 00 08        LD      BC,$0800
3A9E: 11 B0 03        LD      DE,$03B0
L3AA1:
3AA1: 7E              LD      A,(HL)
3AA2: 2C              INC     L
3AA3: A0              AND     B
3AA4: CA AE 3A        JP      Z,L3AAE ; {code.L3AAE}
3AA7: 7E              LD      A,(HL)
3AA8: FE 28           CP      $28
3AAA: DA AE 3A        JP      C,L3AAE ; {code.L3AAE}
3AAD: 0C              INC     C
L3AAE:
3AAE: 7D              LD      A,L
3AAF: 82              ADD     A,D
3AB0: 6F              LD      L,A
3AB1: BB              CP      E
3AB2: C2 A1 3A        JP      NZ,L3AA1 ; {code.L3AA1}
3AB5: 79              LD      A,C
3AB6: A7              AND     A ; updates the zero flag
3AB7: C8              RET     Z
3AB8: FE 08           CP      $08
3ABA: DA BF 3A        JP      C,L3ABF ; {code.L3ABF}
3ABD: 3E 08           LD      A,$08
L3ABF:
3ABF: C6 25           ADD     $25
3AC1: 4F              LD      C,A
3AC2: 21 8C 43        LD      HL,SoundControlA ; {+ram.SoundControlA}
3AC5: 7E              LD      A,(HL)
3AC6: E6 C0           AND     $C0 ; mask out 1100_0000
3AC8: B1              OR      C
3AC9: 77              LD      (HL),A ; trigger sound control A
3ACA: C9              RET
3ACB: FF              .DB $FF
3ACC: FF              .DB $FF
3ACD: FF              .DB $FF
3ACE: FF              .DB $FF
3ACF: FF              .DB $FF
L3AD0:
3AD0: 21 8E 43        LD      HL,M438E ; {+ram.M438E}
3AD3: 7E              LD      A,(HL)
3AD4: E6 01           AND     $01 ; 0000_0001
3AD6: 07              RLCA ; Multiply by 4 ..
3AD7: 07              RLCA ; ..
3AD8: F6 20           OR      $20 ; 0010_0000
3ADA: 47              LD      B,A
3ADB: 2D              DEC     L
3ADC: 7E              LD      A,(HL)
3ADD: E6 C0           AND     $C0 ; 1100_0000
3ADF: B0              OR      B
3AE0: 77              LD      (HL),A
3AE1: 2E 96           LD      L,$96 ; {ram.M4396} $4396
3AE3: 7E              LD      A,(HL)
3AE4: 34              INC     (HL)
3AE5: A7              AND     A ; updates the zero flag
3AE6: CA F8 3A        JP      Z,L3AF8 ; {code.L3AF8}
3AE9: 3A D6 4B        LD      A,(M4BD6) ; {!ram.B4BD6}
3AEC: C6 E0           ADD     $E0 ; LSB of table T3DE0
3AEE: 5F              LD      E,A
3AEF: 16 3D           LD      D,$3D ; MSB of table T3DE0
3AF1: 1A              LD      A,(DE)
3AF2: BE              CP      (HL)
3AF3: D0              RET     NC
3AF4: 36 00           LD      (HL),$00
3AF6: C9              RET
3AF7: 5F              .DB $5F
L3AF8:
3AF8: 2E 8E           LD      L,$8E ; {ram.M438E} $438E
3AFA: 34              INC     (HL)
3AFB: 2D              DEC     L ; SoundControlB
3AFC: 7E              LD      A,(HL)
3AFD: F6 10           OR      $10 ; 0001_0000
3AFF: 77              LD      (HL),A
3B00: C9              RET
3B01: 8E              .DB $8E
L3B02:
3B02: 21 9A 43        LD      HL,Counter9A ; {+ram.Counter9A}
3B05: 7E              LD      A,(HL)
3B06: FE 02           CP      $02
3B08: D0              RET     NC
3B09: 2C              INC     L
3B0A: 7E              LD      A,(HL)
3B0B: 47              LD      B,A
3B0C: E6 60           AND     $60 ; 0110_0000
3B0E: 2E 8D           LD      L,$8D ; SoundControlB
3B10: 36 0A           LD      (HL),$0A ; 0000_1010
3B12: C0              RET     NZ
3B13: 78              LD      A,B
3B14: E6 02           AND     $02 ; 0000_0010
3B16: C6 1C           ADD     $1C
3B18: 77              LD      (HL),A
3B19: C9              RET
3B1A: 78              .DB $78
L3B1B:
3B1B: 21 62 43        LD      HL,M4362 ; {+ram.M4362}
3B1E: 7E              LD      A,(HL)
3B1F: A7              AND     A ; updates the zero flag
3B20: C8              RET     Z ; if $4362 is 0.
3B21: FE 40           CP      $40
3B23: DA 28 3B        JP      C,L3B28 ; {code.L3B28}
3B26: 36 40           LD      (HL),$40
L3B28:
3B28: 35              DEC     (HL)
3B29: 7E              LD      A,(HL)
3B2A: E6 06           AND     $06 ; 0000_0110
3B2C: 07              RLCA ; Multiply by 2
3B2D: 00              NOP
3B2E: 2E 8D           LD      L,$8D ; SoundControlB
3B30: 77              LD      (HL),A
3B31: C9              RET
3B32: FF              .DB $FF
L3B33:
3B33: 21 6A 43        LD      HL,M436A ; {+ram.M436A}
3B36: 7E              LD      A,(HL)
3B37: A7              AND     A ; updates the zero flag
3B38: C8              RET     Z ; if $436A is 0.
3B39: 35              DEC     (HL)
3B3A: E6 08           AND     $08 ; 0000_1000
3B3C: F6 07           OR      $07 ; 0000_0111
3B3E: 2E 8D           LD      L,$8D ; SoundControlB
3B40: 77              LD      (HL),A
3B41: C9              RET
3B42: 8D              .DB $8D
L3B43:
3B43: 21 A4 43        LD      HL,GameState ; {+ram.GameState}
3B46: 7E              LD      A,(HL)
3B47: FE 03           CP      $03
3B49: CC D6 23        CALL    Z,L23D6 ; {code.L23D6} if GameState is 'normal game play'
3B4C: CD 33 3B        CALL    L3B33 ; {code.L3B33}
3B4F: CD 1B 3B        CALL    L3B1B ; {code.L3B1B}
3B52: CD 1D 3A        CALL    L3A1D ; {code.L3A1D}
3B55: CD BD 27        CALL    L27BD ; {code.L27BD}
3B58: CD 82 3A        CALL    L3A82 ; {code.L3A82}
3B5B: C3 90 3A        JP      L3A90 ; {code.L3A90}
3B5E: FF              .DB $FF
3B5F: FF              .DB $FF
T3B60:
3B60: 1F 7C F0 01     .DB $1F, $7C, $F0, $01, $C0
3B64: C0
3B65: 07 7F FC F0     .DB $07, $7F, $FC, $F0, $07, $C0, $1F, $FF, $FC, $03, $F0
3B69: 07 C0 1F FF
3B6D: FC 03 F0
3B70: 0F C0 3F FC     .DB $0F, $C0, $3F, $FC, $1F, $F0, $07, $FE, $3F, $F8, $0F, $FF, $FF, $FC, $1F, $FF
3B74: 1F F0 07 FE
3B78: 3F F8 0F FF
3B7C: FF FC 1F FF
3B80: FC 1F FC 1F     .DB $FC, $1F, $FC, $1F, $F0, $7F, $F0, $7F, $C0, $FF, $01, $C0, $FF, $01, $00, $FF
3B84: F0 7F F0 7F
3B88: C0 FF 01 C0
3B8C: FF 01 00 FF
3B90: 07 00 FF 07     .DB $07, $00, $FF, $07, $FC, $1F, $FC, $1F, $F0, $7F, $F0, $7F, $C0, $FF, $01, $C0
3B94: FC 1F FC 1F
3B98: F0 7F F0 7F
3B9C: C0 FF 01 C0
3BA0: FF 01 00 FF     .DB $FF, $01, $00, $FF, $07, $FF, $07, $FC, $1F, $F8, $0F, $F0, $C0, $03, $FF, $FF
3BA4: 07 FF 07 FC
3BA8: 1F F8 0F F0
3BAC: C0 03 FF FF
3BB0: 03 E0 03 E0     .DB $03, $E0, $03, $E0, $0F, $80, $0F, $00, $3C, $00, $1E, $3F, $00, $FC, $F0, $00
3BB4: 0F 80 0F 00
3BB8: 3C 00 1E 3F
3BBC: 00 FC F0 00
3BC0: 7F FE 00 F0     .DB $7F, $FE, $00, $F0, $03, $E0, $00, $00, $0F, $80, $00, $00, $3F, $00, $FE, $30
3BC4: 03 E0 00 00
3BC8: 0F 80 00 00
3BCC: 3F 00 FE 30
3BD0: 00 06 FF 00     .DB $00, $06, $FF, $00, $F8, $00, $00, $03, $E0, $00, $E0, $08, $20, $04, $C0, $01
3BD4: F8 00 00 03
3BD8: E0 00 E0 08
3BDC: 20 04 C0 01
3BE0: E0 03 F8 0F     .DB $E0, $03, $F8, $0F, $07, $E0, $3F, $03, $FF, $FF, $FF, $3F, $FC, $FF, $F8, $FF
3BE4: 07 E0 3F 03
3BE8: FF FF FF 3F
3BEC: FC FF F8 FF
3BF0: FF 07 E0 1F     .DB $FF, $07, $E0, $1F, $F0, $FF, $FC, $FF, $07, $1E, $FC, $1F, $1F, $7F, $FF, $FF
3BF4: F0 FF FC FF
3BF8: 07 1E FC 1F
3BFC: 1F 7F FF FF
T3C00:
3C00: E8 00 E9 00     .DB $E8, $00, $E9, $00, $C4, $C6, $C5, $C7, $EA, $00, $EB, $00, $00, $00 ; bird shape #24 [Object 3C00](bgtiles.md#object-3c00)
3C04: C4 C6 C5 C7
3C08: EA 00 EB 00
3C0C: 00 00
3C0E: EC 00 E9 00     .DB $EC, $00, $E9, $00, $C8, $CA, $C9, $CB, $EA, $00, $ED, $00, $00, $00 ; #28 [Object 3C0E](bgtiles.md#object-3c0e)
3C12: C8 CA C9 CB
3C16: EA 00 ED 00
3C1A: 00 00
3C1C: EE 00 EF 00     .DB $EE, $00, $EF, $00, $CC, $CF, $CD, $D0, $CE, $D1, $F0, $00, $F1, $00 ; #29 [Object 3C1C](bgtiles.md#object-3c1c)
3C20: CC CF CD D0
3C24: CE D1 F0 00
3C28: F1 00
3C2A: F2 00 EF 00     .DB $F2, $00, $EF, $00, $D2, $00, $D3, $D5, $D4, $D6, $F0, $00, $F3, $00 ; #30 [Object 3C2A](bgtiles.md#object-3c2a)
3C2E: D2 00 D3 D5
3C32: D4 D6 F0 00
3C36: F3 00
3C38: E8 00 E9 00     .DB $E8, $00, $E9, $00, $C4, $C6, $C5, $C7, $00, $00 ; #24 without right wing [Object 3C38](bgtiles.md#object-3c38)
3C3C: C4 C6 C5 C7
3C40: 00 00
3C42: EC 00 E9 00     .DB $EC, $00, $E9, $00, $C8, $CA, $C9, $CB, $00, $00 ; #28 without right wing [Object 3C42](bgtiles.md#object-3c42)
3C46: C8 CA C9 CB
3C4A: 00 00
3C4C: EE 00 EF 00     .DB $EE, $00, $EF, $00, $CC, $CF, $CD, $D0, $DD, $D1 ; #29 without right wing and regrowing ($DD) [Object 3C4C](bgtiles.md#object-3c4c)
3C50: CC CF CD D0
3C54: DD D1
3C56: F2 00 EF 00     .DB $F2, $00, $EF, $00, $D2, $00, $D3, $D5, $DD, $D6 ; #30 without right wing and regrowing ($DD) [Object 3C56](bgtiles.md#object-3c56)
3C5A: D2 00 D3 D5
3C5E: DD D6
3C60: 00 00 00 00     .DB $00, $00, $00, $00, $C4, $C6, $C5, $C7, $EA, $00, $EB, $00, $00, $00 ; #24 without left wing [Object 3C60](bgtiles.md#object-3c60)
3C64: C4 C6 C5 C7
3C68: EA 00 EB 00
3C6C: 00 00
3C6E: 00 00 00 00     .DB $00, $00, $00, $00, $DB, $CA, $C9, $CB, $EA, $00, $ED, $00, $00, $00 ; #28 without left wing and regrowing ($DB) [Object 3C6E](bgtiles.md#object-3c6e)
3C72: DB CA C9 CB
3C76: EA 00 ED 00
3C7A: 00 00
3C7C: 00 00 00 00     .DB $00, $00, $00, $00, $DC, $CF, $CD, $D0, $CE, $D1, $F0, $00, $F1, $00 ; #29 without left wing and regrowing ($DC) [Object 3C7C](bgtiles.md#object-3c7c)
3C80: DC CF CD D0
3C84: CE D1 F0 00
3C88: F1 00
3C8A: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $D3, $D5, $D4, $D6, $F0, $00, $F3, $00 ; #30 without left wing [Object 3C8A](bgtiles.md#object-3c8a)
3C8E: 00 00 D3 D5
3C92: D4 D6 F0 00
3C96: F3 00
3C98: 00 00 00 00     .DB $00, $00, $00, $00, $C4, $C6, $C5, $C7, $00, $00 ; #24 without left and right wing [Object 3C98](bgtiles.md#object-3c98)
3C9C: C4 C6 C5 C7
3CA0: 00 00
3CA2: 00 00 00 00     .DB $00, $00, $00, $00, $DB, $CA, $C9, $CB, $00, $00 ; #28 without left and right wing and regrowing ($DB) [Object 3CA2](bgtiles.md#object-3ca2)
3CA6: DB CA C9 CB
3CAA: 00 00
3CAC: 00 00 00 00     .DB $00, $00, $00, $00, $DC, $CF, $CD, $D0, $DD, $D1 ; #29 without left and right wing and regrowing ($DC,$DD) [Object 3CAC](bgtiles.md#object-3cac)
3CB0: DC CF CD D0
3CB4: DD D1
3CB6: 00 00 00 00     .DB $00, $00, $00, $00, $00, $00, $D3, $D5, $DD, $D6 ; #30 without left and right wing and regrowing ($DD) [Object 3CB6](bgtiles.md#object-3cb6)
3CBA: 00 00 D3 D5
3CBE: DD D6
3CC0: 00 00 DE E2     .DB $00, $00, $DE, $E2, $AB, $B2, $AC, $B3, $DF, $E3, $00, $00 ; #21 [Object 3CC0](bgtiles.md#object-3cc0)
3CC4: AB B2 AC B3
3CC8: DF E3 00 00
3CCC: 00 00 00 E5     .DB $00, $00, $00, $E5, $B4, $B6, $B5, $B7, $E4, $E6, $00, $00 ; #25 [Object 3CCC](bgtiles.md#object-3ccc)
3CD0: B4 B6 B5 B7
3CD4: E4 E6 00 00
3CD8: 00 00 00 00     .DB $00, $00, $00, $00, $B8, $BB, $B9, $BC, $BA, $BD, $00, $00 ; #26 [Object 3CD8](bgtiles.md#object-3cd8)
3CDC: B8 BB B9 BC
3CE0: BA BD 00 00
3CE4: 00 00 00 00     .DB $00, $00, $00, $00, $BE, $C1, $BF, $C2, $C0, $C3, $00, $E7 ; #27 [Object 3CE4](bgtiles.md#object-3ce4)
3CE8: BE C1 BF C2
3CEC: C0 C3 00 E7
3CF0: FF FF FF FF     .DB $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF ; not used
3CF4: FF FF FF FF
3CF8: FF FF FF FF
3CFC: FF FF FF FF
3D00: 00 00 FA FC     .DB $00, $00, $FA, $FC, $D7, $D9, $D8, $DA, $FB, $FD, $00, $00 ; #22 [Object 3D00](bgtiles.md#object-3d00)
3D04: D7 D9 D8 DA
3D08: FB FD 00 00
3D0C: F4 F6 F5 00     .DB $F4, $F6, $F5, $00, $C4, $C6, $C5, $C7, $F7, $00, $F8, $F9 ; #23 [Object 3D0C](bgtiles.md#object-3d0c)
3D10: C4 C6 C5 C7
3D14: F7 00 F8 F9
3D18: 00 00 00 00     .DB $00, $00, $00, $00, $A7, $A9, $A8, $AA, $00, $00 ; #17 [Object 3D18](bgtiles.md#object-3d18)
3D1C: A7 A9 A8 AA
3D20: 00 00
3D22: 00 00 00 00     .DB $00, $00, $00, $00, $AB, $AD, $AC, $AE, $00, $00 ; #18 [Object 3D22](bgtiles.md#object-3d22)
3D26: AB AD AC AE
3D2A: 00 00
3D2C: 00 00 DE 00     .DB $00, $00, $DE, $00, $AB, $B0, $AC, $B1, $DF, $00 ; #19 [Object 3D2C](bgtiles.md#object-3d2c)
3D30: AB B0 AC B1
3D34: DF 00
3D36: 00 00 DE E0     .DB $00, $00, $DE, $E0, $AB, $B2, $AC, $B3, $DF, $E1 ; #20 [Object 3D36](bgtiles.md#object-3d36)
3D3A: AB B2 AC B3
3D3E: DF E1
3D40: 00 00 9D 00     .DB $00, $00, $9D, $00, $9E, $00, $00, $00 ; #12 [Object 3D40](bgtiles.md#object-3d40)
3D44: 9E 00 00 00
3D48: 00 00 9F 00     .DB $00, $00, $9F, $00, $A0, $00, $00, $00 ; #13 [Object 3D48](bgtiles.md#object-3d48)
3D4C: A0 00 00 00
3D50: 00 00 00 00     .DB $00, $00, $00, $00, $9C, $00, $00, $00 ; #11 [Object 3D50](bgtiles.md#object-3d50)
3D54: 9C 00 00 00
3D58: 00 00 00 00     .DB $00, $00, $00, $00, $A3, $A5, $A4, $A6 ; #16 [Object 3D58](bgtiles.md#object-3d58)
3D5C: A3 A5 A4 A6
3D60: 00 00 9C 00     .DB $00, $00, $9C, $00, $00, $00 ; #11 one pos moved to the left [Object 3D60](bgtiles.md#object-3d60)
3D64: 00 00
3D66: 00 00 9D 00     .DB $00, $00, $9D, $00, $9E, $00 ; #12 (but 3x2) [Object 3D66](bgtiles.md#object-3d66)
3D6A: 9E 00
3D6C: 00 00 9F 00     .DB $00, $00, $9F, $00, $A0, $00 ; #13 [Object 3D6C](bgtiles.md#object-3d6c)
3D70: A0 00
3D72: 00 00 A1 00     .DB $00, $00, $A1, $00, $A2, $00 ; #14 [Object 3D72](bgtiles.md#object-3d72)
3D76: A2 00
3D78: 00 00 96 00     .DB $00, $00, $96, $00, $00, $00 ; #7 [Object 3D78](bgtiles.md#object-3d78)
3D7C: 00 00
3D7E: 00 00 97 00     .DB $00, $00, $97, $00, $93, $00 ; #8 [Object 3D7E](bgtiles.md#object-3d7e)
3D82: 93 00
3D84: 00 00 98 00     .DB $00, $00, $98, $00, $99, $00 ; #9 [Object 3D84](bgtiles.md#object-3d84)
3D88: 99 00
3D8A: 00 00 9A 00     .DB $00, $00, $9A, $00, $9B, $00 ; #10 [Object 3D8A](bgtiles.md#object-3d8a)
3D8E: 9B 00
3D90: 00 00 90 00     .DB $00, $00, $90, $00, $00, $00 ; #3 [Object 3D90](bgtiles.md#object-3d90)
3D94: 00 00
3D96: 00 00 91 00     .DB $00, $00, $91, $00, $00, $00 ; #4 [Object 3D96](bgtiles.md#object-3d96)
3D9A: 00 00
3D9C: 00 00 92 00     .DB $00, $00, $92, $00, $93, $00 ; #5 [Object 3D9C](bgtiles.md#object-3d9c)
3DA0: 93 00
3DA2: 00 00 94 00     .DB $00, $00, $94, $00, $95, $00 ; #6 [Object 3DA2](bgtiles.md#object-3da2)
3DA6: 95 00
3DA8: 00 00 01 00     .DB $00, $00, $01, $00 ; like small star [Object 3DA8](bgtiles.md#object-3da8)
3DAC: 00 00 08 00     .DB $00, $00, $08, $00 ; like medium star [Object 3DAC](bgtiles.md#object-3dac)
3DB0: 00 00 0A 00     .DB $00, $00, $0A, $00 ; like big star [Object 3DB0](bgtiles.md#object-3db0)
3DB4: 00 00 0B 00     .DB $00, $00, $0B, $00, $0C, $0C, $0E, $FF ; group of stars [Object 3DB4](bgtiles.md#object-3db4)
3DB8: 0C 0C 0E FF
3DBC: 0D 0E 0D FF     .DB $0D, $0E, $0D, $FF ; group of stars [Object 3DBC](bgtiles.md#object-3dbc)
T3DC0:
3DC0: 06 70           .DB $06, $70
3DC2: 07 70           .DB $07, $70
3DC4: 08 70           .DB $08, $70
3DC6: 08 70           .DB $08, $70
3DC8: 08 70           .DB $08, $70
3DCA: 07 78           .DB $07, $78
3DCC: 06 80           .DB $06, $80
3DCE: 05 88           .DB $05, $88
3DD0: 04 90           .DB $04, $90
3DD2: 03 98           .DB $03, $98
3DD4: 02 A0           .DB $02, $A0
3DD6: 01 A8           .DB $01, $A8
3DD8: 02 70           .DB $02, $70
3DDA: 03 70           .DB $03, $70
3DDC: 04 70           .DB $04, $70
3DDE: 05 70           .DB $05, $70
T3DE0:
3DE0: 40 40 40 40     .DB $40, $40, $40, $40, $40, $40, $40, $34, $2C, $26, $20, $1C, $18, $14, $12, $0F
3DE4: 40 40 40 34
3DE8: 2C 26 20 1C
3DEC: 18 14 12 0F
3DF0: 0D 0B 09 08     .DB $0D, $0B, $09, $08, $07, $06, $05, $04, $03, $02, $02, $02, $02, $02, $02, $02
3DF4: 07 06 05 04
3DF8: 03 02 02 02
3DFC: 02 02 02 02
3E00: 01 02 04 08     .DB $01, $02, $04, $08, $10, $20, $40, $80
3E04: 10 20 40 80
T3E08:
3E08: 3D A8           .DB $3D, $A8 ; like small star                  2x2
3E0A: 3D AC           .DB $3D, $AC ; like medium star                 2x2
3E0C: 3D B0           .DB $3D, $B0 ; like big star                    2x2
3E0E: 3D B4           .DB $3D, $B4 ; group of stars
3E10: 3D 90           .DB $3D, $90 ; #3                               3x2
3E12: 3D 96           .DB $3D, $96 ; #4                               3x2
3E14: 3D 9C           .DB $3D, $9C ; #5                               3x2
3E16: 3D A2           .DB $3D, $A2 ; #6                               3x2
3E18: 3D 78           .DB $3D, $78 ; #7                               3x2
3E1A: 3D 7E           .DB $3D, $7E ; #8                               3x2
3E1C: 3D 84           .DB $3D, $84 ; #9                               3x2
3E1E: 3D 8A           .DB $3D, $8A ; #10                              3x2
3E20: 3D 60           .DB $3D, $60 ; #11 one pos moved to the left    3x2
3E22: 3D 66           .DB $3D, $66 ; #12 (but 3x2)                    3x2
3E24: 3D 6C           .DB $3D, $6C ; #13                              3x2
3E26: 3D 72           .DB $3D, $72 ; #14                              3x2
3E28: 3D 40           .DB $3D, $40 ; #12                              4x2
3E2A: 3D 48           .DB $3D, $48 ; #13                              4x2
3E2C: 3D 50           .DB $3D, $50 ; #11                              4x2
3E2E: 3D 58           .DB $3D, $58 ; #16                              4x2
3E30: 3D 18           .DB $3D, $18 ; #17                              5x2
3E32: 3D 22           .DB $3D, $22 ; #18                              5x2
3E34: 3D 2C           .DB $3D, $2C ; #19                              5x2
3E36: 3D 36           .DB $3D, $36 ; #20                              5x2
3E38: 3C C0           .DB $3C, $C0 ; #21                              6x2
3E3A: 3D 00           .DB $3D, $00 ; #22                              6x2
3E3C: 3D 0C           .DB $3D, $0C ; #23                              6x2
3E3E: 3C 00           .DB $3C, $00 ; #24                              7x2
3E40: 3D 58           .DB $3D, $58 ; #16                              4x2
3E42: 3D 50           .DB $3D, $50 ; #11                              4x2
3E44: 3D 48           .DB $3D, $48 ; #13                              4x2
3E46: 3D 40           .DB $3D, $40 ; #12                              4x2
3E48: 3D 36           .DB $3D, $36 ; #20                              5x2
3E4A: 3D 2C           .DB $3D, $2C ; #19                              5x2
3E4C: 3D 22           .DB $3D, $22 ; #18                              5x2
3E4E: 3D 18           .DB $3D, $18 ; #17                              5x2
3E50: 3C 00           .DB $3C, $00 ; #24                              7x2
3E52: 3D 0C           .DB $3D, $0C ; #23                              6x2
3E54: 3D 00           .DB $3D, $00 ; #22                              6x2
3E56: 3C C0           .DB $3C, $C0 ; #21                              6x2
3E58: 3C 00           .DB $3C, $00 ; #24                              7x2
3E5A: 3C 0E           .DB $3C, $0E ; #28                              7x2
3E5C: 3C 1C           .DB $3C, $1C ; #29                              7x2
3E5E: 3C 2A           .DB $3C, $2A ; #30                              7x2
3E60: 3C 38           .DB $3C, $38 ; #24 without right wing           5x2
3E62: 3C 42           .DB $3C, $42 ; #28 without right wing           5x2
3E64: 3C 4C           .DB $3C, $4C ; #29 without right wing reg.      5x2
3E66: 3C 56           .DB $3C, $56 ; #30 without right wing reg.      5x2
3E68: 3C 60           .DB $3C, $60 ; #24 without left wing            7x2
3E6A: 3C 6E           .DB $3C, $6E ; #28 without left wing reg.       7x2
3E6C: 3C 7C           .DB $3C, $7C ; #29 without left wing reg.       7x2
3E6E: 3C 8A           .DB $3C, $8A ; #30 without left wing            7x2
3E70: 3C 98           .DB $3C, $98 ; #24 without left/right wing      5x2
3E72: 3C A2           .DB $3C, $A2 ; #28 without left/right wing reg  5x2
3E74: 3C AC           .DB $3C, $AC ; #29 without left/right wing reg  5x2
3E76: 3C B6           .DB $3C, $B6 ; #30 without left/right wing reg  5x2
3E78: 3C C0           .DB $3C, $C0 ; #21                              6x2
3E7A: 3C CC           .DB $3C, $CC ; #25                              6x2
3E7C: 3C D8           .DB $3C, $D8 ; #26                              6x2
3E7E: 3C E4           .DB $3C, $E4 ; #27                              6x2
T3E80:
3E80: 05 40           .DB $05, $40
3E82: 05 20           .DB $05, $20
3E84: 04 30           .DB $04, $30
3E86: 04 10           .DB $04, $10
3E88: 06 48           .DB $06, $48
3E8A: 06 28           .DB $06, $28
3E8C: 05 38           .DB $05, $38
3E8E: 05 18           .DB $05, $18
3E90: 07 50           .DB $07, $50
3E92: 07 30           .DB $07, $30
3E94: 06 40           .DB $06, $40
3E96: 06 20           .DB $06, $20
3E98: 08 58           .DB $08, $58
3E9A: 08 38           .DB $08, $38
3E9C: 07 48           .DB $07, $48
3E9E: 07 28           .DB $07, $28
3EA0: 06 10           .DB $06, $10
3EA2: 05 20           .DB $05, $20
3EA4: 05 30           .DB $05, $30
3EA6: 05 40           .DB $05, $40
3EA8: 08 18           .DB $08, $18
3EAA: 07 28           .DB $07, $28
3EAC: 07 38           .DB $07, $38
3EAE: 06 48           .DB $06, $48
3EB0: 08 20           .DB $08, $20
3EB2: 07 30           .DB $07, $30
3EB4: 07 40           .DB $07, $40
3EB6: 07 50           .DB $07, $50
3EB8: 08 30           .DB $08, $30
3EBA: 08 40           .DB $08, $40
3EBC: 08 50           .DB $08, $50
3EBE: 08 60           .DB $08, $60
T3EC0:
3EC0: FF              .DB $FF
3EC1: 48 40 40 40     .DB $48, $40, $40, $40, $38, $30, $28, $38, $30, $28, $20, $30, $20, $30, $28
3EC5: 38 30 28 38
3EC9: 30 28 20 30
3ECD: 20 30 28
T3ED0:
3ED0: 01 01 01 01     .DB $01, $01, $01, $01
3ED4: 00 00 01 01     .DB $00, $00, $01, $01
3ED8: 00 01 01 01     .DB $00, $01, $01, $01
3EDC: 00 00 00 01     .DB $00, $00, $00, $01
3EE0: 05 04 03 02     .DB $05, $04, $03, $02, $01, $00
3EE4: 01 00
3EE6: 00 00 00 00     .DB $00, $00, $00, $00, $01, $01
3EEA: 01 01
3EEC: 01 01 02 02     .DB $01, $01, $02, $02
3EF0: 02 02 03 03     .DB $02, $02, $03, $03
3EF4: 03 04 04 04     .DB $03, $04, $04, $04
3EF8: 05 05 06 06     .DB $05, $05, $06, $06
3EFC: 07 08 07 06     .DB $07, $08, $07, $06
T3F00:
3F00: FF FF FF FF     .DB $FF, $FF, $FF, $FF ; not used
3F04: FF FF           .DB $FF, $FF ; not used
3F06: FF FF           .DB $FF, $FF, ; not used
3F08: 20 FF 02 FF     .DB $20, $FF, $02, $FF ; BC and DE register contents
3F0C: 36 D2           .DW L36D2 ; address to call
3F0E: 36 C0           .DW L36C0 ; address to call
3F10: 20 FF 03 FF     .DB $20, $FF, $03, $FF
3F14: 36 D2           .DW L36D2 ; address
3F16: 35 E0           .DW L35E0 ; address
3F18: 30 FF 04 FF     .DB $30, $FF, $04, $FF
3F1C: 36 D2           .DW L36D2 ; address
3F1E: 35 E0           .DW L35E0 ; address
3F20: 10 FF 05 FF     .DB $10, $FF, $05, $FF
3F24: 36 EA           .DW L36EA ; address
3F26: 35 E0           .DW L35E0 ; address
3F28: 10 FF 06 FF     .DB $10, $FF, $06, $FF
3F2C: 36 EA           .DW L36EA ; address
3F2E: 36 C0           .DW L36C0 ; address
3F30: 10 60 07 1F     .DB $10, $60, $07, $1F
3F34: 37 0A           .DW L370A ; address
3F36: 36 C0           .DW L36C0 ; address
3F38: F0 10 0B 1A     .DB $F0, $10, $0B, $1A
3F3C: 37 0A           .DW L370A ; address
3F3E: 36 C0           .DW L36C0 ; address
3F40: 40 FF 04 FF     .DB $40, $FF, $04, $FF
3F44: 36 EA           .DW L36EA, ; address
3F46: 36 C0           .DW L36C0 ; address
3F48: 10 FF 08 FF     .DB $10, $FF, $08, $FF
3F4C: 36 EA           .DW L36EA ; address
3F4E: 36 C0           .DW L36C0 ; address
3F50: 40 10 0F 17     .DB $40, $10, $0F, $17
3F54: 37 0A           .DW L370A ; address
3F56: 36 C0           .DW L36C0 ; address
3F58: 10 FF 0A FF     .DB $10, $FF, $0A, $FF
3F5C: 36 EA           .DW L36EA ; address
3F5E: 35 E0           .DW L35E0 ; address
3F60: FF FF FF FF     .DB $FF, $FF, $FF, $FF
3F64: 36 CC           .DW L36CC ; address
3F66: 35 E0           .DW L35E0 ; address
3F68: FF FF FF FF     .DB $FF, $FF, $FF, $FF
3F6C: 36 CC           .DW L36CC ; address
3F6E: 35 E0           .DW L35E0 ; address
3F70: 10 FF 06 FF     .DB $10, $FF, $06, $FF
3F74: 36 EA           .DW L36EA ; address
3F76: 35 E0           .DW L35E0 ; address
3F78: 10 10 07 79     .DB $10, $10, $07, $79
3F7C: 37 0A           .DW L370A ; address
3F7E: 35 E0           .DW L35E0 ; address
T3F80:
3F80: 01 48 EE 00     .DB $01, $48, $EE, $00, $10, $B0, $10, $20 ; 0
3F84: 10 B0 10 20
3F88: 01 49 2C 00     .DB $01, $49, $2C, $00, $10, $A0, $00, $B0 ; 1
3F8C: 10 A0 00 B0
3F90: 01 49 6A 00     .DB $01, $49, $6A, $00, $10, $90, $00, $B8 ; 2
3F94: 10 90 00 B8
3F98: 01 49 A8 00     .DB $01, $49, $A8, $00, $10, $80, $00, $C0 ; 3
3F9C: 10 80 00 C0
3FA0: 01 49 E6 00     .DB $01, $49, $E6, $00, $10, $70, $00, $C8 ; 4
3FA4: 10 70 00 C8
3FA8: 01 4A 24 00     .DB $01, $4A, $24, $00, $10, $60, $00, $C8 ; 5
3FAC: 10 60 00 C8
3FB0: 01 4A 62 00     .DB $01, $4A, $62, $00, $10, $50, $00, $C8 ; 6
3FB4: 10 50 00 C8
3FB8: 01 4A A0 00     .DB $01, $4A, $A0, $00, $10, $40, $00, $C8 ; 7
3FBC: 10 40 00 C8
3FC0: 01 4A CE 00     .DB $01, $4A, $CE, $00, $10, $38, $00, $B0 ; 0
3FC4: 10 38 00 B0
3FC8: 01 48 CC 00     .DB $01, $48, $CC, $00, $10, $B8, $10, $20 ; 1
3FCC: 10 B8 10 20
3FD0: 01 4A CA 00     .DB $01, $4A, $CA, $00, $10, $38, $00, $B8 ; 2
3FD4: 10 38 00 B8
3FD8: 01 48 C8 00     .DB $01, $48, $C8, $00, $10, $B8, $10, $18 ; 3
3FDC: 10 B8 10 18
3FE0: 01 4A C6 00     .DB $01, $4A, $C6, $00, $10, $38, $00, $C0 ; 4
3FE4: 10 38 00 C0
3FE8: 01 48 C4 00     .DB $01, $48, $C4, $00, $10, $B8, $10, $10 ; 5
3FEC: 10 B8 10 10
3FF0: 01 4A C2 00     .DB $01, $4A, $C2, $00, $10, $38, $00, $C8 ; 6
3FF4: 10 38 00 C8
3FF8: 01 48 C0 00     .DB $01, $48, $C0, $00, $10, $B8, $10, $08 ; 7
3FFC: 10 B8 10 08
