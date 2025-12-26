from pydub import AudioSegment
import numpy as np
import matplotlib.pyplot as plt

# Load your audio file (MP3, WAV, etc.)
audio_path = "mic_recording_boosted.wav"
audio = AudioSegment.from_file(audio_path)

# Convert to mono to keep things simple
audio = audio.set_channels(1)

# Extract raw audio samples as a NumPy array
samples = np.array(audio.get_array_of_samples()).astype(np.float32)

# Normalize the waveform to range [-1, 1]
samples /= np.max(np.abs(samples))

# Get sample rate (frames per second)
sample_rate = audio.frame_rate

# Print summary
print(f"Audio duration: {len(samples)/sample_rate:.2f} seconds")
print(f"Sample rate: {sample_rate} Hz")

# Plot waveform using matplotlib
plt.figure(figsize=(12, 4))
plt.plot(samples, color='slateblue')
plt.title("Original Audio Waveform")
plt.xlabel("Sample Index")
plt.ylabel("Amplitude")
plt.grid(True)
plt.tight_layout()
plt.show()