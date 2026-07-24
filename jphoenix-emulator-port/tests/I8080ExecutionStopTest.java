public final class I8080ExecutionStopTest {
    private I8080ExecutionStopTest() {
    }

    public static void main(String[] args) {
        StoppableCpu cpu = new StoppableCpu();
        cpu.execute();
        if (cpu.interrupts != 1) {
            throw new AssertionError("expected one interrupt before stop, got " + cpu.interrupts);
        }
        System.out.println("ok - CPU execution stop");
    }

    private static final class StoppableCpu extends I8080 {
        int interrupts;

        StoppableCpu() {
            super(0.01);
        }

        @Override
        public int interrupt() {
            interrupts++;
            requestStop();
            return 0;
        }
    }
}
