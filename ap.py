import streamlit as st
from services import extract_text_from_pdf, generate_mcq
from services_summary import summarize_text
from true_false_generator import generate_true_false
import pdfplumber
import re

# --- Page Setup ---
st.set_page_config(page_title="📘 PDF AI Assistant", layout="wide")
st.title("📘 PDF AI Assistant")

# --- Session State Defaults ---
defaults = {
    "chat": [],
    "history": [],
    "pdf_text": "",
    "num_questions": 5,
    "num_pages": 1,
    "pdf_uploaded": False,
    "total_pages": 1,
    "mcq_output": "",
    "tf_output": "",
    "summary_output": ""
}
for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# --- Sidebar: Chat History ---
with st.sidebar:
    st.markdown("## 💬 Chat History")
    for sender, msg in st.session_state.chat:
        icon = "👤" if sender == "user" else "🤖"
        st.markdown(f"{icon} {msg.splitlines()[0][:50]}...")

    if st.button("🧹 Clear History"):
        st.session_state.chat = []

# --- Main Interface ---
st.markdown("### 📤 Upload PDF and Configure")

col1, col2 = st.columns(2)
with col1:
    pdf_file = st.file_uploader("📂 Upload PDF file", type="pdf")
    if pdf_file:
        try:
            with pdfplumber.open(pdf_file) as pdf:
                st.session_state.total_pages = len(pdf.pages)
        except:
            st.error("⚠️ Error reading PDF file.")

        st.session_state.num_pages = st.number_input(
            "📄 Number of pages to extract",
            min_value=1,
            max_value=st.session_state.total_pages,
            value=min(3, st.session_state.total_pages)
        )

        st.session_state.pdf_text = extract_text_from_pdf(pdf_file, st.session_state.num_pages)
        st.session_state.pdf_uploaded = True
        st.success("✅ PDF uploaded and text extracted.")

with col2:
    st.session_state.num_questions = st.number_input(
        "📝 Number of Questions",
        min_value=1,
        max_value=50,
        value=5
    )
    selected_action = st.selectbox(
        "💡 Choose Action",
        ["-- Select --", "Generate MCQ Questions", "Generate True/False Questions", "Summarize Text"]
    )

    question_mode = st.radio(
        "🧠 Select Question Mode",
        ["Generated Questions and Answers", "Test Yourself"],
        index=1
    )

# --- Run Button ---
if st.button("🚀 Run"):
    if not st.session_state.pdf_uploaded:
        st.error("⚠️ Please upload a PDF file.")
    else:
        input_text = st.session_state.pdf_text[:1500]

        st.session_state.chat.append(("user", selected_action))
        st.session_state.chat.append(("assistant", f"{selected_action} generated."))

        if selected_action == "Generate MCQ Questions":
            st.session_state.mcq_output = generate_mcq(input_text, st.session_state.num_questions)
            st.success("✅ MCQ Questions generated!")

        elif selected_action == "Generate True/False Questions":
            st.session_state.tf_output = generate_true_false(input_text, st.session_state.num_questions)
            st.success("✅ True/False Questions generated!")

        elif selected_action == "Summarize Text":
            st.session_state.summary_output = summarize_text(input_text, num_sentences=5)
            st.success("✅ Summary generated!")

# --- Quiz Viewer ---
if st.session_state.mcq_output.strip() or st.session_state.tf_output.strip():
    st.markdown("---")

    if question_mode == "Test Yourself":
        st.markdown("### 🧐 Test Yourself")
    else:
        st.markdown("### 📋 Generated Questions with Answers")

    quiz_text = st.session_state.mcq_output + "\n\n" + st.session_state.tf_output
    raw_questions = re.findall(r'(.*?Answer:\s*(True|False|[a-dA-D]))', quiz_text.strip(), re.DOTALL)

    for idx, (full_block, answer) in enumerate(raw_questions):
        correct_answer = answer.strip()
        question_only = re.sub(r'\s*Answer:\s*(True|False|[a-dA-D])', '', full_block).strip()

        with st.expander(f"Question {idx + 1}"):
            st.markdown(question_only)

            if question_mode == "Generated Questions and Answers":
                st.info(f"**Answer:** {correct_answer}")

            elif question_mode == "Test Yourself":
                # Detect MCQ
                if re.search(r'[a-d]\)', question_only):
                    options = re.findall(r'[a-d]\)\s*(.*)', question_only)
                    labels = re.findall(r'([a-d])\)', question_only)
                    user_choice = st.radio("Choose your answer:", options, key=f"quiz_{idx}")

                    if st.button("Check", key=f"btn_{idx}"):
                        selected_label = labels[options.index(user_choice)]
                        if selected_label.lower() == correct_answer.lower():
                            st.success("✅ Correct Answer!")
                        else:
                            st.error(f"❌ Incorrect. Correct answer is: {correct_answer}")
                else:
                    user_choice = st.radio("Select:", ["True", "False"], key=f"quiz_tf_{idx}")
                    if st.button("Check", key=f"btn_tf_{idx}"):
                        if user_choice.lower() == correct_answer.lower():
                            st.success("✅ Correct Answer!")
                        else:
                            st.error(f"❌ Incorrect. Correct answer is: {correct_answer}")

# --- Summarization Viewer ---
if st.session_state.summary_output.strip():
    st.markdown("---")
    st.markdown("### 📄 Text Summarization")
    st.markdown(st.session_state.summary_output)

    st.download_button(
        label="📥 Download Summary as .txt",
        data=st.session_state.summary_output.encode("utf-8"),
        file_name="summary.txt",
        mime="text/plain"
    )

# --- End Session ---
st.markdown("---")
if st.button("❌ End Session"):
    st.session_state.clear()
    st.experimental_rerun()
