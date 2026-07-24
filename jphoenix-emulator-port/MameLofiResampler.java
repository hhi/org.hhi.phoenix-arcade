final class MameLofiResampler {
	interface Source {
		double nextSample();
	}

	static final int PHASE_ONE = 0x1000000;
	static final int PHASE_MASK = PHASE_ONE - 1;
	private static final float[][] INTERPOLATION = createInterpolation();

	private final int sourceDivide;
	private final int step;
	private int phase;
	private float s0;
	private float s1;
	private float s2;
	private float s3;

	MameLofiResampler(int sourceRate, int targetRate) {
		if (sourceRate <= 0 || targetRate <= 0) {
			throw new IllegalArgumentException("Sample rates must be positive");
		}
		sourceDivide = sourceRate <= targetRate ? 1 : 1 + sourceRate / targetRate;
		step = (int) ((long) sourceRate * PHASE_ONE / targetRate / sourceDivide);
	}

	double nextSample(Source source) {
		int currentPhase = phase >>> 12;
		float output =
				-s0 * INTERPOLATION[0][0x1000 - currentPhase]
				+ s1 * INTERPOLATION[1][0x1000 - currentPhase]
				+ s2 * INTERPOLATION[1][currentPhase]
				- s3 * INTERPOLATION[0][currentPhase];

		phase += step;
		if ((phase & PHASE_ONE) != 0) {
			phase &= PHASE_MASK;
			s0 = s1;
			s1 = s2;
			s2 = s3;
			s3 = readSource(source);
		}
		return output;
	}

	private float readSource(Source source) {
		float sum = 0.0f;
		for (int i = 0; i < sourceDivide; i++) {
			sum += (float) source.nextSample();
		}
		return sum / sourceDivide;
	}

	int sourceDivide() {
		return sourceDivide;
	}

	int step() {
		return step;
	}

	void writeState(java.io.DataOutput output) throws java.io.IOException {
		output.writeInt(sourceDivide);
		output.writeInt(step);
		output.writeInt(phase);
		output.writeFloat(s0);
		output.writeFloat(s1);
		output.writeFloat(s2);
		output.writeFloat(s3);
	}

	void readState(java.io.DataInput input) throws java.io.IOException {
		int savedSourceDivide = input.readInt();
		int savedStep = input.readInt();
		if (savedSourceDivide != sourceDivide || savedStep != step) {
			throw new java.io.IOException("audio resampler configuration mismatch");
		}
		phase = input.readInt();
		if ((phase & ~PHASE_MASK) != 0) {
			throw new java.io.IOException("invalid audio resampler phase");
		}
		s0 = input.readFloat();
		s1 = input.readFloat();
		s2 = input.readFloat();
		s3 = input.readFloat();
	}

	static float interpolation(int lane, int index) {
		return INTERPOLATION[lane][index];
	}

	private static float[][] createInterpolation() {
		float[][] table = new float[2][0x1001];
		for (int i = 1; i < 4096; i++) {
			float p = i / 4096.0f;
			table[0][i] = (p - p * p * p) / 6.0f;
		}
		for (int i = 1; i < 2049; i++) {
			float p = i / 4096.0f;
			table[1][i] = p + (p * p - p * p * p) / 2.0f;
		}
		for (int i = 2049; i < 4096; i++) {
			table[1][i] = 1.0f + table[0][i] + table[0][4096 - i] - table[1][4096 - i];
		}
		table[0][0] = 0.0f;
		table[0][0x1000] = 0.0f;
		table[1][0] = 0.0f;
		table[1][0x1000] = 1.0f;
		return table;
	}
}
