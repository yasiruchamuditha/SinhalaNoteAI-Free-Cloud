# SinhalaNote AI — Free Cloud v0.4

**A shareable Sinhala lecture transcriber and study-note creator using Streamlit Community Cloud + Google Gemini API.** Users only need a browser. Nobody needs to install Whisper, Ollama or an AI model.

> **Free-to-start, not unlimited:** The Streamlit Community Cloud hosting tier is free and Gemini `gemini-3.8-flash` currently has a free API tier for eligible projects. Quotas and availability are controlled by Google/Streamlit and can change. To avoid unexpected costs, use a Gemini API project on the **free tier without paid billing enabled** and verify its current limits in Google AI Studio.

## Features

- Shared website: visitors can open the Streamlit app URL from a phone or laptop.
- Upload MP3, WAV, M4A, AAC, OGG, FLAC or WebM (application limit 25 MiB), or record from a browser microphone.
- Convert Sinhala speech (including mixed English technical terms) into editable Sinhala text using Gemini cloud AI.
- Paste or load example text to test without recording.
- Generate structured study notes in Sinhala, bilingual Sinhala/English, or English.
- Download transcript `.txt`, notes `.md`, combined `.docx`, or printable `.html` which can be saved as PDF.
- Optional **shared classroom passcode**. This is basic demo access control, **not user accounts**.
- Best-effort in-process limit: 10 calls/hour, 40 calls/day shared across app visitors, which resets after server restart and is **not** a security guarantee.
- No permanent database or persistent recording storage in our app. Download notes before leaving.

## DEPLOY: no local installation needed

### Step 1 — Create the GitHub repository

1. Open https://github.com and sign in.
2. Click **+ → New repository**. Name it `SinhalaNoteAI-Free-Cloud`.
3. Choose **Public** for easiest visibility; **Private** is also supported by Streamlit for eligible accounts. Choose **Add a README file** if Github requires an initial commit, then create the repository.
4. Double-click the downloaded ZIP to extract it. In the repository on GitHub, click **Add file → Upload files**.
5. Upload these **unpacked individual files** into the repository root:
   - `app.py`
   - `core.py`
   - `requirements.txt`
   - `README.md` (optional to replace the GitHub-generated README)
   - `.gitignore` (optional)
6. Commit the changes. Don't upload your Gemini key or any `secrets.toml` file.

**Optional style configuration:** The `.streamlit/config.toml` file in the ZIP provides upload limits and styling. Because `.streamlit` can be hidden in Finder, in GitHub choose **Add file → Create new file**, enter the filename `.streamlit/config.toml`, and paste the contents from the ZIP file, then commit. **It is optional**: the app works without it, because our code enforces a 25 MiB limit.

### Step 2 — Create a free-tier Gemini key

1. Go to https://aistudio.google.com/apikey and sign in with Google.
2. Create/select a project whose **Gemini API usage tier is Free** (check https://aistudio.google.com/usage or the Projects/Rate limits screens).
3. Choose **Create API key**; copy it privately. Never paste it into your source files, screenshots, or chats.
4. Check current availability of `gemini-3.8-flash` under **Models** and **Rate limits** in AI Studio. Your region/account eligibility is determined by Google.
5. **Do not enable paid API billing** if your requirement is strictly zero cost. The app itself does not purchase anything, but enabling paid billing at the provider can change your charges.

### Step 3 — Deploy to Streamlit Community Cloud

1. Visit https://share.streamlit.io , sign in via GitHub and authorize access to your new repository.
2. Click **Create app** → **Yup, I have an app** (label may vary).
3. Choose your GitHub repository, branch `main`, and **Main file path** `app.py`.
4. Open **Advanced settings**, select Python `3.12` if asked, and paste this into **Secrets**:

   ```toml
   GEMINI_API_KEY = "YOUR_REAL_GEMINI_API_KEY"
   GEMINI_MODEL = "gemini-3.8-flash"
   APP_PASSCODE = "a-long-classroom-code"
   ```

   Replace only the placeholder values. `APP_PASSCODE` is optional: delete that line to allow anyone with the link to use the app. Because a public link shares your Gemini quota, **keeping a passcode is safer for early testing**. Do not accidentally enter the sample placeholders unchanged.

5. Click **Save**, then **Deploy**. Streamlit installs the Python dependencies on its cloud server automatically. **There is no Python installation step for you or your visitors.**
6. Your app receives a link similar to `https://your-app-name.streamlit.app` (your actual link may differ). Share the **real URL** after deployment.

Official deployment instructions: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
Secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management

### Step 4 — First test

1. Open the newly deployed app and enter the classroom passcode if set.
2. Check the cloud-processing permission box.
3. Go to **Paste transcript → Load sample**. The sample is Sinhala with English technical words.
4. Click **Generate study notes**. This makes one cloud API request.
5. Inspect your Sinhala notes; download the Word document.
6. For PDF: download **Printable page (.html)**, open that file in a browser, then **Print → Save as PDF**. Sinhala fonts available on the viewer's device affect PDF appearance.
7. Test a short, clear 30–60 second Sinhala recording (and consent to sharing the material). Click Transcribe then correct mistakes and generate notes.
8. Share the website URL with 2–5 friends first. Watch API usage and errors before opening it to a larger group.

### Step 5 — Update the app later (including from v0.3)

If you already have the previous `SinhalaNoteAI-Cloud-Share-v0.3` GitHub project:

1. In your existing GitHub repository, **replace** `app.py`, `core.py` and `requirements.txt` with the v0.4 files in this ZIP (commit the changes).
2. Optionally update the README and `.streamlit/config.toml` as well.
3. Keep the existing Streamlit **Secrets**; confirm `GEMINI_MODEL = "gemini-3.8-flash"` and a valid `GEMINI_API_KEY`.
4. Streamlit will rebuild/redeploy on GitHub updates. Re-open the existing website link and test with **Load sample**.
5. **Do not copy Flask/Whisper/Ollama files** from the MacBook-only v0.1/v0.2 versions; they are not needed in this cloud project.

## File map

```text
app.py                    Streamlit UI
core.py                   Gemini audio/notes, input checks, exports, request limiter
requirements.txt          Python dependencies installed by Streamlit Cloud
README.md                 This deployment guide
secrets.example.toml      EXAMPLE ONLY (never real secrets)
.gitignore                Prevents local secret files from being committed
.streamlit/config.toml    Optional theme and upload setting
tests/test_core.py        Mocked unit tests; no real Gemini calls
```

## Zero-cost boundaries and privacy

- No monthly app-hosting fee is necessary for an eligible Streamlit Community Cloud app; this is subject to platform resource and account limits.
- Gemini free-tier limits (requests/minute, tokens/minute, requests/day) vary by project and model. A request to transcribe and a request to generate notes each consume quota.
- Our basic limiter is shared across users but is **per server process and resets on restart**, and is not robust enough for a large public launch. It is not a substitute for verified API provider limits, sign-ins, or abuse protection.
- With an unbilled Gemini free-tier project, requests should fail when free quota is exhausted; do not switch to a billed project unless you are prepared for charges.
- Uploaded audio and transcript text are sent to Google for processing. Google's **free-tier content can be used to improve its products**; do not upload sensitive, secret or restricted recordings. Get permission to record/share class material.
- Temporary audio files are removed from the Streamlit server. Files uploaded to Gemini are deleted using the Files API on a best-effort basis after the request; data processing/retention is governed by Google's policies.
- Visitor data is only kept in Streamlit session memory, which may be cleared by app restart or session end. No permanent library, accounts or recovery of lost notes.
- A passcode does not provide account-level privacy or isolate users from each other; this prototype uses session state, not a production authentication system.
- AI transcription may make mistakes in Sinhala dialects, poor audio, or technical terminology; verify content before studying.

## Troubleshooting

| Problem | Fix |
|---|---|
| Missing API key | Streamlit dashboard → App settings → Secrets → add `GEMINI_API_KEY` and save. Never commit real keys to GitHub. |
| App doesn't start | Make sure `app.py`, `core.py`, `requirements.txt` are at repository root. Check app logs. |
| `404` model not found | Check model list and available Gemini API models in AI Studio. Use an available model that supports **audio input** and **free-tier usage**; change `GEMINI_MODEL` in Secrets. |
| `429` quota exhausted | Your Gemini project hit a per-minute/day/token limit. Check https://aistudio.google.com/usage and rate limits. Wait for quota reset or reduce usage; do **not** enable paid billing to satisfy a zero-cost requirement. |
| Audio too large | Our application restricts files to 25 MiB. Compress audio to MP3 or split lecture. |
| Mic doesn't work | Use the `https://` Streamlit URL, grant browser microphone permissions, or upload an existing audio file instead. |
| Sinhala PDF looks wrong | Install/use a Sinhala-supporting system font or create PDF from the Word export on a system with Sinhala fonts. The HTML export intentionally uses no bundled fonts. |
| Need permanent lecture storage | This zero-setup demo has none; add a cloud database with access control later. |

## Optional: code testing by developers only

You do **not** need these commands to deploy via GitHub + Streamlit.

```bash
python -m pip install -r requirements.txt pytest
python -m pytest -q
streamlit run app.py
```

For local tests with the actual Gemini service, set a local `GEMINI_API_KEY` environment variable; **never commit it**.

## Sources checked October 2026

- Gemini audio: https://ai.google.dev/gemini-api/docs/generate-content/audio
- Gemini free pricing: https://ai.google.dev/gemini-api/docs/pricing
- Gemini rate limits: https://ai.google.dev/gemini-api/docs/rate-limits
- Streamlit deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
