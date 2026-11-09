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


demo = gr.ChatInterface(
    fn=chat,
    title="MAKS AI સાથી",
    description="ગુજરાતીમાં પૂછો: ભાવ, હિસાબ, ખેતી, ધંધાની સલાહ.",
    examples=["મારી દુકાન માટે દિવાળી ઓફરનો મેસેજ લખી આપો",
              "100 કિલો કપાસ 7200 રૂપિયે ક્વિન્ટલ વેચું તો કેટલા મળે?"],
)

if __name__ == "__main__":
    demo.launch()
