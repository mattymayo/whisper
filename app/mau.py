from kivy.app import App
from kivy.uix.button import  Button
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.properties import StringProperty
import whisper
from transformers import M2M100ForConditionalGeneration
from tokenization_small100 import SMALL100Tokenizer
import speech_recognition as sr

"""for index, name in enumerate(sr.Microphone.list_microphone_names()):
    print("Microphone with name \"{1}\" found for `Microphone(device_index={0})`".format(index, name))"""

r = sr.Recognizer()
m = sr.Microphone()

record_var = ""

model_whisper = whisper.load_model("base")
model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100")
tokenizer = SMALL100Tokenizer.from_pretrained("alirezamsh/small100")

class RecordButton(Button):
    # String Property to Hold output for publishing by Textinput

    def record(self):
        # GUI Blocking Audio Capture
        with m as source:
            audio = r.listen(source)
            with open("microphone-results.flac", "wb") as f:
                f.write(audio.get_flac_data())
                f.close()

        try:
            # recognize speech using Whisper
            value = model_whisper.transcribe("microphone-results.flac", task='translate')
            self.output = "You said \"{}\"".format(value)
            return value

        except sr.UnknownValueError:
            self.output = ("Oops! Didn't catch that")

        except sr.RequestError as e:
            self.output = ("Uh oh! Couldn't request results from Google Speech Recognition service; {0}".format(e))

with m as source:
    r.adjust_for_ambient_noise(source)


class ClearApp(App):
    def build(self):
        self.MainLayout = BoxLayout(orientation='vertical')

        #Row 1, text input
        self.inputbox = BoxLayout(orientation='horizontal', size_hint=(1, 0.4))
        self.input = TextInput(hint_text='Translated input', size_hint=(1,1), disabled=True, font_size=20)
        self.inputbox.add_widget(self.input)
        self.MainLayout.add_widget(self.inputbox)

        #Row 2, record button
        self.recordbox = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        self.btnR = RecordButton(text='Record Input for Transcription', on_press=self.records, size_hint=(1,0.7))
        self.lang = TextInput(hint_text='Detected Language: es', size_hint=(1, 0.3), disabled=True, font_size=12, background_color='10B3CD')
        self.lang.text = 'Detected Language: es'
        self.recordbox.add_widget(self.lang)
        self.recordbox.add_widget(self.btnR)
        self.MainLayout.add_widget(self.recordbox)

        #Row 3, text output
        self.outputbox = BoxLayout(orientation='horizontal', size_hint=(1, 0.4))
        self.output = TextInput(hint_text='Translated output', size_hint=(1,1), disabled=True, font_size=20)
        self.outputbox.add_widget(self.output)
        self.MainLayout.add_widget(self.outputbox)

        #Bottom row, text input and one button
        self.box = BoxLayout(orientation='horizontal', size_hint=(1, 0.2))
        self.buttonbox = BoxLayout(orientation='vertical', size_hint=(.2,1))
        self.txt = TextInput(hint_text='Write here', size_hint=(.8,1), disabled=False)
        self.btnT = Button(text='Translate', on_press=self.english2output, size_hint=(1, .5))
        self.box.add_widget(self.txt)
        self.box.add_widget(self.buttonbox)
        self.buttonbox.add_widget(self.btnT)
        self.MainLayout.add_widget(self.box)

        return self.MainLayout

    def clearText(self, instance):
        self.txt.text = ''

    def records(self, instance):
        val = RecordButton.record(instance)
        print(val)
        self.lang.text = 'Detected Language: ' + str(val['language'])
        self.input.text = val['text']

    def english2output(self, instance):
        input_text = self.txt.text
        lang = self.lang.text[19:]
        tokenizer.tgt_lang = lang
        encoded_text = tokenizer(input_text, return_tensors="pt")
        generated_tokens = model.generate(**encoded_text)
        results = tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)
        print(results)
        self.output.text = results[0]

#model = whisper.load_model("tiny")
ClearApp().run()