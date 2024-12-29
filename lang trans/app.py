from flask import Flask, render_template, request, jsonify, send_file
import speech_recognition as spr
from googletrans import Translator
from gtts import gTTS
import os

app = Flask(__name__)

# Ensure the 'outputs' folder exists
if not os.path.exists('outputs'):
    os.makedirs('outputs')

# Initialize recognizer and translator
recog1 = spr.Recognizer()
translator = Translator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_audio():
    try:
        # Retrieve target language from form
        target_language = request.form['language']
        language_map = {
            'Hindi': 'hi',
            'Telugu': 'te',
            'Kannada': 'kn',
            'Tamil': 'ta',
            'Malayalam': 'ml',
            'Bengali': 'bn',
            'English': 'en',
        }
        if target_language not in language_map:
            return jsonify({'error': f"Invalid language: {target_language}"})

        target_language_code = language_map[target_language]

        # Save the uploaded file
        audio_file = request.files['audio']
        audio_path = os.path.join('outputs', audio_file.filename)
        audio_file.save(audio_path)

        # Recognize speech from audio
        with spr.AudioFile(audio_path) as source:
            audio = recog1.record(source)

        recognized_text = recog1.recognize_google(audio)
        print(f"Recognized Text: {recognized_text}")

        # Detect the language
        detected_language = translator.detect(recognized_text).lang
        print(f"Detected Language: {detected_language}")

        # Translate the text
        translation = translator.translate(recognized_text, src=detected_language, dest=target_language_code)
        translated_text = translation.text
        print(f"Translated Text: {translated_text}")

        # Convert translated text to audio
        tts = gTTS(text=translated_text, lang=target_language_code, slow=False)
        output_audio_file = os.path.join('outputs', f"translated_{target_language}.mp3")
        tts.save(output_audio_file)

        return jsonify({
            'recognized_text': recognized_text,
            'translated_text': translated_text,
            'audio_file': output_audio_file,
        })
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/outputs/<path:filename>')
def get_audio_file(filename):
    return send_file(os.path.join('outputs', filename))

if __name__ == '__main__':
    app.run(debug=True)
