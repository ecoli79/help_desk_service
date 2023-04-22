from huggingsound import SpeechRecognitionModel

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
audio_paths = ["/home/medic/djangoproject/bot_support/static/audio/voice.wav"]

transcriptions = model.transcribe(audio_paths)
print(transcriptions[0]['transcription'])