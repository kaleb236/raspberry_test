import pyaudio
import numpy as np
import matplotlib.pyplot as plt
import wave
import time

# ======================
# Audio configuration
# ======================
FORMAT = pyaudio.paInt16
CHANNELS = 2            
RATE = 48000            
CHUNK = 2048            
GAIN = 1.0              # This is a linear multiplier

RECORD_SECONDS = 10
OUTPUT_FILENAME = "mic_recording_boosted.wav"
frames = []             

p = pyaudio.PyAudio()

stream = p.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK
)

print(f"🎤 Recording with {GAIN}x Gain...")

# ======================
# Streaming loop
# ======================
start_time = time.time()

try:
    while time.time() - start_time < RECORD_SECONDS:
        # 1. Read raw data
        data = stream.read(CHUNK, exception_on_overflow=False)
        
        # 2. Convert to numpy to apply gain
        samples = np.frombuffer(data, dtype=np.int16)[0::2].astype(np.float32)
        
        # 3. Apply Gain
        # samples = samples * GAIN
        
        # 4. CRITICAL: Clip the values
        # 16-bit audio must stay between -32768 and 32767
        samples = np.clip(samples, -32768, 32767)
        
        # 5. Convert back to Int16 and save
        boosted_data = samples.astype(np.int16).tobytes()
        frames.append(boosted_data)

    print("⏹ Done recording.")

except KeyboardInterrupt:
    print("\n🛑 Stopped.")

finally:
    stream.stop_stream()
    stream.close()
    p.terminate()

    with wave.open(OUTPUT_FILENAME, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2) 
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    print(f"💾 Saved BOOSTED recording to {OUTPUT_FILENAME}")