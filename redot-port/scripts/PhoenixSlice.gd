extends Node2D

# The image is the original 208x256 Phoenix video surface.  It is rasterised
# by the local C core from its two tile RAM planes and ROM-derived tile/palette
# data; this script intentionally contains no substitute ship or enemy art.
const WIDTH := 416
const HEIGHT := 512
const BTN_COIN := 0x01
const BTN_START_1P := 0x02
const BTN_START_2P := 0x04
const BTN_FIRE := 0x10
const BTN_RIGHT := 0x20
const BTN_LEFT := 0x40
const BTN_SHIELD := 0x80
const C2_HIRES_SHADER := preload("res://shaders/c2_hires.gdshader")

var core: PhoenixCore
var background_textures: Array[ImageTexture] = []
var foreground_textures: Array[ImageTexture] = []
var background_sprite: Sprite2D
var foreground_sprite: Sprite2D
var prompt_panel: ColorRect
var prompt_label: Label
var audio_player: AudioStreamPlayer
var audio_playback
var texture_index := 0
var frame_blend := 1.0
var demo_running := false
var credit_inserted := false
var game_running := false


func _ready() -> void:
	core = PhoenixCore.new()
	core.reset()
	create_video_layers()
	create_prompt()
	create_audio()
	update_frame()
	refresh_prompt()


func _unhandled_key_input(event: InputEvent) -> void:
	var key_event := event as InputEventKey
	if key_event == null or not key_event.pressed or key_event.echo:
		return
	if key_event.keycode == KEY_ENTER or key_event.keycode == KEY_1:
		if not demo_running:
			demo_running = true
		elif credit_inserted and not game_running:
			start_credited_game(BTN_START_1P)
	elif key_event.keycode == KEY_2 and credit_inserted and not game_running:
		start_credited_game(BTN_START_2P)
	elif key_event.keycode == KEY_C and demo_running and not game_running:
		# C is the cabinet coin switch. It adds a credit but does not silently
		# begin a game; Enter remains the original 1-player start control.
		core.step(0xff & ~BTN_COIN)
		core.step(0xff)
		credit_inserted = true
		update_frame()
	elif key_event.keycode == KEY_R:
		core.reset()
		demo_running = false
		credit_inserted = false
		game_running = false
	refresh_prompt()


func _physics_process(_delta: float) -> void:
	# The cabinet start gate must not let the original program advance unseen.
	# Its first ENTER therefore starts the authentic attract sequence at frame 0.
	if not demo_running:
		return
	var input_mask := cabinet_input()
	core.step(input_mask)
	update_frame()
	queue_audio_frame()
	frame_blend = 0.0
	refresh_prompt()


func _process(delta: float) -> void:
	# Presentation can run at the monitor refresh rate; gameplay remains 60 Hz.
	frame_blend = minf(frame_blend + delta * 60.0, 1.0)
	set_shader_blend(background_sprite, frame_blend)
	set_shader_blend(foreground_sprite, frame_blend)


func cabinet_input() -> int:
	if not game_running:
		return 0xff
	var input_mask := 0xff
	if Input.is_key_pressed(KEY_LEFT) or Input.is_key_pressed(KEY_A):
		input_mask &= ~BTN_LEFT
	if Input.is_key_pressed(KEY_RIGHT) or Input.is_key_pressed(KEY_D):
		input_mask &= ~BTN_RIGHT
	if Input.is_key_pressed(KEY_SPACE) or Input.is_key_pressed(KEY_Z):
		input_mask &= ~BTN_FIRE
	if Input.is_key_pressed(KEY_DOWN) or Input.is_key_pressed(KEY_S) or Input.is_key_pressed(KEY_K):
		input_mask &= ~BTN_SHIELD
	return input_mask


func start_credited_game(start_button: int) -> void:
	core.step(0xff & ~start_button)
	# Release Start and let the original game-state transitions play in real
	# time; do not skip forward to an already-active wave.
	game_running = true
	update_frame()


func update_frame() -> void:
	var background_rgba := core.video_layer_rgba(false)
	var foreground_rgba := core.video_layer_rgba(true)
	if background_rgba.size() != 208 * 256 * 4 or foreground_rgba.size() != 208 * 256 * 4:
		return
	var background_image := Image.create_from_data(208, 256, false, Image.FORMAT_RGBA8, background_rgba)
	var foreground_image := Image.create_from_data(208, 256, false, Image.FORMAT_RGBA8, foreground_rgba)
	if background_textures.is_empty():
		background_textures = [ImageTexture.create_from_image(background_image), ImageTexture.create_from_image(background_image)]
		foreground_textures = [ImageTexture.create_from_image(foreground_image), ImageTexture.create_from_image(foreground_image)]
	else:
		texture_index = 1 - texture_index
		background_textures[texture_index].update(background_image)
		foreground_textures[texture_index].update(foreground_image)
	set_layer_textures(background_sprite, background_textures)
	set_layer_textures(foreground_sprite, foreground_textures)


func set_layer_textures(sprite: Sprite2D, textures: Array[ImageTexture]) -> void:
	var material := sprite.material as ShaderMaterial
	var previous_index := 1 - texture_index
	sprite.texture = textures[texture_index]
	material.set_shader_parameter("source_texture", textures[texture_index])
	material.set_shader_parameter("previous_texture", textures[previous_index])
	material.set_shader_parameter("frame_blend", frame_blend)


func set_shader_blend(sprite: Sprite2D, blend: float) -> void:
	if sprite != null:
		(sprite.material as ShaderMaterial).set_shader_parameter("frame_blend", blend)


func create_video_layers() -> void:
	background_sprite = create_c2_sprite()
	foreground_sprite = create_c2_sprite()
	add_child(background_sprite)
	add_child(foreground_sprite)


func create_c2_sprite() -> Sprite2D:
	var sprite := Sprite2D.new()
	sprite.centered = false
	sprite.scale = Vector2(2, 2)
	var material := ShaderMaterial.new()
	material.shader = C2_HIRES_SHADER
	sprite.material = material
	return sprite


func create_prompt() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 1
	add_child(layer)
	prompt_panel = ColorRect.new()
	# Keep cabinet instructions below the normal player-ship flight area.
	prompt_panel.position = Vector2(18, 468)
	prompt_panel.size = Vector2(380, 40)
	prompt_panel.color = Color(0.0, 0.0, 0.0, 0.78)
	layer.add_child(prompt_panel)
	prompt_label = Label.new()
	prompt_label.position = Vector2(30, 471)
	prompt_label.size = Vector2(356, 30)
	prompt_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	prompt_label.add_theme_font_size_override("font_size", 18)
	prompt_label.add_theme_color_override("font_color", Color.WHITE)
	layer.add_child(prompt_label)


func create_audio() -> void:
	audio_player = AudioStreamPlayer.new()
	var stream := AudioStreamGenerator.new()
	stream.mix_rate = 48000.0
	stream.buffer_length = 0.35
	audio_player.stream = stream
	add_child(audio_player)
	audio_player.play()
	audio_playback = audio_player.get_stream_playback()


func queue_audio_frame() -> void:
	if audio_playback == null:
		audio_playback = audio_player.get_stream_playback()
		if audio_playback == null:
			return
	var pcm := core.audio_frame()
	for sample in pcm:
		if audio_playback.get_frames_available() <= 0:
			break
		var mono := float(sample) * 0.42
		audio_playback.push_frame(Vector2(mono, mono))


func refresh_prompt() -> void:
	if not demo_running:
		prompt_panel.visible = true
		prompt_label.text = "PRESS ENTER"
	elif not credit_inserted:
		prompt_panel.visible = true
		prompt_label.text = "PRESS C: COIN"
	elif not game_running:
		prompt_panel.visible = true
		prompt_label.text = "PRESS 1/ENTER: 1P · 2: 2P"
	else:
		prompt_panel.visible = false
		prompt_label.text = ""
