local trace_path = os.getenv("PHOENIX_SOUND_TRACE")
if not trace_path or trace_path == "" then
	error("PHOENIX_SOUND_TRACE must name the output CSV")
end
local raw_dir = os.getenv("PHOENIX_SOUND_RAW_DIR")
local fixture_enabled = os.getenv("PHOENIX_SOUND_FIXTURE") == "1"

local machine = manager.machine
local program = machine.devices[":maincpu"].spaces["program"]
local state = {
	taps = {},
	events = {},
	raw = {}
}
_G.phoenix_sound_trace_state = state

local function record(control, data)
	state.events[#state.events + 1] = string.format("%.12f,%s,0x%02x\n",
		machine.time:as_double(), control, data & 0xff)
end

local function fixture_value(control, data)
	if not fixture_enabled then
		return data & 0xff
	end
	local time = machine.time:as_double()
	if time < 0.5 then
		return control == "A" and 0x0f or 0x0f
	elseif time < 2.5 then
		return control == "A" and 0x28 or 0x0f
	elseif time < 4.5 then
		return control == "A" and 0x0f or 0x18
	elseif time < 6.5 then
		return control == "A" and 0x0f or 0x38
	elseif time < 8.5 then
		return control == "A" and 0xcf or 0x0f
	elseif time < 14.5 then
		return control == "A" and 0x0f or 0x8f
	elseif time < 20.5 then
		return control == "A" and 0x0f or 0xcf
	else
		return 0x0f
	end
end

state.taps.control_a = program:install_write_tap(
	0x6000, 0x63ff, "phoenix_sound_control_a",
	function(offset, data, mask)
		local value = fixture_value("A", data)
		record("A", value)
		return value
	end)

state.taps.control_b = program:install_write_tap(
	0x6800, 0x6bff, "phoenix_sound_control_b",
	function(offset, data, mask)
		local value = fixture_value("B", data)
		record("B", value)
		return value
	end)

if raw_dir and raw_dir ~= "" then
	local sources = {
		[":discrete"] = { file = "discrete.f32", rate = 120000 },
		[":cust"] = { file = "custom.f32", rate = 48000 },
		[":tms"] = { file = "tms.f32", rate = 372 * 64 }
	}
	for tag, source in pairs(sources) do
		source.handle = assert(io.open(raw_dir .. "/" .. source.file, "wb"))
		source.samples = 0
		state.raw[tag] = source
		manager.machine.sounds[tag].hook = true
	end

	emu.register_sound_update(function(samples)
		for tag, channels in pairs(samples) do
			local source = state.raw[tag]
			if source then
				local channel = channels[1]
				local packed = {}
				for i = 1, #channel do
					packed[i] = string.pack("<f", channel[i])
				end
				source.handle:write(table.concat(packed))
				source.samples = source.samples + #channel
			end
		end
	end)
end

state.stop_notifier = emu.add_machine_stop_notifier(function()
	local trace = assert(io.open(trace_path, "w"))
	trace:write("time_seconds,control,value\n")
	trace:write(table.concat(state.events))
	trace:close()
	if next(state.raw) then
		local manifest = assert(io.open(raw_dir .. "/manifest.csv", "w"))
		manifest:write("tag,file,sample_rate,samples\n")
		for tag, source in pairs(state.raw) do
			source.handle:close()
			manifest:write(string.format("%s,%s,%d,%d\n",
				tag, source.file, source.rate, source.samples))
		end
		manifest:close()
	end
	state.taps = {}
end)
