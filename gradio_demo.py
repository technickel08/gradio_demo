
import requests
import logging
import logging.handlers
logger = logging.getLogger(__name__)
import gradio as gr
import time 
from io import BytesIO
import numpy as np
from pathlib import Path
import gradio as gr
import openai
import pyttsx3
# from dotenv import load_dotenv
import os
import base64
from pydub import AudioSegment
import io
from functools import partial
from datetime import datetime
import sseclient
import json
import audioread

# def audio_stream(audio):
#     file_path = "/app/audio_input.wav"
#     url = "http://ec2-3-110-105-77.ap-south-1.compute.amazonaws.com:8501/audio2audio_stream?user_id=12345678&selected_model=gpt-3.5-turbo&context_enable=false&voice_code=en-IN&voice_gender=FEMALE&voice_name=en-IN-Standard-A&tts_lang=en"

#     payload = {}
#     files=[
#     ('audio',(file_path,open(audio,'rb'),'application/octet-stream'))
#     ]
#     headers = {
#   'accept': 'application/json'
#                 }

#     # response = requests.request("POST", url, headers=headers, data=payload, files=files,stream=True)
#     with requests.request("POST", url, headers=headers, data=payload, files=files,stream=True) as r:
#         r.raise_for_status()
#         wait = 0
#         for chunk in r.iter_content(chunk_size=1024):
#             if wait==1:
#                 time.sleep(5)
#             file_name = datetime.today()
#             file_path = "/app/out/{}.wav".format(file_name)
#             logger.info("saving audio chunk - {}.wav".format(file_name))
#             # b8 = base64.b64decode(chunk[1:])
#             # b64 = base64.b64encode(b8).decode()
#             # wav_file = open(file_path, "wb")
#             # wav_file.write(chunk[1:])
#             # wav_file.close()
#             # recording = AudioSegment.from_file(io.BytesIO(b8), format="mp3")
#             # recording.export('/app/temp_audio_2.mp3', format='mp3')
#             wait=1
#             yield file_path


def audio_stream_1(audio,lang,context,user_id,session_id):
    print("audio2audio streaming started")
    url = f"http://192.168.1.7:8555/audio2audio_stream?user_id={user_id}&session_id={session_id}&selected_model=gpt-3.5-turbo&context_enable={context}&voice_code=en-IN&voice_gender=FEMALE&voice_name=en-IN-Standard-A&tts_lang={lang}"
    print(audio,"*"*10)
    payload = {}
    files=[
    ('audio',(audio,open(audio,'rb'),'application/octet-stream'))
    ]
    headers = {
  'accept': 'application/json',
  'Authorization': "Basic ZHNfdXNlcjpkc0BiaGFyYXRwZTEyMw=="}

    response = requests.request("POST", url, headers=headers, data=payload, files=files,stream=True)
    client = sseclient.SSEClient(response)
    wait = True
    text_out = ""
    if client:
        for event in client.events():
            if event.data != '[DONE]':
                try:
                    if wait:
                        pass 
                    else:
                        with audioread.audio_open(file_path) as f:
                                totalsec = f.duration
                                time.sleep(totalsec)
                    wait = False
                except Exception as e:
                    print("Exception Occured - {}".format(str(e)))

                file_name = datetime.today()
                file_path = "/app/out/audio_out.wav"
                audio_out = eval(event.data)
                audio_base64 = base64.b64encode(audio_out).decode("utf-8")
                audio_player = f'<audio src="data:audio/mpeg;base64,{audio_base64}" controls autoplay></audio>'
                text_out = text_out+"\n"+event.event
                wav_file = open(file_path, "wb")
                wav_file.write(audio_out)
                wav_file.close()
                print(file_path,"file saved")
                # if "img src" in event.event:
                #     audio_player = None
                yield audio_player,text_out




# def add_to_stream(audio, instream):
#     time.sleep(1)
#     if audio is None:
#         return gr.update(), instream
#     if instream is None:
#         ret = audio
#     else:
#         ret = (audio[0], np.concatenate((instream[1], audio[1])))
#     return ret, ret

# with gr.Blocks() as demo:
#     inp = gr.Audio(audio_stream)
#     out = gr.Audio()
#     stream = gr.State()
#     clear = gr.Button("Clear")

#     inp.stream(add_to_stream, [inp, stream], [out, stream])
#     clear.click(lambda: [None, None, None], None, [inp, out, stream])


# if __name__ == "__main__":
#     print("Gradio App Initialised")
#     demo.launch()
#     print("Gradio App Launched")

openai.api_key =  os.getenv("OPENAI_API_KEY")

messages=[
        {"role": "system", "content": "You are a teacher"}
    ]
def transcribe(audio):
    global messages
    file = open(audio, "rb")
    transcription = openai.Audio.transcribe("whisper-1", file)
    print(transcription)
    messages.append({"role": "user", "content": transcription["text"]})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    AImessage = response["choices"][0]["message"]["content"]
    engine = pyttsx3.init()
    engine.say(AImessage)
    engine.runAndWait()
    messages.append({"role": "assistant", "content": AImessage})
    chat = ''
    for message in messages:
        if message["role"] != 'system':
            chat += message["role"] + ':' + message["content"] + "\n\n"
    return chat


# autoplay_audio = """async () => {
#         console.log('playing audio in 2 seconds')
#         let gradioEl = document.querySelector('body > gradio-app').shadowRoot;
#         setTimeout(() => {
#             let audioplayer = gradioEl.querySelector('#speaker > audio');
#             audioplayer.play();
#         }, 2000)
#         }"""
# audio_out=gr.Audio(type="numpy", elem_id="speaker")
# def dummy():
#     return True
# audio_out.change(fn= dummy,inputs=[],_js=autoplay_audio)
# chatbot = gr.Chatbot([], elem_id="chatbot").style(height=750)



html = gr.HTML()
ui = gr.Interface(fn=audio_stream_1,
                  inputs=[gr.Audio(source='microphone',type='filepath'),
                          gr.Radio(["hi","en"], label="language", info="language selector"),
                          gr.Radio([True,False], label="enable_context", info="enable_context selector"),
                          gr.Textbox(label = "enter User ID"),
                          gr.Textbox(label = "enter session ID")
                          ], 
                  outputs= [html,gr.HTML()]
                  )

# with gr.Blocks() as demo:
#     # chatbot = gr.Chatbot()
#     with gr.Row():
#         audio_message = gr.Audio(
#                 source="microphone",
#                 type="filepath"
#             )
#         audio = gr.Audio( elem_id="speaker")
#         state = gr.State()
#         agent_state = gr.State(value="")
#         autoplay_audio = """async () => {
#         console.log('playing audio in 2 seconds')
#         let gradioEl = document.querySelector('body > gradio-app').shadowRoot;
        # setTimeout(() => {
        #     let audioplayer = gradioEl.querySelector('#speaker > audio');
        #     audioplayer.play();
        # }, 2000)
#         }"""
#         # button = gr.Button()
#         audio.change(fn=audio_stream_1,
#             inputs=audio_message,
#             outputs=audio,
#             show_progress=False,_js=autoplay_audio
#         )
#         # gr.Interface(fn=audio_stream ,
#         #           inputs=gr.Audio(source='microphone',type='filepath'), 
#         #           outputs="audio"
#         #           )


# demo.queue()
# # ui.launch(server_name="0.0.0.0",share=False)
# demo.launch(server_name="0.0.0.0",share=False,debug=True)



# def transcribe(audio, state=""):
#     print(audio)
#     time.sleep(2)
#     text = "mai akshat hoon"
#     state += text + " "
#     return state, state


# with gr.Blocks() as demo:
#   state = gr.State(value="")
#   autoplay_audio = """async () => {
#     try{
#         console.log('playing audio in 2 seconds')
#         let gradioEl = document.querySelector('#speaker');
#         setTimeout(() => {
#             let audioplayer = gradioEl.querySelector('#speaker > audio');
#             audioplayer.play();
#         }, 2000)
#         }
#     catch(err) {
#     console.log("abc")
#     }
#         }"""
#   with gr.Row():
#       with gr.Column():
#         audio = gr.Audio(source="microphone", type="filepath") 
#     #   with gr.Column():
#         # textbox = gr.Textbox()
#   audio.stream(fn=audio_stream_1, inputs=[audio], outputs=[gr.Audio( elem_id="speaker")])
ui.queue()
ui.launch(debug=True,server_name="0.0.0.0",share=False)
