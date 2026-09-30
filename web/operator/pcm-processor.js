class PCM16Downsampler extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.targetSampleRate = options?.processorOptions?.targetSampleRate || 16000;
    this.ratio = sampleRate / this.targetSampleRate;
    this.buffer = [];
    this.cursor = 0;
  }

  process(inputs) {
    const channel = inputs?.[0]?.[0];
    if (!channel || channel.length === 0) return true;

    for (let i = 0; i < channel.length; i += 1) {
      this.buffer.push(channel[i]);
    }

    const pcm = [];
    while (this.cursor + this.ratio <= this.buffer.length) {
      const start = Math.floor(this.cursor);
      const end = Math.max(start + 1, Math.floor(this.cursor + this.ratio));
      let sum = 0;
      let count = 0;
      for (let i = start; i < end && i < this.buffer.length; i += 1) {
        sum += this.buffer[i];
        count += 1;
      }
      const sample = Math.max(-1, Math.min(1, count ? sum / count : 0));
      pcm.push(sample < 0 ? sample * 0x8000 : sample * 0x7fff);
      this.cursor += this.ratio;
    }

    const consumed = Math.floor(this.cursor);
    if (consumed > 0) {
      this.buffer = this.buffer.slice(consumed);
      this.cursor -= consumed;
    }

    if (pcm.length) {
      const out = new Int16Array(pcm.length);
      for (let i = 0; i < pcm.length; i += 1) out[i] = pcm[i];
      this.port.postMessage(out.buffer, [out.buffer]);
    }

    return true;
  }
}

registerProcessor("pcm16-downsampler", PCM16Downsampler);
