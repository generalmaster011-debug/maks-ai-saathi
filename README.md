# MAKS AI સાથી (MAKS AI Saathi)

A Gujarati-speaking AI assistant for farmers and small traders. Ask in Gujarati about prices, weights, sums and everyday business, and get a clear Gujarati answer.

ગુજરાતી બોલતો AI સહાયક, નાના વેપારીઓ અને ખેડૂતો માટે.

## How it works
- **Gemini** (cloud, `gemini-3.5-flash-lite`) answers first.
- **Ollama** (`qwen2.5:3b`, offline) takes over when there is no internet or Gemini fails. Answers then start with `(ઓફલાઇન મોડ)`.
- Simple Gradio chat in the browser.

## Example
> 100 કિલો કપાસ 7200 રૂપિયે ક્વિન્ટલ વેચું તો કેટલા મળે?
>
> તમને ₹7,200 મળશે. (1 ક્વિન્ટલ = 100 કિલો)

## Run (Windows)
1. Put your Gemini API key in a `.env` file: `GEMINI_API_KEY=...` (or let `copy_key.py` copy it).
2. Double-click `Start.bat`.
3. Open http://127.0.0.1:7860

Optional `.env` settings: `GEMINI_MODEL`, `OLLAMA_MODEL`, `OLLAMA_URL`.

The key lives only in `.env`, which git ignores. Gemini prompts are sent to Google; don't type private data.

## Roadmap
- Gujarati voice input and spoken answers
- Mandi price lookups

Built for ACE Builders Hackathon by Codebenders (Nov 2026).
