# 🤖 AI Interview Agent

<div align="center">

![AI Interview Agent](https://img.icons8.com/color/96/000000/artificial-intelligence.png)

**Your Personal Interview Coach - Practice with AI-Powered Feedback**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Demo](#demo) • [Contributing](#contributing)

</div>

---

## 📋 Overview

**AI Interview Agent** is an intelligent interview simulation platform that helps job seekers practice and improve their interview skills. Using advanced AI and NLP techniques, it provides realistic interview experiences with instant feedback and detailed performance analysis.

### 🎯 Key Highlights

- **Realistic Interviews**: Role-specific questions for Python Developers, Data Scientists, and Web Developers
- **AI-Powered Evaluation**: Semantic similarity analysis with detailed scoring (0-10 scale)
- **Voice Support**: Speak your answers naturally or type them out
- **Instant Feedback**: Get constructive feedback on every answer
- **Performance Tracking**: Track your progress over time with detailed analytics
- **Professional Experience**: Simulates real interview environments

---

## ✨ Features

### 🎤 Multi-Modal Input
- **Text Input**: Type your answers with a rich text editor
- **Voice Input**: Record answers using your microphone (Whisper AI transcription)
- **AI Voice Output**: Listen to questions spoken by AI (edge-tts)

### 🧠 Intelligent Evaluation
- **Semantic Analysis**: Uses Sentence Transformers for meaning comparison
- **Detailed Scoring**: 0-10 scale with Poor/Average/Excellent categories
- **Multi-Factor Assessment**:
  - Technical Accuracy (40%)
  - Completeness (30%)
  - Clarity (20%)
  - Relevance (10%)

### 💡 Comprehensive Feedback
For every answer, receive:
- ✅ **What Was Good**: Specific strengths identified
- ❌ **What Was Missing**: Key concepts you didn't cover
- 💡 **How to Improve**: Actionable suggestions for improvement
- 📖 **Ideal Answer**: Reference answer to learn from

### 📊 Performance Analytics
- **Session History**: Review all past interviews
- **Progress Tracking**: See improvement over time
- **Role-Based Stats**: Performance breakdown by job role
- **Downloadable Reports**: Export interview results

### 🎯 Customizable Experience
- **3 Job Roles**: Python Developer, Data Scientist, Web Developer
- **3 Difficulty Levels**: Easy, Medium, Hard
- **Flexible Length**: Choose 3-10 questions per session
- **Mixed Question Types**: Technical + HR/Behavioral questions

---

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Microphone (optional, for voice input)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/ai-interview-agent.git
cd ai-interview-agent
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: First-time installation may take 5-10 minutes as it downloads AI models.

### Step 4: Verify Installation

```bash
streamlit --version
```

---

## 🎮 Usage

### Starting the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

### Quick Start Guide

1. **Home Page**
   - Read about features and available roles
   - Click "Start Your Interview" button

2. **Configure Interview**
   - Select your **Job Role** (Python Developer, Data Scientist, Web Developer)
   - Choose **Difficulty Level** (Easy, Medium, Hard)
   - Set **Number of Questions** (3-10)
   - Enable/Disable **Voice Features**
   - Click "Start Interview"

3. **Answer Questions**
   - Read the question carefully
   - Optional: Click "Listen to Question" for audio
   - Choose input method:
     - **Type Answer**: Write your response in the text area
     - **Voice Answer**: Upload an audio recording
   - Click "Submit Answer"

4. **Review Feedback**
   - See your score (0-10) and category
   - Read detailed feedback
   - Review ideal answer
   - Click "Next Question" to continue

5. **Complete Interview**
   - View final performance summary
   - Review all questions and answers
   - Download performance report
   - Start a new interview or return home

### Navigation

- **🏠 Home**: Welcome page and features overview
- **📝 Interview**: Active interview session
- **📊 History**: View past interview sessions
- **📈 Statistics**: Overall performance analytics

---

## 📁 Project Structure

```
AI_Interview_Agent/
├── app.py                          # Main Streamlit application
├── interview_engine.py             # Question generation engine
├── evaluation.py                   # Answer evaluation and scoring
├── speechtotext.py                 # Whisper speech-to-text
├── text_to_speech.py              # Edge-TTS text-to-speech
├── database.py                     # SQLite session management
├── prompts/
│   └── interviewer_prompt.txt     # AI interviewer system prompt
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── interview_history.db            # SQLite database (created at runtime)
└── assets/                         # Additional resources
```

---

## 🎓 How It Works

### Question Generation
- **Question Bank**: Curated questions for each role and difficulty level
- **Dynamic Selection**: Alternates between technical and HR questions
- **Progressive Difficulty**: Questions match selected level

### Answer Evaluation Process

1. **Transcription** (if voice input): Whisper AI converts speech to text
2. **Semantic Analysis**: Sentence Transformers encode answers
3. **Similarity Calculation**: Cosine similarity between user and ideal answers
4. **Quality Adjustments**: 
   - Length ratio analysis
   - Presence of examples
   - Structural organization
5. **Feedback Generation**: AI-generated constructive feedback
6. **Scoring**: Final score (0-10) with category

### Scoring Criteria

| Score Range | Category | Description |
|-------------|----------|-------------|
| 8.0 - 10.0  | Excellent | Strong understanding, comprehensive answer |
| 5.0 - 7.9   | Average  | Basic understanding, room for improvement |
| 0.0 - 4.9   | Poor     | Needs significant improvement |

---

## 📊 Sample Questions

### Python Developer (Medium)
> "Explain the difference between list and tuple in Python. When would you use each?"

### Data Scientist (Hard)
> "Explain the mathematical intuition behind Support Vector Machines and kernel tricks."

### Web Developer (Easy)
> "What is the difference between GET and POST HTTP methods?"

---

## 🔧 Configuration

### Customizing Questions

Edit `interview_engine.py` to add your own questions:

```python
QUESTION_BANK = {
    "Your Role": {
        "Easy": [
            {
                "question": "Your question here?",
                "ideal_answer": "Ideal answer here..."
            }
        ]
    }
}
```

### Adjusting Voice Settings

Edit `text_to_speech.py` to change AI voice:

```python
# Choose from available voices
voice = "en-US-AriaNeural"  # Professional female
# voice = "en-US-GuyNeural"  # Professional male
```

### Database Location

By default, interview history is stored in `interview_history.db`. To change location, edit `database.py`:

```python
DB_PATH = "your/custom/path/interview_history.db"
```

---

## 🐛 Troubleshooting

### Common Issues

**Issue**: "Module not found" error
```bash
# Solution: Reinstall requirements
pip install -r requirements.txt --upgrade
```

**Issue**: Whisper model download fails
```bash
# Solution: Download manually
python -c "import whisper; whisper.load_model('base')"
```

**Issue**: Audio recording not working
```bash
# Solution: Install PyAudio properly (Windows)
pip install pipwin
pipwin install pyaudio
```

**Issue**: Edge-TTS not generating audio
```bash
# Solution: Check internet connection (edge-tts requires online access)
# Alternative: Use offline TTS library
```

---

## 🎯 Advanced Features

### Session Management
- All interviews are saved automatically
- View complete history with scores
- Export sessions as text reports
- Track improvement over time

### Performance Analytics
- Overall average score across all sessions
- Performance breakdown by job role
- Trend analysis (Improving/Stable/Declining)
- Question-level performance review

### Customization Options
- Number of questions (3-10)
- Enable/disable voice features
- Choose difficulty appropriate for your level
- Focus on specific roles

---

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/AmazingFeature`
3. **Commit changes**: `git commit -m 'Add AmazingFeature'`
4. **Push to branch**: `git push origin feature/AmazingFeature`
5. **Open a Pull Request**

### Areas for Contribution
- 🆕 Add more job roles and questions
- 🌐 Add multilingual support
- 📱 Mobile-responsive UI improvements
- 🎨 UI/UX enhancements
- 🐛 Bug fixes and optimizations
- 📚 Documentation improvements

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **OpenAI Whisper** - Speech recognition
- **Microsoft Edge TTS** - Text-to-speech
- **Sentence Transformers** - Semantic similarity
- **Streamlit** - Web framework
- **Hugging Face** - AI models

---

## 📧 Contact & Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/ai-interview-agent/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/ai-interview-agent/discussions)
- **Email**: your.email@example.com

---

## 🗺️ Roadmap

### Version 2.0 (Planned)
- [ ] More job roles (DevOps, ML Engineer, etc.)
- [ ] Custom question upload
- [ ] Video interview practice
- [ ] Emotion detection from voice
- [ ] Multi-language support
- [ ] Mobile app
- [ ] Interview scheduling with reminders
- [ ] Peer comparison analytics
- [ ] AI-generated custom study plans
- [ ] Integration with job boards

---

## 📊 Project Stats

- **Total Questions**: 50+ curated questions
- **Job Roles**: 3 (Python, Data Science, Web Dev)
- **Difficulty Levels**: 3 (Easy, Medium, Hard)
- **Supported Languages**: English (more coming soon)
- **AI Models**: Whisper, Sentence Transformers, Edge-TTS

---

## 💪 Success Stories

> "This tool helped me identify my weak areas and improve my interview performance significantly!" - *Anonymous User*

> "The detailed feedback is incredibly helpful. It's like having a personal interview coach." - *Anonymous User*

---

<div align="center">

**⭐ If you find this project helpful, please give it a star! ⭐**

Made with ❤️ by developers, for developers

[⬆ Back to Top](#-ai-interview-agent)

</div>
