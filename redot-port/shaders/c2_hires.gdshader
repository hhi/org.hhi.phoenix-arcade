shader_type canvas_item;

uniform vec2 source_pixel_size = vec2(0.0048076923, 0.00390625);
uniform sampler2D source_texture : source_color, filter_nearest;
uniform sampler2D previous_texture : source_color, filter_nearest;
uniform float frame_blend : hint_range(0.0, 1.0) = 1.0;

// GPU counterpart of the C2 hires presentation pass.  The input is one raw
// 208x256 Phoenix layer; the Sprite2D is drawn at exactly 2x before the window
// scaler runs.  Keeping this pass in Redot avoids uploading a CPU-made 416x512
// framebuffer every frame.

vec4 texel_at(vec2 cell) {
	vec2 size = 1.0 / source_pixel_size;
	cell = clamp(cell, vec2(0.0), size - vec2(1.0));
	vec2 uv = (cell + vec2(0.5)) * source_pixel_size;
	return mix(texture(previous_texture, uv), texture(source_texture, uv), frame_blend);
}

bool same_pixel(vec4 a, vec4 b) {
	return max(max(abs(a.r - b.r), abs(a.g - b.g)), max(abs(a.b - b.b), abs(a.a - b.a))) < 0.004;
}

float stable_noise(vec2 point, float channel) {
	return fract(sin(dot(point + channel * 19.19, vec2(12.9898, 78.233))) * 43758.5453);
}

void fragment() {
	vec2 source_position = UV / source_pixel_size;
	vec2 cell = floor(source_position);
	vec2 quadrant = fract(source_position);
	vec4 e = texel_at(cell);
	vec4 b = texel_at(cell + vec2(0.0, -1.0));
	vec4 d = texel_at(cell + vec2(-1.0, 0.0));
	vec4 f = texel_at(cell + vec2(1.0, 0.0));
	vec4 h = texel_at(cell + vec2(0.0, 1.0));
	vec4 result = e;

	// The exact C2 Scale2x decision tree, now evaluated per GPU fragment.
	if (e.a > 0.0 && !same_pixel(b, h) && !same_pixel(d, f)) {
		if (quadrant.x < 0.5 && quadrant.y < 0.5 && same_pixel(d, b)) result = d;
		if (quadrant.x >= 0.5 && quadrant.y < 0.5 && same_pixel(b, f)) result = f;
		if (quadrant.x < 0.5 && quadrant.y >= 0.5 && same_pixel(d, h)) result = d;
		if (quadrant.x >= 0.5 && quadrant.y >= 0.5 && same_pixel(h, f)) result = f;
	}
	if (result.a == 0.0) {
		COLOR = result;
	} else {
		// C2's colour-transition treatment, restricted to opaque neighbours so
		// silhouettes stay crisp. The colour grain is coordinate-stable: no flicker.
		vec3 mixed = result.rgb;
		float samples = 1.0;
		if (b.a > 0.0 && !same_pixel(result, b)) { mixed += b.rgb; samples += 1.0; }
		if (d.a > 0.0 && !same_pixel(result, d)) { mixed += d.rgb; samples += 1.0; }
		if (f.a > 0.0 && !same_pixel(result, f)) { mixed += f.rgb; samples += 1.0; }
		if (h.a > 0.0 && !same_pixel(result, h)) { mixed += h.rgb; samples += 1.0; }
		mixed = mix(result.rgb, mixed / samples, 0.42);
		vec2 output_cell = floor(UV / (source_pixel_size * 0.5));
		vec3 grain = vec3(stable_noise(output_cell, 0.0), stable_noise(output_cell, 1.0), stable_noise(output_cell, 2.0)) - 0.5;
		COLOR = vec4(clamp(mixed + grain * (6.0 / 255.0), 0.0, 1.0), result.a);
	}
}
