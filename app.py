"""
CCISO Certification Testing Engine
A Streamlit-based application for CCISO exam preparation
"""

import streamlit as st
import re
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional

# Domain names mapping
DOMAIN_NAMES = {
    1: "Governance, Risk, and Compliance",
    2: "Information Security Controls and Audit Management",
    3: "Security Program Management and Operations",
    4: "Information Security Core Competencies",
    5: "Strategic Planning, Finance, Procurement, and Vendor Management"
}

# Practice exam distribution (rounded up)
EXAM_DISTRIBUTION = {
    1: 32,  # 21%
    2: 30,  # 20%
    3: 32,  # 21%
    4: 29,  # 19%
    5: 29   # 19%
}

TOTAL_EXAM_QUESTIONS = 152
PASSING_PERCENTAGE = 80
PASSING_SCORE = 122  # 80% of 152
EXAM_DURATION_MINUTES = 150


def parse_questions(content: str) -> List[Dict]:
    """Parse the uploaded text file into question objects."""
    questions = []

    # Split by question delimiter
    question_blocks = re.split(r'----Question\s+(\d+)', content)

    # Process each question block
    i = 1
    while i < len(question_blocks):
        try:
            question_id = int(question_blocks[i])
            block = question_blocks[i + 1] if i + 1 < len(question_blocks) else ""

            # Extract domain
            domain_match = re.search(r'Domain:\s*(.+?)(?:\n|$)', block)
            if not domain_match:
                i += 2
                continue

            domain_text = domain_match.group(1).strip()

            # Extract domain number
            domain_num_match = re.search(r'Domain\s*(\d+)', domain_text)
            domain_number = int(domain_num_match.group(1)) if domain_num_match else 0

            # Extract question text
            question_match = re.search(r'Question text:\s*(.+?)(?=\nOptions:|\Z)', block, re.DOTALL)
            question_text = question_match.group(1).strip() if question_match else ""

            # Extract options
            options_match = re.search(r'Options:\s*(.+?)(?=\nExcerpt from source:|\Z)', block, re.DOTALL)
            options_text = options_match.group(1).strip() if options_match else ""

            # Parse individual options
            options = []
            option_pattern = r'([A-D])\.\s*(.+?)(?=\n[A-D]\.|$)'
            option_matches = re.findall(option_pattern, options_text, re.DOTALL)

            for letter, text in option_matches:
                text = text.strip()
                is_correct = '[CORRECT]' in text
                clean_text = text.replace('[CORRECT]', '').strip()
                options.append({
                    'letter': letter,
                    'text': clean_text,
                    'isCorrect': is_correct
                })

            # Extract excerpt
            excerpt_match = re.search(r'Excerpt from source:\s*(.+?)(?=\n----Question|\Z)', block, re.DOTALL)
            excerpt = excerpt_match.group(1).strip() if excerpt_match else ""

            # Only add if we have valid data
            if question_text and options:
                questions.append({
                    'id': question_id,
                    'domain': domain_text,
                    'domainNumber': domain_number,
                    'questionText': question_text,
                    'options': options,
                    'excerpt': excerpt
                })

            i += 2
        except Exception as e:
            i += 2
            continue

    return questions


def initialize_session_state():
    """Initialize all session state variables."""
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'mode' not in st.session_state:
        st.session_state.mode = 'main'
    if 'exam_questions' not in st.session_state:
        st.session_state.exam_questions = []
    if 'current_question_index' not in st.session_state:
        st.session_state.current_question_index = 0
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = {}
    if 'exam_start_time' not in st.session_state:
        st.session_state.exam_start_time = None
    if 'exam_end_time' not in st.session_state:
        st.session_state.exam_end_time = None
    if 'show_results' not in st.session_state:
        st.session_state.show_results = False
    if 'show_review' not in st.session_state:
        st.session_state.show_review = False
    if 'study_domain' not in st.session_state:
        st.session_state.study_domain = 1
    if 'study_num_questions' not in st.session_state:
        st.session_state.study_num_questions = 10
    if 'show_feedback' not in st.session_state:
        st.session_state.show_feedback = False
    if 'current_answer_correct' not in st.session_state:
        st.session_state.current_answer_correct = None
    if 'file_uploaded' not in st.session_state:
        st.session_state.file_uploaded = False
    if 'show_exit_confirm' not in st.session_state:
        st.session_state.show_exit_confirm = False


def get_questions_by_domain(questions: List[Dict], domain: int) -> List[Dict]:
    """Get all questions for a specific domain."""
    return [q for q in questions if q['domainNumber'] == domain]


def select_exam_questions(questions: List[Dict]) -> List[Dict]:
    """Select questions for practice exam based on domain distribution."""
    selected = []

    for domain, count in EXAM_DISTRIBUTION.items():
        domain_questions = get_questions_by_domain(questions, domain)
        if len(domain_questions) >= count:
            selected.extend(random.sample(domain_questions, count))
        else:
            # If not enough questions, use all available
            selected.extend(domain_questions)
            # Fill remaining with random questions from other domains
            remaining = count - len(domain_questions)
            other_questions = [q for q in questions if q['domainNumber'] != domain]
            if other_questions:
                selected.extend(random.sample(other_questions, min(remaining, len(other_questions))))

    random.shuffle(selected)
    return selected


def calculate_score(exam_questions: List[Dict], user_answers: Dict) -> tuple:
    """Calculate the exam score."""
    correct = 0
    total = len(exam_questions)

    for i, question in enumerate(exam_questions):
        user_answer = user_answers.get(i)
        if user_answer:
            correct_option = next((opt for opt in question['options'] if opt['isCorrect']), None)
            if correct_option and user_answer == correct_option['letter']:
                correct += 1

    percentage = (correct / total * 100) if total > 0 else 0
    passed = percentage >= PASSING_PERCENTAGE

    return correct, total, percentage, passed


def format_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def get_remaining_time() -> int:
    """Get remaining exam time in seconds."""
    if st.session_state.exam_end_time:
        remaining = (st.session_state.exam_end_time - datetime.now()).total_seconds()
        return max(0, int(remaining))
    return 0


def render_main_menu():
    """Render the main menu interface."""
    st.title("CCISO Certification Testing Engine")

    # File uploader
    uploaded_file = st.file_uploader(
        "Upload Question Repository",
        type=['txt'],
        help="Upload a .txt file containing CCISO practice questions"
    )

    if uploaded_file is not None:
        try:
            content = uploaded_file.read().decode('utf-8')
            questions = parse_questions(content)

            if not questions:
                st.error("No valid questions found in the uploaded file. Please check the file format.")
                return

            st.session_state.questions = questions
            st.session_state.file_uploaded = True
            st.success(f"Successfully loaded {len(questions)} questions!")

            # Show domain breakdown
            domain_counts = {}
            for q in questions:
                d = q['domainNumber']
                domain_counts[d] = domain_counts.get(d, 0) + 1

            with st.expander("Question Distribution by Domain"):
                for domain in sorted(domain_counts.keys()):
                    st.write(f"Domain {domain}: {domain_counts[domain]} questions")

        except Exception as e:
            st.error(f"Error parsing file: {str(e)}")
            return

    # Show mode selection buttons if questions are loaded
    if st.session_state.file_uploaded and st.session_state.questions:
        st.markdown("---")
        st.subheader("Select Mode")

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("Practice Exam", use_container_width=True, type="primary"):
                start_practice_exam()

        with col2:
            if st.button("Study Mode", use_container_width=True, type="primary"):
                st.session_state.mode = 'study_setup'
                st.rerun()

        with col3:
            if st.button("Exit", use_container_width=True):
                st.session_state.clear()
                st.rerun()


def start_practice_exam():
    """Initialize and start a practice exam."""
    st.session_state.exam_questions = select_exam_questions(st.session_state.questions)
    st.session_state.current_question_index = 0
    st.session_state.user_answers = {}
    st.session_state.exam_start_time = datetime.now()
    st.session_state.exam_end_time = datetime.now() + timedelta(minutes=EXAM_DURATION_MINUTES)
    st.session_state.show_results = False
    st.session_state.show_review = False
    st.session_state.show_exit_confirm = False
    st.session_state.mode = 'practice_exam'
    st.rerun()


def render_practice_exam():
    """Render the practice exam interface."""
    # Check if time has expired
    remaining_time = get_remaining_time()

    if remaining_time <= 0:
        st.session_state.show_results = True
        st.rerun()
        return

    # Timer display
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("Practice Exam")
    with col2:
        if remaining_time < 600:  # Less than 10 minutes
            st.markdown(f"### ⚠️ Time: {format_time(remaining_time)}")
            st.warning("Less than 10 minutes remaining!")
        else:
            st.markdown(f"### ⏱️ Time: {format_time(remaining_time)}")

    # Auto-refresh for timer
    time.sleep(0.1)  # Small delay to prevent excessive CPU usage

    # Progress
    current_idx = st.session_state.current_question_index
    total = len(st.session_state.exam_questions)
    st.progress((current_idx + 1) / total)
    st.write(f"**Question {current_idx + 1} of {total}**")

    # Current question
    question = st.session_state.exam_questions[current_idx]

    st.markdown("---")
    st.markdown(f"**{question['questionText']}**")

    # Answer options
    options = [f"{opt['letter']}. {opt['text']}" for opt in question['options']]

    # Get previous answer if exists
    previous_answer = st.session_state.user_answers.get(current_idx)
    default_index = None
    if previous_answer:
        for i, opt in enumerate(question['options']):
            if opt['letter'] == previous_answer:
                default_index = i
                break

    selected = st.radio(
        "Select your answer:",
        options,
        index=default_index,
        key=f"practice_q_{current_idx}",
        horizontal=False
    )

    # Extract selected letter
    selected_letter = selected[0] if selected else None

    # Navigation buttons
    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if current_idx > 0:
            if st.button("← Previous"):
                if selected_letter:
                    st.session_state.user_answers[current_idx] = selected_letter
                st.session_state.current_question_index -= 1
                st.rerun()

    with col2:
        submit_disabled = selected_letter is None
        if st.button("Submit Answer", disabled=submit_disabled, type="primary"):
            st.session_state.user_answers[current_idx] = selected_letter

            # Check if this was the last question
            if current_idx == total - 1:
                st.session_state.show_results = True
            else:
                st.session_state.current_question_index += 1
            st.rerun()

    with col3:
        if current_idx < total - 1:
            if st.button("Next →"):
                if selected_letter:
                    st.session_state.user_answers[current_idx] = selected_letter
                st.session_state.current_question_index += 1
                st.rerun()

    # Finish exam button
    st.markdown("---")
    if st.button("Finish Exam", type="secondary"):
        if selected_letter:
            st.session_state.user_answers[current_idx] = selected_letter
        st.session_state.show_results = True
        st.rerun()

    # Force rerun to update timer
    st.rerun()


def render_results():
    """Render the results screen."""
    st.title("Exam Results")

    correct, total, percentage, passed = calculate_score(
        st.session_state.exam_questions,
        st.session_state.user_answers
    )

    # Score display
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Score", f"{correct}/{total}")
        st.metric("Percentage", f"{percentage:.1f}%")

    with col2:
        if passed:
            st.success("# ✅ PASSED")
            st.balloons()
        else:
            st.error("# ❌ FAILED")

        st.write(f"Passing score: {PASSING_PERCENTAGE}% ({PASSING_SCORE} correct)")

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Review Answers", use_container_width=True, type="primary"):
            st.session_state.show_review = True
            st.rerun()

    with col2:
        if st.button("Return to Main Menu", use_container_width=True):
            st.session_state.mode = 'main'
            st.session_state.show_results = False
            st.session_state.show_review = False
            st.rerun()


def render_review():
    """Render the answer review screen."""
    st.title("Answer Review")

    correct, total, percentage, passed = calculate_score(
        st.session_state.exam_questions,
        st.session_state.user_answers
    )

    st.write(f"**Final Score: {correct}/{total} ({percentage:.1f}%)**")
    st.markdown("---")

    for i, question in enumerate(st.session_state.exam_questions):
        user_answer = st.session_state.user_answers.get(i)
        correct_option = next((opt for opt in question['options'] if opt['isCorrect']), None)
        is_correct = user_answer == correct_option['letter'] if correct_option and user_answer else False

        # Question header with status
        if is_correct:
            st.markdown(f"### ✅ Question {i + 1}")
        else:
            st.markdown(f"### ❌ Question {i + 1}")

        st.write(f"**{question['questionText']}**")

        # Display options with highlighting
        for opt in question['options']:
            letter = opt['letter']
            text = opt['text']

            if opt['isCorrect'] and letter == user_answer:
                # User selected correct answer
                st.markdown(f"**{letter}. {text}** ✅ (Your answer - Correct)")
            elif opt['isCorrect']:
                # Correct answer user didn't select
                st.success(f"**{letter}. {text}** ← Correct answer")
            elif letter == user_answer:
                # User's incorrect answer
                st.error(f"**{letter}. {text}** ← Your answer")
            else:
                st.write(f"{letter}. {text}")

        # Metadata
        with st.expander("Show Details"):
            st.write(f"**Domain:** {question['domain']}")
            if question['excerpt']:
                st.write(f"**Excerpt:** {question['excerpt']}")

        st.markdown("---")

    # Return button
    if st.button("Return to Main Menu", use_container_width=True, type="primary"):
        st.session_state.mode = 'main'
        st.session_state.show_results = False
        st.session_state.show_review = False
        st.rerun()


def render_study_setup():
    """Render the study mode setup screen."""
    st.title("Study Mode Setup")

    # Domain selection
    domain_options = [f"Domain {i}: {DOMAIN_NAMES[i]}" for i in range(1, 6)]
    selected_domain = st.selectbox(
        "Select Domain",
        domain_options,
        index=st.session_state.study_domain - 1
    )

    # Extract domain number
    domain_number = int(selected_domain.split(":")[0].replace("Domain ", ""))
    st.session_state.study_domain = domain_number

    # Get available questions for domain
    domain_questions = get_questions_by_domain(st.session_state.questions, domain_number)
    max_questions = len(domain_questions)

    if max_questions == 0:
        st.warning(f"No questions available for Domain {domain_number}")
        if st.button("Return to Main Menu"):
            st.session_state.mode = 'main'
            st.rerun()
        return

    st.write(f"Available questions: {max_questions}")

    # Number of questions
    col1, col2 = st.columns([3, 1])

    with col1:
        num_questions = st.number_input(
            "Number of questions",
            min_value=1,
            max_value=max_questions,
            value=min(st.session_state.study_num_questions, max_questions)
        )
        st.session_state.study_num_questions = num_questions

    with col2:
        st.write("")  # Spacing
        st.write("")
        if st.button("All Questions"):
            st.session_state.study_num_questions = max_questions
            st.rerun()

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Start Study Session", use_container_width=True, type="primary"):
            # Select random questions from domain
            selected = random.sample(domain_questions, st.session_state.study_num_questions)
            st.session_state.exam_questions = selected
            st.session_state.current_question_index = 0
            st.session_state.user_answers = {}
            st.session_state.show_feedback = False
            st.session_state.current_answer_correct = None
            st.session_state.show_exit_confirm = False
            st.session_state.mode = 'study'
            st.rerun()

    with col2:
        if st.button("Return to Main Menu", use_container_width=True):
            st.session_state.mode = 'main'
            st.rerun()


def render_study_mode():
    """Render the study mode interface."""
    st.title("Study Mode")

    current_idx = st.session_state.current_question_index
    total = len(st.session_state.exam_questions)

    # Progress
    st.progress((current_idx + 1) / total)
    st.write(f"**Question {current_idx + 1} of {total}**")

    # Current question
    question = st.session_state.exam_questions[current_idx]

    st.markdown("---")
    st.markdown(f"**{question['questionText']}**")

    # Answer options
    options = [f"{opt['letter']}. {opt['text']}" for opt in question['options']]

    # Check if showing feedback
    if st.session_state.show_feedback:
        # Display the question with feedback
        user_answer = st.session_state.user_answers.get(current_idx)
        correct_option = next((opt for opt in question['options'] if opt['isCorrect']), None)

        # Show answer feedback
        if st.session_state.current_answer_correct:
            st.success("✅ Correct!")
        else:
            st.error("❌ Incorrect")

            # Show correct answer
            if correct_option:
                st.info(f"Correct answer: **{correct_option['letter']}. {correct_option['text']}**")

            # Show metadata for incorrect answers
            st.markdown("**Question Details:**")
            st.write(f"**Domain:** {question['domain']}")
            if question['excerpt']:
                st.write(f"**Excerpt from source:** {question['excerpt']}")

        # Display all options with highlighting
        st.markdown("---")
        for opt in question['options']:
            letter = opt['letter']
            text = opt['text']

            if opt['isCorrect']:
                st.success(f"**{letter}. {text}** ✅")
            elif letter == user_answer and not opt['isCorrect']:
                st.error(f"**{letter}. {text}** (Your answer)")
            else:
                st.write(f"{letter}. {text}")

        st.markdown("---")

        # Next question or finish
        if current_idx < total - 1:
            if st.button("Next Question →", type="primary"):
                st.session_state.current_question_index += 1
                st.session_state.show_feedback = False
                st.session_state.current_answer_correct = None
                st.rerun()
        else:
            if st.button("View Results", type="primary"):
                st.session_state.show_results = True
                st.rerun()
    else:
        # Show answer selection
        selected = st.radio(
            "Select your answer:",
            options,
            index=None,
            key=f"study_q_{current_idx}",
            horizontal=False
        )

        selected_letter = selected[0] if selected else None

        # Submit button
        if st.button("Submit Answer", disabled=selected_letter is None, type="primary"):
            st.session_state.user_answers[current_idx] = selected_letter

            # Check if correct
            correct_option = next((opt for opt in question['options'] if opt['isCorrect']), None)
            is_correct = selected_letter == correct_option['letter'] if correct_option else False

            st.session_state.current_answer_correct = is_correct
            st.session_state.show_feedback = True
            st.rerun()

    # Return to main menu (with warning)
    st.markdown("---")

    if not st.session_state.show_exit_confirm:
        if st.button("Return to Main Menu"):
            st.session_state.show_exit_confirm = True
            st.rerun()
    else:
        st.warning("Are you sure? Your progress will be lost.")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Exit", key="confirm_exit"):
                st.session_state.mode = 'main'
                st.session_state.show_feedback = False
                st.session_state.show_exit_confirm = False
                st.rerun()
        with col2:
            if st.button("No, Continue", key="cancel_exit"):
                st.session_state.show_exit_confirm = False
                st.rerun()


def render_study_results():
    """Render study mode results."""
    st.title("Study Session Results")

    correct, total, percentage, passed = calculate_score(
        st.session_state.exam_questions,
        st.session_state.user_answers
    )

    # Score display
    st.markdown("---")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Score", f"{correct}/{total}")
        st.metric("Percentage", f"{percentage:.1f}%")

    with col2:
        if passed:
            st.success("# ✅ PASSED")
        else:
            st.error("# ❌ FAILED")

        st.write(f"Passing score: {PASSING_PERCENTAGE}%")

    st.markdown("---")

    # Action buttons
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Review Answers", use_container_width=True, type="primary"):
            st.session_state.show_review = True
            st.rerun()

    with col2:
        if st.button("Return to Main Menu", use_container_width=True):
            st.session_state.mode = 'main'
            st.session_state.show_results = False
            st.session_state.show_review = False
            st.session_state.show_feedback = False
            st.rerun()


def main():
    """Main application entry point."""
    st.set_page_config(
        page_title="CCISO Testing Engine",
        page_icon="📚",
        layout="wide"
    )

    # Custom CSS for better styling
    st.markdown("""
        <style>
        .stButton > button {
            height: 50px;
            font-size: 16px;
        }
        .stRadio > label {
            font-size: 16px;
        }
        div[data-testid="stMetricValue"] {
            font-size: 36px;
        }
        /* Force radio buttons to display vertically */
        div[data-testid="stRadio"] > div {
            flex-direction: column !important;
        }
        div[data-testid="stRadio"] > div > label {
            margin-bottom: 8px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    initialize_session_state()

    # Route to appropriate view
    if st.session_state.mode == 'main':
        render_main_menu()
    elif st.session_state.mode == 'practice_exam':
        if st.session_state.show_review:
            render_review()
        elif st.session_state.show_results:
            render_results()
        else:
            render_practice_exam()
    elif st.session_state.mode == 'study_setup':
        render_study_setup()
    elif st.session_state.mode == 'study':
        if st.session_state.show_review:
            render_review()
        elif st.session_state.show_results:
            render_study_results()
        else:
            render_study_mode()


if __name__ == "__main__":
    main()
