# app.py

import streamlit as st
from services import extract_text_from_pdf, generate_mcq
from services_summary import summarize_text

st.set_page_config(page_title="📘 PDF AI Assistant", layout="wide")
st.title("📘 PDF AI Assistant (Questions & Summary)")

# --- Session state init ---
if "chat" not in st.session_state:
    st.session_state.chat = []
if "history" not in st.session_state:
    st.session_state.history = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 1
if "pdf_uploaded" not in st.session_state:
    st.session_state.pdf_uploaded = False
if "total_pages" not in st.session_state:
    st.session_state.total_pages = 1

# --- Main Interface ---
st.markdown("### 📥 Upload and Settings")

col1, col2 = st.columns([2, 2])

with col1:
    pdf_file = st.file_uploader("📂 Upload PDF file", type="pdf")

    if pdf_file:
        import pdfplumber
        try:
            with pdfplumber.open(pdf_file) as pdf:
                total = len(pdf.pages)
                st.session_state.total_pages = total
        except:
            st.error("⚠️ Error reading PDF.")

        st.session_state.num_pages = st.number_input(
            "📄 Number of pages to read",
            min_value=1,
            max_value=st.session_state.total_pages,
            value=min(3, st.session_state.total_pages)
        )

        st.session_state.pdf_text = extract_text_from_pdf(pdf_file, st.session_state.num_pages)
        st.session_state.pdf_uploaded = True
        st.success("✅ PDF uploaded and text extracted.")

with col2:
    st.session_state.num_questions = st.number_input(
        "📝 Number of MCQs",
        min_value=1,
        max_value=50,
        value=5
    )

    selected_action = st.selectbox("💡 What do you want to generate?", ["-- Select --", "Generate Questions", "Summarize Text"])

    if st.button("🚀 Run"):
        if not st.session_state.pdf_uploaded:
            st.error("⚠️ Please upload a PDF file first.")
        else:
            if selected_action == "Generate Questions":
                st.session_state.chat.append(("user", "Generate Questions"))
                with st.chat_message("user"):
                    st.markdown("Generate Questions")

                with st.chat_message("assistant"):
                    st.markdown("Generating questions...")

                response = generate_mcq(
                    st.session_state.pdf_text[:1500],
                    st.session_state.num_questions
                )

                st.session_state.chat.append(("assistant", response))
                st.session_state.history.append(response)

                with st.chat_message("assistant"):
                    st.markdown(response)
                    st.download_button(
                        label="💾 Download Questions as .txt",
                        data=response.encode("utf-8"),
                        file_name="mcq_questions.txt",
                        mime="text/plain"
                    )

            elif selected_action == "Summarize Text":
                st.session_state.chat.append(("user", "Summarize Text"))
                with st.chat_message("user"):
                    st.markdown("Summarize Text")

                with st.chat_message("assistant"):
                    st.markdown("Summarizing text...")

                summary = summarize_text(st.session_state.pdf_text[:1500], num_sentences=5)

                st.session_state.chat.append(("assistant", summary))
                st.session_state.history.append(summary)

                with st.chat_message("assistant"):
                    st.markdown(summary)
                    st.download_button(
                        label="💾 Download Summary as .txt",
                        data=summary.encode("utf-8"),
                        file_name="summary.txt",
                        mime="text/plain"
                    )

st.markdown("---")
for sender, msg in st.session_state.chat:
    with st.chat_message(sender):
        st.markdown(msg)

st.markdown("---")
if st.button("❌ End Session"):
    st.session_state.clear()
    st.experimental_rerun()
