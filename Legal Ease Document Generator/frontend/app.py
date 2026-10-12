"""Streamlit drafting workspace for LegalEase."""

import re

import requests
import streamlit as st

from legal_ease.config import get_settings
from legal_ease.services.documents import create_docx, create_pdf

st.set_page_config(page_title="LegalEase | Document Studio", page_icon="L", layout="wide")
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Source+Serif+4:wght@500;600;700&display=swap');
    :root { --ink: #202b29; --muted: #65716d; --paper: #f5f6f2; --line: #d9dfd9; --green: #286052; }
    .stApp { background: var(--paper); color: var(--ink); }
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    h1, h2, h3 { font-family: 'Source Serif 4', Georgia, serif !important; color: var(--ink); }
    .block-container { max-width: 1260px; padding-top: 2.2rem; padding-bottom: 3rem; }
    .eyebrow { color: var(--green); font-size: 0.75rem; font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
    .lede { color: var(--muted); max-width: 720px; margin-top: -0.5rem; }
    div[data-testid="stForm"] { border: 1px solid var(--line); border-radius: 6px; background: #fff; padding: 1.25rem; }
    div[data-testid="stTextArea"] textarea, div[data-testid="stTextInput"] input { border-radius: 4px; }
    div.stButton > button, div[data-testid="stFormSubmitButton"] button { border-radius: 4px; font-weight: 600; }
    .draft-note { border-left: 3px solid #a8843a; background: #f2eee3; padding: 0.8rem 1rem; color: #4c483d; font-size: 0.86rem; }
    .status-line { color: var(--muted); font-size: 0.85rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

settings = get_settings()
st.session_state.setdefault("draft", "")
st.session_state.setdefault("document_type", "")

st.markdown('<div class="eyebrow">LegalEase / Document Studio</div>', unsafe_allow_html=True)
st.title("Draft with clarity.")
st.markdown(
    '<p class="lede">Create a structured first draft from your terms, refine the wording, '
    "then export an editable copy.</p>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.subheader("Workspace status")
    try:
        health_response = requests.get(f"{settings.api_base_url}/health", timeout=2)
        health_response.raise_for_status()
        is_configured = health_response.json().get("gemini_configured", False)
        if is_configured:
            st.success("API connected · Gemini configured")
        else:
            st.warning("API connected · Gemini key missing")
    except requests.RequestException:
        st.error("API unavailable. Start the FastAPI task first.")
    st.caption("Your prompts and drafts are sent to the configured AI provider when you generate.")

input_col, draft_col = st.columns([0.92, 1.08], gap="large")
with input_col:
    st.subheader("Document details")
    with st.form("document_request"):
        document_type = st.text_input(
            "Document type",
            placeholder="For example, Freelance Services Agreement",
        )
        parties = st.text_area(
            "Parties and roles",
            placeholder="Jane Doe (Service Provider); Northstar Studio (Client)",
            height=95,
        )
        terms = st.text_area(
            "Terms and conditions",
            placeholder="Payment within 30 days; delivery by June 15; confidentiality obligations",
            height=155,
            help="Separate individual terms with semicolons or new lines.",
        )
        effective_date = st.text_input(
            "Effective date",
            placeholder="October 10, 2026",
        )
        submitted = st.form_submit_button("Generate first draft", type="primary", use_container_width=True)

    if submitted:
        payload = {
            "document_type": document_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
        }
        try:
            response = requests.post(
                f"{settings.api_base_url}/generate",
                json=payload,
                timeout=120,
            )
            if response.ok:
                st.session_state["draft"] = response.json()["document"]
                st.session_state["document_type"] = document_type.strip()
                st.success("Draft generated. Review every clause before use.")
            else:
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text
                st.error(f"Generation failed ({response.status_code}): {detail}")
        except requests.RequestException as exc:
            st.error(f"Could not reach the generation API: {exc}")

with draft_col:
    st.subheader("Review and edit")
    if st.session_state["draft"]:
        safe_name = re.sub(r"[^a-zA-Z0-9]+", "_", st.session_state["document_type"]).strip("_").lower()
        safe_name = safe_name or "legal_document"
        draft = st.text_area(
            "Editable document text",
            key="draft",
            height=440,
            label_visibility="collapsed",
        )
        st.markdown('<p class="status-line">Changes here are included in every export.</p>', unsafe_allow_html=True)
        download_cols = st.columns(3, gap="small")
        with download_cols[0]:
            st.download_button(
                "Download TXT",
                data=draft.encode("utf-8"),
                file_name=f"{safe_name}.txt",
                mime="text/plain; charset=utf-8",
                use_container_width=True,
            )
        with download_cols[1]:
            st.download_button(
                "Download DOCX",
                data=create_docx(draft, st.session_state["document_type"]),
                file_name=f"{safe_name}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with download_cols[2]:
            st.download_button(
                "Download PDF",
                data=create_pdf(draft, st.session_state["document_type"]),
                file_name=f"{safe_name}.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
    else:
        st.info("Your generated document will appear here. Add the parties, key terms, and effective date to begin.")

st.divider()
st.markdown(
    '<div class="draft-note"><strong>Important:</strong> LegalEase creates a drafting aid, not legal '
    "advice. AI-generated text may be incomplete or inaccurate. Have a qualified lawyer review the "
    "document for your facts and jurisdiction before signing or relying on it.</div>",
    unsafe_allow_html=True,
)
