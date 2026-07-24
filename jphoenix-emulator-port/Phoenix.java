/*	Java Phoenix Emulator v0.8
    Official Home-page: http://www3.brfree.com.br/vgc//hosted/muriloq/index2.html

    Emulator by Murilo Saraiva de Queiroz (muriloq@dcc.ufmg.br) based on
    Phoenix Emulator by Richard Davies (R.Davies@dcs.hull.ac.uk) and MAME
    project, by Nicola Salmoria (MC6489@mclink.it) and others.

    The emulator structure, and many solutions are based in Jasper, the
    Java Spectrum Emulator, by Adam Davidson & Andrew Pollard.
    Used with permission.

    The machine architecture information is from Ralph Kimmlingen
    (ub2f@rz.uni-karlsruhe.de).
*/

/* Phoenix Hardware Specification
Resolution 26x8 = 208 columns x 32x8 = 256 lines
Phoenix memory map

  0000-3fff 16Kb Program ROM
  4000-43ff 1Kb Video RAM Charset A (4340-43ff variables)
  4400-47ff 1Kb Work RAM
  4800-4bff 1Kb Video RAM Charset B (4840-4bff variables)
  4c00-4fff 1Kb Work RAM
  5000-53ff 1Kb Video Control write-only (mirrored)
  5400-47ff 1Kb Work RAM
  5800-5bff 1Kb Video Scroll Register (mirrored)
  5c00-5fff 1Kb Work RAM
  6000-63ff 1Kb Sound Control A (mirrored)
  6400-67ff 1Kb Work RAM
  6800-6bff 1Kb Sound Control B (mirrored)
  6c00-6fff 1Kb Work RAM
  7000-73ff 1Kb 8bit Game Control read-only (mirrored)
  7400-77ff 1Kb Work RAM
  7800-7bff 1Kb 8bit Dip Switch read-only (mirrored)
  7c00-7fff 1Kb Work RAM

  memory mapped ports:

    read-only:
    7000-73ff IN
    7800-7bff Dip-Switch Settings (DSW)

    * IN (all bits are inverted)
    * bit 7 : barrier
    * bit 6 : Left
    * bit 5 : Right
    * bit 4 : Fire
    * bit 3 : -
    * bit 2 : Start 2
    * bit 1 : Start 1
    * bit 0 : Coin

    * Dip-Switch Settings (DSW)
    * bit 7 : VBlank
    * bit 6 : free play (pleiads only)
    * bit 5 : attract sound 0 = off 1 = on (pleiads only?)
    * bit 4 : coins per play	0 = 1 coin	1 = 2 coins
    * bit 3 :\ bonus
    * bit 2 :/ 00 = 3000	01 = 4000  10 = 5000  11 = 6000
    * bit 1 :\ number of lives
    * bit 0 :/ 00 = 3  01 = 4  10 = 5  11 = 6

    Palette
    0 bit 5 of video ram value (divides 256 chars in 8 color sections)
    1 bit 6 of video ram value (divides 256 chars in 8 color sections)
    2 bit 7 of video ram value (divides 256 chars in 8 color sections)
    3 bit 0 of pixelcolor  (either from CHAR-A or CHAR-B, depends on Bit5)
    4 bit 1 of pixelcolor  (either from CHAR-A or CHAR-B, depends on Bit5)
    5 0 = CHAR-A, 1 = CHAR-B
    6 palette flag (video control register bit 1)
    7 always 0
*/

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URL;
import java.nio.file.Path;
import java.util.concurrent.ConcurrentLinkedQueue;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.TimeUnit;


public class Phoenix extends I8080 {
    private static final boolean DEBUG = Boolean.getBoolean("phoenix.debug");
    // Lockstep verification: dump 0x4000-0x4BFF each VBLANK to compare against the C port.
    private static final String RAMDUMP_PATH = System.getProperty("phoenix.ramdump");
    private static final String RUNTIME_CALL_TRACE_PATH = System.getProperty("phoenix.runtimecalltrace");
    private static final int RAMDUMP_FRAMES = Integer.getInteger("phoenix.ramdump.frames", 3600);
    private java.io.DataOutputStream ramDumpOut;
    private boolean ramDumpDisabled = false;
    private boolean ramDumpArmed = false;
    // Opt-in alternative input-script clock ("poll"): fire events indexed by
    // the game's own main-loop iteration (the WaitVBlankCoin poll, the same
    // deterministic moment the RAM dump uses) instead of raw vblank
    // interrupts. The C port counts frames per main-loop iteration, so this
    // is the only clock the two emulators share: real hardware sometimes
    // spends >1 vblank per loop iteration (e.g. the boot RAM clear), which
    // makes interrupt-indexed replays land on different game moments.
    // Default (unset) keeps the hardware-authentic interrupt clock.
    private static final boolean INPUT_CLOCK_POLL =
            "poll".equals(System.getProperty("phoenix.inputclock"));
    private boolean pollArmed = false;
    private int pollCounter = 0;
    private PhoenixInputScript inputScript;
    private PhoenixInputScript.Recorder inputRecorder;
    private PcCoverage pcCoverage;
    private RuntimeCallTrace runtimeCallTrace;
    private final PhoenixVideoRenderer videoRenderer = new PhoenixVideoRenderer();
    private final PhoenixFrameBuffer frameBuffer = new PhoenixFrameBuffer();
    private final int[] framePixels =
            new int[PhoenixFrameBuffer.WIDTH * PhoenixFrameBuffer.HEIGHT];
    private final int[][] videoRamPages = new int[2][0x1000];
    private int videoRamPage = 0;
    private int[] Character; // Caracteres decodificados

    private int savedHiScore=0;

    public static final int nPixelsWide = PhoenixFrameBuffer.WIDTH;
    public static final int nPixelsHigh = PhoenixFrameBuffer.HEIGHT;

    private byte[] chr = new byte [0x2000]; // CHARSET roms
    private int[] paletteColors;

    private int   vblankReadsRemaining = 0;
    private int   ScrollReg   = 0;
    private int   PaletteReg = 0;
    private volatile int gameControlState = 0xff;
    private int   interruptCounter = 0;
    private int   frameSkip = 1;
    private int   sleepHack = 5;
    private final boolean fastMode;
    private final int stopAfterFrames;
    private boolean resetAtNextInterrupt = false;
    private final Object pauseLock = new Object();
    private volatile boolean pauseAtNextInterrupt = false;
    private boolean refreshNextInterrupt = true;
    private int lastLoggedCounter98 = -1;
    private int lastLoggedForegroundChecksum = -1;
    private int lastLoggedBackgroundChecksum = -1;
    private int lastLogged43a2 = -1;
    private int lastLogged43a3 = -1;

    public  Thread  pausedThread = null;
    public  long  timeOfLastFrameInterrupt = 0;
    private long nextFrameTimeNanos = 0;
    private Sound sound;
    private final ConcurrentLinkedQueue<StateCommand> stateCommands =
            new ConcurrentLinkedQueue<StateCommand>();

    public Phoenix() {
        this(PcmSink.discarding());
    }

    public Phoenix(PcmSink pcmSink) {
        // Phoenix runs at 0.74 MHz.
        super(0.74);
        gameControlState = 0xff;
        sound = new Sound(pcmSink);
        fastMode = Boolean.getBoolean("phoenix.fast");
        stopAfterFrames = Integer.getInteger("phoenix.stopframes", 0);
        pcCoverage = PcCoverage.fromProperty("phoenix.pccoverage");
        if (RUNTIME_CALL_TRACE_PATH != null) {
            runtimeCallTrace = new RuntimeCallTrace();
        }
        loadInputScriptFromProperty();
        startInputRecorderFromProperty();
    }

    public PhoenixFrameBuffer frameBuffer() {
        return frameBuffer;
    }

    public boolean togglePause() {
        setPaused(!pauseAtNextInterrupt);
        return pauseAtNextInterrupt;
    }

    public boolean isPaused() {
        return pauseAtNextInterrupt;
    }

    public void setPaused(boolean paused) {
        synchronized (pauseLock) {
            pauseAtNextInterrupt = paused;
            if (!paused) {
                pauseLock.notifyAll();
            }
        }
    }

    public void stop() {
        setPaused(false);
        requestStop();
        sound.stop();
        stopInputRecorder();
        stopPcCoverage();
    }

    @Override
    protected void recordInstruction(int pc) {
        if (pcCoverage != null) {
            pcCoverage.record(pc);
        }
    }

    @Override
    protected void recordCall(int caller, int callee) {
        if (runtimeCallTrace != null) {
            runtimeCallTrace.record(caller, callee);
        }
    }

    @Override
    protected void executionFinished() {
        writeRuntimeCallTrace();
        stopInputRecorder();
        stopPcCoverage();
    }

    public void saveState(Path path) throws IOException {
        runStateCommand(() -> PhoenixSaveState.save(this, path));
    }

    public void loadState(Path path) throws IOException {
        runStateCommand(() -> PhoenixSaveState.load(this, path));
    }

    private void runStateCommand(StateOperation operation) throws IOException {
        if (!isExecuting() || isExecutionThread()) {
            operation.run();
            return;
        }
        StateCommand command = new StateCommand(operation);
        stateCommands.add(command);
        try {
            while (!command.completed.await(1, TimeUnit.SECONDS)) {
                if (!isExecuting() && stateCommands.remove(command)) {
                    throw new IOException("emulator stopped before save-state operation");
                }
            }
        } catch (InterruptedException e) {
            if (stateCommands.remove(command)) {
                Thread.currentThread().interrupt();
                throw new IOException("save-state operation interrupted", e);
            }
            boolean interrupted = true;
            while (true) {
                try {
                    command.completed.await();
                    break;
                } catch (InterruptedException ignored) {
                    interrupted = true;
                }
            }
            if (interrupted) {
                Thread.currentThread().interrupt();
            }
        }
        if (command.failure != null) {
            throw command.failure;
        }
    }

    private void processStateCommands() {
        StateCommand command;
        while ((command = stateCommands.poll()) != null) {
            try {
                command.operation.run();
            } catch (IOException e) {
                command.failure = e;
            } finally {
                command.completed.countDown();
            }
        }
    }


    /** Byte access */
    public void pokeb( int addr, int newByte ) {

        addr &= 0xffff;

        if ( addr >=  0x5800 && addr <= 0x5bff ) {
            ScrollReg = newByte;
        }

        if ( addr >= 0x5000 && addr <= 0x53ff ) {
            selectVideoRegister(newByte);
        }

        if ( addr >= 0x6000 && addr <= 0x63ff) {
            if ( peekb(addr)!=newByte ) {
                mem[addr] = newByte;
                if (DEBUG) {
                    System.out.println("Sound A = 0x" + Integer.toHexString(newByte & 0xff)
                            + " pc=0x" + Integer.toHexString(PC())
                            + " mode43a2=0x" + Integer.toHexString(mem[0x43a2] & 0xff)
                            + " mode43a3=0x" + Integer.toHexString(mem[0x43a3] & 0xff));
                }
                sound.updateControlA((byte)newByte, cycleInInterruptFrame(), cyclesPerInterrupt());
            }
        }

        if ( addr >= 0x6800 && addr <= 0x6bff ) {
            if ( peekb(addr)!=newByte ) {
                mem[ addr ] = newByte;
                if (DEBUG) {
                    System.out.println("Sound B = 0x" + Integer.toHexString(newByte & 0xff)
                            + " pc=0x" + Integer.toHexString(PC())
                            + " mode43a2=0x" + Integer.toHexString(mem[0x43a2] & 0xff)
                            + " mode43a3=0x" + Integer.toHexString(mem[0x43a3] & 0xff));
                }
                sound.updateControlB((byte) newByte, cycleInInterruptFrame(), cyclesPerInterrupt());
            }
        }

        // Hi Score Saving - Thanks MAME ! :)
        if ( addr == 0x438c ) {
            if ( newByte == 0x0f ) {
                mem[addr]=newByte;
                int hiScore = getScore(0x4388);
                if ( hiScore > savedHiScore ) hisave();
                if ( hiScore < savedHiScore ) hiload();
            }
        }
        if (DEBUG && shouldLogWrite(addr, newByte)) {
            System.out.println("Write 0x" + Integer.toHexString(addr)
                    + " = 0x" + Integer.toHexString(newByte & 0xff)
                    + " pc=0x" + Integer.toHexString(PC()));
        }
        if (addr >= 0x4000 && addr <= 0x4fff) {
            videoRamPages[videoRamPage][addr - 0x4000] = newByte & 0xff;
        }
        if ( addr >= 0x4000 ) {   // 0x0000 - 0x3fff Program ROM
            mem [addr]=newByte;
        }

        return;
    }

    /** Word access */
    public void pokew( int addr, int word ) {
        addr &= 0xffff;
        if ( addr >= 0x4000 ) {
            pokeb(addr, word & 0xff);
            if ( ++addr != 65536 ) {
                pokeb(addr, word >> 8);
            }
        }
        return;
    }

    private void selectVideoRegister(int value) {
        int newPage = value & 0x01;
        PaletteReg = (value >> 1) & 0x01;
        if (newPage == videoRamPage) {
            return;
        }

        System.arraycopy(mem, 0x4000, videoRamPages[videoRamPage], 0, 0x1000);
        videoRamPage = newPage;
        System.arraycopy(videoRamPages[videoRamPage], 0, mem, 0x4000, 0x1000);
    }

    int videoRamPage() {
        return videoRamPage;
    }

    int paletteBank() {
        return PaletteReg;
    }

    public int peekb( int addr ) {
        addr &= 0xffff;
        // decode the addresses (addr)
        if ( addr >= 0x7800 && addr <=0x7bff ) {
            if ( vblankReadsRemaining > 0 ) {
                vblankReadsRemaining--;
                return 128;
            } else {
                // First 0-read after the interrupt *from WaitVBlankCoin's
                // own wait loop* (reads at PC $0082/$0088, so PC() < $0100)
                // = the blanking flag clears = deterministic frame start of
                // the game loop. Dump here so records align with the C
                // port's dump point (start of wait_vblank_coin).
                // The PC gate matters: $7800 doubles as the DIP-switch port
                // and is also read mid-frame ($0161, $02D8, $0350, $14E1,
                // $17E0). Without the gate those reads consumed the armed
                // flags, skewing both the dump moment and the poll-indexed
                // input clock (each DSW read added a spurious tick).
                if (PC() < 0x0100) {
                    if (pollArmed) {
                        pollArmed = false;
                        pollCounter++;
                        if (inputScript != null && INPUT_CLOCK_POLL) {
                            // Mirror the C port's ordering: events for loop
                            // iteration N are applied before frame N's logic
                            // reads the inputs.
                            inputScript.applyDueEvents(pollCounter, this);
                        }
                    }
                    if (ramDumpArmed) {
                        ramDumpArmed = false;
                        dumpRamFrame();
                    }
                }
                return 0;
            }
        }
        if ( addr >= 0x7000 && addr <= 0x73ff ) {
            return gameControlState;
        }

        else  return mem[addr];

    }

    public int peekw( int addr ) {
        addr &= 0xffff;
        // decode the addresses (addr)
        if ( addr >= 0x7800 && addr <=0x7bff ) {
            if ( vblankReadsRemaining > 0 ) {
                vblankReadsRemaining--;
                return 128;
            } else
                return 0;
        }

        int      t = peekb( addr );
        addr++;
        return t | (peekb( addr ) << 8);
    }


    // The Hi Score is BCD (Binary Coded Decimal).
    // We convert this to integer here.
    public int getScore(int Addr) {
        int score=0;
        score += (peekb (Addr+3)/16) * 10     + (peekb (Addr+3) % 16);
        score += (peekb (Addr+2)/16) * 1000   + (peekb (Addr+2) % 16)*100;
        score += (peekb (Addr+1)/16) * 100000   + (peekb (Addr+1) % 16)*10000;
        score += (peekb (Addr)  /16) * 10000000 + (peekb (Addr) % 16)*1000000;
        return score;
    }

    public void hisave () {
        // Hi score saving. Again, thanks MAME project... :)
        int OneScore=getScore(0x4380);
        int TwoScore=getScore(0x4384);
        int HiScore=getScore(0x4388);
        int HiAddress = 0x4388;
        if ( OneScore > HiScore ) HiAddress=0x4380;
        if ( TwoScore > HiScore ) HiAddress=0x4384;


        try {
            // URL baseURL = applet.getDocumentBase();
            OutputStream os;
            /*
            if (baseURL != null) {
            URL scoreURL = new URL (baseURL, "hiscore.sav");
            URLConnection connection = new URLConnection (scoreURL);
            os = connection.getOutputStream();
            }
            else {
            */
            File scoreFile = new File ("hiscore.sav");
            os = new FileOutputStream (scoreFile);
            //}
            for ( int i=0;i<4;i++ ) {
                os.write ((byte) peekb(HiAddress+i));
            }
            os.flush();
            os.close();
        } catch ( Exception e ) {
            System.out.println ("Error saving high score");
        }
        savedHiScore = getScore (HiAddress);
        System.out.println ("High Score: "+savedHiScore+" saved.");
    }

    public void hiload () {
        int HiAddress = 0x4388;
        try {
            // URL baseURL = applet.getDocumentBase();
            InputStream is;
            /*
            if (baseURL != null) {
            URL scoreURL = new URL (baseURL, "hiscore.sav");
            URLConnection connection = new URLConnection (scoreURL);
            os = connection.getOutputStream();
            }
            else {
            */
            File scoreFile = new File ("hiscore.sav");
            is = new FileInputStream (scoreFile);
            //}
            for ( int i=0;i<4;i++ ) mem [HiAddress+i]=is.read ();
            is.close();
        } catch ( Exception e ) {
            System.out.println ("Error loading high score");
        }
        // Force hi score atualizing
        pokeb(0x41e1, (peekb(0x4389) / 16)+0x20);
        pokeb(0x41c1, (peekb(0x4389) & 0xf)+0x20);
        pokeb(0x41a1, (peekb(0x438a) / 16)+0x20);
        pokeb(0x4181, (peekb(0x438a) & 0xf)+0x20);
        pokeb(0x4161, (peekb(0x438b) / 16)+0x20);
        pokeb(0x4141, (peekb(0x438b) & 0xf)+0x20);

        savedHiScore = getScore(HiAddress);
        System.out.println ("High Score: "+savedHiScore+" loaded.");
    }

    /** Carga das roms */
    public void loadRom(URL baseURL) throws IOException {
        System.out.print ("Reading program roms... ");
        byte[] buffer = RomLoader.load(baseURL, RomLoader.PROGRAM);
        System.out.println(buffer.length + " bytes, SHA-256 ok");
        for (int i = 0; i < buffer.length; i++) {
            mem[i] = buffer[i] & 0xff;
        }
    }

    /** Carga dos bancos de caracteres*/
    public void loadChr(URL baseURL) throws IOException {
        System.out.print ("Reading character set roms... ");
        byte[] buffer = RomLoader.load(baseURL, RomLoader.GRAPHICS);
        System.out.println(buffer.length + " bytes, SHA-256 ok");
        for (int i = 0; i < buffer.length; i++) {
            chr[i] = buffer[i];
        }
        System.out.print("Reading palette PROM... ");
        byte[] paletteProm = RomLoader.load(baseURL, RomLoader.PALETTE);
        paletteColors = PhoenixPalette.decode(paletteProm);
        System.out.println("512 bytes, SHA-256 ok");
    }




    public final int interrupt() {
        processStateCommands();

        waitWhilePaused();

        if ( resetAtNextInterrupt ) {
            resetAtNextInterrupt = false;
            reset();
        }

        interruptCounter++;
        if (inputScript != null && !INPUT_CLOCK_POLL) {
            inputScript.applyDueEvents(interruptCounter, this);
        }
        pollArmed = true;

        if (RAMDUMP_PATH != null && !ramDumpDisabled && interruptCounter <= RAMDUMP_FRAMES) {
            ramDumpArmed = true; // actual dump happens at the vblank-clear read
        }

        vblankReadsRemaining = 2;

        if ( interruptCounter % frameSkip == 0 )  screenRefresh ();
        sound.endFrame();
        if (DEBUG && interruptCounter % 60 == 0) {
            int counter98 = ((mem[0x4398] & 0xff) << 8) | (mem[0x4399] & 0xff);
            int foregroundChecksum = checksum(0x4000, 0x400);
            int backgroundChecksum = checksum(0x4800, 0x400);
            if (counter98 != lastLoggedCounter98
                    || foregroundChecksum != lastLoggedForegroundChecksum
                    || backgroundChecksum != lastLoggedBackgroundChecksum) {
                lastLoggedCounter98 = counter98;
                lastLoggedForegroundChecksum = foregroundChecksum;
                lastLoggedBackgroundChecksum = backgroundChecksum;
                System.out.println("Frame " + interruptCounter
                        + " Counter98=0x" + Integer.toHexString(counter98)
                        + " mode43a2=0x" + Integer.toHexString(mem[0x43a2] & 0xff)
                        + " mode43a3=0x" + Integer.toHexString(mem[0x43a3] & 0xff)
                        + " coins=0x" + Integer.toHexString(mem[0x438f] & 0xff)
                        + " scroll=0x" + Integer.toHexString(ScrollReg & 0xff)
                        + " page=0x" + Integer.toHexString(videoRamPage)
                        + " palette=0x" + Integer.toHexString(PaletteReg & 0xff)
                        + " fg=0x" + Integer.toHexString(foregroundChecksum)
                        + " bg=0x" + Integer.toHexString(backgroundChecksum)
                        + " pc=0x" + Integer.toHexString(PC()));
            }
        }

        if (stopAfterFrames > 0 && interruptCounter >= stopAfterFrames) {
            requestStop();
        }
        if (!fastMode) {
            paceFrame();
        }

        return super.interrupt();
    }

    private void waitWhilePaused() {
        synchronized (pauseLock) {
            if (!pauseAtNextInterrupt) {
                pausedThread = null;
                return;
            }
            pausedThread = Thread.currentThread();
            while (pauseAtNextInterrupt) {
                try {
                    pauseLock.wait();
                } catch (InterruptedException ignored) {
                }
            }
            pausedThread = null;
        }
    }

    void writeState(java.io.DataOutput output) throws IOException {
        writeCpuState(output);
        System.arraycopy(mem, 0x4000, videoRamPages[videoRamPage], 0, 0x1000);
        output.writeInt(videoRamPage);
        for (int[] page : videoRamPages) {
            for (int value : page) {
                output.writeByte(value);
            }
        }
        output.writeInt(savedHiScore);
        output.writeInt(vblankReadsRemaining);
        output.writeInt(ScrollReg);
        output.writeInt(PaletteReg);
        output.writeInt(interruptCounter);
        output.writeInt(frameSkip);
        output.writeBoolean(resetAtNextInterrupt);
        output.writeBoolean(refreshNextInterrupt);
        sound.writeState(output);
    }

    void readState(java.io.DataInput input) throws IOException {
        readCpuState(input);
        int savedVideoRamPage = input.readInt();
        if (savedVideoRamPage < 0 || savedVideoRamPage >= videoRamPages.length) {
            throw new IOException("invalid video RAM page");
        }
        for (int[] page : videoRamPages) {
            for (int i = 0; i < page.length; i++) {
                page[i] = input.readUnsignedByte();
            }
        }
        videoRamPage = savedVideoRamPage;
        for (int i = 0; i < 0x1000; i++) {
            if ((mem[0x4000 + i] & 0xff) != videoRamPages[videoRamPage][i]) {
                throw new IOException("active video RAM page is inconsistent");
            }
        }
        savedHiScore = input.readInt();
        vblankReadsRemaining = input.readInt();
        ScrollReg = input.readInt();
        PaletteReg = input.readInt();
        interruptCounter = input.readInt();
        frameSkip = input.readInt();
        resetAtNextInterrupt = input.readBoolean();
        refreshNextInterrupt = input.readBoolean();
        if (vblankReadsRemaining < 0 || vblankReadsRemaining > 2
                || (PaletteReg & ~1) != 0 || frameSkip < 1) {
            throw new IOException("invalid Phoenix machine state");
        }
        sound.readState(input);

        gameControlState = 0xff;
        setPaused(false);
        pausedThread = null;
        ramDumpArmed = false;
        nextFrameTimeNanos = 0;
        lastLoggedCounter98 = -1;
        lastLoggedForegroundChecksum = -1;
        lastLoggedBackgroundChecksum = -1;
        lastLogged43a2 = -1;
        lastLogged43a3 = -1;
        screenRefresh();
    }

    @FunctionalInterface
    private interface StateOperation {
        void run() throws IOException;
    }

    private static final class StateCommand {
        final StateOperation operation;
        final CountDownLatch completed = new CountDownLatch(1);
        volatile IOException failure;

        StateCommand(StateOperation operation) {
            this.operation = operation;
        }
    }

    /** Record format per frame: 4-byte big-endian frame number + 3072 bytes RAM (0x4000-0x4BFF). */
    private void dumpRamFrame() {
        try {
            if (ramDumpOut == null) {
                ramDumpOut = new java.io.DataOutputStream(
                        new java.io.BufferedOutputStream(new java.io.FileOutputStream(RAMDUMP_PATH)));
                System.out.println("RAM dump to " + RAMDUMP_PATH + " for " + RAMDUMP_FRAMES + " frames");
            }
            ramDumpOut.writeInt(interruptCounter);
            for (int a = 0x4000; a < 0x4c00; a++) {
                ramDumpOut.writeByte(mem[a]);
            }
            if (interruptCounter == RAMDUMP_FRAMES) {
                ramDumpOut.close();
                ramDumpOut = null;
                System.out.println("RAM dump complete (" + RAMDUMP_FRAMES + " frames)");
            } else {
                ramDumpOut.flush();
            }
        } catch (java.io.IOException e) {
            System.out.println("RAM dump failed, disabling: " + e.getMessage());
            ramDumpOut = null;
            ramDumpDisabled = true;
        }
    }

    private void paceFrame() {
        long frameNanos = 1_000_000_000L / 60L;
        long now = System.nanoTime();
        if (nextFrameTimeNanos == 0 || now > nextFrameTimeNanos + frameNanos) {
            nextFrameTimeNanos = now + frameNanos;
            return;
        }
        long sleepNanos = nextFrameTimeNanos - now;
        if (sleepNanos > 0) {
            try {
                Thread.sleep(sleepNanos / 1_000_000L, (int)(sleepNanos % 1_000_000L));
            } catch (InterruptedException ignored) {
            }
        }
        nextFrameTimeNanos += frameNanos;
    }

    private int checksum(int start, int length) {
        int sum = 0;
        for (int i = 0; i < length; i++) {
            sum = (sum * 31 + (mem[start + i] & 0xff)) & 0xffff;
        }
        return sum;
    }

    private boolean shouldLogWrite(int addr, int newByte) {
        newByte &= 0xff;
        if (addr == 0x438f || addr == 0x4142) {
            return true;
        }
        if (addr == 0x43a2 && newByte != lastLogged43a2) {
            lastLogged43a2 = newByte;
            return true;
        }
        if (addr == 0x43a3 && newByte != lastLogged43a3) {
            lastLogged43a3 = newByte;
            return true;
        }
        return false;
    }

    private void loadInputScriptFromProperty() {
        String path = System.getProperty("phoenix.inputscript");
        if (path == null || path.isEmpty()) {
            return;
        }
        try {
            inputScript = PhoenixInputScript.load(Path.of(path));
        } catch (IOException e) {
            System.out.println("Input script failed to open " + path + ", disabling");
        }
    }

    private void startInputRecorderFromProperty() {
        String path = System.getProperty("phoenix.recordinput");
        if (path == null || path.isEmpty()) {
            return;
        }
        try {
            inputRecorder = new PhoenixInputScript.Recorder(Path.of(path));
        } catch (IOException e) {
            System.out.println("Input recording failed to open " + path + ", disabling");
        }
    }

    private void stopInputRecorder() {
        if (inputRecorder == null) {
            return;
        }
        try {
            inputRecorder.close();
        } catch (IOException e) {
            System.out.println("Input recording failed to close cleanly: " + e.getMessage());
        } finally {
            inputRecorder = null;
        }
    }

    private void stopPcCoverage() {
        if (pcCoverage == null) {
            return;
        }
        try {
            pcCoverage.close();
        } catch (IOException e) {
            System.out.println("PC coverage failed to close cleanly: " + e.getMessage());
        } finally {
            pcCoverage = null;
        }
    }

    private void writeRuntimeCallTrace() {
        if (runtimeCallTrace == null) {
            return;
        }
        try {
            runtimeCallTrace.write(java.nio.file.Path.of(RUNTIME_CALL_TRACE_PATH));
            System.out.println("Runtime call trace written to " + RUNTIME_CALL_TRACE_PATH);
        } catch (IOException e) {
            System.out.println("Runtime call trace failed: " + e.getMessage());
        } finally {
            runtimeCallTrace = null;
        }
    }

    public void screenRefresh () {
        if (Character == null) {
            return;
        }
        videoRenderer.render(mem, Character, PaletteReg, ScrollReg, framePixels);
        frameBuffer.publish(framePixels);
    }

    public void decodeChars () {
        if (paletteColors == null) {
            throw new IllegalStateException("palette PROMs have not been loaded");
        }
        /* Due the lack of explicit pointers, and the inefficiency of the use of a
        great number of Image objects, I've decided to apply an non-conventional
        approach. All game graphics is kept in a invisible region of the buffer
        image. When one is necessary, I've simply copy the image from a region to
        another. It's not elegant, nor efficient: unfortunately, it's the only
        choice I Know... :)
          */
        Character = new int[2*512*64];
        byte[] pixelIndices = PhoenixGraphicsDecoder.decode(chr);
        System.out.print ("Decoding character sets to off-screen buffer...");

        for ( int s=0;s<2;s++ ) {             // Charset
            for ( int c=0;c<256;c++ ) {         // Character
                int pixelOffset = (s * 256 + c) * 64;
                for (int pixel = 0; pixel < 64; pixel++) {
                    int pixelValue = pixelIndices[pixelOffset + pixel] & 0xff;
                    for (int palette = 0; palette < 2; palette++) {
                        int colorGroup =
                                (c >> 5)
                                        | (s << 3)
                                        | (palette << 4);
                        int color = paletteColors[colorGroup * 4 + pixelValue];
                        if (color == 0xff000000) color = 0; // Transparency
                        Character[palette * 512 * 64 + pixelOffset + pixel] = color;
                    }
                }
            } // for c

        } // for s

        System.out.println ("Ok.");

    }
    public final boolean doKey( int down, int ascii) {
        int bit = -1;
        switch ( ascii ) {
        case '3':  bit = 0;    break; // Coin
        case '1':  bit = 1;    break; // Start 1
        case '2':  bit = 2;    break; // Start 2
        case 32 :  bit = 4;    break; // Fire
            // RIGHT = 1007 LEFT = 1006 DOWN = 1005
        case 1007:   bit = 5;    break; // Right
        case 1006:   bit = 6;    break; // Left
        case 1005:   bit = 7;    break; // Barrier

        case 'b':  bit = 7;    break; // Barrier

        case '[':  frameSkip-=down;
            if ( frameSkip < 1 ) frameSkip = 1; // Decrease frame rate
            System.out.println ("Frame Skip:"+frameSkip);break;
        case ']':  frameSkip+=down;       // Increase frame rate
            System.out.println ("Frame Skip:"+frameSkip);
            break;
        }
        if (bit >= 0) {
            int mask = 1 << bit;
            boolean press = down == 1;
            boolean wasPressed = (gameControlState & mask) == 0;
            if (wasPressed != press) {
                applyInputEvent(mask, press);
                if (inputRecorder != null) {
                    inputRecorder.record(interruptCounter + 1, mask, press);
                }
            }
        }
        return true;
    }

    void applyInputEvent(int mask, boolean press) {
        if (press) {
            gameControlState &= ~mask;
        } else {
            gameControlState |= mask;
        }
    }

    int gameControlStateForTest() {
        return gameControlState;
    }

}
