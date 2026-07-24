/* ***************************************************************************
 *
 * Phoenix sound hardware simulation - still very ALPHA!
 *
 * If you find errors or have suggestions, please mail me.
 * Juergen Buchmueller <pullmoll@t-online.de>
 *
 ****************************************************************************/
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class Sound {
	public final int VMIN = 0;
	public final int VMAX = 32767;
	private final double C18a = 0.01e-6;
	private final double C20 = 1.0e-6;
	private final double C22 = 100.0e-6;
	private final double C24 = 6.8e-6;
	private final double C25 = 6.8e-6;
	private final double C7 = 6.8e-6;
	private final int R22 = 470;
	private final int R23 = 100000;
	private final int R24 = 33000;
	private final int R40 = 47000;
	private final int R41 = 100000;
	private final int R43 = 510000;
	private final int R44 = 510000;
	private final int R45 = 5100;
	private final int R46 = 5100;
	private final int R49 = 1000;
	private final int R50 = 1000;
	private final int R51 = 330;
	private final int R52 = 20000;
	private final int R53 = 330;
	private final int R54 = 47000;

	private volatile int sound_latch_a;
	private volatile int sound_latch_b;
	private int renderLatchA;
	private int renderLatchB;

	private int[] poly18;

	private double effect2C22Voltage;
	private Astable555 effect2Node33 = new Astable555(5.0, 4.0);
	private Astable555 effect2Node34 = new Astable555(5.0, 4.0);
	private Astable555 effect2Node39 = new Astable555(5.0, 3.8);
	private Astable555 effect1Node21 = new Astable555(5.0, 3.8);

	private int effect2NoteCount1;
	private int effect2NoteCount2;

	private RcDisc4Type1 effect1Node20 = new RcDisc4Type1(R22, R23, R24, C7, 12.0);

	private int effect1NoteCount1;
	private int effect1NoteCount2;

	private int c24Counter;
	private int c24Level;

	private int c25Counter;
	private int c25Level;

	private int nCounter;
	private int nPolyoffs;
	private int nPolybit;
	private int nLowpass_counter;
	private int nLowpass_polybit;

	private int sampleRate = 48000;
	private int discreteSampleRate = 120000;
	private static final int FRAMES_PER_SECOND = 60;
	private static final int MAX_FRAME_SAMPLES = 1024;
	private static final double MAME_DISCRETE_OUTPUT_GAIN = 40000.0;
	private static final double MAME_STREAM_FULL_SCALE = 32768.0;
	private static final double MAME_TTL_LOGIC_1 = 3.4;
	private static final double MAME_DISCRETE_ROUTE = 0.6;
	private static final double MAME_CUSTOM_ROUTE = 0.4;
	private static final double MAME_TMS_ROUTE = 0.5;
	private byte[] playbackBuffer;
	private int frameSampleRemainder;
	private final List<SoundEvent> frameEvents = new ArrayList<SoundEvent>();
	private double[] mixerInputCaps = new double[4];
	private double mixerAmpCap;
	private double effect1FilterState;
	private final MameLofiResampler discreteResampler =
			new MameLofiResampler(discreteSampleRate, sampleRate);
	private int discreteSourceLatchA;
	private int discreteSourceLatchB;
	private final MameLofiResampler.Source discreteSource = this::renderDiscreteSourceSample;

	private final PcmSink pcmSink;
	private boolean stopped;

	private TMS36XX music;

	public Sound() {
		this(PcmSink.discarding());
	}

	public Sound(PcmSink pcmSink) {
		if (pcmSink == null) {
			throw new NullPointerException("pcmSink");
		}
		this.pcmSink = pcmSink;
		int shiftreg = 0;
		poly18 = new int[1 << (18 - 5)];

		for (int i = 0; i < (1 << (18 - 5)); i++) {
			int bits = 0;
			for (int j = 0; j < 32; j++) {
				bits = (bits >>> 1) | (shiftreg << 31);
				if (((shiftreg >> 16) & 1) == ((shiftreg >> 17) & 1))
					shiftreg = (shiftreg << 1) | 1;
				else
					shiftreg <<= 1;
			}
			poly18[i] = bits;
		}

		this.playbackBuffer = new byte[MAX_FRAME_SAMPLES * 2];
		music = new TMS36XX();
		resetDiscreteNodes();

	}

	private void resetDiscreteNodes() {
		// MAME's 555 reset initializes the state and performs one discrete-rate step.
		effect2Node33.stepEnergy(R40, R41, effect2Capacitance(0), -1.0, discreteSampleRate);
		effect2Node34.stepEnergy(R43, R44, C20, -1.0, discreteSampleRate);
	}

	private double effect2Capacitance(int frequencySelect) {
		switch (frequencySelect) {
			case 1:
				return C18a + 0.47e-6;
			case 2:
				return C18a + 1.0e-6;
			case 3:
				return C18a + 0.47e-6 + 1.0e-6;
			default:
				return C18a;
		}
	}

	private double effect2C22TargetVoltage(double node33, double node34) {
		return effect2MixerNodes(node33, node34).node36;
	}

	private Effect2MixerNodes effect2MixerNodes(double node33, double node34) {
		double node35 = resistorMixer(
				new double[] { node33, node34, 5.0 },
				new double[] { 10000.0, 5100.0 + 5100.0, 5000.0 },
				10000.0);
		double node36 = resistorMixer(
				new double[] { node34, node35 },
				new double[] { 5100.0, 5100.0 },
				0.0);
		return new Effect2MixerNodes(node35, node36);
	}

	private double effect2ControlVoltage(double node33, double c22Voltage) {
		return resistorMixer(
				new double[] { node33, c22Voltage, 5.0 },
				new double[] { 10000.0, 5100.0, 5000.0 },
				10000.0);
	}

	private double effect2ChargeResistance() {
		double internal = 1.0 / (1.0 / 10000.0 + 1.0 / 5000.0 + 1.0 / 10000.0);
		return 1.0 / (1.0 / 5100.0 + 1.0 / (5100.0 + internal));
	}

	private double effect2C22Exponent(int rate) {
		return 1.0 - Math.exp(-1.0 / (rate * effect2ChargeResistance() * C22));
	}

	private double resistorMixer(double[] values, double[] resistors, double feedback) {
		double current = 0.0;
		double conductance = feedback != 0.0 ? 1.0 / feedback : 0.0;
		for (int i = 0; i < values.length; i++) {
			current += values[i] / resistors[i];
			conductance += 1.0 / resistors[i];
		}
		return current / conductance;
	}

	private double parallel(double r1, double r2) {
		return 1.0 / (1.0 / r1 + 1.0 / r2);
	}

	private double effect1Filter(double input, int latchB) {
		double resistance = parallel(10000.0, 100000.0);
		double capacitor = 0.047e-6;
		double exponent = 1.0 - Math.exp(-1.0 / (discreteSampleRate * resistance * capacitor));
		effect1FilterState += (input - effect1FilterState) * exponent;
		return SoundControlMapping.effect1Filter(latchB) ? effect1FilterState : input;
	}

	private double noteEnergy(int data, double clockInput, boolean effect2) {
		int count1 = effect2 ? effect2NoteCount1 : effect1NoteCount1;
		int count2 = effect2 ? effect2NoteCount2 : effect1NoteCount2;
		int lastCount2 = count2;
		int increments = (int) clockInput;
		double xTime = clockInput - increments;

		if (data != 0x0f) {
			for (int i = 0; i < increments; i++) {
				count1++;
				if (count1 > 0x0f) {
					count1 = data;
					count2++;
					if (count2 > 1) {
						count2 = 0;
					}
				}
			}
		}

		double output = count2;
		if (count2 != lastCount2) {
			if (xTime == 0.0) {
				xTime = 1.0;
			}
			output = lastCount2;
			if (count2 > lastCount2) {
				output += (count2 - lastCount2) * xTime;
			} else {
				output -= (lastCount2 - count2) * xTime;
			}
		}

		if (effect2) {
			effect2NoteCount1 = count1;
			effect2NoteCount2 = count2;
		} else {
			effect1NoteCount1 = count1;
			effect1NoteCount2 = count2;
		}
		return output;
	}

	public final int update_c24(int samplerate, int latchA) {
		if (SoundControlMapping.noiseC24Discharge(latchA)) {
			if (c24Level > VMIN) {
				c24Counter -= (int) ((c24Level - VMIN) / (R52 * C24));
				if (c24Counter <= 0) {
					int n = -c24Counter / samplerate + 1;
					c24Counter += n * samplerate;
					if ((c24Level -= n) < VMIN)
						c24Level = VMIN;
				}
			}
		} else {
			if (c24Level < VMAX) {
				c24Counter -= (int) ((VMAX - c24Level) / ((R51 + R49) * C24));
				if (c24Counter <= 0) {
					int n = -c24Counter / samplerate + 1;
					c24Counter += n * samplerate;
					if ((c24Level += n) > VMAX)
						c24Level = VMAX;
				}
			}
		}
		return VMAX - c24Level;
	}

	public final int update_c25(int samplerate, int latchA) {
		if (SoundControlMapping.noiseC25Charge(latchA)) {
			if (c25Level < VMAX) {
				c25Counter -= (int) ((VMAX - c25Level) / ((R50 + R53) * C25));
				if (c25Counter <= 0) {
					int n = -c25Counter / samplerate + 1;
					c25Counter += n * samplerate;
					if ((c25Level += n) > VMAX)
						c25Level = VMAX;
				}
			}
		} else {
			if (c25Level > VMIN) {
				c25Counter -= (int) ((c25Level - VMIN) / (R54 * C25));
				if (c25Counter <= 0) {
					int n = -c25Counter / samplerate + 1;
					c25Counter += n * samplerate;
					if ((c25Level -= n) < VMIN)
						c25Level = VMIN;
				}
			}
		}
		return c25Level;
	}

	public final int noise(int samplerate, int latchA) {
		int vc24 = update_c24(samplerate, latchA);
		int vc25 = update_c25(samplerate, latchA);
		int sum = 0, level, frequency;

		if (vc24 < vc25)
			level = vc24 + (vc25 - vc24) / 2;
		else
			level = vc25 + (vc24 - vc25) / 2;

		frequency = 588 + 6325 * level / 32768;

		nCounter -= frequency;
		if (nCounter <= 0) {
			int n = (-nCounter / samplerate) + 1;
			nCounter += n * samplerate;
			nPolyoffs = (nPolyoffs + n) & 0x3ffff;
			nPolybit = (poly18[nPolyoffs >> 5] >> (nPolyoffs & 31)) & 1;
		}
		if (nPolybit == 0)
			sum += vc24;

		nLowpass_counter -= 400;
		if (nLowpass_counter <= 0) {
			nLowpass_counter += samplerate;
			nLowpass_polybit = nPolybit;
		}
		if (nLowpass_polybit == 0)
			sum += vc25;

		return sum;
	}

	public void process(byte[] target, int length) {
		int bufferIndex = 0;
		int eventIndex = 0;
		for (int sampleIndex = 0; sampleIndex < length; sampleIndex++) {
			while (eventIndex < frameEvents.size() && frameEvents.get(eventIndex).sampleIndex <= sampleIndex) {
				applyEvent(frameEvents.get(eventIndex));
				eventIndex++;
			}
			int latchA = renderLatchA & 0xff;
			int latchB = renderLatchB & 0xff;
			discreteSourceLatchA = latchA;
			discreteSourceLatchB = latchB;
			double discrete = discreteResampler.nextSample(discreteSource);
			double customNoise = (noise(sampleRate, latchA) / 2.0) / MAME_STREAM_FULL_SCALE;
			double tms = music.nextSample(sampleRate);
			double mixed = discrete * MAME_DISCRETE_ROUTE + customNoise * MAME_CUSTOM_ROUTE + tms * MAME_TMS_ROUTE;
			int signedSample = clampPcm16((int) Math.round(mixed * MAME_STREAM_FULL_SCALE));
			target[bufferIndex++] = (byte) (signedSample & 0xff);
			target[bufferIndex++] = (byte) ((signedSample >> 8) & 0xff);
		}
		while (eventIndex < frameEvents.size()) {
			applyEvent(frameEvents.get(eventIndex));
			eventIndex++;
		}
	}

	private double renderDiscreteSourceSample() {
		return stepDiscreteNodes(discreteSourceLatchA, discreteSourceLatchB).node90;
	}

	public synchronized void endFrame() {
		if (stopped) {
			return;
		}
		int samples = renderFrame(playbackBuffer);
		pcmSink.write(playbackBuffer, 0, samples * 2);
	}

	synchronized byte[] renderFrameForTest() {
		int samples = renderFrame(playbackBuffer);
		return Arrays.copyOf(playbackBuffer, samples * 2);
	}

	private int renderFrame(byte[] target) {
		frameSampleRemainder += sampleRate;
		int samples = frameSampleRemainder / FRAMES_PER_SECOND;
		frameSampleRemainder -= samples * FRAMES_PER_SECOND;
		if (samples > MAX_FRAME_SAMPLES) {
			samples = MAX_FRAME_SAMPLES;
		}
		process(target, samples);
		frameEvents.clear();
		return samples;
	}

	private void applyEvent(SoundEvent event) {
		if (event.control == 'A') {
			renderLatchA = event.value;
		} else {
			renderLatchB = event.value;
			updateMusic(event.value);
		}
	}

	private double mixDiscreteSources(double effect1, double effect2) {
		double[] inputs = {
				effect1,
				effect2,
				0.0,
				0.0
		};
		double[] resistors = { 57000.0, 30000.0, 20000.0, 20000.0 };
		double[] capacitors = { 10.0e-6, 10.0e-6, 0.1e-6, 10.0e-6 };
		double feedback = 10000.0;
		double totalConductance = 1.0 / feedback;
		double current = 0.0;

		for (int i = 0; i < inputs.length; i++) {
			double filtered = highPassMixerInput(i, inputs[i], resistors[i], feedback, capacitors[i]);
			current += filtered / resistors[i];
			totalConductance += 1.0 / resistors[i];
		}

		double mixedVoltage = current / totalConductance;
		double output = highPassMixerOutput(mixedVoltage);
		return output * MAME_DISCRETE_OUTPUT_GAIN / MAME_STREAM_FULL_SCALE;
	}

	SoundNodes stepDiscreteNodes(int latchA, int latchB) {
		double effect2Node30 = effect2Capacitance(SoundControlMapping.effect2Frequency(latchA));
		double effect2Node31 = (SoundControlMapping.effect2Frequency(latchA) & 0x02) != 0 ? 1.0 : 0.0;
		double effect2Node32 = effect2Node31 != 0.0 ? MAME_TTL_LOGIC_1 / 2.0 : MAME_TTL_LOGIC_1;
		double effect2Node33 = this.effect2Node33.stepEnergy(R40, R41, effect2Node30, -1.0, discreteSampleRate);
		double effect2Node34 = this.effect2Node34.stepEnergy(R43, R44, C20, -1.0, discreteSampleRate);
		Effect2MixerNodes effect2MixerNodes = effect2MixerNodes(effect2Node33, effect2Node34);
		double effect2Node35 = effect2MixerNodes.node35;
		double effect2Node36 = effect2MixerNodes.node36;
		effect2C22Voltage += (effect2Node36 - effect2C22Voltage) * effect2C22Exponent(discreteSampleRate);
		double effect2Node37 = effect2C22Voltage;
		double effect2Node38 = effect2ControlVoltage(effect2Node33, effect2Node37);
		double effect2Node39 = this.effect2Node39.stepCountF(20000.0, 20000.0, 0.001e-6,
				effect2Node38, discreteSampleRate);
		double effect2Node40 = noteEnergy(SoundControlMapping.effect2Data(latchA), effect2Node39, true);
		double effect2Sound = effect2Node40 * effect2Node32;

		double effect1Node20 = this.effect1Node20.step(SoundControlMapping.effect1Frequency(latchB), discreteSampleRate);
		double effect1Node21 = this.effect1Node21.stepCountF(47000.0, 47000.0, 0.001e-6,
				effect1Node20, discreteSampleRate);
		double effect1Node22 = noteEnergy(SoundControlMapping.effect1Data(latchB), effect1Node21, false);
		double effect1Node23 = SoundControlMapping.effect1Filter(latchB)
				? MAME_TTL_LOGIC_1 * 100000.0 / 110000.0 : MAME_TTL_LOGIC_1;
		double effect1Node24 = effect1Node22 * effect1Node23;
		double effect1Node25 = effect1Filter(effect1Node24, latchB);
		double effect1Sound = SoundControlMapping.effect1Filter(latchB) ? effect1Node25 : effect1Node24;
		double node90 = mixDiscreteSources(effect1Sound, effect2Sound);

		return new SoundNodes(
				effect1Node20, effect1Node21, effect1Node22, effect1Node23, effect1Node24, effect1Node25,
				effect1Sound, effect2Node30, effect2Node31, effect2Node32, effect2Node33, effect2Node34,
				effect2Node35, effect2Node36,
				effect2Node37, effect2Node38, effect2Node39, effect2Node40, effect2Sound,
				node90);
	}

	private double highPassMixerInput(int index, double input, double resistor, double feedback, double capacitor) {
		double rcResistance = parallel(resistor, feedback);
		double exponent = 1.0 - Math.exp(-1.0 / (discreteSampleRate * rcResistance * capacitor));
		mixerInputCaps[index] += (input - mixerInputCaps[index]) * exponent;
		return input - mixerInputCaps[index];
	}

	private double highPassMixerOutput(double input) {
		double exponent = 1.0 - Math.exp(-1.0 / (discreteSampleRate * 100000.0 * 10.0e-6));
		mixerAmpCap += (input - mixerAmpCap) * exponent;
		return input - mixerAmpCap;
	}

	private int clampPcm16(int sample) {
		if (sample < -32768) {
			return -32768;
		}
		if (sample > 32767) {
			return 32767;
		}
		return sample;
	}

	private static final class RcDisc4Type1 {
		private final double[] target = new double[2];
		private final double[] rc = new double[2];
		private final double maxOutput;
		private double capVoltage;

		RcDisc4Type1(double r1, double r2, double r3, double c, double supplyVoltage) {
			double diodeSupply = supplyVoltage - 0.5;

			double inputHighR = parallelStatic(r1, r3);
			double inputHighCurrent = diodeSupply / (r2 + inputHighR);
			target[1] = inputHighCurrent * inputHighR + 0.5;
			rc[1] = parallelStatic(r2, inputHighR) * c;

			double inputLowCurrent = diodeSupply / (r2 + r3);
			target[0] = inputLowCurrent * r3 + 0.5;
			rc[0] = parallelStatic(r2, r3) * c;

			maxOutput = supplyVoltage - 1.5;
		}

		double step(boolean input, int sampleRate) {
			int index = input ? 1 : 0;
			double exponent = 1.0 - Math.exp(-1.0 / (sampleRate * rc[index]));
			capVoltage += (target[index] - capVoltage) * exponent;
			if (capVoltage < 0.0) {
				return 0.0;
			}
			if (capVoltage > maxOutput) {
				return maxOutput;
			}
			return capVoltage;
		}

		private static double parallelStatic(double r1, double r2) {
			return 1.0 / (1.0 / r1 + 1.0 / r2);
		}
	}

	private static final class Astable555 {
		private final double vPos;
		private final double vOutHigh;
		private boolean flipFlop = true;
		private double capVoltage;
		private double lastOutput;

		Astable555(double vPos, double vOutHigh) {
			this.vPos = vPos;
			this.vOutHigh = vOutHigh;
		}

		double stepCountF(double r1, double r2, double c, double controlVoltage, int sampleRate) {
			return step(r1, r2, c, controlVoltage, sampleRate, true);
		}

		double stepEnergy(double r1, double r2, double c, double controlVoltage, int sampleRate) {
			return step(r1, r2, c, controlVoltage, sampleRate, false);
		}

		private double step(double r1, double r2, double c, double controlVoltage, int sampleRate, boolean countFOutput) {
			boolean useControlVoltage = controlVoltage >= 0.0;
			double threshold = useControlVoltage ? controlVoltage : vPos * 2.0 / 3.0;
			if (threshold < 0.25) {
				return lastOutput;
			}
			double trigger = threshold / 2.0;
			double chargeVoltage = vPos;
			double dt = 1.0 / sampleRate;
			double xTime = 0.0;
			int countF = 0;
			int countR = 0;

			if (useControlVoltage) {
				if (capVoltage >= threshold) {
					flipFlop = false;
					countF++;
				} else if (capVoltage <= trigger) {
					flipFlop = true;
					countR++;
				}
			}

			while (dt > 0.0) {
				if (c == 0.0) {
					flipFlop = true;
					capVoltage = chargeVoltage;
					break;
				}

				if (flipFlop) {
					if (r1 == 0.0) {
						capVoltage -= capVoltage * rcExponent(10000000.0 * c, dt);
						break;
					}
					double rc = (r1 + r2) * c;
					double next = capVoltage + (chargeVoltage - capVoltage) * rcExponent(rc, dt);
					if (next >= threshold) {
						double overshootRatio = (next - threshold) / (chargeVoltage - capVoltage);
						dt = rc * Math.log(1.0 / (1.0 - overshootRatio));
						xTime = dt;
						capVoltage = threshold;
						flipFlop = false;
						countF++;
					} else {
						capVoltage = next;
						dt = 0.0;
					}
				} else {
					if (r2 == 0.0) {
						capVoltage = trigger;
					} else {
						double rc = r2 * c;
						double next = capVoltage - capVoltage * rcExponent(rc, dt);
						if (next <= trigger) {
							if (next < trigger && capVoltage > 0.0) {
								double overshootRatio = (trigger - next) / capVoltage;
								dt = rc * Math.log(1.0 / (1.0 - overshootRatio));
							}
							xTime = dt;
							capVoltage = trigger;
							flipFlop = true;
							countR++;
						} else {
							capVoltage = next;
							dt = 0.0;
						}
					}
				}
			}

			double xRatio = xTime * sampleRate;
			double output;
			if (countFOutput) {
				output = countF != 0 ? countF + xRatio : 0.0;
			} else {
				if (xRatio == 0.0) {
					xRatio = 1.0;
				}
				output = vOutHigh * (flipFlop ? xRatio : (1.0 - xRatio));
			}
			lastOutput = output;
			return output;
		}

		private double rcExponent(double rc, double dt) {
			if (rc <= 0.0) {
				return 1.0;
			}
			return 1.0 - Math.exp(-dt / rc);
		}
	}

	private static final class Effect2MixerNodes {
		final double node35;
		final double node36;

		Effect2MixerNodes(double node35, double node36) {
			this.node35 = node35;
			this.node36 = node36;
		}
	}

	public synchronized void updateControlA(byte data, int cycleInFrame, int cyclesPerFrame) {
		int latch = data & 0xff;
		if (latch == sound_latch_a)
			return;

		sound_latch_a = latch;
		queueEvent('A', latch, cycleInFrame, cyclesPerFrame);
	}

	public synchronized void updateControlB(byte data, int cycleInFrame, int cyclesPerFrame) {
		int latch = data & 0xff;
		if (latch == sound_latch_b)
			return;

		sound_latch_b = latch;
		queueEvent('B', latch, cycleInFrame, cyclesPerFrame);
	}

	private void queueEvent(char control, int value, int cycleInFrame, int cyclesPerFrame) {
		int sampleIndex = 0;
		int nominalFrameSamples = (sampleRate + FRAMES_PER_SECOND - 1) / FRAMES_PER_SECOND;
		if (cyclesPerFrame > 0) {
			sampleIndex = (int) ((long) cycleInFrame * nominalFrameSamples / cyclesPerFrame);
		}
		if (sampleIndex < 0) {
			sampleIndex = 0;
		}
		if (sampleIndex >= nominalFrameSamples) {
			sampleIndex = nominalFrameSamples - 1;
		}
		SoundEvent event = new SoundEvent(sampleIndex, control, value);
		int insertAt = frameEvents.size();
		while (insertAt > 0 && frameEvents.get(insertAt - 1).sampleIndex > sampleIndex) {
			insertAt--;
		}
		frameEvents.add(insertAt, event);
	}

	/** Changes the tune that the MM6221AA is playing */
	public void updateMusic(int data) {
		if (music != null)
			music.mm6221aa_tune_w(SoundControlMapping.mm6221aaTune(data));
	}

	synchronized void writeState(java.io.DataOutput output) throws java.io.IOException {
		output.writeInt(sampleRate);
		output.writeInt(discreteSampleRate);
		output.writeInt(sound_latch_a);
		output.writeInt(sound_latch_b);
		output.writeInt(renderLatchA);
		output.writeInt(renderLatchB);
		output.writeDouble(effect2C22Voltage);
		writeAstableState(output, effect2Node33);
		writeAstableState(output, effect2Node34);
		writeAstableState(output, effect2Node39);
		writeAstableState(output, effect1Node21);
		output.writeDouble(effect1Node20.capVoltage);
		output.writeInt(effect2NoteCount1);
		output.writeInt(effect2NoteCount2);
		output.writeInt(effect1NoteCount1);
		output.writeInt(effect1NoteCount2);
		output.writeInt(c24Counter);
		output.writeInt(c24Level);
		output.writeInt(c25Counter);
		output.writeInt(c25Level);
		output.writeInt(nCounter);
		output.writeInt(nPolyoffs);
		output.writeInt(nPolybit);
		output.writeInt(nLowpass_counter);
		output.writeInt(nLowpass_polybit);
		output.writeInt(frameSampleRemainder);
		output.writeInt(frameEvents.size());
		for (SoundEvent event : frameEvents) {
			output.writeInt(event.sampleIndex);
			output.writeChar(event.control);
			output.writeInt(event.value);
		}
		output.writeInt(mixerInputCaps.length);
		for (double value : mixerInputCaps) {
			output.writeDouble(value);
		}
		output.writeDouble(mixerAmpCap);
		output.writeDouble(effect1FilterState);
		discreteResampler.writeState(output);
		output.writeInt(discreteSourceLatchA);
		output.writeInt(discreteSourceLatchB);
		music.writeState(output);
	}

	synchronized void readState(java.io.DataInput input) throws java.io.IOException {
		int savedSampleRate = input.readInt();
		int savedDiscreteSampleRate = input.readInt();
		if (savedSampleRate != sampleRate || savedDiscreteSampleRate != discreteSampleRate) {
			throw new java.io.IOException("sound sample-rate mismatch");
		}
		sound_latch_a = input.readInt();
		sound_latch_b = input.readInt();
		renderLatchA = input.readInt();
		renderLatchB = input.readInt();
		effect2C22Voltage = input.readDouble();
		readAstableState(input, effect2Node33);
		readAstableState(input, effect2Node34);
		readAstableState(input, effect2Node39);
		readAstableState(input, effect1Node21);
		effect1Node20.capVoltage = input.readDouble();
		effect2NoteCount1 = input.readInt();
		effect2NoteCount2 = input.readInt();
		effect1NoteCount1 = input.readInt();
		effect1NoteCount2 = input.readInt();
		c24Counter = input.readInt();
		c24Level = input.readInt();
		c25Counter = input.readInt();
		c25Level = input.readInt();
		nCounter = input.readInt();
		nPolyoffs = input.readInt();
		nPolybit = input.readInt();
		nLowpass_counter = input.readInt();
		nLowpass_polybit = input.readInt();
		frameSampleRemainder = input.readInt();
		int eventCount = input.readInt();
		if (eventCount < 0 || eventCount > 4096) {
			throw new java.io.IOException("invalid pending sound-event count");
		}
		frameEvents.clear();
		for (int i = 0; i < eventCount; i++) {
			int sampleIndex = input.readInt();
			char control = input.readChar();
			int value = input.readInt();
			if (sampleIndex < 0 || sampleIndex >= MAX_FRAME_SAMPLES
					|| (control != 'A' && control != 'B')) {
				throw new java.io.IOException("invalid pending sound event");
			}
			frameEvents.add(new SoundEvent(sampleIndex, control, value));
		}
		int mixerCapCount = input.readInt();
		if (mixerCapCount != mixerInputCaps.length) {
			throw new java.io.IOException("sound mixer-state length mismatch");
		}
		for (int i = 0; i < mixerInputCaps.length; i++) {
			mixerInputCaps[i] = input.readDouble();
		}
		mixerAmpCap = input.readDouble();
		effect1FilterState = input.readDouble();
		discreteResampler.readState(input);
		discreteSourceLatchA = input.readInt();
		discreteSourceLatchB = input.readInt();
		music.readState(input);
	}

	private static void writeAstableState(java.io.DataOutput output, Astable555 node)
			throws java.io.IOException {
		output.writeBoolean(node.flipFlop);
		output.writeDouble(node.capVoltage);
		output.writeDouble(node.lastOutput);
	}

	private static void readAstableState(java.io.DataInput input, Astable555 node)
			throws java.io.IOException {
		node.flipFlop = input.readBoolean();
		node.capVoltage = input.readDouble();
		node.lastOutput = input.readDouble();
	}

	public synchronized void stop() {
		if (!stopped) {
			stopped = true;
			pcmSink.close();
		}
	}

	private static final class SoundEvent {
		final int sampleIndex;
		final char control;
		final int value;

		SoundEvent(int sampleIndex, char control, int value) {
			this.sampleIndex = sampleIndex;
			this.control = control;
			this.value = value;
		}
	}

	static final class SoundNodes {
		final double node20;
		final double node21;
		final double node22;
		final double node23;
		final double node24;
		final double node25;
		final double effect1Sound;
		final double node30;
		final double node31;
		final double node32;
		final double node33;
		final double node34;
		final double node35;
		final double node36;
		final double node37;
		final double node38;
		final double node39;
		final double node40;
		final double effect2Sound;
		final double node90;

		SoundNodes(double node20, double node21, double node22, double node23, double node24,
				double node25, double effect1Sound, double node30, double node31, double node32,
				double node33, double node34, double node35, double node36,
				double node37, double node38, double node39, double node40, double effect2Sound,
				double node90) {
			this.node20 = node20;
			this.node21 = node21;
			this.node22 = node22;
			this.node23 = node23;
			this.node24 = node24;
			this.node25 = node25;
			this.effect1Sound = effect1Sound;
			this.node30 = node30;
			this.node31 = node31;
			this.node32 = node32;
			this.node33 = node33;
			this.node34 = node34;
			this.node35 = node35;
			this.node36 = node36;
			this.node37 = node37;
			this.node38 = node38;
			this.node39 = node39;
			this.node40 = node40;
			this.effect2Sound = effect2Sound;
			this.node90 = node90;
		}
	}

}
