# Copies your Gemini key from Hermes's .env into this folder's .env (stays on your PC).
import os, pathlib
src = pathlib.Path(os.environ["LOCALAPPDATA"]) / "hermes" / ".env"
dst = pathlib.Path(__file__).with_name(".env")
if dst.exists():
    print(".env already exists - skipped"); raise SystemExit
key = None
if src.exists():
    for line in src.read_text(encoding="utf-8", errors="ignore").splitlines():
        name, _, val = line.partition("=")
        if name.strip() in ("GEMINI_API_KEY", "GOOGLE_API_KEY") and val.strip():
            key = val.strip().strip('"').strip("'"); break
if key:
    dst.write_text(f"GEMINI_API_KEY={key}\n", encoding="utf-8")
    print("OK: key copied to .env")
else:
    print("Key not found in Hermes .env. Open .env here and add: GEMINI_API_KEY=your_key")
    dst.write_text("GEMINI_API_KEY=\n", encoding="utf-8")
