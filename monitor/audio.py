import audioop
from typing import Dict, Iterator, Optional, Tuple
from multiprocessing import Process, Queue

import pyaudio

CHUNK = 1024 * 8
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100


class Audio:
    audio: pyaudio.PyAudio

    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def list_input_devices(self) -> Dict[int, str]:
        """Returns a mapping of index to name for all available input devices"""
        out = {}
        for n in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(n)
            try:
                max_channels = int(info["maxInputChannels"])
            except (ValueError, KeyError):
                max_channels = 0
            if max_channels < 1:
                continue
            out[n] = info["name"]
        return out

    def data_and_rms(self, input_device_index: int = 0) -> Iterator[Tuple[bytes, int]]:
        # We read our audio stream in a subprocess to ensure that we don't block and cause the buffer to overflow
        def read_stream(queue: Queue):
            try:
                while True:
                    stream = self.audio.open(
                        format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        input_device_index=input_device_index,
                    )
                    stream_open = True
                    while stream_open:
                        try:
                            data = stream.read(CHUNK)
                        except IOError:
                            # Even though we try to prevent overflows they sometimes still happen
                            # When they do just mark the stream as closed and then re-open it
                            stream_open = False
                        else:
                            queue.put_nowait(data)
                    stream.close()
            except KeyboardInterrupt:
                pass

        queue = Queue()
        reader = Process(target=read_stream, args=(queue,))
        reader.start()

        try:
            while reader.is_alive():
                data = queue.get()
                rms = audioop.rms(data, 2)
                yield data, rms
        finally:
            reader.terminate()
            reader.join()
