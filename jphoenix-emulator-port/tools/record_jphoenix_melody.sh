#!/bin/sh
# Run this locally (you have a working JDK 26) from the PHOENIX_THE_GAME folder.
# Produces jphoenix_tune3.wav: the same tune3 ("ESTUDIO", Phoenix's theme,
# SoundControlB=0xCF, SoundControlA=0x0f -- exactly what l3a10 writes at the
# start of a level) rendered by jphoenix-emulator-port's real MAME-verified
# Sound/TMS36XX engine, via the project's own SoundMameTraceReplay tool.
set -e
cd jphoenix-emulator-port

make compile
javac -cp build/classes -d build/classes tools/sound/SoundRenderUtil.java tools/sound/SoundMameTraceReplay.java

printf 'time_seconds,control,value\n0.0,A,0x0f\n0.0,B,0xCF\n' > /tmp/mame-events.csv
java -cp build/classes SoundMameTraceReplay /tmp/mame-events.csv ../melody-comparison/jphoenix_tune3.wav 15

echo "Done: melody-comparison/jphoenix_tune3.wav"
