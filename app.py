"""SinhalaNote AI — shareable, free-tier cloud Streamlit app."""
from __future__ import annotations

import hmac
import os

import streamlit as st

from core import (
    AUDIO_TYPES, DEFAULT_MODEL, MAX_AUDIO_BYTES, MAX_TRANSCRIPT_CHARS,
    UsageLimiter, UserFacingError, clean_title, generate_notes,
    printable_html, to_docx, transcribe_audio,
)

st.set_page_config(page_title="SinhalaNote AI", page_icon="📚", layout="wide")


def setting(name: str, default: str = "") -> str:
    value = os.environ.get(name)
    if value:
        return value
    try:
        return str(st.secrets.get(name, default) or default)
    except Exception:
        return default


@st.cache_resource
def shared_limiter():
    return UsageLimiter(per_hour=10, per_day=40)


def allowed_to_call() -> bool:
    ok, reason = shared_limiter().reserve()
    if not ok:
        st.warning(reason)
    return ok


def display_failure(exc: Exception) -> None:
    if isinstance(exc, UserFacingError):
        st.warning(str(exc))
        return
    # Avoid exposing API key / provider details in exceptions to visitors.
    message = str(exc).lower()
    if "429" in message or "resource_exhausted" in message or "quota" in message:
        st.error("Free Gemini quota exhausted or too many requests. Check AI Studio usage and try later.")
    elif "404" in message or "not found" in message:
        st.error("Configured Gemini model is unavailable. Ask the owner to review GEMINI_MODEL in Secrets.")
    elif "400" in message or "401" in message or "403" in message:
        st.error("Gemini rejected the request. Ask the owner to check the API key, model and project access.")
    else:
        st.error("Cloud AI request failed. Try a short, supported audio recording or ask the owner to check deployment logs.")


st.title("📚 SinhalaNote AI")
st.caption("Sinhala lecture transcription & study notes · Web browser only · Free-tier prototype")

key = setting("GEMINI_API_KEY")
model = setting("GEMINI_MODEL", DEFAULT_MODEL)
passcode = setting("APP_PASSCODE")

if passcode and not st.session_state.get("authenticated", False):
    with st.form("classroom_login"):
        entered = st.text_input("Classroom access code", type="password")
        submitted = st.form_submit_button("Open SinhalaNote AI")
    if submitted:
        if hmac.compare_digest(entered, passcode):
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Invalid access code.")
    st.info("This app is shared by invitation. Contact its owner for the code.")
    st.stop()

if not key or key == "PASTE_YOUR_GEMINI_API_KEY":
    st.error("Owner setup required: add GEMINI_API_KEY in Streamlit App settings → Secrets.")
    st.stop()

for state_name in ("transcript", "notes"):
    if state_name not in st.session_state:
        st.session_state[state_name] = ""

with st.sidebar:
    st.header("Lecture settings")
    title = st.text_input("Lecture title", "Sinhala lecture", max_chars=120)
    subject = st.text_input("Subject", "General", max_chars=120)
    language = st.selectbox("Note language", ["Sinhala", "Bilingual", "English"])
    st.divider()
    st.caption("No user account or permanent storage in this prototype. Download before closing the tab.")
    st.caption("The owner pays no subscription within the providers' free-tier quotas; public sharing still needs usage controls.")
    if st.button("Clear transcript and notes"):
        st.session_state["transcript"] = ""
        st.session_state["notes"] = ""
        st.rerun()

st.info(
    "Audio and transcript text are sent to Google Gemini. Free-tier content may be used to improve "
    "Google's products. Do not upload sensitive or confidential lectures."
)
consent = st.checkbox("I have permission to process this recording and agree to cloud AI processing.")

left, right = st.columns([1, 1.1], gap="large")
with left:
    st.subheader("1. Record or upload")
    upload_tab, record_tab, paste_tab = st.tabs(["Upload", "Record", "Paste transcript"])
    with upload_tab:
        uploaded = st.file_uploader(
            "Upload a Sinhala lecture",
            type=[extension[1:] for extension in AUDIO_TYPES],
            help="MP3 / WAV / M4A / AAC / OGG / FLAC / WebM",
        )
        if uploaded:
            st.audio(uploaded)
            st.caption(f"File size: {len(uploaded.getvalue()) / (1024*1024):.1f} MiB")
        upload_btn = st.button("Transcribe uploaded audio", type="primary", disabled=not consent or uploaded is None)
    with record_tab:
        recorded = st.audio_input("Record a short lecture segment (stop to transcribe)", sample_rate=16000)
        record_btn = st.button("Transcribe recorded audio", type="primary", disabled=not consent or recorded is None)
    with paste_tab:
        sample_text = "අද අපි දත්ත සමුදාය ගැන ඉගෙන ගනිමු. Database එකක තොරතුරු tables වල ගබඩා කරනවා. Primary key මගින් එක් row එකක් වෙනම හඳුනාගන්න පුළුවන්."
        pasted = st.text_area("Paste Sinhala text or try the example", placeholder=sample_text, height=110)
        a, b = st.columns(2)
        with a:
            paste_btn = st.button("Use pasted text", disabled=not bool(pasted.strip()))
        with b:
            example_btn = st.button("Load sample")

    if paste_btn or example_btn:
        st.session_state["transcript"] = (sample_text if example_btn else pasted).strip()[:MAX_TRANSCRIPT_CHARS]
        st.session_state["notes"] = ""
        st.success("Transcript is ready. Review before generating notes.")

    selected_audio = uploaded if upload_btn else (recorded if record_btn else None)
    if selected_audio is not None and consent and allowed_to_call():
        try:
            with st.spinner("Transcribing audio using Gemini (cloud)…"):
                result = transcribe_audio(
                    key, selected_audio.getvalue(),
                    getattr(selected_audio, "name", "recording.wav"), model=model,
                )
            st.session_state["transcript"] = result[:MAX_TRANSCRIPT_CHARS]
            st.session_state["notes"] = ""
            st.success("Transcription complete. Please correct errors before generating notes.")
        except Exception as exc:
            display_failure(exc)

    st.subheader("2. Correct transcript")
    st.text_area("Editable Sinhala / English transcript", key="transcript", height=315, max_chars=MAX_TRANSCRIPT_CHARS)
    transcript_text = st.session_state["transcript"].strip()
    if transcript_text:
        st.download_button(
            "Download transcript (.txt)", transcript_text.encode("utf-8"),
            file_name="sinhalanote_transcript.txt", mime="text/plain",
        )

with right:
    st.subheader("3. Generate notes")
    st.caption("Structured summaries, headings, concepts and revision questions using your corrected transcript.")
    ready = consent and len(st.session_state["transcript"].strip()) >= 20
    if st.button("✨ Generate study notes", type="primary", use_container_width=True, disabled=not ready):
        if allowed_to_call():
            try:
                with st.spinner("Generating Sinhala study notes using Gemini (cloud)…"):
                    generated = generate_notes(
                        key, st.session_state["transcript"], title, subject,
                        language=language, model=model,
                    )
                st.session_state["notes"] = generated
                st.success("Notes ready. Check facts and technical spellings.")
            except Exception as exc:
                display_failure(exc)

    if st.session_state["notes"].strip():
        st.markdown(st.session_state["notes"])
        with st.expander("Edit notes"):
            st.text_area("Notes (Markdown)", key="notes", height=300)
        notes_text = st.session_state["notes"]
        st.download_button(
            "Download notes (.md)", notes_text.encode("utf-8"),
            file_name="sinhalanote_notes.md", mime="text/markdown",
        )
        st.download_button(
            "Download Word (.docx)",
            to_docx(clean_title(title), subject, st.session_state["transcript"], notes_text),
            file_name="SinhalaNoteAI_Lecture.docx",
            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        )
        st.download_button(
            "Download printable page (.html) → Save as PDF",
            printable_html(title, subject, st.session_state["transcript"], notes_text),
            file_name="SinhalaNoteAI_Print.html", mime="text/html",
        )
        st.caption("For PDF: open the downloaded HTML file in a browser → Print → Save as PDF.")
    else:
        st.write("Your AI study notes will appear here after you load a transcript and click Generate.")

st.divider()
st.caption(
    f"Free-tier demo · Up to {MAX_AUDIO_BYTES // (1024*1024)} MiB per audio file · "
    "No persistent notes database · AI processing requires an available Gemini quota. "
    "Uploaded audio is deleted from Gemini Files API on a best-effort basis after use."
)
