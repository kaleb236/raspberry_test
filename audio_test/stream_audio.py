import asyncio
import numpy as np
import pyaudio
from google import genai

# --- Configuration ---
MODEL = "gemini-2.0-flash-exp"
MIC_SAMPLE_RATE = 48000 
SPEAKER_SAMPLE_RATE = 48000 
SEND_SAMPLE_RATE = 16000
RECEIVE_SAMPLE_RATE = 24000
CHANNELS = 1
FORMAT = pyaudio.paInt16
CHUNK_SIZE = 2048 

class GeminiLiveClient:
    def __init__(self):
        self.client = genai.Client()
        self.pya = pyaudio.PyAudio()
        self.audio_queue_output = asyncio.Queue()
        self.audio_queue_mic = asyncio.Queue(maxsize=10)
        
        # The "Gatekeeper": When set, mic data is sent. When cleared, mic data is ignored.
        self.is_gemini_silent = asyncio.Event()
        self.is_gemini_silent.set() # Start by listening

    def resample(self, data, input_rate, output_rate):
        audio_np = np.frombuffer(data, dtype=np.int16)
        if input_rate == output_rate:
            return data
        duration = len(audio_np) / input_rate
        num_samples = int(duration * output_rate)
        resampled_data = np.interp(
            np.linspace(0, duration, num_samples, endpoint=False),
            np.linspace(0, duration, len(audio_np), endpoint=False),
            audio_np
        )
        return resampled_data.astype(np.int16).tobytes()

    async def listen_audio(self):
        """Captures audio but only queues it if Gemini is silent."""
        mic_info = self.pya.get_default_input_device_info()
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=MIC_SAMPLE_RATE,
            input=True,
            input_device_index=mic_info["index"],
            frames_per_buffer=CHUNK_SIZE,
        )
        
        print("Microphone active...")
        try:
            while True:
                data = await asyncio.to_thread(stream.read, CHUNK_SIZE, exception_on_overflow=False)
                
                # CHECK THE GATE: If Gemini is talking, we discard the mic input
                if self.is_gemini_silent.is_set():
                    resampled_data = self.resample(data, MIC_SAMPLE_RATE, SEND_SAMPLE_RATE)
                    await self.audio_queue_mic.put({"data": resampled_data, "mime_type": "audio/pcm"})
                else:
                    # Optional: Clear the queue while Gemini is talking to ensure no lag
                    while not self.audio_queue_mic.empty():
                        self.audio_queue_mic.get_nowait()
        finally:
            stream.stop_stream()
            stream.close()

    async def send_realtime(self, session):
        while True:
            msg = await self.audio_queue_mic.get()
            await session.send_realtime_input(audio=msg)

    async def receive_audio(self, session):
        """Monitors when Gemini starts and stops talking."""
        while True:
            turn = session.receive()
            async for response in turn:
                # If we get a response, Gemini is starting to talk
                if response.server_content and response.server_content.model_turn:
                    self.is_gemini_silent.clear() # STOP listening
                    
                    for part in response.server_content.model_turn.parts:
                        if part.inline_data and isinstance(part.inline_data.data, bytes):
                            self.audio_queue_output.put_nowait(part.inline_data.data)

            # Once the 'turn' iterator finishes, Gemini is done talking
            self.is_gemini_silent.set() # START listening again

    async def play_audio(self):
        stream = await asyncio.to_thread(
            self.pya.open,
            format=FORMAT,
            channels=CHANNELS,
            rate=SPEAKER_SAMPLE_RATE,
            output=True,
        )
        try:
            while True:
                bytestream = await self.audio_queue_output.get()
                upsampled_data = self.resample(bytestream, RECEIVE_SAMPLE_RATE, SPEAKER_SAMPLE_RATE)
                await asyncio.to_thread(stream.write, upsampled_data)
        finally:
            stream.stop_stream()
            stream.close()

    async def run(self):
        config = {
            "response_modalities": ["AUDIO"],
            "system_instruction": "Lütfen sadece Türkçe konuş.",
            "speech_config": {
                "voice_config": {
                    "prebuilt_voice_config": {
                        "voice_name": "Leda"  # Set the specific voice
                    }
                },
                "language_code": "tr-TR"  # Set Turkish (Turkey)
            }
        }
        try:
            async with self.client.aio.live.connect(model=MODEL, config=config) as session:
                print("Connected! Gemini is ready.")
                async with asyncio.TaskGroup() as tg:
                    tg.create_task(self.listen_audio())
                    tg.create_task(self.send_realtime(session))
                    tg.create_task(self.receive_audio(session))
                    tg.create_task(self.play_audio())
        except Exception as e:
            print(f"Error: {e}")
        finally:
            self.pya.terminate()

if __name__ == "__main__":
    client_app = GeminiLiveClient()
    try:
        asyncio.run(client_app.run())
    except KeyboardInterrupt:
        print("Stopped.")