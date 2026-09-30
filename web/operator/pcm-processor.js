class PCM16Downsampler extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.targetSampleRate = options?.processorOptions?.targetSampleRate || 16000;
    this.chunkDurationMs = options?.processorOptions?.chunkDurationMs || 100;
    this.ratio = sampleRate / this.targetSampleRate;
    this.inputBuffer = [];
    this.cursor = 0;
    this.outputBuffer = [];
    this.targetChunkSamples = Math.max(
      800,
      Math.round(this.targetSampleRate * this.chunkDurationMs / 1000),
    );
  }

  flushChunk() {
    if (this.outputBuffer.length < this.targetChunkSamples) return;
    const out = new Int16Array(this.targetChunkSamples);
    for (let i = 0; i < this.targetChunkSamples; i += 1) {
      out[i] = this.outputBuffer[i];
    }
    this.outputBuffer = this.outputBuffer.slice(this.targetChunkSamples);
    this.port.postMessage(out.buffer, [out.buffer]);
  }

  process(inputs) {
    const channel = inputs?.[0]?.[0];
    if (!channel || channel.length === 0) return true;

    for (let i = 0; i < channel.length; i += 1) {
      this.inputBuffer.push(channel[i]);
    }

    while (this.cursor + this.ratio <= this.inputBuffer.length) {
      const start = Math.floor(this.cursor);
      const end = Math.max(start + 1, Math.floor(this.cursor + this.ratio));
      let sum = 0;
      let count = 0;

      for (let i = start; i < end && i < this.inputBuffer.length; i += 1) {
        sum += this.inputBuffer[i];
        count += 1;
      }

      const sample = Math.max(-1, Math.min(1, count ? sum / count : 0));
      this.outputBuffer.push(
        sample < 0 ? Math.round(sample * 0x8000) : Math.round(sample * 0x7fff),
      );
      this.cursor += this.ratio;
      this.flushChunk();
    }

    const consumed = Math.floor(this.cursor);
    if (consumed > 0) {
      this.inputBuffer = this.inputBuffer.slice(consumed);
      this.cursor -= consumed;
    }

    return true;
  }
}

registerProcessor("pcm16-downsampler", PCM16Downsampler);
