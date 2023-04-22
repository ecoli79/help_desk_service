from typing import List
from fastapi import FastAPI, File, UploadFile
#from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
import os
import shutil
#import librosa
from huggingsound import SpeechRecognitionModel

app = FastAPI()

model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-russian")

#tokenizer = Wav2Vec2Tokenizer.from_pretrained("facebook/wav2vec2-large-960h-lv60")
#model = Wav2Vec2ForCTC.from_pretrained("facebook/wav2vec2-large-960h-lv60")

@app.post("/transcribe/")
async def transcribe(files: List[UploadFile] = File(...)):
    contents = await files[0].read()
    with open("audio.wav", "wb") as f:
        f.write(contents)

    #speech, rate = librosa.load("audio.wav", sr=16000)
    #os.remove("audio.wav")

    #model = SpeechRecognitionModel("jonatasgrosman/wav2vec2-large-xlsr-53-russian")
    audio_paths = [os.path("audio.wav")]

    transcriptions = model.transcribe(audio_paths)

    #input_values = tokenizer(speech, return_tensors='pt').input_values
   # with torch.no_grad():
   #     logits = model(input_values).logits

    #predicted_ids = torch.argmax(logits, dim=-1)
    #transcription = tokenizer.batch_decode(predicted_ids)[0]
    os.remove("audio.wav")

    return {"transcription": transcription[0]['transcription']}
