import audioop
import pyaudio

SAMPLING_RATE = 22050
NUM_SAMPLES = 2048

def main():
    pa = pyaudio.PyAudio()
    stream = pa.open(format=pyaudio.paInt16, channels=1, rate=SAMPLING_RATE,
                     input=True, frames_per_buffer=NUM_SAMPLES)
    while True:
        data = stream.read(NUM_SAMPLES)
        rms = audioop.rms(data, 2)
        print(rms)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
