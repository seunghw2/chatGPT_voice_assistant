# 음성으로 대화하는 chatGPT

# 배경

학교에서 멀티미디어 프로그래밍 과목을 수강하며, ASR(automatic speech recognition, 음성 인식)과 TTS(Text to Speech, 음성 합성)에 대해서 배웠다. 

굉장히 어려워보일 것 같은 기술이지만, 파이썬에서 speeck_recognition와 gtts 패키지를 import하면 바로 작동하는 것에 무척 놀랐다.

이 기술들을 사용하여 다른 응용 프로그램을 만들고 싶었고, chatGPT API를 무료로 사용할 수 있다는 이야기를 듣고 진행해보았다.

# 프로젝트 시나리오

타겟 사용자 : 멀티미디어 프로그래밍 수업을 듣는 건국대학교 학생

1. 사용자가 한국어로 질문 내용을 말함
2. 한국어를 영어로 번역함
3. chatGPT에게 영어로 질문함
4. chatGPT는 '멀티미디어 프로그래밍 수업을 강의하는 교수'의 관점에서 답변을 해줌
5. 영어 답변을 한글로 번역함
6. 한글 답변 내용을 읽어줌

*한국어에서 영어로 번역한 후 chatGPT에게 영어로 질문을 하는 이유는, chatGPT에게 영어로 질문을 하면 더욱 높은 수준의 답변을 제공받을 수 있기 때문이다.

# 코드 구성

### 라이브러리

```python
import speech_recognition as sr
from gtts import gTTS
import soundfile as sf
from scipy import signal
import playsound
import urllib.request
import json
import openai
```

### **ASR**

수강생은 자신의 질문 내용을 정리한 뒤, 15초라는 제한적인 시간동안 질문 내용을 말할 수 있다.

```python
# ASR
r = sr.Recognizer()

with sr.Microphone() as source:
    print("Speak something")
    audio = r.record(source, duration=15)

ask_ko = r.recognize_google(audio, language="ko-KR")
print("<질문 한글 내용>\n", ask_ko)
```

### **PAPAGO (ko → en)**

인식된 한글 질문 내용이 파파고 API를 통해 영어로 번역된다.

```python
#PAPAGO
client_id = "나의 아이디"
client_secret = "나의 시크릿"
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
```

### **chatGPT**

chatGPT API를 이용하여 질문 내용을 전달하고 영어로 된 답변을 얻는다. 이 때 chatGPT의 어시스턴트는 멀티미디어 프로그래밍 강의를 진행하는 교수이며, 답변을 영어 150단어 이내로 설명해준다는 조건을 추가했다.

```python
#CHATGPT
openai.api_key = "내 API Key" # API Key
completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    max_tokens = 500,
    temperature = 0,
    messages=[{"role": "system", "content": "assistant is a professor who lecture on a multimedia programming class and explain in 150 words"},
              {"role": "user", "content": ask_en}]
)
ans_en = completion["choices"][0]["message"]["content"]
print("<대답 영어 내용>\n", ans_en)
```

### **PAPAGO (en → ko)**

chatGPT에게 전달받은 영어 답변을 파파고를 이용해 한글로 번역한다.

```python
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
```

### **TTS**

한글로 된 답변을 음성으로 재생한다.

```python
#TTS

tts = gTTS(text=ans_ko, lang='ko')
tts.save('voice.wav')
d, fs = sf.read('voice.wav')
ds = signal.resample(d, int(len(d)*16/24))
sf.write('voice.wav', ds, 16000)

playsound.playsound('voice.wav')
```

# **구현**

![Untitled](https://s3-us-west-2.amazonaws.com/secure.notion-static.com/2d499859-86f2-4f54-8ab7-c74e5173b91c/Untitled.png)

### **<질문** **한글** **내용>**

음성 인식에서 끝점 추출에 대해 자세히 설명해 주세요

### **<질문** **영어** **번역>**

Describe the extraction of endpoints from speech recognition in detail

### **<대답** **영어** **내용>**

Speech recognition is the process of converting spoken words into text. The extraction of endpoints from speech recognition refers to the identification of the beginning and end of a spoken word or phrase. This is an important step in speech recognition because it allows the system to accurately transcribe the spoken words.

The extraction of endpoints is typically done using a technique called endpoint detection. This involves analyzing the audio signal to identify changes in the energy level or frequency content of the signal. When a person begins speaking, there is typically a sudden increase in energy level and a change in frequency content. Similarly, when a person stops speaking, there is a sudden decrease in energy level and a change in frequency content.

Endpoint detection algorithms use these changes in energy level and frequency content to identify the beginning and end of a spoken word or phrase. There are several different algorithms that can be used for endpoint detection, including threshold-based algorithms, energy-based algorithms, and spectral-based algorithms.

Once the endpoints have been identified, the speech recognition system can use this information to accurately transcribe the spoken words. This is typically done using a combination of acoustic modeling and language modeling techniques. Acoustic modeling involves analyzing the audio signal to identify the phonemes (individual speech sounds) that are being spoken. Language modeling involves using statistical techniques to predict the most likely sequence of words based on the identified phonemes.

### **<대답** **한글** **번역>**

음성 인식은 구어를 텍스트로 변환하는 과정이다. 음성 인식으로부터 엔드포인트를 추출하는 것은 음성 단어 또는 구의 시작과 끝을 식별하는 것을 의미한다. 이것은 시스템이 음성 단어를 정확하게 기록할 수 있게 해주기 때문에 음성 인식의 중요한 단계이다.

엔드포인트 추출은 일반적으로 엔드포인트 탐지라는 기술을 사용하여 수행됩니다. 여기에는 오디오 신호를 분석하여 신호의 에너지 레벨 또는 주파수 내용의 변화를 식별하는 작업이 포함됩니다. 사람이 말하기 시작하면 일반적으로 에너지 레벨이 갑자기 증가하고 주파수 내용이 변경됩니다. 마찬가지로, 사람이 말을 멈추면, 에너지 레벨이 갑자기 감소하고 주파수 함량이 변화한다.

엔드포인트 탐지 알고리즘은 이러한 에너지 수준 및 주파수 내용의 변화를 사용하여 음성 단어 또는 구문의 시작과 끝을 식별합니다. 한계값 기반 알고리듬, 에너지 기반 알고리듬 및 스펙트럼 기반 알고리듬을 포함하여 엔드포인트 탐지에 사용할 수 있는 몇 가지 다른 알고리듬이 있다.

엔드포인트가 식별되면 음성 인식 시스템은 이 정보를 사용하여 음성 단어를 정확하게 기록할 수 있다. 이것은 일반적으로 음향 모델링과 언어 모델링 기술의 조합을 사용하여 수행된다. 음향 모델링은 오디오 신호를 분석하여 말하는 음소(개별 음성)를 식별하는 것을 포함한다. 언어 모델링은 식별된 음소를 기반으로 가장 가능성이 높은 단어 순서를 예측하기 위해 통계 기법을 사용하는 것을 포함한다.

# **의의**

ASR과 TTS를 이용하여 텍스트를 작성하고 읽는 과정 없이 음성만으로 chatGPT를 이용할 수 있었다. chatGPT의 답변을 얻는 과정의 시간 소요가 길어 실제 대화하는 느낌을 받기는 힘들었지만, 시각적으로 불편함을 가지고 있는 학생들에게 이전보다 더 좋은 학습 환경을 제공할 수 있을 것이라고 생각한다.

# **참고** **자료**

**chatGPT API reference**

**[https://platform.openai.com/docs/api-reference](https://platform.openai.com/docs/api-reference)**

**Papago 언어** **번역** **API**

**https://developers.naver.com/products/papago/nmt/nmt.md**

# **블로그 주소**

**TISTORY**

**[https://sseung.tistory.com/15](https://sseung.tistory.com/15)**
