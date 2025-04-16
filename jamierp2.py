import streamlit as st
from openai import OpenAI
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import os
from playsound import playsound
import re
import random

# ✅ 숫자 표현 정리 함수들
def convert_thousands_to_dollar_format(text):
    text = re.sub(r"(\d{2,3})\s*thousand\s*dollars", lambda m: f"${int(m.group(1)) * 1000:,}", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d{1,3}),\s*(\d{3})", r"\1,\2", text)
    return text

def fix_number_spacing(text):
    text = re.sub(r"(\$\d{1,3},\d{3})(?=[a-zA-Z])", r"\1 ", text)
    text = re.sub(r"(\$\d{1,3},\d{3})(?=to)", r"\1 ", text)
    text = re.sub(r"(to)(\$\d{1,3},\d{3})", r"\1 \2", text)
    text = re.sub(r"(\d{1,3},\d{3})(?=[a-zA-Z])", r"\1 ", text)
    text = re.sub(r"(\d{1,3},\d{3})(?=to)", r"\1 ", text)
    text = re.sub(r"(to)(\d{1,3},\d{3})", r"\1 \2", text)
    return text

def ensure_final_period(text):
    return text.strip() + '.' if not text.strip().endswith(('.', '!', '?')) else text

from num2words import num2words
import re

def convert_dollar_amount_to_words(text):
    # $38,000 → thirty-eight thousand dollars
    def replace_match(match):
        number = int(match.group(1).replace(',', ''))
        return num2words(number, to='cardinal', lang='en') + ' dollars'

    return re.sub(r"\$(\d{1,3}(?:,\d{3})+)", replace_match, text)


# ✅ 상태 초기화
if "started" not in st.session_state:
    st.session_state.started = False
if "finished" not in st.session_state:
    st.session_state.finished = False
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "user_turns" not in st.session_state:
    st.session_state.user_turns = []
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False
if "first_message_played" not in st.session_state:
    st.session_state.first_message_played = False

# ✅ 슬로건과 시작 화면 (텍스트 먼저 렌더링 후 음성 출력)
if not st.session_state.started:
    st.markdown("""
    <style>
    @keyframes fadeUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .animated-word {
        color: crimson;
        font-style: italic;
        display: inline-block;
        animation: fadeUp 1s ease forwards;
    }
    .delay-1 { animation-delay: 0.2s; }
    .delay-2 { animation-delay: 0.5s; }
    .delay-3 { animation-delay: 0.8s; }
    .tagline {
        text-align: center;
        line-height: 1.8;
        font-size: 2.4em;
        font-weight: 500;
        margin-top: 3em;
    }
    .starter-text {
        font-size: 1.6em;
        color: #444;
        text-align: center;
        margin-top: 1.4em;
        font-weight: 400;
    }
    </style>

    <div class='tagline'>
        Rock 'n <span class='animated-word delay-1'>Role</span>.<br>
        Let it <span class='animated-word delay-2'>Flo</span>.<br>
        RoleFlo<span class='animated-word delay-3'>Bot™</span>.
    </div>

    <div class='starter-text'>
        Ready for a roleplay with 🤖 <strong>RoleFloBot™</strong>?
    </div>
    """, unsafe_allow_html=True)

    # 👉 간격 추가
    st.markdown("<div style='height: 1em;'></div>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.8, 2, 1])
    with col2:
        if st.button("🎬 Start Interview"):
            st.session_state.started = True
            st.rerun()

    try:
        import os

        openai_api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=openai_api_key)

        welcome_text = "Rock and Role. Let it Flow. Role Flow Bot."
        tts_path = os.path.join(os.getenv("TEMP"), "slogan.mp3")
        if os.path.exists(tts_path):
            os.remove(tts_path)
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=welcome_text
        )
        tts_response.stream_to_file(tts_path)
        playsound(tts_path)
    except Exception as e:
        st.warning(f"TTS intro failed: {e}")

    st.stop()

# ✅ 여기부터 기존 인터뷰 로직
# 👉 이 아래에 원래의 인터뷰 전체 코드 붙이면 완성!
# 예: assistant message, user input, Whisper 처리, GPT 응답, 피드백 등

# (✂️ 이후 블록은 이미 너가 작업한 인터뷰 로직이므로 복사해 붙여넣으면 됨.)
import streamlit as st
from openai import OpenAI
import sounddevice as sd
import scipy.io.wavfile as wav
import numpy as np
import tempfile
import os
from playsound import playsound
import re
import random

# 숫자 표현을 정리하는 함수
def convert_thousands_to_dollar_format(text):
    text = re.sub(r"(\d{2,3})\s*thousand\s*dollars", lambda m: f"${int(m.group(1)) * 1000:,}", text, flags=re.IGNORECASE)
    text = re.sub(r"(\d{1,3}),\s*(\d{3})", r"\1,\2", text)
    return text


def fix_number_spacing(text):
    # $38,000per → $38,000 per
    text = re.sub(r"(\$\d{1,3},\d{3})(?=[a-zA-Z])", r"\1 ", text)
    # $38,000to → $38,000 to
    text = re.sub(r"(\$\d{1,3},\d{3})(?=to)", r"\1 ", text)
    # to$39,000 → to $39,000
    text = re.sub(r"(to)(\$\d{1,3},\d{3})", r"\1 \2", text)

    # 38,000per → 38,000 per
    text = re.sub(r"(\d{1,3},\d{3})(?=[a-zA-Z])", r"\1 ", text)
    # 38,000to → 38,000 to
    text = re.sub(r"(\d{1,3},\d{3})(?=to)", r"\1 ", text)
    # to39,000 → to 39,000
    text = re.sub(r"(to)(\d{1,3},\d{3})", r"\1 \2", text)

    return text

def ensure_final_period(text):
    if not text.strip().endswith(('.', '!', '?')):
        return text.strip() + '.'
    return text

import re
from num2words import num2words

# ✅ 숫자 → 자연어 달러 표현
def convert_dollar_amount_to_words(text):
    def replace_match(match):
        number = int(match.group(1).replace(',', ''))
        return num2words(number, to='cardinal', lang='en') + " dollars"
    return re.sub(r"\$(\d{1,3}(?:,\d{3})*|\d+)", replace_match, text)


# 상태 초기화
if "started" not in st.session_state:
    st.session_state.started = False
if "finished" not in st.session_state:
    st.session_state.finished = False
if "recording" not in st.session_state:
    st.session_state.recording = False
if "audio_buffer" not in st.session_state:
    st.session_state.audio_buffer = None
if "user_turns" not in st.session_state:
    st.session_state.user_turns = []
if "review_mode" not in st.session_state:
    st.session_state.review_mode = False
if "first_message_played" not in st.session_state:
    st.session_state.first_message_played = False

if not st.session_state.started:
    st.markdown("### Ready to start a roleplay with 🤖 RoleFloBot™?")
    if st.button("🎬 Start Interview"):
        st.session_state.started = True
        st.rerun()
    st.stop()

import os

openai_api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=openai_api_key)

st.markdown("""
<div style='text-align: center;'>
    <h1 style='margin-bottom: 0;'>🤖 RoleFloBot™</h1>
    <p style='font-size: 1.1em; color: #666; margin-top: 0;'>
        Master real-world conversation skills with task-based, AI-powered roleplay.
    </p>
</div>
""", unsafe_allow_html=True)

scenario = st.selectbox("🧩 Current Scenario:", ["Hotel Job Interview"])

st.markdown("### 🎫 Your Role Card")
st.markdown("""
**Name**: Jamie Lee  
**Position Applied**: Front Desk Clerk  
**Background**:  
- You worked at *The Riverside Hotel* for 4 years.  
- You handled **reservations**, **customer service**, and occasionally **complaint resolution**.  
- You are flexible but prefer **weekday day shifts**.  
- Your expected salary is **more than $40,000**, but you're open to negotiation.  
- You want **medical insurance** and **at least 12 days of paid leave**.

✅ Try to stay in character while answering!
""")

system_prompt = '''
You are Alex Carter, the personnel manager at Grandview Hotel. You're conducting a job interview with Jamie Lee, who is applying for a front desk clerk position.

Your goal is to simulate a real job interview. The conversation must follow this exact sequence, and you must not skip or reorder the steps:

---

1️⃣ **Ask clearly about Jamie's previous work history.**

- Wait until Jamie **explicitly describes** their responsibilities related to front desk or reservation work.
- If Jamie is vague or says they have no experience, ask ONE follow-up question to check for any **similar or transferable experience** (e.g., customer-facing roles).
- If Jamie still refuses or says no, **do not proceed to the next topic**. Politely explain that the interview cannot move forward without this information and **end the interview.**

---

2️⃣ **Ask about Jamie’s flexibility with shift schedules.**

- Make sure Jamie answers clearly whether they are comfortable working **evenings, weekends, and holidays.**
- If the response is vague or resistant, ask ONE follow-up to clarify.
- If Jamie refuses, politely say the interview cannot proceed and **end the interview.**

---

3️⃣ **Ask about salary expectations.**

- Only discuss salary **after** step 1 and 2 have been completed properly.
- Jamie may request $40,000. You should respond by saying the standard offer is **$38,000**, and if Jamie has strong experience, you can offer **up to $39,000**.
- If Jamie **insists** on over $39,000, politely explain that it exceeds your limit and **end the interview.**

---

4️⃣ **Ask about benefits.**

- Ask what benefits Jamie is hoping for.
- You may offer 10 days of paid leave and basic medical insurance.
- If Jamie asks for more, you can offer **12 days of paid leave** and **comprehensive insurance**.

---

5️⃣ **Close the interview.**

- If all prior steps are complete and Jamie is satisfied, thank them politely and end the interview.
- If Jamie has final questions, answer them briefly and professionally.

---

🔒 **Important Rules:**

- Never skip ahead. **Do not mention later topics** (like salary or benefits) if earlier steps are not completed.
- Ask **one question at a time**, with no more than **2–3 short sentences**.
- If Jamie's answer is vague, ask **one follow-up question** only.
- If Jamie refuses to answer a required question, **close the interview immediately**, without continuing.
- Stay professional and polite at all times.
'''



if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": system_prompt},
        {"role": "assistant", "content": "Hello Jamie, it's nice to meet you. Can you tell me about your work history, especially any experience related to front desk or reservations?"}
    ]

# ✅ 최초 메시지 출력 및 음성 재생
if not st.session_state.first_message_played:
    intro_text = st.session_state.messages[1]["content"]
    st.markdown(f"🧔‍♂️ Alex (Manager): {intro_text}")
    try:
        tts_path = os.path.join(os.getenv("TEMP"), "bot_reply.mp3")
        if os.path.exists(tts_path):
            os.remove(tts_path)
        tts_response = client.audio.speech.create(
            model="tts-1",
            voice="onyx",
            input=intro_text
        )
        tts_response.stream_to_file(tts_path)
        playsound(tts_path)
    except Exception as e:
        st.error(f"TTS Error: {e}")
    st.session_state.first_message_played = True

# ✅ 대화 스크립트 출력 (중복 제거)
st.markdown("---")
seen = set()
for msg in st.session_state.messages[1:]:
    key = (msg["role"], msg["content"])
    if key in seen:
        continue
    seen.add(key)
    role = "🧔‍♂️ Alex (Manager):" if msg["role"] == "assistant" else "🧑‍💼 You:"
    text = fix_number_spacing(convert_thousands_to_dollar_format(msg["content"]))
    st.markdown(f"{role} {text}\n\n", unsafe_allow_html=True)  # 👈 공백 추가로 숫자 깨짐 방지


if not st.session_state.finished:
    col1, col2 = st.columns(2)
    user_input = ""

    with col1:
        if st.button("🎙️ Start Voice Input"):
            st.session_state.recording = True
            fs = 44100
            st.session_state.audio_buffer = sd.rec(int(20 * fs), samplerate=fs, channels=1, dtype='int16')
            sd.sleep(100)
            st.info("🎤 Recording... Press 'End Voice Input' to finish.")

    with col2:
        if st.button("⏹️ End Voice Input") and st.session_state.recording:
            sd.stop()
            st.session_state.recording = False
            temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".wav")
            wav.write(temp_audio.name, 44100, st.session_state.audio_buffer)

            try:
                with open(temp_audio.name, "rb") as audio_file:
                    transcript = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language="en"
                    )
                    user_input = transcript.text
                    user_input = convert_dollar_amount_to_words(user_input)
                    user_input = fix_number_spacing(convert_thousands_to_dollar_format(user_input))
                    st.session_state.user_turns.append(user_input)
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.markdown(f"<div style='color: green;'>🧑‍💼 You: {user_input}</div>", unsafe_allow_html=True)
            except Exception as e:
                st.error(f"STT Error: {e}")
            finally:
                try:
                    os.remove(temp_audio.name)
                except Exception:
                    pass

    if user_input:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=st.session_state.messages,
            temperature=0.7,
        )
        bot_reply = response.choices[0].message.content
        bot_reply = fix_number_spacing(convert_thousands_to_dollar_format(bot_reply))
        bot_reply = convert_dollar_amount_to_words(bot_reply)
        bot_reply = ensure_final_period(bot_reply)
        bot_reply = re.sub(r"[*_]", "", bot_reply)

        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        st.markdown(f"<p>🧔‍♂️ Alex (Manager): {bot_reply}</p>", unsafe_allow_html=True)

        try:
            tts_path = os.path.join(os.getenv("TEMP"), "bot_reply.mp3")
            if os.path.exists(tts_path):
                os.remove(tts_path)
            tts_response = client.audio.speech.create(
                model="tts-1",
                voice="onyx",
                input=bot_reply
            )
            tts_response.stream_to_file(tts_path)
            playsound(tts_path)
        except Exception as e:
            st.error(f"TTS Error: {e}")

    if st.button("🎯 Finish Roleplay and Review Transcript"):
        st.session_state.finished = True
        st.session_state.review_mode = True
        st.success("🎉 You've completed the roleplay session. Great job!")

if st.session_state.review_mode:
    user_sentences = st.session_state.user_turns
    if len(user_sentences) >= 1:
        feedback_samples = random.sample(user_sentences, min(3, len(user_sentences)))
        st.markdown("---")
        st.markdown("### 🧑‍🏫 Language Feedback (up to 3 sentences)")
        for i, sentence in enumerate(feedback_samples):
            revision = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a strict but supportive English teacher. "
                                   "Check for grammar, word choice, and sentence structure. "
                                   "Do not ignore issues with incorrect verb tenses, mismatched subjects, or unnatural phrasing."
                                   "Correct all grammar mistakes, especially verb forms and word order. Focus on spoken fluency, but do not excuse clearly ungrammatical verb constructions or awkward collocations."
                                   "Do not point out issues with capitalization and punctuation like using a comma, period, and question mark unless it affects meaning or clarity. "
                                   "For example, do not suggest changes like 'as' to 'As' if the sentence was spoken, not written. Do not point out 'wait' to 'Wait,'"

                    },
                    {
                        "role": "user",
                        "content": f"Evaluate this sentence: {sentence}"
                    }
                ]
            )
            suggestion = revision.choices[0].message.content.strip()
            suggestion = fix_number_spacing(suggestion)
            st.markdown(f"**{i+1}. You said:** {sentence}")
            if suggestion == "✅ This sentence is fine.":
                st.markdown(f"👉 {suggestion}")
            else:
                st.markdown(f"👉 Suggested: <span style='color:brownst'>{suggestion}</span>", unsafe_allow_html=True)
            st.markdown("---")
