import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;

public class SoundMameTraceabilityTest {
	private static final Mapping[] SOUND_MAPPINGS = {
			new Mapping("PHOENIX_EFFECT_2_DATA", "SoundControlMapping.effect2Data"),
			new Mapping("PHOENIX_EFFECT_2_FREQ", "SoundControlMapping.effect2Frequency"),
			new Mapping("PHOENIX_EFFECT_1_DATA", "SoundControlMapping.effect1Data"),
			new Mapping("PHOENIX_EFFECT_1_FREQ", "SoundControlMapping.effect1Frequency"),
			new Mapping("PHOENIX_EFFECT_1_FILT", "SoundControlMapping.effect1Filter"),
			new Mapping("NODE_20 RCDISC4", "effect1Node20"),
			new Mapping("NODE_21 555 astable CV", "effect1Node21"),
			new Mapping("NODE_22 DISCRETE_NOTE", "noteEnergy"),
			new Mapping("DEFAULT_TTL_V_LOGIC_1", "MAME_TTL_LOGIC_1"),
			new Mapping("NODE_25 RCFILTER", "effect1Node25"),
			new Mapping("NODE_30 capacitance selector", "effect2Capacitance"),
			new Mapping("NODE_31 high frequency bit", "effect2Node31"),
			new Mapping("NODE_32 effect 2 voltage level", "effect2Node32"),
			new Mapping("NODE_33 555 astable", "effect2Node33"),
			new Mapping("NODE_34 555 astable", "effect2Node34"),
			new Mapping("555 reset performs one step", "resetDiscreteNodes"),
			new Mapping("NODE_35 R42/R46 junction", "effect2Node35"),
			new Mapping("NODE_37 C22 RC filter", "effect2C22Voltage"),
			new Mapping("NODE_38 control voltage mixer", "effect2ControlVoltage"),
			new Mapping("NODE_39 555 astable CV", "effect2Node39"),
			new Mapping("NODE_40 DISCRETE_NOTE", "noteEnergy"),
			new Mapping("NODE_90 discrete mixer", "mixDiscreteSources"),
			new Mapping("custom noise stream", "noise(sampleRate, latchA) / 2.0"),
			new Mapping("MM6221AA tune select", "SoundControlMapping.mm6221aaTune")
	};

	private static final Mapping[] TMS_MAPPINGS = {
			new Mapping("TMS36XX clock 372", "basefreq = 372"),
			new Mapping("TMS36XX internal rate clock*64", "basefreq * 64"),
			new Mapping("MM6221AA tune speed 0.21", "VMAX / 0.21"),
			new Mapping("Phoenix MM6221AA decay 0.50", "VMAX / 0.50"),
			new Mapping("Phoenix MM6221AA decay 1.05", "VMAX / 1.05"),
			new Mapping("shared MAME LoFi resampler", "MameLofiResampler")
	};

	private static final Mapping[] RESAMPLER_MAPPINGS = {
			new Mapping("MAME LoFi resampler 24-bit phase", "PHASE_ONE = 0x1000000"),
			new Mapping("MAME LoFi source divide", "1 + sourceRate / targetRate"),
			new Mapping("MAME LoFi cubic interpolation", "createInterpolation")
	};

	public static void main(String[] args) throws IOException {
		String sound = Files.readString(Path.of("Sound.java"));
		String tms = Files.readString(Path.of("TMS36XX.java"));
		String resampler = Files.readString(Path.of("MameLofiResampler.java"));
		for (Mapping mapping : SOUND_MAPPINGS) {
			assertContains("Sound.java", sound, mapping);
		}
		for (Mapping mapping : TMS_MAPPINGS) {
			assertContains("TMS36XX.java", tms, mapping);
		}
		for (Mapping mapping : RESAMPLER_MAPPINGS) {
			assertContains("MameLofiResampler.java", resampler, mapping);
		}
	}

	private static void assertContains(String file, String source, Mapping mapping) {
		if (!source.contains(mapping.javaToken)) {
			throw new AssertionError(file + " no longer exposes Java mapping for "
					+ mapping.mameName + ": " + mapping.javaToken);
		}
	}

	private static final class Mapping {
		final String mameName;
		final String javaToken;

		Mapping(String mameName, String javaToken) {
			this.mameName = mameName;
			this.javaToken = javaToken;
		}
	}
}
