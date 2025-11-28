from sentence_transformers import SentenceTransformer, util
import re

model = SentenceTransformer('all-MiniLM-L6-v2')

def evaluate_answer(user_answer: str, ideal_answer: str, question: str = "", question_data: dict = None) -> dict:
    if not user_answer or len(user_answer.strip()) < 1:
        return {
            "score": 0.5,
            "category": "Poor",
            "feedback": "Your answer is too brief and lacks substance.",
            "what_was_good": "You attempted to answer the question.",
            "what_was_missing": "A comprehensive explanation with key concepts, examples, and details.",
            "how_to_improve": "Provide a detailed answer covering all aspects of the question. Include definitions, examples, and practical applications.",
            "ideal_answer": ideal_answer
        }
    
    is_mcq = question_data and 'options' in question_data and 'correct_answer' in question_data
    
    if is_mcq:
        user_choice = user_answer.strip().upper()
        correct_answer = question_data['correct_answer'].upper()
        
        if user_choice in ['A', 'B', 'C', 'D'] and len(user_choice) == 1:
            is_correct = (user_choice == correct_answer)
            
            if is_correct:
                base_score = 10.0
                feedback_text = "Correct answer! Excellent choice."
                what_was_good = f"You selected the correct option {correct_answer}."
                what_was_missing = "Consider adding an explanation to demonstrate deeper understanding."
                how_to_improve = "While you got the right answer, explaining your reasoning shows mastery of the concept."
            else:
                base_score = 2.0
                correct_option_text = question_data['options'][correct_answer]
                feedback_text = f"Incorrect. The correct answer is {correct_answer}."
                what_was_good = "You made an attempt at the question."
                what_was_missing = f"The correct answer is {correct_answer}: {correct_option_text}"
                how_to_improve = "Review the concept and understand why the correct option is appropriate."
            
            return {
                "score": base_score,
                "category": categorize_score(base_score),
                "feedback": feedback_text,
                "what_was_good": what_was_good,
                "what_was_missing": what_was_missing,
                "how_to_improve": how_to_improve,
                "ideal_answer": ideal_answer,
                "is_mcq_correct": is_correct if 'is_correct' in locals() else None
            }
    
    user_emb = model.encode(user_answer, convert_to_tensor=True)
    ideal_emb = model.encode(ideal_answer, convert_to_tensor=True)
    similarity = util.pytorch_cos_sim(user_emb, ideal_emb)
    raw_score = float(similarity)
    
    answer_length = len(user_answer.split())
    ideal_length = len(ideal_answer.split())
    
    length_ratio = answer_length / ideal_length if ideal_length > 0 else 0
    length_factor = 1.0
    if length_ratio < 0.3:
        length_factor = 0.85
    elif length_ratio > 3.0:
        length_factor = 0.95
    
    has_examples = any(phrase in user_answer.lower() for phrase in ['example', 'for instance', 'such as', 'like', 'e.g.'])
    has_structure = any(phrase in user_answer.lower() for phrase in ['first', 'second', 'finally', 'however', 'additionally'])
    
    quality_bonus = 0
    if has_examples:
        quality_bonus += 0.05
    if has_structure:
        quality_bonus += 0.05
    
    if is_mcq:
        user_choice = user_answer.strip()[0].upper() if user_answer.strip() else ""
        correct_answer = question_data['correct_answer'].upper()
        if user_choice == correct_answer:
            quality_bonus += 0.15
    
    final_score = (raw_score * length_factor) + quality_bonus
    final_score = min(10, max(0, final_score * 10))
    final_score = round(final_score, 1)
    
    category = categorize_score(final_score)
    
    feedback = generate_feedback(final_score, user_answer, ideal_answer, raw_score)
    
    result = {
        "score": final_score,
        "category": category,
        "feedback": feedback["main_feedback"],
        "what_was_good": feedback["what_was_good"],
        "what_was_missing": feedback["what_was_missing"],
        "how_to_improve": feedback["how_to_improve"],
        "ideal_answer": ideal_answer
    }
    
    if is_mcq:
        user_choice = user_answer.strip()[0].upper() if user_answer.strip() else ""
        correct_answer = question_data['correct_answer'].upper()
        result["is_mcq_correct"] = (user_choice == correct_answer)
    
    return result

def categorize_score(score: float) -> str:
    if score >= 8.0:
        return "Excellent"
    elif score >= 5.0:
        return "Average"
    else:
        return "Poor"

def generate_feedback(score: float, user_answer: str, ideal_answer: str, similarity: float) -> dict:
    feedback = {}
    
    if score >= 8.0:
        feedback["main_feedback"] = "Excellent answer! You demonstrated strong understanding of the concept."
        feedback["what_was_good"] = "Your answer covered the key points accurately, showed good understanding, and was well-structured."
    elif score >= 6.5:
        feedback["main_feedback"] = "Good answer with room for improvement. You covered the main points but could add more depth."
        feedback["what_was_good"] = "You understood the core concept and provided relevant information."
    elif score >= 5.0:
        feedback["main_feedback"] = "Average answer. You have basic understanding but missed important details."
        feedback["what_was_good"] = "You showed some understanding of the topic and attempted to explain it."
    elif score >= 3.0:
        feedback["main_feedback"] = "Below average answer. Your response lacks key information and clarity."
        feedback["what_was_good"] = "You made an attempt to answer the question."
    else:
        feedback["main_feedback"] = "Poor answer. The response needs significant improvement in both content and depth."
        feedback["what_was_good"] = "You provided a response, which is a starting point."
    
    if score < 8.0:
        ideal_keywords = extract_key_concepts(ideal_answer)
        user_keywords = extract_key_concepts(user_answer)
        missing_concepts = [kw for kw in ideal_keywords if kw not in user_keywords]
        
        if missing_concepts and len(missing_concepts) > 0:
            missing_sample = ", ".join(missing_concepts[:3])
            feedback["what_was_missing"] = f"Important concepts not fully addressed: {missing_sample}. More depth and specific examples would strengthen your answer."
        else:
            feedback["what_was_missing"] = "More elaboration, specific examples, and clearer explanation of key concepts."
    else:
        feedback["what_was_missing"] = "Your answer was comprehensive. Minor refinements could include additional examples or edge cases."
    
    if score >= 8.0:
        feedback["how_to_improve"] = "Continue your excellent work. Consider adding real-world examples or discussing trade-offs and edge cases to achieve perfection."
    elif score >= 6.5:
        feedback["how_to_improve"] = "Expand on the key concepts with more detail. Include concrete examples and explain the 'why' behind concepts, not just the 'what'."
    elif score >= 5.0:
        feedback["how_to_improve"] = "Study the ideal answer structure. Focus on covering all major points, use clear explanations, and support your points with examples. Practice explaining concepts in a structured way."
    else:
        feedback["how_to_improve"] = "Review the fundamental concepts thoroughly. Break down your answer into clear parts: definition, explanation, examples, and use cases. Practice articulating technical concepts clearly and completely."
    
    return feedback

def extract_key_concepts(text: str) -> list:
    common_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'can', 'it', 'its', 'this', 'that', 'these', 'those'}
    
    words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
    key_terms = [word for word in words if word not in common_words and len(word) > 3]
    
    return list(set(key_terms))

def calculate_interview_summary(scores: list, role: str, level: str) -> dict:
    if not scores:
        return {
            "average_score": 0,
            "total_questions": 0,
            "excellent_count": 0,
            "average_count": 0,
            "poor_count": 0,
            "overall_performance": "No data",
            "recommendation": "Complete the interview to get performance summary."
        }
    
    avg_score = sum(scores) / len(scores)
    excellent = sum(1 for s in scores if s >= 8.0)
    average = sum(1 for s in scores if 5.0 <= s < 8.0)
    poor = sum(1 for s in scores if s < 5.0)
    
    if avg_score >= 8.0:
        overall = "Excellent"
        recommendation = f"Outstanding performance! You're well-prepared for {role} positions at {level} level. Focus on real-world experience and advanced topics to excel further."
    elif avg_score >= 6.5:
        overall = "Good"
        recommendation = f"Good performance with room for growth. Review the areas where you scored below 8 and deepen your understanding of {role} concepts at {level} level."
    elif avg_score >= 5.0:
        overall = "Average"
        recommendation = f"Average performance. Invest more time studying {role} fundamentals. Practice explaining concepts clearly and work through more hands-on projects at {level} level."
    else:
        overall = "Needs Improvement"
        recommendation = f"Significant improvement needed. Focus on building strong fundamentals in {role}. Study the ideal answers, practice regularly, and consider structured learning resources for {level} level content."
    
    return {
        "average_score": round(avg_score, 1),
        "total_questions": len(scores),
        "excellent_count": excellent,
        "average_count": average,
        "poor_count": poor,
        "overall_performance": overall,
        "recommendation": recommendation
    }
