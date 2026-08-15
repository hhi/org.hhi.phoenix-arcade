#include "phoenix_core_extension.h"

#include <godot_cpp/core/class_db.hpp>
#include <godot_cpp/variant/array.hpp>

extern "C" {
#include "redot_core.h"
}

using namespace godot;

static Dictionary to_dictionary(const PhoenixRedotSnapshot &state) {
	Dictionary result;
	result["game_or_attract"] = state.game_or_attract;
	result["game_state"] = state.game_state;
	result["level_and_round"] = state.level_and_round;
	result["player_x"] = state.player_x;
	result["player_y"] = state.player_y;
	result["player_bullet_x"] = state.player_bullet_x;
	result["player_bullet_y"] = state.player_bullet_y;
	result["player_bullet_state"] = state.player_bullet_state;
	result["player_lives"] = state.player_lives;
	result["aliens_left"] = state.aliens_left;
	result["birds_left"] = state.birds_left;
	result["score"] = static_cast<int64_t>(state.score);
	Array aliens;
	Array birds;
	Array enemy_bullets;
	for (const PhoenixRedotObject &object : state.aliens) {
		Dictionary value;
		value["active"] = object.active != 0;
		value["shape"] = object.shape;
		value["x"] = object.x;
		value["y"] = object.y;
		aliens.append(value);
	}
	for (const PhoenixRedotObject &object : state.birds) {
		Dictionary value;
		value["active"] = object.active != 0;
		value["shape"] = object.shape;
		value["x"] = object.x;
		value["y"] = object.y;
		value["screen_addr"] = object.screen_addr;
		birds.append(value);
	}
	for (const PhoenixRedotObject &object : state.enemy_bullets) {
		Dictionary value;
		value["active"] = object.active != 0;
		value["x"] = object.x;
		value["y"] = object.y;
		enemy_bullets.append(value);
	}
	result["aliens"] = aliens;
	result["birds"] = birds;
	result["enemy_bullets"] = enemy_bullets;
	return result;
}

void PhoenixCore::_bind_methods() {
	ClassDB::bind_method(D_METHOD("reset"), &PhoenixCore::reset);
	ClassDB::bind_method(D_METHOD("step", "input_mask"), &PhoenixCore::step);
	ClassDB::bind_method(D_METHOD("snapshot"), &PhoenixCore::snapshot);
	ClassDB::bind_method(D_METHOD("frame_rgba"), &PhoenixCore::frame_rgba);
	ClassDB::bind_method(D_METHOD("video_layer_rgba", "foreground"), &PhoenixCore::video_layer_rgba);
	ClassDB::bind_method(D_METHOD("audio_frame"), &PhoenixCore::audio_frame);
}

PhoenixCore::PhoenixCore() {
	reset();
}

void PhoenixCore::reset() {
	phoenix_redot_create();
}

Dictionary PhoenixCore::step(int input_mask) {
	phoenix_redot_set_input(static_cast<uint8_t>(input_mask));
	phoenix_redot_step();
	return snapshot();
}

Dictionary PhoenixCore::snapshot() const {
	PhoenixRedotSnapshot state = {};
	phoenix_redot_snapshot(&state);
	return to_dictionary(state);
}

PackedByteArray PhoenixCore::frame_rgba() const {
	PackedByteArray frame;
	frame.resize(416 * 512 * 4);
	phoenix_redot_frame_rgba(frame.ptrw(), frame.size());
	return frame;
}

PackedByteArray PhoenixCore::video_layer_rgba(bool foreground) const {
	PackedByteArray frame;
	frame.resize(208 * 256 * 4);
	phoenix_redot_layer_rgba(frame.ptrw(), frame.size(), foreground ? 1 : 0);
	return frame;
}

PackedFloat32Array PhoenixCore::audio_frame() {
	int16_t pcm[1024] = {};
	uint32_t samples = phoenix_redot_audio_pcm(pcm, 1024);
	PackedFloat32Array output;
	output.resize(samples);
	for (uint32_t index = 0; index < samples; index++) {
		output.set(index, static_cast<float>(pcm[index]) / 32768.0f);
	}
	return output;
}
