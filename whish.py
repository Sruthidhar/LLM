from transformers import WhisperProcessor, WhisperForConditionalGeneration
from pydub import AudioSegment
import numpy as np

processor = WhisperProcessor.from_pretrained("openai/whisper-large")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-large")

audio_path = "/home/llm-01/Downloads/sd.aac"

audio = AudioSegment.from_file(audio_path, format="aac")

audio = audio.set_frame_rate(16000).set_channels(1)
audio_data = np.array(audio.get_array_of_samples(), dtype=np.float32) / 32768.0

ds = processor(audio_data, sampling_rate=16000, return_tensors="pt", padding="longest")
input_features = ds.input_features

forced_decoder_ids = processor.get_decoder_prompt_ids(language="english", task="translate")

predicted_ids = model.generate(input_features, forced_decoder_ids=forced_decoder_ids)

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
print(transcription[0])
