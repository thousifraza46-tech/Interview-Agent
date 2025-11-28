from openai import OpenAI
import google.generativeai as genai
from typing import Dict, List, Optional
import json
import random
import config

if config.AI_PROVIDER == "gemini":
    genai.configure(api_key=config.GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel(config.GEMINI_MODEL)
else:
    client = OpenAI(api_key=config.OPENAI_API_KEY)

def generate_ai_question(role: str, level: str, question_number: int = 0, previous_performance: Optional[float] = None) -> Dict:
    question_type = "behavioral/HR" if question_number % 4 == 0 and question_number > 0 else "technical"
    
    adjusted_level = level
    if previous_performance is not None and question_number > 2:
        if previous_performance >= 8.5 and level != "Hard":
            adjusted_level = "harder than usual"
        elif previous_performance < 5.0 and level != "Easy":
            adjusted_level = "slightly easier"
    
    role_topics = {
        "Python Developer": ["data structures", "OOP concepts", "frameworks like Django/Flask", "testing", "async programming", "decorators", "generators"],
        "Data Scientist": ["machine learning algorithms", "statistical analysis", "data preprocessing", "model evaluation", "feature engineering", "Python libraries (pandas, numpy, scikit-learn)"],
        "Web Developer": ["HTML/CSS/JavaScript", "frontend frameworks (React, Vue, Angular)", "backend development", "REST APIs", "databases", "responsive design", "security"]
    }
    
    topics = role_topics.get(role, ["general programming"])
    selected_topic = random.choice(topics)
    
    prompt = f"""Generate a UNIQUE and DIVERSE {adjusted_level} level {question_type} interview question for a {role} position.

Focus area: {selected_topic}

Requirements:
- Create a FRESH, ORIGINAL multiple-choice question (4 options: A, B, C, D)
- Question should be clear, focused, and practical
- Appropriate for {level} difficulty level
- Test real-world knowledge and problem-solving
- Include 4 options with only ONE correct answer
- Include an ideal answer with detailed explanation
- Make it specific to {role} role

Format your response as JSON:
{{
    "question": "Your unique question here",
    "options": {{
        "A": "First option",
        "B": "Second option",
        "C": "Third option",
        "D": "Fourth option"
    }},
    "correct_answer": "A",
    "ideal_answer": "Detailed explanation of why this answer is correct and why others are wrong"
}}

Question #{question_number + 1} - Make this question different from typical interview questions."""

    try:
        if config.AI_PROVIDER == "gemini":
            full_prompt = f"{config.INTERVIEWER_SYSTEM_PROMPT}\n\n{prompt}"
            response = gemini_model.generate_content(full_prompt)
            content = response.text.strip()
        else:
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": config.INTERVIEWER_SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                temperature=config.AI_TEMPERATURE,
                max_tokens=config.AI_MAX_TOKENS
            )
            content = response.choices[0].message.content.strip()
        
        
        try:
            result = json.loads(content)
            return {
                "question": result.get("question", ""),
                "options": result.get("options", {}),
                "correct_answer": result.get("correct_answer", "A"),
                "ideal_answer": result.get("ideal_answer", ""),
                "source": config.AI_PROVIDER
            }
        except json.JSONDecodeError:
            lines = content.split('\n')
            question = ""
            ideal_answer = ""
            
            for line in lines:
                if '"question"' in line.lower() or 'question:' in line.lower():
                    question = line.split(':', 1)[-1].strip(' "')
                elif '"ideal_answer"' in line.lower() or 'answer:' in line.lower():
                    ideal_answer = line.split(':', 1)[-1].strip(' "')
            
            return {
                "question": question or content[:200],
                "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
                "correct_answer": "A",
                "ideal_answer": ideal_answer or "Refer to industry best practices.",
                "source": config.AI_PROVIDER
            }
    
    except Exception as e:
        print(f"Error generating AI question: {e}")
        from interview_engine import generate_question as fallback_generate
        return fallback_generate(role, level, question_number)

def evaluate_answer_with_ai(question: str, user_answer: str, ideal_answer: str, role: str, level: str) -> Dict:
    if not user_answer or len(user_answer.strip()) < 10:
        return {
            "score": 0.5,
            "category": "Poor",
            "feedback": "Your answer is too brief and lacks substance.",
            "what_was_good": "You attempted to answer.",
            "what_was_missing": "A comprehensive explanation with details and examples.",
            "how_to_improve": "Provide a detailed answer covering all aspects of the question.",
            "ideal_answer": ideal_answer,
            "source": "rule-based"
        }
    
    evaluation_prompt = f"""Evaluate this interview answer:

**Question:** {question}

**Ideal Answer:** {ideal_answer}

**Candidate's Answer:** {user_answer}

**Context:**
- Role: {role}
- Difficulty: {level}

Provide evaluation in JSON format:
{{
    "score": 8.5,
    "feedback": "Overall assessment",
    "what_was_good": "Specific strengths",
    "what_was_missing": "Key gaps",
    "how_to_improve": "Actionable suggestions"
}}

Be fair but realistic for {level} level."""

    try:
        if config.AI_PROVIDER == "gemini":
            full_prompt = f"{config.EVALUATOR_SYSTEM_PROMPT}\n\n{evaluation_prompt}"
            response = gemini_model.generate_content(full_prompt)
            content = response.text.strip()
        else:
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": config.EVALUATOR_SYSTEM_PROMPT},
                    {"role": "user", "content": evaluation_prompt}
                ],
                temperature=0.7,
                max_tokens=600
            )
            content = response.choices[0].message.content.strip()
        
        try:
            result = json.loads(content)
            score = float(result.get("score", 5.0))
            
            score = max(0.0, min(10.0, score))
            
            if score >= 8.0:
                category = "Excellent"
            elif score >= 5.0:
                category = "Average"
            else:
                category = "Poor"
            
            return {
                "score": round(score, 1),
                "category": category,
                "feedback": result.get("feedback", "Good effort."),
                "what_was_good": result.get("what_was_good", "You showed understanding."),
                "what_was_missing": result.get("what_was_missing", "More depth needed."),
                "how_to_improve": result.get("how_to_improve", "Study the ideal answer."),
                "ideal_answer": ideal_answer,
                "source": config.AI_PROVIDER
            }
        
        except json.JSONDecodeError:
            score = 6.0
            feedback_text = content
            
            if "score" in content.lower():
                for line in content.split('\n'):
                    if 'score' in line.lower():
                        try:
                            score = float(''.join(filter(str.isdigit, line.split(':')[-1]))[:2]) / 10
                        except:
                            pass
            
            return {
                "score": round(score, 1),
                "category": "Average",
                "feedback": feedback_text[:200],
                "what_was_good": "Partial understanding shown.",
                "what_was_missing": "More comprehensive coverage needed.",
                "how_to_improve": "Review the ideal answer and practice.",
                "ideal_answer": ideal_answer,
                "source": f"{config.AI_PROVIDER}-partial"
            }
    
    except Exception as e:
        print(f"Error in AI evaluation: {e}")
        from evaluation import evaluate_answer as fallback_eval
        result = fallback_eval(user_answer, ideal_answer, question)
        result["source"] = "fallback"
        return result

def generate_interview_greeting(role: str, level: str, candidate_name: str = "Candidate") -> str:
    prompt = f"""Generate a professional interview greeting for a {role} position interview at {level} level.

Address the candidate as {candidate_name}.
Keep it warm but professional (2-3 sentences)."""

    try:
        if config.AI_PROVIDER == "gemini":
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        else:
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
    except:
        return f"Welcome, {candidate_name}! I'm pleased to conduct your interview for the {role} position at {level} level. Let's begin with your questions."

def generate_final_recommendations(role: str, level: str, scores: list, weak_areas: list = []) -> str:
    avg_score = sum(scores) / len(scores) if scores else 0
    
    prompt = f"""Generate personalized improvement recommendations for a {role} candidate at {level} level.

Interview Performance:
- Average Score: {avg_score:.1f}/10
- Scores: {scores}
- Weak areas: {', '.join(weak_areas) if weak_areas else 'General improvement needed'}

Provide 3-4 specific, actionable recommendations."""

    try:
        if config.AI_PROVIDER == "gemini":
            response = gemini_model.generate_content(prompt)
            return response.text.strip()
        else:
            response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            return response.choices[0].message.content.strip()
    except:
        return "Focus on strengthening your fundamentals, practice explaining concepts clearly, and work on real-world projects."

def check_api_status() -> dict:
    try:
        if config.AI_PROVIDER == "gemini":
            test_response = gemini_model.generate_content("Say hello")
            return {
                "status": "connected",
                "provider": "Google Gemini",
                "model": config.GEMINI_MODEL
            }
        else:
            test_response = client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[{"role": "user", "content": "Say hello"}],
                max_tokens=10
            )
            return {
                "status": "connected",
                "provider": "OpenAI",
                "model": config.OPENAI_MODEL
            }
    except Exception as e:
        return {
            "status": "error",
            "provider": config.AI_PROVIDER,
            "error": str(e)
        }
