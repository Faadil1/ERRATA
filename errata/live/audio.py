from __future__ import annotations

import asyncio
import base64
from dataclasses import dataclass


SAMPLE_RATE = 24_000
CHANNELS = 1
DTYPE = "int16"
BLOCK_FRAMES = 1_200  # 50 ms at 24 kHz


class AudioDependencyError(RuntimeError):
    pass


def _sd():
    try:
        import sounddevice as sd
    except ImportError as exc:
        raise AudioDependencyError(
            "sounddevice is required for a live microphone run. "
            "Install requirements-live.txt and PortAudio for your OS."
        ) from exc
    return sd


@dataclass
class LiveAudio:
    loop: asyncio.AbstractEventLoop
    queue: asyncio.Queue[bytes]
    input_stream: object | None = None
    output_stream: object | None = None

    @classmethod
    def create(cls) -> "LiveAudio":
        loop = asyncio.get_running_loop()
        return cls(loop=loop, queue=asyncio.Queue(maxsize=100))

    def start(self) -> None:
        sd = _sd()

        def on_input(indata, frames, time_info, status):
            chunk = bytes(indata)
            def put():
                if not self.queue.full():
                    self.queue.put_nowait(chunk)
            self.loop.call_soon_threadsafe(put)

        self.input_stream = sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_FRAMES,
            channels=CHANNELS,
            dtype=DTYPE,
            callback=on_input,
        )
        self.output_stream = sd.RawOutputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
        )
        self.input_stream.start()
        self.output_stream.start()

    def stop(self) -> None:
        for stream in (self.input_stream, self.output_stream):
            if stream is None:
                continue
            try:
                stream.stop()
            except Exception:
                pass
            try:
                stream.close()
            except Exception:
                pass

    def play_b64(self, data: str) -> None:
        if self.output_stream is None:
            return
        self.output_stream.write(base64.b64decode(data))

    def flush_output(self) -> None:
        if self.output_stream is None:
            return
        try:
            self.output_stream.abort()
            self.output_stream.start()
        except Exception:
            pass
