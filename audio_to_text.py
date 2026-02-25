# import whisper

# model = whisper.load_model("base")

# # load audio and pad/trim it to fit 30 seconds
# audio = whisper.load_audio('./static/audio/voice.wav')   #("audio.mp3")
# #audio = whisper.pad_or_trim(audio)

# # make log-Mel spectrogram and move to the same device as the model
# mel = whisper.log_mel_spectrogram(audio).to(model.device)

# # detect the spoken language
# _, probs = model.detect_language(mel)
# print(f"Detected language: {max(probs, key=probs.get)}")

# # decode the audio
# options = whisper.DecodingOptions()
# result = whisper.decode(model, mel, options)

# # print the recognized text
# print(result.text)

# import requests

# url = "http://localhost:5000/api/speech-to-text"

# file = './static/audio/voice.wav'

# with open(file, 'rb') as f:
#     audio_file_content = f.read()


# data = {'audio': audio_file_content}

# response = requests.post(url, data = data)


from huggingsound import SpeechRecognitionModel

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
audio_paths = ["/home/medic/djangoproject/bot_support/static/audio/voice.wav"]

transcriptions = model.transcribe(audio_paths)
print(transcriptions[0]['transcription'])