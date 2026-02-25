import os
import torch
import librosa
import numpy as np
from transformers import Wav2Vec2ForCTC, Wav2Vec2Tokenizer
from flask import Flask, jsonify, request
from flask_cors import CORS

# Инициализация модели Wave2Vec2
tokenizer = Wav2Vec2Tokenizer.from_pretrained("wav2vec2-large-xlsr-53-russian")
model = Wav2Vec2ForCTC.from_pretrained("wav2vec2-large-xlsr-53-russian")

# Инициализация Flask приложения
app = Flask(__name__)
CORS(app)

# Обработка POST-запросов на распознавание речи
@app.route('/api/speech-to-text', methods=['POST'])
def speech_to_text():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if not file.filename.endswith('.wav'):
        return jsonify({'error': 'Unsupported media type'}), 415
    
    wav, _ = librosa.load(file)
    input_values = tokenizer(wav, return_tensors='pt').input_values
    logits = model(input_values).logits
    predicted_ids = torch.argmax(logits, dim=-1)
    transcription = tokenizer.batch_decode(predicted_ids)[0].replace('<s>', '').replace('</s>', '')
    
    return jsonify({'transcription': transcription})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
