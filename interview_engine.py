import random
from typing import Dict, List, Tuple
import json

# Initialize OpenAI client only if API key is available
openai_client = None
try:
    from openai import OpenAI
    from config import OPENAI_API_KEY
    if OPENAI_API_KEY:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    print(f"OpenAI initialization skipped: {e}")

# Initialize Gemini client only if API key is available
genai = None
genai_model = None
try:
    import google.generativeai as genai
    from config import GEMINI_API_KEY, GEMINI_MODEL
    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        genai_model = genai.GenerativeModel(GEMINI_MODEL)
except Exception as e:
    print(f"Gemini initialization skipped: {e}")

from config import AI_PROVIDER, OPENAI_MODEL

def generate_ai_question(role: str, level: str, question_number: int, is_hr: bool = False) -> Dict:
    """Generate AI question with proper error handling for missing API keys"""
    
    # Check if AI is available
    if not openai_client and not genai_model:
        print("No AI client available, using fallback questions")
        return None
    
    question_type = "HR behavioral" if is_hr else "technical"
    
    prompt = f"""Generate a {level} level {question_type} interview question for a {role} position.

Requirements:
1. Create a clear, specific question appropriate for {level} difficulty
2. Provide 4 multiple choice options (A, B, C, D)
3. Indicate the correct answer (A, B, C, or D)
4. Provide a comprehensive ideal answer/explanation (100-150 words)

Return ONLY a valid JSON object in this exact format:
{{
  "question": "Your question here?",
  "options": {{
    "A": "First option",
    "B": "Second option",
    "C": "Third option",
    "D": "Fourth option"
  }},
  "correct_answer": "B",
  "ideal_answer": "Detailed explanation of the concept..."
}}

Make the question {"challenging and require deep understanding" if level == "Hard" else "moderately challenging" if level == "Medium" else "foundational and clear"}."""

    try:
        if AI_PROVIDER == "openai" and openai_client:
            response = openai_client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert technical interviewer. Generate high-quality interview questions with MCQ options. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=600
            )
            content = response.choices[0].message.content.strip()
        elif AI_PROVIDER == "gemini" and genai_model:
            response = genai_model.generate_content(prompt)
            content = response.text.strip()
        else:
            print(f"AI provider {AI_PROVIDER} not available")
            return None
        
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()
        
        question_data = json.loads(content)
        
        if not all(key in question_data for key in ['question', 'options', 'correct_answer', 'ideal_answer']):
            raise ValueError("Missing required fields in AI response")
        
        return question_data
        
    except Exception as e:
        print(f"Error generating AI question: {e}")
        return None

QUESTION_BANK = {
    "Python Developer": {
        "Easy": [
            {
                "question": "What is a list in Python and how is it different from an array?",
                "options": {
                    "A": "Lists can only store same data types, arrays can store mixed types",
                    "B": "Lists are dynamic and can contain mixed data types, arrays are fixed",
                    "C": "Lists and arrays are exactly the same in Python",
                    "D": "Lists require numpy library, arrays don't"
                },
                "correct_answer": "B",
                "ideal_answer": "A list in Python is a built-in data structure that can hold multiple items of different data types. Unlike arrays in languages like C or Java, Python lists are dynamic, can grow or shrink in size, and can contain mixed data types. Lists are created using square brackets and support operations like append, insert, remove, and slicing."
            },
            {
                "question": "Explain the difference between '==' and 'is' operators in Python.",
                "options": {
                    "A": "'==' checks identity, 'is' checks value",
                    "B": "'==' checks value, 'is' checks identity (memory location)",
                    "C": "Both operators do exactly the same thing",
                    "D": "'==' is faster than 'is' operator"
                },
                "correct_answer": "B",
                "ideal_answer": "The '==' operator compares the values of two objects to check if they are equal, while 'is' checks if two variables point to the same object in memory (identity comparison). For example, two lists with the same content will return True with '==' but False with 'is' unless they reference the exact same object."
            },
            {
                "question": "What are Python decorators and give a simple example?",
                "options": {
                    "A": "Functions that delete other functions",
                    "B": "Classes that inherit from multiple parents",
                    "C": "Functions that modify behavior of other functions using @ symbol",
                    "D": "Variables that store function names"
                },
                "correct_answer": "C",
                "ideal_answer": "Decorators are functions that modify the behavior of other functions or methods. They use the @ symbol and are placed above a function definition. A simple example is @staticmethod or @property. Decorators allow you to wrap another function to extend its behavior without permanently modifying it."
            },
            {
                "question": "How do you handle exceptions in Python?",
                "options": {
                    "A": "Using if-else statements only",
                    "B": "Using try-except-else-finally blocks",
                    "C": "Using switch-case statements",
                    "D": "Exceptions cannot be handled in Python"
                },
                "correct_answer": "B",
                "ideal_answer": "Exceptions in Python are handled using try-except blocks. Code that might raise an exception goes in the try block, and exception handling code goes in the except block. You can also use else for code that runs if no exception occurs, and finally for cleanup code that always runs. Example: try-except-else-finally structure."
            }
        ],
        "Medium": [
            {
                "question": "Explain the difference between list and tuple in Python. When would you use each?",
                "options": {
                    "A": "Lists are immutable, tuples are mutable",
                    "B": "Lists are mutable, tuples are immutable",
                    "C": "Both are immutable data structures",
                    "D": "Lists are faster than tuples"
                },
                "correct_answer": "B",
                "ideal_answer": "Lists are mutable, meaning their elements can be changed after creation, while tuples are immutable and cannot be modified. Lists use square brackets [], tuples use parentheses (). Use lists when you need to modify data frequently, and tuples for fixed data that shouldn't change, like coordinates or database records. Tuples are also faster and use less memory."
            },
            {
                "question": "What is a generator in Python and why would you use it?",
                "options": {
                    "A": "A function that creates random numbers",
                    "B": "A function that returns an iterator using yield keyword",
                    "C": "A class that generates instances",
                    "D": "A module that creates files"
                },
                "correct_answer": "B",
                "ideal_answer": "A generator is a function that returns an iterator using the yield keyword instead of return. Generators produce values on-the-fly and don't store all values in memory at once, making them memory-efficient for large datasets. They're useful for processing large files, infinite sequences, or when you need lazy evaluation."
            },
            {
                "question": "Explain the difference between deep copy and shallow copy in Python.",
                "options": {
                    "A": "Shallow copy copies nested objects, deep copy doesn't",
                    "B": "Deep copy creates independent copy of all nested objects, shallow copy just copies references",
                    "C": "Both create completely independent copies",
                    "D": "Deep copy is faster than shallow copy"
                },
                "correct_answer": "B",
                "ideal_answer": "A shallow copy creates a new object but doesn't create copies of nested objects; it just copies references. A deep copy creates a completely independent copy of an object and all objects nested within it. Use copy.copy() for shallow copy and copy.deepcopy() for deep copy. Shallow copies are faster but changes to nested objects affect both copies."
            },
            {
                "question": "What are Python's *args and **kwargs? Provide examples.",
                "ideal_answer": "*args allows a function to accept any number of positional arguments as a tuple, while **kwargs allows any number of keyword arguments as a dictionary. They provide flexibility in function definitions. Example: def func(*args, **kwargs) lets you call func(1, 2, 3, name='John', age=30) where (1,2,3) goes to args and {'name':'John', 'age':30} goes to kwargs."
            }
        ],
        "Hard": [
            {
                "question": "Explain Python's memory management and garbage collection mechanism.",
                "ideal_answer": "Python uses automatic memory management with reference counting and a garbage collector. Every object has a reference count that tracks how many references point to it. When the count reaches zero, the memory is deallocated. Python also uses a generational garbage collector to detect and clean up circular references. The GC divides objects into three generations (0, 1, 2) based on how many collection cycles they've survived, optimizing performance by focusing on younger objects."
            },
            {
                "question": "What is the Global Interpreter Lock (GIL) and how does it affect Python programs?",
                "ideal_answer": "The GIL is a mutex that protects access to Python objects, preventing multiple threads from executing Python bytecode simultaneously. This means that even on multi-core systems, only one thread executes Python code at a time. The GIL impacts CPU-bound multi-threaded programs negatively but doesn't affect I/O-bound programs much. Solutions include using multiprocessing instead of threading for CPU-bound tasks, or using alternative Python implementations like Jython or IronPython."
            },
            {
                "question": "Explain metaclasses in Python and when you would use them.",
                "ideal_answer": "Metaclasses are classes of classes that define how classes behave. A class is an instance of a metaclass. The default metaclass is 'type'. Metaclasses allow you to intercept class creation and modify class definitions. They're useful for API development, ORMs (like Django models), validation frameworks, and automatic registration systems. However, they're complex and should be used sparingly when simpler solutions like decorators or class decorators won't work."
            },
            {
                "question": "How do you optimize Python code for performance? Discuss multiple strategies.",
                "ideal_answer": "Key optimization strategies include: 1) Use built-in functions and libraries (they're implemented in C), 2) Use list comprehensions instead of loops, 3) Avoid global variables, 4) Use local variables in functions, 5) Use generators for large datasets, 6) Profile code with cProfile to find bottlenecks, 7) Use appropriate data structures (sets for membership testing, deque for queues), 8) Consider Cython or NumPy for numerical operations, 9) Use multiprocessing for CPU-bound tasks, 10) Cache results with functools.lru_cache."
            }
        ]
    },
    "Data Scientist": {
        "Easy": [
            {
                "question": "What is the difference between supervised and unsupervised learning?",
                "ideal_answer": "Supervised learning uses labeled data where the target output is known, and the model learns to map inputs to outputs (e.g., classification, regression). Unsupervised learning works with unlabeled data to find hidden patterns or structures (e.g., clustering, dimensionality reduction). Supervised learning needs training data with correct answers, while unsupervised learning discovers patterns on its own."
            },
            {
                "question": "Explain what a p-value means in statistics.",
                "ideal_answer": "A p-value is the probability of obtaining test results at least as extreme as the observed results, assuming the null hypothesis is true. A small p-value (typically < 0.05) suggests strong evidence against the null hypothesis, so you reject it. A large p-value suggests weak evidence against the null hypothesis, so you fail to reject it. It's a measure of statistical significance."
            },
            {
                "question": "What is overfitting in machine learning and how can you prevent it?",
                "ideal_answer": "Overfitting occurs when a model learns the training data too well, including noise and outliers, resulting in poor generalization to new data. The model performs well on training data but poorly on test data. Prevention methods include: using cross-validation, regularization (L1/L2), reducing model complexity, using more training data, dropout in neural networks, and early stopping."
            }
        ],
        "Medium": [
            {
                "question": "Explain the bias-variance tradeoff in machine learning.",
                "ideal_answer": "The bias-variance tradeoff is a fundamental concept where bias refers to errors from overly simplistic models (underfitting) and variance refers to errors from overly complex models (overfitting). High bias means the model doesn't capture the underlying pattern well. High variance means the model is too sensitive to training data fluctuations. The goal is to find the sweet spot that minimizes both, achieving good generalization."
            },
            {
                "question": "What is the difference between bagging and boosting ensemble methods?",
                "ideal_answer": "Bagging (Bootstrap Aggregating) creates multiple models independently using different random subsets of training data and combines them by averaging (regression) or voting (classification). Random Forest is an example. Boosting builds models sequentially, where each new model focuses on correcting errors made by previous models. Examples include AdaBoost, Gradient Boosting, and XGBoost. Boosting typically achieves higher accuracy but is more prone to overfitting."
            },
            {
                "question": "Explain precision, recall, and F1-score with examples.",
                "ideal_answer": "Precision is the ratio of true positives to all predicted positives (TP/(TP+FP)) - how many of your positive predictions were correct. Recall is the ratio of true positives to all actual positives (TP/(TP+FN)) - how many actual positives you found. F1-score is the harmonic mean of precision and recall. For a spam filter: precision is % of flagged emails that are actually spam, recall is % of all spam emails that were caught."
            }
        ],
        "Hard": [
            {
                "question": "Explain the mathematical intuition behind Support Vector Machines and kernel tricks.",
                "ideal_answer": "SVMs find the optimal hyperplane that maximizes the margin between classes. The margin is the distance between the hyperplane and the nearest data points (support vectors). For non-linearly separable data, kernel tricks transform data into higher dimensions where linear separation is possible, without explicitly computing the transformation. Common kernels include RBF, polynomial, and sigmoid. The kernel function computes dot products in transformed space efficiently, solving the dual optimization problem using Lagrange multipliers."
            },
            {
                "question": "How does backpropagation work in neural networks? Explain the mathematics.",
                "ideal_answer": "Backpropagation calculates gradients of the loss function with respect to network weights using the chain rule. It propagates errors backward through layers. For each layer, it computes: 1) the gradient of loss with respect to layer output, 2) gradient with respect to layer input using chain rule, 3) gradient with respect to weights. The algorithm uses these gradients for weight updates via gradient descent. The chain rule links: dL/dw = dL/da * da/dz * dz/dw, where L is loss, a is activation, z is weighted sum, and w is weight."
            },
            {
                "question": "Explain different dimensionality reduction techniques and when to use each.",
                "ideal_answer": "PCA (Principal Component Analysis) uses linear transformations to find orthogonal directions of maximum variance - best for linear relationships and visualization. t-SNE preserves local structure and is excellent for visualization but not for preprocessing. UMAP is faster than t-SNE and preserves both local and global structure. Autoencoders use neural networks for non-linear reduction. LDA is supervised and maximizes class separability. Use PCA for speed and interpretability, t-SNE/UMAP for visualization, autoencoders for complex non-linear patterns."
            }
        ]
    },
    "Web Developer": {
        "Easy": [
            {
                "question": "What is the difference between HTML, CSS, and JavaScript?",
                "ideal_answer": "HTML (HyperText Markup Language) structures the content and defines elements like headings, paragraphs, and links. CSS (Cascading Style Sheets) handles presentation and styling, controlling colors, layouts, and fonts. JavaScript adds interactivity and dynamic behavior, allowing user interactions, animations, and data manipulation. Think of HTML as the skeleton, CSS as the skin, and JavaScript as the muscles that make it move."
            },
            {
                "question": "Explain the box model in CSS.",
                "ideal_answer": "The CSS box model describes how elements are rendered as rectangular boxes. Each box consists of four areas: content (the actual content), padding (space between content and border), border (surrounds the padding), and margin (space outside the border separating elements). The total width/height includes content + padding + border (in standard box model), but you can use box-sizing: border-box to include padding and border in the defined width/height."
            },
            {
                "question": "What is the difference between GET and POST HTTP methods?",
                "ideal_answer": "GET requests retrieve data from a server and parameters are visible in the URL. GET is idempotent (multiple identical requests have the same effect), can be cached and bookmarked, has length restrictions, and should only retrieve data. POST sends data to create/update resources, with data in the request body (not visible in URL). POST is not idempotent, can't be cached or bookmarked, has no length restrictions, and can modify server state."
            }
        ],
        "Medium": [
            {
                "question": "Explain event bubbling and event capturing in JavaScript.",
                "ideal_answer": "Event propagation in the DOM has three phases: capturing (event travels from window to target element), target (event reaches the target), and bubbling (event bubbles up from target to window). By default, event handlers execute during bubbling. Event.stopPropagation() stops propagation, and event.preventDefault() prevents default behavior. Use capture by setting addEventListener's third parameter to true. Understanding this is crucial for event delegation patterns."
            },
            {
                "question": "What is the difference between cookies, localStorage, and sessionStorage?",
                "ideal_answer": "Cookies are small data pieces sent with every HTTP request, have expiration dates, ~4KB limit, and can be accessed server-side. localStorage persists data indefinitely (until manually cleared), has ~5-10MB limit, and is client-side only. sessionStorage is similar to localStorage but clears when the browser tab closes. Use cookies for server-side data, localStorage for persistent client-side data, and sessionStorage for temporary session data."
            },
            {
                "question": "Explain the concept of RESTful APIs and their key principles.",
                "ideal_answer": "REST (Representational State Transfer) is an architectural style for APIs. Key principles: 1) Stateless - each request contains all needed information, 2) Client-Server separation, 3) Cacheable responses, 4) Uniform interface using standard HTTP methods (GET, POST, PUT, DELETE), 5) Resource-based URLs (nouns not verbs), 6) JSON/XML for data transfer. Example: GET /api/users/123 retrieves user 123, POST /api/users creates a user, PUT /api/users/123 updates user 123, DELETE /api/users/123 deletes user 123."
            }
        ],
        "Hard": [
            {
                "question": "Explain how the JavaScript event loop and call stack work.",
                "ideal_answer": "JavaScript is single-threaded with a call stack for executing functions. The event loop monitors the call stack and callback queue. When the stack is empty, it moves callbacks from the queue to the stack. Asynchronous operations (setTimeout, HTTP requests, promises) are handled by Web APIs. When complete, their callbacks enter the task queue (macrotasks) or microtask queue (promises). Microtasks execute before macrotasks. This enables non-blocking I/O despite being single-threaded. Understanding this is crucial for async programming and avoiding race conditions."
            },
            {
                "question": "What are Web Workers and when would you use them?",
                "ideal_answer": "Web Workers allow running JavaScript in background threads, separate from the main execution thread. They enable true parallel processing without blocking the UI. Workers can't access DOM but can perform CPU-intensive tasks like complex calculations, data processing, or encryption. Communication happens via postMessage and onmessage events. Use cases: image manipulation, large data parsing, cryptographic operations, or real-time data processing. They're essential for maintaining responsive UIs during heavy computation."
            },
            {
                "question": "Explain Cross-Origin Resource Sharing (CORS) and how to handle it.",
                "ideal_answer": "CORS is a security mechanism that controls how web pages from one domain can access resources from another domain. Browsers enforce same-origin policy by default. CORS uses HTTP headers: Access-Control-Allow-Origin specifies allowed domains, Access-Control-Allow-Methods specifies allowed HTTP methods, Access-Control-Allow-Headers specifies allowed headers. Preflight requests (OPTIONS) check permissions before actual requests. Server-side solutions include setting appropriate headers, using CORS middleware, or implementing a proxy. Client-side solutions include JSONP (legacy) or server-side proxies."
            }
        ]
    }
}

HR_QUESTIONS = {
    "Easy": [
        {
            "question": "Tell me about yourself and your background.",
            "ideal_answer": "A good answer should be concise (2-3 minutes), covering: current role/education, relevant skills and experience, key achievements, and why you're interested in this position. Structure: Present (current situation), Past (how you got here), Future (career goals). Focus on professional aspects relevant to the job, show enthusiasm, and connect your background to the role you're applying for."
        },
        {
            "question": "Why do you want to work for our company?",
            "ideal_answer": "A strong answer demonstrates research about the company, mentions specific aspects that attract you (company values, culture, products, growth opportunities), connects your skills to their needs, and shows genuine enthusiasm. Avoid generic responses. Mention recent company achievements, projects, or values that resonate with you. Show how you can contribute to their goals."
        }
    ],
    "Medium": [
        {
            "question": "Describe a challenging project you worked on and how you overcame obstacles.",
            "ideal_answer": "Use the STAR method: Situation (context), Task (your responsibility), Action (specific steps you took), Result (outcome and what you learned). Choose a relevant technical challenge, explain the problem clearly, detail your problem-solving approach, mention collaboration if applicable, quantify results if possible, and reflect on lessons learned. Show initiative, technical skills, and ability to persevere through difficulties."
        },
        {
            "question": "What are your greatest strengths and weaknesses?",
            "ideal_answer": "For strengths: Choose 2-3 relevant to the job, provide specific examples demonstrating them, and explain how they benefit the employer. For weaknesses: Be honest but strategic, choose something you're actively improving, explain steps you're taking to address it, and show self-awareness. Avoid cliché weaknesses like 'I'm a perfectionist.' Example: 'I'm working on public speaking by joining Toastmasters and presenting at team meetings.'"
        }
    ],
    "Hard": [
        {
            "question": "Where do you see yourself in 5 years and how does this position fit into your career goals?",
            "ideal_answer": "Show ambition balanced with realism, demonstrate understanding of the industry and career path, align your goals with the company's growth, show commitment without seeming like you'll leave quickly, mention skills you want to develop, and express interest in growing within the company. Avoid: 'I want your job' or being too vague. Show you've thought about your career trajectory and this role is a strategic step."
        },
        {
            "question": "Tell me about a time you failed and what you learned from it.",
            "ideal_answer": "Choose a real professional failure that wasn't catastrophic, take accountability without excessive blame, use STAR method, focus more on what you learned and how you improved than the failure itself, show resilience and growth mindset, and ideally mention how you applied those lessons successfully later. Demonstrates maturity, self-awareness, and ability to learn from mistakes - all valuable traits employers seek."
        }
    ]
}

def generate_question(role: str, level: str, question_number: int = 0, include_hr: bool = True, use_ai: bool = True) -> Dict:
    """Generate question with fallback to static bank if AI fails"""
    is_hr_question = include_hr and question_number % 4 == 0 and question_number > 0
    
    if use_ai:
        try:
            ai_question = generate_ai_question(role, level, question_number, is_hr_question)
            if ai_question:
                return ai_question
        except Exception as e:
            print(f"Falling back to static questions due to error: {e}")
    
    # Fallback to static questions
    if is_hr_question:
        questions = HR_QUESTIONS.get(level, HR_QUESTIONS["Easy"])
    else:
        questions = QUESTION_BANK.get(role, QUESTION_BANK["Python Developer"]).get(level, QUESTION_BANK["Python Developer"]["Easy"])
    
    question_index = (question_number // 2) % len(questions)
    return questions[question_index]

def get_total_questions(role: str, level: str) -> int:
    technical_questions = len(QUESTION_BANK.get(role, QUESTION_BANK["Python Developer"]).get(level, []))
    hr_questions = len(HR_QUESTIONS.get(level, []))
    return technical_questions + hr_questions

def generate_interview_questions(role: str, level: str, num_questions: int = 50) -> List[Dict]:
    questions = []
    for i in range(num_questions):
        question = generate_question(role, level, i)
        questions.append(question)
    return questions

def get_interviewer_prompt(role: str, level: str) -> str:
    return f"""You are a professional AI Interview Agent conducting a {level} level interview for a {role} position.

Your responsibilities:
- Ask clear, structured questions appropriate for the role and difficulty level
- Evaluate responses based on accuracy, clarity, relevance, and completeness
- Provide constructive feedback with specific improvement suggestions
- Maintain a professional, encouraging, but appropriately challenging tone
- Score answers objectively on a scale of 0-10
- Help candidates understand what makes a strong answer

Evaluation Criteria:
- Technical Accuracy (40%): Is the answer technically correct?
- Completeness (30%): Does it cover all key aspects?
- Clarity (20%): Is it well-explained and easy to understand?
- Relevance (10%): Does it directly address the question?

Be fair but realistic in your assessment. This is a {level} level interview, so adjust expectations accordingly."""
