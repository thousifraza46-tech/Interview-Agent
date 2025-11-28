"""
AI Interview Agent - Main Application
Professional Interview Simulation with Voice Support
"""
import streamlit as st
import os
from datetime import datetime
import time

from interview_engine import (
    generate_question, 
    get_interviewer_prompt,
    generate_interview_questions,
    get_total_questions
)
from evaluation import evaluate_answer, calculate_interview_summary
from speechtotext import transcribe_audio
from text_to_speech import text_to_speech
from database import (
    create_session,
    save_answer,
    complete_session,
    get_session_history,
    get_session_details,
    get_statistics,
    export_session_to_text
)

st.set_page_config(
    page_title="AI Interview Agent",
    page_icon="AI",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .score-excellent {
        color: #28a745;
        font-weight: bold;
        font-size: 2rem;
    }
    .score-average {
        color: #ffc107;
        font-weight: bold;
        font-size: 2rem;
    }
    .score-poor {
        color: #dc3545;
        font-weight: bold;
        font-size: 2rem;
    }
    .question-box {
        background-color: #e3f2fd;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .question-box h3 {
        color: #1565c0;
        margin-bottom: 0.8rem;
    }
    .question-box p {
        color: #212121;
        line-height: 1.6;
        font-weight: 500;
    }
    .feedback-box {
        background-color: #f9f9f9;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .stButton>button {
        width: 100%;
    }
    [data-testid="stSidebar"] {
        display: none;
    }
    .nav-button {
        background-color: #1f77b4;
        color: white;
        border: none;
        padding: 10px 20px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 16px;
        margin: 4px 2px;
        cursor: pointer;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

if 'interview_started' not in st.session_state:
    st.session_state.interview_started = False
if 'current_question_num' not in st.session_state:
    st.session_state.current_question_num = 0
if 'scores' not in st.session_state:
    st.session_state.scores = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = None
if 'all_qa_data' not in st.session_state:
    st.session_state.all_qa_data = []
if 'total_questions' not in st.session_state:
    st.session_state.total_questions = 5
if 'current_question' not in st.session_state:
    st.session_state.current_question = None
if 'voice_enabled' not in st.session_state:
    st.session_state.voice_enabled = True
if 'question_start_time' not in st.session_state:
    st.session_state.question_start_time = None
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'answer_submitted' not in st.session_state:
    st.session_state.answer_submitted = False
if 'current_evaluation' not in st.session_state:
    st.session_state.current_evaluation = None
if 'use_ai_questions' not in st.session_state:
    st.session_state.use_ai_questions = True
if 'session_start_time' not in st.session_state:
    st.session_state.session_start_time = None
if 'session_time_limit' not in st.session_state:
    st.session_state.session_time_limit = None
if 'timer_expired' not in st.session_state:
    st.session_state.timer_expired = False

def reset_interview():
    st.session_state.interview_started = False
    st.session_state.current_question_num = 0
    st.session_state.scores = []
    st.session_state.session_id = None
    st.session_state.all_qa_data = []
    st.session_state.current_question = None
    st.session_state.question_start_time = None
    st.session_state.answer_submitted = False
    st.session_state.current_evaluation = None
    st.session_state.session_start_time = None
    st.session_state.session_time_limit = None
    st.session_state.timer_expired = False

def start_interview(role, level, num_questions, voice_enabled, time_limit):
    st.session_state.interview_started = True
    st.session_state.current_question_num = 0
    st.session_state.scores = []
    st.session_state.all_qa_data = []
    st.session_state.total_questions = num_questions
    st.session_state.voice_enabled = voice_enabled
    st.session_state.role = role
    st.session_state.level = level
    st.session_state.question_start_time = time.time()
    st.session_state.session_start_time = time.time()
    st.session_state.session_time_limit = time_limit * 60 if time_limit > 0 else None
    st.session_state.timer_expired = False
    
    st.session_state.session_id = create_session(role, level)
    
    question_data = generate_question(role, level, 0, use_ai=st.session_state.use_ai_questions)
    st.session_state.current_question = question_data

def process_answer(user_answer, question_data):
    evaluation = evaluate_answer(
        user_answer,
        question_data['ideal_answer'],
        question_data['question'],
        question_data
    )
    
    save_answer(
        st.session_state.session_id,
        st.session_state.current_question_num + 1,
        question_data['question'],
        user_answer,
        question_data['ideal_answer'],
        evaluation
    )
    
    st.session_state.scores.append(evaluation['score'])
    st.session_state.all_qa_data.append({
        'question': question_data['question'],
        'user_answer': user_answer,
        'evaluation': evaluation
    })
    
    st.session_state.answer_submitted = True
    st.session_state.current_evaluation = evaluation
    
    return evaluation

def next_question():
    st.session_state.current_question_num += 1
    st.session_state.question_start_time = time.time()
    st.session_state.answer_submitted = False
    st.session_state.current_evaluation = None
    
    if st.session_state.current_question_num < st.session_state.total_questions:
        question_data = generate_question(
            st.session_state.role,
            st.session_state.level,
            st.session_state.current_question_num,
            use_ai=st.session_state.use_ai_questions
        )
        st.session_state.current_question = question_data
    else:
        avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
        complete_session(
            st.session_state.session_id,
            avg_score,
            st.session_state.total_questions
        )
        st.session_state.current_question = None

def previous_question():
    if st.session_state.current_question_num > 0:
        st.session_state.current_question_num -= 1
        st.session_state.question_start_time = time.time()
        question_data = generate_question(
            st.session_state.role,
            st.session_state.level,
            st.session_state.current_question_num
        )
        st.session_state.current_question = question_data

st.markdown('<div class="main-header">AI Interview Agent</div>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; font-size: 1.1rem; color: #666; margin-top: -10px;">Your Personal AI-Powered Interview Coach | Practice, Learn, Excel</p>', unsafe_allow_html=True)
st.markdown("---")

col1, col2, col3, col4 = st.columns(4)
with col1:
    if st.button("Home", use_container_width=True, type="primary" if st.session_state.page == "Home" else "secondary"):
        st.session_state.page = "Home"
        st.rerun()
with col2:
    if st.button("Interview", use_container_width=True, type="primary" if st.session_state.page == "Interview" else "secondary"):
        st.session_state.page = "Interview"
        st.rerun()
with col3:
    if st.button("History", use_container_width=True, type="primary" if st.session_state.page == "History" else "secondary"):
        st.session_state.page = "History"
        st.rerun()
with col4:
    if st.button("Statistics", use_container_width=True, type="primary" if st.session_state.page == "Statistics" else "secondary"):
        st.session_state.page = "Statistics"
        st.rerun()

st.markdown("---")

if st.session_state.page == "Home":
    st.markdown('<div class="sub-header">Your Personal Interview Coach</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
        ### Welcome to AI Interview Agent!
        
        This intelligent platform simulates realistic job interviews to help you:
        
        - **Practice** with role-specific questions  
        - **Get instant feedback** on your answers  
        - **Improve** with detailed suggestions  
        - **Track** your performance over time  
        
        Ready to ace your next interview? Let's get started!
        """)
        
        if st.button("Start Your Interview", type="primary", use_container_width=True):
            st.session_state.page = "Interview"
            st.rerun()
    
    st.markdown("---")
    st.markdown("### Key Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### Voice Support
        - Speak your answers naturally
        - Automatic speech-to-text
        - AI voice for questions
        """)
    
    with col2:
        st.markdown("""
        #### AI Evaluation
        - Semantic similarity analysis
        - Detailed scoring (0-10)
        - Constructive feedback
        """)
    
    with col3:
        st.markdown("""
        #### Progress Tracking
        - Session history
        - Performance analytics
        - Downloadable reports
        """)
    
    st.markdown("---")
    st.markdown("### Available Roles")
    
    roles_col1, roles_col2, roles_col3 = st.columns(3)
    
    with roles_col1:
        st.info("**Python Developer**\nData structures, algorithms, frameworks")
    
    with roles_col2:
        st.info("**Data Scientist**\nML, statistics, data analysis")
    
    with roles_col3:
        st.info("**Web Developer**\nHTML, CSS, JavaScript, APIs")

elif st.session_state.page == "Interview":
    if hasattr(st.session_state, 'navigate_to_interview'):
        del st.session_state.navigate_to_interview
    
    if not st.session_state.interview_started:
        st.title("Configure Your Interview")
        
        col1, col2 = st.columns(2)
        
        with col1:
            role = st.selectbox(
                "Select Job Role",
                ["Python Developer", "Data Scientist", "Web Developer"],
                help="Choose the role you want to practice for"
            )
            
            level = st.selectbox(
                "Select Difficulty Level",
                ["Easy", "Medium", "Hard"],
                help="Choose the difficulty level appropriate for your experience"
            )
        
        with col2:
            num_questions = st.slider(
                "Number of Questions",
                min_value=3,
                max_value=50,
                value=5,
                help="Select how many questions you want to answer"
            )
            
            time_limit = st.slider(
                "Session Time Limit (minutes)",
                min_value=0,
                max_value=120,
                value=30,
                step=5,
                help="Set time limit for entire interview session. Set to 0 for no time limit."
            )
            
            voice_enabled = st.checkbox(
                "Enable Voice Features",
                value=True,
                help="AI will speak questions and you can use voice input"
            )
            
            st.session_state.use_ai_questions = st.checkbox(
                "Use AI-Generated Questions",
                value=True,
                help="Generate unique questions using OpenAI/Gemini AI. Uncheck to use static question bank."
            )
        
        st.markdown("---")
        
        with st.expander("Interview Guidelines"):
            interviewer_prompt = get_interviewer_prompt(role, level)
            st.markdown(interviewer_prompt)
        
        col_start1, col_start2, col_start3 = st.columns([1, 2, 1])
        with col_start2:
            if st.button("Start Interview", type="primary", use_container_width=True):
                start_interview(role, level, num_questions, voice_enabled, time_limit)
                st.rerun()
    
    else:
        show_timer = st.session_state.session_time_limit and st.session_state.session_start_time
        
        if show_timer:
            session_elapsed = int(time.time() - st.session_state.session_start_time)
            time_remaining = st.session_state.session_time_limit - session_elapsed
            
            if time_remaining <= 0:
                if not st.session_state.timer_expired:
                    st.session_state.timer_expired = True
                    if st.session_state.scores:
                        avg_score = sum(st.session_state.scores) / len(st.session_state.scores)
                        complete_session(
                            st.session_state.session_id,
                            avg_score,
                            len(st.session_state.scores)
                        )
                
                st.warning("Time's up! Your interview session has ended.")
                st.info(f"You completed {len(st.session_state.scores)} out of {st.session_state.total_questions} questions.")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("View Results", type="primary", use_container_width=True):
                        st.session_state.page = "Statistics"
                        st.rerun()
                
                with col2:
                    if st.button("Start New Interview", use_container_width=True):
                        reset_interview()
                        st.rerun()
            else:
                mins_remaining = time_remaining // 60
                secs_remaining = time_remaining % 60
                
                timer_color = "⚫" if time_remaining < 300 else "⚫" if time_remaining < 600 else "⚫"
                st.markdown(f"### Session Time Remaining: {mins_remaining}:{secs_remaining:02d}")
                st.markdown("---")
        
        if st.session_state.current_question and not st.session_state.get('timer_expired', False):
            question_data = st.session_state.current_question
            
            progress = st.session_state.current_question_num / st.session_state.total_questions
            st.progress(progress, text=f"Question {st.session_state.current_question_num + 1} of {st.session_state.total_questions}")
            
            if st.session_state.question_start_time:
                elapsed_time = int(time.time() - st.session_state.question_start_time)
                st.markdown(f"**Time Elapsed:** {elapsed_time} seconds")
            
            st.markdown(f'<div class="question-box"><h3>Question {st.session_state.current_question_num + 1}</h3><p style="font-size:1.2rem;">{question_data["question"]}</p></div>', unsafe_allow_html=True)
            
            if st.session_state.voice_enabled:
                if st.button("Listen to Question"):
                    with st.spinner("Generating audio..."):
                        audio_file = text_to_speech(question_data['question'])
                        if audio_file and os.path.exists(audio_file):
                            st.audio(audio_file)
            
            st.markdown("### Your Answer")
            
            tab1, tab2 = st.tabs(["Type Answer", "Voice Answer"])
            
            with tab1:
                if 'options' in question_data and question_data['options']:
                    st.markdown("#### Select Your Answer")
                    selected_option = st.radio(
                        "Choose the correct option:",
                        options=list(question_data['options'].keys()),
                        format_func=lambda x: f"{x}. {question_data['options'][x]}",
                        key=f"mcq_radio_{st.session_state.current_question_num}",
                        disabled=st.session_state.answer_submitted
                    )
                    
                    with st.expander("Want to add explanation? (Optional)"):
                        user_explanation = st.text_area(
                            "Explain your reasoning (optional):",
                            height=150,
                            placeholder="Explain why you chose this option...",
                            key=f"explanation_{st.session_state.current_question_num}",
                            disabled=st.session_state.answer_submitted
                        )
                    
                    user_answer = selected_option + (f"\n\nExplanation: {user_explanation}" if user_explanation else "")
                else:
                    user_answer = st.text_area(
                        "Type your answer here:",
                        height=200,
                        placeholder="Provide a detailed answer...",
                        key=f"text_answer_{st.session_state.current_question_num}",
                        disabled=st.session_state.answer_submitted
                    )
                
                if st.button("Submit Answer", type="primary", key="submit_text", disabled=st.session_state.answer_submitted):
                    is_mcq = 'options' in question_data and question_data['options']
                    min_length = 1 if is_mcq else 10
                    
                    if user_answer and len(user_answer.strip()) >= min_length:
                        with st.spinner("Evaluating your answer..."):
                            evaluation = process_answer(user_answer, question_data)
                            st.rerun()
                    else:
                        if is_mcq:
                            st.error("Please select an option")
                        else:
                            st.error("Please provide a more detailed answer (at least 10 characters)")
                
                if st.session_state.answer_submitted and st.session_state.current_evaluation:
                    evaluation = st.session_state.current_evaluation
                    
                    st.markdown("---")
                    st.markdown("### Evaluation Results")
                    
                    if 'is_mcq_correct' in evaluation and evaluation['is_mcq_correct'] is not None:
                        if evaluation['is_mcq_correct']:
                            st.success(f"✓ Correct! The answer is {question_data['correct_answer']}")
                        else:
                            st.error(f"✗ Incorrect. The correct answer is {question_data['correct_answer']}: {question_data['options'][question_data['correct_answer']]}")
                    
                    score_class = "score-excellent" if evaluation['score'] >= 8 else "score-average" if evaluation['score'] >= 5 else "score-poor"
                    st.markdown(f'<div class="{score_class}">Score: {evaluation["score"]}/10 ({evaluation["category"]})</div>', unsafe_allow_html=True)
                    
                    col_fb1, col_fb2 = st.columns(2)
                    
                    with col_fb1:
                        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
                        st.markdown("**Overall Feedback**")
                        st.write(evaluation['feedback'])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
                        st.markdown("**Strengths**")
                        st.success(evaluation['what_was_good'])
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with col_fb2:
                        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
                        st.markdown("**Areas to Improve**")
                        st.warning(evaluation['what_was_missing'])
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        st.markdown('<div class="feedback-box">', unsafe_allow_html=True)
                        st.markdown("**Recommendations**")
                        st.info(evaluation['how_to_improve'])
                        st.markdown("</div>", unsafe_allow_html=True)
                    
                    with st.expander("View Ideal Answer"):
                        st.write(evaluation['ideal_answer'])
                    
                    st.markdown("---")
                    
                    if st.session_state.current_question_num < st.session_state.total_questions - 1:
                        if st.button("Next Question", type="primary", use_container_width=True, key="next_btn"):
                            next_question()
                            st.rerun()
                    else:
                        if st.button("Submit Interview", type="primary", use_container_width=True, key="submit_interview"):
                            next_question()
                            st.rerun()
            
            with tab2:
                st.info("Record your answer using the audio recorder")
                audio_file = st.file_uploader(
                    "Upload audio file (mp3, wav, m4a)",
                    type=['mp3', 'wav', 'm4a'],
                    key=f"audio_answer_{st.session_state.current_question_num}"
                )
                
                if audio_file:
                    temp_audio_path = f"temp_audio_{st.session_state.current_question_num}.wav"
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_file.getbuffer())
                    
                    if st.button("Transcribe & Submit", type="primary", key="submit_voice"):
                        with st.spinner("Transcribing audio..."):
                            try:
                                transcribed_text = transcribe_audio(temp_audio_path)
                                st.success("Transcription complete!")
                                st.write("**Transcribed Text:**")
                                st.write(transcribed_text)
                                
                                if len(transcribed_text.strip()) > 10:
                                    with st.spinner("Evaluating your answer..."):
                                        evaluation = process_answer(transcribed_text, question_data)
                                        
                                        st.markdown("---")
                                        st.markdown("### Evaluation Results")
                                        
                                        score_class = "score-excellent" if evaluation['score'] >= 8 else "score-average" if evaluation['score'] >= 5 else "score-poor"
                                        st.markdown(f'<div class="{score_class}">Score: {evaluation["score"]}/10 ({evaluation["category"]})</div>', unsafe_allow_html=True)
                                        
                                        col_fb1, col_fb2 = st.columns(2)
                                        
                                        with col_fb1:
                                            st.markdown("**Overall Feedback**")
                                            st.write(evaluation['feedback'])
                                            st.markdown("**Strengths**")
                                            st.success(evaluation['what_was_good'])
                                        
                                        with col_fb2:
                                            st.markdown("**Areas to Improve**")
                                            st.warning(evaluation['what_was_missing'])
                                            st.markdown("**Recommendations**")
                                            st.info(evaluation['how_to_improve'])
                                        
                                        with st.expander("View Ideal Answer"):
                                            st.write(evaluation['ideal_answer'])
                                        
                                        st.markdown("---")
                                        
                                        if st.session_state.current_question_num < st.session_state.total_questions - 1:
                                            if st.button("Next Question", type="primary", use_container_width=True, key="next_after_voice"):
                                                next_question()
                                                st.rerun()
                                        else:
                                            if st.button("Submit Interview", type="primary", use_container_width=True, key="submit_interview_voice"):
                                                next_question()
                                                st.rerun()
                                else:
                                    st.error("Transcription too short. Please provide a more detailed answer.")
                            except Exception as e:
                                st.error(f"Error transcribing audio: {str(e)}")
                            finally:
                                if os.path.exists(temp_audio_path):
                                    os.remove(temp_audio_path)
        
        else:
            st.success("Interview Completed!")
            
            st.markdown("### Final Performance Summary")
            
            summary = calculate_interview_summary(
                st.session_state.scores,
                st.session_state.role,
                st.session_state.level
            )
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Average Score", f"{summary['average_score']}/10")
            with col2:
                st.metric("Total Questions", summary['total_questions'])
            with col3:
                st.metric("Excellent Answers", summary['excellent_count'])
            with col4:
                st.metric("Performance", summary['overall_performance'])
            
            st.markdown("---")
            col_break1, col_break2 = st.columns(2)
            
            with col_break1:
                st.markdown("#### Score Distribution")
                st.write(f"Excellent (8-10): {summary['excellent_count']}")
                st.write(f"Average (5-7): {summary['average_count']}")
                st.write(f"Poor (0-4): {summary['poor_count']}")
            
            with col_break2:
                st.markdown("#### Recommendation")
                st.info(summary['recommendation'])
            
            st.markdown("---")
            st.markdown("### Detailed Question Review")
            
            for i, qa in enumerate(st.session_state.all_qa_data):
                with st.expander(f"Question {i+1} - Score: {qa['evaluation']['score']}/10"):
                    st.markdown(f"**Question:** {qa['question']}")
                    st.markdown(f"**Your Answer:** {qa['user_answer']}")
                    st.markdown(f"**Score:** {qa['evaluation']['score']}/10 ({qa['evaluation']['category']})")
                    st.markdown(f"**Feedback:** {qa['evaluation']['feedback']}")
            
            st.markdown("---")
            col_action1, col_action2, col_action3 = st.columns(3)
            
            with col_action1:
                if st.button("Download Report", use_container_width=True):
                    report_file = f"interview_report_{st.session_state.session_id}.txt"
                    export_session_to_text(st.session_state.session_id, report_file)
                    with open(report_file, 'r', encoding='utf-8') as f:
                        st.download_button(
                            "Download Text Report",
                            f.read(),
                            file_name=report_file,
                            mime="text/plain"
                        )
            
            with col_action2:
                if st.button("New Interview", use_container_width=True, key="btn_new_interview"):
                    reset_interview()
                    st.rerun()
            
            with col_action3:
                if st.button("Home", use_container_width=True, key="btn_home_end"):
                    reset_interview()
                    st.session_state.page = "Home"
                    st.rerun()

elif st.session_state.page == "History":
    st.title("Interview History")
    
    sessions = get_session_history(20)
    
    if not sessions:
        st.info("No interview history yet. Start your first interview!")
    else:
        st.markdown(f"### Recent Sessions ({len(sessions)} total)")
        
        for session in sessions:
            with st.expander(f"{session['role']} - {session['level']} | {session['start_time'][:16]} | Score: {session['average_score']}/10"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Role:** {session['role']}")
                    st.write(f"**Level:** {session['level']}")
                
                with col2:
                    st.write(f"**Date:** {session['start_time'][:16]}")
                    st.write(f"**Status:** {session['status']}")
                
                with col3:
                    st.write(f"**Score:** {session['average_score']}/10")
                    st.write(f"**Questions:** {session['total_questions']}")
                
                if st.button(f"View Details", key=f"details_{session['session_id']}"):
                    details = get_session_details(session['session_id'])
                    st.markdown("#### Detailed Answers")
                    
                    for answer in details['answers']:
                        st.markdown(f"**Q{answer['question_number']}:** {answer['question']}")
                        st.markdown(f"**Your Answer:** {answer['user_answer'][:200]}...")
                        st.markdown(f"**Score:** {answer['score']}/10 ({answer['category']})")
                        st.markdown("---")

elif st.session_state.page == "Statistics":
    st.title("Overall Statistics")
    
    stats = get_statistics()
    
    if stats['total_completed_sessions'] == 0:
        st.info("No statistics available yet. Complete some interviews to see your progress!")
    else:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Interviews", stats['total_completed_sessions'])
        with col2:
            st.metric("Overall Average", f"{stats['overall_average_score']}/10")
        with col3:
            st.metric("Trend", stats['trend'])
        
        st.markdown("---")
        st.markdown("### Performance by Role")
        
        if stats['performance_by_role']:
            for role, data in stats['performance_by_role'].items():
                col_role1, col_role2 = st.columns([2, 1])
                with col_role1:
                    st.write(f"**{role}**")
                with col_role2:
                    sessions_text = f"{data.get('session_count', data.get('sessions_count', 0))} sessions"
                    st.write(f"Avg: {data['average_score']}/10 ({sessions_text})")
        
        st.markdown("---")
        st.info("Tip: Complete more interviews to get detailed analytics and track your improvement over time!")

st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>AI Interview Agent | Built with Streamlit & AI | © 2024</p>
    <p>Practice makes perfect. Good luck with your interviews!</p>
</div>
""", unsafe_allow_html=True)
