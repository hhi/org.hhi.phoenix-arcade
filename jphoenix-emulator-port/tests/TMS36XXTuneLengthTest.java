public final class TMS36XXTuneLengthTest {
    private TMS36XXTuneLengthTest() {
    }

    public static void main(String[] args) {
        for (int tune = 1; tune <= 3; tune++) {
            TMS36XX chip = new TMS36XX();
            chip.mm6221aa_tune_w(tune);

            int expectedNotes = TMS36XX.tunes[tune].length / 6;
            if (chip.tune_max != expectedNotes) {
                throw new AssertionError(
                        "Tune " + tune + " expected " + expectedNotes
                                + " notes, got " + chip.tune_max);
            }
        }

        TMS36XX chip = new TMS36XX();
        chip.mm6221aa_tune_w(1);
        chip.mm6221aa_tune_w(0);
        if (chip.tune_max != 0) {
            throw new AssertionError("Tune 0 must not select melody notes");
        }
    }
}
