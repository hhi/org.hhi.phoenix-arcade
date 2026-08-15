#ifndef PHOENIX_CORE_EXTENSION_H
#define PHOENIX_CORE_EXTENSION_H

#include <godot_cpp/classes/ref_counted.hpp>
#include <godot_cpp/variant/dictionary.hpp>
#include <godot_cpp/variant/packed_byte_array.hpp>
#include <godot_cpp/variant/packed_float32_array.hpp>

namespace godot {

class PhoenixCore : public RefCounted {
	GDCLASS(PhoenixCore, RefCounted)

protected:
	static void _bind_methods();

public:
	PhoenixCore();
	void reset();
	Dictionary step(int input_mask);
	Dictionary snapshot() const;
	PackedByteArray frame_rgba() const;
	PackedByteArray video_layer_rgba(bool foreground) const;
	PackedFloat32Array audio_frame();
};

} // namespace godot

#endif
