import whisper

model = whisper.load_model("tiny")
result = model.transcribe('jfk.flac')
print(result["text"])