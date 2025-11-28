from typing import Optional, Dict
import os
from text_to_speech import text_to_speech
from speechtotext import transcribe_audio

def load_voice_prompt() -> str:
    return """You are a professional AI interview agent conducting job interviews.
Your role is to ask questions clearly and provide constructive feedback.
Be professional, encouraging, and supportive throughout the interview process."""

VOICE_PROMPT = load_voice_prompt()

class VoiceInterviewAgent:
    
    def __init__(self, voice: str = "en-US-AriaNeural"):
        self.voice = voice
        self.speech_rate = 150
        self.pause_duration = 0.7
    
    def generate_greeting(self, role: str, level: str, num_questions: int) -> str:
        greeting = f"""Hello! Welcome to your interview for {role} at {level} level.
I'll be conducting your interview today.

We'll cover {num_questions} questions that will assess your technical knowledge 
and problem-solving abilities. Please answer each question thoroughly, 
and feel free to take your time to think through your responses.

Are you ready to begin? Let's start with question one."""
        
        return greeting
    
    def speak_greeting(self, role: str, level: str, num_questions: int) -> Optional[str]:
        greeting_text = self.generate_greeting(role, level, num_questions)
        return self.speak_text(greeting_text)
    
    def speak_question(self, question: str, question_num: int, total_questions: int) -> Optional[str]:
        intro = f"Question {question_num} of {total_questions}."
        full_text = f"{intro}\n\n{question}\n\nPlease provide your answer when you're ready."
        
        return self.speak_text(full_text)
    
    def speak_acknowledgment(self, is_last_question: bool = False) -> Optional[str]:
        if is_last_question:
            text = "Thank you for that response. Let me evaluate your answer."
        else:
            text = "Thank you. I've recorded your response. Let's move to the next question."
        
        return self.speak_text(text)
    
    def speak_closing(self, average_score: float) -> Optional[str]:
        if average_score >= 8.0:
            closing = """That completes our interview session. 
Excellent work today! You demonstrated strong knowledge and communication skills.
Your detailed feedback and performance report are now available for review.
Thank you for your time, and best of luck with your interview preparation!"""
        elif average_score >= 6.0:
            closing = """That completes our interview session.
You showed good understanding with room for improvement in some areas.
Please review your detailed feedback to identify areas for growth.
Thank you for your time, and keep practicing!"""
        else:
            closing = """That completes our interview session.
Thank you for participating. Review your feedback carefully to identify 
areas where you can strengthen your knowledge and interview skills.
Keep practicing and studying - improvement comes with dedicated effort.
Thank you for your time."""
        
        return self.speak_text(closing)
    
    def speak_text(self, text: str) -> Optional[str]:
        try:
            audio_file = text_to_speech(text, voice=self.voice)
            return audio_file
        except Exception as e:
            print(f"TTS Error: {e}")
            return None
    
    def transcribe_answer(self, audio_file: str) -> Optional[str]:
        try:
            if not os.path.exists(audio_file):
                print(f"Audio file not found: {audio_file}")
                return None
            
            transcribed_text = transcribe_audio(audio_file)
            return transcribed_text
        except Exception as e:
            print(f"Transcription Error: {e}")
            return None
    
    def generate_transition(self, from_score: float) -> str:
        if from_score >= 8.0:
            return "Excellent answer. Let's continue with the next question."
        elif from_score >= 6.0:
            return "Good response. Moving on to the next question."
        else:
            return "Thank you for that answer. Let's proceed to the next question."
    
    def speak_feedback_summary(self, score: float, category: str) -> Optional[str]:
        feedback_text = f"You scored {score} out of 10, which is {category}."
        return self.speak_text(feedback_text)

def create_voice_agent(voice: str = "en-US-AriaNeural") -> VoiceInterviewAgent:
    return VoiceInterviewAgent(voice=voice)

def get_available_voices() -> Dict[str, str]:
    return {
        "en-US-AriaNeural": "Professional Female (Default)",
        "en-US-GuyNeural": "Professional Male",
        "en-US-JennyNeural": "Friendly Female",
        "en-US-AndrewNeural": "Warm Male",
        "en-GB-SoniaNeural": "British Female",
        "en-GB-RyanNeural": "British Male",
        "en-AU-NatashaNeural": "Australian Female",
        "en-AU-WilliamNeural": "Australian Male"
    }

def validate_audio_file(file_path: str) -> bool:
    if not os.path.exists(file_path):
        return False
    
    if os.path.getsize(file_path) == 0:
        return False
    
    valid_extensions = ['.mp3', '.wav', '.m4a', '.ogg', '.flac', '.webm']
    _, ext = os.path.splitext(file_path)
    
    return ext.lower() in valid_extensions

VOICE_TEMPLATES = {
    "greeting": """Hello! Welcome to your interview for {role} at {level} level.
I'll be conducting your interview today. We'll cover {num_questions} questions.
Please answer thoroughly and take your time. Let's begin.""",
    
    "question_intro": "Question {num} of {total}.",
    
    "acknowledgment": "Thank you for that response.",
    
    "transition": "Let's move to the next question.",
    
    "final_question": "This is our final question.",
    
    "closing_excellent": """That completes our interview. Excellent performance!
Your feedback is ready for review. Thank you and good luck!""",
    
    "closing_good": """That completes our interview. You showed good understanding.
Review your feedback for improvement areas. Thank you!""",
    
    "closing_needs_work": """That completes our interview. Please review your feedback
carefully to strengthen your skills. Keep practicing. Thank you!"""
}

def format_question_for_speech(question: str) -> str:
    formatted = question.replace('?', '?[PAUSE]')
    formatted = formatted.replace('.', '.[PAUSE]')
    
    formatted = ' '.join(formatted.split())
    
    replacements = {
        'API': 'A P I',
        'HTTP': 'H T T P',
        'SQL': 'S Q L',
        'JSON': 'J SON',
        'XML': 'X M L',
        'CSS': 'C S S',
        'HTML': 'H T M L'
    }
    
    for abbr, spoken in replacements.items():
        formatted = formatted.replace(abbr, spoken)
    
    return formatted

def estimate_speaking_time(text: str, words_per_minute: int = 150) -> float:
    word_count = len(text.split())
    time_seconds = (word_count / words_per_minute) * 60
    
    sentence_count = text.count('.') + text.count('?') + text.count('!')
    time_seconds += sentence_count * 0.5
    
    return round(time_seconds, 1)
