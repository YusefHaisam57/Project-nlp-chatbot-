import streamlit as st
from services import extract_text_from_pdf, generate_mcq
from services_summary import summarize_text
from true_false_generator import generate_true_false

st.set_page_config(page_title="📘 PDF AI Assistant", layout="wide")
st.title("📘 PDF AI Assistant (Questions, Summary & Self-Test)")

# --- Session State Init ---
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "num_questions" not in st.session_state:
    st.session_state.num_questions = 5
if "num_pages" not in st.session_state:
    st.session_state.num_pages = 1
if "total_pages" not in st.session_state:
    st.session_state.total_pages = 1
if "qa_history" not in st.session_state:
    st.session_state.qa_history = []
if "quiz_text" not in st.session_state:
    st.session_state.quiz_text = ""

# --- Sidebar (History) ---
st.sidebar.title("📜 History")
for i, q in enumerate(st.session_state.qa_history[::-1]):
    with st.sidebar.expander(f"Interaction {len(st.session_state.qa_history) - i}"):
        st.markdown(q)

# --- Upload PDF ---
st.markdown("### 📥 Upload PDF and Configure")
col1, col2 = st.columns(2)

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
        st.success("✅ PDF uploaded and text extracted.")

with col2:
    st.session_state.num_questions = st.number_input(
        "📝 Number of Questions",
        min_value=1,
        max_value=50,
        value=5
    )

# --- Generate Buttons ---
st.markdown("### ✨ Choose Action")
action = st.radio("Select Task", ["-- Select --", "Generate MCQ", "Generate True/False", "Summarize Text"])

if st.button("🚀 Generate"):
    if not st.session_state.pdf_text:
        st.error("⚠️ Please upload a PDF first.")
    else:
        if action == "Generate MCQ":
            result = generate_mcq(st.session_state.pdf_text[:1500], st.session_state.num_questions)
            st.session_state.quiz_text = result
            st.session_state.qa_history.append("### MCQ Generated\n" + result)

        elif action == "Generate True/False":
            result = generate_true_false(st.session_state.pdf_text[:1500], st.session_state.num_questions)
            st.session_state.quiz_text = result
            st.session_state.qa_history.append("### True/False Generated\n" + result)

        elif action == "Summarize Text":
            result = summarize_text(st.session_state.pdf_text[:1500], num_sentences=5)
            st.session_state.qa_history.append("### Summary\n" + result)
            st.markdown(result)
            st.download_button("💾 Download Summary", data=result.encode("utf-8"), file_name="summary.txt")

        if action in ["Generate MCQ", "Generate True/False"]:
            st.markdown("### ✅ Questions Generated")
            st.markdown(result)
            st.download_button("💾 Download Questions", data=result.encode("utf-8"), file_name="questions.txt")

# --- Self Test Section ---
st.markdown("---")
st.markdown("### 🧠 Test Yourself")

quiz_text = st.session_state.quiz_text
if quiz_text:
    questions_blocks = quiz_text.strip().split("\n\n")
    for idx, block in enumerate(questions_blocks):
        lines = block.strip().split("\n")
        if not lines or "Answer:" not in lines[-1]:
            continue

        answer_line = lines[-1].strip()
        correct_answer = answer_line.replace("Answer:", "").strip()
        question_text = "\n".join(lines[:-1])

        with st.expander(f"Q{idx+1}: {lines[0]}"):
            if len(lines) > 2 and lines[1].startswith("a)"):
                options = [l[3:] for l in lines[1:-1]]
                labels = [l[:2] for l in lines[1:-1]]
                user_choice = st.radio("اختر الإجابة:", options, key=question_text)
                selected_label = labels[options.index(user_choice)]

                if st.button("تحقق", key=question_text + "_btn"):
                    if selected_label in correct_answer:
                        st.success("✅ إجابة صحيحة!")
                    else:
                        st.error(f"❌ إجابة خاطئة. الإجابة الصحيحة: {correct_answer}")
            else:
                user_choice = st.radio("اختر:", ["True", "False"], key=question_text)
                if st.button("تحقق", key=question_text + "_btn"):
                    if user_choice.lower() in correct_answer.lower():
                        st.success("✅ إجابة صحيحة!")
                    else:
                        st.error(f"❌ إجابة خاطئة. الإجابة الصحيحة: {correct_answer}")

# --- End Session ---
st.markdown("---")
if st.button("❌ End Session"):
    st.session_state.clear()
    st.experimental_rerun()
