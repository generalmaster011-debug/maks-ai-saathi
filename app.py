"""MAKS AI Saathi - ગુજરાતી AI સહાયક (ACE Builders Hackathon base)
Gemini (cloud, free key) + Ollama (offline backup).
"""
import os
import requests
import gradio as gr
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

SYSTEM = (
    "તમે 'MAKS AI સાથી' છો: નાના વેપારીઓ અને ખેડૂતો માટેનો મદદગાર AI. "
    "હંમેશા સરળ ગુજરાતીમાં, ટૂંકા અને સ્પષ્ટ જવાબ આપો. "
    "ખબર ન હોય તો સાચું કહો. પૈસા, દવા કે કાયદાની બાબતમાં નિષ્ણાતની સલાહ લેવાનું કહો."
)

gemini_client = None
if API_KEY:
    from google import genai
    from google.genai import types
    gemini_client = genai.Client(api_key=API_KEY)


def norm(history):
    """Gradio history -> list of (role, text); works with old and new formats."""
    out = []
    for t in history or []:
        if isinstance(t, dict):
            c = t.get("content")
            if isinstance(c, list):
                c = " ".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in c)
            out.append((t.get("role", "user"), str(c)))
        elif isinstance(t, (list, tuple)) and len(t) == 2:
            if t[0]: out.append(("user", str(t[0])))
            if t[1]: out.append(("assistant", str(t[1])))
    return out


def ask_gemini(message, history):
    contents = []
    for role, text in norm(history):
        role = "user" if role == "user" else "model"
        contents.append(types.Content(role=role, parts=[types.Part(text=text)]))
    contents.append(types.Content(role="user", parts=[types.Part(text=message)]))
    resp = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=types.GenerateContentConfig(system_instruction=SYSTEM),
    )
    return resp.text


def ask_ollama(message, history):
    msgs = [{"role": "system", "content": SYSTEM}]
    for role, text in norm(history):
        msgs.append({"role": role, "content": text})
    msgs.append({"role": "user", "content": message})
    r = requests.post(f"{OLLAMA_URL}/api/chat",
                      json={"model": OLLAMA_MODEL, "messages": msgs, "stream": False},
                      timeout=300)
    r.raise_for_status()
    return r.json()["message"]["content"]


def chat(message, history):
    if gemini_client:
        try:
            return ask_gemini(message, history)
        except Exception as e:
            print("Gemini error, using Ollama:", e)
    try:
        return "(ઓફલાઇન મોડ) " + ask_ollama(message, history)
    except Exception as e:
        return f"માફ કરશો, અત્યારે જવાબ ન મળ્યો. ભૂલ: {e}"


# ---------- Voice ----------
def transcribe(audio_path):
    """Gujarati speech -> text with Gemini (cloud)."""
    if not (gemini_client and audio_path):
        return ""
    ext = os.path.splitext(audio_path)[1].lower().lstrip(".") or "wav"
    mime = {"wav": "audio/wav", "mp3": "audio/mp3", "webm": "audio/webm",
            "ogg": "audio/ogg", "m4a": "audio/mp4", "flac": "audio/flac"}.get(ext, "audio/wav")
    with open(audio_path, "rb") as f:
        data = f.read()
    resp = gemini_client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[types.Part.from_bytes(data=data, mime_type=mime),
                  "આ ઓડિયોમાં જે બોલાયું છે તે ગુજરાતી લિપિમાં બરાબર લખો. ફક્ત લખાણ આપો, બીજું કંઈ નહીં."],
    )
    return (resp.text or "").strip()


def speak(text):
    """Gujarati text -> mp3 file (gTTS, needs internet). Returns None on failure."""
    try:
        import re, tempfile
        from gtts import gTTS
        clean = re.sub(r"[*_#`>]", "", text).replace("(ઓફલાઇન મોડ)", "").strip()
        if not clean:
            return None
        path = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
        gTTS(clean[:1500], lang="gu").save(path)
        return path
    except Exception as e:
        print("TTS error:", e)
        return None


def respond(message, history, speak_on):
    history = history or []
    reply = chat(message, history)
    history = history + [{"role": "user", "content": message},
                         {"role": "assistant", "content": reply}]
    audio = speak(reply) if speak_on else None
    return "", history, audio


def respond_voice(audio_path, history, speak_on):
    if not audio_path:
        return history, None, None
    try:
        text = transcribe(audio_path)
    except Exception as e:
        print("Transcribe error:", e)
        text = ""
    if not text:
        history = (history or []) + [{"role": "assistant",
                   "content": "માફ કરશો, અવાજ સમજાયો નહીં. ફરી બોલો અથવા લખીને પૂછો."}]
        return history, None, None
    _, history, audio = respond(text, history, speak_on)
    return history, audio, None


def make_chatbot():
    try:
        return gr.Chatbot(type="messages", height=420, label="MAKS AI સાથી")
    except TypeError:
        return gr.Chatbot(height=420, label="MAKS AI સાથી")


with gr.Blocks(title="MAKS AI સાથી") as demo:
    gr.Markdown("# MAKS AI સાથી\nગુજરાતીમાં લખીને કે બોલીને પૂછો: ભાવ, હિસાબ, ખેતી, ધંધાની સલાહ.")
    bot = make_chatbot()
    with gr.Row():
        box = gr.Textbox(placeholder="અહીં લખો અને Enter દબાવો...", show_label=False, scale=4)
        send = gr.Button("મોકલો", variant="primary", scale=1)
    mic = gr.Audio(sources=["microphone"], type="filepath", label="🎤 બોલીને પૂછો (રેકોર્ડ કરો, પછી Stop)")
    speak_on = gr.Checkbox(value=True, label="🔊 જવાબ બોલીને સંભળાવો")
    voice_out = gr.Audio(label="જવાબ (અવાજ)", autoplay=True, interactive=False)
    gr.Examples(["મારી દુકાન માટે દિવાળી ઓફરનો મેસેજ લખી આપો",
                 "100 કિલો કપાસ 7200 રૂપિયે ક્વિન્ટલ વેચું તો કેટલા મળે?"], inputs=box)

    box.submit(respond, [box, bot, speak_on], [box, bot, voice_out])
    send.click(respond, [box, bot, speak_on], [box, bot, voice_out])
    mic.stop_recording(respond_voice, [mic, bot, speak_on], [bot, voice_out, mic])

if __name__ == "__main__":
    demo.launch(inbrowser=True)
