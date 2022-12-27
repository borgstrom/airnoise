from typing import Dict

import pyaudio


class Audio:
    audio: pyaudio.PyAudio

    def __init__(self):
        self.audio = pyaudio.PyAudio()

    def list_input_devices(self) -> Dict[int, str]:
        """Returns a mapping of index to name for all available input devices"""
        out = {}
        for n in range(self.audio.get_device_count()):
            info = self.audio.get_device_info_by_index(n)
            if info["maxInputChannels"] < 1:
                continue
            out[n] = info["name"]
        return out
