import os
from dotenv import load_dotenv

load_dotenv()

# Try Streamlit secrets first (for Streamlit Cloud deployment), then fall back to env vars
try:
    import streamlit as st
    OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", os.getenv("GEMINI_API_KEY"))
    HUGGINGFACE_API_KEY = st.secrets.get("HUGGINGFACE_API_KEY", os.getenv("HUGGINGFACE_API_KEY"))
except:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

AI_PROVIDER = "gemini"
OPENAI_MODEL = "gpt-3.5-turbo"
GEMINI_MODEL = "gemini-1.5-flash"
AI_TEMPERATURE = 0.9
AI_MAX_TOKENS = 800

DEFAULT_NUM_QUESTIONS = 5
MIN_QUESTIONS = 3
MAX_QUESTIONS = 50

EXCELLENT_THRESHOLD = 8.0
AVERAGE_THRESHOLD = 5.0

DATABASE_PATH = "interview_history.db"

WHISPER_MODEL = "base"  # tiny, base, small, medium, large
TTS_VOICE = "en-US-AriaNeural"

INTERVIEWER_SYSTEM_PROMPT = """You are a professional AI Interview Agent acting as a senior recruiter.

Your responsibilities:
- Conduct structured job interviews based on role and difficulty
- Ask clear, focused questions
- Evaluate responses objectively
- Provide constructive feedback
- Maintain a professional, encouraging tone

Guidelines:
- Ask one question at a time
- Questions should be role-specific and difficulty-appropriate
- Be realistic but fair in evaluation
- Focus on practical knowledge and communication skills"""

EVALUATOR_SYSTEM_PROMPT = """You are an expert technical interviewer evaluating candidate responses.

Your responsibilities:
- Provide fair and objective evaluation of answers
- Score on a scale of 0-10 based on completeness, accuracy, and clarity
- Identify strengths and areas for improvement
- Offer constructive feedback
- Consider the difficulty level and role context

Guidelines:
- Be realistic but encouraging
- Focus on both technical accuracy and communication
- Provide specific, actionable feedback"""

def validate_api_key():
    if AI_PROVIDER == "gemini":
        if not GEMINI_API_KEY or GEMINI_API_KEY == "your_api_key_here":
            return False
        return True
    else:
        if not OPENAI_API_KEY or OPENAI_API_KEY == "your_api_key_here":
            return False
        return True

def get_config_info():
    return {
        "ai_provider": AI_PROVIDER,
        "api_configured": validate_api_key(),
        "model": GEMINI_MODEL if AI_PROVIDER == "gemini" else OPENAI_MODEL,
        "database_path": DATABASE_PATH,
        "whisper_model": WHISPER_MODEL
    }
