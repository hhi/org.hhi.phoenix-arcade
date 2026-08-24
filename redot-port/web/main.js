import createPhoenixModule from "./build/phoenix_core.js?build=2";
import { createC2HiresRenderer } from "./c2_hires_renderer.js";

const ACTIVE_LOW_IDLE = 0xff;
const BUTTONS = {
  ArrowLeft: 0x40, KeyA: 0x40,
  ArrowRight: 0x20, KeyD: 0x20,
  Space: 0x10, KeyZ: 0x10,
  ShiftLeft: 0x80, ShiftRight: 0x80, KeyX: 0x80,
  Digit1: 0x02, Enter: 0x02,
  Digit2: 0x04,
  KeyC: 0x01,
};
const FRAME_INTERVAL_MS = 1000 / 60;

const canvas = document.querySelector("#phoenix-screen");
const startAudioButton = document.querySelector("#start-audio");
const status = document.querySelector("#status");
const renderer = createC2HiresRenderer(canvas);
const heldKeys = new Set();
const releasedAfterNextStep = new Set();
let module;
let audioContext;
let nextAudioTime = 0;
let lastFrameTime = 0;
let accumulator = 0;

function activeLowInputs() {
  let inputs = ACTIVE_LOW_IDLE;
  for (const key of heldKeys) inputs &= ~BUTTONS[key];
  return inputs;
}

function queueAudio() {
  const sampleCount = module._phoenix_web_audio_sample_count();
  if (!audioContext || sampleCount === 0) return;
  const sourcePointer = module._phoenix_web_audio_buffer() >> 1;
  const samples = module.HEAP16.slice(sourcePointer, sourcePointer + sampleCount);
  const buffer = audioContext.createBuffer(1, sampleCount, 48000);
  const channel = buffer.getChannelData(0);
  for (let index = 0; index < sampleCount; index++) channel[index] = samples[index] / 32768;
  const source = audioContext.createBufferSource();
  source.buffer = buffer;
  source.connect(audioContext.destination);
  nextAudioTime = Math.max(nextAudioTime, audioContext.currentTime + 0.03);
  source.start(nextAudioTime);
  nextAudioTime += buffer.duration;
}

function step() {
  module._phoenix_web_set_input(activeLowInputs());
  module._phoenix_web_step();
  // A short key press must survive at least one 60 Hz simulation step.
  // Coin and start are edge-triggered in the Phoenix cabinet interface.
  for (const key of releasedAfterNextStep) heldKeys.delete(key);
  releasedAfterNextStep.clear();
  const layerLength = module._phoenix_web_layer_length();
  const background = module.HEAPU8.subarray(
    module._phoenix_web_background_layer(),
    module._phoenix_web_background_layer() + layerLength,
  );
  const foreground = module.HEAPU8.subarray(
    module._phoenix_web_foreground_layer(),
    module._phoenix_web_foreground_layer() + layerLength,
  );
  renderer.pushLayers(background, foreground);
  queueAudio();
}

function animationFrame(now) {
  if (!lastFrameTime) lastFrameTime = now;
  accumulator += Math.min(now - lastFrameTime, 250);
  lastFrameTime = now;
  while (accumulator >= FRAME_INTERVAL_MS) {
    step();
    accumulator -= FRAME_INTERVAL_MS;
  }
  renderer.render(accumulator / FRAME_INTERVAL_MS);
  requestAnimationFrame(animationFrame);
}

for (const eventName of ["keydown", "keyup"]) {
  window.addEventListener(eventName, (event) => {
    if (BUTTONS[event.code] === undefined) return;
    event.preventDefault();
    if (eventName === "keydown") {
      releasedAfterNextStep.delete(event.code);
      heldKeys.add(event.code);
    } else {
      releasedAfterNextStep.add(event.code);
    }
  });
}

startAudioButton.addEventListener("click", async () => {
  audioContext ??= new AudioContext({ sampleRate: 48000 });
  await audioContext.resume();
  startAudioButton.hidden = true;
  status.textContent = "Phoenix is running in WebAssembly.";
});

try {
  module = await createPhoenixModule();
  window.__phoenixModule = module; // Development-only probe for browser parity checks.
  module._phoenix_web_create();
  const layerLength = module._phoenix_web_layer_length();
  renderer.pushLayers(
    module.HEAPU8.subarray(module._phoenix_web_background_layer(), module._phoenix_web_background_layer() + layerLength),
    module.HEAPU8.subarray(module._phoenix_web_foreground_layer(), module._phoenix_web_foreground_layer() + layerLength),
  );
  status.textContent = "Ready. Click start to enable audio.";
  requestAnimationFrame(animationFrame);
} catch (error) {
  status.textContent = `Loading failed: ${error.message}`;
  console.error(error);
}
