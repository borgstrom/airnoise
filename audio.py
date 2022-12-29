import audioop
from typing import Dict, Iterator, Optional

import pyaudio

SAMPLING_RATE = 22050
NUM_SAMPLES = 1024 * 4


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

    def rms(self, input_device_index: Optional[int] = None) -> Iterator[int]:
        stream = self.audio.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=SAMPLING_RATE,
            input=True,
            input_device_index=input_device_index,
            frames_per_buffer=NUM_SAMPLES,
        )
        while True:
            data = stream.read(NUM_SAMPLES)
            rms = audioop.rms(data, 2)
            yield rms
