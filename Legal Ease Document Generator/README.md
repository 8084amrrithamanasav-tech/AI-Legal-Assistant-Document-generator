# LegalEase

LegalEase is an AI-assisted legal document drafting workspace. It combines a FastAPI backend, Google Gemini generation, and a Streamlit editor with TXT, DOCX, and PDF downloads.

> **Important:** LegalEase is a drafting aid, not a law firm or a substitute for legal advice. Generated documents may be inaccurate or incomplete. Have a qualified lawyer review a draft for your facts and jurisdiction before signing or relying on it. Do not submit sensitive or confidential information unless you have reviewed the data handling terms of the configured AI provider.

## Requirements

- Python 3.10 or newer
- VS Code with the Microsoft Python extension (recommended)
- A Google AI Studio API key for AI generation; health checks, formatting, exports, and tests work without one

## Setup in VS Code on Windows

1. Open this project folder in VS Code.
2. Open **Terminal > New Terminal** and create a virtual environment:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

3. Create the local environment file and add your key:

   ```powershell
   Copy-Item .env.example .env
   ```

   Edit `.env` and set `GEMINI_API_KEY` to your Google AI Studio key. The default model is `gemini-2.5-flash`; set `GEMINI_MODEL` to another model enabled for your API key if needed. `.env` is excluded from Git.

  If PowerShell blocks activation, open a new terminal and invoke the environment's Python directly as `& ".\.venv\Scripts\python.exe"` for the commands below.

## Run the application

Run the backend and frontend in two separate VS Code terminals, from the project root. Activate `.venv` in each terminal, or use the full path to its Python executable.

**Terminal 1: FastAPI backend**

```powershell
python -m uvicorn legal_ease.main:app --reload
```

The API health check is at `http://127.0.0.1:8000/health`; interactive API documentation is at `http://127.0.0.1:8000/docs`.

**Terminal 2: Streamlit frontend**

```powershell
python -m streamlit run frontend/app.py
```

Open the local URL printed by Streamlit, normally `http://localhost:8501`. Fill in document type, parties, terms, and effective date, generate a draft, edit it in the preview, and download the current edited text as TXT, DOCX, or PDF.

You can also use **Run and Debug > LegalEase (API + UI)** in VS Code to start both configured debug sessions.

## Test

With the virtual environment active:

```powershell
python -m pytest -q
```

The tests use a local fake generator for the API contract and do not call Gemini or require a real API key.

## API

`POST /generate` accepts JSON with these string fields:

```json
{
  "document_type": "Freelance Services Agreement",
  "parties": "Jane Doe (Provider); Northstar Studio (Client)",
  "terms": "Payment within 30 days; confidentiality; delivery by June 15",
  "effective_date": "October 10, 2026"
}
```

The response contains `document` and a legal-review `disclaimer`. Requests with missing or blank values are rejected with `422`. If the key is missing, generation returns `503`; provider failures return `502`. The UI creates exports locally from the editable draft, so edits are retained in every downloaded format.

## Project layout

```text
legal_ease/
  api.py                 FastAPI routes and health check
  config.py              Environment configuration
  main.py                ASGI entry point
  schemas.py             Request and response validation
  services/
    documents.py         DOCX and PDF generation
    gemini.py            Gemini prompt and generation service
frontend/
  app.py                 Streamlit authoring and export UI
tests/
  test_api.py
  test_documents.py
.vscode/
  launch.json
  settings.json
  tasks.json
.env.example
requirements.txt
```
