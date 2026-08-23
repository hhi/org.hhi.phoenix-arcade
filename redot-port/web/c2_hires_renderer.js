const VERTEX_SHADER = `#version 300 es
in vec2 position;
out vec2 uv;
void main() { uv = position * 0.5 + 0.5; gl_Position = vec4(position, 0.0, 1.0); }
`;

// WebGL translation of shaders/c2_hires.gdshader. The source remains the
// original 208x256 Phoenix layer; this pass alone produces the 416x512 view.
const FRAGMENT_SHADER = `#version 300 es
precision mediump float;
uniform vec2 source_pixel_size;
uniform sampler2D source_texture;
uniform sampler2D previous_texture;
uniform float frame_blend;
in vec2 uv;
out vec4 colour;
vec4 texel_at(vec2 cell) {
  vec2 size = 1.0 / source_pixel_size;
  cell = clamp(cell, vec2(0.0), size - vec2(1.0));
  vec2 sample_uv = (cell + vec2(0.5)) * source_pixel_size;
  return mix(texture(previous_texture, sample_uv), texture(source_texture, sample_uv), frame_blend);
}
bool same_pixel(vec4 a, vec4 b) {
  return max(max(abs(a.r-b.r), abs(a.g-b.g)), max(abs(a.b-b.b), abs(a.a-b.a))) < 0.004;
}
float stable_noise(vec2 point, float channel) {
  return fract(sin(dot(point + channel * 19.19, vec2(12.9898, 78.233))) * 43758.5453);
}
void main() {
  vec2 source_position = uv / source_pixel_size;
  vec2 cell = floor(source_position);
  vec2 quadrant = fract(source_position);
  vec4 e = texel_at(cell), b = texel_at(cell + vec2(0.0, -1.0));
  vec4 d = texel_at(cell + vec2(-1.0, 0.0)), f = texel_at(cell + vec2(1.0, 0.0));
  vec4 h = texel_at(cell + vec2(0.0, 1.0));
  vec4 result = e;
  if (e.a > 0.0 && !same_pixel(b,h) && !same_pixel(d,f)) {
    if (quadrant.x < 0.5 && quadrant.y < 0.5 && same_pixel(d,b)) result = d;
    if (quadrant.x >= 0.5 && quadrant.y < 0.5 && same_pixel(b,f)) result = f;
    if (quadrant.x < 0.5 && quadrant.y >= 0.5 && same_pixel(d,h)) result = d;
    if (quadrant.x >= 0.5 && quadrant.y >= 0.5 && same_pixel(h,f)) result = f;
  }
  if (result.a == 0.0) { colour = result; return; }
  vec3 mixed = result.rgb; float samples = 1.0;
  if (b.a > 0.0 && !same_pixel(result,b)) { mixed += b.rgb; samples += 1.0; }
  if (d.a > 0.0 && !same_pixel(result,d)) { mixed += d.rgb; samples += 1.0; }
  if (f.a > 0.0 && !same_pixel(result,f)) { mixed += f.rgb; samples += 1.0; }
  if (h.a > 0.0 && !same_pixel(result,h)) { mixed += h.rgb; samples += 1.0; }
  mixed = mix(result.rgb, mixed / samples, 0.42);
  vec2 output_cell = floor(uv / (source_pixel_size * 0.5));
  vec3 grain = vec3(stable_noise(output_cell,0.0), stable_noise(output_cell,1.0), stable_noise(output_cell,2.0)) - 0.5;
  colour = vec4(clamp(mixed + grain * (6.0/255.0), 0.0, 1.0), result.a);
}`;

function compile(gl, type, source) {
  const shader = gl.createShader(type);
  gl.shaderSource(shader, source);
  gl.compileShader(shader);
  if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(shader));
  return shader;
}

export function createC2HiresRenderer(canvas) {
  const gl = canvas.getContext("webgl2", { alpha: false, antialias: false });
  if (!gl) throw new Error("WebGL 2 is vereist voor de Redot C2-hires-presentatie.");
  const program = gl.createProgram();
  gl.attachShader(program, compile(gl, gl.VERTEX_SHADER, VERTEX_SHADER));
  gl.attachShader(program, compile(gl, gl.FRAGMENT_SHADER, FRAGMENT_SHADER));
  gl.linkProgram(program);
  if (!gl.getProgramParameter(program, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(program));
  gl.useProgram(program);
  const vertexArray = gl.createVertexArray();
  gl.bindVertexArray(vertexArray);
  const buffer = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1, 1,-1, -1,1, 1,1]), gl.STATIC_DRAW);
  const position = gl.getAttribLocation(program, "position");
  gl.enableVertexAttribArray(position);
  gl.vertexAttribPointer(position, 2, gl.FLOAT, false, 0, 0);
  const textures = Array.from({ length: 4 }, () => {
    const texture = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    return texture;
  });
  let textureIndex = 0;
  let initialized = false;
  const upload = (texture, pixels) => {
    gl.bindTexture(gl.TEXTURE_2D, texture);
    // Phoenix layer rows start at the visual top, just like Redot's Image.
    // WebGL texture uploads use the opposite origin unless this is enabled.
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 208, 256, 0, gl.RGBA, gl.UNSIGNED_BYTE, pixels);
  };
  const drawLayer = (current, previous, blend) => {
    gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, current);
    gl.activeTexture(gl.TEXTURE1); gl.bindTexture(gl.TEXTURE_2D, previous);
    gl.uniform1i(gl.getUniformLocation(program, "source_texture"), 0);
    gl.uniform1i(gl.getUniformLocation(program, "previous_texture"), 1);
    gl.uniform2f(gl.getUniformLocation(program, "source_pixel_size"), 1 / 208, 1 / 256);
    gl.uniform1f(gl.getUniformLocation(program, "frame_blend"), blend);
    gl.drawArrays(gl.TRIANGLE_STRIP, 0, 4);
  };
  return {
    pushLayers(background, foreground) {
      textureIndex = 1 - textureIndex;
      upload(textures[textureIndex], background);
      upload(textures[textureIndex + 2], foreground);
      if (!initialized) {
        upload(textures[1 - textureIndex], background);
        upload(textures[3 - textureIndex], foreground);
        initialized = true;
      }
    },
    render(blend) {
      gl.viewport(0, 0, canvas.width, canvas.height);
      gl.clearColor(0, 0, 0, 1); gl.clear(gl.COLOR_BUFFER_BIT);
      gl.disable(gl.BLEND);
      drawLayer(textures[textureIndex], textures[1 - textureIndex], blend);
      gl.enable(gl.BLEND); gl.blendFunc(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA);
      drawLayer(textures[textureIndex + 2], textures[3 - textureIndex], blend);
    },
  };
}
