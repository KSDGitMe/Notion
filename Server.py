from flask import Flask, render_template, request

from werkzeug.utils import secure_filename
import os
import main
app = Flask(__name__)

@app.route('/get-audio', methods=['GET'])
def audio_input():
    # This will serve the getaudio.html file from the templates folder
    return render_template('getaudio.html')


UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_audio(file_path):
    # Call your function here to process the audio
    #main()
    
    
    print(f"Processing file: {file_path}")
    # Example: Your function to process the audio file
    upload_file()
    
    #result = main.main(file_path)
print("Before audio processing")
@app.route('/process-audio', methods=['POST'])
def upload_file():
    print("in upload")
    if 'audio' not in request.files:
        return 'No file part', 400
    file = request.files['audio']
    if file.filename == '':
        return 'No selected file', 400
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        print("filepath: " + filepath)
        main.main(filepath)
        return 'File uploaded and processed successfully', 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001, debug=True, use_evalex=False )  # Uncomment this for production use







#if __name__ == "__main__":
    #app.run(debug=True, use_evalex=False )  # Uncomment this for production use