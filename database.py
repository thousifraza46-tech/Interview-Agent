import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os

DB_PATH = "interview_history.db"

def init_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            session_id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            level TEXT NOT NULL,
            start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            end_time TIMESTAMP,
            average_score REAL,
            total_questions INTEGER,
            status TEXT DEFAULT 'in_progress'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            answer_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            question_number INTEGER,
            question TEXT,
            user_answer TEXT,
            ideal_answer TEXT,
            score REAL,
            feedback TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(session_id)
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(role: str, level: str) -> int:
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (role, level, status)
        VALUES (?, ?, 'in_progress')
    ''', (role, level))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id

def save_answer(session_id: int, question_number: int, question: str, 
                user_answer: str, ideal_answer: str, evaluation: dict):
    import json
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO answers (session_id, question_number, question, user_answer,
                           ideal_answer, score, feedback)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        session_id,
        question_number,
        question,
        user_answer,
        ideal_answer,
        evaluation.get('score', 0),
        json.dumps({
            'main_feedback': evaluation.get('feedback', ''),
            'what_was_good': evaluation.get('what_was_good', ''),
            'what_was_missing': evaluation.get('what_was_missing', ''),
            'how_to_improve': evaluation.get('how_to_improve', '')
        })
    ))
    
    conn.commit()
    conn.close()

def complete_session(session_id: int, average_score: float, total_questions: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE sessions
        SET end_time = CURRENT_TIMESTAMP,
            average_score = ?,
            total_questions = ?,
            status = 'completed'
        WHERE session_id = ?
    ''', (average_score, total_questions, session_id))
    
    conn.commit()
    conn.close()

def get_session_history(limit: int = None) -> list:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    if limit:
        cursor.execute('''
            SELECT session_id, role, level, start_time, end_time,
                   average_score, total_questions, status
            FROM sessions
            ORDER BY start_time DESC
            LIMIT ?
        ''', (limit,))
    else:
        cursor.execute('''
            SELECT session_id, role, level, start_time, end_time,
                   average_score, total_questions, status
            FROM sessions
            ORDER BY start_time DESC
        ''')
    
    sessions = []
    for row in cursor.fetchall():
        sessions.append({
            'session_id': row[0],
            'role': row[1],
            'level': row[2],
            'start_time': row[3],
            'end_time': row[4],
            'average_score': row[5],
            'total_questions': row[6],
            'status': row[7]
        })
    
    conn.close()
    return sessions

def get_session_details(session_id: int) -> Optional[Dict]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT session_id, role, level, start_time, end_time,
               average_score, total_questions, status
        FROM sessions
        WHERE session_id = ?
    ''', (session_id,))
    
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None
    
    session = {
        'session_id': row[0],
        'role': row[1],
        'level': row[2],
        'start_time': row[3],
        'end_time': row[4],
        'average_score': row[5],
        'total_questions': row[6],
        'status': row[7],
        'answers': []
    }
    
    cursor.execute('''
        SELECT question_number, question, user_answer, ideal_answer,
               score, feedback, timestamp
        FROM answers
        WHERE session_id = ?
        ORDER BY question_number
    ''', (session_id,))
    
    import json
    for row in cursor.fetchall():
        feedback_json = json.loads(row[5]) if row[5] else {}
        session['answers'].append({
            'question_number': row[0],
            'question': row[1],
            'user_answer': row[2],
            'ideal_answer': row[3],
            'score': row[4],
            'category': 'Excellent' if row[4] >= 8 else 'Average' if row[4] >= 5 else 'Poor',
            'feedback': feedback_json,
            'timestamp': row[6]
        })
    
    conn.close()
    return session

def get_statistics() -> Dict:
    init_database()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM sessions WHERE status = "completed"')
    total_sessions = cursor.fetchone()[0]
    
    cursor.execute('SELECT AVG(average_score) FROM sessions WHERE status = "completed"')
    overall_avg = cursor.fetchone()[0] or 0
    
    cursor.execute('''
        SELECT role, AVG(average_score), COUNT(*)
        FROM sessions
        WHERE status = "completed"
        GROUP BY role
    ''')
    
    role_stats = {}
    for row in cursor.fetchall():
        role_stats[row[0]] = {
            'average_score': round(row[1], 1),
            'session_count': row[2]
        }
    
    cursor.execute('''
        SELECT average_score
        FROM sessions
        WHERE status = "completed"
        ORDER BY start_time DESC
        LIMIT 10
    ''')
    
    recent_scores = [row[0] for row in cursor.fetchall() if row[0]]
    
    trend = "N/A"
    if len(recent_scores) >= 2:
        recent_avg = sum(recent_scores[:5]) / min(5, len(recent_scores[:5]))
        older_avg = sum(recent_scores[5:]) / len(recent_scores[5:]) if len(recent_scores) > 5 else recent_avg
        if recent_avg > older_avg + 0.5:
            trend = "Improving"
        elif recent_avg < older_avg - 0.5:
            trend = "Declining"
        else:
            trend = "Stable"
    
    conn.close()
    
    return {
        'total_completed_sessions': total_sessions,
        'overall_average_score': round(overall_avg, 1),
        'performance_by_role': role_stats,
        'trend': trend
    }

def delete_session(session_id: int):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM answers WHERE session_id = ?', (session_id,))
    cursor.execute('DELETE FROM sessions WHERE session_id = ?', (session_id,))
    
    conn.commit()
    conn.close()

def export_session_to_text(session_id: int, output_file: str):
    session = get_session_details(session_id)
    if not session:
        return False
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("="*60 + "\n")
        f.write("AI INTERVIEW AGENT - PERFORMANCE REPORT\n")
        f.write("="*60 + "\n\n")
        f.write(f"Role: {session['role']}\n")
        f.write(f"Level: {session['level']}\n")
        f.write(f"Date: {session['start_time']}\n")
        f.write(f"Average Score: {session['average_score']:.1f}/10\n")
        f.write(f"Total Questions: {session['total_questions']}\n")
        f.write("\n" + "="*60 + "\n\n")
        
        for answer in session['answers']:
            f.write(f"Question {answer['question_number']}:\n")
            f.write(f"{answer['question']}\n\n")
            f.write(f"Your Answer:\n{answer['user_answer']}\n\n")
            f.write(f"Score: {answer['score']}/10 ({answer['category']})\n\n")
            
            feedback = answer['feedback']
            f.write(f"Feedback: {feedback.get('main_feedback', '')}\n")
            f.write(f"What was good: {feedback.get('what_was_good', '')}\n")
            f.write(f"What was missing: {feedback.get('what_was_missing', '')}\n")
            f.write(f"How to improve: {feedback.get('how_to_improve', '')}\n\n")
            f.write(f"Ideal Answer:\n{answer['ideal_answer']}\n\n")
            f.write("-"*60 + "\n\n")
    
    return True
