public class TMS36XX {

	public static final boolean VERBOSE = false;
	public static final int VMIN = 0x0000;
	public static final int VMAX = 0x7fff;

	/* the frequencies are later adjusted by "* clock / FSCALE" */
	public static final int FSCALE = 1024;

	String subtype; /* subtype name MM6221AA, TMS3615 or TMS3617 */
	int channel; /* returned by stream_init() */

	int samplerate; /* MAME uses clock * 64 */

	int basefreq = 372; /* chip's base frequency */
	int octave; /* octave select of the TMS3615 */

	int speed = (int) (VMAX / 0.21); /* speed of the tune */
	int tune_counter; /* tune counter */
	int note_counter; /* note counter */

	int voices; /* active voices */
	int shift; /* shift toggles between 0 and 6 to allow decaying voices */
	int vol[] = new int[12]; /* (decaying) volume of harmonics notes */
	int vol_counter[] = new int[12]; /* volume adjustment counter */
	int decay[] = { (int) (VMAX / 0.50), 0, 0, (int) (VMAX / 1.05), 0, 0,
			(int) (VMAX / 0.50), 0, 0, (int) (VMAX / 1.05), 0, 0 }; /*
																	 * volume
																	 * adjustment
																	 * rate -
																	 * dervied
																	 * from
																	 * decay
																	 */

	int counter[] = new int[12]; /* tone frequency counter */
	int frequency[] = new int[12]; /* tone frequency */
	int output; /* output signal bits */
	int enable; /* mask which harmonics */
	int tune_num; /* tune currently playing */
	int tune_ofs; /* note currently playing */
	int tune_max; /* end of tune */
	private int resampleOutputRate;
	private MameLofiResampler resampler;
	private final MameLofiResampler.Source resampleSource = this::renderInternalSample;

	public static final int C(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.18921);
	} /* 2^(3/12) */

	public static final int Cx(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.25992);
	} /* 2^(4/12) */

	public static final int D(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.33484);
	} /* 2^(5/12) */

	public static final int Dx(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.41421);
	} /* 2^(6/12) */

	public static final int E(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.49831);
	} /* 2^(7/12) */

	public static final int F(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.58740);
	} /* 2^(8/12) */

	public static final int Fx(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.68179);
	} /* 2^(9/12) */

	public static final int G(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.78180);
	} /* 2^(10/12) */

	public static final int Gx(int n) {
		return (int) ((FSCALE << (n - 1)) * 1.88775);
	} /* 2^(11/12) */

	public static final int A(int n) {
		return FSCALE << n;
	} /* A */

	public static final int Ax(int n) {
		return (int) ((FSCALE << n) * 1.05946);
	} /* 2^(1/12) */

	public static final int B(int n) {
		return (int) ((FSCALE << n) * 1.12246);
	} /* 2^(2/12) */

	/*
	 * Alarm sound? It is unknown what this sound is like. Until somebody
	 * manages trigger sound #1 of the Phoenix PCB sound chip I put just
	 * something 'alarming' in here.
	 */
	public static int[] tune1 = { C(3), 0, 0, C(2), 0, 0, G(3), 0, 0, 0, 0, 0,
			C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0,
			G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0,
			C(3), 0, 0, C(4), 0, 0, G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0,
			G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0,
			C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0, C(3), 0, 0, C(2), 0, 0,
			G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0,
			C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0,
			G(3), 0, 0, 0, 0, 0, C(3), 0, 0, C(4), 0, 0, G(3), 0, 0, 0, 0, 0,
			C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0,
			G(3), 0, 0, 0, 0, 0, C(3), 0, 0, 0, 0, 0, G(3), 0, 0, 0, 0, 0, };

	/*
	 * Fuer Elise, Beethoven (Excuse my non-existent musical skill, Mr. B ;-)
	 */
	public static int tune2[] = { D(3), D(4), D(5), 0, 0, 0, Cx(3), Cx(4),
			Cx(5), 0, 0, 0, D(3), D(4), D(5), 0, 0, 0, Cx(3), Cx(4), Cx(5), 0,
			0, 0, D(3), D(4), D(5), 0, 0, 0, A(2), A(3), A(4), 0, 0, 0, C(3),
			C(4), C(5), 0, 0, 0, Ax(2), Ax(3), Ax(4), 0, 0, 0, G(2), G(3),
			G(4), 0, 0, 0, D(1), D(2), D(3), 0, 0, 0, G(1), G(2), G(3), 0, 0,
			0, Ax(1), Ax(2), Ax(3), 0, 0, 0,

			D(2), D(3), D(4), 0, 0, 0, G(2), G(3), G(4), 0, 0, 0, A(2), A(3),
			A(4), 0, 0, 0, D(1), D(2), D(3), 0, 0, 0, A(1), A(2), A(3), 0, 0,
			0, D(2), D(3), D(4), 0, 0, 0, Fx(2), Fx(3), Fx(4), 0, 0, 0, A(2),
			A(3), A(4), 0, 0, 0, Ax(2), Ax(3), Ax(4), 0, 0, 0, D(1), D(2),
			D(3), 0, 0, 0, G(1), G(2), G(3), 0, 0, 0, Ax(1), Ax(2), Ax(3), 0,
			0, 0,

			D(3), D(4), D(5), 0, 0, 0, Cx(3), Cx(4), Cx(5), 0, 0, 0, D(3),
			D(4), D(5), 0, 0, 0, Cx(3), Cx(4), Cx(5), 0, 0, 0, D(3), D(4),
			D(5), 0, 0, 0, A(2), A(3), A(4), 0, 0, 0, C(3), C(4), C(5), 0, 0,
			0, Ax(2), Ax(3), Ax(4), 0, 0, 0, G(2), G(3), G(4), 0, 0, 0, D(1),
			D(2), D(3), 0, 0, 0, G(1), G(2), G(3), 0, 0, 0, Ax(1), Ax(2),
			Ax(3), 0, 0, 0,

			D(2), D(3), D(4), 0, 0, 0, G(2), G(3), G(4), 0, 0, 0, A(2), A(3),
			A(4), 0, 0, 0, D(1), D(2), D(3), 0, 0, 0, A(1), A(2), A(3), 0, 0,
			0, D(2), D(3), D(4), 0, 0, 0, Ax(2), Ax(3), Ax(4), 0, 0, 0, A(2),
			A(3), A(4), 0, 0, 0, 0, 0, 0, G(2), G(3), G(4), D(1), D(2), D(3),
			0, 0, 0, G(1), G(2), G(3), 0, 0, 0, 0, 0, 0, 0, 0, 0 };

	/*
	 * The theme from Phoenix, a sad little tune. Gerald Coy: The starting song
	 * from Phoenix is coming from a old french movie and it's called : "Jeux
	 * interdits" which means "unallowed games" ;-) Mirko Buffoni: It's called
	 * "Sogni proibiti" in italian, by Anonymous. Magic*: This song is a
	 * classical piece called "ESTUDIO" from M.A.Robira.
	 */
	public static int tune3[] = { A(2), A(3), A(4), D(1), D(2), D(3), 0, 0, 0,
			0, 0, 0, A(2), A(3), A(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, A(2), A(3),
			A(4), 0, 0, 0, 0, 0, 0, 0, 0, 0,

			A(2), A(3), A(4), A(1), A(2), A(3), 0, 0, 0, 0, 0, 0, G(2), G(3),
			G(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, F(2), F(3), F(4), 0, 0, 0, 0, 0,
			0, 0, 0, 0,

			F(2), F(3), F(4), F(1), F(2), F(3), 0, 0, 0, 0, 0, 0, E(2), E(3),
			E(4), F(1), F(2), F(3), 0, 0, 0, 0, 0, 0, D(2), D(3), D(4), F(1),
			F(2), F(3), 0, 0, 0, 0, 0, 0,

			D(2), D(3), D(4), A(1), A(2), A(3), 0, 0, 0, 0, 0, 0, F(2), F(3),
			F(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, A(2), A(3), A(4), 0, 0, 0, 0, 0,
			0, 0, 0, 0,

			D(3), D(4), D(5), D(1), D(2), D(3), 0, 0, 0, 0, 0, 0, 0, 0, 0,
			D(1), D(2), D(3), 0, 0, 0, F(1), F(2), F(3), 0, 0, 0, A(1), A(2),
			A(3), 0, 0, 0, D(2), D(2), D(2),

			D(3), D(4), D(5), D(1), D(2), D(3), 0, 0, 0, 0, 0, 0, C(3), C(4),
			C(5), 0, 0, 0, 0, 0, 0, 0, 0, 0, Ax(2), Ax(3), Ax(4), 0, 0, 0, 0,
			0, 0, 0, 0, 0,

			Ax(2), Ax(3), Ax(4), Ax(1), Ax(2), Ax(3), 0, 0, 0, 0, 0, 0, A(2),
			A(3), A(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, G(2), G(3), G(4), 0, 0, 0,
			0, 0, 0, 0, 0, 0,

			G(2), G(3), G(4), G(1), G(2), G(3), 0, 0, 0, 0, 0, 0, A(2), A(3),
			A(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, Ax(2), Ax(3), Ax(4), 0, 0, 0, 0,
			0, 0, 0, 0, 0,

			A(2), A(3), A(4), A(1), A(2), A(3), 0, 0, 0, 0, 0, 0, Ax(2), Ax(3),
			Ax(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, A(2), A(3), A(4), 0, 0, 0, 0, 0,
			0, 0, 0, 0,

			Cx(3), Cx(4), Cx(5), A(1), A(2), A(3), 0, 0, 0, 0, 0, 0, Ax(2),
			Ax(3), Ax(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, A(2), A(3), A(4), 0, 0, 0,
			0, 0, 0, 0, 0, 0,

			A(2), A(3), A(4), F(1), F(2), F(3), 0, 0, 0, 0, 0, 0, G(2), G(3),
			G(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, F(2), F(3), F(4), 0, 0, 0, 0, 0,
			0, 0, 0, 0,

			F(2), F(3), F(4), D(1), D(2), D(3), 0, 0, 0, 0, 0, 0, E(2), E(3),
			E(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, D(2), D(3), D(4), 0, 0, 0, 0, 0,
			0, 0, 0, 0,

			E(2), E(3), E(4), E(1), E(2), E(3), 0, 0, 0, 0, 0, 0, E(2), E(3),
			E(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, E(2), E(3), E(4), 0, 0, 0, 0, 0,
			0, 0, 0, 0,

			E(2), E(3), E(4), Ax(1), Ax(2), Ax(3), 0, 0, 0, 0, 0, 0, F(2),
			F(3), F(4), 0, 0, 0, 0, 0, 0, 0, 0, 0, E(2), E(3), E(4), F(1),
			F(2), F(3), 0, 0, 0, 0, 0, 0,

			D(2), D(3), D(4), D(1), D(2), D(3), 0, 0, 0, 0, 0, 0, F(2), F(3),
			F(4), A(1), A(2), A(3), 0, 0, 0, 0, 0, 0, A(2), A(3), A(4), F(1),
			F(2), F(3), 0, 0, 0, 0, 0, 0,

			D(3), D(4), D(5), D(1), D(2), D(3), 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
			0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0 };

	/* This is used to play single notes for the TMS3615/TMS3617 */
	public static int tune4[] = {
	/* 16' 8' 5 1/3' 4' 2 2/3' 2' */
	B(0), B(1), Dx(2), B(2), Dx(3), B(3), C(1), C(2), E(2), C(3), E(3), C(4),
			Cx(1), Cx(2), F(2), Cx(3), F(3), Cx(4), D(1), D(2), Fx(2), D(3),
			Fx(3), D(4), Dx(1), Dx(2), G(2), Dx(3), G(3), Dx(4), E(1), E(2),
			Gx(2), E(3), Gx(3), E(4), F(1), F(2), A(2), F(3), A(3), F(4),
			Fx(1), Fx(2), Ax(2), Fx(3), Ax(3), Fx(4), G(1), G(2), B(2), G(3),
			B(3), G(4), Gx(1), Gx(2), C(3), Gx(3), C(4), Gx(4), A(1), A(2),
			Cx(3), A(3), Cx(4), A(4), Ax(1), Ax(2), D(3), Ax(3), D(4), Ax(4),
			B(1), B(2), Dx(3), B(3), Dx(4), B(4) };

	public static int[][] tunes = { null, tune1, tune2, tune3, tune4 };

	public void DECAY(int voice) {
		if (vol[voice] > VMIN) {
			/* decay of first voice */
			vol_counter[voice] -= decay[voice];
			while (vol_counter[voice] <= 0) {
				vol_counter[voice] += samplerate;
				if (vol[voice]-- <= VMIN) {
					frequency[voice] = 0;
					vol[voice] = VMIN;
					break;
				}
			}
		}
	}

	public void RESTART(int voice) {
		if ((tunes[tune_num][tune_ofs * 6 + voice]) != 0) {
			frequency[shift + voice] = tunes[tune_num][tune_ofs * 6 + voice]
					* (basefreq << octave) / FSCALE;
			vol[shift + voice] = VMAX;
		}
	}

	public int TONE(int voice, int sum) {
		if (((enable & (1 << voice)) != 0) && (frequency[voice]) != 0) {
			/* first note */
			counter[voice] -= frequency[voice];
			while (counter[voice] <= 0) {
				counter[voice] += samplerate;
				output ^= 1 << voice;
			}
			if ((output & enable & (1 << voice)) != 0)
				sum += vol[voice];
		}
		return sum;
	}

	public synchronized double nextSample(int outputRate) {
		if (outputRate <= 0) {
			throw new IllegalArgumentException("outputRate must be positive");
		}
		if (outputRate != resampleOutputRate) {
			resampleOutputRate = outputRate;
			resampler = new MameLofiResampler(samplerate, outputRate);
		}
		return resampler.nextSample(resampleSource);
	}

	private double renderInternalSample() {
		if ((tunes[tune_num] == null) || voices == 0)
			return 0.0;

		int sum = 0;

		DECAY(0);
		DECAY(1);
		DECAY(2);
		DECAY(3);
		DECAY(4);
		DECAY(5);
		DECAY(6);
		DECAY(7);
		DECAY(8);
		DECAY(9);
		DECAY(10);
		DECAY(11);

		tune_counter -= speed;
		if (tune_counter <= 0) {
			int n = (-tune_counter / samplerate) + 1;
			tune_counter += n * samplerate;

			if ((note_counter -= n) <= 0) {
				note_counter += VMAX;
				if (tune_ofs < tune_max) {
					shift ^= 6;
					RESTART(0);
					RESTART(1);
					RESTART(2);
					RESTART(3);
					RESTART(4);
					RESTART(5);
					tune_ofs++;
				}
			}
		}

		sum = TONE(0, sum);
		sum = TONE(1, sum);
		sum = TONE(2, sum);
		sum = TONE(3, sum);
		sum = TONE(4, sum);
		sum = TONE(5, sum);
		sum = TONE(6, sum);
		sum = TONE(7, sum);
		sum = TONE(8, sum);
		sum = TONE(9, sum);
		sum = TONE(10, sum);
		sum = TONE(11, sum);

		return sum / (double) (32768 * voices);
	}

	synchronized double nextInternalSampleForTest() {
		return renderInternalSample();
	}

	public void reset_counters() {

		tune_counter = 0;
		note_counter = 0;
		vol_counter = new int[vol_counter.length];
		counter = new int[counter.length];
	}

	synchronized void mm6221aa_tune_w(int tune) {
		/* which tune? */
		tune &= 3;
		if (tune == tune_num)
			return;

		// System.out.println(("%s tune:%X\n", subtype, tune));

		/* update the stream before changing the tune */
		// stream_update(channel,0);
		tune_num = tune;
		tune_ofs = 0;
		tune_max = tunes[tune_num] == null ? 0 : tunes[tune_num].length / 6;
	}

	public synchronized void note_w(int octave, int note) {
		octave &= 3;
		note &= 15;

		if (note > 12)
			return;

		// System.out.println(("%s octave:%X note:%X\n", tms->subtype, octave,
		// note));

		/* update the stream before changing the tune */
		// stream_update(tms->channel,0);
		/* play a single note from 'tune 4', a list of the 13 tones */
		reset_counters();
		this.octave = octave;
		tune_num = 4;
		tune_ofs = note;
		tune_max = note + 1;
	}

	public synchronized void tms3617_enable_w(int enable) {
		tms3617_enable(enable);
	}

	private void tms3617_enable(int enable) {

		int i, bits = 0;

		/* duplicate the 6 voice enable bits */
		enable = (enable & 0x3f) | ((enable & 0x3f) << 6);
		if (enable == this.enable)
			return;

		/* update the stream before changing the tune */
		// stream_update(tms->channel,0);
		// System.out.println(("%s enable voices", tms->subtype));
		for (i = 0; i < 6; i++) {
			if ((enable & (1 << i)) != 0) {
				bits += 2; /* each voice has two instances */
				if (VERBOSE) {
					switch (i) {
					case 0:
						System.out.println((" 16'"));
						break;
					case 1:
						System.out.println((" 8'"));
						break;
					case 2:
						System.out.println((" 5 1/3'"));
						break;
					case 3:
						System.out.println((" 4'"));
						break;
					case 4:
						System.out.println((" 2 2/3'"));
						break;
					case 5:
						System.out.println((" 2'"));
						break;
					}
				}
			}
		}
		/* set the enable mask and number of active voices */
		this.enable = enable;
		voices = bits;
		// System.out.println(("%s\n", bits ? "" : " none"));
	}

	synchronized void writeState(java.io.DataOutput output) throws java.io.IOException {
		output.writeBoolean(subtype != null);
		if (subtype != null) {
			output.writeUTF(subtype);
		}
		output.writeInt(channel);
		output.writeInt(samplerate);
		output.writeInt(basefreq);
		output.writeInt(octave);
		output.writeInt(speed);
		output.writeInt(tune_counter);
		output.writeInt(note_counter);
		output.writeInt(voices);
		output.writeInt(shift);
		writeIntArray(output, vol);
		writeIntArray(output, vol_counter);
		writeIntArray(output, decay);
		writeIntArray(output, counter);
		writeIntArray(output, frequency);
		output.writeInt(this.output);
		output.writeInt(enable);
		output.writeInt(tune_num);
		output.writeInt(tune_ofs);
		output.writeInt(tune_max);
		output.writeInt(resampleOutputRate);
		output.writeBoolean(resampler != null);
		if (resampler != null) {
			resampler.writeState(output);
		}
	}

	synchronized void readState(java.io.DataInput input) throws java.io.IOException {
		subtype = input.readBoolean() ? input.readUTF() : null;
		channel = input.readInt();
		samplerate = input.readInt();
		basefreq = input.readInt();
		octave = input.readInt();
		speed = input.readInt();
		tune_counter = input.readInt();
		note_counter = input.readInt();
		voices = input.readInt();
		shift = input.readInt();
		readIntArray(input, vol);
		readIntArray(input, vol_counter);
		readIntArray(input, decay);
		readIntArray(input, counter);
		readIntArray(input, frequency);
		output = input.readInt();
		enable = input.readInt();
		tune_num = input.readInt();
		tune_ofs = input.readInt();
		tune_max = input.readInt();
		resampleOutputRate = input.readInt();
		boolean hasResampler = input.readBoolean();
		if (hasResampler) {
			if (samplerate <= 0 || resampleOutputRate <= 0) {
				throw new java.io.IOException("invalid TMS resampler rates");
			}
			resampler = new MameLofiResampler(samplerate, resampleOutputRate);
			resampler.readState(input);
		} else {
			resampler = null;
		}
		if (tune_num < 0 || tune_num >= tunes.length || tune_ofs < 0 || tune_max < 0) {
			throw new java.io.IOException("invalid TMS tune state");
		}
	}

	private static void writeIntArray(java.io.DataOutput output, int[] values)
			throws java.io.IOException {
		output.writeInt(values.length);
		for (int value : values) {
			output.writeInt(value);
		}
	}

	private static void readIntArray(java.io.DataInput input, int[] destination)
			throws java.io.IOException {
		int length = input.readInt();
		if (length != destination.length) {
			throw new java.io.IOException(
					"TMS array length mismatch: expected " + destination.length
							+ ", got " + length);
		}
		for (int i = 0; i < destination.length; i++) {
			destination[i] = input.readInt();
		}
	}

	public TMS36XX() {
		this.samplerate = basefreq * 64;
		int initialEnable = 0;
		for (int j = 0; j < 6; j++) {
			if (decay[j] > 0)
				initialEnable |= 0x41 << j;
		}
		tms3617_enable(initialEnable);
	}
}
