# Import necessary libraries
import speech_recognition as sr
from gtts import gTTS
import soundfile as sf
from scipy import signal
import playsound
import urllib.request
import json
import openai


# ASR
r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak something")
    audio = r.record(source, duration=15)

ask_ko = r.recognize_google(audio, language="ko-KR")
print("<질문 한글 내용>\n", ask_ko)

#PAPAGO
client_id = "EG21kNIbTWrepOhx4uev"
client_secret = "ztce6bGWJM"
url = "https://openapi.naver.com/v1/papago/n2mt"
request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id",client_id)
request.add_header("X-Naver-Client-Secret",client_secret)

source = 'ko'
target = 'en'

encText = urllib.parse.quote(ask_ko)
data = f'source={source}&target={target}&text=' + encText

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()

if rescode == 200:
    response_body = response.read()
    decode = json.loads(response_body.decode('utf-8'))
    ask_en = decode['message']['result']['translatedText']
    print("<질문 영어 번역>\n", ask_en)
else:
    print('Error Code:' + str(rescode))


#CHATGPT
openai.api_key = "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" # API Key
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens = 500,
    temperature = 0,
    messages=[{"role": "system", "content": "assistant is a professor who lecture on a multimedia programming class and explain in 150 words"},
              {"role": "user", "content": ask_en}]
)
ans_en = completion["choices"][0]["message"]["content"]
print("<대답 영어 내용>\n", ans_en)


#PAPAGO
source = 'en'
target = 'ko'

encText = urllib.parse.quote(ans_en)
data = f'source={source}&target={target}&text=' + encText

request = urllib.request.Request(url)
request.add_header("X-Naver-Client-Id", client_id)
request.add_header("X-Naver-Client-Secret", client_secret)

response = urllib.request.urlopen(request, data=data.encode("utf-8"))
rescode = response.getcode()

if rescode == 200:
    response_body = response.read()
    decode = json.loads(response_body.decode('utf-8'))
    ans_ko = decode['message']['result']['translatedText']
    print("<대답 한글 번역>\n", ans_ko)
else:
    print('Error Code:' + str(rescode))

#TTS

tts = gTTS(text=ans_ko, lang='ko')
tts.save('voice.wav')
d, fs = sf.read('../voice.wav')
ds = signal.resample(d, int(len(d)*16/24))
sf.write('../voice.wav', ds, 16000)

playsound.playsound('voice.wav')